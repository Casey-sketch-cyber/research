"""Scenario adequacy, shape-cluster uncertainty and area-gap outputs."""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from fea.io import write_json
from phase07_statistics import adequate_crossing, interval
from phase09_execution import hash_inputs

ROOT = Path("results/scenario_hk")


def summarize(data, threshold, count, confidence, seed):
    data = data.copy()
    data["adequate"] = data.fciq >= threshold-1e-9
    by_size = data.groupby(["area_m2", "household", "strategy"], as_index=False).agg(
        n_shells=("unit_key", "size"), n_adequate=("adequate", "sum"), adequate_share=("adequate", "mean"),
        mean_fci=("fci", "mean"), mean_fciq=("fciq", "mean"))
    combined = []
    time_effect = []
    rng = np.random.default_rng(seed)
    for household, subset in data.groupby("household", sort=True):
        wide = subset.pivot(index=["unit_key", "area_m2", "shape"], columns="strategy", values="fciq").reset_index()
        if wide.isna().any().any():
            raise ValueError("Scenario strategies have different support")
        a = wide.area_m2.to_numpy()
        categories = [s for s in ("S0", "S1", "S2", "S2_kit") if s in wide]
        y = wide[categories].to_numpy() >= threshold-1e-9
        point = [adequate_crossing(a, y[:, j]) for j in range(len(categories))]
        indices = [g.index.to_numpy() for _, g in wide.groupby("shape", sort=True)]
        boot = np.full((count, len(categories)), np.nan)
        for b in range(count):
            draw = np.concatenate([indices[i] for i in rng.integers(len(indices), size=len(indices))])
            for j in range(len(categories)):
                cross = adequate_crossing(a[draw], y[draw, j])["a_min_m2"]
                if cross is not None:
                    boot[b, j] = cross
        start = point[0]["a_min_m2"]
        for j, strategy in enumerate(categories):
            value = point[j]["a_min_m2"]
            low, high, n_ci, status = interval(boot[:, j], confidence)
            delta = start-value if start is not None and value is not None else None
            dlo, dhi, dn, dstat = interval(boot[:, 0]-boot[:, j], confidence)
            if delta is None:
                dlo, dhi, dstat = None, None, "point_crossing_not_identified"
            if value is None:
                low, high, status = None, None, "point_crossing_not_identified"
            gap = float(np.maximum(0., value-a).mean()) if value is not None else None
            gap_change = float(np.mean(np.maximum(0., start-a)-np.maximum(0., value-a))) if delta is not None else None
            combined.append(dict(household=household, strategy=strategy, n_shells=len(wide),
                                 n_shape_clusters=len(indices), adequate_share=float(y[:, j].mean()),
                                 below_adequacy_share=float((~y[:, j]).mean()), a_min=value, a_min_status=point[j]["status"],
                                 ci_lo=low, ci_hi=high, ci_successful=n_ci, ci_status=status,
                                 delta_a_min_vs_S0_m2=delta, delta_ci_lo=dlo, delta_ci_hi=dhi,
                                 delta_ci_successful=dn, delta_ci_status=dstat, mean_shell_area_gap_m2=gap,
                                 mean_shell_gap_reduction_m2=gap_change, tau=threshold))
        wide["form_effect"] = wide.S1-wide.S0
        wide["time_effect"] = wide.S2-wide.S1
        for area, group in wide.groupby("area_m2", sort=True):
            time_effect.append(dict(household=household, area_m2=area, n_shells=len(group),
                                    mean_form_effect=float(group.form_effect.mean()),
                                    mean_time_effect=float(group.time_effect.mean()),
                                    n_positive_time_effect=int((group.time_effect > 1e-9).sum())))
    return by_size, pd.DataFrame(combined), pd.DataFrame(time_effect)


def figure_f10(by_size, output, threshold):
    households = sorted(by_size.household.unique())
    fig, axes = plt.subplots(1, len(households), figsize=(12, 4.5), sharey=True, layout="constrained")
    styles = {"S0": ("#545454", "o"), "S1": ("#4375a6", "s"), "S2": ("#008477", "^"), "S2_kit": ("#bc5d23", "D")}
    for axis, hh in zip(axes, households):
        subset = by_size[by_size.household == hh]
        for strategy, (color, marker) in styles.items():
            rows = subset[subset.strategy == strategy]
            if len(rows):
                axis.plot(rows.area_m2, rows.adequate_share, color=color, marker=marker, markersize=3, label=strategy)
        axis.set(xlim=(7.7, 20.3), ylim=(-.03, 1.03), xlabel="Shell NIA (m²)", title=hh.split("_")[0])
        axis.set_xticks([8, 10, 12, 14, 16, 18, 20])
        axis.grid(axis="y", alpha=.2)
        axis.legend(loc="lower right", fontsize=8)
    axes[0].set_ylabel(f"Adequate share (FCIq ≥ {threshold:g})")
    fig.suptitle("F10  Hong Kong scenario on equally weighted shell templates", fontsize=12)
    output.parent.mkdir(parents=True, exist_ok=True)
    for extension in ("png", "pdf"):
        fig.savefig(output.with_suffix("."+extension), dpi=220, bbox_inches="tight")
    plt.close(fig)


def export_hk(config, digest, data, shells, elapsed):
    params = config["experiments"]
    options = params["bootstrap"]
    area, pooled, time_effect = summarize(data, params["adequacy_tau"], options["n"], options["ci"], config["seed"])
    census = pd.read_csv("reports/schemas/D6_data.csv")
    total = census[census.dc_eng.str.contains("territory|total", case=False, regex=True, na=False)]
    if len(total) != 1:
        raise ValueError("D6 territory aggregate could not be identified")
    census_out = total[["dc_eng", "sdu_pop", "sdu_dh", "sdu_oq", "sdu_n"]].copy()
    paths = []
    for name, frame in [("cases", data), ("shells", shells), ("adequacy_by_size", area), ("scenario_summary", pooled),
                        ("form_time_effects", time_effect), ("territory_context", census_out)]:
        frame["base_config_hash"] = digest
        target = ROOT/(name+".csv")
        frame.to_csv(target, index=False)
        paths.append(target)
    coverage = ROOT/"coverage.json"
    write_json(coverage, dict(census_weighting=False, household_size_distribution_available=False,
                              floor_area_distribution_available=False, population="territory context and balanced D3 scenarios",
                              carbon_applied=False, carbon_factor_status=config["hk_scenario"]["embodied_carbon_kgco2e_per_m2"]))
    output = Path("results/figures/F10")
    figure_f10(area, output, params["adequacy_tau"])
    cols = ["household", "strategy", "n_shells", "adequate_share", "a_min", "a_min_status",
            "delta_a_min_vs_S0_m2", "delta_ci_lo", "delta_ci_hi", "mean_shell_gap_reduction_m2"]
    report = Path("reports/phase_11_HK_results.md")
    report.write_text("\n".join([
        "# Phase 11 — Hong Kong scenario results", "",
        f"The 13 prescribed size levels from 8 to 20 m² contain {int(shells.evaluable.sum())} eligible shells from "
        f"{len(shells)} generated geometry combinations. The scenario evaluates H1, H3 and H4. "
        f"The solver and evidence checks took {elapsed/3600:.3f} hours in this invocation.", "",
        "## Adequacy and supported area estimates", "",
        pooled[cols].to_markdown(index=False, floatfmt=".5f"), "",
        "Estimates use the prescribed functional-adequacy threshold and the reviewed in-support logistic crossings. "
        "Intervals resample shape templates with all observed sizes and matched strategies together. "
        "The area gap averages the shortfall to the estimated minimum over model shells. "
        "Undefined crossings and gap changes remain empty.", "",
        "The by-size table gives denominators for each 1 m² level. The form/time table reports S1−S0 and S2−S1 "
        "under the catalogue separately. S2_kit uses the quality-aware design for H1 and H3 and independent FCIq checks.", "",
        "## D6 coverage", "",
        census_out[["dc_eng", "sdu_pop", "sdu_dh", "sdu_oq", "sdu_n"]].to_markdown(index=False), "",
        "D6 contains territory and district counts. The missing household-size and floor-area distributions prevent "
        "census-based weights, so the adequacy and floor-area gaps describe the equally weighted shell scenario. "
        "Area is reported in square metres because the carbon factor remains unverified.", "",
        "Reproduce with scripts/11_scenario_hk.py after the accepted reduced K and corrected main experiments.", "",
    ]), encoding="utf-8")
    paths += [coverage, output.with_suffix(".png"), output.with_suffix(".pdf"), report]
    return hash_inputs(paths)
