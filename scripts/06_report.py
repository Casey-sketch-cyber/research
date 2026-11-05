"""Independently audit the complete frozen pilot and generate G2 evidence."""
from __future__ import annotations

import ast
import hashlib
import json
import math
from pathlib import Path
import subprocess
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import shapely
from shapely.geometry import GeometryCollection
from shapely.ops import unary_union
from tqdm import tqdm

from fea.geometry.unit import Unit, parts
from fea.geometry.raster import rasterize, door_keepout, fixed_service_doors, FURNISHABLE
from fea.households import parse_households
from fea.io import prepare_cli, start_run, write_json, sha256_file
from fea.validate import validate_layout
from fea.viz.corpus import draw_unit
from fea.viz.layouts import render_layout

REVIEW_RENDER_STYLE = {"figure.constrained_layout.h_pad": .15,
    "figure.constrained_layout.w_pad": .08, "figure.constrained_layout.hspace": .16,
    "figure.constrained_layout.wspace": .06}


def method_signature() -> str:
    """Use the same explicit code dependency list as the frozen pilot runner."""
    paths = [Path("src/fea")/p for p in ("config.py", "households.py", "metrics.py", "validate.py",
        "geometry/unit.py", "geometry/raster.py", "furniture/library.py", "furniture/candidates.py",
        "solve/cpsat.py", "solve/reachability.py", "viz/corpus.py", "viz/layouts.py")]+[Path("scripts/06_pilot.py")]
    return hashlib.sha256(b"".join(p.read_bytes() for p in paths)).hexdigest()


def access_diagnostic(unit, grid, checked, width):
    """Compare empty raster access with continuous conservative source geometry.

    The continuous check is diagnostic only; it never replaces validator scores.
    A tiny numerical closure joins coincident polygon edges, not physical gaps.
    """
    free = unary_union([unit.classes.get(k, GeometryCollection()) for k in
                        ("furnishable", "storage_only", "walkable_only")]).difference(unit.walls)
    portal = door_keepout(unit.entrance, unit.interior, both_sides=True).difference(unit.interior).difference(unit.walls)
    continuous = unary_union([free, portal]).buffer(1e-9).buffer(-width/2, quad_segs=32)
    connected = unary_union([p for p in parts(continuous) if p.intersection(portal).area > 1e-9])
    doors = fixed_service_doors(unit, grid.resolution)
    reached = checked["paths"]["normal"]["night"]
    rows = []
    for index, (target, door) in enumerate(zip(grid.service_targets, doors)):
        raster_ok = bool(np.any(target & reached))
        continuous_ok = not connected.intersection(door.buffer(.3+grid.resolution)).is_empty
        reason = ("reachable" if raster_ok else "conservative_raster_loss" if continuous_ok
                  else "fixed_classification_or_source_geometry_blocks_continuous_approach")
        rows.append(dict(unit_key=unit.unit_key, source=unit.source, nia_m2=unit.interior.area,
                         target_index=index, raster_reachable=raster_ok,
                         continuous_diagnostic_reachable=continuous_ok, reason=reason,
                         approach_distance_m=None if connected.is_empty else connected.distance(door),
                         target_cells=int(target.sum()), reachable_empty_cells=int(reached.sum())))
    return rows


def render_access(units, grids, checked):
    """Show every frozen unit's empty reachable region and fixed-service targets."""
    for source in ("D1", "D2", "D3"):
        selected = [u for u in units if u.source == source]
        fig, axes = plt.subplots(2, 4, figsize=(16, 9), layout="constrained")
        for ax, unit in zip(axes.flat, selected):
            grid, result = grids[unit.unit_key], checked[unit.unit_key]
            draw_unit(ax, unit, short=True)
            yy, xx = np.where(result["paths"]["normal"]["night"])
            ax.scatter(grid.origin[0]+(xx+.5)*grid.resolution, grid.origin[1]+(yy+.5)*grid.resolution,
                       s=1.5, color="#009b9d", alpha=.55, linewidths=0)
            for i, target in enumerate(grid.service_targets):
                yy, xx = np.where(target)
                okay = bool(np.any(target & result["paths"]["normal"]["night"]))
                ax.scatter(grid.origin[0]+(xx+.5)*grid.resolution, grid.origin[1]+(yy+.5)*grid.resolution,
                           s=4, color="#004da5" if okay else "#e02f4b", linewidths=0)
                if len(xx): ax.text(grid.origin[0]+(xx.mean()+.5)*grid.resolution,
                                   grid.origin[1]+(yy.mean()+.5)*grid.resolution, str(i), fontsize=9)
            ax.set_title(f"{unit.unit_key[-8:]} | NIA {unit.interior.area:.2f} m²\nEmpty access: {'PASS' if result['pass'] else 'FAIL'}", fontsize=10)
        for ax in axes.flat[len(selected):]: ax.axis("off")
        fig.suptitle(f"{source} frozen pilot: empty-layout access\nCyan: reachable centres; blue/red: reachable/unreachable fixed-service approaches", fontsize=13)
        fig.savefig(Path("results/pilot")/f"empty_access_{source}.png", dpi=180)
        plt.close(fig)


def runtime_projection(frame, config):
    """Source-stratified measured-runtime extrapolation, with explicit limitations."""
    sample = pd.read_csv("results/corpus/expA_sample.csv")
    overhead = pd.read_csv("results/candidates/counts.csv").drop_duplicates("unit_key")
    by_unit = frame.groupby(["source", "unit_key"]).solve_time_s.sum().reset_index()
    source_rows = []
    for source in ("D1", "D2", "D3"):
        elapsed = by_unit[by_unit.source == source].solve_time_s
        prep = overhead[overhead.source == source]
        preparation = float((prep.raster_time_s+prep.candidate_time_s).mean())
        count = int((sample.source == source).sum())
        seconds = float(elapsed.mean()+preparation)
        source_rows.append(dict(source=source, full_units=count, pilot_units=len(elapsed),
            mean_unit_solver_s=float(elapsed.mean()), mean_unit_preparation_s=preparation,
            projected_s=count*seconds, projected_h=count*seconds/3600))
    sources = pd.DataFrame(source_rows)
    sources.to_csv("results/pilot/runtime_projection.csv", index=False)
    total = float(sources.projected_h.sum())
    rng = np.random.default_rng(config["seed"])
    draws = np.zeros(1000)
    for row in source_rows:
        values = by_unit[by_unit.source == row["source"]].solve_time_s.to_numpy()
        draws += row["full_units"]*(rng.choice(values, (len(draws), len(values)), replace=True).mean(axis=1)
                                   +row["mean_unit_preparation_s"])/3600
    base_other_s = float(sources[sources.source != "D1"].projected_s.sum())
    d1 = source_rows[0]
    d1_unit_s = d1["mean_unit_solver_s"]+d1["mean_unit_preparation_s"]
    cap = max(0, min(d1["full_units"], math.floor((36*3600-base_other_s)/d1_unit_s)))
    # Buffer is an explicit scheduling assumption, not an observed performance gain.
    buffered_cap = max(0, min(cap, math.floor((36*3600/1.2-base_other_s)/d1_unit_s)))
    return dict(concurrent_solves=1, projected_h=total,
                descriptive_unit_bootstrap_interval_h=np.quantile(draws, [.025, .975]).tolist(),
                budget_h=36, over_budget=total > 36,
                d2_d3_only_h=base_other_s/3600, d1_max_at_point_estimate=cap,
                d1_max_with_20pct_scheduling_margin=buffered_cap,
                adjustment="lower_D1_cap_first" if total > 36 else "no_cap_change_proposed",
                limitations=["One solve at a time; 12 household/strategy cases per unit; preceding-strategy incumbents retained.",
                    "Measured preparation overhead comes from the frozen 24-unit candidate benchmark.",
                    "Source-stratified extrapolation from a small pilot, not a guaranteed completion time.",
                    "D3 intentionally spans six area values rather than a probability sample; bootstrap interval is descriptive.",
                    "Includes fast structurally invalid cases; geometry revisions require a new pilot projection.",
                    "Excludes full-experiment aggregation, I/O, and the selected publication renders; 20% margin is an optional scheduling assumption."])


def main():
    """Audit every saved case before writing method and runtime summaries."""
    parser = prepare_cli(__doc__)
    parser.add_argument("--geometry-only", action="store_true")
    parser.add_argument("--run-tests", action="store_true", help="Run only when no pilot solver is active")
    parser.add_argument("--keep-renders", action="store_true", help="Reuse already checked review-style renders")
    args = parser.parse_args()
    config, digest, _ = start_run(args, "06_report")
    if args.dry_run:
        print("Would independently validate all frozen cases and generate G2 summaries.")
        return
    units = [Unit.from_dict(u) for u in json.loads(Path("results/pilot/pilot_units.json").read_text())["units"]]
    households = parse_households(config["households"], config["furniture"])
    first_h = households[config["households"]["main_households"][0]]
    grids, empty_checked, access_rows, space_rows = {}, {}, [], []
    for unit in tqdm(units, desc="Empty geometry diagnostic"):
        grid = grids[unit.unit_key] = rasterize(unit, config["raster"]["resolution_m"])
        result = empty_checked[unit.unit_key] = validate_layout({"strategy": "S0", "items": [], "service": {}}, grid, config, first_h, diagnostics=True)
        access_rows.extend(access_diagnostic(unit, grid, result, config["furniture"]["meta"]["walking_width"]))
        free = unary_union([unit.classes.get(k, GeometryCollection()) for k in
            ("furnishable", "storage_only", "walkable_only")]).difference(unit.walls)
        portal = door_keepout(unit.entrance, unit.interior, both_sides=True).difference(unit.interior).difference(unit.walls)
        components = parts(unary_union([free, portal]).buffer(1e-9))
        connected = unary_union([p for p in components if p.intersection(portal).area > 1e-9])
        space_rows.append(dict(unit_key=unit.unit_key, source=unit.source, nia_m2=unit.interior.area,
            free_components_before_walking_erosion=len(components),
            connected_furnishable_area_before_erosion_m2=connected.intersection(unit.classes["furnishable"]).area,
            furnishable_area_m2=unit.classes["furnishable"].area,
            furnishable_cells=int((grid.labels == FURNISHABLE).sum()),
            reachable_empty_furnishable_cells=int(((grid.labels == FURNISHABLE) & result["paths"]["normal"]["night"]).sum()),
            empty_fixed_service_valid=result["pass"], config_hash=digest))
    pd.DataFrame(access_rows).to_csv("results/pilot/fixed_service_diagnostic.csv", index=False)
    pd.DataFrame(space_rows).to_csv("results/pilot/empty_space_summary.csv", index=False)
    render_access(units, grids, empty_checked)
    if args.geometry_only:
        print(json.dumps(dict(units=len(units), empty_access_failures=sum(not r["pass"] for r in empty_checked.values()))))
        return
    frame = pd.read_csv("results/pilot/pilot_solutions.csv")
    # Publication padding avoids overlapping row titles on near-square plans.
    # This changes presentation only, never JSON layouts or solver checkpoints.
    plt.rcParams.update(REVIEW_RENDER_STYLE)
    signature = method_signature()
    checks = dict(expected_count=len(frame) == len(units)*len(config["households"]["main_households"])*3,
                  unique_cases=not frame.duplicated(["unit_key", "household", "strategy"]).any(),
                  config_hash=set(frame.config_hash) == {digest}, code_hash=set(frame.code_hash) == {signature})
    audits, artifacts = [], []
    for unit in tqdm(units, desc="Independent saved-layout audit"):
        for household_name in config["households"]["main_households"]:
            for strategy in ("S0", "S1", "S2"):
                stem = unit.unit_key.replace(":", "_")+"_"+household_name.split("_")[0]+"_"+strategy
                path = Path("results/layouts/pilot")/(stem+".json")
                layout = json.loads(path.read_text())
                result = validate_layout(layout, grids[unit.unit_key], config, households[household_name])
                if not args.keep_renders:
                    render_layout(unit, layout, config, households[household_name], path.with_suffix(".png"), grids[unit.unit_key])
                row = frame[(frame.unit_key == unit.unit_key) & (frame.household == household_name) & (frame.strategy == strategy)].iloc[0]
                solver = layout["solver"]
                expected_failure = (not result["pass"] and not empty_checked[unit.unit_key]["pass"]
                    and solver["status"] == "STRUCTURAL_UNREACHABLE"
                    and all(v.startswith("fixed_service_unreachable:") for v in result["violations"]))
                audits.append(dict(unit_key=unit.unit_key, household=household_name, strategy=strategy,
                    independently_valid=result["pass"], explained_failure=expected_failure,
                    csv_fci_difference=abs(row.fci_validator-result["fci"]),
                    json_fci_difference=abs(layout["fci"]-result["fci"]),
                    solver_assignment_fci_difference=abs(solver["fci_solver"]-result["fci"]),
                    tb_difference=abs(layout["tb"]-result["tb"]),
                    hash_match=layout["config_hash"] == digest and layout["code_hash"] == signature,
                    metadata_match=(layout["unit_key"] == unit.unit_key and layout["source"] == unit.source
                        and layout["household"] == household_name and layout["strategy"] == strategy
                        and abs(layout["nia_m2"]-unit.interior.area) <= 1e-6),
                    saved_validation_match=(layout["validator"]["pass"] == result["pass"]
                        and layout["validator"]["violations"] == result["violations"]
                        and bool(row.validator_pass) == result["pass"]),
                    status=solver["status"], termination=solver.get("termination", "search_completed_or_budget_limit"),
                    retained_previous_incumbent=solver.get("retained_previous_incumbent", False),
                    primary_upper_bound=solver.get("primary_upper_bound"),
                    raw_last_model_fci=solver.get("raw_last_model_fci"),
                    window_tiebreak_optimized=solver.get("window_tiebreak_optimized", False),
                    violations=";".join(result["violations"])))
                for item in (path, path.with_suffix(".png")):
                    artifacts.append(dict(path=item.as_posix(), bytes=item.stat().st_size, sha256=sha256_file(item)))
    audit = pd.DataFrame(audits)
    audit.to_csv("results/pilot/validation_audit.csv", index=False)
    pd.DataFrame(artifacts).to_csv("results/pilot/layout_manifest.csv", index=False)
    write_json("reports/pilot_render_style.json", dict(style=REVIEW_RENDER_STYLE,
        layout_jsons_unchanged=True, config_hash=digest, code_hash=signature))
    checks.update(all_valid_or_explained=bool((audit.independently_valid | audit.explained_failure).all()),
        fci_agreement=bool(audit[["csv_fci_difference", "json_fci_difference", "solver_assignment_fci_difference"]].max().max() <= 1e-6),
        tb_agreement=bool(audit.tb_difference.max() <= 1e-6), layout_hashes=bool(audit.hash_match.all()),
        layout_metadata=bool(audit.metadata_match.all()), saved_validation=bool(audit.saved_validation_match.all()),
        publication_sizes=all(a["bytes"] < 50_000_000 for a in artifacts))
    pivot = frame.pivot(index=["unit_key", "household"], columns="strategy", values="fci_validator").reset_index()
    pivot["S1_minus_S0"], pivot["S2_minus_S1"] = pivot.S1-pivot.S0, pivot.S2-pivot.S1
    pivot["ordering_pass"] = (pivot.S1_minus_S0 >= -1e-6) & (pivot.S2_minus_S1 >= -1e-6)
    pivot.to_csv("results/pilot/ordering.csv", index=False)
    checks["strategy_ordering"] = bool(pivot.ordering_pass.all())
    tree = ast.parse(Path("src/fea/validate.py").read_text())
    imports = [node.module or "" for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)]
    imports += [a.name for node in ast.walk(tree) if isinstance(node, ast.Import) for a in node.names]
    checks["independent_validator_imports"] = not any("solve" in m or "candidates" in m or "furniture.library" in m for m in imports)
    stats = frame.groupby(["source", "household", "strategy"]).agg(n=("status", "size"),
        valid=("validator_pass", "sum"), mean_fci=("fci_validator", "mean"), median_fci=("fci_validator", "median"),
        mean_s=("solve_time_s", "mean"), median_s=("solve_time_s", "median"), max_s=("solve_time_s", "max"))
    stats.to_csv("results/pilot/summary_by_group.csv")
    unit_summary = frame.assign(zero_service=frame.fci_validator <= 1e-9).groupby(
        ["source", "unit_key", "nia_m2"]).agg(cases=("status", "size"),
        valid=("validator_pass", "sum"), zero_service=("zero_service", "sum"),
        mean_fci=("fci_validator", "mean"), solver_total_s=("solve_time_s", "sum"))
    unit_summary.to_csv("results/pilot/summary_by_unit.csv")
    projection = runtime_projection(frame, config)
    write_json("reports/pilot_runtime_projection.json", projection)
    test_path = Path("reports/pilot_tests.json")
    if args.run_tests:
        test = subprocess.run([sys.executable, "-m", "pytest", "-q"], capture_output=True, text=True)
        write_json(test_path, dict(command="python -m pytest -q", exit_code=test.returncode,
            stdout=test.stdout.strip(), stderr=test.stderr.strip(), config_hash=digest, code_hash=signature))
    tests = json.loads(test_path.read_text()) if test_path.exists() else {}
    checks["tests_current_and_passed"] = tests.get("exit_code") == 0 and tests.get("code_hash") == signature
    summary = dict(config_hash=digest, code_hash=signature, cases=len(frame), units=len(units),
        valid=int(frame.validator_pass.sum()), explained_invalid=int(audit.explained_failure.sum()),
        empty_invalid_units=sum(not c["pass"] for c in empty_checked.values()),
        ordering_pairs=len(pivot), ordering_failures=int((~pivot.ordering_pass).sum()),
        status_counts={k: int(v) for k, v in frame.status.value_counts().items()},
        final_valid_empty=int(((frame.n_items == 0) & frame.validator_pass).sum()),
        final_valid_nonempty=int(((frame.n_items > 0) & frame.validator_pass).sum()),
        final_valid_zero_service=int(((frame.fci_validator <= 1e-9) & frame.validator_pass).sum()),
        final_valid_nonempty_zero_service=int(((frame.n_items > 0) & (frame.fci_validator <= 1e-9) & frame.validator_pass).sum()),
        retained_previous_incumbents=int(audit.retained_previous_incumbent.sum()),
        early_bound_incumbents=int((audit.termination == "primary_bound_incumbent").sum()),
        solver_time_sum_s=float(frame.solve_time_s.sum()),
        runtime_quantiles_s={str(q): float(frame.solve_time_s.quantile(q)) for q in (.5, .9, .95, 1)},
        layout_artifacts=len(artifacts), artifact_bytes=sum(a["bytes"] for a in artifacts),
        checks={k: bool(v) for k, v in checks.items()}, **{"pass": bool(all(checks.values()))})
    write_json("reports/pilot_audit.json", summary)
    print(json.dumps(summary, indent=2))
    raise SystemExit(not summary["pass"])


if __name__ == "__main__":
    main()
