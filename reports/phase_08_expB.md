# Phase 8 — Algorithm comparison

- [x] Freeze 200 evaluable (unit, household) S2 pairs, stratified by source × within-source NIA tercile × household, with the fixed seed.
- [x] Match all 200 frozen pairs to corrected main evidence and independently revalidate their saved layouts.
- [x] Use only descending-footprint greedy as the greedy arm (B1); the service-aware portfolio remains CP-SAT initialization only.
- [x] Implement and test simulated annealing: same candidates, penalty objective, 20000 iterations × three restarts.
- [x] Run the three algorithms, independently validate each result, and report invalid outputs and runtime.
- [x] Benchmark runtime before launching the full comparison; keep actual algorithm budgets explicit.
- [x] Report source/size/household results and algorithm-validity checks.

Optional local LLM omitted to prioritize the required research. Corrected F1/F2 and mirrored F3 have passed full package acceptance; the earlier fixed-left A2 continuation gate is superseded. Sample allocation is balanced across the 36 source/tercile/household strata (five or six each); pooled B results describe this balanced benchmark, not the population mix. Within-source area ties stay together. No outcomes enter sample selection.

Sample preparation passed: 200 unique pairs across 36 strata; source counts D1=67, D2=68, D3=65. Selection uses E1 geometry and household labels only. The 12-pair runtime pilot passed all 36 outputs; the full 200-pair comparison passed. Evidence: results/expB/sample_manifest.json and sampling_allocation.csv. The sampling regression verifies input-row-order invariance, quota balance, unique pairs and exclusion of non-evaluable units.

Input preparation completed with scripts/08_check_expB_ready.py: 99 H3/H4 cases use corrected F1 re-solves and 101 H1/H2 cases retain verified original provenance. All 200 layouts validate both with their actual recorded configuration and the corrected main rules, with unchanged scores. The original sample bytes and stratification remain unchanged. Evidence is in readiness.json, corrected_main_reference.csv and reference_revalidation.csv. These reference checks are not new algorithm runs or fresh CP-SAT timing measurements. The independent baseline, pilot and full frozen sample are complete.

## Approved continuation and pre-run implementation plan

Latest phase07_review_F.md approves F1/F2/F3 and continuation to G3; P1 reporting was accepted alongside B. Frozen settings are in config/expB_algorithms.yaml. Run fresh standalone S2 CP-SAT with the reviewed per-unit budget, no historical layout supplied, and report the corrected A reference separately. This avoids treating historical shared-strategy runtime as fresh algorithm timing. Greedy uses only the existing descending-footprint policy with its full deterministic scan. Annealing uses the same candidate tables, all physical inventory instances, free per-slot states, 20000 proposals per restart and three restarts, initialized only by standalone greedy. Temperature decreases geometrically from 0.1 to 0.001; cost is negative reachable FCI plus 0.25 per geometric/access violation and a 1e-6 burden term. These defaults are frozen before reading B outcomes, not selected for winning comparisons.

Fast annealing geometry/reachability scoring shares solver-side primitives, while every new feasible best and every final output is checked with the separate validator. Any disagreement stops the run. Validate equivalence on deterministic synthetic layouts before a 12-pair source/household runtime pilot; retain pilot results as part of the fixed 200-pair run if the fingerprint matches. Report both preparation and algorithm time, cold per-algorithm end-to-end time, invalid scores and all termination statuses.

## Observed execution

Pilot completed 2026-11-11T03:07:33+00:00: 12 pairs / 36 outputs, zero invalid outputs, 10.669 measured minutes; every annealing case completed 60000 proposals. The full run started 2026-11-11T03:07:34+00:00 and preserves the exact fingerprint and all pilot checkpoints. The full stage completed 2026-11-11T04:07:34+00:00 in 0.999105 measured hours. All 200 triplets completed, with 600 valid outputs.

Seven preflight tests cover 120 synthetic random layouts against the independent validator, deterministic annealing, fixed proposal counts, invalid-output retention and pilot selection. Six further analysis/sampling/P1 tests pass (13 distinct related tests total). P1 has separately passed numerical and figure acceptance. The independent saved-layout audit passed at 2026-11-11T04:07:58+00:00. See the [benchmark results](phase_08_B_results.md) and [acceptance manifest](../results/expB/report_acceptance.json).
