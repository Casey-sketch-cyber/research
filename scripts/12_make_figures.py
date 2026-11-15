"""Build the G4 figures from the accepted experiment files."""

import argparse
import json
import time
from datetime import datetime, timezone
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import yaml
from matplotlib.lines import Line2D
from matplotlib.patches import FancyBboxPatch, Patch, Polygon, Rectangle
from matplotlib.ticker import PercentFormatter
from PIL import Image
from shapely.geometry import MultiPoint

from fea.config import load_config
from fea.furniture.library import library, rectangles
from fea.geometry.unit import Unit
from fea.households import parse_households
from fea.io import sha256_file
from phase12_artifacts import write_manifest
from fea.viz.corpus import COLORS as PLAN_COLORS, draw_unit
from phase09_execution import apply_production
from phase11_kit_design import BED, kit_configuration


RESULTS = Path("results")
OUTPUT = RESULTS / "figures/g4"
A = RESULTS / "expA_f1"
P1 = A / "analysis_p1"
K = RESULTS / "g3_review_k3"
HK = RESULTS / "g3_review/hong_kong"
R = RESULTS / "expR"
RENDERS = RESULTS / "renders3d"
CONFIG = Path("config/project.yaml")
COLORS = ("#0072B2", "#E69F00", "#009E73", "#CC79A7", "#D55E00")
INK, MUTED, GRID = "#203048", "#536278", "#DCE4ED"
SPARSE = "#81858E"
STRATEGIES = dict(zip(("S0", "S1", "S2"), COLORS))
RENDER_CONFIG = Path("config/render.yaml")
FUNCTIONS = yaml.safe_load(RENDER_CONFIG.read_text(encoding="utf-8"))["palette"]
HOUSEHOLDS = {
    "H1_single_commuter": "H1 · Single commuter",
    "H2_single_remote_worker": "H2 · Single remote worker",
    "H3_couple_one_remote": "H3 · Couple, one remote worker",
    "H4_parent_child": "H4 · Parent and child",
}
SLOT_LABELS = {"night": "Night", "day": "Workday", "dinner": "Dinner"}
UNITS = {"real_plans": "Observed plans (D1 + D2)", "D3": "Generated shells (D3)"}
INPUTS = {CONFIG, RENDER_CONFIG, Path("config/furniture.yaml"), Path("config/households.yaml"), Path("scripts/12_make_figures.py"), Path("config/downloads.yaml"),
          Path("scripts/phase09_execution.py"), Path("scripts/phase11_kit_design.py"),
          Path("scripts/phase12_artifacts.py")}


def csv(path, **kwargs):
    INPUTS.add(path)
    return pd.read_csv(path, **kwargs)


def document(path):
    INPUTS.add(path)
    return json.loads(path.read_text(encoding="utf-8"))


def start_style():
    plt.rcParams.update({
        "font.family": "DejaVu Sans", "font.size": 9, "text.color": INK,
        "axes.labelcolor": INK, "axes.edgecolor": GRID, "axes.spines.top": False,
        "axes.spines.right": False, "xtick.color": MUTED, "ytick.color": MUTED,
        "axes.titleweight": "bold", "axes.titlesize": 10, "legend.frameon": False,
        "figure.facecolor": "white", "axes.facecolor": "white", "pdf.fonttype": 42,
    })


def figure(fig, label, title, subtitle):
    fig.suptitle(f"{label}  {title}", fontsize=17, fontweight="bold", ha="left", x=.055, y=.982)
    fig.text(.055, .981 - .32/fig.get_figheight(), subtitle, fontsize=9, color=MUTED, ha="left", va="top")


def export(fig, name):
    OUTPUT.mkdir(parents=True, exist_ok=True)
    stem = OUTPUT / name
    with_metadata = {"CreationDate": datetime.now(timezone.utc), "Title": name}
    fig.savefig(stem.with_suffix(".pdf"), dpi=300, metadata=with_metadata)
    fig.savefig(stem.with_suffix(".png"), dpi=300)
    plt.close(fig)
    return [stem.with_suffix(".pdf"), stem.with_suffix(".png")]


def grid(ax):
    ax.set_axisbelow(True)
    ax.grid(axis="y", color=GRID, linewidth=.7)


def legend(fig, handles, ncol, y=.879):
    fig.legend(handles=handles, loc="upper center", bbox_to_anchor=(.5, y), ncol=ncol,
               borderaxespad=0, fontsize=8)


def strategy_legend():
    return [Line2D([], [], color=color, lw=2, label=f"{name} · {label}")
            for (name, color), label in zip(STRATEGIES.items(), ("Static", "Form only", "Form + time"))]


def binned_area(values):
    return 2 * np.floor((values + 1e-8) / 2)


def f1():
    for path in (CONFIG, Path("docs/RESEARCH_PLAN.md"), Path("src/fea/validate.py")):
        INPUTS.add(path)
    fig, ax = plt.subplots(figsize=(11, 4.2))
    figure(fig, "F1", "Measuring how much dwelling function fits",
           "Matched layouts keep the shell and household fixed while the furniture strategy changes.")
    ax.set(xlim=(0, 11), ylim=(0, 3.35))
    ax.axis("off")
    specs = [
        (.18, 2.15, "Dwelling", "Normalized shell, openings\nand walkable space", COLORS[0]),
        (.18, 1.16, "Household", "Activity demand, duration\nand day variants", COLORS[0]),
        (.18, .17, "Furniture", "Bodies, clearance, storage\nand allowed states", COLORS[0]),
        (3.02, 2.15, "S0 · Static", "Catalogue of static pieces", COLORS[0]),
        (3.02, 1.16, "S1 · Form", "Transformable, one state", COLORS[1]),
        (3.02, .17, "S2 · Form and time", "States can change by slot", COLORS[2]),
        (5.85, 1.63, "Solve and validate", "Search with CP-SAT.\nRecheck geometry and service.", INK),
        (5.85, .54, "Score accepted layout", "Function coverage (FCI)\nand transformation burden (TB)", INK),
        (8.68, 1.63, "Equivalent area", "Map paired scores to a\ncommon static area curve.", COLORS[4]),
        (8.68, .54, "Adequate area", "Estimate the area crossing\nat a common FCI threshold.", COLORS[4]),
    ]
    for x, y, title, label, color in specs:
        ax.add_patch(FancyBboxPatch((x, y), 2.15, .76, boxstyle="round,pad=.06",
                                   facecolor="#F1F5F9", edgecolor=color, linewidth=1.1))
        ax.text(x+.12, y+.58, title, color=color, fontsize=10, fontweight="bold", va="center")
        ax.text(x+.12, y+.33, label, fontsize=8.2, va="top", linespacing=1.17)
    ax.plot([2.69]*2, [.55, 2.53], color=MUTED, lw=1.05)
    for y in (.55, 1.54, 2.53):
        ax.plot([2.40, 2.69], [y, y], color=MUTED, lw=1.05)
        ax.annotate("", (2.92, y), (2.69, y), arrowprops={"arrowstyle": "->", "color": MUTED})
    for src, dst in [((5.27, y), (5.74, 2.01)) for y in (.55, 1.54, 2.53)]:
        ax.annotate("", dst, src, arrowprops={"arrowstyle": "->", "color": MUTED})
    for src, dst in [((6.92, 1.55), (6.92, 1.38)), ((8.12, .93), (8.58, .93)),
                     ((8.12, 1.04), (8.58, 1.93))]:
        ax.annotate("", dst, src, arrowprops={"arrowstyle": "->", "color": MUTED})
    fig.subplots_adjust(top=.83, left=.038, right=.973, bottom=.057)
    return export(fig, "F1")


def f2():
    sample = csv(A / "sample.csv")
    examples = document(RESULTS / "corpus/sample_units.json")["units"]
    fig = plt.figure(figsize=(10, 7.6))
    figure(fig, "F2", "Net internal area in the evaluable sample",
           "Observed plans supply the larger comparison units. Generated shells extend coverage down to 8 m².")
    gs = fig.add_gridspec(2, 3, height_ratios=(1.25, 1), hspace=.48, wspace=.33)
    ax = fig.add_subplot(gs[0, :])
    grid(ax)
    names = {"D1": "Swiss Dwellings", "D2": "ResPlan", "D3": "Generated shells"}
    for (code, source), color in zip(sample.groupby("source"), COLORS):
        ax.hist(source.nia_m2, bins=np.arange(8, 52, 2), histtype="step", linewidth=2.1,
                color=color, label=f"{code} · {names[code]}  (n={len(source):,})")
    ax.set(xlabel="Net internal area (m²)", ylabel="Units per 2 m² bin", xlim=(7.7, 50.2))
    ax.legend(ncol=3, loc="upper left")
    eligible = set(sample.unit_key)
    for i, code in enumerate(names):
        plan = next(v for v in examples if v["source"] == code and v["unit_key"] in eligible)
        ax = fig.add_subplot(gs[1, i])
        unit = Unit.from_dict(plan)
        draw_unit(ax, unit, short=True)
        ax.set_title(f"{code} · Example, {unit.interior.area:.1f} m²")
        ax.set_xlabel("Local position (m)")
        ax.set_ylabel("Local position (m)" if i == 0 else "")
        ax.locator_params(nbins=4)
    legend(fig, [Patch(facecolor=k, label=s.replace("_", " ").title()) for s, k in PLAN_COLORS.items()] + [
        Line2D([], [], color="#bf2441", label="Entrance"),
        Line2D([], [], color="#167dcc", label="Window"),
    ], 7, y=.029)
    fig.subplots_adjust(top=.865, bottom=.125, left=.09, right=.965)
    return export(fig, "F2")


def accepted_showcases():
    rows = csv(A / "analysis/layout_selection.csv").query("purpose == 'showcase'")
    audit = csv(A / "analysis/layout_audit.csv").set_index(["unit_key", "household", "strategy"])
    for area, group in rows.groupby("target_nia_m2"):
        entry = group.iloc[0]
        prefix = A / "analysis/layouts/showcase" / (entry.unit_key.replace(":", "_") + "_unit.json")
        units = {}
        for row in group.itertuples(index=False):
            record = audit.loc[(row.unit_key, row.household, row.strategy)]
            path = Path(record.file_stem + ".json")
            if sha256_file(path) != record.layout_sha256 or not record.validator_pass:
                raise ValueError("A showcase layout differs from the validator audit")
            units[row.strategy] = document(path), path
        yield int(area), Unit.from_dict(document(prefix)), entry.household, units


def footprints(layout, unit, config, production, household, slot):
    applied, _ = apply_production(config, production, unit.interior.area)
    hh = parse_households(applied["households"], applied["furniture"])[household]
    items = library(applied["furniture"], layout["strategy"], hh.overrides.get("global_clearance_scale"))
    resolution = applied["raster"]["resolution_m"]
    for placed in layout["items"]:
        name = placed["type"]
        state_name = placed["states"]["normal"][slot]
        state = next(s for s in items[name].states if s.name == state_name)
        dx, dy, w, h = rectangles(state, resolution, placed["orientation_deg"])[0]
        x, y = placed["x"] + dx*resolution, placed["y"] + dy*resolution
        vertices = [(x, y), (x+w*resolution, y), (x+w*resolution, y+h*resolution), (x, y+h*resolution)]
        function = next((key for term, key in (
            ("bed", "sleep"), ("desk", "work"), ("table", "dine"), ("sofa", "lounge"),
            ("armchair", "lounge"), ("wardrobe", "storage"), ("shelving", "storage"),
        ) if term in name), "fixed")
        yield placed["instance_id"], vertices, state_name, function


def f3():
    config = load_config(CONFIG)
    production = document(A / "run.json")["production_settings"]
    fig, axes = plt.subplots(3, 9, figsize=(14, 7.2))
    figure(fig, "F3", "How the same shell serves different slots",
           "Validated H3 layouts on a normal day. Each row keeps the plan and scale fixed.")
    handles = [Patch(facecolor=c, label=k.title()) for k, c in FUNCTIONS.items()]
    legend(fig, handles + [Patch(facecolor="white", edgecolor=MUTED, hatch="///", label="Stowed")], 7, y=.903)
    for r, (_, unit, household, layouts) in enumerate(accepted_showcases()):
        xmin, ymin, xmax, ymax = unit.interior.bounds
        for s, strategy in enumerate(STRATEGIES):
            layout, _ = layouts[strategy]
            for i, slot in enumerate(SLOT_LABELS):
                ax = axes[r, 3*s+i]
                draw_unit(ax, unit, short=True)
                ax.set(xlim=(xmin-.23, xmax+.23), ylim=(ymin-.23, ymax+.23), title="")
                ax.axis("off")
                if r == 0:
                    ax.set_title(f"{strategy} · {SLOT_LABELS[slot]}", fontsize=7.4)
                if s == 0 and i == 0:
                    ax.text(-.08, .50, f"{unit.source}\n{unit.interior.area:.2f} m²", transform=ax.transAxes,
                            ha="right", va="center", fontsize=8.3, fontweight="bold")
                for _, points, state, function in footprints(layout, unit, config, production, household, slot):
                    ax.add_patch(Polygon(points, facecolor=FUNCTIONS[function], edgecolor=INK, linewidth=.46,
                                         alpha=.87, hatch="////" if state == "stowed" else None, zorder=2))
    fig.subplots_adjust(top=.84, bottom=.038, left=.095, right=.979, hspace=.13, wspace=.20)
    return export(fig, "F3")


def f4():
    data = csv(A / "solutions.csv", usecols=["source", "nia_m2", "household", "strategy", "fci_validator"])
    data["pool"] = np.where(data.source.eq("D3"), "D3", "real_plans")
    data["mid"] = binned_area(data.nia_m2) + 1
    med = data.groupby(["household", "pool", "strategy", "mid"], as_index=False).fci_validator.median()
    curves = csv(P1 / "f0_curves.csv").query("method == 'median_bin_cummax'")
    fig, axs = plt.subplots(2, 4, figsize=(13, 6.8), sharex=True, sharey=True)
    figure(fig, "F4", "Function coverage as floor area increases",
           "Median FCI by 2 m² bin and the monotone static reference used to estimate equivalent area.")
    legend(fig, strategy_legend()+[Line2D([], [], color=INK, ls="--", label="Fitted static reference")], 4)
    for r, (pool, pool_name) in enumerate(UNITS.items()):
        for c, (hh, name) in enumerate(HOUSEHOLDS.items()):
            ax = axs[r, c]
            grid(ax)
            if r == 0:
                ax.set_title(name, fontsize=9)
            if c == 0:
                ax.set_ylabel(f"{pool_name}\nMedian FCI")
            if r == 1:
                ax.set_xlabel("Net internal area (m²)")
            for strategy, grp in med[(med.household == hh) & (med.pool == pool)].groupby("strategy"):
                ax.plot(grp.mid, grp.fci_validator, color=STRATEGIES[strategy], marker="o", markersize=2.8, lw=1.2)
            fit = curves[(curves.household == hh) & (curves.reference_pooling == pool)]
            ax.plot(fit.area_m2, fit.fitted_fci_S0, "--", color=INK, lw=1.35)
            ax.axhline(.95, lw=.65, color=MUTED, ls=":")
            ax.set(xlim=(7.8, 50), ylim=(0, 1.02))
    fig.subplots_adjust(top=.81, left=.083, right=.98, bottom=.10, wspace=.12, hspace=.18)
    return export(fig, "F4")


def f5():
    data = csv(RESULTS / "g3/area_summary.csv").query(
        "stratum == 'area_bin' and pooling == reference_pooling and pooling in ['real_plans', 'D3']"
    )
    fig, axs = plt.subplots(2, 4, figsize=(13, 7.1), sharex=True, sharey="row")
    figure(fig, "F5", "Equivalent static area gained by form and time",
           "All matched pairs, including equal scores. Bands show reference-support bounds. The smallest observed-plan bin has six pairs.")
    handles = [Line2D([], [], label=l, color=c, marker=m, ms=4)
               for l, c, m in zip(UNITS.values(), COLORS, ("o", "s"))]
    handles.extend([Line2D([], [], color=SPARSE, marker="o", ls="", label="Fewer than 10 pairs"),
                    Line2D([], [], color=MUTED, marker="^", ls="", label="Upper bound unbounded")])
    legend(fig, handles, 4)
    for c, (hh, title) in enumerate(HOUSEHOLDS.items()):
        for r, (suffix, label) in enumerate([("m2", "Median gain (m²)"), ("pct_nia", "Median gain (% of NIA)")]):
            ax = axs[r, c]
            grid(ax)
            for (pool, color, mark) in zip(UNITS, COLORS, ("o", "s")):
                group = data[(data.pooling == pool) & (data.household == hh)].sort_values("area_bin_lo")
                x = (group.area_bin_lo + group.area_bin_hi)/2
                lo = group[f"all_pair_median_delta_ea_lower_{suffix}"]
                hi = group[f"all_pair_median_delta_ea_upper_{suffix}"]
                opens = group["all_pair_median_delta_ea_upper_unbounded" if r == 0 else
                              "all_pair_median_delta_ea_upper_pct_nia_unbounded"]
                supported = group.n_units.ge(10)
                ax.plot(x, lo.where(supported), marker=mark, ms=3.7, color=color, lw=1.25)
                ax.plot(x, hi.where(supported), ls=":", color=color, lw=1)
                ax.fill_between(x, lo, hi, where=supported, color=color, alpha=.13)
                sparse_bounds = ~supported & hi.notna() & hi.gt(lo)
                ax.vlines(x[sparse_bounds], lo[sparse_bounds], hi[sparse_bounds], color=SPARSE, lw=1.2)
                sparse_points = ~supported & ~opens
                ax.scatter(x[sparse_points], lo[sparse_points], color=SPARSE, s=18, marker=mark, zorder=4)
                ax.scatter(x[opens], lo[opens], marker="^", s=33,
                           color=np.where(supported[opens], color, SPARSE), zorder=5)
            if c == 0:
                ax.set_ylabel(label)
            if r == 0:
                ax.set_title(title, fontsize=9)
            else:
                ax.set_xlabel("Net internal area (m²)")
            ax.set(xlim=(7.5, 50.5))
    for r, suffix in enumerate(("m2", "pct_nia")):
        columns = [f"all_pair_median_delta_ea_{lim}_{suffix}" for lim in ("lower", "upper")]
        axs[r, 0].set_ylim(0, 1.06*data[columns].max().max())
    fig.subplots_adjust(top=.818, left=.077, right=.981, bottom=.10, hspace=.17, wspace=.15)
    return export(fig, "F5")


def f6():
    data = csv(RESULTS / "expD/dispersion.csv").query("population in ['real_plans', 'D3']")
    fig, axs = plt.subplots(2, 4, figsize=(13, 6.4), sharex=True, sharey=True)
    figure(fig, "F6", "Function varies within the same floor-area bin",
           "Interquartile range (75th less 25th percentile) across dwellings in each 2 m² bin.")
    legend(fig, strategy_legend(), 3)
    for r, (pool, label) in enumerate(UNITS.items()):
        for c, (hh, title) in enumerate(HOUSEHOLDS.items()):
            ax = axs[r, c]
            grid(ax)
            for strategy, grp in data[(data.population == pool) & (data.household == hh)].groupby("strategy"):
                ax.plot((grp.area_bin_lo+grp.area_bin_hi)/2, grp.fci_iqr,
                        marker="o", markersize=2.6, color=STRATEGIES[strategy], lw=1.2)
            if c == 0:
                ax.set_ylabel(f"{label}\nInterquartile range of FCI")
            if r == 0:
                ax.set_title(title, fontsize=9)
            if r == 1:
                ax.set_xlabel("Net internal area (m²)")
            ax.set(xlim=(7.5, 50.5))
    axs[0, 0].set_ylim(0, 1.06*data.fci_iqr.max())
    fig.subplots_adjust(top=.812, left=.087, right=.98, bottom=.10, wspace=.13, hspace=.19)
    return export(fig, "F6")


def f7():
    data = csv(RESULTS / "g3_review/benchmark/algorithm_summary.csv")
    labels = {"cp_sat": "Standalone CP-SAT", "greedy_footprint": "Greedy",
              "simulated_annealing": "Simulated annealing", "production_pipeline": "Production S0–S2"}
    fig, axs = plt.subplots(1, 3, figsize=(12, 4.8))
    figure(fig, "F7", "Layout quality, validity and solver time",
           f"{int(data.n_pairs.iloc[0])} matched pairs. Production time sums the three strategies. Standalone time includes S2 preparation and validation.")
    names = [labels[key] for key in data.algorithm]
    for i, (ax, column, title) in enumerate(zip(axs, ("validity_rate", "mean_fci", "mean_time_s"),
                                                ("Valid layouts (%)", "Mean validator FCI", "Mean elapsed time (s)"))):
        values = data[column]*(100 if i == 0 else 1)
        ax.barh(names, values, color=COLORS[:len(names)], height=.57)
        grid(ax)
        limit = (100, 1, values.max()*1.24)[i]
        ax.set(xlabel=title, xlim=(0, limit), ylim=(-.6, len(names)-.4))
        ax.invert_yaxis()
        for j, value in enumerate(values):
            label = f"{value:.0f}%" if i == 0 else f"{value:.3f}" if i == 1 else f"{value:.1f}"
            x, align, color = (value-4, "right", "#20242A") if i == 0 else (value+.018*limit, "left", INK)
            if i == 1:
                x, align = value-.04, "right"
            ax.text(x, j, label, color=color, ha=align, va="center", fontsize=9)
        if i:
            ax.tick_params(labelleft=False)
    fig.subplots_adjust(top=.81, left=.175, right=.978, bottom=.16, wspace=.16)
    return export(fig, "F7")


def f8():
    data = csv(RESULTS / "expC/predictions.csv").query("label_status == 'identified'")
    scores = csv(RESULTS / "expC/metrics.csv")
    tests = {"D1_test": "D1 held-out groups", "D2_external": "D2 transfer", "D3_external": "D3 transfer"}
    targets = dict(zip(("fci_S0", "fci_S2", "saving_m2"), ("Static FCI", "Form + time FCI", "Equivalent-area gain (m²)")))
    fig, axs = plt.subplots(3, 3, figsize=(10, 10.3), sharex="row", sharey="row")
    figure(fig, "F8", "GraphSAGE predictions against solver-derived labels",
           "The parity line marks exact agreement. Area targets include only identified labels.")
    legend(fig, [Line2D([], [], label=hh[:2], color=c, marker="o", ls="", ms=5)
                 for hh, c in zip(HOUSEHOLDS, COLORS)], 4, y=.903)
    for r, (target, label) in enumerate(targets.items()):
        bound = data[data.target.eq(target)][["y_true", "y_pred_gnn_graph"]].max().max() if r == 2 else 1
        for c, (test, title) in enumerate(tests.items()):
            ax = axs[r, c]
            grid(ax)
            sl = data[(data.target == target) & (data.test_set == test)]
            perf = scores[(scores.target == target) & (scores.test_set == test) & (scores.model == "gnn_graph")]
            if not len(sl) or (perf.n_evaluated.sum() != len(sl)):
                raise ValueError(f"Parity panel does not match held-out metrics: {test}, {target}")
            ax.plot([0, bound], [0, bound], color=MUTED, linewidth=1, ls="--")
            for hh, color in zip(HOUSEHOLDS, COLORS):
                pts = sl[sl.household == hh]
                ax.scatter(pts.y_true, pts.y_pred_gnn_graph, s=10, alpha=.28, color=color, edgecolors="none",
                           rasterized=True)
            if r == 0:
                ax.set_title(title)
            if c == 0:
                ax.set_ylabel(f"Predicted {label}")
            ax.set(xlabel=f"Solver label · {label}", xlim=(-.02*bound, 1.02*bound), ylim=(-.02*bound, 1.02*bound))
    fig.subplots_adjust(top=.852, left=.112, right=.977, bottom=.065, wspace=.15, hspace=.30)
    return export(fig, "F8")


def f9():
    data = csv(RESULTS / "ablations/summary.csv", dtype={"value": str})
    controls = {"clearance_scale": "1.0", "walking_width": "0.6", "resolution_m": "0.1"}
    data = data[~data.ablation.isin(["production", "household"])].copy()
    data = data[data.ablation.map(controls) != data.value].copy()
    labels = {"drop_one": "Remove", "clearance_scale": "Clearance ×", "walking_width": "Walk (m)",
              "resolution_m": "Grid (m)", "time_limit_s": "Limit (s)"}
    data["condition"] = [f"{labels[a]} {v.replace('_', ' ')}" for a, v in zip(data.ablation, data.value)]
    conditions = sorted(data.condition.unique())
    y = np.arange(len(conditions))
    fig, axes = plt.subplots(2, 4, figsize=(14, 9), sharey=True)
    figure(fig, "F9", "Sensitivity to geometry, furniture and search budget",
           "Changes relative to each matched control. × marks an unidentified contrast. Horizontal scales vary by panel.")
    metrics = [("change_median_saving_m2", "Change in median\nidentified ΔEA (m²)"),
               ("change_delta_a_min_m2", "Change in ΔAₘᵢₙ (m²)")]
    for c, (hh, label) in enumerate(HOUSEHOLDS.items()):
        rows = data[data.household == hh].set_index("condition").reindex(conditions)
        for r, (key, xlabel) in enumerate(metrics):
            ax = axes[r, c]
            values = rows[key].to_numpy(float)
            good = np.isfinite(values)
            ax.axvline(0, color=MUTED, lw=.8)
            ax.barh(y[good], values[good], color=np.where(values[good] >= 0, COLORS[0], COLORS[4]), height=.65)
            ax.scatter(np.zeros((~good).sum()), y[~good], marker="x", color=MUTED, s=16)
            ax.set_yticks(y, conditions, fontsize=7.6)
            ax.set_xlabel(xlabel)
            ax.grid(axis="x", color=GRID, linewidth=.65)
            ax.set_axisbelow(True)
            if r == 0:
                ax.set_title(label, fontsize=9.1)
    axes[0, 0].invert_yaxis()
    fig.text(.055, .027, "The ΔEA median uses the improved pairs with an identified positive gain. This subset can change between conditions.",
             fontsize=9, color=MUTED)
    fig.subplots_adjust(top=.853, left=.20, right=.975, bottom=.106, wspace=.19, hspace=.32)
    return export(fig, "F9")


def f10():
    by_size = csv(K / "hk_adequacy_by_size.csv")
    summary = csv(K / "hk_scenario_summary.csv")
    style = {
        "S0": ("Static", COLORS[0], "o", "-"),
        "S1": ("Form only", COLORS[1], "s", "-"),
        "S2": ("Form + time", COLORS[2], "D", "-"),
        "S2_catalogue_optimized": ("Optimized catalogue", INK, "o", "--"),
        "S2_compact_kit": ("H1 tested compact kit", COLORS[3], "x", ":"),
        "S2_larger_kit": ("H3 larger kit", COLORS[4], "^", "-"),
    }
    fig, axs = plt.subplots(2, 3, figsize=(12.7, 7.8))
    figure(fig, "F10", "Adequacy by size in Hong Kong scenario shells",
           "Each modeled size has 30 matched shapes. Adequacy uses the common quality rule at FCIq ≥ 0.95.")
    legend(fig, [Line2D([], [], label=t, color=c, marker=m, ms=4, ls=s) for t, c, m, s in style.values()], 6, y=.893)
    names = [(h, label) for h, label in HOUSEHOLDS.items() if h in set(by_size.household)]
    if len(names) != 3:
        raise ValueError("Unexpected household scope of the final scenario")
    for ax, (hh, name) in zip(axs[0], names):
        grid(ax)
        if hh.startswith("H3"):
            ax.axvspan(12.5, 16.5, color=COLORS[4], alpha=.11, zorder=0)
        for strategy, g in by_size[by_size.household == hh].groupby("strategy"):
            _, color, marker, line = style[strategy]
            ax.plot(g.area_m2, g.adequate_share, color=color, marker=marker, ls=line, ms=3.8, lw=1.4)
        ax.set(title=name, xlim=(7.7, 20.3), ylim=(0, 1.04), xlabel="Net internal area (m²)",
               xticks=[8, 10, 12, 14, 16, 18, 20], ylabel="Share adequate" if ax is axs[0, 0] else "")
        ax.yaxis.set_major_formatter(PercentFormatter(1, decimals=0))
    ax = axs[1, 0]
    h3 = next(h for h in HOUSEHOLDS if h.startswith("H3"))
    quality = by_size[by_size.household.eq(h3)]
    for strategy in ("S2_catalogue_optimized", "S2_larger_kit"):
        _, color, marker, line = style[strategy]
        part = quality[quality.strategy == strategy]
        ax.plot(part.area_m2, part.mean_fciq, color=color, marker=marker, ls=line, ms=3.8, lw=1.4)
    grid(ax)
    ax.axvspan(7.7, 12.5, color=COLORS[4], alpha=.11, zorder=0)
    ax.set(title="H3 · Mean service scored by quality", xlim=(7.7, 20.3), ylim=(0, 1.04),
           xlabel="Net internal area (m²)", ylabel="Mean FCIq", xticks=[8, 10, 12, 14, 16, 18, 20])
    ax = axs[1, 1]
    contrast = summary[summary.household == h3].set_index("strategy")
    order = ["S2_larger_kit", "S2_catalogue_optimized", "S2", "S1"]
    for i, strategy in enumerate(order):
        row, spec = contrast.loc[strategy], style[strategy]
        ax.hlines(i, row.ci_lo, row.ci_hi, color=spec[1], linewidth=2)
        ax.scatter(row.a_min, i, color=spec[1], marker=spec[2], zorder=3)
    ax.set_yticks(range(len(order)), labels=[style[k][0].replace("H3 ", "") for k in order], fontsize=7.7)
    ax.set(title="H3 · Modeled area at 50% adequate", xlabel="Crossing area (m²) and 95% interval")
    ax.grid(axis="x", color=GRID, linewidth=.7)
    ax = axs[1, 2]
    bands = csv(K / "hk_h3_size_bands.csv").set_index("area_min_m2")
    b = bands.loc[13]
    small = bands.loc[8]
    ax.axis("off")
    ax.text(.02, .91, "H3 · Larger kit versus catalogue", fontsize=10, fontweight="bold", transform=ax.transAxes)
    ax.text(.02, .67, f"{int(b.kit_adequate)}/{int(b.n_pairs)} vs {int(b.catalogue_adequate)}/{int(b.n_pairs)}",
            color=COLORS[4], fontsize=17, fontweight="bold", transform=ax.transAxes)
    ax.text(.02, .55, "adequate at 13–16 m²", fontsize=9, transform=ax.transAxes)
    ax.text(.02, .32, f"{small.kit_mean_fciq:.3f} vs {small.catalogue_mean_fciq:.3f}",
            color=INK, fontsize=15, fontweight="bold", transform=ax.transAxes)
    ax.text(.02, .21, "mean FCIq below 13 m²", fontsize=9, transform=ax.transAxes)
    fig.subplots_adjust(top=.827, left=.075, bottom=.105, right=.974, wspace=.435, hspace=.54)
    return export(fig, "F10")


def f11():
    repro = csv(R / "reproduction.csv").query("condition == 'paper_envelope_catalogue_only'")
    general = csv(R / "generalization_summary.csv").query("scope == 'overall' and population in ['real_plans', 'D3']")
    bridge = csv(R / "bridge.csv").query("reference_scope == 'population_specific'")
    source = csv(R / "source_values.csv").set_index("quantity").value
    fig, axs = plt.subplots(1, 3, figsize=(13.4, 5.5))
    figure(fig, "F11", "Room-level activity area and whole-dwelling equivalent area",
           "The reference room study deducts clearances. The modeled comparisons deduct furniture bodies.")
    ax = axs[0]
    x = np.arange(2)
    wide = repro.pivot(index="household", columns="strategy", values="free_activity_area_day_m2")
    for offset, strategy in zip((-.18, .18), ("S0", "S2")):
        ax.bar(x+offset, wide[strategy], color=STRATEGIES[strategy], width=.32, label=strategy)
    ax.axhspan(source.activity_area_static_low, source.activity_area_static_high, color=MUTED, alpha=.16)
    ax.axhline(source.activity_area_flexible, ls="--", lw=1, color=MUTED)
    ax.set_xticks(x, [h[:2] for h in wide.index])
    ax.set(title="Approximate 4 × 3 m room", ylabel="Daytime free area (m²)", ylim=(0, 10.3))
    ax.legend(handles=[Patch(color=STRATEGIES[s], label=s) for s in ("S0", "S2")] + [
        Patch(color=MUTED, alpha=.20, label="Source static (with clearance)"),
        Line2D([], [], color=MUTED, ls="--", label="Source folded (with clearance)"),
    ], loc="upper center", bbox_to_anchor=(.5, -.10), ncol=2, fontsize=6.9)
    ax = axs[1]
    order = general.set_index(["population", "household"]).loc[
        [(p, h) for p in UNITS for h in wide.index]
    ].reset_index()
    x = np.arange(len(order))
    left = np.zeros(len(order))
    for values, label, color in [
        (order.share_negative, "Decreased", COLORS[4]), (order.share_zero, "Equal", "#CED8E3"),
        (1-order.share_negative-order.share_zero, "Increased", COLORS[0]),
    ]:
        ax.barh(x, values, left=left, label=label, color=color, height=.54)
        left += values
    ax.set_yticks(x, [f"{r.household[:2]} · {'D3' if r.population == 'D3' else 'D1+D2'}"
                      for r in order.itertuples(index=False)])
    ax.set(title="Change in body-free area", xlabel="Share of layouts", xlim=(0, 1))
    ax.xaxis.set_major_formatter(PercentFormatter(1, decimals=0))
    ax.invert_yaxis()
    ax.legend(loc="upper center", bbox_to_anchor=(.5, -.20), ncol=3, fontsize=7.5)
    ax = axs[2]
    for hh, color in zip(wide.index, COLORS):
        g = bridge[(bridge.household == hh) & (bridge.reference_pooling == "real_plans")]
        exact = g[g.delta_gain_identified]
        bounds = g[g.delta_gain_lower_bound_only]
        ax.scatter(exact.gain_m2, exact.delta_ea_m2, label=hh[:2], color=color, alpha=.38, s=15,
                   edgecolors="none", rasterized=True)
        ax.scatter(bounds.gain_m2, bounds.delta_ea_lower_bound_m2, facecolors="none", edgecolors=color,
                   alpha=.65, s=19, marker="^", linewidths=.85, rasterized=True)
    ax.set(title="Equivalent-area gain in observed plans", xlabel="S2 − S0 body-free area (m²)",
           ylabel="Paired equivalent-area gain (m²)")
    handles, _ = ax.get_legend_handles_labels()
    ax.legend(handles=handles+[Line2D([], [], color=MUTED, marker="^", markerfacecolor="none", ls="",
                                     label="Gain ≥ marker value")],
              loc="upper center", bbox_to_anchor=(.5, -.20), ncol=3, fontsize=7.4)
    for ax in axs:
        grid(ax)
    fig.subplots_adjust(top=.81, left=.077, bottom=.235, right=.977, wspace=.44)
    return export(fig, "F11")


def f12():
    choice_path = K / "kit.yaml"
    chosen = document(choice_path)
    record = document(K / "release_manifest.json")
    config = load_config(CONFIG)
    if not record["passed"] or sha256_file(choice_path) != record["files"][choice_path.as_posix()]:
        raise ValueError("K3 selected geometry differs from the reviewed geometry")
    fig, axs = plt.subplots(4, 4, figsize=(10.5, 12.4),
                            gridspec_kw={"height_ratios": [2.49, 1.11, 1.30, 1.13]})
    figure(fig, "F12", "Dimensions of the K3 furniture kits",
           "Plan-view body dimensions at a common scale. The studied H1 candidate is illustrative.")
    for col, (hh, selection) in enumerate(chosen["by_household"].items()):
        pick = selection["kit"]
        kit, quality = kit_configuration(config, hh, pick)
        if quality != pick["qualities"]:
            raise ValueError("K3 quality factors differ")
        fig.text(.274 + col*.465, .894, f"{hh[:2]}  {pick['kit_id']} · "
                 f"{'largest observed mean' if col else 'ranking only, retain catalogue'}",
                 ha="center", color=INK, fontweight="bold", fontsize=10)
        item_keys = (BED[hh][0], "fold_down_desk", "drop_leaf_table", "wardrobe")
        for row, (key, title, color) in enumerate(zip(item_keys, ("Wall bed", "Fold-down desk", "Drop-leaf table", "Wardrobe"),
                                                      (FUNCTIONS[v] for v in ("sleep", "work", "dine", "storage")))):
            for offset, state in enumerate(("deployed", "stowed")):
                ax = axs[row, 2*col+offset]
                ax.axis("off")
                if key == "wardrobe" and offset == 1:
                    continue
                cfg = kit["furniture"]
                body = (cfg["static_items"][key] if key == "wardrobe" else
                        cfg["transformable_items"][key]["states"][state])
                width, depth = body["footprint"]
                label = f"{title} · {body['storage_units']:.1f} storage units" if key == "wardrobe" else f"{title} · {state}"
                ax.set(xlim=(-.11, 1.97), ylim=(-.29, (2.20, .82, 1.01, .84)[row]), aspect="equal")
                ax.set_title(label, fontsize=8.4)
                ax.add_patch(Rectangle((0, 0), width, depth, facecolor=color, alpha=.29, edgecolor=INK))
                arrow = dict(arrowstyle="<->", color=MUTED, lw=.72, shrinkA=0, shrinkB=0)
                ax.annotate("", (width, -.09), (0, -.09), arrowprops=arrow)
                ax.annotate("", (width+.10, depth), (width+.10, 0), arrowprops=arrow)
                ax.text(width/2, -.22, f"{width:.2f} m", ha="center", va="center", fontsize=8)
                ax.text(width+.22, depth/2, f"{depth:.2f} m", ha="center", va="center", rotation=90, fontsize=8)
    effects = csv(K / "paired_effects.csv")
    cohorts = [("heldout", "Held-out D3 shells"), ("real", "Observed plans ≤20 m²")]
    for col, (hh, selection) in enumerate(chosen["by_household"].items()):
        n = selection["n_training"]
        training = [
            [label, f"{selection[key+'_fciq']:.3f}", f"{selection[key+'_adequate']}/{n}"]
            for key, label in [("catalogue", "Catalogue"), ("selected", "Kit"), ("bespoke", "Bespoke")]
        ]
        transfer = []
        for key, label in cohorts:
            row = effects[(effects.household == hh) & (effects.cohort == key)].iloc[0]
            transfer.append([label, f"{row.mean_kit_fciq:.3f} / {row.mean_catalogue_fciq:.3f}",
                             f"{row.kit_adequate} / {row.catalogue_adequate} of {row.n_pairs}"])
        ax = fig.add_axes([.060 + col*.465, .018, .424, .182])
        ax.axis("off")
        for pos, title, table_rows, labels in [
            (.535, "Training", training, ["Fit-out", "Mean FCIq", "Adequate"]),
            (.00, "Transfer · Kit / catalogue", transfer, ["Sample", "Mean FCIq", "Adequate"]),
        ]:
            ax.text(0, pos+.459, title, fontsize=8.6, fontweight="bold", transform=ax.transAxes)
            table = ax.table(cellText=table_rows, colLabels=labels, cellLoc="left", colLoc="left",
                             colWidths=[.41, .32, .27], bbox=(0, pos, 1, .405))
            table.auto_set_font_size(False)
            table.set_fontsize(7.7)
            for (row, _), cell in table.get_celld().items():
                cell.set_edgecolor("white")
                cell.set_facecolor("#E5EDF4" if row == 0 else "#F3F7FA")
    fig.subplots_adjust(top=.858, left=.055, right=.97, bottom=.227, hspace=.41, wspace=.16)
    return export(fig, "F12")


def checked_still(path):
    INPUTS.add(path)
    with Image.open(path) as img:
        return np.asarray(img.convert("RGB"))


def checked_polish(index_path, render, frames):
    """Load the eight source-bound presentation renders used in F3b."""
    directory = RENDERS / "polish"
    proof = document(directory / "manifest.json")
    script = Path("scripts/12c_render_polish.py")
    INPUTS.add(script)
    if (not proof["passed"] or proof["scene_index_sha256"] != sha256_file(index_path)
            or proof["base_renderer_sha256"] != render["renderer_sha256"]
            or proof["polish_renderer_sha256"] != sha256_file(script)):
        raise ValueError("Presentation renders do not match their accepted scenes and renderer")
    expected = {
        *[("showcase_10", strategy, slot, "cutaway") for strategy in ("S0", "S2") for slot in SLOT_LABELS],
        *[("showcase_30", strategy, "day", "detail") for strategy in ("S0", "S2")],
    }
    views = {}
    for row in proof["frames"]:
        key = row["alias"], row["strategy"], row["slot"], row["view"]
        path = directory / ("_".join(key) + ".png")
        if (key in views or key not in expected or path.as_posix() != row["still"]
                or frames[key[:3]]["scene_sha256"] != row["scene_sha256"]
                or sha256_file(path) != row["sha256"]):
            raise ValueError("Wrong presentation render or altered frame")
        views[key] = path
    if views.keys() != expected:
        raise ValueError("Incomplete presentation render set")
    return views


def showcase_panel(unit, area, frames, polish):
    """Compose the three daily states and a matched room detail where supplied."""
    alias = f"showcase_{area:02d}"
    strategies = (("S0", "Static"), ("S2", "Form + time"))
    cuts = area == 10
    details = area == 30
    if details:
        fig = plt.figure(figsize=(11, 10.1))
        layout = fig.add_gridspec(3, 6, height_ratios=(1, 1, 1.45))
        panels = [[fig.add_subplot(layout[r, 2*c:2*c+2]) for c in range(3)] for r in range(2)]
    else:
        fig, panels = plt.subplots(2, 3, figsize=(11, 7))
    scenes = {s: document(Path(frames[(alias, s, "day")]["scene"])) for s, _ in strategies}
    caption = ["Validated H3 layouts on a normal day. Camera, lighting and scale are held fixed within this dwelling."]
    if details:
        caption = ["Validated H3 layouts on a normal day. The whole-flat views share camera, lighting and scale."]
    if scenes["S2"]["tb"] == 0:
        caption.append("S2 furniture states stay fixed throughout the day (TB = 0).")
    if cuts:
        caption[-1] += " The toilet enclosure is cut away to show the furniture."
    if details:
        caption[-1] += " The daytime close-ups use low wall sections to expose the main room."
    figure(fig, "F3b", f"{unit.source} · {unit.interior.area:.2f} m² for a couple", "\n".join(caption))
    for r, (strategy, strategy_label) in enumerate(strategies):
        scene = scenes[strategy]
        for c, (slot, slot_label) in enumerate(SLOT_LABELS.items()):
            key = alias, strategy, slot
            path = polish[(*key, "cutaway")] if cuts else Path(frames[key]["still"])
            ax = panels[r][c]
            ax.imshow(checked_still(path))
            ax.set_title(f"{strategy} {strategy_label} · {slot_label}\n"
                         f"FCI {scene['fci']:.3f}  ·  TB {scene['tb']:.2f}", fontsize=8.8)
            ax.axis("off")
    if details:
        for c, (strategy, strategy_label) in enumerate(strategies):
            ax = fig.add_subplot(layout[2, 3*c:3*c+3])
            ax.imshow(checked_still(polish[(alias, strategy, "day", "detail")]))
            ax.set_title(f"{strategy} {strategy_label} · Main room detail", fontsize=10)
            ax.axis("off")
    fig.subplots_adjust(top=.875 if details else .827 if cuts else .86,
                        left=.038, right=.975, bottom=.041, hspace=.20 if details else .18, wspace=.20 if details else .045)
    return export(fig, f"F3b_{area:02d}")


def render_panels(panel_areas=None):
    manifest_path = RENDERS / "render_manifest.json"
    scenes_path = RENDERS / "scene_index.json"
    render = document(manifest_path)
    index = document(scenes_path)
    if not render["passed"] or render["scene_index_sha256"] != sha256_file(scenes_path):
        raise ValueError("Rendered frames do not match scene origins")
    expected = {(e["alias"], e["strategy"], s) for e in index["scenes"] for s in e["slots"]}
    frames = {(r["alias"], r["strategy"], r["slot"]): r for r in render["frames"]}
    if expected != frames.keys() or len(frames) != 30 or render["stills"] != 30:
        raise ValueError("Incomplete Phase 12b figure input")
    for row in frames.values():
        for path, digest in {**row["outputs"], row["scene"]: row["scene_sha256"]}.items():
            if sha256_file(Path(path)) != digest:
                raise ValueError(f"Changed rendering input: {path}")
    polish = checked_polish(scenes_path, render, frames)
    config = load_config(CONFIG)
    production = document(A / "run.json")["production_settings"]
    files, audits = [], []
    for area, unit, hh, layouts in accepted_showcases():
        alias = f"showcase_{area:02d}"
        if panel_areas is None or area in panel_areas:
            files.extend(showcase_panel(unit, area, frames, polish))
        if panel_areas is not None:
            continue

        frame = frames[(alias, "S2", "day")]
        stem = Path(frame["audit"])
        projection = document(stem.with_suffix(".json"))
        layout, layout_path = layouts["S2"]
        scene = document(Path(frame["scene"]))
        if (scene["layout_sha256"] != sha256_file(layout_path) or projection["unit_key"] != unit.unit_key
                or projection["strategy"] != "S2" or projection["slot"] != "day"
                or projection["top_render_sha256"] != sha256_file(stem.with_suffix(".png"))):
            raise ValueError("An orthographic check refers to a different layout")
        expected_bodies = {key: v for key, v, _, _ in footprints(layout, unit, config, production, hh, "day")}
        actual_bodies = projection["projected_body_vertices_m"]
        if expected_bodies.keys() != actual_bodies.keys() or not expected_bodies:
            raise ValueError("Projection does not cover every furniture instance")
        fig, ax = plt.subplots(figsize=(5, 5))
        x0, y0, x1, y1 = projection["bounds_m"]
        ax.imshow(checked_still(stem.with_suffix(".png")), extent=(x0, x1, y0, y1))
        for item in expected_bodies:
            source, rendered = [MultiPoint(b[item]).convex_hull for b in (expected_bodies, actual_bodies)]
            distance = source.hausdorff_distance(rendered)
            ax.plot(*source.exterior.xy, color="#F7D154", lw=2.2)
            ax.plot(*rendered.exterior.xy, color=COLORS[0], lw=1.1, ls="--")
            audits.append(dict(showcase=area, unit_key=unit.unit_key, instance_id=item,
                               error_m=distance, passed=distance < .02))
        ax.set(xlabel="Local x (m)", ylabel="Local y (m)", title=f"{unit.source} · S2 daytime projections")
        ax.legend(handles=[Line2D([], [], color="#F7D154", lw=2.2, label="Validated layout outline"),
                           Line2D([], [], color=COLORS[0], ls="--", label="Projected mesh outline")],
                  loc="upper center", bbox_to_anchor=(.5, -.14), ncol=2, fontsize=7)
        fig.subplots_adjust(top=.94, bottom=.175)
        overlay = stem.with_name(stem.stem + "_overlay.png")
        fig.savefig(overlay, dpi=200)
        plt.close(fig)
        files.append(overlay)
    if panel_areas is not None:
        return files
    audit = pd.DataFrame(audits)
    if not audit.passed.all() or audit.showcase.nunique() != 3:
        raise ValueError("At least one projected furniture outline differs by 2 cm or more")
    csv_path = RENDERS / "geometry_audit.csv"
    audit.to_csv(csv_path, index=False, lineterminator="\n")
    return files+[csv_path]


def record_figures(key, outputs, started, refresh=False):
    path = OUTPUT / f"manifest_{key}.json"
    current = {"passed": True, "dpi": 300, "package": key,
               "inputs": {}, "outputs": {}}
    if refresh:
        current = json.loads(path.read_text(encoding="utf-8"))
        refreshed = {p.as_posix() for p in outputs}
        for name, digest in current["outputs"].items():
            if name not in refreshed and sha256_file(Path(name)) != digest:
                raise ValueError(f"Existing figure output changed: {name}")
        for name, digest in current["inputs"].items():
            if Path(name) not in INPUTS and sha256_file(Path(name)) != digest:
                raise ValueError(f"Existing figure source changed: {name}")
    elapsed = "polish_elapsed_seconds" if refresh else "elapsed_seconds"
    current[elapsed] = round(time.perf_counter()-started, 3)
    current["inputs"].update({p.as_posix(): sha256_file(p) for p in sorted(INPUTS)})
    current["outputs"].update({p.as_posix(): sha256_file(p) for p in outputs})
    write_manifest(path, current)


def main():
    started = time.perf_counter()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--only", choices=["2d", "3d", "polish"], help="Build a subset of the publication figures")
    args = parser.parse_args()
    start_style()
    if args.only == "polish":
        common_inputs = INPUTS.copy()
        record_figures("2d", f5()+f9(), started, refresh=True)
        INPUTS.clear()
        INPUTS.update(common_inputs)
        started = time.perf_counter()
        record_figures("3d", render_panels(panel_areas={10, 30}), started, refresh=True)
        print("Built F5, F9 and the two revised F3b figures", flush=True)
        return

    outputs = []
    if args.only != "3d":
        for build in (f1, f2, f3, f4, f5, f6, f7, f8, f9, f10, f11, f12):
            outputs.extend(build())
            print(f"Built {build.__name__.upper()}", flush=True)
    if args.only != "2d":
        outputs.extend(render_panels())
        print("Built F3b and three geometry overlays", flush=True)
    record_figures(args.only or "all", outputs, started)

if __name__ == "__main__":
    main()
