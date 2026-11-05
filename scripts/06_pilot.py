"""Prepare and run the frozen 20-unit, four-household, three-strategy pilot."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import time

import numpy as np
import pandas as pd
from tqdm import tqdm

from fea.geometry.unit import Unit
from fea.geometry.raster import rasterize
from fea.furniture.library import library
from fea.furniture.candidates import generate_candidates
from fea.households import parse_households
from fea.io import prepare_cli, start_run, write_json
from fea.solve.cpsat import solve_layout
from fea.validate import validate_layout
from fea.viz.layouts import render_layout


def prepare(config, digest):
    """Select by NIA before viewing solver outcomes; serialize normalized geometry."""
    sample = pd.read_csv("results/corpus/expA_sample.csv")
    assert set(sample.config_hash) == {digest}, "Rebuild corpus for the current config"
    rng = np.random.default_rng(config["seed"])
    indices = []
    for source, count in (("D1", 8), ("D2", 6)):
        ordered = sample[sample.source == source].sort_values(["nia_m2", "unit_key"]).index.to_numpy()
        indices.extend(int(rng.choice(stratum)) for stratum in np.array_split(ordered, count))
    for area in (8, 12, 16, 22, 32, 40):
        options = sample[(sample.source == "D3") & np.isclose(sample.nia_m2, area)].sort_values("unit_key").index
        indices.append(int(rng.choice(options.to_numpy())))
    selected = sample.loc[indices].copy().reset_index(drop=True)
    selected["pilot_order"] = np.arange(len(selected))
    selected["selection_rule"] = "fixed-seed NIA rank strata; D3 target areas 8/12/16/22/32/40"
    output = Path("results/pilot"); output.mkdir(parents=True, exist_ok=True)
    frozen = output/"pilot_units.csv"
    if frozen.exists():
        prior = pd.read_csv(frozen)
        assert prior.unit_key.tolist() == selected.unit_key.tolist(), "Pilot selection must not change after viewing results"
    selected.to_csv(frozen, index=False)
    processed = pd.read_parquet(Path(config["paths"]["processed"])/"corpus_units.parquet",
        columns=["unit_key", "unit_json"], filters=[("unit_key", "in", selected.unit_key.tolist())]).set_index("unit_key")
    units = [Unit.from_dict(json.loads(processed.loc[key, "unit_json"])) for key in selected.unit_key]
    write_json(output/"pilot_units.json", dict(seed=config["seed"], config_hash=digest, units=[u.to_dict() for u in units]))
    h = parse_households(config["households"], config["furniture"])[config["households"]["main_households"][0]]
    access = []
    for unit in units:
        grid = rasterize(unit, config["raster"]["resolution_m"])
        checked = validate_layout({"strategy": "S0", "items": [], "service": {}}, grid, config, h, diagnostics=True)
        failures = [v for v in checked["violations"] if ":normal:night:" in v]
        access.append(dict(unit_key=unit.unit_key, source=unit.source, nia_m2=unit.interior.area,
            entrance_cells=int(grid.entrance.sum()), portal_cells=int(grid.entrance_extension.sum()),
            reachable_empty_cells=int(checked["paths"]["normal"]["night"].sum()),
            fixed_service_targets=len(grid.service_targets), empty_layout_valid=checked["pass"],
            failures=";".join(failures), config_hash=digest))
    pd.DataFrame(access).to_csv(output/"empty_access_audit.csv", index=False)
    return units


def main():
    """Resume only identical config/code runs; every partial aggregate is labelled."""
    parser = prepare_cli(__doc__)
    parser.add_argument("--prepare-only", action="store_true")
    parser.add_argument("--max-instances", type=int)
    parser.add_argument("--unit-index", type=int, help="Debug one selected unit; does not replace the frozen sample")
    args = parser.parse_args()
    config, digest, start = start_run(args, "06_pilot")
    if args.dry_run:
        print("Would freeze 20 sample units, then solve 240 cases and render each saved layout.")
        return
    units = prepare(config, digest)
    if args.prepare_only:
        print(json.dumps({"units": len(units), "expected_instances": 240, "config_hash": digest}))
        return
    if args.unit_index is not None: units = [units[args.unit_index]]
    files = [Path("src/fea")/p for p in ("config.py", "households.py", "metrics.py", "validate.py",
        "geometry/unit.py", "geometry/raster.py", "furniture/library.py", "furniture/candidates.py",
        "solve/cpsat.py", "solve/reachability.py", "viz/corpus.py", "viz/layouts.py")]+[Path(__file__)]
    signature = hashlib.sha256(b"".join(p.read_bytes() for p in files)).hexdigest()
    cache = Path(config["paths"]["interim"])/"pilot"/(digest[:12]+"_"+signature[:12])
    cache.mkdir(parents=True, exist_ok=True)
    households = parse_households(config["households"], config["furniture"])
    rows, completed = [], 0
    # The current effective quota supports one 8-thread solver at a time. No
    # nested solver process pool is started; portable runners may parallelize units.
    progress = tqdm(total=len(units)*12, desc="Pilot solves")
    for unit in units:
        grid = rasterize(unit, config["raster"]["resolution_m"])
        candidates = generate_candidates(grid, library(config["furniture"]), config["raster"]["orientations_deg"])
        for household_name in config["households"]["main_households"]:
            household = households[household_name]
            incumbent = None
            for strategy in ("S0", "S1", "S2"):
                stem = unit.unit_key.replace(":", "_")+"_"+household_name.split("_")[0]+"_"+strategy
                checkpoint = cache/(stem+".json")
                if checkpoint.exists():
                    layout = json.loads(checkpoint.read_text())
                else:
                    layout = solve_layout(unit, household, strategy, config, incumbent, (grid, candidates))
                    layout["code_hash"] = signature
                    write_json(checkpoint, layout)
                checked = validate_layout(layout, grid, config, household)
                assert abs(checked["fci"]-layout["fci"]) < 1e-6
                output = Path("results/layouts/pilot")/(stem+".json")
                write_json(output, layout)
                render_layout(unit, layout, config, household, output.with_suffix(".png"), grid)
                solver = layout["solver"]
                rows.append(dict(unit_key=unit.unit_key, source=unit.source, nia_m2=unit.interior.area,
                    furnishable_area_m2=unit.classes["furnishable"].area, household=household_name,
                    strategy=strategy, algorithm="cp_sat", status=solver["status"], fci_validator=checked["fci"],
                    fci_solver=solver["fci_solver"], tb=checked["tb"], n_items=len(layout["items"]),
                    served_hours=checked["served_hours"], demanded_hours=checked["demanded_hours"],
                    solve_time_s=solver["time_s"], reach_iterations=solver["reach_iterations"],
                    objective=solver["objective"], bound=solver["bound"], validator_pass=checked["pass"],
                    n_violations=len(checked["violations"]), violations=";".join(checked["violations"]),
                    config_hash=digest, code_hash=signature))
                pd.DataFrame(rows).to_csv("results/pilot/pilot_solutions_PARTIAL.csv", index=False)
                if checked["pass"]: incumbent = layout
                completed += 1; progress.update(1)
                if args.max_instances and completed >= args.max_instances: break
            if args.max_instances and completed >= args.max_instances: break
        if args.max_instances and completed >= args.max_instances: break
    progress.close()
    if len(rows) == 240:
        pd.DataFrame(rows).to_csv("results/pilot/pilot_solutions.csv", index=False)
    print(json.dumps(dict(completed=len(rows), expected=240, total_wall_time_s=time.perf_counter()-start,
                         config_hash=digest, code_hash=signature)))


if __name__ == "__main__":
    main()
