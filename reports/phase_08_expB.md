# Phase 8 — Algorithm comparison

- [x] Freeze 200 evaluable (unit, household) S2 pairs, stratified by source × within-source NIA tercile × household, with the fixed seed.
- [ ] Use only descending-footprint greedy as the greedy arm (B1); the service-aware portfolio remains CP-SAT initialization only.
- [ ] Implement and test simulated annealing: same candidates, penalty objective, 20000 iterations × three restarts.
- [ ] Run the three algorithms, independently validate each result, and report invalid outputs and runtime.
- [ ] Benchmark runtime before launching the full comparison; keep actual algorithm budgets explicit.
- [ ] Report source/size/household results and algorithm-validity checks.

Optional local LLM omitted to prioritize the required research. A2 comparison must pass before launching B. Sample allocation is balanced across the 36 source/tercile/household strata (five or six each); pooled B results describe this balanced benchmark, not the population mix. Within-source area ties stay together. No outcomes enter sample selection.

Sample preparation passed: 200 unique pairs across 36 strata; source counts D1=67, D2=68, D3=65. Selection uses E1 geometry and household labels only. Algorithm runs have not started. Evidence: results/expB/sample_manifest.json and sampling_allocation.csv. The sampling regression verifies input-row-order invariance, quota balance, unique pairs and exclusion of non-evaluable units.
