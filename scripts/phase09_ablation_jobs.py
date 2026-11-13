"""Independently validated ablation layouts with exact and saturated-control reuse."""
from copy import deepcopy
import importlib.util
from math import ceil
from pathlib import Path
import time
import json

from fea.config import config_hash
from fea.furniture.candidates import generate_candidates
from fea.furniture.library import library
from fea.geometry.raster import rasterize
from fea.geometry.unit import Unit
from fea.households import parse_households
from fea.io import sha256_file, write_json
from fea.solve.cpsat import solve_layout
from fea.validate import validate_layout
from phase09_execution import load_json

STRATEGIES = ("S0", "S1", "S2")
TOL = 1e-8
revision_spec = importlib.util.spec_from_file_location("reviewed_sharing", "scripts/06_revision.py")
revision = importlib.util.module_from_spec(revision_spec)
revision_spec.loader.exec_module(revision)


def changed_config(production, kind, value):
    """Change the active variable and keep anchors representable on its grid."""
    cfg = deepcopy(production)
    if kind == "drop_one":
        del cfg["furniture"]["transformable_items"][value]
    elif kind == "clearance_scale":
        cfg["furniture"]["meta"]["global_clearance_scale"] = float(value)
    elif kind == "walking_width":
        cfg["furniture"]["meta"]["walking_width"] = float(value)
    elif kind == "resolution_m":
        raster = cfg["raster"]
        raster["resolution_m"] = resolution = float(value)
        base_stride = raster["anchor_stride_m"]
        if abs(base_stride / resolution - round(base_stride / resolution)) > 1e-9:
            raster["anchor_stride_m"] = round(max(1, ceil(base_stride / resolution - 1e-9)) * resolution, 10)
    elif kind == "time_limit_s":
        cfg["solver"]["time_limit_s"] = int(value)
    elif kind not in ("production", "household"):
        raise ValueError("Unknown ablation")
    return cfg


def verified_grid_recovery(job, old_cache, old_fingerprint):
    """Inherit a complete, configuration-identical triplet without editing its evidence."""
    if job["anchor_adjusted"]:
        return None
    root = old_cache / job["task_key"]
    done = root / "record.json"
    if not done.exists():
        return None
    prior = load_json(done)
    if prior["fingerprint"] != old_fingerprint or len(prior["rows"]) != len(STRATEGIES):
        raise ValueError("Recovered ablation checkpoint has an unexpected fingerprint or size")
    if set(prior["layouts"]) != {s + ".json" for s in STRATEGIES}:
        raise ValueError("Recovered ablation checkpoint is missing a layout")
    cfg, task_key = job["config"], job["task_key"]
    expected_config = config_hash(cfg)
    rows = []
    for strategy, row in zip(STRATEGIES, prior["rows"]):
        file = strategy + ".json"
        if (row["strategy"], row["task_key"], row["config_hash"], row["code_hash"],
                row["ablation"], row["value"], row["sample"], row["household"]) != (
                strategy, task_key, expected_config, old_fingerprint,
                job["kind"], job["value"], job["sample"], job["household"]):
            raise ValueError("Recovered ablation row differs from the required case")
        if sha256_file(root / file) != prior["layouts"][file] or row["layout_sha256"] != prior["layouts"][file]:
            raise ValueError("Recovered ablation layout digest differs")
        rows.append(dict(row, resolution_m=cfg["raster"]["resolution_m"],
                         anchor_stride_m=cfg["raster"]["anchor_stride_m"],
                         checkpoint_origin="verified_previous_grid_attempt"))
    return rows


def validated_reference(record, grid, config, household):
    """Read the exact accepted layout and evaluate it under the active condition."""
    path = Path(record["path"])
    layout = load_json(path)
    if any(layout[k] != record[k] for k in ("unit_key", "household", "strategy", "code_hash", "config_hash")):
        raise ValueError("Saved control layout identity changed")
    check = validate_layout(layout, grid, config, household)
    return layout, check, sha256_file(path)


def run_ablation(job):
    """Solve or exactly reuse one unit-household triplet, then audit each layout."""
    root = Path(job["cache"]) / job["task_key"]
    done = root / "record.json"
    if done.exists():
        checkpoint = load_json(done)
        if checkpoint["fingerprint"] != job["fingerprint"]:
            raise ValueError("Ablation checkpoint fingerprint differs")
        for path, digest in checkpoint["layouts"].items():
            if sha256_file(root / path) != digest:
                raise ValueError("Ablation checkpoint layout differs")
        return checkpoint["rows"]

    started = time.perf_counter()
    cfg, digest = job["config"], config_hash(job["config"])
    unit = Unit.from_dict(json.loads(job["unit_json"]))
    household = parse_households(cfg["households"], cfg["furniture"])[job["household"]]
    raster = cfg["raster"]
    furniture = cfg["furniture"]["meta"]
    width = household.overrides.get("walking_width", furniture["walking_width"])
    scale = household.overrides.get("global_clearance_scale", furniture["global_clearance_scale"])
    grid = rasterize(unit, raster["resolution_m"], width, raster["source_gap_close_m"])
    reference = job["reference"]
    layouts, timings, provenance = {}, {}, {}
    candidates = None
    incumbent = None
    exact = job["exact_control"]
    for strategy in STRATEGIES:
        checkpoint = root / ("own_" + strategy + ".json")
        if checkpoint.exists():
            partial = load_json(checkpoint)
            if partial["fingerprint"] != job["fingerprint"]:
                raise ValueError("Ablation partial checkpoint differs")
            layout = partial["layout"]
            timings[strategy] = partial["search_time_s"]
            provenance[strategy] = partial["provenance"]
        else:
            layout = None
            origin, source_hash = "fresh_solve", ""
            can_recheck = reference and (exact or job["kind"] in ("drop_one", "clearance_scale", "walking_width"))
            if can_recheck:
                previous, valid, source_hash = validated_reference(reference[strategy], grid, cfg, household)
                unchanged_s0 = strategy == "S0" and job["kind"] == "drop_one"
                if exact or unchanged_s0:
                    if not valid["pass"] or abs(valid["fci"] - reference[strategy]["fci_validator"]) > TOL:
                        raise ValueError("Exact ablation reuse changes accepted score or validity")
                    layout, origin = previous, "identical_accepted_control" if exact else "unchanged_static_inventory"
                elif valid["pass"] and valid["fci"] >= 1 - TOL and abs(valid["tb"]) < TOL:
                    layout, origin = previous, "validated_FCI1_TB0"
                if layout is not None:
                    layout.update({k: valid[k] for k in ("fci", "fci_by_variant", "tb", "served_hours", "demanded_hours")})
                    layout["validator"] = valid
            if layout is None:
                if candidates is None:
                    candidates = generate_candidates(
                        grid, library(cfg["furniture"], clearance_scale=scale),
                        raster["orientations_deg"], raster["anchor_stride_m"],
                    )
                layout = solve_layout(unit, household, strategy, cfg, incumbent, (grid, candidates))
                source_hash = ""
            if not exact and origin != "fresh_solve":
                layout["solver"].pop("shared_from_strategy", None)
            layout["config_hash"], layout["code_hash"] = digest, job["fingerprint"]
            timings[strategy] = float(layout["solver"]["time_s"]) if origin == "fresh_solve" else 0.
            provenance[strategy] = (origin, source_hash)
            write_json(checkpoint, {"fingerprint": job["fingerprint"], "layout": layout,
                                    "search_time_s": timings[strategy], "provenance": provenance[strategy]})
        check = validate_layout(layout, grid, cfg, household)
        if abs(check["fci"] - layout["fci"]) > TOL:
            raise ValueError("Ablation solver/validator disagreement")
        layouts[strategy] = layout
        if check["pass"]:
            incumbent = layout

    if not exact:
        layouts = revision.share(layouts, grid, cfg, household)
    rows, saved = [], {}
    for strategy in STRATEGIES:
        layout = layouts[strategy]
        check = validate_layout(layout, grid, cfg, household)
        structural = not check["pass"] and not layout["items"] and all(
            v.startswith("fixed_service_unreachable:") for v in check["violations"]
        )
        if abs(check["fci"] - layout["fci"]) > TOL or (not check["pass"] and not structural):
            raise ValueError("Unexpected retained ablation layout failure")
        layout["validator"] = check
        filename = strategy + ".json"
        write_json(root / filename, layout)
        saved[filename] = sha256_file(root / filename)
        sharing = layout["solver"].get("shared_from_strategy")
        if exact:
            sharing = None
        final_origin, source_hash = provenance[sharing or strategy]
        rows.append({
            "task_key": job["task_key"], "unit_key": unit.unit_key, "source": unit.source,
            "nia_m2": unit.interior.area, "household": household.name, "strategy": strategy,
            "ablation": job["kind"], "value": job["value"], "sample": job["sample"],
            "fci_validator": check["fci"], "tb": check["tb"], "validator_pass": check["pass"],
            "structural_unreachable": structural, "violations": ";".join(check["violations"]),
            "resolution_m": raster["resolution_m"], "anchor_stride_m": raster["anchor_stride_m"],
            "checkpoint_origin": "current_grid_implementation",
            "own_search_time_s": timings[strategy], "case_wall_time_s": time.perf_counter() - started,
            "budget_s": cfg["solver"]["time_limit_s"], "solver_workers": cfg["solver"]["num_workers"],
            "own_origin": provenance[strategy][0], "result_origin": final_origin,
            "shared_from_strategy": sharing or "", "source_layout_sha256": source_hash,
            "layout_sha256": saved[filename], "config_hash": digest, "code_hash": job["fingerprint"],
            "solver_status": layout["solver"]["status"],
        })
    if any(rows[i]["fci_validator"] + TOL < rows[i-1]["fci_validator"] for i in (1, 2)):
        raise ValueError("Ablation paired strategy ordering failed")
    write_json(done, {"fingerprint": job["fingerprint"], "layouts": saved, "rows": rows})
    return rows
