"""Separate measured/provisional budgets from uncalibrated remaining experiments."""
import json
import math
from pathlib import Path

import pandas as pd
import yaml

from fea.io import prepare_cli, start_run, write_json


def main():
    args = prepare_cli(__doc__).parse_args()
    config, _, _ = start_run(args, "06_total_budget")
    if args.dry_run:
        print("Would sum A, A2 and the active K scope, and list uncalibrated work; no solves.")
        return
    root = Path("results/pilot/round3")
    projection_path = root/"expA_projection.json"
    if not projection_path.exists():
        projection_path = root/"expA_provisional_projection.json"
    projection = json.loads(projection_path.read_text())
    selected = root/"expA_selected_sample.csv"
    sample = pd.read_csv(selected if selected.exists() else "results/corpus/expA_sample.csv")
    small = sample[sample.nia_m2 <= 20+1e-8]
    benchmark = Path("results/pilot/benchmarks/refresh_small_w4_s10_t120")
    frame = pd.read_csv(benchmark/"cases.csv")
    summary = json.loads((benchmark/"summary.json").read_text())
    factor = max(1., summary["wall_time_s"]*summary["concurrent_solves"]/frame.solve_time_s.sum())
    cap = summary["time_limit_s"]+max(0., frame.solve_time_s.max()-summary["time_limit_s"])
    per_case_hours = cap*factor/summary["concurrent_solves"]/3600*1.15
    a2_cases = len(small)*2*3
    policy_path = Path("config/execution_policy.yaml")
    policy = yaml.safe_load(policy_path.read_text())["K_kit_design"] if policy_path.exists() else {}
    k_scope = policy.get("planned_scope", "full_grid")
    k = pd.read_csv(root/"expK_projection.csv").set_index("scope").loc[k_scope]
    if policy.get("full_grid_enabled") is False and k_scope == "full_grid":
        raise ValueError("Withdrawn full K grid cannot enter the active budget")
    quantified = [dict(experiment="A", solves=len(sample)*12, hours=projection["retained_hours"],
                        basis="measured pilot mean costs; conditional on quality acceptance"),
        dict(experiment="A2", solves=a2_cases, hours=a2_cases*per_case_hours,
             basis="all selected small units, H3/H4, S0/S1/S2; full 120 s cap plus pilot overhead, not measured A2"),
        dict(experiment="K_full" if k_scope == "full_grid" else "K_reduced_exploratory",
             solves=int(k.total_solves), hours=float(k.projected_hours_with_margin),
             basis="active planned scope at 120 s cap plus pilot overhead, not measured K")]
    pending = [
        dict(experiment="B", scope="200 pairs: footprint greedy, simulated annealing and CP-SAT; optional LLM separate", hours=None),
        dict(experiment="other_sensitivities", scope="drop-one items, clearance, walking width, raster resolution, solve budget and strict access", hours=None),
        dict(experiment="C", scope="four surrogate models and validation-only tuning; grids/runtime not yet calibrated", hours=None),
        dict(experiment="D_R_HK", scope="reuse A layouts where applicable; R reproduction and kit-HK extensions need their own checks", hours=None),
        dict(experiment="analysis_and_delivery", scope="FEA/adequacy/bootstrap analysis, literature, figures, rendering and review revisions", hours=None)]
    total = sum(row["hours"] for row in quantified)
    progress_path = Path("results/expA/progress_snapshot.json")
    progress = json.loads(progress_path.read_text()) if progress_path.exists() else None
    remaining_a = progress["remaining_hours_relative_to_prior_projection"] if progress else projection["retained_hours"]
    remaining_quantified = None if remaining_a is None else remaining_a+sum(row["hours"] for row in quantified[1:])
    # Explicit engineering scheduling allowances, NOT measured runtimes or research results.
    # These cover the remaining Phase 7–12 tasks from PROCEDURES, beyond A/A2/K solves.
    allowances = [
        dict(work="A metrics, statistical analysis and validation", low_days=.5, high_days=1.),
        dict(work="B algorithm implementation and comparisons", low_days=.5, high_days=1.),
        dict(work="other sensitivities plus D/R analysis", low_days=1., high_days=2.),
        dict(work="C surrogate models and HK scenario", low_days=1., high_days=2.),
        dict(work="remaining literature, figures, renders and package QA", low_days=2., high_days=3.)]
    planning = None if remaining_quantified is None else [
        remaining_quantified/24+sum(row[key] for row in allowances) for key in ("low_days", "high_days")]
    result = dict(quantified_budgets=quantified, quantified_subtotal_hours=total, K_scope=k_scope,
        full_K_grid_selected=k_scope == "full_grid", execution_policy_decision=policy.get("decision"),
        quantified_subtotal_days_at_continuous_execution=total/24, margin_included=.15,
        still_uncalibrated=pending, complete_total_hours=None,
        current_A_progress=progress, remaining_quantified_hours=remaining_quantified,
        unmeasured_engineering_planning_allowances=allowances,
        provisional_remaining_calendar_days=planning,
        rounded_planning_days=None if planning is None else [math.ceil(v) for v in planning],
        planning_conditions="Continuous execution and active implementation, reduced K scope, no major methodological rework. External reviewer waiting, author writing and submission are excluded. Allowances are judgement, not benchmark evidence or a delivery guarantee.",
        assumptions="Same current concurrency; serial allocation of the same compute budget. Not a minimum, hard upper bound or promised delivery date. No overlap deducted. Optional tasks and review delays are not quantified.",
        K_runtime_pilot_required=True)
    write_json(root/"overall_runtime_budget.json", result)
    table = pd.DataFrame(quantified)
    table["days"] = table.hours/24
    lines = ["# Research execution budget", "",
        ("D-38 supersedes D-37: the author restores K's two-day budget and withdraws the full grid. Plan the previously reported reduced exploratory scope: H1/H2, eight kits, 30 training shells, 15 held-out shells and 15 real plans. Freeze the candidate grid and confirm runtime before execution; per-solve budgets are unchanged. The rejected full-grid budget is excluded from the active subtotal."
         if k_scope != "full_grid" else
         "The author permits K to exceed two days (D-37). Preserve the planned full scope; no per-solve budget is reduced."), "",
        table.to_markdown(index=False, floatfmt=".3f"), "",
        f"Quantified subtotal: **{total:.3f} hours / {total/24:.3f} days** of continuous serial use at the current concurrency. These budgets already include a 15% margin. A is pilot-calibrated; A2 and K use the full per-solve cap and are not measured run durations. The subtotal is neither a minimum nor a complete project ETA.", "",
        "Still uncalibrated:", "", pd.DataFrame(pending)[["experiment", "scope"]].to_markdown(index=False), "",
        "## Provisional remaining delivery schedule", "",
        (f"Using the dated A progress snapshot, the remaining quantified solve budget is {remaining_quantified:.3f} h ({remaining_quantified/24:.3f} days). This uses the accepted pilot projection, not a linear extrapolation from early cases."
         if remaining_quantified is not None else "A has exceeded the prior projection; a revised remaining solve estimate is required."), "",
        "The following are explicit, unmeasured engineering planning allowances for work outside those solves, based on the remaining Phase 7–12 task list:", "",
        pd.DataFrame(allowances).to_markdown(index=False, floatfmt=".1f"), "",
        (f"Provisional planning range for a complete package ready for review: about **{math.ceil(planning[0])}–{math.ceil(planning[1])} further days**. This assumes continuous execution and active implementation, the reduced K scope, and no major methodological rework. External review waiting, author writing and submission are excluded. It is a planning allowance, not a measured total runtime or promised completion date."
         if planning is not None else "No updated complete-package date is claimed."), "",
        "Do not interpret this partial subtotal as the whole project's delivery date. Actual early stopping can shorten solves, while changed parametric domains, implementation, failures and review can extend the calendar. K's reduced scope is exploratory, with limited household and design-grid coverage; report those limits.", "",
        "## Review sequence", "",
        "G2 round 3 §3 explicitly permits starting A without another stop if fresh hybrid quality and A runtime checks pass. If the prescribed fallback still fails, stop and report. This does not abolish later G3/G4 reviews. The active K budget follows config/execution_policy.yaml; method validation and the K pilot remain required.", ""]
    Path("reports/COMPUTE_BUDGET.md").write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps(result))


if __name__ == "__main__":
    main()
