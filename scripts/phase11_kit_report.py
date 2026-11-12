"""Report matched kit, catalogue, flat-quality and finite-grid bespoke comparisons."""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import numpy as np
import pandas as pd

from fea.config import config_hash
from fea.io import write_json
from phase07_statistics import adequate_crossing
from phase09_execution import hash_inputs
from phase11_kit_design import BED, kit_configuration

ROOT = Path("results/expK")


def comparison(config, confirmed, bespoke):
    chosen = confirmed[(confirmed.condition == "kit") & (confirmed["set"] == "train") & (confirmed.strategy == "S2")]
    candidates = pd.concat([bespoke.assign(set_="train"), chosen], ignore_index=True)
    best = candidates.sort_values(["fciq", "tb", "kit_id"], ascending=[False, True, True])
    best = best.drop_duplicates(["unit_key", "household"]).copy()
    best["condition"], best["set"] = "bespoke", "train"
    check = chosen.merge(best, on=["unit_key", "household"], validate="one_to_one", suffixes=("_kit", "_bespoke"))
    if len(check) != len(chosen) or (check.fciq_bespoke+1e-9 < check.fciq_kit).any():
        raise ValueError("Bespoke comparison omits a feasible confirmed kit")
    data = pd.concat([confirmed, best], ignore_index=True)
    tau = config["experiments"]["adequacy_tau"]
    rows = []
    keys = ["household", "condition", "set", "strategy"]
    for labels, part in data.groupby(keys, sort=True):
        adequate = part.fciq >= tau-1e-9
        cross = adequate_crossing(part.nia_m2, adequate)
        row = dict(zip(keys, labels))
        row.update(n=len(part), fci_mean=float(part.fci.mean()), fciq_mean=float(part.fciq.mean()),
                   adequate_share=float(adequate.mean()), a_min_m2=cross["a_min_m2"], a_min_status=cross["status"])
        for area in (8, 10, 12):
            on_area = np.isclose(part.nia_m2, area, atol=1e-7, rtol=0)
            row[f"n_at_{area}"] = int(on_area.sum())
            row[f"adequacy_share_at_{area}"] = float(adequate[on_area].mean()) if on_area.any() else None
        rows.append(row)
    output = pd.DataFrame(rows).rename(columns={"set": "test_set"})
    cats = output[output.condition == "catalogue"].set_index(["household", "test_set", "strategy"])
    bespoke_mean = output[output.condition == "bespoke"].set_index(["household", "test_set"]).fciq_mean
    output["share_of_bespoke_gain"] = np.nan
    for i, row in output.iterrows():
        cat = cats.loc[(row.household, row.test_set, row.strategy)]
        cat_s0 = cats.loc[(row.household, row.test_set, "S0")]
        output.loc[i, "mean_fciq_gain_vs_catalogue_same_strategy"] = row.fciq_mean-cat.fciq_mean
        output.loc[i, "adequacy_share_gain_vs_catalogue_same_strategy"] = row.adequate_share-cat.adequate_share
        if pd.notna(cat_s0.a_min_m2) and pd.notna(row.a_min_m2):
            output.loc[i, "delta_a_min_vs_catalogue_S0_m2"] = cat_s0.a_min_m2-row.a_min_m2
        if row.strategy == "S2" and row.test_set == "train":
            denominator = bespoke_mean.loc[(row.household, row.test_set)]-cat.fciq_mean
            if denominator > 1e-9:
                output.loc[i, "share_of_bespoke_gain"] = (row.fciq_mean-cat.fciq_mean)/denominator
    effects = []
    for labels, part in confirmed.groupby(["household", "condition", "set"]):
        wide = part.pivot(index="unit_key", columns="strategy", values=["fci", "fciq"])
        effects.append(dict(household=labels[0], condition=labels[1], test_set=labels[2], n=len(wide),
                            form_effect_fci=float((wide.fci.S1-wide.fci.S0).mean()),
                            time_effect_fci=float((wide.fci.S2-wide.fci.S1).mean()),
                            form_effect_fciq=float((wide.fciq.S1-wide.fciq.S0).mean()),
                            time_effect_fciq=float((wide.fciq.S2-wide.fciq.S1).mean())))
    return output, pd.DataFrame(effects), best.drop(columns=["set_"], errors="ignore")


def kit_figure(config, choices, output):
    households = sorted(choices)
    fig, axes = plt.subplots(4, len(households)*2, figsize=(12, 10.5), layout="constrained")
    for j, hh in enumerate(households):
        kit, q = kit_configuration(config, hh, choices[hh]["kit"])
        bed = BED[hh][0]
        names = [bed, "fold_down_desk", "drop_leaf_table", "wardrobe"]
        for i, name in enumerate(names):
            if name == "wardrobe":
                states = [("static", kit["furniture"]["static_items"][name])]
            else:
                states = sorted(kit["furniture"]["transformable_items"][name]["states"].items())
            for k in (0, 1):
                ax = axes[i, j*2+k]
                ax.set_aspect("equal")
                ax.set_xlim(-.35, 1.95)
                ax.set_ylim(-.35, 2.5)
                ax.axis("off")
                if k >= len(states):
                    continue
                state, data = states[k]
                width, depth = data["footprint"]
                ax.add_patch(Rectangle((0, 0), width, depth, facecolor="#deedf2", edgecolor="#1c6d8b", linewidth=1.3))
                ax.annotate("", xy=(width, -.15), xytext=(0, -.15),
                            arrowprops=dict(arrowstyle="<->", color=".25", lw=.8))
                ax.text(width/2, -.27, f"{width:.2f} m", ha="center", va="center", fontsize=8)
                ax.annotate("", xy=(width+.13, depth), xytext=(width+.13, 0),
                            arrowprops=dict(arrowstyle="<->", color=".25", lw=.8))
                ax.text(width+.24, depth/2, f"{depth:.2f} m", rotation=90, va="center", ha="center", fontsize=8)
                label = f"q = {q[name]:.2f}" if name in q else f"{data['storage_units']:.1f} storage units"
                ax.text(width/2, depth/2, label, ha="center", va="center", fontsize=8)
                ax.set_title(hh.split("_")[0]+" "+name.replace("_", " ")+"\n"+state, fontsize=9)
    fig.suptitle("F12  Selected quality-aware kits\nTop-view body dimensions in metres", fontsize=13)
    output.parent.mkdir(parents=True, exist_ok=True)
    for extension in ("png", "pdf"):
        fig.savefig(output.with_suffix("."+extension), dpi=220, bbox_inches="tight")
    plt.close(fig)


def export_results(config, digest, experiment, choices, shells, confirmed, bespoke):
    all_rows = pd.DataFrame(row for records in experiment.rows.values() for row in records)
    if all_rows.duplicated(["task_key", "strategy"]).any() or not all_rows.validator_pass.all():
        raise ValueError("K audit failed")
    if not np.isfinite(all_rows[["fci", "fciq"]]).all().all() or (all_rows.fciq > all_rows.fci+1e-8).any():
        raise ValueError("K FCIq values inconsistent")
    want = len(choices)*len(shells)*9
    if len(confirmed) != want or confirmed.duplicated(["unit_key", "household", "condition", "strategy"]).any():
        raise ValueError("K transfer comparisons incomplete")
    outcomes, effects, best = comparison(config, confirmed, bespoke)
    data = [("cases", all_rows), ("search_log", pd.DataFrame(experiment.search_log)), ("confirmations", confirmed),
            ("comparison", outcomes), ("form_time_effects", effects), ("bespoke_choices", best)]
    paths = []
    for name, frame in data:
        frame["base_config_hash"] = digest
        path = ROOT/(name+".csv")
        frame.to_csv(path, index=False)
        paths.append(path)
    designs = {}
    for household, selected in choices.items():
        designs[household] = {}
        for condition, candidate in selected.items():
            cfg, quality = kit_configuration(config, household, candidate)
            designs[household][condition] = {**candidate, "qualities": quality, "dimension_config_hash": config_hash(cfg)}
    # JSON is a YAML subset and preserves the exact numeric vectors.
    kit = ROOT/"kit.yaml"
    write_json(kit, dict(config_hash=digest, selection="reduced_halving", by_household=designs))
    plot = Path("results/figures/F12")
    kit_figure(config, choices, plot)
    view = outcomes[outcomes.strategy == "S2"]
    fields = ["household", "condition", "test_set", "n", "fciq_mean", "adequate_share",
              "mean_fciq_gain_vs_catalogue_same_strategy", "a_min_m2", "share_of_bespoke_gain"]
    report = Path("reports/phase_11b_K_results.md")
    pilot = pd.read_csv(ROOT/"active_shell_sets.csv")["set"].value_counts().to_dict()
    report.write_text("\n".join([
        "# Phase 11b — Reduced furniture-kit results", "",
        f"Validated {len(all_rows):,} saved layouts. H1 and H3 used eight frozen dimension vectors each. "
        f"The active sets comprise {pilot['train']} training shells, {pilot['heldout']} held-out shells and {pilot['real']} real plans. "
        "All cases use the reviewed small-home time limit and anchor setting. The runtime pilot and its projected time-box checks are archived.", "",
        "## S2 comparison", "", view[fields].to_markdown(index=False, floatfmt=".6f"), "",
        "The quality-aware objective takes minimum reachable service quality and retains the storage capacity cap. "
        "Catalogue service quality is one. Flat-quality search uses ordinary FCI, and its evaluated FCIq uses the selected physical dimensions. "
        "The bespoke result is the best observed candidate per training shell, with the confirmed selected-kit layout available as an incumbent. "
        "Its scope is the frozen eight-vector grid and the recorded search budget.", "",
        "## Separate form and time effects", "", effects.to_markdown(index=False, floatfmt=".6f"), "",
        "Adequate-area crossings are shown where identified within sample support. Rates at 8, 10 and 12 m² include their denominators. "
        "Any decrease versus the catalogue remains in the comparison. The H1 and H3 dimensions and qualities are supplied to the HK solver scenario.", "",
        "Reproduce with scripts/11b_run_expK.py after the accepted Exp. C run.", "",
    ]), encoding="utf-8")
    paths += [kit, plot.with_suffix(".png"), plot.with_suffix(".pdf"), report, ROOT/"active_shell_sets.csv",
              ROOT/"runtime_pilot.csv", ROOT/"runtime_pilot.json", ROOT/"candidate_kits.json", ROOT/"shell_sets.csv"]
    return dict(audited_layouts=len(all_rows), confirmation_layouts=len(confirmed),
                all_layouts_valid=True, bespoke_contains_confirmed_kit=True, outputs=hash_inputs(paths))
