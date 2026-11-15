"""Build the seven final publication tables from accepted evidence."""

import json
import time
from pathlib import Path

import pandas as pd

from fea.config import load_config
from fea.io import sha256_file
from phase12_artifacts import write_manifest


RESULTS = Path("results")
OUTPUT = RESULTS / "tables/g4"
CONFIG = Path("config/project.yaml")
A = RESULTS / "expA_f1"
ANALYSIS = A / "analysis"
BENCHMARK = RESULTS / "g3_review/benchmark"
INPUTS = {CONFIG, Path("config/furniture.yaml"), Path("config/households.yaml"),
          Path("config/downloads.yaml"), Path("scripts/12_make_tables.py"), Path("scripts/phase12_artifacts.py")}
OUTPUTS = []
DASH = "—"


def read(path, **kwargs):
    INPUTS.add(path)
    return pd.read_csv(path, **kwargs)


def document(path):
    INPUTS.add(path)
    return json.loads(path.read_text(encoding="utf-8"))


def md_cell(value):
    return DASH if pd.isna(value) else str(value).replace("|", r"\|").replace("\n", " ")


def markdown_table(headers, rows):
    lines = [headers, [":---"]*len(headers), *rows]
    return "\n".join("| " + " | ".join(md_cell(cell) for cell in row) + " |" for row in lines)


def interval(value, lo, hi, places=2):
    if pd.isna(value):
        return DASH
    point = f"{value:.{places}f}"
    if pd.isna(lo) or pd.isna(hi):
        return point
    return f"{point} [{lo:.{places}f}, {hi:.{places}f}]"


def fmt(value, places=3):
    return DASH if pd.isna(value) else f"{value:.{places}f}"


def percent(value):
    return DASH if pd.isna(value) else f"{100*value:.1f}%"


def source_notes(paths):
    return " · ".join(f"[{p.name}](../../../{p.as_posix()})" for p in map(Path, paths)) + "."


def publish(name, title, data, text):
    stem = OUTPUT / name
    files = [stem.with_suffix(".csv"), stem.with_suffix(".md")]
    data.to_csv(files[0], index=False, lineterminator="\n")
    files[1].write_text(f"# {name} · {title}\n\n{text.strip()}\n", encoding="utf-8", newline="\n")
    OUTPUTS.extend(files)


def t1():
    count = RESULTS / "corpus/counts.csv"
    sample = A / "sample.csv"
    abo = Path("reports/schemas/D4_summary.json")
    hk = RESULTS / "scenario_hk/territory_context.csv"
    units = read(count).set_index("source")
    area = read(sample).groupby("source").nia_m2
    abo_meta = document(abo)
    context = read(hk).iloc[0]
    names = {
        "D1": "Swiss Dwellings", "D2": "ResPlan", "D3": "Generated shells",
        "D4": "Amazon Berkeley Objects", "D5": "American Time Use Survey",
        "D6": "Hong Kong 2021 census",
    }
    data = []
    for code, name in names.items():
        row = {"dataset": code, "name": name}
        if code in units.index:
            record, values = units.loc[code], area.get_group(code)
            row.update(total_records=int(record.total), unique_eligible=int(record.included),
                       selected_exp_a=int(record.expA_sample), evaluable_exp_a=len(values),
                       min_nia_m2=values.min(), median_nia_m2=values.median(), max_nia_m2=values.max(),
                       role="Normalized plans" if code != "D3" else "Controlled shell grid")
        elif code == "D4":
            row.update(total_records=abo_meta["listings"],
                       role=f"Dimension context, {abo_meta['usable_dimension_triples']:,} usable dimension triples")
        elif code == "D5":
            row.update(role="Optional calibration omitted")
        else:
            row.update(total_records=int(context.sdu_n), role="Territory context, number of subdivided units")
        data.append(row)
    frame = pd.DataFrame(data)
    for col in ["total_records", "unique_eligible", "selected_exp_a", "evaluable_exp_a"]:
        frame[col] = frame[col].astype("Int64")
    rows = [[r.dataset, r.name, r.total_records, r.unique_eligible, r.selected_exp_a, r.evaluable_exp_a,
             f"{r.min_nia_m2:.2f} / {r.median_nia_m2:.2f} / {r.max_nia_m2:.2f}" if pd.notna(r.min_nia_m2) else DASH,
             r.role] for r in frame.itertuples(index=False)]
    md = markdown_table(["ID", "Dataset", "Records", "Unique eligible", "Selected A", "Evaluable A",
                         "NIA min / median / max (m²)", "Role"], rows)
    publish("T1", "Datasets and analysis coverage", frame,
            f"{md}\n\nThe Exp. A sample counts before and after the independent empty-geometry screen appear in the "
            f"two A columns. D6 coverage supplies counts for the territory.\n\n{source_notes([count, sample, abo, hk])}")


def t2(cfg):
    path = RESULTS / "furniture/abo_dimension_check.csv"
    abo = read(path).set_index(["item", "state"])
    data = []
    for group, strategies in [("static_items", "S0, S1, S2"), ("transformable_items", "S1, S2")]:
        for name, item in cfg[group].items():
            for state, body in item.get("states", {"static": item}).items():
                flag = abo.loc[(name, state)] if (name, state) in abo.index else None
                tokens = item["serves"] if state == "static" else item["serves"][state]
                row = dict(item=name, state=state, width_m=body["footprint"][0], depth_m=body["footprint"][1],
                           clearance_m=", ".join(f"{side} {depth:.2f}" for side, depth in body["clearance"].items()),
                           capabilities=", ".join(tokens), applicable_strategies=strategies,
                           wall_backed=item["wall_backed"], tall=item["tall"], storage_units=item.get("storage_units", 0),
                           effort_per_change=item.get("effort", 0),
                           max_instances=cfg["max_instances"].get(name, cfg["max_instances"]["default"]),
                           abo_flag=flag.flag if flag is not None else None,
                           abo_matches=flag.n if flag is not None else None)
                data.append(row)
    frame = pd.DataFrame(data).astype({"abo_matches": "Int64"})
    rows = [[r.item.replace("_", " "), r.state, f"{r.width_m:.2f} × {r.depth_m:.2f}", r.clearance_m or DASH,
             r.capabilities or DASH, r.applicable_strategies, r.max_instances, r.abo_flag]
            for r in frame.itertuples(index=False)]
    md = markdown_table(["Item", "State", "Body (m)", "Clearance (m)", "Capabilities", "Strategies",
                         "Max. count", "ABO flag"], rows)
    publish("T2", "Furniture bodies, clearance and capabilities", frame,
            f"{md}\n\nThe CSV includes storage, anchoring, height class and transformation effort. ABO product "
            f"categories provide dimensional context. The approved dimension check retained the catalogue "
            f"values.\n\n{source_notes([Path('config/furniture.yaml'), path])}")


def t3(cfg):
    data = []
    for household, spec in cfg["households"].items():
        for variant, day in spec["variants"].items():
            for slot, (start, end) in cfg["slots"].items():
                demands = day["demand"][slot]
                text = []
                for demand in demands:
                    token = demand["need"]
                    if "units" in demand:
                        token += f" ({demand['units']:g} capacity units)"
                    if "weight" in demand:
                        token += f" (weight {demand['weight']:g})"
                    text.append(token)
                data.append(dict(household=household, persons=spec["persons"], variant=variant,
                                 frequency=day["frequency"], slot=slot, start_hour=start, end_hour=end,
                                 duration_h=(end-start) % 24, demands=", ".join(text) or "Away",
                                 scope="Primary" if household in cfg["main_households"] else "Sensitivity"))
    frame = pd.DataFrame(data)
    if not frame.groupby(["household", "variant"]).duration_h.sum().eq(24).all():
        raise ValueError("A household schedule does not cover 24 hours")
    rows = [[r.household.split("_")[0], r.persons, r.variant, fmt(r.frequency), r.slot,
             f"{r.start_hour:02d}:00–{r.end_hour:02d}:00 ({r.duration_h} h)", r.demands]
            for r in frame.itertuples(index=False)]
    md = markdown_table(["Household", "People", "Day variant", "Frequency", "Slot", "Clock (duration)", "Demand"], rows)
    publish("T3", "Household schedules", frame,
            f"{md}\n\nThe FCI demand schedule covers furniture-supported activities. Fixed service rooms cover cooking and hygiene. "
            f"Storage is credited by available capacity. H5 is used in sensitivity analysis.\n\n"
            f"{source_notes([Path('config/households.yaml')])}")


def t4():
    area_path = RESULTS / "g3/area_summary.csv"
    fci_path = ANALYSIS / "primary_effects.csv"
    crossing_path = ANALYSIS / "min_adequate_area.csv"
    area = read(area_path).query("stratum == 'overall' and pooling == reference_pooling")
    scores = read(fci_path).query("stratum == 'overall'")
    crossings = read(crossing_path).query("strategy == 'S2' and tau == 0.95")
    keys = ["pooling", "household"]
    frame = area.drop(columns=["stratum", "area_bin_lo", "area_bin_hi"])
    for comparison, label in [("S1-S0", "form"), ("S2-S1", "time"), ("S2-S0", "total")]:
        subset = scores[scores.comparison == comparison][keys + ["mean_difference", "mean_difference_ci_lo",
                                                                "mean_difference_ci_hi", "mean_difference_ci_status"]]
        subset = subset.rename(columns={k: f"{label}_{k}" for k in subset if k not in keys})
        frame = frame.merge(subset, on=keys, validate="one_to_one")
    crossing_cols = ["delta_vs_S0_m2", "delta_vs_S0_m2_ci_lo", "delta_vs_S0_m2_ci_hi", "delta_vs_S0_m2_ci_status"]
    frame = frame.merge(crossings[keys + crossing_cols], on=keys, validate="one_to_one")
    if len(frame) != len(area):
        raise ValueError("Incomplete joined primary effects")
    md = []
    for pool in ["real_plans", "D3", "D1", "D2", "pooled"]:
        data = frame[frame.pooling == pool]
        if data.empty:
            continue
        md.append(f"## {pool.replace('_', ' ')}")
        rows = []
        for r in data.itertuples(index=False):
            effects = [interval(getattr(r, f"{key}_mean_difference"), getattr(r, f"{key}_mean_difference_ci_lo"),
                                getattr(r, f"{key}_mean_difference_ci_hi"), 4) for key in ("form", "time")]
            gain = interval(r.median_delta_ea_identified_positive_m2, r.median_delta_ea_identified_positive_m2_ci_lo,
                            r.median_delta_ea_identified_positive_m2_ci_hi)
            bounds = f"{r.all_pair_median_delta_ea_lower_m2:.2f}–{r.all_pair_median_delta_ea_upper_m2:.2f}"
            if r.all_pair_median_delta_ea_upper_unbounded:
                bounds = f"≥{r.all_pair_median_delta_ea_lower_m2:.2f}"
            crossing = interval(r.delta_vs_S0_m2, r.delta_vs_S0_m2_ci_lo, r.delta_vs_S0_m2_ci_hi)
            rows.append([r.household[:2], r.n_units, percent(r.share_fully_functional_S0),
                         percent(r.share_fci_improved), *effects, r.n_identified_positive_gains, gain,
                         r.n_lower_bound_among_fci_improved,
                         f"≥{r.median_among_fci_improved_lower_bound_m2:.2f}" if r.n_lower_bound_among_fci_improved else DASH,
                         bounds, crossing])
        md.append(markdown_table(["Household", "Pairs", "Full S0", "S2 improves", "Mean form effect", "Mean time effect",
                                  "Identified positive n", "Their median ΔEA (m²)", "Bound-only improved n",
                                  "Improved-group median lower bound (m²)", "All-pair median ΔEA bounds (m²)",
                                  "ΔA-min at τ=0.95 (m²)"], rows))
    md += ["Intervals are 95% bootstrap intervals when supported. All-pair bounds and the improved-group lower bound "
           "reflect reference-curve support. The CSV retains fit statuses and counts of supported resamples.",
           source_notes([area_path, fci_path, crossing_path])]
    publish("T4", "Matched effects, equivalent area and adequacy", frame, "\n\n".join(md))


def t5():
    path = BENCHMARK / "algorithm_summary.csv"
    frame = read(path)
    rows = [[r.algorithm.replace("_", " "), r.n_pairs, percent(r.validity_rate), fmt(r.mean_fci, 4),
             fmt(r.median_fci, 4), fmt(r.mean_time_s, 2), fmt(r.median_time_s, 2), r.timing_basis]
            for r in frame.itertuples(index=False)]
    md = markdown_table(["Method", "Matched cases", "Valid", "Mean FCI", "Median FCI", "Mean s", "Median s",
                         "Time basis"], rows)
    publish("T5", "Solver comparison", frame, f"{md}\n\n{source_notes([path])}")


def t6():
    path = RESULTS / "expC/metrics.csv"
    auc_path = BENCHMARK / "c_adequacy_auc.csv"
    frame, auc = read(path), read(auc_path)
    keys = ["test_set", "household", "target", "model"]
    extra = [*keys, "roc_auc", "status", "n_adequate", "n_at_full_fci", "tau"]
    all_metrics = frame.merge(auc[extra].rename(columns={"status": "auc_status"}), on=keys,
                              how="left", validate="one_to_one")
    md = []
    for test, group in all_metrics.groupby("test_set", sort=False):
        md.append(f"## {test.replace('_', ' ')}")
        rows = [[r.household[:2], r.target, r.model, r.n_evaluated, r.n_bound_only, fmt(r.mae),
                 fmt(r.rmse), fmt(r.r2), fmt(r.spearman), fmt(r.infer_ms_per_unit, 4), fmt(r.roc_auc)]
                for r in group.itertuples(index=False)]
        md.append(markdown_table(["Household", "Target", "Model", "Evaluated n", "Bounds n", "MAE", "RMSE", "R²",
                                  "Spearman", "ms per unit", "Adequacy ROC AUC"], rows))
    md.extend(["Errors are in FCI units for coverage and m² for equivalent-area gain. ROC AUC is a post-hoc "
               "diagnostic for FCI at least 0.95. Single-outcome strata and non-FCI labels have no ROC AUC.",
               source_notes([path, auc_path])])
    publish("T6", "Surrogate accuracy and transfer", all_metrics, "\n\n".join(md))


def t7():
    path = RESULTS / "expD/confusion.csv"
    frame = read(path).query("tau == 0.95").copy()
    names = {
        "ulrich_threshold": "Ulrich (2025) area comparator",
        "hk_bhu_8m2": "Hong Kong basic housing unit area minimum",
    }
    frame = frame.rename(columns={"indicator": "comparator"})
    frame["comparator"] = frame["comparator"].replace(names)
    INPUTS.add(RESULTS / "expD/threshold_sweeps.csv")
    sections = []
    for population, group in frame.groupby("population", sort=False):
        sections.append(f"## {population.replace('_', ' ')}")
        rows = [[r.household[:2], r.strategy, r.comparator, fmt(r.threshold_m2, 0), r.n,
                 r.tp, r.tn, r.fp, r.fn, percent(r.misclassification_rate)]
                for r in group.itertuples(index=False)]
        sections.append(markdown_table(["Household", "Strategy", "Comparator", "NIA cutoff (m²)", "Cases",
                                        "TP", "TN", "FP", "FN", "Disagreement"], rows))
    sections += ["Positive means adequate. Disagreement uses modeled FCI at least 0.95 as its reference. "
                 "The 30/45 m² and 8 m² comparators are simple modeled area rules.",
                 source_notes([path, RESULTS / "expD/threshold_sweeps.csv"])]
    publish("T7", "Disagreement between area cutoffs and modeled adequacy", frame, "\n\n".join(sections))


def main():
    started = time.perf_counter()
    OUTPUT.mkdir(parents=True, exist_ok=True)
    config = load_config(CONFIG)
    t1()
    t2(config["furniture"])
    t3(config["households"])
    t4()
    t5()
    t6()
    t7()
    write_manifest(OUTPUT / "manifest.json", {
        "passed": True, "elapsed_seconds": round(time.perf_counter()-started, 3),
        "inputs": {p.as_posix(): sha256_file(p) for p in sorted(INPUTS)},
        "outputs": {p.as_posix(): sha256_file(p) for p in OUTPUTS},
    })
    print("Built T1–T7 in CSV and Markdown")


if __name__ == "__main__":
    main()
