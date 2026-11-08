"""Resumable approved one-side bed-access sensitivity on all evaluable small A units."""
import os
for _name in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ[_name] = "1"

from concurrent.futures import ProcessPoolExecutor, wait, FIRST_COMPLETED
from copy import deepcopy
from datetime import datetime, timezone
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
from fea.io import prepare_cli, sha256_file, start_run, write_json
from fea.solve.cpsat import solve_layout
from fea.validate import validate_layout
from phase07_a2 import HOUSEHOLDS, acceptance, variant_config
from phase07_analysis import load_evaluable_solutions


def revision():
    spec = importlib.util.spec_from_file_location("a2_revision", "scripts/06_revision.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def solve_job(job):
    serialized, hname, config, cache_dir, main_cache, fingerprint, main_scores = job
    unit = Unit.from_dict(json.loads(serialized))
    household = parse_households(config["households"], config["furniture"])[hname]
    grid = rasterize(unit, config["raster"]["resolution_m"], config["furniture"]["meta"]["walking_width"], config["raster"]["source_gap_close_m"])
    candidates = generate_candidates(grid, library(config["furniture"]), config["raster"]["orientations_deg"], config["raster"]["anchor_stride_m"])
    digest = config_hash(config)
    layouts, main_validity = {}, {}
    previous = None
    cache = Path(cache_dir)
    for strategy in ("S0", "S1", "S2"):
        name = unit.unit_key.replace(":", "_")+"_"+hname.split("_")[0]+"_"+strategy+".json"
        baseline = json.loads((Path(main_cache)/name).read_text())
        if (baseline["unit_key"] != unit.unit_key or baseline["household"] != hname
                or baseline["strategy"] != strategy or abs(baseline["fci"]-main_scores[strategy]) > 1e-8):
            raise ValueError("A2 warm-start layout differs from its frozen main record")
        main_checked = validate_layout(baseline, grid, config, household)
        main_validity[strategy] = main_checked["pass"]
        incumbent = deepcopy(previous) if previous is not None else None
        if incumbent is not None:
            incumbent["strategy"] = strategy
        if main_checked["pass"] and (incumbent is None or main_checked["fci"] > incumbent["fci"]+1e-9):
            incumbent = deepcopy(baseline)
            incumbent["config_hash"] = digest
            incumbent["warm_start_source"] = "frozen_main_A_revalidated_under_A2"
        path = cache/name
        if path.exists():
            layout = json.loads(path.read_text())
            if layout["code_hash"] != fingerprint or layout["config_hash"] != digest:
                raise ValueError("A2 cached fingerprint mismatch")
        else:
            layout = solve_layout(unit, household, strategy, config, incumbent, (grid, candidates))
            layout["code_hash"], layout["config_hash"] = fingerprint, digest
            write_json(path, layout)
        checked = validate_layout(layout, grid, config, household)
        if not checked["pass"] or abs(checked["fci"]-layout["fci"]) > 1e-8:
            raise ValueError("A2 layout failed independent validation")
        layouts[strategy] = layout
        previous = layout
    layouts = revision().share(layouts, grid, config, household)
    rows = []
    for strategy, layout in layouts.items():
        checked = validate_layout(layout, grid, config, household)
        name = unit.unit_key.replace(":", "_")+"_"+hname.split("_")[0]+"_"+strategy+".json"
        write_json(cache/"shared"/name, layout)
        rows.append(dict(unit_key=unit.unit_key, source=unit.source, nia_m2=unit.interior.area,
            household=hname, strategy=strategy, fci_validator=checked["fci"], validator_pass=checked["pass"],
            violations=";".join(checked["violations"]), tb=checked["tb"], n_items=len(layout["items"]),
            solve_time_s=layout["solver"]["time_s"], status=layout["solver"]["status"],
            main_fci=main_scores[strategy], main_layout_valid_under_variant=main_validity[strategy],
            delta_fci=checked["fci"]-main_scores[strategy], config_hash=digest, code_hash=fingerprint,
            layout_file=name))
    return rows


def main():
    args = prepare_cli(__doc__).parse_args()
    config, _, _ = start_run(args, "07_run_a2")
    if args.dry_run:
        print("Would require accepted A1 evidence, freeze evaluable small units, and solve H3/H4 × S0/S1/S2 under the explicit one-side override.")
        return
    main_solutions, analysis_acceptance = load_evaluable_solutions(config)
    package = json.loads(Path("results/expA/analysis_package_acceptance.json").read_text())
    if not package["passed"] or package["evaluability_sha256"] != analysis_acceptance["evaluability_sha256"]:
        raise ValueError("A1 package is not accepted for continuation")
    main_run = json.loads(Path("results/expA/run.json").read_text())
    if config_hash(config) != main_run["base_config_hash"] or revision().signature() != main_run["production_settings"]["benchmark_driver_hash"]:
        raise ValueError("Main numerical inputs changed after frozen A")
    sample = main_solutions[main_solutions.nia_m2 <= 20+1e-8].drop_duplicates("unit_key")[["unit_key", "source", "nia_m2"]].sort_values("unit_key")
    root = Path("results/expA2")
    root.mkdir(parents=True, exist_ok=True)
    sample.to_csv(root/"sample.csv", index=False)
    variant = variant_config(config)
    inputs = dict(main_solutions_sha256=sha256_file(Path("results/expA/solutions.csv")),
        main_code_hash=main_run["code_hash"], sample_sha256=sha256_file(root/"sample.csv"),
        evaluability_sha256=analysis_acceptance["evaluability_sha256"], config_hash=config_hash(variant),
        override_sha256=sha256_file(Path("config/a2_overrides.yaml")),
        driver_sha256=sha256_file(Path(__file__)), helper_sha256=sha256_file(Path("scripts/phase07_a2.py")))
    fingerprint = hashlib.sha256(json.dumps(inputs, sort_keys=True).encode()).hexdigest()
    cache = Path(config["paths"]["interim"])/"expA2"/fingerprint[:16]
    cache.mkdir(parents=True, exist_ok=True)
    manifest = dict(inputs=inputs, units=len(sample), households=HOUSEHOLDS, strategies=["S0", "S1", "S2"],
        expected_cases=len(sample)*6, config=variant, numerical_change="explicit A2 furniture override only",
        concurrency=3, per_solve_workers=4, time_limit_s=120, cache=cache.as_posix(),
        warm_start="original A layouts revalidated under A2 plus preceding strategy; invalid old layouts are not reused",
        limitations="Fixed local-left access with four rotations; no mirrored-family search. Original sofa_bed had front-only 0.50 m clearance, so A2 is not a uniform relaxation of all items.")
    manifest = json.loads(json.dumps(manifest))  # Normalize integer mapping keys for resumable equality.
    signature_path = cache/"run.json"
    if signature_path.exists() and json.loads(signature_path.read_text()) != manifest:
        raise ValueError("A2 existing run differs; do not mix outcomes")
    write_json(signature_path, manifest)
    write_json(root/"run.json", {**manifest, "status":"running"})
    corpus = pd.read_parquet(Path(config["paths"]["processed"])/"corpus_units.parquet", columns=["unit_key", "unit_json"]).set_index("unit_key")
    baseline = main_solutions.set_index(["unit_key", "household", "strategy"]).fci_validator
    jobs = iter((corpus.loc[key, "unit_json"], h, variant, str(cache), str(Path(main_run["cache"])/"small"/"shared"), fingerprint,
        {s:float(baseline.loc[key, h, s]) for s in ("S0", "S1", "S2")}) for key in sample.unit_key for h in HOUSEHOLDS)
    rows = []
    started = time.perf_counter()
    with ProcessPoolExecutor(max_workers=3) as pool:
        active = set()
        for _ in range(6):
            job = next(jobs, None)
            if job is not None: active.add(pool.submit(solve_job, job))
        with tqdm(total=len(sample)*2, desc="A2 unit/household triplets") as progress:
            while active:
                finished, active = wait(active, return_when=FIRST_COMPLETED)
                for future in finished:
                    rows.extend(future.result())
                    progress.update(1)
                    job = next(jobs, None)
                    if job is not None: active.add(pool.submit(solve_job, job))
                write_json(root/"progress.json", dict(completed_cases=len(rows), expected_cases=len(sample)*6,
                    elapsed_this_invocation_s=time.perf_counter()-started))
    result = pd.DataFrame(rows).sort_values(["unit_key", "household", "strategy"])
    result.to_csv(root/"solutions.csv", index=False)
    check = acceptance(result, sample.unit_key)
    write_json(root/"acceptance.json", check)
    write_json(root/"run.json", {**manifest, "status":"complete", "wall_time_this_invocation_s":time.perf_counter()-started})
    write_json(root/"config_snapshot.json", variant)
    print(json.dumps(check))


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        root = Path("results/expA2")
        write_json(root/"error.json", dict(exception_type=type(error).__name__,
            observed_at_utc=datetime.now(timezone.utc).isoformat(timespec="seconds")))
        if (root/"run.json").exists():
            record = json.loads((root/"run.json").read_text())
            write_json(root/"run.json", {**record, "status":"failed"})
        raise
