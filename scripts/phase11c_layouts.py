"""Shared catalogue scoring and independently validated review jobs."""

from copy import deepcopy
import json
from pathlib import Path
import time

import numpy as np

from fea.config import config_hash
from fea.furniture.candidates import generate_candidates
from fea.furniture.library import library
from fea.geometry.raster import rasterize
from fea.geometry.unit import Unit
from fea.households import parse_households
from fea.io import sha256_file, write_json
from phase09_execution import checked_inputs, load_json
from phase11_kit_solver import objective_score, solve_quality
from phase11_kit_validator import quality_metrics


STRATEGIES = ("S0", "S1", "S2")
TOL = 1e-8
K = Path("results/expK")
HK = Path("results/scenario_hk")
REVIEW = Path("results/g3_review")


def accepted(root: Path, gate_name: str = "acceptance.json") -> dict:
    """Require the accepted output bytes before reusing their evidence."""
    gate = load_json(root / gate_name)
    if gate["passed"] is not True:
        raise ValueError(f"Unaccepted source: {root}")
    checked_inputs(gate["outputs"])
    return gate


def catalogue_dimensions(config: dict) -> dict[str, float]:
    """Read the catalogue vector directly from the configured bodies."""
    furniture = config["furniture"]
    items = furniture["transformable_items"]
    deployed = {name: item["states"]["deployed"]["footprint"]
                for name, item in items.items() if name in
                {"wall_bed_single", "wall_bed_double", "fold_down_desk", "drop_leaf_table"}}
    desk, table = deployed["fold_down_desk"], deployed["drop_leaf_table"]
    return {
        "wall_bed_width_single": deployed["wall_bed_single"][0],
        "wall_bed_width_double": deployed["wall_bed_double"][0],
        "desk_width": desk[0], "desk_depth_deployed": desk[1],
        "table_width": table[0], "table_depth_deployed": table[1],
        "wardrobe_frontage": furniture["static_items"]["wardrobe"]["footprint"][0],
    }


def catalogue_qualities(config: dict) -> dict[str, float]:
    """Apply the configured design curves to both beds, the desk and the table."""
    variables = config["experiments"]["K_kit_design"]["variables"]
    dimensions = catalogue_dimensions(config)
    if any(value not in variables[key]["values"] for key, value in dimensions.items()):
        raise ValueError("The catalogue is outside the reviewed design grid")
    def quality(key):
        curve = variables[key]
        return float(np.interp(dimensions[key], curve["values"], curve["q"]))
    return {
        "wall_bed_single": quality("wall_bed_width_single"),
        "wall_bed_double": quality("wall_bed_width_double"),
        "fold_down_desk": min(quality("desk_width"), quality("desk_depth_deployed")),
        "drop_leaf_table": min(quality("table_width"), quality("table_depth_deployed")),
    }


def layout_inputs(job: dict):
    """Build the geometry and household under the supplied catalogue or kit."""
    config = job["config"]
    unit = Unit.from_dict(json.loads(job["unit_json"]))
    household = parse_households(config["households"], config["furniture"])[job["household"]]
    furniture, raster = config["furniture"]["meta"], config["raster"]
    width = household.overrides.get("walking_width", furniture["walking_width"])
    grid = rasterize(unit, raster["resolution_m"], width, raster["source_gap_close_m"])
    return unit, household, grid


def read_scored_layout(reference: dict, grid, config: dict, household, qualities: dict):
    """Check layout identity, known digests, validity and accepted plain scores."""
    path = Path(reference["path"])
    digest = sha256_file(path)
    if reference.get("layout_sha256") and digest != reference["layout_sha256"]:
        raise ValueError("Saved layout checksum differs")
    layout = load_json(path)
    keys = ("unit_key", "household", "strategy", "code_hash", "config_hash")
    if any(layout[key] != reference[key] for key in keys):
        raise ValueError("Saved layout identity differs")
    check = quality_metrics(layout, grid, config, household, qualities)
    if not check["pass"] or abs(check["fci"] - reference["fci"]) > TOL or abs(check["tb"] - reference["tb"]) > TOL:
        raise ValueError("The validator disagrees with the accepted layout")
    if "expected_fciq" in reference and abs(check["fciq"] - reference["expected_fciq"]) > TOL:
        raise ValueError("The validator disagrees with the accepted quality score")
    return layout, check, digest


def score_row(reference: dict, check: dict, digest: str, qualities: dict, code: str) -> dict:
    """Record the independently recomputed outcome and its source digest."""
    return {
        "unit_key": reference["unit_key"], "household": reference["household"], "strategy": reference["strategy"],
        "fci": check["fci"], "fciq": check["fciq"], "tb": check["tb"], "validator_pass": check["pass"],
        "source_layout_sha256": digest, "source_config_hash": reference["config_hash"],
        "source_code_hash": reference["code_hash"], "quality_rule": "configured_size_curves",
        "quality_factors": json.dumps(qualities, sort_keys=True, separators=(",", ":")), "code_hash": code,
    }


def save_quality_layout(path: Path, layout: dict, check: dict, config: dict, code: str) -> None:
    """Save the rescored layout in a new cache without editing the source."""
    layout = {**layout, "config_hash": config_hash(config), "code_hash": code, "validator": check}
    layout.update({key: check[key] for key in ("fci", "fciq", "fci_by_variant", "served_hours", "demanded_hours", "tb")})
    write_json(path, layout)


def checkpoint(root: Path, code: str) -> dict | None:
    """Return a completed job only when its fingerprint and bytes agree."""
    record = root / "record.json"
    if not record.exists():
        return None
    result = load_json(record)
    if result["code_hash"] != code:
        raise ValueError("Review checkpoint belongs to different inputs")
    for name, digest in result["layouts"].items():
        if sha256_file(root / name) != digest:
            raise ValueError("Review checkpoint layout differs")
    return result


def rescore_catalogue(job: dict) -> tuple:
    """Validate all three saved strategies and retain the exact rescored layouts."""
    config, qualities = job["config"], job["qualities"]
    unit, household, grid = layout_inputs(job)
    saved = {}
    for strategy in STRATEGIES:
        reference = job["references"][strategy]
        saved[strategy] = read_scored_layout(reference, grid, config, household, qualities)
    return unit, household, grid, saved


def best_s2_incumbent(saved: dict, grid, config: dict, household, qualities: dict):
    """Compare the checked S0 → S1 → S2 chain after mapping each layout to S2."""
    best, best_check, origin = None, None, None
    for strategy in STRATEGIES:
        proposal = deepcopy(saved[strategy][0])
        proposal["strategy"] = "S2"
        trial = quality_metrics(proposal, grid, config, household, qualities)
        if not trial["pass"]:
            raise ValueError("A saved catalogue predecessor is not feasible under S2")
        if best_check is None or objective_score(trial) >= objective_score(best_check):
            best, best_check, origin = proposal, trial, strategy
    return best, best_check, origin


def run_catalogue_job(job: dict) -> dict:
    """Rescore a saved triplet and optionally optimize its S2 with the same budget as K."""
    root = Path(job["cache"]) / job["task_key"]
    if result := checkpoint(root, job["code_hash"]):
        return result
    started = time.perf_counter()
    config, qualities, code = job["config"], job["qualities"], job["code_hash"]
    unit, household, grid, saved = rescore_catalogue(job)
    rows = [score_row(job["references"][s], saved[s][1], saved[s][2], qualities, code) for s in STRATEGIES]
    result = {"code_hash": code, "rescored": rows, "optimized": None, "layouts": {}}
    if job["optimize"]:
        furniture, raster = config["furniture"], config["raster"]
        scale = household.overrides.get("global_clearance_scale", furniture["meta"]["global_clearance_scale"])
        candidates = generate_candidates(grid, library(furniture, clearance_scale=scale),
                                         raster["orientations_deg"], raster["anchor_stride_m"])
        incumbent, best, origin = best_s2_incumbent(saved, grid, config, household, qualities)
        layout = solve_quality(unit, household, "S2", config, qualities, (grid, candidates), incumbent)
        check = quality_metrics(layout, grid, config, household, qualities)
        if not check["pass"] or abs(check["fciq"] - layout["fciq"]) > TOL or check["fciq"] + TOL < best["fciq"]:
            raise ValueError("Reoptimized catalogue lost a valid quality incumbent")
        if abs(check["fciq"] - best["fciq"]) <= TOL and check["tb"] > best["tb"] + TOL:
            raise ValueError("Reoptimized catalogue increased time burden at equal quality")
        filename = root / "S2.json"
        save_quality_layout(filename, layout, check, config, code)
        result["layouts"][filename.name] = sha256_file(filename)
        row = score_row(job["references"]["S2"], check, saved["S2"][2], qualities, code)
        result["optimized"] = {**row, "task_key": job["task_key"], "config_hash": config_hash(config),
                               "incumbent_strategy": origin, "incumbent_fciq": best["fciq"],
                               "original_fciq_rescored": saved["S2"][1]["fciq"],
                               "search_time_s": layout["solver"]["time_s"], "status": layout["solver"]["status"],
                               "layout_sha256": result["layouts"][filename.name]}
    result["elapsed_seconds"] = time.perf_counter() - started
    write_json(root / "record.json", result)
    return result
