"""Guarded, resumable full-sample Experiment A with size-dependent solve budgets."""
from __future__ import annotations

import os
for _name in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ[_name] = "1"

from concurrent.futures import ProcessPoolExecutor, wait, FIRST_COMPLETED
from copy import deepcopy
import hashlib
import importlib.util
import json
from pathlib import Path
import time

import pandas as pd
from tqdm import tqdm

from fea.config import config_hash
from fea.io import prepare_cli, start_run, write_json


def load_driver(filename, name):
    """Load a numbered phase driver without changing its experiment semantics."""
    spec = importlib.util.spec_from_file_location(name, filename)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def solve_job(job):
    """Reuse the independently validated three-strategy solver and exchange."""
    driver = load_driver("scripts/06_revision.py", "revision_worker")
    return driver.solve_triplet(job)


def check_selection(selection: dict, numerical_hash: str):
    """Reject an unreviewed or stale production setting, even on resume."""
    for key in ("accepted", "mechanism_pass", "source_quality_pass", "small_quality_pass"):
        if selection.get(key) is not True:
            raise ValueError("Round-2 acceptance missing: "+key)
    if selection.get("numerical_hash") != numerical_hash:
        raise ValueError("Production selection predates the current numerical implementation")
    if not 0 < selection.get("projected_expA_hours", float("inf")) <= 36:
        raise ValueError("Experiment A must fit the reviewed 36-hour projection")
    if selection.get("small_nia_max_m2") != 20:
        raise ValueError("The reviewed size-dependent boundary is NIA <=20 m²")
    for key in ("small", "large"):
        arm = selection[key]
        if arm["num_workers"] not in (1, 2, 4, 8) or arm["anchor_stride_m"] not in (.1, .2):
            raise ValueError("Unbenchmarked production parameters")
        if arm["time_limit_s"] not in (30, 60, 120, 300):
            raise ValueError("Unbenchmarked time limit")


def main():
    parser = prepare_cli(__doc__)
    parser.add_argument("--selection", default="results/pilot/round2/production_selection.json")
    args = parser.parse_args()
    config, _, _ = start_run(args, "07_run_expA")
    if args.dry_run:
        print("Would require round-2 acceptance, then resume all frozen sample × household × strategy cases. No uploads.")
        return
    selection_path = Path(args.selection)
    if not selection_path.is_file():
        raise RuntimeError("Round-2 production selection is not complete; no formal experiment started")
    selection = json.loads(selection_path.read_text())
    round2 = load_driver("scripts/06_round2.py", "round2_signature")
    numerical = round2.code_hash()
    check_selection(selection, numerical)
    sample_path = Path(selection.get("sample_path", "results/corpus/expA_sample.csv"))
    sample = pd.read_csv(sample_path)
    sample_hash = hashlib.sha256(sample_path.read_bytes()).hexdigest()
    if sample_hash != selection["sample_sha256"]:
        raise ValueError("Frozen sample changed after budget selection")
    if sample.unit_key.duplicated().any():
        raise ValueError("Duplicate sample units")
    original = pd.read_csv("results/corpus/expA_sample.csv")
    mandatory = set(original.loc[(original.source == "D3") & (original.nia_m2 <= 20+1e-8), "unit_key"])
    if not mandatory <= set(sample.unit_key):
        raise ValueError("A sample cap dropped a mandatory small D3 shell")
    frame = pd.read_parquet(Path(config["paths"]["processed"])/"corpus_units.parquet",
                             columns=["unit_key", "unit_json"]).set_index("unit_key")
    units = frame.loc[sample.unit_key, "unit_json"].to_dict()
    input_hash = hashlib.sha256("".join(units[key] for key in sorted(units)).encode()).hexdigest()
    files = [Path("scripts/07_run_expA.py"), Path("scripts/06_revision.py")]
    code = hashlib.sha256(numerical.encode()+b"".join(p.read_bytes() for p in files)).hexdigest()
    manifest = dict(code_hash=code, numerical_hash=numerical, sample_sha256=sample_hash,
        inputs_hash=input_hash, selection_sha256=hashlib.sha256(selection_path.read_bytes()).hexdigest(),
        base_config_hash=config_hash(config), expected_cases=len(sample)*len(config["households"]["main_households"])*3,
        selected_units=len(sample), production_settings=selection, automatic_publication=False)
    cache = Path(config["paths"]["interim"])/"expA"/(code[:12]+"_"+manifest["selection_sha256"][:12])
    if (cache/"run.json").exists() and json.loads((cache/"run.json").read_text()) != manifest:
        raise ValueError("Existing run fingerprint differs; do not mix results")
    write_json(cache/"run.json", manifest)
    rows, timing = [], []
    for group in ("small", "large"):
        settings = selection[group]
        run_config = deepcopy(config)
        run_config["solver"].update(num_workers=settings["num_workers"], time_limit_s=settings["time_limit_s"])
        run_config["raster"]["anchor_stride_m"] = settings["anchor_stride_m"]
        subset = sample[sample.nia_m2 <= 20+1e-8] if group == "small" else sample[sample.nia_m2 > 20+1e-8]
        concurrency = max(1, 14//settings["num_workers"])
        jobs = iter((json.loads(units[key]), h, run_config, str(cache/group), code)
                    for key in subset.unit_key for h in config["households"]["main_households"])
        before = len(list((cache/group).glob("*.json")))
        started = time.perf_counter()
        with ProcessPoolExecutor(max_workers=concurrency) as pool:
            active = set()
            for _ in range(concurrency*2):
                job = next(jobs, None)
                if job is not None:
                    active.add(pool.submit(solve_job, job))
            with tqdm(total=len(subset)*len(config["households"]["main_households"]), desc="ExpA "+group) as bar:
                while active:
                    finished, active = wait(active, return_when=FIRST_COMPLETED)
                    for future in finished:
                        rows.extend({**row, "budget_group": group} for row in future.result())
                        bar.update(1)
                        job = next(jobs, None)
                        if job is not None:
                            active.add(pool.submit(solve_job, job))
                    write_json(cache/"progress.json", dict(completed_cases=len(rows), expected_cases=manifest["expected_cases"], group=group))
        timing.append(dict(group=group, wall_time_s=time.perf_counter()-started,
                           prior_checkpoints=before, concurrency=concurrency, num_workers=settings["num_workers"]))
    result = pd.DataFrame(rows).sort_values(["unit_key", "household", "strategy"])
    if len(result) != manifest["expected_cases"] or result.duplicated(["unit_key", "household", "strategy"]).any():
        raise RuntimeError("Incomplete or duplicated Experiment A table")
    pivot = result.pivot(index=["unit_key", "household"], columns="strategy", values="fci_validator")
    ordering_failures = int(((pivot.S2 < pivot.S1-1e-8) | (pivot.S1 < pivot.S0-1e-8)).sum())
    output = Path("results/expA")
    output.mkdir(parents=True, exist_ok=True)
    result.to_csv(output/"solutions.csv", index=False)
    write_json(output/"run.json", {**manifest, "timing": timing, "cache": cache.as_posix()})
    zero = (result.fci_validator <= 1e-9)
    acceptance = dict(completed_cases=len(result), expected_cases=manifest["expected_cases"],
        invalid_cases=int((~result.validator_pass).sum()), zero_service_cases=int(zero.sum()),
        zero_service_rate=float(zero.mean()), ordering_failures=ordering_failures,
        status_distribution=result.status.value_counts().to_dict(),
        passed=bool(result.validator_pass.all() and ordering_failures == 0 and zero.mean() < .05))
    write_json(output/"solve_acceptance.json", acceptance)
    print(json.dumps(acceptance))


if __name__ == "__main__":
    main()
