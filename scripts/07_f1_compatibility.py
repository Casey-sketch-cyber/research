"""Verify all H1/H2 candidate tables and primary bounds before F1 result reuse."""
import os
for name in ("OPENBLAS_NUM_THREADS","OMP_NUM_THREADS","MKL_NUM_THREADS"):
    os.environ[name]="1"
from concurrent.futures import ProcessPoolExecutor
from copy import deepcopy
from dataclasses import asdict
import hashlib
import json
from pathlib import Path
from types import SimpleNamespace
import numpy as np
import pandas as pd
from tqdm import tqdm
from fea.config import config_hash
from fea.furniture.library import library
from fea.furniture.candidates import generate_candidates
from fea.geometry.raster import rasterize
from fea.geometry.unit import Unit
from fea.households import parse_households
from fea.solve.cpsat import relaxed_capacity_bound
from fea.io import prepare_cli,start_run,write_json,sha256_file
from phase07_analysis import load_evaluable_solutions
from phase07_f1 import original_configuration,UNCHANGED_HOUSEHOLDS


def candidate_hash(candidates):
    digest=hashlib.sha256()
    for name,poses in sorted(candidates.items()):
        digest.update(name.encode());digest.update(str(poses.shape).encode());digest.update(poses.astype('<i4').tobytes())
    return digest.hexdigest()


def check_unit(job):
    serialized,old,new,settings=job
    unit=Unit.from_dict(json.loads(serialized));group="small" if unit.interior.area<=20+1e-8 else "large";arm=settings[group]
    grid=rasterize(unit,new["raster"]["resolution_m"],new["furniture"]["meta"]["walking_width"],new["raster"]["source_gap_close_m"])
    old_items,new_items=library(old["furniture"]),library(new["furniture"])
    old_candidates=generate_candidates(grid,old_items,new["raster"]["orientations_deg"],arm["anchor_stride_m"])
    new_candidates=generate_candidates(grid,new_items,new["raster"]["orientations_deg"],arm["anchor_stride_m"])
    if set(old_candidates)!=set(new_candidates) or any(not np.array_equal(old_candidates[k],new_candidates[k]) for k in old_candidates):
        raise ValueError("H1/H2 geometric candidate tables changed")
    old_digest,new_digest=candidate_hash(old_candidates),candidate_hash(new_candidates)
    households=parse_households(new["households"],new["furniture"]);records=[]
    for strategy in ("S0","S1","S2"):
        bounds=[];instance_counts=[]
        for cfg,candidates in [(old,old_candidates),(new,new_candidates)]:
            items=library(cfg["furniture"],strategy)
            instances={f"{name}#{i+1}":SimpleNamespace(item=item) for name,item in items.items() if len(candidates[name]) for i in range(item.max_instances)}
            bounds.append({h:relaxed_capacity_bound(instances,households[h]) for h in UNCHANGED_HOUSEHOLDS})
            instance_counts.append(len(instances))
        for h in UNCHANGED_HOUSEHOLDS:
            if bounds[0][h]!=bounds[1][h]:raise ValueError("H1/H2 primary FCI bound changed")
            records.append(dict(unit_key=unit.unit_key,source=unit.source,household=h,strategy=strategy,budget_group=group,
                candidate_tables_equal=True,old_candidates_sha256=old_digest,new_candidates_sha256=new_digest,
                old_primary_fci_bound=float(bounds[0][h]),new_primary_fci_bound=float(bounds[1][h]),
                old_available_instances=instance_counts[0],new_available_instances=instance_counts[1]))
    return records


def main():
    args=prepare_cli(__doc__).parse_args();config,_,_=start_run(args,"07_f1_compatibility")
    if args.dry_run:print("Would compare every evaluable H1/H2 candidate table and exact rational primary FCI upper bound.");return
    main_run=json.loads(Path("results/expA/run.json").read_text());old=original_configuration(config,main_run["base_config_hash"])
    households=parse_households(config["households"],config["furniture"])
    for name in UNCHANGED_HOUSEHOLDS:
        h=households[name]
        sleeps=[(s,d) for v in h.variants for s,ds in v.demand.items() for d in ds if d.need.startswith("sleep")]
        if len(h.variants)!=1 or len(sleeps)!=1 or sleeps[0][0]!="night" or sleeps[0][1].need!="sleep_1":
            raise ValueError("H1/H2 unchanged-result argument no longer applies")
    solutions,gate=load_evaluable_solutions(old)
    units=solutions.drop_duplicates("unit_key").sort_values("unit_key")
    corpus=pd.read_parquet(Path(config["paths"]["processed"])/"corpus_units.parquet",columns=["unit_key","unit_json"]).set_index("unit_key")
    root=Path("results/expA_f1");root.mkdir(parents=True,exist_ok=True)
    jobs=((corpus.loc[k,"unit_json"],old,config,main_run["production_settings"]) for k in units.unit_key)
    rows=[]
    with ProcessPoolExecutor(max_workers=4) as pool:
        for records in tqdm(pool.map(check_unit,jobs,chunksize=5),total=len(units),desc="F1 H1/H2 compatibility"):
            rows.extend(records)
            if len(rows)%600==0:write_json(root/"compatibility_progress.json",dict(units_checked=len(rows)//6,expected_units=len(units)))
    pd.DataFrame(rows).to_csv(root/"H1H2_compatibility.csv",index=False)
    write_json(root/"compatibility_acceptance.json",dict(passed=True,units=len(units),household_strategy_checks=len(rows),
        candidate_mismatches=0,primary_bound_mismatches=0,original_config_hash=config_hash(old),corrected_config_hash=config_hash(config),
        evaluability_sha256=gate["evaluability_sha256"],original_solutions_sha256=sha256_file(Path("results/expA/solutions.csv")),
        audit_sha256=sha256_file(root/"H1H2_compatibility.csv"),implementation_sha256=sha256_file(Path(__file__)),
        bound_definition="Exact relaxed primary FCI bound used by Model, after removing item types without feasible candidates. Primary coefficients depend on unchanged demands, frequencies and durations.",
        limitation="Instance-variable counts and the secondary-objective weighting can change. This is not a claim that CP-SAT search traces or every scalar objective coefficient are identical.",
        reuse_basis="Each H1/H2 schedule has one sleep_1 occurrence, only at night, and no alternative-day schedule. Extra single sleepers cannot serve another demand; unused items cannot improve objectives and the model excludes them. Reuse requested by review F1.",
        outcomes_relabelled=False))
    print(json.dumps(dict(passed=True,units=len(units),checks=len(rows))))


if __name__=="__main__":main()
