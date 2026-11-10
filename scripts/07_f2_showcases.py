"""Revalidate and render the same 33 examples using corrected F1 evidence."""
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
from phase07_corrected import load_corrected


def main():
    args = prepare_cli(__doc__).parse_args()
    config, _, _ = start_run(args, "07_f2_showcases")
    if args.dry_run:
        print("Would revalidate and render the same original 33 examples using corrected F1 outcomes and actual H1/H2 provenance.")
        return
    root = Path("results/expA_f1/analysis")
    solutions, acceptance = load_corrected(config)
    run = json.loads(Path("results/expA_f1/run.json").read_text())
    original_run = json.loads(Path("results/expA/run.json").read_text())
    original_config = json.loads(Path("results/expA_f1/original_config_snapshot.json").read_text())
    frozen = pd.read_csv("results/expA/layout_selection.csv")
    keys = ["unit_key", "household", "strategy"]
    selection = frozen[keys+["purpose", "target_nia_m2"]].merge(solutions, on=keys, how="left", validate="many_to_one")
    if len(selection) != 33 or selection.fci_validator.isna().any():
        raise ValueError("The original 33 example cases must remain available")
    selection[["unit_key", "source", "nia_m2", "household", "strategy", "purpose", "target_nia_m2"]].to_csv(root/"layout_selection.csv", index=False)
    corpus = pd.read_parquet(Path(config["paths"]["processed"])/"corpus_units.parquet",
        columns=["unit_key", "unit_json"]).set_index("unit_key")
    households = parse_households(config["households"], config["furniture"])
    evidence = []
    for _, row in tqdm(selection.iterrows(), total=len(selection), desc="A example layouts"):
        reused = row.result_origin == "original_A_H1H2_verified_unaffected"
        selected_run = original_run if reused else run
        selected_config = original_config if reused else config
        layout_path = Path(selected_run["cache"])/row.budget_group/"shared"/row.layout_file
        layout = json.loads(layout_path.read_text())
        unit = Unit.from_dict(json.loads(corpus.loc[row.unit_key, "unit_json"]))
        settings = run["production_settings"][row.budget_group]
        local_config = deepcopy(selected_config)
        local_config["solver"].update(num_workers=settings["num_workers"], time_limit_s=settings["time_limit_s"])
        local_config["raster"]["anchor_stride_m"] = settings["anchor_stride_m"]
        if config_hash(local_config) != row.config_hash or layout["config_hash"] != row.config_hash:
            raise ValueError("Saved layout configuration mismatch")
        grid = rasterize(unit, config["raster"]["resolution_m"], config["furniture"]["meta"]["walking_width"], config["raster"]["source_gap_close_m"])
        checked = validate_layout(layout, grid, local_config, households[row.household])
        if not checked["pass"] or abs(checked["fci"]-row.fci_validator) > 1e-8:
            raise ValueError("Saved example failed independent revalidation")
        destination = root/"layouts"/row.purpose
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
        audit_sha256=sha256_file(root/"layout_audit.csv"), evaluability_sha256=acceptance["input_provenance"]["evaluability_sha256"],
        selection_rule="Exact original 33 example cases; original fixed-seed and geometry-only selection retained; corrected H3/H4 outcomes and unchanged H1/H2 provenance",
        F1_solutions_sha256=acceptance["combined_sha256"], original_selection_sha256=sha256_file(Path("results/expA/layout_selection.csv")),
        visual_review_pending=True))
    print(json.dumps(dict(rendered=len(evidence), all_revalidated=True)))


if __name__ == "__main__":
    main()
