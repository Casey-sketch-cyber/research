"""Render a dated round-3 status without publishing incomplete score averages."""
from datetime import datetime, timezone
import json
from pathlib import Path

import pandas as pd
import yaml

from fea.io import prepare_cli, start_run, write_json


def main():
    args = prepare_cli(__doc__).parse_args()
    start_run(args, "06_round3_status")
    if args.dry_run:
        print("Would render a dated status of complete evidence and pending work.")
        return
    root = Path("results/pilot/round3")
    execution = json.loads((root/"execution_status.json").read_text())
    queue = json.loads(Path("results/pilot/round2/pilot_refresh_status.json").read_text())
    rows = []
    for settings in queue["plan"]:
        directory = Path("results/pilot/benchmarks")/settings["arm"]
        manifest = json.loads((directory/"run.json").read_text())
        summary = directory/"summary.json"
        checkpoints = len(list(Path(manifest["cache"]).glob("*.json")))
        row = dict(arm=settings["arm"], expected_cases=manifest["expected_cases"],
                   saved_checkpoints=checkpoints, completed_validated_cases=0, status="running_or_queued")
        if summary.exists():
            s = json.loads(summary.read_text())
            assert s["completed_cases"] == s["expected_cases"] == s["validator_pass_cases"]
            row.update(completed_validated_cases=s["completed_cases"], status="complete")
        rows.append(row)
    observed = datetime.now(timezone.utc).isoformat(timespec="seconds")
    formal_progress = Path("results/expA/progress.json")
    formal_started = Path("results/expA/run.json").exists()
    snapshot = dict(observed_at_utc=observed, execution=execution, pilot_arms=rows,
                    ExpA_started=formal_started,
                    ExpA_progress=json.loads(formal_progress.read_text()) if formal_progress.exists() else None,
                    partial_score_means_published=False)
    write_json(root/"progress_snapshot.json", snapshot)
    check = json.loads((root/"implementation_checks.json").read_text())
    projection_path = root/"expA_projection.json"
    if not projection_path.exists():
        projection_path = root/"expA_provisional_projection.json"
    projection = json.loads(projection_path.read_text())
    kp = json.loads((root/"expK_projection.json").read_text())
    policy_path = Path("config/execution_policy.yaml")
    policy = yaml.safe_load(policy_path.read_text())["K_kit_design"] if policy_path.exists() else {}
    phase_status = "Formal A has started; see its run/progress records." if formal_started else "Formal A has not started at this snapshot."
    text = ["# G2 round-3 implementation and status", "", "Observed: "+observed, "",
        "The reviewer conditionally approves Phase 7. The author requests implementing this review. Main runs keep the two-side double-bed clearances; the approved one-side variant is A2 only. Review files are unchanged.", "",
        "## Fresh pilot and continuation", "", pd.DataFrame(rows).to_markdown(index=False), "",
        "Execution stage: `"+execution["stage"]+"`. "+phase_status+" Checkpoints are not completed-arm acceptance. No partial score means are reported.", "",
        "The continuation checks the source means, small-home mean, current code/configuration and measured runtime. It tries 2 workers / 60 s only for the reviewed larger-home quality fallback. Failed conditions stop A. Passing conditions launch the guarded A runner without another review stop, then generate A1 only after the complete A table passes solve acceptance.", "",
        "## Runtime evidence", "",
        f"A under the measured candidate setting: {projection['retained_hours']:.6f} projected hours including 15% margin; caps: {json.dumps(projection['caps'])}. This remains conditional on the hybrid quality comparison. Source/size cost calibration is in `expA_cost_calibration.csv`; absent small-source pilot cells use the full solve cap plus observed overrun.", "",
        "K uses the approved 120 s small-home budget, including full S0/S1/S2 evaluations for the time effect. The table is a conservative workload projection, not observed K runtime:", "",
        pd.DataFrame(kp["options"]).to_markdown(index=False, floatfmt=".3f"), "",
        ("K has not started. D-38 restores the two-day limit and withdraws the full grid. Plan the previously reported eight-kit exploratory scope: H1/H2, 30 training shells, 15 held-out shells and 15 real plans. Freeze the candidate grid and confirm cost in a K pilot. Per-solve budgets remain unchanged; the full-grid row is a rejected historical alternative."
         if policy.get("full_grid_enabled") is False else
         "K has not started. D-37 waives the two-day limit; the planned full grid and per-solve budgets are retained. A K pilot must calibrate actual costs. The smaller-scope rows are historical alternatives, not selected changes."
         if not policy.get("two_day_limit_enforced", True) else
         "K has not started. The full grid and the first two prescribed reductions still exceed 48 h. The reduced exploratory option is a proposal requiring a frozen candidate grid and a confirming K pilot; it is not a selected scope. Per-solve budgets are not shortened."), "",
        "## Implementation and remaining work", "",
        f"- {check['targeted_tests_passed']} targeted acceptance, continuation, launch-guard and paired-statistics tests pass. Numerical solver logic is unchanged.",
        "- A1 is implemented: paired form/time/total effects, S2>S1 shares, household × 2 m²-bin means, 1,000 unit-bootstrap resamples and 95% intervals. Source-specific tables accompany pooled tables. Single-unit bins have no CI. F4b uses stacked effects and separate form/total intervals; time intervals are in the table.",
        "- The F4b renderer was checked visually on completed pilot pairs in private scratch output; this is not a formal A figure or result.",
        "- A2 runs after A on every selected NIA<=20 unit, H3/H4, S0/S1/S2, retaining the small-home budget. It has not run. Main furniture defaults remain unchanged.",
        "- B1 is retained as a requirement for the future Exp. B runner: call the footprint policy alone; do not label the CP-SAT initialization portfolio as that baseline.",
        "- A3 requires the separate time effect in K and HK. Remaining Phase 7 FEA/adequacy analysis, layout review and literature screening are still due.", "",
        "## Reproduce", "",
        "`python scripts/06_round3_continue.py --launch-expA` waits for the already-launched fresh pilot queue, verifies acceptance and stops on unsupported conditions. `python scripts/06_round3_status.py` refreshes this snapshot. `python scripts/07_decomposition.py` requires complete accepted A results.", "",
        "The preserved benchmark configuration and the new approved project configuration are included. Their only difference is the inactive A2 declaration; no completed benchmark was silently relabelled with a new hash.", ""]
    Path("reports/G2_round3_status.md").write_text("\n".join(text), encoding="utf-8")
    print(json.dumps({"stage": execution["stage"], "observed_at_utc": observed, "pilot_arms": rows}))


if __name__ == "__main__":
    main()
