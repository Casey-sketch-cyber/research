"""Compare all frozen small-home budget arms without selecting favorable cases."""
from pathlib import Path
import json

import pandas as pd

from fea.io import prepare_cli, start_run, write_json


def main():
    parser = prepare_cli(__doc__)
    args = parser.parse_args()
    start_run(args, "06_round2_budget_report")
    if args.dry_run:
        print("Would compare the complete 16-unit S1/S2 budget arms and write provisional quality checks.")
        return
    root = Path("results/pilot/round2")
    arm_names = {"long": "small_final_w8_t300", "medium": "small_final_w4_t120", "short": "small_final_w1_t30"}
    frames, summaries = {}, {}
    keys = ["unit_key", "household", "strategy"]
    for label, arm in arm_names.items():
        summaries[label] = json.loads((root/arm/"summary.json").read_text())
        frames[label] = pd.read_csv(root/arm/"cases.csv")
        if len(frames[label]) != 128 or not frames[label].validator_pass.all() or frames[label].duplicated(keys).any():
            raise ValueError("The frozen 16-unit, four-household, two-strategy comparison must be complete and valid")
    if len({s["code_hash"] for s in summaries.values()}) != 1:
        raise ValueError("Budget arms used different numerical implementations")
    if len({s["inputs_hash"] for s in summaries.values()}) != 1:
        raise ValueError("Budget arms used different frozen inputs")
    combined = frames["long"][keys+["source", "nia_m2", "fci_validator", "tb", "solve_time_s"]].rename(
        columns={k: k+"_long" for k in ("fci_validator", "tb", "solve_time_s")})
    for label in ("medium", "short"):
        right = frames[label][keys+["fci_validator", "tb", "solve_time_s"]].rename(
            columns={k: k+"_"+label for k in ("fci_validator", "tb", "solve_time_s")})
        combined = combined.merge(right, on=keys, validate="one_to_one")
    if len(combined) != 128:
        raise ValueError("Unit-household-strategy keys do not match")
    combined.to_csv(root/"small_budget_case_comparison.csv", index=False)
    groups = []
    for scope, subset in [("all_16_units", combined), ("NIA<=20", combined[combined.nia_m2 <= 20+1e-8])]:
        for label in arm_names:
            s2 = subset[subset.strategy == "S2"]
            s1 = subset[subset.strategy == "S1"]
            difference = float((s2["fci_validator_"+label]-s2.fci_validator_long).mean())
            groups.append(dict(scope=scope, arm=arm_names[label], n_s2=len(s2),
                mean_s2=s2["fci_validator_"+label].mean(), difference_from_long=difference,
                mean_s1=s1["fci_validator_"+label].mean(),
                s1_difference_from_long=float((s1["fci_validator_"+label]-s1.fci_validator_long).mean()),
                within_001_of_long=difference >= -.01-1e-9))
    pd.DataFrame(groups).to_csv(root/"small_budget_quality.csv", index=False)
    gains = {}
    for label, frame in frames.items():
        pivot = frame.pivot(index=["unit_key", "household"], columns="strategy", values="fci_validator")
        gains[label] = pivot.S2-pivot.S1
    gain_table = pd.DataFrame(gains)
    gain_table["long_gain_missing_in_short"] = (gain_table.long > 1e-9) & (gain_table.short <= 1e-9)
    gain_table.reset_index().to_csv(root/"small_budget_transformation_gains.csv", index=False)
    medium_pass = all(row["within_001_of_long"] for row in groups if row["arm"] == arm_names["medium"])
    chosen = "medium" if medium_pass else "long"
    assessment = dict(provisional_small_arm=arm_names[chosen],
        num_workers=summaries[chosen]["num_workers"], time_limit_s=summaries[chosen]["time_limit_s"], anchor_stride_m=.1,
        selection_rule="Choose 4-worker/120-second full anchors if S2 mean is within 0.01 of 8-worker/300-second full anchors in both scopes; otherwise retain the long setting",
        long_improved_pairs=int((gain_table.long > 1e-9).sum()),
        long_gain_missing_in_short_pairs=int(gain_table.long_gain_missing_in_short.sum()),
        interpretation=("time-sharing gains observed in long-budget diagnostic cohort" if (gain_table.long > 1e-9).any()
                        else "No time-sharing gain found in this cohort; retain null finding and distinguish S1 compactness from S2 switching"),
        numerical_hash=summaries[chosen]["code_hash"], r2_hybrid_quality_pending=True,
        fixed_state_mean_gap_needs_attention=any(row["s1_difference_from_long"] < -.01-1e-9
            for row in groups if row["arm"] == arm_names[chosen]),
        runtime_reprojection_pending=True, formal_experiment_authorized_by_this_file=False)
    write_json(root/"small_budget_assessment.json", assessment)
    print(json.dumps(assessment))


if __name__ == "__main__":
    main()
