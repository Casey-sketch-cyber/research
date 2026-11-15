"""Run the 60 prescribed warm-started K3 S2 searches."""

from datetime import datetime, timezone
from pathlib import Path
import time

import pandas as pd
from tqdm import tqdm

from fea.config import config_hash
from fea.furniture.candidates import generate_candidates
from fea.furniture.library import library
from fea.io import prepare_cli, sha256_file, start_run, write_json
from phase09_execution import apply_production, checked_inputs, cpu_slots, fingerprint, hash_inputs, load_json, run_weighted
from phase11_kit_design import kit_configuration
from phase11_kit_solver import solve_quality
from phase11_kit_validator import quality_metrics
from phase11c_layouts import K, REVIEW, TOL, accepted, checkpoint, layout_inputs, read_scored_layout, save_quality_layout


ROOT = Path("results/g3_review_k3")
PRODUCTION = Path("results/expA_f1/run.json")
TRIALS = {
    "H1_single_commuter": "H1_kit_02",
    "H3_couple_one_remote": "H3_kit_02",
}
KEYS = ["household", "kit_id", "unit_key"]


def best_per_shell(frame: pd.DataFrame) -> pd.DataFrame:
    """Choose the highest validated FCIq, breaking ties by time burden."""
    valid = frame[frame.validator_pass.eq(True)]
    return (valid.sort_values(["fciq", "tb", "task_key"], ascending=[False, True, True])
            .drop_duplicates(KEYS).reset_index(drop=True))


def saved_training() -> tuple[pd.DataFrame, dict, dict]:
    """Recover one best accepted S2 layout for each frozen vector and shell."""
    gate = accepted(K)
    run = load_json(K / "run.json")
    if run["status"] != "complete" or gate["code_hash"] != run["code_hash"]:
        raise ValueError("K run and accepted evidence differ")
    shells = pd.read_csv(K / "active_shell_sets.csv")
    if shells["set"].value_counts().to_dict() != {"train": 30, "heldout": 15, "real": 15}:
        raise ValueError("Original K cohorts differ")
    train = shells.loc[shells["set"].eq("train"), "unit_key"]
    designs = load_json(K / "candidate_kits.json")
    cases = pd.read_csv(K / "cases.csv")
    cases = cases[cases.strategy.eq("S2") & cases.unit_key.isin(train) & cases.kit_id.ne("catalogue")]
    seeds = best_per_shell(cases)
    expected = {(household, d["kit_id"], unit) for household, vectors in designs.items()
                for d in vectors for unit in train}
    if (len(expected) != 480 or set(seeds[KEYS].itertuples(index=False, name=None)) != expected
            or not seeds.code_hash.eq(gate["code_hash"]).all()):
        raise ValueError("Incomplete saved training evidence for the eight vectors")
    return seeds, designs, run


def build_jobs(config: dict, corpus: pd.DataFrame, cache: Path, code: str) -> list[dict]:
    """Freeze one matched S2 optimization per specified training pair."""
    seeds, designs, run = saved_training()
    catalogue = accepted(REVIEW / "catalogue")
    if catalogue["k_optimized"] != 120 or catalogue["config_hash"] != config_hash(config):
        raise ValueError("Catalogue optimization differs from the reviewed comparison")
    production = load_json(PRODUCTION)["production_settings"]
    settings = production["small"]
    if (settings["time_limit_s"], settings["num_workers"], settings["anchor_stride_m"]) != (120, 4, .1):
        raise ValueError("The reviewed small-home solver settings differ")
    base, _ = apply_production(config, production, 20.)
    jobs = []
    for household, kit_id in TRIALS.items():
        design = next(d for d in designs[household] if d["kit_id"] == kit_id)
        cfg, qualities = kit_configuration(base, household, design)
        expected_hash = config_hash(cfg)
        selected = seeds[seeds.household.eq(household) & seeds.kit_id.eq(kit_id)]
        if len(selected) != 30 or not selected.config_hash.eq(expected_hash).all():
            raise ValueError("Warm-start layouts differ from the selected dimensions or budget")
        for row in selected.sort_values("unit_key").to_dict("records"):
            unit = row["unit_key"]
            reference = {
                **row, "expected_fciq": row["fciq"],
                "path": str(Path(run["cache"]) / row["task_key"] / "S2.json"),
            }
            jobs.append({
                "task_key": fingerprint([unit, household, kit_id, "K3"])[:24], "cache": cache.as_posix(),
                "code_hash": code, "household": household, "config": cfg, "qualities": qualities,
                "unit_json": corpus.loc[unit, "unit_json"], "reference": reference,
                "threads": cfg["solver"]["num_workers"],
            })
    return jobs


def run_job(job: dict) -> dict:
    """Revalidate the exact starting layout, run S2 and retain the best validated score."""
    root = Path(job["cache"]) / job["task_key"]
    code = job["code_hash"]
    if saved := checkpoint(root, code):
        return saved["row"]
    config, qualities, reference = job["config"], job["qualities"], job["reference"]
    unit, household, grid = layout_inputs(job)
    incumbent, before, source_sha = read_scored_layout(reference, grid, config, household, qualities)
    furniture, raster = config["furniture"], config["raster"]
    scale = household.overrides.get("global_clearance_scale", furniture["meta"]["global_clearance_scale"])
    candidates = generate_candidates(grid, library(furniture, clearance_scale=scale),
                                     raster["orientations_deg"], raster["anchor_stride_m"])
    fresh = solve_quality(unit, household, "S2", config, qualities, (grid, candidates), incumbent)
    trial = quality_metrics(fresh, grid, config, household, qualities)
    if not trial["pass"] or abs(trial["fci"] - fresh["fci"]) > TOL:
        raise ValueError("The extra S2 solve failed independent validation")
    if "fciq" in fresh and abs(trial["fciq"] - fresh["fciq"]) > TOL:
        raise ValueError("The extra solve and validator disagree on FCIq")
    if trial["fciq"] > before["fciq"] or (trial["fciq"] == before["fciq"] and trial["tb"] <= before["tb"]):
        layout, checked, origin = fresh, trial, "extra_quality_solve"
    else:
        layout, checked, origin = incumbent, before, "warm_start_retained"
    target = root / "S2.json"
    save_quality_layout(target, layout, checked, config, code)
    result = {
        **{k: reference[k] for k in KEYS}, "task_key": job["task_key"], "strategy": "S2",
        "source": unit.source, "nia_m2": unit.interior.area, "set": "train",
        "fci": checked["fci"], "fciq": checked["fciq"], "tb": checked["tb"], "validator_pass": checked["pass"],
        "warm_start_task_key": reference["task_key"], "warm_start_sha256": source_sha,
        "warm_start_mode": reference["mode"], "warm_start_flat_quality": reference["flat_quality"],
        "warm_start_fci": before["fci"], "warm_start_fciq": before["fciq"], "warm_start_tb": before["tb"],
        "solver_returned_fciq": trial["fciq"], "layout_origin": origin,
        "solve_time_s": fresh["solver"]["time_s"], "solver_status": fresh["solver"]["status"],
        "budget_s": config["solver"]["time_limit_s"], "config_hash": config_hash(config), "code_hash": code,
        "layout_sha256": sha256_file(target),
    }
    write_json(root / "record.json", {"code_hash": code, "layouts": {"S2.json": result["layout_sha256"]}, "row": result})
    return result


def run(config: dict, digest: str) -> None:
    """Save an independently checked, resumable record for every warm-started solve."""
    started = time.perf_counter()
    corpus_path = Path(config["paths"]["processed"]) / "corpus_units.parquet"
    inputs = hash_inputs([
        Path(__file__).resolve().relative_to(Path.cwd()), PRODUCTION, corpus_path,
        K / "acceptance.json", K / "run.json", REVIEW / "catalogue/acceptance.json",
        Path("scripts/phase09_execution.py"), Path("scripts/phase11c_layouts.py"),
        Path("scripts/phase11_kit_design.py"), Path("scripts/phase11_kit_solver.py"),
        Path("scripts/phase11_kit_validator.py"), *sorted(Path("src/fea").rglob("*.py")),
    ])
    code = fingerprint({"config_hash": digest, "inputs": inputs})
    cache = Path(config["paths"]["interim"]) / "g3_review_k3" / code[:18]
    if (ROOT / "solve_acceptance.json").exists():
        gate = accepted(ROOT, "solve_acceptance.json")
        if gate["code_hash"] != code:
            raise ValueError("Accepted K3 solves use different inputs")
        return
    corpus = pd.read_parquet(corpus_path, columns=["unit_key", "unit_json"]).set_index("unit_key")
    jobs = build_jobs(config, corpus, cache, code)
    rows = []
    for row in tqdm(run_weighted(run_job, jobs, cpu_slots()), total=len(jobs), desc="K3 warm-start S2"):
        rows.append(row)
        if len(rows) % 5 == 0 or len(rows) == len(jobs):
            write_json(ROOT / "progress.json", {"status": "running", "completed": len(rows), "total": len(jobs)})
    cases = pd.DataFrame(rows).sort_values(KEYS)
    if (len(cases) != 60 or cases.duplicated(KEYS).any() or not cases.validator_pass.all()
            or not cases.budget_s.eq(120).all() or (cases.fciq + TOL < cases.warm_start_fciq).any()):
        raise ValueError("Incomplete or invalid K3 S2 solves")
    path = ROOT / "warm_start_s2.csv"
    cases.assign(base_config_hash=digest).to_csv(path, index=False)
    checked_inputs(inputs)
    write_json(ROOT / "solve_acceptance.json", {
        "passed": True, "code_hash": code, "config_hash": digest, "input_sha256": inputs,
        "outputs": hash_inputs([path]), "solves": len(cases), "budget_per_solve_s": 120,
        "elapsed_seconds": time.perf_counter() - started,
        "completed_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    })
    write_json(ROOT / "progress.json", {"status": "complete", "completed": len(rows), "total": len(jobs)})


def main() -> None:
    """Run only the two candidate groups requested by the reviewer."""
    args = prepare_cli(__doc__).parse_args()
    config, digest, _ = start_run(args, "11d_run_k3")
    if args.dry_run:
        print("Warm-start 30 S2 layouts for each of H1_kit_02 and H3_kit_02, with a 120 s cap per solve.")
        return
    import fcntl

    ROOT.mkdir(parents=True, exist_ok=True)
    with (ROOT / ".run.lock").open("w") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        try:
            run(config, digest)
        except Exception as error:
            write_json(ROOT / "progress.json", {"status": "failed", "error_type": type(error).__name__})
            raise


if __name__ == "__main__":
    main()
