"""Independent HK kit reuse checks and fallback to the same quality solver."""
import json
from pathlib import Path
import time

from fea.config import config_hash
from fea.geometry.raster import rasterize
from fea.geometry.unit import Unit
from fea.households import parse_households
from fea.io import sha256_file, write_json
from phase09_execution import load_json
from phase11_kit_jobs import run_kit_case
from phase11_kit_validator import quality_metrics


def run_scenario_kit(job):
    """Revalidate prior K results and certify the FCIq=1, TB=0 cases."""
    root = Path(job["cache"])/job["task_key"]
    record = root/"record.json"
    if record.exists():
        return run_kit_case(job)
    prior = job.get("exact_kit")
    baseline = job.get("catalogue_layout")
    if not prior and not baseline:
        return run_kit_case(job)
    began = time.perf_counter()
    config = job["config"]
    unit = Unit.from_dict(json.loads(job["unit_json"]))
    furniture, raster = config["furniture"], config["raster"]
    household = parse_households(config["households"], furniture)[job["household"]]
    grid = rasterize(unit, raster["resolution_m"], furniture["meta"]["walking_width"], raster["source_gap_close_m"])
    reference = prior or baseline
    path = Path(reference["path"])
    layout = load_json(path)
    source_sha = sha256_file(path)
    if any(layout[key] != reference[key] for key in ("unit_key", "household", "strategy", "code_hash", "config_hash")):
        raise ValueError("HK saved layout identity differs")
    if reference.get("layout_sha256") and source_sha != reference["layout_sha256"]:
        raise ValueError("HK saved layout checksum differs")
    checked = quality_metrics(layout, grid, config, household, job["qualities"])
    digest = config_hash(config)
    if prior:
        if not checked["pass"] or digest != prior["config_hash"] or abs(checked["fciq"]-prior["fciq"]) > 1e-8:
            raise ValueError("HK exact K reuse changes validation")
        origin = "exact_accepted_K"
    elif checked["pass"] and checked["fciq"] >= 1-1e-8 and checked["tb"] <= 1e-9:
        origin = "validated_FCIq1_TB0"
    else:
        return run_kit_case(job)
    layout.update(config_hash=digest, code_hash=job["code_hash"], validator=checked,
                  fci=checked["fci"], fciq=checked["fciq"], tb=checked["tb"])
    saved = root/"S2.json"
    write_json(saved, layout)
    digest_layout = sha256_file(saved)
    row = dict(task_key=job["task_key"], unit_key=unit.unit_key, source=unit.source,
               nia_m2=unit.interior.area, household=household.name, kit_id=job["kit_id"],
               strategy="S2", mode="search", flat_quality=False, fci=checked["fci"], fciq=checked["fciq"],
               objective_score=checked["fciq"], tb=checked["tb"], validator_pass=True, shared_from_strategy="S2",
               own_search_time_s=0., preparation_time_s=time.perf_counter()-began,
               layout_sha256=digest_layout, config_hash=digest, code_hash=job["code_hash"],
               result_origin=origin, source_layout_sha256=source_sha)
    write_json(record, dict(code_hash=job["code_hash"], layouts={"S2.json": digest_layout},
                           rows=[row], elapsed_seconds=time.perf_counter()-began))
    return [row]
