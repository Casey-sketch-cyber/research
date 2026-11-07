"""Publish a bounded progress snapshot without treating partial scores as results."""
from datetime import datetime, timezone
import json
from pathlib import Path

import pandas as pd

from fea.io import prepare_cli, start_run, write_json


def main():
    parser = prepare_cli(__doc__)
    args = parser.parse_args()
    config, _, _ = start_run(args, "06_round2_status")
    if args.dry_run:
        print("Would record completed results and saved checkpoint counts; no partial score averages.")
        return
    root = Path("results/pilot/round2")
    units = len(json.loads((root/"small_units.json").read_text())["units"])
    expected = units*len(config["households"]["main_households"])*2
    rows = []
    for arm in ("small_final_w8_t300", "small_final_w4_t120", "small_final_w1_t30"):
        directory = root/arm
        checkpoint_count = len(list((Path(config["paths"]["interim"])/"round2"/arm).glob("*.json")))
        summary_path = directory/"summary.json"
        row = dict(arm=arm, expected_cases=expected, saved_case_checkpoints=checkpoint_count,
                   status="running" if (directory/"run.json").exists() else "queued",
                   completed_validated_cases=0)
        if summary_path.exists():
            summary = json.loads(summary_path.read_text())
            frame = pd.read_csv(directory/"cases.csv")
            complete = len(frame) == expected == summary["completed_cases"]
            unique = not frame.duplicated(["unit_key", "household", "strategy"]).any()
            if not complete or not unique or not frame.validator_pass.all():
                raise ValueError("Completed arm failed the completeness/validation check: "+arm)
            row.update(status="complete", completed_validated_cases=expected)
        rows.append(row)
    result = dict(observed_at_utc=datetime.now(timezone.utc).isoformat(timespec="seconds"),
        frozen_units=units, expected_cases_all_arms=expected*3,
        completed_validated_cases=sum(r["completed_validated_cases"] for r in rows),
        saved_case_checkpoints=sum(r["saved_case_checkpoints"] for r in rows),
        all_three_arms_complete=all(r["status"] == "complete" for r in rows),
        partial_scores_published=False, arms=rows)
    write_json(root/"progress_snapshot.json", result)
    pd.DataFrame(rows).to_csv(root/"progress_snapshot.csv", index=False)
    print(json.dumps(result))


if __name__ == "__main__":
    main()
