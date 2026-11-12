"""Summarize completed ablations using the reviewed support-aware area definitions."""
from datetime import datetime, timezone
from pathlib import Path
import time

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from fea.io import prepare_cli, sha256_file, start_run, write_json
from phase07_corrected import load_corrected
from phase07_p1_area import fit_reference, gain_summary, paired_gain
from phase07_statistics import adequate_crossing
from phase09_execution import checked_inputs, hash_inputs, load_json

ROOT = Path("results/ablations")


def score_pairs(frame):
    scores = frame.pivot(index=["unit_key", "source", "nia_m2"], columns="strategy", values="fci_validator")
    return scores.sort_index().reset_index()


def describe(scores, curve, threshold):
    gain = gain_summary(paired_gain(curve, scores.S0.to_numpy(), scores.S2.to_numpy()))
    s0 = adequate_crossing(scores.nia_m2, scores.S0 >= threshold-1e-9)
    s2 = adequate_crossing(scores.nia_m2, scores.S2 >= threshold-1e-9)
    a0, a2 = s0["a_min_m2"], s2["a_min_m2"]
    return dict(n=len(scores), median_fci_S2=float(scores.S2.median()),
                mean_fci_S2=float(scores.S2.mean()), mean_form_effect=float((scores.S1-scores.S0).mean()),
                mean_time_effect=float((scores.S2-scores.S1).mean()), median_saving_m2=gain["median_delta_ea_identified_positive_m2"],
                n_identified_positive=gain["n_identified_positive_gains"], n_area_bounds=gain["n_lower_bound_among_fci_improved"],
                median_lower_bound_m2=gain["median_among_fci_improved_lower_bound_m2"],
                adequate_S0=float((scores.S0 >= threshold-1e-9).mean()),
                adequate_S2=float((scores.S2 >= threshold-1e-9).mean()),
                a_min_S0_m2=a0, a_min_S2_m2=a2, a_min_S0_status=s0["status"], a_min_S2_status=s2["status"],
                delta_a_min_m2=a0-a2 if a0 is not None and a2 is not None else None)


def difference(left, right):
    return left-right if left is not None and right is not None else None


def summary_tables(config, frame, corrected):
    tau = config["experiments"]["adequacy_tau"]
    controls = frame[frame.ablation == "production"]
    refs = {hh: fit_reference(group.nia_m2, group.fci_validator)
            for hh, group in corrected[corrected.strategy == "S0"].groupby("household")}
    rows = []
    keys = ["sample", "ablation", "value", "household"]
    for (sample, ablation, value, hh), group in frame.groupby(keys, sort=True):
        pairs = score_pairs(group)
        curve = refs[hh] if hh in refs else fit_reference(pairs.nia_m2, pairs.S0)
        row = describe(pairs, curve, tau)
        row.update(dict(zip(keys, (sample, ablation, value, hh))), tau=tau,
                   structural_unreachable_layouts=int(group.structural_unreachable.sum()),
                   exact_or_saturated_own_layouts=int((group.own_origin != "fresh_solve").sum()))
        if sample != "B_units":
            compare = score_pairs(controls[(controls["sample"] == sample) & (controls.household == hh)])
            paired = pairs.merge(compare, on=["unit_key", "source", "nia_m2"], validate="one_to_one", suffixes=("", "_control"))
            if len(paired) != len(pairs) or len(paired) != len(compare):
                raise ValueError("Matched control membership differs")
            base = describe(compare, curve, tau)
            row.update(change_median_saving_m2=difference(row["median_saving_m2"], base["median_saving_m2"]),
                       change_delta_a_min_m2=difference(row["delta_a_min_m2"], base["delta_a_min_m2"]),
                       paired_mean_fci_S2_change=float((paired.S2-paired.S2_control).mean()),
                       n_unchanged_s2=int(np.isclose(paired.S2, paired.S2_control, atol=1e-9, rtol=0).sum()),
                       paired_mean_time_effect_change=float(((paired.S2-paired.S1)-(paired.S2_control-paired.S1_control)).mean()))
        rows.append(row)
    summary = pd.DataFrame(rows)
    tau_rows = []
    for pooling, data in [("pooled", corrected), ("real_plans", corrected[corrected.source != "D3"]), ("D3", corrected[corrected.source == "D3"])]:
        for hh, group in data.groupby("household"):
            pairs = score_pairs(group)
            for threshold in config["experiments"]["tau_sensitivity"]:
                tau_rows.append(dict(pooling=pooling, household=hh, tau=threshold, **describe(pairs, refs[hh], threshold)))
    return summary, pd.DataFrame(tau_rows)


def f9(summary, output):
    controls = {"clearance_scale": "1.0", "walking_width": "0.6", "resolution_m": "0.1"}
    plot = summary[~summary.ablation.isin(["production", "household"])].copy()
    plot = plot[~plot.apply(lambda r: controls.get(r.ablation) == r.value, axis=1)]
    labels = {"drop_one": "Remove", "clearance_scale": "Clearance", "walking_width": "Walk (m)",
              "resolution_m": "Grid (m)", "time_limit_s": "Limit (s)"}
    plot["condition"] = [labels[k]+" "+str(v).replace("_", " ") for k, v in zip(plot.ablation, plot.value)]
    households = sorted(plot.household.unique())
    fig, axes = plt.subplots(2, len(households), figsize=(15, 9), sharey=True, layout="constrained")
    conditions = sorted(plot.condition.unique())
    for j, hh in enumerate(households):
        rows = plot[plot.household == hh].set_index("condition").reindex(conditions)
        for i, (key, xlabel) in enumerate([
            ("change_median_saving_m2", "Change in median gain (m²)"),
            ("change_delta_a_min_m2", "Change in ΔAmin (m²)"),
        ]):
            ax = axes[i, j]
            y = np.arange(len(conditions))
            values = rows[key].to_numpy(float)
            finite = np.isfinite(values)
            ax.axvline(0, color="0.5", lw=.8)
            ax.barh(y[finite], values[finite], color=np.where(values[finite]>=0, "#16739d", "#c76539"))
            ax.scatter(np.zeros((~finite).sum()), y[~finite], marker="x", color="0.55", s=14)
            ax.set_yticks(y, conditions, fontsize=8)
            ax.set_title(hh.split("_")[0], fontsize=11)
            ax.set_xlabel(xlabel, fontsize=9)
            ax.grid(axis="x", alpha=.18)
    fig.suptitle("F9  Ablations versus matched production control\n× indicates an unidentified area contrast", fontsize=13)
    output.parent.mkdir(parents=True, exist_ok=True)
    for ext in ("png", "pdf"):
        fig.savefig(output.with_suffix("."+ext), dpi=200, bbox_inches="tight")
    plt.close(fig)


def summarize(config, digest):
    run, gate = load_json(ROOT/"run.json"), load_json(ROOT/"acceptance.json")
    if run["status"] != "complete" or not gate["passed"] or gate["cases_sha256"] != sha256_file(ROOT/"cases.csv"):
        raise ValueError("Ablation run is not accepted")
    checked_inputs(run["inputs"])
    corrected, _ = load_corrected(config)
    frame = pd.read_csv(ROOT/"cases.csv", dtype={"value": str})
    summary, tau = summary_tables(config, frame, corrected)
    summary["config_hash"], tau["config_hash"] = digest, digest
    summary_path, tau_path = ROOT/"summary.csv", ROOT/"tau_sensitivity.csv"
    summary.to_csv(summary_path, index=False)
    tau.to_csv(tau_path, index=False)
    plot_path = Path("results/figures/F9")
    f9(summary, plot_path)
    effect = summary[~summary.ablation.isin(["production", "household"])].copy()
    effect["abs_change"] = effect.paired_mean_fci_S2_change.abs()
    top = effect.nlargest(12, "abs_change")[["household", "ablation", "value", "n", "paired_mean_fci_S2_change",
                                             "change_median_saving_m2", "change_delta_a_min_m2", "structural_unreachable_layouts"]]
    report = Path("reports/phase_09_ablation_results.md")
    report.write_text("\n".join([
        "# Phase 9 — Completed ablations", "",
        f"Audited {gate['layouts']:,} layouts in {gate['triplets']:,} three-strategy triplets. "
        f"The full invocation took {run['wall_time_this_invocation_s']/3600:.3f} hours. "
        f"Exact accepted and saturated layouts are traced in the case table. "
        f"Structurally unreachable empty-shell results: {gate['structurally_unreachable']:,}. "
        "They retain zero validator score and an explicit structural status.", "",
        "Resolution and time-limit conditions share the fixed 50-unit sample. Item removal, walking width and clearance use the B pairs. H5 and all main households are also tabulated on the same distinct B units. F3 remains the accepted mirrored-access result on its separately defined small-home cohort.", "",
        "## Largest matched differences in mean S2 FCI", "", top.to_markdown(index=False, floatfmt=".6f"), "",
        "Positive and negative results are retained. The pooled static curve from corrected main evidence is held fixed per household. Area summaries use identified positive gains and state support-limited counts separately. The median contrast compares the observed identified subsets. Adequate-area differences require two supported crossings. Both finite solver budgets and structural feasibility can contribute to observed differences.", "",
        "## Reproduction", "",
        "Run scripts/09_run_ablations.py, then scripts/09_report_ablations.py. F9 and the threshold sensitivity table are produced from the accepted cases and frozen corrected main scores.", "",
    ]), encoding="utf-8")
    write_json(ROOT/"report_acceptance.json", dict(
        passed=True, numerical_checks_passed=True, config_hash=digest, layouts=gate["layouts"],
        input_sha256=hash_inputs([ROOT/"acceptance.json", ROOT/"run.json", "scripts/09_report_ablations.py"]),
        outputs=hash_inputs([summary_path, tau_path, report, plot_path.with_suffix(".png"), plot_path.with_suffix(".pdf")]),
        completed_at_utc=datetime.now(timezone.utc).isoformat(timespec="seconds"),
    ))
    print(f"Summarized {len(summary)} sensitivity rows and {len(tau)} threshold rows")


def main():
    parser = prepare_cli(__doc__)
    parser.add_argument("--wait", action="store_true")
    args = parser.parse_args()
    cfg, digest, _ = start_run(args, "09_report_ablations")
    if args.dry_run:
        print("Would summarize accepted ablation layouts and generate F9")
        return
    if args.wait:
        while not (ROOT/"acceptance.json").exists() or load_json(ROOT/"run.json")["status"] != "complete":
            state = Path(".tmp/g3_ablations_pipeline.json")
            if state.exists() and load_json(state)["status"] == "failed":
                raise ValueError("Ablation execution failed")
            time.sleep(30)
    summarize(cfg, digest)


if __name__ == "__main__":
    main()
