"""Frozen round-2 mechanism tests and small-home budget comparisons."""
from __future__ import annotations

import os
for _name in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ[_name] = "1"

from concurrent.futures import ProcessPoolExecutor, as_completed
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import time

import numpy as np
import pandas as pd
from tqdm import tqdm

from fea.config import config_hash
from fea.diagnostics import mechanism_shell, mechanism_witness
from fea.furniture.candidates import generate_candidates
from fea.furniture.library import library
from fea.geometry.raster import rasterize
from fea.geometry.unit import Unit
from fea.households import parse_households
from fea.io import prepare_cli, start_run, write_json
from fea.solve.cpsat import solve_layout
from fea.validate import validate_layout

ROOT = Path("results/pilot/round2")


def code_hash() -> str:
    """Fingerprint the full implementation and this driver before solving."""
    files = sorted(Path("src/fea").rglob("*.py")) + [Path(__file__)]
    return hashlib.sha256(b"".join(str(p).encode()+p.read_bytes() for p in files)).hexdigest()


def prepare(config: dict) -> None:
    """Freeze additional small units by seed, without using any solver outcome."""
    sample = pd.read_csv("results/corpus/expA_sample.csv")
    pilot = json.loads(Path("results/pilot/pilot_units.json").read_text())["units"]
    selected_pilot = [u for u in pilot if Unit.from_dict(u).interior.area <= 22+1e-8]
    keys = {u["unit_key"] for u in pilot}
    pool = sample[(sample.source == "D3") & sample.nia_m2.between(9-1e-8, 15+1e-8)
                  & ~sample.unit_key.isin(keys)].sort_values("unit_key")
    rng = np.random.default_rng(config["seed"])
    extra = pool.iloc[np.sort(rng.choice(len(pool), 12, replace=False))]
    selected_keys = [u["unit_key"] for u in selected_pilot] + extra.unit_key.tolist()
    selection = sample.set_index("unit_key").loc[selected_keys].reset_index()
    selection["selection_reason"] = ["pilot_nia_le_22"]*len(selected_pilot) + ["fixed_seed_D3_9_to_15"]*12
    output = ROOT/"small_units.csv"
    if output.exists():
        assert pd.read_csv(output).unit_key.tolist() == selected_keys, "Frozen sample cannot change"
    output.parent.mkdir(parents=True, exist_ok=True)
    selection.to_csv(output, index=False)
    corpus = pd.read_parquet(Path(config["paths"]["processed"])/"corpus_units.parquet",
                             columns=["unit_key", "unit_json"]).set_index("unit_key")
    serialized = [json.loads(corpus.loc[key, "unit_json"]) for key in selected_keys]
    write_json(ROOT/"small_units.json", {"seed": config["seed"], "units": serialized,
        "config_hash": config_hash(config), "sampling_used_outcomes": False,
        "sample_sha256": hashlib.sha256(Path("results/corpus/expA_sample.csv").read_bytes()).hexdigest()})
    households = parse_households(config["households"], config["furniture"])
    rows = []
    for area in (9, 11, 13):
        unit = mechanism_shell(area)
        grid = rasterize(unit)
        write_json(ROOT/"witnesses"/f"shell_{area}.json", unit.to_dict())
        for name in config["households"]["main_households"]:
            if not name.startswith(("H1_", "H3_")):
                continue
            layout = mechanism_witness(area, households[name])
            checked = validate_layout(layout, grid, config, households[name])
            assert checked["pass"], checked["violations"]
            layout["validator"] = checked
            write_json(ROOT/"witnesses"/f"shell_{area}_{name[:2]}.json", layout)
            rows.append(dict(unit_key=unit.unit_key, nia_m2=area, household=name,
                lower_bound=checked["fci"], tb=checked["tb"], validator_pass=checked["pass"],
                h1_sleep2_does_not_satisfy_sleep1=name.startswith("H1"), population_eligible=False))
    pd.DataFrame(rows).to_csv(ROOT/"witnesses.csv", index=False)
    print(json.dumps({"small_units": len(serialized), "witnesses": len(rows)}))


def solve_pair(job: tuple) -> list[dict]:
    """Search independently of the hand-written witness, revalidating checkpoints."""
    raw, name, config, directory, signature = job
    unit = Unit.from_dict(raw)
    household = parse_households(config["households"], config["furniture"])[name]
    grid = rasterize(unit, config["raster"]["resolution_m"],
        household.overrides.get("walking_width", config["furniture"]["meta"]["walking_width"]),
        config["raster"]["source_gap_close_m"])
    candidates = generate_candidates(grid, library(config["furniture"]),
        config["raster"]["orientations_deg"], config["raster"]["anchor_stride_m"])
    incumbent, layouts = None, {}
    for strategy in ("S1", "S2"):
        path = Path(directory)/(unit.unit_key.replace(":", "_")+"_"+name+"_"+strategy+".json")
        if path.exists():
            layout = json.loads(path.read_text())
            assert layout["code_hash"] == signature and layout["config_hash"] == config_hash(config)
        else:
            layout = solve_layout(unit, household, strategy, config, incumbent, (grid, candidates))
            layout.update(code_hash=signature, config_hash=config_hash(config))
            write_json(path, layout)
        checked = validate_layout(layout, grid, config, household)
        assert checked["pass"], checked["violations"]
        assert abs(checked["fci"]-layout["fci"]) < 1e-7
        incumbent = layout
        layouts[strategy] = layout
    # Downward exchange is valid only for an independently valid S1 schedule.
    downward = deepcopy(layouts["S2"])
    downward["strategy"] = "S1"
    checked = validate_layout(downward, grid, config, household)
    if checked["pass"] and checked["fci"] > layouts["S1"]["fci"]+1e-9:
        downward["solver"] = {**layouts["S1"]["solver"], "shared_from_strategy": "S2"}
        layouts["S1"] = downward
    rows = []
    for strategy, layout in layouts.items():
        checked = validate_layout(layout, grid, config, household)
        filename = unit.unit_key.replace(":", "_")+"_"+name+"_"+strategy+".json"
        write_json(Path(directory)/"validated"/filename, layout)
        sol = layout["solver"]
        lower = (validate_layout(mechanism_witness(int(round(unit.interior.area)), household), grid,
                                 config, household)["fci"] if unit.source == "diagnostic" else None)
        rows.append(dict(unit_key=unit.unit_key, source=unit.source, nia_m2=unit.interior.area,
            household=name, strategy=strategy, fci_validator=checked["fci"], tb=checked["tb"],
            validator_pass=checked["pass"], status=sol["status"], solve_time_s=sol["time_s"],
            reach_iterations=sol["reach_iterations"], greedy_fci=sol.get("greedy_fci"),
            known_lower_bound=lower, witness_provided_to_solver=False,
            config_hash=config_hash(config), code_hash=signature, layout_file=filename))
    return rows


def run(config: dict, args) -> None:
    """Run one immutable comparison arm, with resumable per-case checkpoints."""
    config = deepcopy(config)
    config["solver"].update(num_workers=args.workers, time_limit_s=args.limit)
    config["raster"]["anchor_stride_m"] = args.stride
    signature = code_hash()
    units = ([mechanism_shell(a).to_dict() for a in (9, 11, 13)] if args.mode == "mechanism"
             else json.loads((ROOT/"small_units.json").read_text())["units"])
    names = [h for h in config["households"]["main_households"]
             if args.mode != "mechanism" or h.startswith(("H1_", "H3_"))]
    if args.unit_key:
        units = [u for u in units if u["unit_key"] == args.unit_key]
    if args.household:
        names = [h for h in names if h.startswith(args.household+"_")]
    assert units and names
    directory = ROOT/args.arm
    cache = Path(config["paths"]["interim"])/"round2"/args.arm
    concurrency = min(max(1, 14//args.workers), args.max_jobs or 14)
    manifest = dict(mode=args.mode, arm=args.arm, code_hash=signature, config_hash=config_hash(config),
        num_workers=args.workers, concurrent_solves=concurrency, time_limit_s=args.limit,
        anchor_stride_m=args.stride, expected_cases=len(units)*len(names)*2,
        inputs_hash=hashlib.sha256(json.dumps([units, names], sort_keys=True).encode()).hexdigest(),
        cache=cache.as_posix(), witness_provided_to_solver=False)
    if (directory/"run.json").exists():
        assert json.loads((directory/"run.json").read_text()) == manifest, "New code/config requires a new arm name"
    write_json(directory/"run.json", manifest)
    prior = len(list(cache.glob("*.json")))
    start, rows = time.perf_counter(), []
    jobs = [(u, h, config, str(cache), signature) for u in units for h in names]
    with ProcessPoolExecutor(max_workers=manifest["concurrent_solves"]) as pool:
        pending = [pool.submit(solve_pair, job) for job in jobs]
        for result in tqdm(as_completed(pending), total=len(pending), desc=args.arm):
            rows.extend(result.result())
            pd.DataFrame(rows).to_csv(directory/"cases_PARTIAL.csv", index=False)
    frame = pd.DataFrame(rows).sort_values(["unit_key", "household", "strategy"])
    frame.to_csv(directory/"cases.csv", index=False)
    pairs = frame.pivot(index=["unit_key", "household"], columns="strategy", values="fci_validator")
    pairs["gain_S2_minus_S1"] = pairs.S2-pairs.S1
    pairs.reset_index().to_csv(directory/"pairs.csv", index=False)
    write_json(directory/"summary.json", {**manifest, "completed_cases": len(rows),
        "wall_time_s": time.perf_counter()-start, "resumed_checkpoints": prior,
        "fresh_throughput_measurement": prior == 0, "s2_improved_pairs": int((pairs.gain_S2_minus_S1 > 1e-9).sum()),
        "mean_s1": float(pairs.S1.mean()), "mean_s2": float(pairs.S2.mean()),
        "s2_below_witness": int(((frame.strategy == "S2") &
                                   (frame.fci_validator < frame.known_lower_bound-1e-9)).sum())})


def main():
    parser = prepare_cli(__doc__)
    parser.add_argument("--mode", choices=["prepare", "mechanism", "small"], default="prepare")
    parser.add_argument("--arm", default="mechanism_w8_s10_t300")
    parser.add_argument("--workers", type=int, choices=[1, 2, 4, 8], default=8)
    parser.add_argument("--limit", type=int, choices=[30, 60, 120, 300], default=300)
    parser.add_argument("--stride", type=float, choices=[.1, .2], default=.1)
    parser.add_argument("--unit-key")
    parser.add_argument("--household")
    parser.add_argument("--max-jobs", type=int, choices=range(1, 15), help="Lower concurrency when another diagnostic uses resources")
    args = parser.parse_args()
    config, _, _ = start_run(args, "06_round2")
    if args.dry_run:
        print("Would freeze R1 inputs or run a resumable, independently validated comparison; no uploads.")
    elif args.mode == "prepare":
        prepare(config)
    else:
        run(config, args)


if __name__ == "__main__":
    main()
