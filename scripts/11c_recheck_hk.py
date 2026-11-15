"""Rebuild the HK comparisons using rescored catalogue layouts and the revised K choice."""

from copy import deepcopy
from datetime import datetime, timezone
import fcntl
import importlib.util
import os
from pathlib import Path
import time

import numpy as np
import pandas as pd
from tqdm import tqdm

from fea.config import config_hash
from fea.furniture.candidates import generate_candidates
from fea.furniture.library import library
from fea.io import prepare_cli, sha256_file, start_run, write_json
from phase07_statistics import adequate_crossing, interval
from phase09_execution import apply_production, checked_inputs, cpu_slots, fingerprint, hash_inputs, load_json, run_weighted
from phase11_hk_report import figure_f10, summarize
from phase11_kit_design import kit_configuration
from phase11_kit_solver import objective_score, solve_quality
from phase11_kit_validator import quality_metrics
from phase11c_layouts import (
    HK, K, REVIEW, STRATEGIES, TOL, accepted, best_s2_incumbent, catalogue_qualities, checkpoint,
    layout_inputs, read_scored_layout, rescore_catalogue, save_quality_layout,
)


ROOT = REVIEW / "hong_kong"
CATALOGUE = REVIEW / "catalogue"
KIT = REVIEW / "kit"
F1 = Path("results/expA_f1")
KEYS = ["unit_key", "household", "strategy"]


def driver(path: str):
    """Import a numbered phase script by its checked-in filename."""
    spec = importlib.util.spec_from_file_location(Path(path).stem, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_kit_reference(row: dict, cache: Path, folder: str = "") -> dict:
    """Build the reference for a saved, previously validated S2 case."""
    filename = cache / folder / row["task_key"] / "S2.json"
    return {**row, "strategy": "S2", "path": filename.as_posix(), "expected_fciq": row["fciq"]}


def accepted_hk_kit(job: dict, unit, household, grid) -> tuple | None:
    """Use an exact prior result for the selected dimensions when available."""
    reference = job["prior_kit"]
    if reference is None:
        return None
    if reference["unit_key"] != unit.unit_key or reference["household"] != household.name:
        raise ValueError("Prior kit reference is for a different case")
    config = job["config"]
    if reference["config_hash"] != config_hash(config):
        raise ValueError("Prior kit dimensions differ")
    return read_scored_layout(reference, grid, config, household, job["qualities"])


def evaluate_kit(job: dict) -> dict:
    """Reuse exact outcomes or solve S2 with the same quality objective and budget."""
    root = Path(job["cache"]) / job["task_key"]
    code, config, qualities = job["code_hash"], job["config"], job["qualities"]
    if record := checkpoint(root, code):
        return record["row"]
    prior = job["prior_kit"]
    if job["kit_id"] == "catalogue":
        unit, household, grid, saved = rescore_catalogue(job)
        layout, check, origin = best_s2_incumbent(saved, grid, config, household, qualities)
        source_hash = saved[origin][2]
        previous = accepted_hk_kit(job, unit, household, grid)
        if previous is not None and objective_score(previous[1]) >= objective_score(check):
            layout, check, source_hash = previous
            origin = "exact_reoptimized_K_catalogue"
        elif check["fciq"] >= 1 - TOL and check["tb"] <= 1e-9:
            origin = "validated_FCIq1_TB0"
        else:
            origin = "fresh_quality_solver"
    else:
        unit, household, grid = layout_inputs(job)
        previous = accepted_hk_kit(job, unit, household, grid)
        if previous is not None:
            layout, check, source_hash = previous
            origin = job["prior_origin"]
        else:
            layout, check, source_hash = None, None, ""
            origin = "fresh_quality_solver"
    time_s = 0.
    if origin == "fresh_quality_solver":
        furniture, raster = config["furniture"], config["raster"]
        scale = household.overrides.get("global_clearance_scale", furniture["meta"]["global_clearance_scale"])
        candidates = generate_candidates(grid, library(furniture, clearance_scale=scale),
                                         raster["orientations_deg"], raster["anchor_stride_m"])
        incumbent = check
        layout = solve_quality(unit, household, "S2", config, qualities, (grid, candidates), layout)
        check = quality_metrics(layout, grid, config, household, qualities)
        if incumbent is not None and check["fciq"] + TOL < incumbent["fciq"]:
            raise ValueError("HK quality solve discarded its warm start")
        time_s = float(layout["solver"]["time_s"])
    if not check["pass"]:
        raise ValueError("Invalid HK kit layout")
    target = root / "S2.json"
    save_quality_layout(target, layout, check, config, code)
    digest = sha256_file(target)
    result = {
        "unit_key": unit.unit_key, "household": household.name, "strategy": "S2_kit", "kit_id": job["kit_id"],
        "fci": check["fci"], "fciq": check["fciq"], "tb": check["tb"], "validator_pass": check["pass"],
        "layout_origin": origin, "source_layout_sha256": source_hash, "layout_sha256": digest,
        "source_code_hash": prior["code_hash"] if origin.startswith("exact_") else "",
        "config_hash": config_hash(config), "code_hash": code, "search_time_s": time_s,
    }
    write_json(root / "record.json", {"code_hash": code, "layouts": {"S2.json": digest}, "row": result})
    return result


def paired_switching(config: dict, data: pd.DataFrame, scenario: str) -> dict:
    """Pair resamples of shape templates for the couple's S1-to-S2 contrast."""
    household = "H3_couple_one_remote"
    options = config["experiments"]["bootstrap"]
    tau = config["experiments"]["adequacy_tau"]
    subset = data[data.household.eq(household) & data.strategy.isin(["S1", "S2"])]
    wide = subset.pivot(index=["unit_key", "area_m2", "shape"], columns="strategy", values="fciq").reset_index()
    if len(wide) != 390 or wide[["S1", "S2"]].isna().any().any():
        raise ValueError("H3 switching contrast requires the complete paired grid")
    a = wide.area_m2.to_numpy()
    y = wide[["S1", "S2"]].to_numpy() >= tau - 1e-9
    point = [adequate_crossing(a, y[:, j])["a_min_m2"] for j in range(2)]
    clusters = [g.index.to_numpy() for _, g in wide.groupby("shape", sort=True)]
    rng = np.random.default_rng(config["seed"])
    draws = np.full(options["n"], np.nan)
    for b in range(options["n"]):
        take = rng.integers(0, len(clusters), len(clusters))
        i = np.concatenate([clusters[j] for j in take])
        fits = [adequate_crossing(a[i], y[i, j])["a_min_m2"] for j in range(2)]
        if all(x is not None for x in fits):
            draws[b] = fits[0] - fits[1]
    low, high, successful, status = interval(draws, options["ci"])
    if status == "percentile_unit_bootstrap":
        status = "percentile_shape_bootstrap"
    identified = all(x is not None for x in point)
    return {
        "household": household, "scenario": scenario, "n_shells": len(wide), "n_shape_clusters": len(clusters),
        "n_resamples": options["n"], "a_min_s1_m2": point[0], "a_min_s2_m2": point[1],
        "delta_a_min_s1_minus_s2_m2": point[0] - point[1] if identified else None,
        "ci_lo": low if identified else None, "ci_hi": high if identified else None,
        "ci_successful": successful, "ci_status": status if identified else "point_crossing_not_identified", "tau": tau,
    }


def selected_references(household: str, design: dict, kit_gate: dict, catalogue_gate: dict,
                        hk_gate: dict, old_hk: pd.DataFrame) -> dict:
    """Resolve revised K confirmations and prior HK layouts for unchanged vectors."""
    old_k = load_json(K / "kit.yaml")["by_household"][household]["kit"]
    new = pd.read_csv(KIT / "confirmations.csv")
    new = new[new.household.eq(household) & new.condition.eq("kit") & new.strategy.eq("S2")]
    references = {}
    if design["kit_id"] == old_k["kit_id"] and design["dimensions"] == old_k["dimensions"]:
        hk_cache = Path(load_json(HK / "run.json")["cache"])
        for row in old_hk[old_hk.household.eq(household) & old_hk.strategy.eq("S2_kit")].to_dict("records"):
            key = fingerprint([row["unit_key"], household, design["kit_id"]])[:24]
            path = hk_cache / "kit" / key
            record = load_json(path / "record.json")
            if record["code_hash"] != hk_gate["code_hash"] or record["rows"][0]["unit_key"] != row["unit_key"]:
                raise ValueError("Prior HK kit checkpoint differs")
            row.update(task_key=key, layout_sha256=record["layouts"]["S2.json"])
            references[row["unit_key"]] = (load_kit_reference(row, hk_cache, "kit"), "exact_accepted_HK_kit")
    for row in new.to_dict("records"):
        origin = row["layout_origin"]
        if origin == "quality_optimized_catalogue":
            root = Path(catalogue_gate["cache"]) / "K"
        elif origin == "review_selected_kit":
            root = Path(kit_gate["cache"])
        else:
            root = Path(load_json(K / "run.json")["cache"])
        if row["unit_key"] not in references:
            references[row["unit_key"]] = (load_kit_reference(row, root), "exact_revised_K_kit")
    return references


def run(config: dict, digest: str) -> None:
    """Complete the revised HK comparison on the same 390 geometries."""
    began = time.perf_counter()
    catalogue = accepted(CATALOGUE)
    kit = accepted(KIT)
    scenario = accepted(HK)
    if not catalogue["config_hash"] == kit["config_hash"] == scenario["config_hash"] == digest:
        raise ValueError("Scenario and comparison inputs use different configurations")
    corpus_path = Path(config["paths"]["processed"]) / "corpus_units.parquet"
    inputs = hash_inputs([
        Path(__file__).resolve().relative_to(Path.cwd()), Path("scripts/11c_rescore_catalogue.py"), Path("scripts/phase11c_layouts.py"),
        Path("scripts/phase11_hk_report.py"), Path("scripts/phase07_statistics.py"),
        Path("scripts/phase09_execution.py"), K / "acceptance.json", K / "run.json", F1 / "run.json",
        HK / "acceptance.json", HK / "run.json", CATALOGUE / "acceptance.json", KIT / "acceptance.json", corpus_path,
        *sorted(Path("scripts").glob("phase11_kit_*.py")), *sorted(Path("src/fea").rglob("*.py")),
    ])
    code = fingerprint({"config_hash": digest, "inputs": inputs})
    cache = Path(config["paths"]["interim"]) / "g3_review_hk" / code[:18]
    corpus = pd.read_parquet(corpus_path, columns=["unit_key", "unit_json"]).set_index("unit_key")
    catalogue_driver = driver("scripts/11c_rescore_catalogue.py")
    references, shells = catalogue_driver.saved_hk_references(config, corpus)
    baseline = pd.read_csv(CATALOGUE / "hk_rescored.csv")
    if len(baseline) != 3510 or not baseline.validator_pass.all():
        raise ValueError("The rescored HK catalogue is incomplete")
    old_hk = pd.read_csv(HK / "cases.csv")
    designs = load_json(KIT / "kit.yaml")["by_household"]
    production = load_json(F1 / "run.json")["production_settings"]
    jobs = []
    for household, choice in designs.items():
        design = choice["kit"]
        base, _ = apply_production(config, production, 20.)
        cfg, qualities = kit_configuration(base, household, design)
        if design["kit_id"] == "catalogue":
            qualities = catalogue_qualities(base)
        prior = selected_references(household, design, kit, catalogue, scenario, old_hk)
        for unit in shells.unit_key:
            exact, origin = prior.get(unit, (None, ""))
            jobs.append({
                "task_key": fingerprint([unit, household, design["kit_id"]])[:24], "cache": str(cache),
                "code_hash": code, "config": cfg, "household": household, "kit_id": design["kit_id"],
                "qualities": qualities, "unit_json": corpus.loc[unit, "unit_json"], "prior_kit": exact,
                "prior_origin": origin, "references": references[unit, household],
                "threads": cfg["solver"]["num_workers"],
            })
    rows = []
    for i, row in enumerate(tqdm(run_weighted(evaluate_kit, jobs, cpu_slots()), total=len(jobs), desc="HK revised S2 kits"), 1):
        rows.append(row)
        if i % 5 == 0 or i == len(jobs):
            write_json(ROOT / "progress.json", {"status": "running", "stage": "S2_kit", "done": i, "total": len(jobs)})
    fitted = pd.DataFrame(rows).merge(shells[["unit_key", "area_m2", "nia_m2", "shape"]],
                                      on="unit_key", validate="many_to_one")
    data = pd.concat([baseline.assign(layout_origin="rescored_original_catalogue"), fitted], ignore_index=True)
    if len(data) != 4290 or data.duplicated(KEYS).any() or not data.validator_pass.all():
        raise ValueError("Incomplete or invalid reviewed HK cases")
    if not np.isfinite(data[["fci", "fciq", "tb"]]).all().all() or (data.fciq > data.fci + TOL).any():
        raise ValueError("Invalid reviewed HK scores")
    params = config["experiments"]
    options = params["bootstrap"]
    sizes, summary, effects = summarize(data, params["adequacy_tau"], options["n"], options["ci"], config["seed"])
    summary = summary.replace({"percentile_unit_bootstrap": "percentile_shape_bootstrap"})
    switching = pd.DataFrame([paired_switching(config, data, "configured_size_curves"),
                             paired_switching(config, old_hk, "catalogue_credited_at_full_quality")])
    sensitivity = pd.read_csv(HK / "scenario_summary.csv").assign(sensitivity="catalogue_credited_at_full_quality")
    frames = {
        "cases": data.sort_values(KEYS), "adequacy_by_size": sizes, "scenario_summary": summary,
        "form_time_effects": effects, "couple_switching": switching, "catalogue_full_quality_sensitivity": sensitivity,
    }
    outputs = []
    for name, frame in frames.items():
        path = ROOT / (name + ".csv")
        frame.assign(base_config_hash=digest).to_csv(path, index=False)
        outputs.append(path)
    figure = ROOT / "F10"
    # Matplotlib reads this for PDF metadata, independently of the host timezone.
    os.environ["SOURCE_DATE_EPOCH"] = str(int(datetime.now(timezone.utc).timestamp()))
    figure_f10(sizes, figure, params["adequacy_tau"])
    outputs.extend(figure.with_suffix(ext) for ext in (".pdf", ".png"))
    checked_inputs(inputs)
    write_json(ROOT / "acceptance.json", {
        "passed": True, "config_hash": digest, "code_hash": code, "input_sha256": inputs,
        "outputs": hash_inputs(outputs), "shells": len(shells), "cases": len(data),
        "new_solves": int(fitted.layout_origin.eq("fresh_quality_solver").sum()),
        "kit_layout_origins": fitted.layout_origin.value_counts().to_dict(),
        "census_weighting": False, "carbon_applied": False, "elapsed_seconds": time.perf_counter() - began,
        "completed_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    })
    write_json(ROOT / "progress.json", {"status": "complete"})


def main() -> None:
    """Run the revised Hong Kong scenario after the catalogue and K gates."""
    args = prepare_cli(__doc__).parse_args()
    config, digest, _ = start_run(args, "11c_recheck_hk")
    if args.dry_run:
        print("Reuse the rescored HK catalogue and confirm the revised S2 kits on the same 390 templates.")
        return
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
