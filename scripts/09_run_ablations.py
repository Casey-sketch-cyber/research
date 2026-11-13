"""Freeze and run all specified phase-9 sensitivity cases."""
from collections import Counter
from datetime import datetime, timezone
import fcntl
from pathlib import Path
import time

import numpy as np
import pandas as pd
from tqdm import tqdm

from fea.config import config_hash
from fea.io import prepare_cli, sha256_file, start_run, write_json
from phase07_corrected import load_corrected
from phase08_sampling import select_instances
from phase09_ablation_jobs import STRATEGIES, changed_config, run_ablation, verified_grid_recovery
from phase09_execution import apply_production, checked_inputs, cpu_slots, fingerprint, hash_inputs, load_json, run_weighted

ROOT = Path("results/ablations")
REF = Path("results/expA_f1")
B_SAMPLE = Path("results/expB/instances.csv")
EVALUABILITY = Path("results/expA/evaluability.csv")
GRID_RECOVERY = ROOT / "grid_recovery_source.json"
GRID_RECOVERY_PRIOR_SCRIPTS = {
    "scripts/09_run_ablations.py": "dc1f54f0d63023cf4775fd2958b4d73a812a480f2a5c2949aeb924b6f3956263",
    "scripts/phase09_ablation_jobs.py": "51c23bc99f92f749c7abbb5d93e18154fa4a0573de0bd3f842c6e0b5c58cd9ba",
}


def freeze_subset(config):
    """Balanced source-by-tercile sample, selected from geometry alone."""
    eligible = pd.read_csv(EVALUABILITY)
    assert config["ablations"]["resolution_m"]["subset"] == config["ablations"]["time_limit_s"]["subset"] == 50
    subset, quota, bounds = select_instances(eligible, ["geometry"], config["seed"], total=50)
    subset = subset.drop(columns=["household", "strategy"])
    ROOT.mkdir(parents=True, exist_ok=True)
    for name, table in [("subset.csv", subset), ("subset_allocation.csv", quota.drop(columns=["household"])), ("subset_terciles.csv", bounds)]:
        path = ROOT / name
        encoded = table.to_csv(index=False).encode("utf-8")
        if path.exists() and path.read_bytes() != encoded:
            raise ValueError("Frozen ablation sample differs: " + name)
        path.write_bytes(encoded)
    return subset


def enumerate_conditions(config, subset, benchmark):
    """Use the exact B pairs and the same 50 units for both numerical sweeps."""
    groups = config["households"]
    sweep = subset.merge(pd.DataFrame({"household": groups["main_households"]}), how="cross")
    physical = benchmark[["unit_key", "source", "nia_m2"]].drop_duplicates("unit_key")
    households = physical.merge(pd.DataFrame({"household": groups["main_households"] + groups["ablation_households"]}), how="cross")
    values = config["ablations"]
    yield "B200", "production", "matched", benchmark
    yield "fixed50", "production", "matched", sweep
    yield "B_units", "household", "each", households
    if values["drop_one_transformable"]:
        for item in sorted(config["furniture"]["transformable_items"]):
            yield "B200", "drop_one", item, benchmark
    for name in ("clearance_scale", "walking_width", "resolution_m", "time_limit_s"):
        group = "B200" if name in ("clearance_scale", "walking_width") else "fixed50"
        if group == "B200":
            candidates, pairs = values[name], benchmark
        else:
            candidates, pairs = values[name]["values"], sweep
        for value in candidates:
            yield group, name, value, pairs


def prerequisites(config):
    """Require the completed and hash-bound upstream packages."""
    for path in ["results/expB/report_acceptance.json", "results/expD/acceptance.json",
                 "results/expR/package_acceptance.json", "results/expA_f3/package_acceptance.json",
                 "results/expA_f1/analysis_p1/package_acceptance.json"]:
        gate = load_json(path)
        if not gate["passed"]:
            raise ValueError("Unaccepted prerequisite: " + path)
    rg = load_json("results/expR/package_acceptance.json")
    if rg["numerical_acceptance_sha256"] != sha256_file(Path("results/expR/acceptance.json")):
        raise ValueError("R acceptance differs")
    corrected, _ = load_corrected(config)
    return corrected


def accepted_references(frame):
    main, old = load_json(REF / "run.json"), load_json("results/expA/run.json")
    by_pair = {}
    for row in frame.to_dict("records"):
        source = old if row["result_origin"] == "original_A_H1H2_verified_unaffected" else main
        row["path"] = (Path(source["cache"]) / row["budget_group"] / "shared" / row["layout_file"]).as_posix()
        pair = row["unit_key"], row["household"]
        by_pair.setdefault(pair, {})[row["strategy"]] = row
    return by_pair, main["production_settings"]


def jobs_for(config, subset, benchmark, frame, corpus, cache, code):
    refs, production = accepted_references(frame)
    tasks = []
    for sample, kind, value, pairs in enumerate_conditions(config, subset, benchmark):
        for row in pairs.itertuples(index=False):
            unit_key, hh = row.unit_key, row.household
            cfg, _ = apply_production(config, production, row.nia_m2)
            altered = changed_config(cfg, kind, value)
            accepted = refs.get((unit_key, hh))
            key = fingerprint([sample, kind, value, unit_key, hh])[:24]
            tasks.append(dict(
                task_key=key, sample=sample, kind=kind, value=value, config=altered,
                anchor_adjusted=altered["raster"]["anchor_stride_m"] != cfg["raster"]["anchor_stride_m"],
                threads=altered["solver"]["num_workers"], unit_json=corpus.loc[unit_key, "unit_json"],
                household=hh, reference=accepted, exact_control=accepted is not None and config_hash(cfg) == config_hash(altered),
                cache=cache.as_posix(), fingerprint=code,
            ))
    if len({task["task_key"] for task in tasks}) != len(tasks):
        raise ValueError("Duplicate ablation cases")
    return tasks


def verify_cases(frame, expected):
    if frame.duplicated(["task_key", "strategy"]).any() or set(frame.task_key) != expected:
        raise ValueError("Ablation case membership differs")
    if len(frame) != len(expected) * len(STRATEGIES) or set(frame.strategy) != set(STRATEGIES):
        raise ValueError("Ablation triplets incomplete")
    if not np.isfinite(frame.fci_validator).all() or not frame.fci_validator.between(-1e-9, 1+1e-9).all():
        raise ValueError("Invalid ablation scores")
    if (~frame.validator_pass & ~frame.structural_unreachable).any():
        raise ValueError("Unexpected validation failure")
    anchor_steps = frame.anchor_stride_m / frame.resolution_m
    if (anchor_steps < 1 - 1e-9).any() or not np.allclose(anchor_steps, anchor_steps.round(), rtol=0, atol=1e-9):
        raise ValueError("An ablation anchor stride is incompatible with its grid")
    wide = frame.pivot(index="task_key", columns="strategy", values="fci_validator")
    if (wide.S1 + 1e-8 < wide.S0).any() or (wide.S2 + 1e-8 < wide.S1).any():
        raise ValueError("Ablation strategy ordering differs")


def grid_recovery_source(inputs, digest, old, progress):
    """Accept only the interrupted published grid implementation as a recovery source."""
    if GRID_RECOVERY.exists():
        receipt = load_json(GRID_RECOVERY)
    else:
        if old is None or not progress.exists():
            raise ValueError("The interrupted ablation attempt is missing")
        end = datetime.fromtimestamp(progress.stat().st_mtime, timezone.utc)
        start = datetime.fromisoformat(old["started_at_utc"])
        receipt = dict(prior_run=old, prior_progress=load_json(progress),
                       prior_ended_at_utc=end.isoformat(), prior_elapsed_seconds=(end-start).total_seconds(),
                       correction="Use a 0.20 m anchor on the 0.20 m collision raster when the reviewed small-home anchor was 0.10 m.")
    prior = receipt["prior_run"]
    if (prior["status"] != "failed" or prior.get("exception_type") != "ValueError"
            or prior["config_hash"] != digest or set(prior["inputs"]) != set(inputs)
            or prior["code_hash"] != fingerprint(dict(inputs=prior["inputs"], config_hash=digest))):
        raise ValueError("Unrecognized interrupted grid attempt")
    changed = {name for name in inputs if prior["inputs"][name] != inputs[name]}
    if changed != set(GRID_RECOVERY_PRIOR_SCRIPTS) or any(
        prior["inputs"][name] != expected for name, expected in GRID_RECOVERY_PRIOR_SCRIPTS.items()
    ):
        raise ValueError("Recovery inputs differ beyond the two documented grid-repair scripts")
    prior_cache = Path(prior["cache"])
    if prior_cache != Path("data/interim/ablations") / prior["code_hash"][:18]:
        raise ValueError("Unexpected original ablation cache")
    if not GRID_RECOVERY.exists():
        write_json(GRID_RECOVERY, receipt)
    return receipt, prior_cache


def main():
    parser = prepare_cli(__doc__)
    parser.add_argument("--prepare", action="store_true")
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--slots", type=int, default=None)
    parser.add_argument("--resume-grid-fix", action="store_true",
                        help="Verify and reuse identical completed triplets from the interrupted grid attempt.")
    args = parser.parse_args()
    config, digest, _ = start_run(args, "09_run_ablations")
    if args.dry_run:
        print("Use 50 geometry-selected units for resolution/time, the 200 B pairs for geometry/item ablations, and H5 on the B units.")
        return
    subset = freeze_subset(config)
    if args.prepare:
        print(f"Frozen {len(subset)} units")
        return
    with (ROOT / ".run.lock").open("w") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        run(config, digest, subset, args)


def run(config, digest, subset, args):
    corrected = prerequisites(config)
    benchmark = pd.read_csv(B_SAMPLE)
    if len(benchmark) != 200 or benchmark.duplicated(["unit_key", "household"]).any():
        raise ValueError("B pairs changed")
    corpus_path = Path(config["paths"]["processed"]) / "corpus_units.parquet"
    files = [
        REF / "acceptance.json", REF / "solutions.csv", REF / "run.json", "results/expA/run.json",
        "results/expB/report_acceptance.json", B_SAMPLE, "results/expD/acceptance.json",
        "results/expR/package_acceptance.json", "results/expA_f3/package_acceptance.json",
        "results/expA_f1/analysis_p1/package_acceptance.json", ROOT / "subset.csv", corpus_path,
        "scripts/09_run_ablations.py", "scripts/phase09_ablation_jobs.py", "scripts/phase09_execution.py",
        "scripts/06_revision.py", "scripts/phase08_sampling.py", *sorted(Path("src/fea").rglob("*.py")),
    ]
    inputs = hash_inputs(files)
    code = fingerprint(dict(inputs=inputs, config_hash=digest))
    cache = Path(config["paths"]["interim"]) / "ablations" / code[:18]
    previous = ROOT / "run.json"
    progress = ROOT / "progress.json"
    old = load_json(previous) if previous.exists() else None
    recovery = grid_recovery_source(inputs, digest, old, progress) if args.resume_grid_fix else None
    allowed_codes = {code} | ({recovery[0]["prior_run"]["code_hash"]} if recovery else set())
    if old and old["code_hash"] not in allowed_codes:
        raise ValueError("Ablation inputs changed after the run was frozen")
    if GRID_RECOVERY.exists() and not recovery:
        raise ValueError("Resume the grid recovery with --resume-grid-fix")
    corpus = pd.read_parquet(corpus_path, columns=["unit_key", "unit_json"]).set_index("unit_key")
    tasks = jobs_for(config, subset, benchmark, corrected, corpus, cache, code)
    slots = min(args.slots or cpu_slots(), cpu_slots())
    if args.smoke:
        choose = [next(task for task in tasks if task["anchor_adjusted"])] if recovery else [
            next(task for task in tasks if task["exact_control"] and task["sample"] == "B200"),
            next(task for task in tasks if task["kind"] == "drop_one" and task["threads"] == 1),
            next(task for task in tasks if task["kind"] == "resolution_m" and task["value"] == .05 and task["threads"] == 1),
            next(task for task in tasks if task["anchor_adjusted"]),
        ]
        rows = [r for group in run_weighted(run_ablation, choose, slots) for r in group]
        verify_cases(pd.DataFrame(rows), {task["task_key"] for task in choose})
        print(f"Verified {len(rows)} smoke results in the final checkpoint namespace")
        return
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    record = dict(status="running", started_at_utc=now, code_hash=code, config_hash=digest, inputs=inputs,
                  expected_triplets=len(tasks), expected_layouts=len(tasks)*3, cache=cache.as_posix(),
                  cpu_slots=slots, started_from_checkpoint=previous.exists(),
                  grid_recovery_source_sha256=sha256_file(GRID_RECOVERY) if recovery else None,
                  adjusted_grid_triplets=sum(t["anchor_adjusted"] for t in tasks))
    write_json(previous, record)
    expected = {task["task_key"] for task in tasks}
    began = time.perf_counter()
    rows = []
    try:
        pending = []
        for task in tasks:
            inherited = verified_grid_recovery(task, recovery[1], recovery[0]["prior_run"]["code_hash"]) if recovery else None
            if inherited is None:
                pending.append(task)
            else:
                rows.extend(inherited)
        reused = len(rows) // 3
        write_json(progress, dict(status="running", completed=len(rows), expected=3*len(tasks),
                                  completed_triplets=reused, expected_triplets=len(tasks)))
        for result in tqdm(run_weighted(run_ablation, pending, slots), total=len(tasks), initial=reused, desc="Ablation triplets"):
            rows.extend(result)
            if len(rows) % 30 == 0 or len(rows) == 3 * len(tasks):
                write_json(progress, dict(status="running", completed=len(rows), expected=3*len(tasks),
                                          completed_triplets=len(rows)//3, expected_triplets=len(tasks)))
        frame = pd.DataFrame(rows).sort_values(["sample", "ablation", "value", "household", "unit_key", "strategy"], key=lambda v: v.astype(str))
        verify_cases(frame, expected)
        checked_inputs(inputs)
        path = ROOT / "cases.csv"
        frame.to_csv(path, index=False)
        counts = {str(k): int(v) for k, v in Counter(frame.own_origin).items()}
        write_json(ROOT / "acceptance.json", dict(
            passed=True, layouts=len(frame), triplets=len(tasks), code_hash=code,
            structurally_unreachable=int(frame.structural_unreachable.sum()), own_origin_counts=counts,
            verified_previous_triplets=reused, adjusted_grid_triplets=record["adjusted_grid_triplets"],
            cases_sha256=sha256_file(path), independent_validation=True,
        ))
        write_json(previous, {**record, "status": "complete",
                              "completed_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                              "verified_previous_triplets": reused,
                              "prior_failed_attempt_seconds": recovery[0]["prior_elapsed_seconds"] if recovery else None,
                              "wall_time_this_invocation_s": time.perf_counter()-began})
        write_json(progress, dict(status="complete", completed=len(frame), expected=3*len(tasks),
                                  completed_triplets=len(tasks), expected_triplets=len(tasks)))
    except Exception as error:
        write_json(progress, dict(status="failed", completed=len(rows), expected=3*len(tasks),
                                  exception_type=type(error).__name__))
        write_json(previous, {**record, "status": "failed", "exception_type": type(error).__name__})
        raise


if __name__ == "__main__":
    main()
