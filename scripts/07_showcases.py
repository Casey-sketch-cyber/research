"""Render fixed-seed accepted A examples and geometry-selected 10/18/30 m² H3 showcases."""
from copy import deepcopy
import json
from pathlib import Path

import numpy as np
import pandas as pd
from tqdm import tqdm

from fea.config import config_hash
from fea.geometry.raster import rasterize
from fea.geometry.unit import Unit
from fea.households import parse_households
from fea.io import prepare_cli, sha256_file, start_run, write_json
from fea.validate import validate_layout
from fea.viz.layouts import render_layout
from phase07_analysis import load_evaluable_solutions


def main():
    args = prepare_cli(__doc__).parse_args()
    config, _, _ = start_run(args, "07_showcases")
    if args.dry_run:
        print("Would select 24 cases by seed and 3 H3 unit triplets by NIA alone; revalidate saved layouts and render them.")
        return
    root = Path("results/expA")
    solutions, acceptance = load_evaluable_solutions(config, root)
    solutions = solutions.sort_values(["unit_key", "household", "strategy"])
    run = json.loads((root/"run.json").read_text())
    rng = np.random.default_rng(config["seed"])
    random_cases = solutions.iloc[rng.choice(len(solutions), 24, replace=False)].copy()
    random_cases["purpose"] = "sample"
    random_cases["target_nia_m2"] = np.nan
    units = solutions.drop_duplicates("unit_key").sort_values("unit_key")
    showcase = []
    for target in (10., 18., 30.):
        distance = abs(units.nia_m2-target)
        candidates = units[distance <= distance.min()+1e-6]
        key = candidates.iloc[int(rng.integers(0, len(candidates)))].unit_key
        selected = solutions[(solutions.unit_key == key) & (solutions.household == "H3_couple_one_remote")].copy()
        selected["purpose"], selected["target_nia_m2"] = "showcase", target
        showcase.append(selected)
    selection = pd.concat([random_cases, *showcase], ignore_index=True)
    selection[["unit_key", "source", "nia_m2", "household", "strategy", "purpose", "target_nia_m2"]].to_csv(
        root/"layout_selection.csv", index=False)
    corpus = pd.read_parquet(Path(config["paths"]["processed"])/"corpus_units.parquet",
        columns=["unit_key", "unit_json"]).set_index("unit_key")
    households = parse_households(config["households"], config["furniture"])
    evidence = []
    for _, row in tqdm(selection.iterrows(), total=len(selection), desc="A example layouts"):
        layout_path = Path(run["cache"])/row.budget_group/"shared"/row.layout_file
        layout = json.loads(layout_path.read_text())
        unit = Unit.from_dict(json.loads(corpus.loc[row.unit_key, "unit_json"]))
        settings = run["production_settings"][row.budget_group]
        local_config = deepcopy(config)
        local_config["solver"].update(num_workers=settings["num_workers"], time_limit_s=settings["time_limit_s"])
        local_config["raster"]["anchor_stride_m"] = settings["anchor_stride_m"]
        if config_hash(local_config) != row.config_hash or layout["config_hash"] != row.config_hash:
            raise ValueError("Saved layout configuration mismatch")
        grid = rasterize(unit, config["raster"]["resolution_m"], config["furniture"]["meta"]["walking_width"], config["raster"]["source_gap_close_m"])
        checked = validate_layout(layout, grid, local_config, households[row.household])
        if not checked["pass"] or abs(checked["fci"]-row.fci_validator) > 1e-8:
            raise ValueError("Saved example failed independent revalidation")
        destination = Path("results/layouts")/row.purpose
        destination.mkdir(parents=True, exist_ok=True)
        stem = row.unit_key.replace(":", "_")+"_"+row.household.split("_")[0]+"_"+row.strategy
        write_json(destination/(stem+".json"), layout)
        write_json(destination/(row.unit_key.replace(":", "_")+"_unit.json"), unit.to_dict())
        for extension in ("png", "pdf"):
            render_layout(unit, layout, local_config, households[row.household], destination/(stem+"."+extension), grid)
        evidence.append(dict(unit_key=row.unit_key, household=row.household, strategy=row.strategy, purpose=row.purpose,
            validator_pass=checked["pass"], fci_validator=checked["fci"],
            layout_sha256=sha256_file(destination/(stem+".json")), png_sha256=sha256_file(destination/(stem+".png")),
            pdf_sha256=sha256_file(destination/(stem+".pdf")), file_stem=(destination/stem).as_posix()))
        write_json(root/"layout_progress.json", dict(completed=len(evidence), expected=len(selection)))
    pd.DataFrame(evidence).to_csv(root/"layout_audit.csv", index=False)
    write_json(root/"layout_manifest.json", dict(seed=config["seed"], sample_cases=24, showcase_cases=9,
        all_revalidated=True, selection_sha256=sha256_file(root/"layout_selection.csv"),
        audit_sha256=sha256_file(root/"layout_audit.csv"), evaluability_sha256=acceptance["evaluability_sha256"],
        selection_rule="random cases from evaluable units; H3 showcases nearest target NIA with seeded ties; no score selection",
        visual_review_pending=True))
    print(json.dumps(dict(rendered=len(evidence), all_revalidated=True)))


if __name__ == "__main__":
    main()
