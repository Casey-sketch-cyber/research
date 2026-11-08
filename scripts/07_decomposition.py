"""Round-3 A1: paired form/time effects by household and 2 m² NIA bin."""
import os
for _name in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ[_name] = "1"

import json
from pathlib import Path

import numpy as np
import pandas as pd

from fea.io import prepare_cli, start_run, write_json, sha256_file
from phase07_analysis import load_evaluable_solutions


def paired_effects(solutions: pd.DataFrame) -> pd.DataFrame:
    """Keep all three strategies paired within each unit and household."""
    keys = ["unit_key", "household"]
    if solutions.duplicated(keys+["strategy"]).any() or not solutions.validator_pass.all():
        raise ValueError("Decomposition needs unique independently valid case records")
    if set(solutions.strategy) != {"S0", "S1", "S2"}:
        raise ValueError("All three strategies are required")
    if solutions.groupby(keys)[["source", "nia_m2"]].nunique().gt(1).any().any():
        raise ValueError("Strategy metadata differs within a pair")
    wide = solutions.pivot(index=keys, columns="strategy", values="fci_validator")
    if not np.isfinite(wide.to_numpy()).all():
        raise ValueError("A paired strategy is absent or nonfinite")
    if ((wide.S1 < wide.S0-1e-8) | (wide.S2 < wide.S1-1e-8)).any():
        raise ValueError("Strategy ordering failed; do not hide it in decomposition")
    metadata = solutions.drop_duplicates(keys).set_index(keys)[["source", "nia_m2"]]
    result = wide.join(metadata).reset_index()
    result["form_effect"] = result.S1-result.S0
    result["time_effect"] = result.S2-result.S1
    result["total_effect"] = result.S2-result.S0
    result["time_gain"] = result.time_effect > 1e-9
    result["area_bin_lo"] = np.floor((result.nia_m2+1e-8)/2)*2
    result["area_bin_hi"] = result.area_bin_lo+2
    assert np.allclose(result.form_effect+result.time_effect, result.total_effect, atol=1e-12)
    return result.sort_values(keys).reset_index(drop=True)


def summarize(effects: pd.DataFrame, n_bootstrap: int, confidence: float, seed: int) -> pd.DataFrame:
    """Resample complete unit effect vectors, preserving paired-strategy covariance."""
    if n_bootstrap < 1 or not 0 < confidence < 1:
        raise ValueError("Invalid bootstrap settings")
    rng = np.random.default_rng(seed)
    rows = []
    for pooling in ["pooled", "real_plans"]+sorted(effects.source.unique()):
        frame = effects if pooling == "pooled" else effects[effects.source.isin(["D1", "D2"])] if pooling == "real_plans" else effects[effects.source == pooling]
        for (household, lo), group in frame.groupby(["household", "area_bin_lo"], sort=True):
            group = group.sort_values("unit_key")
            assert not group.unit_key.duplicated().any()
            columns = ["form_effect", "time_effect", "total_effect", "time_gain"]
            values = group[columns].to_numpy(float)
            row = dict(pooling=pooling, household=household, area_bin_lo=lo, area_bin_hi=lo+2,
                n_units=len(group), positive_time_units=int(group.time_gain.sum()),
                ci_status="percentile_unit_bootstrap" if len(group) >= 2 else "insufficient_units",
                bootstrap_resamples=n_bootstrap if len(group) >= 2 else 0)
            draws = None
            if len(group) >= 2:
                draws = np.array([values[rng.integers(0, len(group), size=len(group))].mean(axis=0)
                                  for _ in range(n_bootstrap)])
            for i, name in enumerate(columns):
                label = "share_S2_gt_S1" if name == "time_gain" else "mean_"+name
                row[label] = float(values[:, i].mean())
                interval = np.quantile(draws[:, i], [(1-confidence)/2, (1+confidence)/2]) if draws is not None else [None, None]
                row[label+"_ci_lo"], row[label+"_ci_hi"] = interval
            rows.append(row)
    return pd.DataFrame(rows)


def render_f4b(summary: pd.DataFrame, output: Path) -> None:
    """Draw stacked effects; bars above stacks use the joint total-effect interval."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    frame = summary[summary.pooling.isin(["pooled", "real_plans", "D3"])]
    households = sorted(frame.household.unique())
    panels = [("pooled", "Pooled"), ("real_plans", "Real plans: D1+D2"), ("D3", "Designed shells: D3")]
    fig, axes = plt.subplots(len(households), len(panels), figsize=(16, 3.3*len(households)), sharex=True, sharey=True, squeeze=False)
    for index, ax in enumerate(axes.flat):
        household = households[index//len(panels)]
        pooling, title = panels[index % len(panels)]
        data = frame[(frame.household == household) & (frame.pooling == pooling)].sort_values("area_bin_lo")
        x = data.area_bin_lo+1
        ax.bar(x, data.mean_form_effect, width=1.7, color="#286c91", label="Form: S1 − S0")
        ax.bar(x, data.mean_time_effect, bottom=data.mean_form_effect, width=1.7, color="#e49b32", label="Time: S2 − S1")
        for effect in ("form", "total"):
            name = "mean_"+effect+"_effect"
            valid = data[name+"_ci_lo"].notna()
            # Plot quantile endpoints directly: a percentile interval need not contain the point estimate.
            ax.vlines(x[valid], data.loc[valid, name+"_ci_lo"], data.loc[valid, name+"_ci_hi"], color="#222222", lw=.7)
        ax.set_title(title+"\n"+household.replace("_", " "), fontsize=9)
        ax.set_xlabel("Net internal area (m²); 2 m² bins")
        ax.set_ylabel("Mean FCI gain")
        ax.grid(axis="y", alpha=.2)
        ax.set_axisbelow(True)
    top = float(np.nanmax(frame[["mean_total_effect", "mean_total_effect_ci_hi", "mean_form_effect_ci_hi"]].to_numpy(float)))
    axes.flat[0].set_ylim(0, max(.05, top)*1.08)
    handles, labels = axes.flat[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="upper center", bbox_to_anchor=(.5, .98), ncol=2, frameon=False)
    fig.suptitle("Form and time effects by household", y=.995)
    fig.tight_layout(rect=(0, 0, 1, .955))
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output.with_suffix(".png"), dpi=300, bbox_inches="tight")
    fig.savefig(output.with_suffix(".pdf"), bbox_inches="tight")
    plt.close(fig)


def main():
    args = prepare_cli(__doc__).parse_args()
    config, _, _ = start_run(args, "07_decomposition")
    if args.dry_run:
        print("Would require complete, accepted Exp. A cases and generate paired effects and F4b.")
        return
    root = Path("results/expA")
    path = root/"solutions.csv"
    solutions, analysis_acceptance = load_evaluable_solutions(config, root)
    effects = paired_effects(solutions)
    options = config["experiments"]["bootstrap"]
    summary = summarize(effects, options["n"], options["ci"], config["seed"])
    effects.to_csv(root/"form_time_effects.csv", index=False)
    summary.to_csv(root/"form_time_by_area.csv", index=False)
    render_f4b(summary, Path("results/figures/F4b"))
    write_json(root/"decomposition_manifest.json", dict(source_sha256=sha256_file(path),
        analysis_acceptance_sha256=sha256_file(root/"analysis_acceptance.json"),
        evaluability_sha256=analysis_acceptance["evaluability_sha256"],
        units=int(effects.unit_key.nunique()), paired_cases=len(effects), seed=config["seed"],
        bootstrap_resamples=options["n"], confidence=options["ci"], resampling_unit="unit within household and NIA bin",
        bin_rule="[lo,lo+2); 1e-8 m² tolerance for raster serialization at bin boundaries",
        figure_intervals="paired bootstrap intervals for form and total; time-effect intervals are in the CSV",
        limitations="Pilot squeeze band is exploratory. Single-unit bins have no interval. Pooled source mix and deterministic D3 design coverage limit population generalization."))


if __name__ == "__main__":
    main()
