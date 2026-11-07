"""Recompute round-2 quality checks and diagnostic figures from saved artifacts."""
from pathlib import Path
import json

import pandas as pd

from fea.diagnostics import mechanism_shell, mechanism_witness
from fea.households import parse_households
from fea.io import prepare_cli, start_run, write_json
from fea.viz.layouts import render_layout


def main():
    parser = prepare_cli(__doc__)
    parser.add_argument("--arm", default="r2_wallflush_w1_s20_t30")
    parser.add_argument("--reference", default="w8_s10_t60")
    parser.add_argument("--render", action="store_true")
    args = parser.parse_args()
    config, _, _ = start_run(args, "06_round2_report")
    if args.dry_run:
        print("Would compare measured means and render diagnostic witnesses; no uploads.")
        return
    root = Path("results/pilot/round2")
    benchmarks = Path("results/pilot/benchmarks")
    frame = pd.read_csv(benchmarks/args.arm/"cases.csv")
    reference = pd.read_csv(benchmarks/args.reference/"cases.csv")
    summary = json.loads((benchmarks/args.arm/"summary.json").read_text())
    paired = frame.merge(reference, on=["unit_key", "household", "strategy"], suffixes=("", "_reference"),
                         validate="one_to_one")
    assert len(paired) == 240 and paired.validator_pass.all()
    paired["fci_difference"] = paired.fci_validator-paired.fci_validator_reference
    paired.to_csv(root/(args.arm+"_vs_reference.csv"), index=False)
    groups = []
    for group, data, tolerance in [(s, paired[paired.source == s], .02) for s in ("D1", "D2", "D3")] + [
            ("NIA<=20", paired[paired.nia_m2 <= 20+1e-8], .01)]:
        difference = float(data.fci_difference.mean())
        groups.append(dict(group=group, cases=len(data), mean_fci=data.fci_validator.mean(),
            reference_mean=data.fci_validator_reference.mean(), difference=difference,
            allowed_loss=tolerance, passes=difference >= -tolerance-1e-9))
    group_frame = pd.DataFrame(groups)
    group_frame.to_csv(root/(args.arm+"_quality.csv"), index=False)
    write_json(root/(args.arm+"_quality.json"), {"arm": args.arm, "reference": args.reference,
        "all_quality_checks_pass": all(g["passes"] for g in groups),
        "source_checks_pass": all(g["passes"] for g in groups[:3]),
        "small_unit_check_pass": groups[-1]["passes"], "groups": groups})
    witnesses = pd.read_csv(root/"witnesses.csv")
    runs = []
    for path in sorted(root.glob("*/summary.json")):
        record = json.loads(path.read_text())
        runs.append({k: record[k] for k in ("arm", "mode", "completed_cases", "mean_s1", "mean_s2",
                    "s2_improved_pairs", "s2_below_witness", "wall_time_s")})
    lines = ["# G2 round-2 self-review (in progress)", "",
        "The author delegates continuation and self-review and has paused uploads. This file is an engineering self-review, not a replacement for the immutable reviewer records.", "",
        "## Wall-flush lattice correction", "",
        "Stride is applied along the wall only for wall-backed furniture. Perpendicular flush coordinates remain eligible. Free-standing items still use both axes. Translated-wall tests exercise all four orientations.", "",
        f"Arm `{args.arm}` completed {summary['completed_cases']} cases in {summary['wall_time_s']:.3f} s; all {summary['validator_pass_cases']} layouts pass independent validation. Mean FCI is {summary['mean_fci']:.9f}.", "",
        group_frame.to_markdown(index=False, floatfmt=".6f"), "",
        "The full-anchor reference is the frozen earlier benchmark. At stride 0.10 m the wall correction is an identity; no full-anchor candidate changes. Numerical comparisons are provisional until R1 search checks finish. Positive differences are finite-budget outcomes, not dominance of a coarse domain.", "",
        "## Known-answer diagnostic fixtures", "",
        "Three hand-built rectangles have 9, 11 and 13 m² NIA. Each has a synthetic 0.8×0.8 m fixed pod and 0.4×0.6 m kitchen obstacle, deliberately separate from the D3 dwelling generator. These are algorithmic diagnostics, not habitable minimum dimensions or study-population observations. They must not enter A, K, minimum-area estimates or policy claims.", "",
        "The hand-written table's deployed body intersects the bed's night footprint. The six schedules pass the independent validator, and fixing their poses/states yields feasible CP models. Simultaneous deployment and S1 relabelling are rejected. H1 cannot claim sleep_1 from the requested sleep_2 bed under the unchanged capability rules; its lower bound explicitly omits sleep. H3 exercises the sleep/lounge transformation mechanism.", "",
        witnesses.to_markdown(index=False, floatfmt=".6f"), "",
        "Unconstrained searches never receive these witnesses as incumbents. Fixed-pose model tests establish expressiveness only, not search success.", "",
        "## Completed search diagnostics", "",
        pd.DataFrame(runs).to_markdown(index=False, floatfmt=".6f") if runs else "No completed search diagnostic yet.", "",
        "## Remaining acceptance checks", "",
        "- All six S2 diagnostic searches must reach their hand-written lower bounds; at least one diagnostic shell must have S2>S1.",
        "- Freeze and solve every pilot NIA<=22 plus 12 seed-selected D3 shells of 9–15 m²; use full anchors / 8 workers / 300 s for S1/S2 and all four households.",
        "- Select the size-dependent setting by the predeclared mean criteria; rerun any benchmarks affected by a search correction.",
        "- Reproject A and K; do not start formal A based on the superseded median rule.", "",
        "Reproduce: `python scripts/06_round2.py --mode prepare`; use the explicit mode/arm/worker/limit arguments in each run.json; `python scripts/06_round2_report.py --render`.", ""]
    Path("reports/G2_round2_self_review.md").write_text("\n".join(lines), encoding="utf-8")
    if args.render:
        households = parse_households(config["households"], config["furniture"])
        h = households["H3_couple_one_remote"]
        for area in (9, 11, 13):
            render_layout(mechanism_shell(area), mechanism_witness(area, h), config, h,
                          root/"witnesses"/f"shell_{area}_H3.png")
    print(json.dumps({"source_checks_pass": all(g["passes"] for g in groups[:3]),
                      "small_unit_check_pass": groups[-1]["passes"], "completed_diagnostic_runs": len(runs)}))


if __name__ == "__main__":
    main()
