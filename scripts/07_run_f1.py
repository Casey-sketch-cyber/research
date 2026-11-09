"""Isolated H3/H4 re-solves with reviewed bed caps and frozen production budgets."""
import os
for name in ("OPENBLAS_NUM_THREADS","OMP_NUM_THREADS","MKL_NUM_THREADS","NUMEXPR_NUM_THREADS"):
    os.environ[name]="1"
from concurrent.futures import ProcessPoolExecutor,wait,FIRST_COMPLETED
from copy import deepcopy
from datetime import datetime,timezone
import hashlib
import importlib.util
import json
from pathlib import Path
import time
import numpy as np
import pandas as pd
from tqdm import tqdm
from fea.config import config_hash
from fea.furniture.candidates import generate_candidates
from fea.furniture.library import library
from fea.geometry.raster import rasterize
from fea.geometry.unit import Unit
from fea.households import parse_households
from fea.io import prepare_cli,start_run,write_json,sha256_file
from fea.solve.cpsat import solve_layout
from fea.validate import validate_layout
from phase07_analysis import load_evaluable_solutions
from phase07_f1 import original_configuration,check_cases,CHANGED_HOUSEHOLDS,UNCHANGED_HOUSEHOLDS


def revision():
    spec=importlib.util.spec_from_file_location("F1_revision","scripts/06_revision.py")
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module


def solve_job(job):
    serialized,hname,config,cache,old_cache,fingerprint,main_scores=job
    unit=Unit.from_dict(json.loads(serialized));household=parse_households(config["households"],config["furniture"])[hname]
    grid=rasterize(unit,config["raster"]["resolution_m"],config["furniture"]["meta"]["walking_width"],config["raster"]["source_gap_close_m"])
    candidates=generate_candidates(grid,library(config["furniture"]),config["raster"]["orientations_deg"],config["raster"]["anchor_stride_m"])
    digest=config_hash(config);cache=Path(cache);layouts={};previous=None
    for strategy in ("S0","S1","S2"):
        name=unit.unit_key.replace(":","_")+"_"+hname.split("_")[0]+"_"+strategy+".json"
        old=json.loads((Path(old_cache)/name).read_text());old["strategy"]=strategy
        checked=validate_layout(old,grid,config,household)
        if not checked["pass"] or abs(checked["fci"]-main_scores[strategy])>1e-8:
            raise ValueError("F1 old incumbent invalid or rescored differently")
        incumbent=deepcopy(old)
        if previous is not None and (previous["fci"],-previous["tb"]) > (incumbent["fci"],-incumbent["tb"]):incumbent=deepcopy(previous)
        incumbent["strategy"],incumbent["config_hash"]=strategy,digest
        path=cache/name
        if path.exists():
            layout=json.loads(path.read_text())
            if layout["code_hash"]!=fingerprint or layout["config_hash"]!=digest:raise ValueError("F1 cached fingerprint mismatch")
        else:
            layout=solve_layout(unit,household,strategy,config,incumbent,(grid,candidates))
            layout["code_hash"],layout["config_hash"]=fingerprint,digest
            layout["warm_start_source"]="original A independently revalidated under corrected caps or preceding F1 strategy"
            write_json(path,layout)
        checked=validate_layout(layout,grid,config,household)
        if not checked["pass"] or abs(checked["fci"]-layout["fci"])>1e-8 or checked["fci"]<main_scores[strategy]-1e-8:
            raise ValueError("F1 independent score or incumbent retention failed")
        layouts[strategy]=layout;previous=layout
    layouts=revision().share(layouts,grid,config,household);rows=[]
    for strategy,layout in layouts.items():
        checked=validate_layout(layout,grid,config,household)
        if not checked["pass"] or abs(checked["fci"]-layout["fci"])>1e-8:raise ValueError("Shared F1 layout invalid")
        name=unit.unit_key.replace(":","_")+"_"+hname.split("_")[0]+"_"+strategy+".json";write_json(cache/"shared"/name,layout)
        sol=layout["solver"]
        rows.append(dict(unit_key=unit.unit_key,source=unit.source,nia_m2=unit.interior.area,household=hname,strategy=strategy,
            fci_validator=checked["fci"],fci_solver=sol["fci_solver"],tb=checked["tb"],validator_pass=checked["pass"],
            violations=";".join(checked["violations"]),n_items=len(layout["items"]),solve_time_s=sol["time_s"],
            status=sol["status"],termination=sol.get("termination",""),main_original_fci=main_scores[strategy],
            delta_from_original=checked["fci"]-main_scores[strategy],code_hash=fingerprint,config_hash=digest,layout_file=name,
            result_origin="F1_corrected_rerun",shared_from_strategy=sol.get("shared_from_strategy","")))
    return rows


def main():
    args=prepare_cli(__doc__).parse_args();config,_,_=start_run(args,"07_run_f1")
    if args.dry_run:print("Would require H1/H2 compatibility, then re-solve all evaluable H3/H4 cases with original budgets and isolated caches.");return
    root=Path("results/expA_f1");old_run=json.loads(Path("results/expA/run.json").read_text())
    old_config=original_configuration(config,old_run["base_config_hash"])
    old,gate=load_evaluable_solutions(old_config)
    compat=json.loads((root/"compatibility_acceptance.json").read_text())
    if not compat["passed"] or compat["corrected_config_hash"]!=config_hash(config) or compat["evaluability_sha256"]!=gate["evaluability_sha256"]:
        raise ValueError("F1 compatibility gate stale or failed")
    if compat["audit_sha256"]!=sha256_file(root/"H1H2_compatibility.csv"):raise ValueError("Compatibility table changed")
    signature=revision().signature()
    if signature!=old_run["production_settings"]["benchmark_driver_hash"]:raise ValueError("Numerical implementation changed since A")
    sample=old.drop_duplicates("unit_key")[["unit_key","source","nia_m2"]].sort_values("unit_key")
    sample.to_csv(root/"sample.csv",index=False)
    corpus=pd.read_parquet(Path(config["paths"]["processed"])/"corpus_units.parquet",columns=["unit_key","unit_json"]).set_index("unit_key")
    inputs=dict(corrected_config_hash=config_hash(config),original_config_hash=config_hash(old_config),numerical_signature=signature,
        original_solutions_sha256=sha256_file(Path("results/expA/solutions.csv")),evaluability_sha256=gate["evaluability_sha256"],
        sample_sha256=sha256_file(root/"sample.csv"),compatibility_sha256=sha256_file(root/"compatibility_acceptance.json"),
        driver_sha256=sha256_file(Path(__file__)),helper_sha256=sha256_file(Path("scripts/phase07_f1.py")))
    fingerprint=hashlib.sha256(json.dumps(inputs,sort_keys=True).encode()).hexdigest()
    cache=Path(config["paths"]["interim"])/"expA_f1"/fingerprint[:16]
    settings={name:old_run["production_settings"][name] for name in ["small","large"]}
    manifest=dict(inputs=inputs,units=len(sample),expected_rerun_cases=len(sample)*6,reused_cases=len(sample)*6,
        households=CHANGED_HOUSEHOLDS,strategies=["S0","S1","S2"],production_settings=settings,cache=cache.as_posix(),
        warm_start="Original same-case layouts revalidated under increased caps plus preceding strategy; every affected case calls the unchanged solver. Old H1/H2 scores and actual configuration hashes remain unchanged.")
    if (cache/"run.json").exists() and json.loads((cache/"run.json").read_text())!=manifest:raise ValueError("F1 resume fingerprint differs")
    if not (cache/"run.json").exists():write_json(cache/"run.json",manifest)
    started_at=datetime.fromtimestamp((cache/"run.json").stat().st_mtime,timezone.utc).isoformat(timespec="seconds")
    write_json(root/"config_snapshot.json",config);write_json(root/"original_config_snapshot.json",old_config)
    write_json(root/"run.json",{**manifest,"status":"running","started_at_utc":started_at})
    baseline=old.set_index(["unit_key","household","strategy"]).fci_validator
    rows=[];timing=[];started=time.perf_counter()
    for group in ["small","large"]:
        arm=settings[group];local=deepcopy(config);local["solver"].update(num_workers=arm["num_workers"],time_limit_s=arm["time_limit_s"])
        local["raster"]["anchor_stride_m"]=arm["anchor_stride_m"]
        subset=sample[sample.nia_m2<=20+1e-8] if group=="small" else sample[sample.nia_m2>20+1e-8]
        concurrency=max(1,14//arm["num_workers"])
        jobs=iter((corpus.loc[key,"unit_json"],h,local,str(cache/group),str(Path(old_run["cache"])/group/"shared"),fingerprint,
            {s:float(baseline.loc[key,h,s]) for s in ["S0","S1","S2"]}) for key in subset.unit_key for h in CHANGED_HOUSEHOLDS)
        group_started=time.perf_counter();prior=len(list((cache/group).glob("D*.json")))
        with ProcessPoolExecutor(max_workers=concurrency) as pool:
            active=set()
            for _ in range(concurrency*2):
                job=next(jobs,None)
                if job is not None:active.add(pool.submit(solve_job,job))
            with tqdm(total=len(subset)*2,desc="F1 "+group) as bar:
                while active:
                    finished,active=wait(active,return_when=FIRST_COMPLETED)
                    for future in finished:
                        rows.extend({**row,"budget_group":group} for row in future.result());bar.update(1)
                        job=next(jobs,None)
                        if job is not None:active.add(pool.submit(solve_job,job))
                    write_json(root/"progress.json",dict(completed_cases=len(rows),expected_cases=len(sample)*6,active_group=group,
                        elapsed_this_invocation_s=time.perf_counter()-started,observed_at_utc=datetime.now(timezone.utc).isoformat(timespec="seconds")))
        timing.append(dict(group=group,wall_time_s=time.perf_counter()-group_started,prior_checkpoints=prior,concurrency=concurrency))
    rerun=pd.DataFrame(rows).sort_values(["unit_key","household","strategy"]);accept=check_cases(rerun,sample.unit_key)
    rerun.to_csv(root/"H3H4_solutions.csv",index=False)
    reused=old[old.household.isin(UNCHANGED_HOUSEHOLDS)].copy();reused["result_origin"]="original_A_H1H2_verified_unaffected"
    reused.to_csv(root/"H1H2_reused.csv",index=False)
    combined=pd.concat([rerun,reused],ignore_index=True).sort_values(["unit_key","household","strategy"])
    all_check=check_cases(combined,sample.unit_key,config["households"]["main_households"]);combined.to_csv(root/"solutions.csv",index=False)
    write_json(root/"acceptance.json",dict(passed=True,rerun=accept,combined=all_check,excluded_units=gate["excluded_units"],
        input_provenance=inputs,H3H4_sha256=sha256_file(root/"H3H4_solutions.csv"),combined_sha256=sha256_file(root/"solutions.csv"),
        main_original_untouched=sha256_file(Path("results/expA/solutions.csv"))==inputs["original_solutions_sha256"]))
    write_json(root/"run.json",{**manifest,"status":"complete","started_at_utc":started_at,
        "completed_at_utc":datetime.now(timezone.utc).isoformat(timespec="seconds"),"timing":timing,"wall_time_this_invocation_s":time.perf_counter()-started})
    print(json.dumps(dict(passed=True,rerun_cases=len(rerun),combined_cases=len(combined))))


if __name__=="__main__":
    try:main()
    except Exception as error:
        root=Path("results/expA_f1");write_json(root/"error.json",dict(exception_type=type(error).__name__,observed_at_utc=datetime.now(timezone.utc).isoformat(timespec="seconds")))
        if (root/"run.json").exists():
            record=json.loads((root/"run.json").read_text());write_json(root/"run.json",{**record,"status":"failed"})
        raise
