"""Distinguish historical A/A2, active F1/F3 requirements and unmeasured later work."""
import json
from pathlib import Path
import pandas as pd
import yaml
from fea.io import prepare_cli, start_run, write_json


def main():
    args=prepare_cli(__doc__).parse_args()
    start_run(args,"06_total_budget")
    if args.dry_run:
        print("Would report reviewed F1/F3 workloads and historical runtimes without inventing a full-project ETA.")
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
        A_original_solve_acceptance_passed=False,A_analysis_package_passed=package["passed"],A_resolve_required=True,
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
    f1_path=Path("results/expA_f1/run.json");f1=json.loads(f1_path.read_text()) if f1_path.exists() else {}
    p1=Path("results/expA_f1/progress.json");progress1=json.loads(p1.read_text()) if p1.exists() else {}
    n_small=len(small)*6;n_large=int(e1.evaluable.sum())*6-n_small
    result.update(A_A1_H3H4_status="superseded_pending_F1",A2_interpretation="historical_fixed_left_superseded_by_F3",
        F1_status=f1.get("status","not_started"),F1_expected_cases=n_small+n_large,F1_completed_cases=progress1.get("completed_cases",0),
        F1_nominal_full_caps_hours=(n_small*120/3+n_large*30/14)/3600,
        F1_measured_hours=f1.get("wall_time_this_invocation_s",0)/3600 if f1.get("status")=="complete" else None,
        F3_expected_cases=len(small)*3,F3_nominal_full_caps_hours=len(small)*3*120/3/3600,
        F1_F3_basis="Nominal full solve-cap allocations at frozen concurrency; excludes geometry/validation overhead and is not a measured duration or strict upper bound.")
    f3_path=Path("results/expA_f3/run.json");f3=json.loads(f3_path.read_text()) if f3_path.exists() else {}
    f3_progress_path=Path("results/expA_f3/progress.json");f3_progress=json.loads(f3_progress_path.read_text()) if f3_progress_path.exists() else {}
    result.update(F3_status=f3.get("status","not_started"),F3_completed_cases=f3_progress.get("completed_cases",0),
        F3_measured_hours=f3.get("wall_time_this_invocation_s",0)/3600 if f3.get("status")=="complete" else None)
    f2_package=Path("results/expA_f1/analysis/package_acceptance.json")
    result["F2_package_passed"]=f2_package.exists() and json.loads(f2_package.read_text())["passed"]
    if result["F1_status"]=="complete" and result["F2_package_passed"]:result["A_A1_H3H4_status"]="corrected_F1_F2_accepted"
    result["unmeasured"]=["F3 mirrored-access H3 duration"]+result["unmeasured"]
    write_json(root/"overall_runtime_budget.json",result)
    lines=["# Research execution budget","",
        f"Historical A completed {result['A_completed_cases']} solves in {result['A_compute_hours']:.3f} hours. Historical fixed-left A2 completed {completed} solves in {result['A2_measured_hours']:.3f} hours. The 2026-11-09 review supersedes H3/H4 main outcomes and the fixed-left A2 interpretation; these are not the runtime of the corrected experiments.","",
        f"F1 corrected H3/H4 cases: {result['F1_expected_cases']}. Status: {result['F1_status']}; recorded completed cases: {result['F1_completed_cases']}; measured hours when complete: {result['F1_measured_hours']}. F2 full package passed: {result['F2_package_passed']}. Small-home settings remain 120 seconds / four workers / three concurrent jobs; large-home settings remain 30 seconds / one worker / fourteen concurrent jobs. Nominal full solve-cap allocation: {result['F1_nominal_full_caps_hours']:.3f} hours, excluding geometry and validation overhead. This is neither measured remaining time nor a completion deadline.","",
        f"F3 follows F1 and F2: the same {len(small)} small units × H3 × three strategies = {result['F3_expected_cases']} solves. Nominal full solve-cap allocation: {result['F3_nominal_full_caps_hours']:.3f} hours, excluding overhead. Current status: {result['F3_status']}; recorded completed cases: {result['F3_completed_cases']}. The old fixed-left duration does not calibrate this mirrored run.","",
        f"K follows D-39 and D-38: H1+H3, eight kits, 30 training shells, 15 held-out shells and 15 real plans; {result['K_total_solves']} solves and historical count-based allowance {result['K_count_based_cap_hours']:.3f} hours. H3 costs remain unmeasured. Freeze the grid and run its pilot; if it exceeds 48 hours, reduce training shells 30 → 24 → 18 before dropping H3. The full grid stays disabled.","",
        "B, remaining ablations and C still need runtime calibration. D/R/HK reuse validated corrected evidence where applicable. Full remaining experimental time is unknown. The former 10–14-day calendar estimate is retired; no arbitrary analysis-day reserve is added.","",
        "Execution order: F1 → F2 → F3 → B → D/R/ablations → C → K → HK → literature → G3. The review requires no additional intermediate reviewer stop. G3/G4 remain.",""]
    Path("reports/COMPUTE_BUDGET.md").write_text("\n".join(lines),encoding="utf-8")
    print(json.dumps(result))


if __name__=="__main__":
    main()
