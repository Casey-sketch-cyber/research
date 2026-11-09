# Phase 7 — A2 one-side double-bed sensitivity

## Completion and acceptance

PASS: 2088 cases across 348 evaluable small units. Saved-layout revalidation, exact sample/baseline matching, and within-A2 S2 >= S1 >= S0 all pass. No re-solve or numerical-code change was needed. Completion: 2026-11-09T07:45:07+00:00; measured search wall time 15.081857 hours, distinct from reporting time.

Valid zero cases: 37. Status counts: {"FEASIBLE": 494, "FEASIBLE_ACCESS_ADJUSTED": 123, "OPTIMAL": 493, "TIMEOUT_WITH_INCUMBENT": 978}. TIMEOUT_WITH_INCUMBENT denotes a valid retained solution, not proof of optimality or a missing result.

## Paired form and time effects

Form=S1-S0; time=S2-S1. Each contrast pairs the same unit and household across main and A2. Resample the paired unit vector 1,000 times; 95% percentile intervals describe this retained sample, not a housing population. All 2 m2 bins and source panels are in effect_summary.csv and F4c_A2.

| pooling    | household            |   n_units |   form_main |   form_A2 |   delta_form |   delta_form_ci_lo |   delta_form_ci_hi |   time_main |   time_A2 |   delta_time |   delta_time_ci_lo |   delta_time_ci_hi |
|:-----------|:---------------------|----------:|------------:|----------:|-------------:|-------------------:|-------------------:|------------:|----------:|-------------:|-------------------:|-------------------:|
| pooled     | H3_couple_one_remote |       348 |    0.099310 |  0.103170 |     0.003860 |          -0.004247 |           0.011541 |    0.068500 |  0.045638 |    -0.022862 |          -0.030750 |          -0.015109 |
| pooled     | H4_parent_child      |       348 |    0.120416 |  0.120177 |    -0.000239 |          -0.003045 |           0.002908 |    0.009476 |  0.008929 |    -0.000547 |          -0.001847 |           0.000958 |
| real_plans | H3_couple_one_remote |        18 |    0.036017 |  0.049447 |     0.013429 |          -0.017094 |           0.045794 |    0.134464 |  0.121645 |    -0.012818 |          -0.059529 |           0.028405 |
| real_plans | H4_parent_child      |        18 |    0.133598 |  0.136243 |     0.002646 |           0.000000 |           0.007937 |    0.003307 |  0.003307 |     0.000000 |           0.000000 |           0.000000 |
| D1         | H3_couple_one_remote |        18 |    0.036017 |  0.049447 |     0.013429 |          -0.018326 |           0.047195 |    0.134464 |  0.121645 |    -0.012818 |          -0.053726 |           0.028692 |
| D1         | H4_parent_child      |        18 |    0.133598 |  0.136243 |     0.002646 |           0.000000 |           0.007937 |    0.003307 |  0.003307 |     0.000000 |           0.000000 |           0.000000 |
| D3         | H3_couple_one_remote |       330 |    0.102762 |  0.106100 |     0.003338 |          -0.005237 |           0.011748 |    0.064902 |  0.041492 |    -0.023410 |          -0.032877 |          -0.014693 |
| D3         | H4_parent_child      |       330 |    0.119697 |  0.119300 |    -0.000397 |          -0.003466 |           0.002852 |    0.009812 |  0.009235 |    -0.000577 |          -0.001876 |           0.000938 |

## Limitations and negative changes

Sample composition: {"D1": 18, "D3": 330}. There are no D2 small units; the real-plan panel is D1 only and D3 dominates pooled results.

There are 59 case-level FCI decreases. Of these, 9 original layouts remain geometrically valid under A2 but their rescored service changes; 50 are invalid under A2. Every returned layout scores at least as well as its original layout when that original is valid and rescored under A2. No negative observation was replaced or discarded.

The fixed local-left convention removes the opposite-side service target. In the frozen main validator, the union of both clearance strips is a service approach region; either reachable strip can provide service. Reserving clearance on two sides is distinct from requiring both sides reachable. Removing the reachable side can reduce service even when a layout remains geometrically valid. Four rotations do not introduce mirrored item families. The sofa-bed override additionally replaces front-only 0.50 m access. Thus A2 is a fixed-side variant, not a universal relaxation or an optimized choice of accessible side. Main configuration and all outcomes remain unchanged (Q25).

H4's static catalogue ceiling persists. S1-S0 gains must not be interpreted as pure time sharing; S2-S1 is reported separately. The time effect need not rise when static/form performance improves more strongly.

## Checklist and continuation

- [x] All selected small units, two households, three strategies, original solve budgets.
- [x] Complete solve and independent saved-layout checks, with frozen provenance.
- [x] Paired form/time changes, source and NIA-bin summaries, unit-bootstrap intervals.
- [x] Preserve and explain negative changes without tuning to an expected direction.
- [x] F4c_A2 visually inspected; analysis ready for publication and B continuation.

Reproduce with: python scripts/07_a2_report.py after the frozen A2 run. This report does not authorize a new geometry/access rule or claim later experiments complete.
