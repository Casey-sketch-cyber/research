"""Reviewed H3-only mirrored-access sensitivity after accepted corrected F1/F2."""
import os
for name in ("OPENBLAS_NUM_THREADS","OMP_NUM_THREADS","MKL_NUM_THREADS","NUMEXPR_NUM_THREADS"):os.environ[name]="1"
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
from phase07_corrected import load_corrected
from phase07_f1 import check_cases
from phase07_f3 import HOUSEHOLDS,variant_config,mapped_incumbent


def revision():
    spec=importlib.util.spec_from_file_location("f3_revision","scripts/06_revision.py");module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module


def solve_job(job: tuple) -> list:
    serialized,config,cache,main_cache,fingerprint,main_scores=job;hname=HOUSEHOLDS[0]
    unit=Unit.from_dict(json.loads(serialized));household=parse_households(config["households"],config["furniture"])[hname]
    grid=rasterize(unit,config["raster"]["resolution_m"],config["furniture"]["meta"]["walking_width"],config["raster"]["source_gap_close_m"])
    candidates=generate_candidates(grid,library(config["furniture"]),config["raster"]["orientations_deg"],config["raster"]["anchor_stride_m"])
    digest=config_hash(config);cache=Path(cache);layouts={};mapping={};previous=None
    for strategy in ["S0","S1","S2"]:
        name=unit.unit_key.replace(":","_")+"_H3_"+strategy+".json";baseline=json.loads((Path(main_cache)/name).read_text())
        if baseline["unit_key"]!=unit.unit_key or baseline["household"]!=hname or baseline["strategy"]!=strategy or abs(baseline["fci"]-main_scores[strategy])>1e-8:raise ValueError("F3 baseline layout differs from corrected F1")
        incumbent,mapping[strategy]=mapped_incumbent(baseline,grid,config,household)
        if previous is not None and (incumbent is None or (previous["fci"],-previous["tb"])>(incumbent["fci"],-incumbent["tb"])):incumbent=deepcopy(previous)
        if incumbent is not None:incumbent["strategy"]=strategy;incumbent["config_hash"]=digest
        path=cache/name
        if path.exists():
            layout=json.loads(path.read_text())
            if layout["code_hash"]!=fingerprint or layout["config_hash"]!=digest:raise ValueError("F3 checkpoint provenance changed")
        else:
            layout=solve_layout(unit,household,strategy,config,incumbent,(grid,candidates));layout["code_hash"],layout["config_hash"]=fingerprint,digest
            layout["warm_start_source"]="corrected F1 remapped across physical side choices and independently rescored, or preceding F3 strategy"
            write_json(path,layout)
        checked=validate_layout(layout,grid,config,household)
        if not checked["pass"] or abs(checked["fci"]-layout["fci"])>1e-8:raise ValueError("F3 independent validation failed")
        if incumbent is not None and checked["fci"]<incumbent["fci"]-1e-8:raise ValueError("F3 discarded a better valid mapped incumbent")
        layouts[strategy]=layout;previous=layout
    layouts=revision().share(layouts,grid,config,household);rows=[]
    for strategy,layout in layouts.items():
        checked=validate_layout(layout,grid,config,household)
        if not checked["pass"] or abs(checked["fci"]-layout["fci"])>1e-8:raise ValueError("Shared F3 layout invalid")
        name=unit.unit_key.replace(":","_")+"_H3_"+strategy+".json";write_json(cache/"shared"/name,layout)
        rows.append(dict(unit_key=unit.unit_key,source=unit.source,nia_m2=unit.interior.area,household=hname,strategy=strategy,
            fci_validator=checked["fci"],fci_solver=layout["solver"]["fci_solver"],validator_pass=checked["pass"],tb=checked["tb"],
            violations=";".join(checked["violations"]),n_items=len(layout["items"]),status=layout["solver"]["status"],
            solve_time_s=layout["solver"]["time_s"],main_fci=main_scores[strategy],delta_fci=checked["fci"]-main_scores[strategy],
            **mapping[strategy],config_hash=digest,code_hash=fingerprint,layout_file=name))
    return rows


def main():
    args=prepare_cli(__doc__).parse_args();config,_,_=start_run(args,"07_run_f3")
    if args.dry_run:print("Would require accepted corrected F1/F2 and execute 1044 H3 mirror-choice cases with shared inventory and original small-home settings.");return
    import fcntl
    with Path(".tmp/f3_execution.lock").open("a") as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB);execute(config)


def execute(config: dict) -> None:
    preflight_path=Path("results/expA_f3/preflight.json");preflight=json.loads(preflight_path.read_text())
    if not preflight["passed"] or preflight["numerical_signature"]!=revision().signature():raise ValueError("F3 preflight failed or numerical source changed")
    for name,digest in preflight["implementation"].items():
        if sha256_file(Path(name))!=digest:raise ValueError("F3 preflight implementation changed")
    solutions,accepted=load_corrected(config);f2_path=Path("results/expA_f1/analysis/package_acceptance.json");f2=json.loads(f2_path.read_text())
    if not f2["passed"] or not f2["full_F2_package_complete"] or f2["F1_solutions_sha256"]!=accepted["combined_sha256"]:raise ValueError("F2 package does not permit F3")
    for path,key in [(Path("config/f2_visual_review.json"),"visual_review_sha256"),(Path("results/expA_f1/analysis/acceptance.json"),"numerical_acceptance_sha256")]:
        if sha256_file(path)!=f2[key]:raise ValueError("F2 acceptance input changed")
    main_run=json.loads(Path("results/expA_f1/run.json").read_text());root=Path("results/expA_f3");root.mkdir(parents=True,exist_ok=True)
    sample=solutions[solutions.nia_m2<=20+1e-8].drop_duplicates("unit_key")[["unit_key","source","nia_m2"]].sort_values("unit_key")
    old_sample=pd.read_csv("results/expA2/sample.csv").sort_values("unit_key").reset_index(drop=True)
    if not sample.unit_key.reset_index(drop=True).equals(old_sample.unit_key) or not np.allclose(sample.nia_m2,old_sample.nia_m2,rtol=0,atol=1e-8):raise ValueError("F3 must use the exact old small-unit set")
    sample.to_csv(root/"sample.csv",index=False);variant=variant_config(config)
    inputs=dict(preflight_sha256=sha256_file(preflight_path),F1_solutions_sha256=accepted["combined_sha256"],F2_package_sha256=sha256_file(f2_path),sample_sha256=sha256_file(root/"sample.csv"),
        original_A2_sample_sha256=sha256_file(Path("results/expA2/sample.csv")),main_config_hash=config_hash(config),variant_config_hash=config_hash(variant),
        main_numerical_signature=main_run["inputs"]["numerical_signature"],F3_numerical_signature=revision().signature(),
        override_sha256=sha256_file(Path("config/f3_overrides.yaml")),driver_sha256=sha256_file(Path(__file__)),helper_sha256=sha256_file(Path("scripts/phase07_f3.py")))
    fingerprint=hashlib.sha256(json.dumps(inputs,sort_keys=True).encode()).hexdigest();cache=Path(config["paths"]["interim"])/"expA_f3"/fingerprint[:16]
    manifest=dict(inputs=inputs,units=len(sample),households=HOUSEHOLDS,strategies=["S0","S1","S2"],expected_cases=len(sample)*3,
        cache=cache.as_posix(),concurrency=3,time_limit_s=120,num_workers=4,anchor_stride_m=.1,
        variant="Left/right physical variants, 0.60 m on the chosen side only; original family caps shared across aliases.",
        limitations="Main right strips were 0.50 m and sofa_bed used front 0.50 m; this exact sensitivity is not a universal superset. Keep negative changes and mapping failures.")
    signature=cache/"run.json"
    if signature.exists() and json.loads(signature.read_text())!=manifest:raise ValueError("F3 resume provenance differs")
    if not signature.exists():write_json(signature,manifest)
    started_at=datetime.fromtimestamp(signature.stat().st_mtime,timezone.utc).isoformat(timespec="seconds")
    write_json(root/"run.json",{**manifest,"status":"running","started_at_utc":started_at});write_json(root/"config_snapshot.json",variant)
    corpus=pd.read_parquet(Path(config["paths"]["processed"])/"corpus_units.parquet",columns=["unit_key","unit_json"]).set_index("unit_key")
    baseline=solutions.set_index(["unit_key","household","strategy"]).fci_validator
    jobs=iter((corpus.loc[key,"unit_json"],variant,str(cache),str(Path(main_run["cache"])/"small"/"shared"),fingerprint,
        {s:float(baseline.loc[key,HOUSEHOLDS[0],s]) for s in ["S0","S1","S2"]}) for key in sample.unit_key)
    rows=[];started=time.perf_counter()
    with ProcessPoolExecutor(max_workers=3) as pool:
        active=set()
        for _ in range(6):
            job=next(jobs,None)
            if job is not None:active.add(pool.submit(solve_job,job))
        with tqdm(total=len(sample),desc="F3 H3 mirrored-access triplets") as bar:
            while active:
                finished,active=wait(active,return_when=FIRST_COMPLETED)
                for future in finished:
                    rows.extend(future.result());bar.update(1);job=next(jobs,None)
                    if job is not None:active.add(pool.submit(solve_job,job))
                write_json(root/"progress.json",dict(completed_cases=len(rows),expected_cases=len(sample)*3,
                    elapsed_this_invocation_s=time.perf_counter()-started,observed_at_utc=datetime.now(timezone.utc).isoformat(timespec="seconds")))
    result=pd.DataFrame(rows).sort_values(["unit_key","household","strategy"]);check=check_cases(result,sample.unit_key,HOUSEHOLDS)
    result.to_csv(root/"solutions.csv",index=False);write_json(root/"acceptance.json",{**check,"solutions_sha256":sha256_file(root/"solutions.csv"),
        "negative_vs_main":int((result.delta_fci<-1e-8).sum()),"status_distribution":result.status.value_counts().to_dict()})
    write_json(root/"run.json",{**manifest,"status":"complete","started_at_utc":started_at,"completed_at_utc":datetime.now(timezone.utc).isoformat(timespec="seconds"),"wall_time_this_invocation_s":time.perf_counter()-started})
    print(json.dumps(check))


if __name__=="__main__":
    try:main()
    except BlockingIOError:
        raise SystemExit("F3 is already active; duplicate launch refused")
    except Exception as error:
        root=Path("results/expA_f3");write_json(root/"error.json",dict(exception_type=type(error).__name__,observed_at_utc=datetime.now(timezone.utc).isoformat(timespec="seconds")))
        if (root/"run.json").exists():write_json(root/"run.json",{**json.loads((root/"run.json").read_text()),"status":"failed"})
        raise
