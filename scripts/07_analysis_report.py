"""Verify the complete E1--E4/A1 evidence package before approved A2 continuation."""
import json
from pathlib import Path
import numpy as np
import pandas as pd
from fea.households import parse_households, demanded_hours
from fea.io import prepare_cli, sha256_file, start_run, write_json
from phase07_analysis import load_evaluable_solutions
from phase07_statistics import invert_curve


def require(condition, message):
    if not condition:
        raise ValueError(message)


def main():
    args = prepare_cli(__doc__).parse_args()
    config, _, _ = start_run(args, "07_analysis_report")
    if args.dry_run:
        print("Would check E1--E4, metric identities, provenance and visual-review evidence, then write A1 acceptance.")
        return
    root = Path("results/expA")
    solutions, gate = load_evaluable_solutions(config)
    checks = []
    def check(condition, message):
        require(condition, message)
        checks.append(message)
    read = lambda name: json.loads((root/name).read_text())
    metrics, decomposition, layouts, causes = [read(name) for name in (
        "metrics_run.json", "decomposition_manifest.json", "layout_manifest.json", "exclusion_audit/manifest.json")]
    check(metrics["status"] == "complete" and metrics["completed_groups"] == 20, "All 20 metric groups complete")
    for manifest in [metrics["inputs"], decomposition, layouts]:
        check(manifest["evaluability_sha256"] == gate["evaluability_sha256"], "Analysis uses frozen E1 digest")
    check(metrics["inputs"]["raw_sha256"] == gate["raw_solutions_sha256"] == decomposition["source_sha256"], "Original raw A digest preserved")
    for name, digest in metrics["inputs"]["implementations"].items():
        check(sha256_file(Path(name)) == digest, "Metric implementation digest: "+name)
    for name, key in [("diagnostics.csv", "diagnostics_sha256"), ("cause_classification.csv", "classification_sha256")]:
        check(sha256_file(root/"exclusion_audit"/name) == causes[key], "E2 evidence digest: "+name)
    check(causes["sample_units"] == 20 and not causes["geometry_repaired"] and not causes["main_evaluability_changed"], "E2 fixed 20-unit no-repair audit")
    check(causes["sample_sha256"] == sha256_file(root/"exclusion_audit_sample.csv"), "E2 sample unchanged")
    check(causes["classification_input_sha256"] == sha256_file(Path("config/exclusion_cause_reviews.json")), "E2 visual classification input unchanged")
    visual_path = Path("config/a1_visual_review.json")
    visual = json.loads(visual_path.read_text())
    check(visual["passed"] and visual["reviewed_layouts"] == 33, "Actual visual review covers all 33 layouts")
    for name, digest in visual["hashes"].items():
        check(sha256_file(Path(name)) == digest, "Visual-review artifact digest: "+name)
    audit = pd.read_csv(root/"layout_audit.csv")
    check(len(audit) == 33 and audit.validator_pass.eq(True).all() and layouts["all_revalidated"], "All 33 saved layouts independently validated")
    check(sha256_file(root/"layout_audit.csv") == layouts["audit_sha256"], "Layout audit manifest digest")
    check(sha256_file(root/"layout_selection.csv") == layouts["selection_sha256"], "Layout selection manifest digest")
    for row in audit.itertuples():
        for extension, digest in [("json", row.layout_sha256), ("png", row.png_sha256), ("pdf", row.pdf_sha256)]:
            require(sha256_file(Path(row.file_stem+"."+extension)) == digest, "Saved layout artifact changed")
    checks.append("All 99 layout JSON/PNG/PDF digests match")
    fea, curve, amin, savings, tests = [pd.read_csv(root/(name+".csv")) for name in (
        "fea", "f0_curve", "min_adequate_area", "area_saving_curve", "tests")]
    for frame in [fea, curve, amin, savings, tests]:
        check(not np.isinf(frame.select_dtypes(include="number").to_numpy()).any(), "Numeric output has no infinities")
    main_wide = solutions.pivot(index=["unit_key", "household"], columns="strategy", values="fci_validator")
    counts = solutions.drop_duplicates("unit_key").source.value_counts()
    pool_counts = {"pooled":sum(counts), "real_plans":counts.D1+counts.D2, **counts.to_dict()}
    summaries = []
    for (pooling, household), frame in fea.groupby(["pooling", "household"]):
        require(len(frame) == pool_counts[pooling] and not frame.unit_key.duplicated().any(), "FEA group membership count")
        if pooling != "pooled":
            allowed = ["D1", "D2"] if pooling == "real_plans" else [pooling]
            require(frame.source.isin(allowed).all(), "FEA source membership")
        indexed = frame.set_index(["unit_key", "household"])
        for s in ["S0", "S1", "S2"]:
            require(np.allclose(indexed["fci_"+s], main_wide.loc[indexed.index,s], atol=1e-10), "FEA input capacity mismatch")
        fitted = curve[(curve.pooling == pooling)&(curve.household == household)].sort_values("area_m2")
        expected, censored, lower = invert_curve(fitted.area_m2, fitted.fitted_fci_S0, frame.fci_S2)
        require(np.allclose(expected, frame.fea_m2, equal_nan=True, atol=1e-8), "FEA monotone-inverse identity")
        require(np.array_equal(censored, frame.right_censored) and np.array_equal(lower, frame.at_lower_support_boundary), "FEA support flags")
        require(np.allclose(frame.saving_m2, frame.fea_m2-frame.area_m2, equal_nan=True, atol=1e-8), "Absolute saving identity")
        require(np.allclose(frame.saving_rel, frame.saving_m2/frame.area_m2, equal_nan=True, atol=1e-8), "Relative saving identity")
        valid = frame[~frame.right_censored]
        summaries.append(dict(pooling=pooling, household=household, units=len(frame), uncensored=len(valid),
            right_censored_fraction=float(frame.right_censored.mean()), lower_boundary_fraction=float(lower.mean()),
            median_saving_m2=float(valid.saving_m2.median()) if len(valid) else None,
            negative_savings=int((valid.saving_m2 < -1e-8).sum())))
    check(len(summaries) == 20, "All 20 FEA groups match capacities, source membership, inversion and support flags")
    check(len(amin) == 180 and len(tests) == 60, "Expected adequate-area and paired-test grids")
    for frame in [amin, savings]:
        for lo in [c for c in frame if c.endswith("ci_lo")]:
            hi = lo[:-2]+"hi"
            check(frame[lo].isna().eq(frame[hi].isna()).all() and (frame[lo].dropna() <= frame.loc[frame[lo].notna(), hi]).all(), "Interval endpoints consistent: "+lo)
    check(amin.loc[amin.status != "identified", "a_min_m2"].isna().all(), "Unsupported adequacy crossings withheld")
    check(tests.p_value.between(0,1).all() and tests.p_holm_all_reported_tests.between(0,1).all(), "Paired probabilities within bounds")
    summary = pd.DataFrame(summaries)
    summary.to_csv(root/"analysis_summary.csv",index=False)
    awide = amin.pivot(index=["pooling","household","tau"], columns="strategy", values="a_min_m2")
    reversal = awide[(awide.S2 > awide.S1+1e-8)|(awide.S1 > awide.S0+1e-8)].reset_index()
    reversal.to_csv(root/"adequacy_fit_reversals.csv",index=False)
    h4 = parse_households(config["households"],config["furniture"])["H4_parent_child"]
    furniture = config["furniture"]
    require(h4.capability_rules["sleep_1"]["satisfied_by"] == [["sleep_1"]], "H4 ceiling rule changed")
    providers = {name:item for name,item in furniture["static_items"].items() if "sleep_1" in item["serves"]}
    beds = sum(furniture["max_instances"].get(name,furniture["max_instances"]["default"]) for name in providers)
    require(len(h4.variants)==1 and beds==1, "H4 ceiling derivation prerequisites changed")
    day = h4.variants[0]
    night = next(s for s in h4.slots if s.name == "night")
    sleep_weights = sorted([d.weight for d in day.demand["night"] if d.need == "sleep_1"],reverse=True)
    lost = night.hours*sum(sleep_weights[beds:])
    denominator = demanded_hours(h4,day.name)
    ceiling = 1-lost/denominator
    actual = solutions[(solutions.household==h4.name)&(solutions.strategy=="S0")].fci_validator.max()
    check(actual <= ceiling+1e-8, "H4 S0 observed maximum respects catalogue ceiling")
    limitation = dict(H4_S0=dict(static_sleep_1_items=sorted(providers), max_sleep_1_instances=beds,
        unserved_weighted_hours=lost, denominator=denominator, capacity_upper_bound=ceiling,observed_max=float(actual),
        implication="Catalogue-limited baseline; no H4 static adequate-area or causal area-saving headline."),
        independent_logistic_order_reversals=len(reversal),
        FEA="Conditional on uncensored units; negative values and right-censoring retained. Not a household-specific spatial counterfactual.")
    write_json(root/"analysis_limitations.json",limitation)
    lines = ["# Phase 7 review response and A1 evidence", "",
        "E1--E4 and A1 are complete. Original A solve acceptance remains failed; the separate, reviewed evaluability analysis gate passes. No A re-solve, geometry repair or main numerical-configuration change was made.", "",
        f"E1: {gate['frozen_units']} frozen units; {gate['evaluable_units']} retained and {gate['excluded_units']} excluded. All {gate['included_cases']} retained cases validate with zero strategy-ordering failures. All 116 structural-failure units fail condition (a). Five of seven all-zero D1 units fail (b); the two that pass E1 and 67 valid D3 zero cases remain.", "",
        "E2: fixed-seed 20 excluded units: 8 rasterization, 1 genuinely narrow passage in the supplied drawing, 11 other/ambiguous topology, 0 confirmed conversion. This sample happened to contain only D1. These are audit classifications, not verified real-building causes. See [cause audit](expA_exclusion_causes.md).", "",
        "E3: [composition table and histogram](expA_evaluability.md) report NIA, room count and source shifts. Retained D1/D2/D3 counts are 1236/873/510. Binning does not remove all within-bin selection bias. D3 is a designed grid, not a population sample.", "",
        "E4: all retained units have four households by three strategies. Exclusions match E1 as whole units. A1 has 20 source/household groups, 1,000 paired unit bootstrap draws per group, supported f0 inversions, adequate-area fits, paired tests with Holm adjustments, F4b, and 33 revalidated, visually inspected layouts. Saving and decomposition figures show pooled, real-plan and designed-shell panels (S1).", "",
        "## Interpretation limits discovered during A1", "",
        f"**H4 static catalogue ceiling:** S0 permits one static single bed, while H4 requires two separate sleep_1 tokens. A double-bed sleep_2 token cannot satisfy a sleep_1 demand. At least {lost:g} of {denominator:g} weighted hours are unserved regardless of floor area, giving FCI <= {ceiling:.9f}, exactly the observed maximum. The H4 S0 adequate-area crossing is therefore unidentified, and its form gain combines catalogue availability with geometry. Do not interpret it as a time-sharing or housing-policy effect. Main counts and capability rules remain unchanged; see Q24.", "",
        f"Separate logistic models have {len(reversal)} fitted ordering reversals, recorded in adequacy_fit_reversals.csv. These reflect independently fitted probability curves; all raw paired capacities retain strict ordering. Do not claim that time sharing harms capacity or force fitted crossings into order after seeing the results.", "",
        "FEA is inversion of a pooled static reference, not a spatial counterfactual for the same household. A high-performing small unit or a low-performing large unit may yield a negative equivalent-area difference; flat or saturated curves can leave targets unsupported. The table below reports the uncensored median and censoring share together. No unconditional positive saving claim is supported merely by nonnegative FCI gains. Wide, unidentified and insufficient-bootstrap intervals are explicitly retained.", "",
        summary.to_markdown(index=False,floatfmt=".4f"), "",
        "## Continuation", "",
        "A2 uses all evaluable units at NIA <=20 m2, H3/H4 and S0/S1/S2, with explicit one-side double-bed overrides and unchanged 120-second/four-worker full-anchor solves. Original sofa_bed clearance was front-only 0.50 m, so the override also changes direction for that family; this is not a uniform relaxation. The fixed local-left side and four rotations are stated, without an added mirrored family. Revalidate original layouts before using warm starts.", "",
        "Then B (footprint greedy), D/R/ablations, C, reduced K, HK, literature and G3 follow the review order. K uses H1+H3 and retains the 48-hour limit. No intermediate reviewer stop is required. These future experiments are not claimed complete by this report.", ""]
    Path("reports/phase07_review_response.md").write_text("\n".join(lines),encoding="utf-8")
    outputs = [root/name for name in ["analysis_acceptance.json","evaluability.csv","analysis_summary.csv","analysis_limitations.json",
        "adequacy_fit_reversals.csv","metrics_run.json","decomposition_manifest.json","layout_manifest.json","exclusion_audit/manifest.json"]]
    write_json(root/"analysis_package_acceptance.json",dict(passed=True,evaluability_sha256=gate["evaluability_sha256"],
        original_solve_acceptance_passed=False,checks=checks,visual_review_sha256=sha256_file(visual_path),
        report_sha256=sha256_file(Path("reports/phase07_review_response.md")),
        outputs={p.as_posix():sha256_file(p) for p in outputs},
        permits="A2 continuation under phase07_review; not acceptance of all planned experiments or policy conclusions"))
    print(json.dumps(dict(passed=True,checks=len(checks),units=gate["evaluable_units"],layouts=len(audit),H4_S0_ceiling=ceiling)))


if __name__ == "__main__":
    main()
