"""Report measured A and bounded A2/K planning without a full-project ETA."""
import json
from pathlib import Path
import pandas as pd
import yaml
from fea.io import prepare_cli, start_run, write_json


def main():
    args=prepare_cli(__doc__).parse_args()
    start_run(args,"06_total_budget")
    if args.dry_run:
        print("Would distinguish historical A, active A2 cap and unmeasured H1+H3 K scope.")
        return
    root=Path("results/pilot/round3")
    policy=yaml.safe_load(Path("config/execution_policy.yaml").read_text())["K_kit_design"]
    require=lambda condition: condition or (_ for _ in ()).throw(ValueError("Unsupported active K policy"))
    require(not policy["full_grid_enabled"] and policy["two_day_limit_enforced"])
    scope=policy["reduced_scope"]
    require(scope["households"]==["H1_single_commuter","H3_couple_one_remote"])
    benchmark=Path("results/pilot/benchmarks/refresh_small_w4_s10_t120")
    cases=pd.read_csv(benchmark/"cases.csv")
    pilot=json.loads((benchmark/"summary.json").read_text())
    factor=max(1.,pilot["wall_time_s"]*pilot["concurrent_solves"]/cases.solve_time_s.sum())
    cap=pilot["time_limit_s"]+max(0.,cases.solve_time_s.max()-pilot["time_limit_s"])
    per_case=cap*factor/pilot["concurrent_solves"]/3600*1.15
    e1=pd.read_csv("results/expA/evaluability.csv")
    small=e1[e1.evaluable & (e1.nia_m2 <=20+1e-8)]
    a2_cases=len(small)*6
    a2_progress_path=Path("results/expA2/progress.json")
    progress=json.loads(a2_progress_path.read_text()) if a2_progress_path.exists() else {}
    completed=progress.get("completed_cases",0)
    a2_run_path=Path("results/expA2/run.json")
    a2_run=json.loads(a2_run_path.read_text()) if a2_run_path.exists() else {}
    # Historical grid has identical counts, but H3 runtime is not measured by H1/H2 evidence.
    historical=pd.read_csv(root/"expK_projection.csv").set_index("scope").loc["exploratory_8_kits_30_train_15_holdout_15_real_H1_H2"]
    require([scope[k] for k in ["candidate_kits","training_shells","heldout_shells","real_plans"]]==[8,30,15,15])
    a_run=json.loads(Path("results/expA/run.json").read_text())
    package=json.loads(Path("results/expA/analysis_package_acceptance.json").read_text())
    result=dict(A_completed_cases=a_run["expected_cases"],A_compute_hours=sum(row["wall_time_s"] for row in a_run["timing"])/3600,
        A_original_solve_acceptance_passed=False,A_analysis_package_passed=package["passed"],A_resolve_required=False,
        A2_status=a2_run.get("status","not_started"),A2_units=len(small),A2_expected_cases=a2_cases,A2_completed_cases=completed,
        A2_measured_hours=a2_run.get("wall_time_this_invocation_s",0)/3600 if a2_run.get("status")=="complete" else None,
        A2_planning_cap_hours=a2_cases*per_case,A2_remaining_cap_hours=max(0,a2_cases-completed)*per_case,
        A2_basis="120-second cap plus prior pilot overhead and 15% margin; not measured A2 duration or hard upper bound",
        K_scope=policy["planned_scope"],K_households=scope["households"],K_total_solves=int(historical.total_solves),
        K_count_based_cap_hours=float(historical.projected_hours_with_margin),K_hard_budget_hours=48,
        K_pilot_measured=False,K_basis="Same work counts as historical H1/H2 scope; H3 costs unmeasured. Runtime pilot required before kit execution.",
        K_if_over_budget=policy["if_runtime_pilot_exceeds_two_days"],
        full_project_remaining_hours=None,unmeasured=["B: footprint-only greedy, annealing, CP-SAT comparison","D/R and ablations","C surrogate training","K runtime pilot","HK and literature"],
        no_fixed_analysis_calendar_surcharge=True)
    write_json(root/"overall_runtime_budget.json",result)
    lines=["# Research execution budget","",
        "A completed 32,904 solves in 25.403 hours. Original solve acceptance remains failed; reviewed E1 filtering and A1 package acceptance now pass. No A re-solve is required.","",
        f"A2 covers {len(small)} evaluable small units × H3/H4 × three strategies = {a2_cases} solves. Status: {result['A2_status']}; completed {completed}. Planning cap: {result['A2_planning_cap_hours']:.3f} hours; remaining case-cap allowance {result['A2_remaining_cap_hours']:.3f} hours. These use the 120-second cap, prior main-pilot overhead and 15% margin, not measured A2 throughput; warm starts and early stopping may shorten runtime. They are not a promised completion date or strict upper bound.","",
        f"K follows D-39 (household update) and D-38 (budget): H1+H3, eight kits, 30 training shells, 15 held-out shells and 15 real plans. Identical work counts give {int(historical.total_solves)} solves and the historical cap-based allowance {float(historical.projected_hours_with_margin):.3f} hours. This is not a measured H3 projection. Freeze the grid and run the K pilot; if it exceeds 48 hours, reduce training shells 30 → 24 → 18 before dropping H3. The full grid remains disabled.","",
        (f"A2 measured completed runtime: {result['A2_measured_hours']:.3f} hours. No A2 solve time remains." if result["A2_measured_hours"] is not None else "A2 runtime is not final."),"",
        "B, the remaining ablations and C still require runtime calibration. D/R/HK reuse validated A evidence where applicable. No complete remaining experimental runtime is known. The previous 10–14-day calendar estimate is withdrawn; no arbitrary analysis-day reserve is added.","",
        "Phase-7 review permits continuation in order through A1, A2, B/D/R/ablations, C, K, HK and literature, without another stop before G3. G3/G4 review gates remain.",""]
    Path("reports/COMPUTE_BUDGET.md").write_text("\n".join(lines),encoding="utf-8")
    print(json.dumps(result))


if __name__=="__main__":
    main()
