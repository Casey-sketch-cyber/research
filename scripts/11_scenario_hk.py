"""Run all prescribed 8–20 m² scenario sizes using solver evidence and accepted kits."""
from copy import deepcopy
from datetime import datetime, timezone
import fcntl
import json
from pathlib import Path
import time

import numpy as np
import pandas as pd
from tqdm import tqdm

from fea.config import config_hash
from fea.data.d3_shells import load_d3
from fea.geometry.normalize import normalize
from fea.geometry.unit import Unit
from fea.io import prepare_cli, start_run, write_json
from phase07_corrected import load_corrected
from phase07_evaluability import evaluate_empty
from phase09_ablation_jobs import run_ablation
from phase09_execution import apply_production, checked_inputs, cpu_slots, fingerprint, hash_inputs, load_json, run_weighted
from phase11_hk_cases import run_scenario_kit
from phase11_hk_report import export_hk
from phase11_kit_design import kit_configuration

ROOT = Path("results/scenario_hk")
K = Path("results/expK")
F1 = Path("results/expA_f1")
SIZES = list(range(8, 21))


def shell_record(unit, origin, eligible, reason):
    p = unit.meta["parameters"]
    shape = [p["aspect_ratio"], p["entrance_position"], p["window_position"]]
    return dict(unit_key=unit.unit_key, area_m2=int(p["gross_area_m2"]), nia_m2=unit.interior.area,
                aspect_ratio=shape[0], entrance_position=shape[1], window_position=shape[2],
                shape="|".join(map(str, shape)), origin=origin, evaluable=bool(eligible), eligibility_reason=reason)


def complete_shells(config, corrected, corpus):
    """Keep the accepted D3 grid and generate the two absent integer sizes."""
    source = corrected[corrected.source.eq("D3") & corrected.nia_m2.between(8-1e-8, 20+1e-8)]
    serialized, records = {}, []
    for key in sorted(source.unit_key.unique()):
        serialized[key] = corpus.loc[key, "unit_json"]
        unit = Unit.from_dict(json.loads(serialized[key]))
        records.append(shell_record(unit, "accepted_D3", True, "accepted_E1"))
    existing = {row["area_m2"] for row in records}
    absent = sorted(set(SIZES)-existing)
    cfg = deepcopy(config)
    cfg["shells_D3"]["areas_m2"] = absent
    for unit in load_d3(cfg):
        unit = normalize(unit)
        generator_failure = unit.meta.get("generator_failure")
        result = evaluate_empty(unit, config["raster"]["resolution_m"], config["raster"]["source_gap_close_m"])
        eligible = not generator_failure and result["evaluable"]
        records.append(shell_record(unit, "integer_size_completion", eligible, generator_failure or result["reason"]))
        if eligible:
            serialized[unit.unit_key] = json.dumps(unit.to_dict())
    shells = pd.DataFrame(records).sort_values(["area_m2", "shape"]).reset_index(drop=True)
    combos = config["shells_D3"]
    expected = len(SIZES)*len(combos["aspect_ratios"])*len(combos["entrance_positions"])*len(combos["window_positions"])
    if len(shells) != expected or shells.duplicated(["area_m2", "shape"]).any():
        raise ValueError("Scenario geometry template coverage differs")
    if set(shells.loc[shells.evaluable, "area_m2"]) != set(SIZES):
        raise ValueError("At least one prescribed size has no eligible geometry")
    return shells, serialized


def wait_for_kit(wait):
    path = K/"acceptance.json"
    while not path.exists():
        if not wait:
            raise ValueError("Reduced K is not complete")
        state = Path(".tmp/g3_kit_pipeline.json")
        if state.exists() and load_json(state)["status"] == "failed":
            raise ValueError("K execution failed")
        time.sleep(30)
    gate = load_json(path)
    if not gate["passed"] or not gate["all_layouts_valid"]:
        raise ValueError("K acceptance differs")
    checked_inputs(gate["outputs"])
    return gate


def collect(worker, stage, tasks, prior=0):
    rows = []
    for done, values in enumerate(tqdm(run_weighted(worker, tasks, cpu_slots()), total=len(tasks), desc=stage), 1):
        rows.extend(values)
        if done % 5 == 0 or done == len(tasks):
            write_json(ROOT/"progress.json", dict(status="running", stage=stage, completed_tasks=done,
                       expected_tasks=len(tasks), prior_layouts=prior, completed_layouts=prior+len(rows)))
    return pd.DataFrame(rows)


def run(config, digest, corrected, shells, serialized):
    began = time.perf_counter()
    sources = [
        K/"acceptance.json", K/"kit.yaml", K/"confirmations.csv", K/"run.json",
        F1/"solutions.csv", F1/"acceptance.json", F1/"run.json", "results/expA/run.json",
        "reports/schemas/D6_data.csv", "reports/schemas/D6.md", "reports/schemas/D1_opening_dimensions.json",
        "scripts/11_scenario_hk.py", "scripts/phase11_hk_cases.py", "scripts/phase11_hk_report.py",
        "scripts/phase07_evaluability.py", "scripts/phase09_ablation_jobs.py", "scripts/phase09_execution.py",
        *sorted(Path("scripts").glob("phase11_kit_*.py")), *sorted(Path("src/fea").rglob("*.py")),
    ]
    inputs = hash_inputs(sources)
    code = fingerprint(dict(config_hash=digest, inputs=inputs, shells=hash_inputs([ROOT/"frozen_shells.csv"])))
    previous = ROOT/"run.json"
    if previous.exists() and load_json(previous)["code_hash"] != code:
        raise ValueError("Scenario inputs changed")
    cache = Path(config["paths"]["interim"])/"scenario_hk"/code[:18]
    write_json(previous, dict(status="running", code_hash=code, inputs=inputs, cache=cache.as_posix()))
    accepted_shells = shells[shells.evaluable]
    households = config["hk_scenario"]["households"]
    production = load_json(F1/"run.json")["production_settings"]
    old_cache = load_json("results/expA/run.json")["cache"]
    f1_cache = load_json(F1/"run.json")["cache"]
    main = corrected[corrected.unit_key.isin(accepted_shells.unit_key) & corrected.household.isin(households)].copy()
    main["fci"] = main.fci_validator
    main["fciq"] = main.fci
    main["result_origin"] = main.result_origin.astype(str)
    baseline_layouts = {}
    for row in main[main.strategy.eq("S2")].to_dict("records"):
        path = old_cache if row["result_origin"] == "original_A_H1H2_verified_unaffected" else f1_cache
        row["path"] = (Path(path)/row["budget_group"]/"shared"/row["layout_file"]).as_posix()
        baseline_layouts[row["unit_key"], row["household"]] = row
    catalog_jobs = []
    for row in accepted_shells[accepted_shells.origin == "integer_size_completion"].itertuples(index=False):
        cfg, _ = apply_production(config, production, row.nia_m2)
        for household in households:
            key = fingerprint([row.unit_key, household, "catalogue"])[:24]
            catalog_jobs.append(dict(task_key=key, sample="HK", kind="production", value="integer_size_completion",
                                    config=cfg, threads=cfg["solver"]["num_workers"], unit_json=serialized[row.unit_key],
                                    household=household, reference={}, exact_control=False,
                                    cache=(cache/"catalogue").as_posix(), fingerprint=code))
    additional = collect(run_ablation, "catalogue_missing_sizes", catalog_jobs, len(main))
    if len(additional):
        additional["fci"] = additional.fci_validator
        additional["fciq"] = additional.fci
        for row in additional[additional.strategy.eq("S2")].to_dict("records"):
            row["path"] = (cache/"catalogue"/row["task_key"]/"S2.json").as_posix()
            baseline_layouts[row["unit_key"], row["household"]] = row
    catalogue = pd.concat([main, additional], ignore_index=True)
    fields = ["unit_key", "household", "strategy", "fci", "fciq", "tb", "validator_pass", "config_hash", "code_hash", "result_origin"]
    catalogue = catalogue[fields]
    if len(catalogue) != len(accepted_shells)*len(households)*3:
        raise ValueError("Incomplete catalogue scenario")

    selection = load_json(K/"kit.yaml")["by_household"]
    confirmed = pd.read_csv(K/"confirmations.csv")
    selected = confirmed[(confirmed.condition == "kit") & confirmed.strategy.eq("S2")]
    k_cache = Path(load_json(K/"run.json")["cache"])
    exact = {}
    for row in selected.to_dict("records"):
        row["path"] = (k_cache/row["task_key"]/"S2.json").as_posix()
        exact[row["unit_key"], row["household"]] = row
    kit_jobs = []
    for household, designs in selection.items():
        if household not in households:
            raise ValueError("Selected kit is outside the configured scenario")
        design = designs["kit"]
        if config_hash(kit_configuration(config, household, design)[0]) != design["dimension_config_hash"]:
            raise ValueError("Kit dimension specification differs")
        for row in accepted_shells.itertuples(index=False):
            base, _ = apply_production(config, production, row.nia_m2)
            cfg, quality = kit_configuration(base, household, design)
            key = fingerprint([row.unit_key, household, design["kit_id"]])[:24]
            kit_jobs.append(dict(task_key=key, unit_json=serialized[row.unit_key], household=household,
                                 config=cfg, qualities=quality, kit_id=design["kit_id"], flat=False, mode="search",
                                 code_hash=code, threads=cfg["solver"]["num_workers"], cache=(cache/"kit").as_posix(),
                                 deadline_epoch=float("inf"), exact_kit=exact.get((row.unit_key, household)),
                                 catalogue_layout=baseline_layouts.get((row.unit_key, household))))
    fitted = collect(run_scenario_kit, "kit_S2", kit_jobs, len(catalogue))
    fitted["strategy"] = "S2_kit"
    fitted["result_origin"] = fitted.get("result_origin", pd.Series(index=fitted.index, dtype=object)).fillna("fresh_quality_solver")
    data = pd.concat([catalogue, fitted[fields]], ignore_index=True).merge(
        accepted_shells[["unit_key", "area_m2", "nia_m2", "shape"]], on="unit_key", validate="many_to_one")
    if len(data) != len(accepted_shells)*(3*len(households)+len(selection)) or data.duplicated(["unit_key", "household", "strategy"]).any():
        raise ValueError("Scenario case coverage differs")
    if not data.validator_pass.all() or not data.fciq.between(0., 1+1e-9).all() or (data.fciq > data.fci+1e-8).any():
        raise ValueError("Scenario retained invalid outputs")
    outputs = export_hk(config, digest, data, shells, time.perf_counter()-began)
    checked_inputs(inputs)
    finished = datetime.now(timezone.utc).isoformat(timespec="seconds")
    write_json(previous, dict(status="complete", code_hash=code, inputs=inputs, cache=cache.as_posix(),
                              elapsed_seconds=time.perf_counter()-began, completed_at_utc=finished))
    write_json(ROOT/"acceptance.json", dict(passed=True, code_hash=code, config_hash=digest, input_sha256=inputs,
               outputs=outputs, shells=len(accepted_shells), cases=len(data), households=households,
               carbon_applied=False, census_weighting=False, elapsed_seconds=time.perf_counter()-began,
               completed_at_utc=finished))
    write_json(ROOT/"progress.json", dict(status="complete", completed_layouts=len(data)))
    print(f"Validated HK evidence for {len(data)} layouts and {len(accepted_shells)} shell geometries")


def main():
    parser = prepare_cli(__doc__)
    parser.add_argument("--prepare", action="store_true")
    parser.add_argument("--wait", action="store_true")
    args = parser.parse_args()
    cfg, digest, _ = start_run(args, "11_scenario_hk")
    if args.dry_run:
        print("Use 13 integer size levels, approved catalogue layouts, and two quality-aware S2 kits.")
        return
    ROOT.mkdir(parents=True, exist_ok=True)
    corrected, _ = load_corrected(cfg)
    corpus = pd.read_parquet(Path(cfg["paths"]["processed"])/"corpus_units.parquet",
                             columns=["unit_key", "unit_json"]).set_index("unit_key")
    shells, units = complete_shells(cfg, corrected, corpus)
    frozen = ROOT/"frozen_shells.csv"
    encoded = shells.to_csv(index=False).encode()
    if frozen.exists() and frozen.read_bytes() != encoded:
        raise ValueError("Frozen HK shell definitions differ")
    frozen.write_bytes(encoded)
    if args.prepare:
        print(f"Froze {len(shells)} template attempts, {int(shells.evaluable.sum())} eligible")
        return
    with (ROOT/".run.lock").open("w") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX|fcntl.LOCK_NB)
        write_json(ROOT/"status.json", dict(status="waiting_for_K"))
        try:
            wait_for_kit(args.wait)
            write_json(ROOT/"status.json", dict(status="running"))
            run(cfg, digest, corrected, shells, units)
            write_json(ROOT/"status.json", dict(status="complete"))
        except Exception as error:
            write_json(ROOT/"status.json", dict(status="failed", exception_type=type(error).__name__))
            raise


if __name__ == "__main__":
    main()
