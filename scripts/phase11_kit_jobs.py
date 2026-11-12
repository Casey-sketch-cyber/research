"""Run and retain each independently checked kit layout once per evaluation mode."""
from copy import deepcopy
import json
from pathlib import Path
import time

from fea.config import config_hash
from fea.furniture.candidates import generate_candidates
from fea.furniture.library import library
from fea.geometry.raster import rasterize
from fea.geometry.unit import Unit
from fea.households import parse_households
from fea.io import sha256_file, write_json
from phase09_execution import load_json
from phase11_kit_solver import solve_quality
from phase11_kit_validator import quality_metrics

TRIPLET = ("S0", "S1", "S2")
TOL = 1e-8


def run_kit_case(job):
    """Audit all candidates and revalidate nested strategy sharing in the selected objective."""
    cache = Path(job["cache"])/job["task_key"]
    checkpoint = cache/"record.json"
    if checkpoint.exists():
        result = load_json(checkpoint)
        if result["code_hash"] != job["code_hash"]:
            raise ValueError("Kit checkpoint fingerprint differs")
        for name, digest in result["layouts"].items():
            if sha256_file(cache/name) != digest:
                raise ValueError("Saved kit layout differs")
        return result["rows"]
    started = time.perf_counter()
    config = job["config"]
    strategies = ("S2",) if job["mode"] == "search" else TRIPLET
    if time.time() + len(strategies)*(config["solver"]["time_limit_s"]+30) >= job["deadline_epoch"]:
        raise TimeoutError("Remaining kit time box cannot accommodate the configured case budgets")
    digest = config_hash(config)
    unit = Unit.from_dict(json.loads(job["unit_json"]))
    household = parse_households(config["households"], config["furniture"])[job["household"]]
    furniture, raster = config["furniture"], config["raster"]
    width = household.overrides.get("walking_width", furniture["meta"]["walking_width"])
    scale = household.overrides.get("global_clearance_scale", furniture["meta"]["global_clearance_scale"])
    grid = rasterize(unit, raster["resolution_m"], width, raster["source_gap_close_m"])
    candidates = generate_candidates(grid, library(furniture, clearance_scale=scale),
                                     raster["orientations_deg"], raster["anchor_stride_m"])
    preparation = time.perf_counter()-started
    physical = job["qualities"]
    objective = {} if job["flat"] else physical
    score_key = "fci" if job["flat"] else "fciq"
    layouts, validations, times = {}, {}, {}
    incumbent = None
    for strategy in strategies:
        own_file = cache/("own_"+strategy+".json")
        if own_file.exists():
            own = load_json(own_file)
            if own["code_hash"] != job["code_hash"] or own["config_hash"] != digest:
                raise ValueError("Partial kit result has different inputs")
        else:
            own = solve_quality(unit, household, strategy, config, objective, (grid, candidates), incumbent)
            own["code_hash"], own["config_hash"] = job["code_hash"], digest
            write_json(own_file, own)
        checked = quality_metrics(own, grid, config, household, physical)
        if not checked["pass"] or abs(checked["fci"]-own["fci"]) > TOL:
            raise ValueError("Kit own-search validation failed")
        if not job["flat"] and "fciq" in own and abs(checked["fciq"]-own["fciq"]) > TOL:
            raise ValueError("Kit own-search FCIq validation failed")
        layouts[strategy], validations[strategy] = own, checked
        times[strategy] = float(own["solver"]["time_s"])
        incumbent = own

    rows, hashes = [], {}
    for strategy in strategies:
        best, checked, origin = layouts[strategy], validations[strategy], strategy
        for candidate_strategy, candidate in layouts.items():
            if candidate_strategy == strategy:
                continue
            proposal = deepcopy(candidate)
            proposal["strategy"] = strategy
            trial = quality_metrics(proposal, grid, config, household, physical)
            improvement = trial[score_key] > checked[score_key]+TOL
            tie = abs(trial[score_key]-checked[score_key]) <= TOL and trial["tb"] < checked["tb"]-TOL
            if trial["pass"] and (improvement or tie):
                best, checked, origin = proposal, trial, candidate_strategy
        layout_path = cache/(strategy+".json")
        best = {**best, "validator": checked}
        best.update({key: checked[key] for key in ("fci", "fciq", "fci_by_variant", "served_hours", "demanded_hours", "tb")})
        write_json(layout_path, best)
        hashes[layout_path.name] = sha256_file(layout_path)
        rows.append(dict(task_key=job["task_key"], unit_key=unit.unit_key, source=unit.source, nia_m2=unit.interior.area,
                         household=household.name, kit_id=job["kit_id"], strategy=strategy, mode=job["mode"],
                         flat_quality=job["flat"], fci=checked["fci"], fciq=checked["fciq"], objective_score=checked[score_key],
                         tb=checked["tb"], validator_pass=checked["pass"], shared_from_strategy=origin,
                         own_search_time_s=times[strategy], preparation_time_s=preparation,
                         layout_sha256=hashes[layout_path.name], config_hash=digest, code_hash=job["code_hash"]))
    if len(rows) == 3 and any(rows[i]["objective_score"]+TOL < rows[i-1]["objective_score"] for i in (1, 2)):
        raise ValueError("Kit nested objective ordering failed")
    write_json(checkpoint, dict(code_hash=job["code_hash"], layouts=hashes, rows=rows,
                                elapsed_seconds=time.perf_counter()-started))
    return rows
