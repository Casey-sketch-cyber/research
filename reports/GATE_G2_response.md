# Gate G2 response

> Current round-2 status takes precedence: see [G2_round2_self_review.md](G2_round2_self_review.md). The earlier median-based production selection and runtime projections below are historical. The author has delegated self-review and reauthorized sanitized uploads; formal experiments await the updated quality and runtime checks.

Status: READY_FOR_CLAUDE_REVIEW. Reviewed baseline: 67af2ee; requested corrections: a228786. No Phase 7, K or R experiment was started. The author requests another review even if the continuation criteria pass.

## Outcomes

- Fixed pilot: 240 cases; 240 valid and 0 invalid. Independent FCI agreement: 100%.
- Ordering violations after sharing: 0; missed feasible downward improvements: 0.
- Anchor comparison at 8 workers / 60 s: mean FCI change (0.20 m minus 0.10 m) -0.019849; source means {"D1": -0.062106, "D2": 0.00931, "D3": 0.007333}. Passing the median selection rule does not establish equal quality for every source or case.
- Selected configuration versus the corrected full-anchor 8-worker reference: mean FCI change -0.047510; by source {"D1": -0.11443, "D2": 0.005113, "D3": -0.010908}. See selected_reference_comparison.csv; these finite-budget quality changes remain part of this review even if every continuation criterion passes.
- Valid zero-service cases: 0; causes: {}.
- Tests: 79 passed; measured test runtime 57.75 s.
- All five reviewer continuation criteria pass: **True**. Criterion results: {"budget": true, "explained_valid_zeros": true, "ordering": true, "structural_failures": true, "validator_agreement": true}.

## M1–M3 and M8: geometry and access

D3 tries ordered near-corner/wall placements, rejects bodies touching the entrance keepout, checks continuous 0.90 m disc connectivity to the main floor and pod door, then tests empty raster access. Parameter keys are retained. Rejected combinations are labelled generator_infeasible and excluded before sampling. The mapping has 510 parameter combinations and 0 generator exclusions; see d3_regeneration_mapping.csv. Its new_sample flag records the uncapped geometry redraw; retained_analysis_sample records the later budget selection. All original pilot D3 parameters are preserved.

Kitchen rooms are walkable, not furnishable; fixtures and sanitary bodies remain blocked. Kitchen reachability is tested separately. A wall-aware morphological close adds circulation across source seams up to 0.15 m, without changing NIA. The complete D1/D2 blocker-type audit confirms that the loaded source blockers are polygonal; a separate raster regression preserves zero-thickness internal separators. In the full uncapped sample, 746 of 2742 units gain reachability to previously existing cells. Detailed staged pilot diagnostics are in fixed_service_diagnostic.csv; remaining valid zeros and explicit evidence are in zero_service_diagnoses.csv. The 0.30 m gap probe in that file is diagnosis only and is never used to optimize scores.

No unit fails empty fixed-service access.

Solver and validator independently erode by an even/odd discrete disc, traverse reference positions and dilate by the same disc to recover covered access area. Exact 0.60/0.50 m and 0.90/0.80 m corridor boundaries, bed-side strips, rotated cases and irregular obstacles are tested. Both still share rasterization; validation therefore does not independently establish source geometry correctness.

## M4–M5 and M9: search and throughput

| arm | workers | concurrency | seconds_per_100 | median_FCI | mean_FCI | valid | median_iterations | first_positive_valid_s |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| w8_s10_t60 | 8 | 1 | 1600.882 | 1.0 | 0.909685 | 240 | 0.0 | 0.028 |
| w8_s20_t60 | 8 | 1 | 789.806 | 1.0 | 0.889835 | 240 | 0.0 | 0.03 |
| w1_s20_t60 | 1 | 14 | 160.82 | 1.0 | 0.868661 | 240 | 0.0 | 0.032 |
| w2_s20_t60 | 2 | 7 | 170.158 | 1.0 | 0.889503 | 240 | 0.0 | 0.032 |
| w4_s20_t60 | 4 | 3 | 288.768 | 1.0 | 0.890858 | 240 | 0.0 | 0.031 |
| w1_s20_t30 | 1 | 14 | 87.454 | 1.0 | 0.862174 | 240 | 0.0 | 0.032 |

Selected arm: **w1_s20_t30**. Worker quality criterion met: True. The fastest 60 s worker arm must be within 0.01 median FCI of both corrected 8-worker references; 30 s is retained only if faster and within 0.01 of that selection as well. All distributions include invalid cases at zero, and individual case scores are published. The 8-worker exhaustive arm isolates corrected-geometry full anchors; the second arm isolates 0.20 m anchors. Collision and access remain 0.10 m. The full-anchor check remains required in resolution sensitivity.

Paired 0.20 m minus 0.10 m anchor differences, with 8 workers and 60 s held fixed:

| source | strategy | n | mean_full_FCI | mean_coarse_FCI | mean_delta_FCI | min_delta_FCI | max_delta_FCI | improved | reduced |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| D1 | S0 | 32 | 0.906794 | 0.829654 | -0.077139 | -0.692308 | 0.115385 | 3 | 11 |
| D1 | S1 | 32 | 0.981284 | 0.926695 | -0.054589 | -0.384615 | 0.0055 | 1 | 10 |
| D1 | S2 | 32 | 0.981284 | 0.926695 | -0.054589 | -0.384615 | 0.0055 | 1 | 10 |
| D2 | S0 | 24 | 0.893773 | 0.922161 | 0.028388 | -0.153846 | 0.692308 | 3 | 1 |
| D2 | S1 | 24 | 0.992827 | 0.992598 | -0.000229 | -0.153846 | 0.076923 | 3 | 2 |
| D2 | S2 | 24 | 0.992827 | 0.992598 | -0.000229 | -0.153846 | 0.076923 | 3 | 2 |
| D3 | S0 | 24 | 0.703106 | 0.736934 | 0.033828 | -0.019231 | 0.576923 | 4 | 1 |
| D3 | S1 | 24 | 0.84425 | 0.838336 | -0.005914 | -0.167577 | 0.047619 | 4 | 2 |
| D3 | S2 | 24 | 0.84425 | 0.838336 | -0.005914 | -0.167577 | 0.047619 | 4 | 2 |

The complete 240 paired changes are in anchor_stride_comparison.csv. Positive differences reflect finite-budget search outcomes, not a claim that the coarser feasible set contains the finer one.

The greedy baseline sorts by descending footprint, takes the first improving feasible wall-adjacent pose, and is independently checked before hinting CP-SAT. Each search uses at most 3 s (also bounded by 15% of its total budget) for that warm start. Geometry constraints, lazy checks and validation share the total 30/60 s budget; CP search initially uses 5 s rounds so access can be checked promptly. A round returning UNKNOWN is retried with a doubled slice, up to the remaining total budget; it does not terminate the case early. After a solution-bearing round the slice resets to 5 s. Iterations are consequently not directly equivalent to the old single long search. First-valid timings refer to positive-FCI layouts, not the empty initial incumbent. The budget is checked between stages and solver calls; model construction and final validation are not preempted and may overrun it slightly. Runtime projections use the measured elapsed times.

In summary_by_group.csv, proved_bound_share records an actual early bound stop in the case's own search; final_at_proved_bound_share records whether the final, possibly shared layout attains the relaxed bound with zero burden. Timeout-with-incumbent uses recorded timeout status or elapsed time at the limit. These flags are not mutually exclusive after sharing; zero_service_fallback_share counts valid zeros specifically diagnosed as search_fallback.

All strategies exchange only layouts independently feasible under the receiving strategy. Scores and differences are reported after this exchange. The final validation audit searches again for missed downward improvements.

M9 uses geometric frontier witness rectangles. A cut requires at least one blocking body to stop covering its witness rectangle, or the failed assignment to be withdrawn, or its movable target pose to change. It removes ranges of poses, not one exact tuple. This guarded disjunction intentionally replaces unconditional reservation of every old bottleneck: that proposed shortcut could exclude a valid alternate route. Regression tests retain alternate routes/target relocation while excluding multiple blocking poses. Each restart is hinted with the previous layout minus offending items. A separate paired comparison holds revised geometry, greedy, lattice, round schedule and limits fixed on all 20 H1/S2 cases:

| mode | n | mean_fci | median_fci | mean_iterations | median_iterations | mean_first_cp_valid_s | mean_first_positive_including_greedy_s | valid | wall_time_s |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| exact_cut_cold_restart | 20 | 0.871693 | 0.97619 | 1.6 | 0.5 | 15.550257 | 0.401835 | 20 | 32.146382 |
| geometric_cut_refreshed_hint | 20 | 0.871693 | 0.97619 | 1.6 | 0.5 | 15.372106 | 0.320386 | 20 | 31.831774 |

First CP-valid time runs from case start to the first positive, independently checked CP-generated candidate. Greedy/incumbent checks do not trigger this event; their elapsed time is still included. Cases returning at an incumbent bound before CP have no such timing. Paired case records are in cut_comparison/cases.csv. The old pilot did not record time to first valid solution, so no retrospective timing is invented. The raw CP-SAT objective/bound describes its last solution-bearing search, not an optimality gap of a shared or retained layout.

## M6–M7: projections and sample rule

Measured parallel wall time calibrates source-specific mean solve costs, including preparation/queue overhead in the calibration factor. Exp. A projection with 15% margin: 9.510 h before caps, 9.510 h for the retained sample. Source counts: {"D1": 1348, "D2": 884, "D3": 510}. Cap actions: []. Every valid D3 shell at NIA ≤20 m² is preserved (330). D1/D2 floors and the 60 larger-D3 floor are enforced; no further reduction is authorized by this script.

Exp. K is projected separately: 67443 solves, 37.382 h with 15% margin under the full workload in expK_projection.csv. No K solve was run; changed parametric domains and FCIq may change build/search cost. Recheck on a K pilot before its 2-day time box. Within the planned two-day K time box: True. These are explicit workload projections, not observed K results or guarantees.

## Visual review and limitations

10 current layout renders and 5 preparation/contact views were inspected; paths, hashes and observations are in pilot_visual_review.json, including H1 S0/S2 at 8 and 12 m². Kitchen rooms have a light-grey hatch with a contrasting edge and an explicit legend. The presentation wrapper adjusts hatch contrast only, preserving the measured numerical implementation. Drawn lines guide through the covered area; they are not swept-motion trajectories. Multi-person access still uses one reachable point in the union of strips; the approved strict_access sensitivity is due on the future 200-instance Exp. B sample. Endpoint-only transformations, catalogue assumptions and the anchor-based window tie-break remain explicit limitations.

## Reproduction

After installing dependencies and supplying the pinned raw releases:

1. python scripts/03_build_corpus.py
2. python scripts/06_revision.py --prepare
3. python scripts/06_revision_pipeline.py
4. python scripts/06_cut_comparison.py
5. python scripts/06_revision_report.py --export --render --run-tests
6. Inspect the new images and update their factual visual-review record.
7. python scripts/06_revision_report.py --write-report

The optional prepare-pilot mode can overlap completed D1 / selected D2 conversion with later nonpilot conversion. Publication requires exact equality with the subsequent full-corpus pilot serialization. Cached benchmark cases may be resumed for results, but resumed throughput is explicitly ineligible for selection. Parallel CP-SAT incumbents may vary with scheduling despite a fixed seed. No FEA, minimum-area estimate or hypothesis verdict is inferred from this methods pilot.

## Round 2 — self-review continuation

The author has delegated continuation and self-review and reauthorized sanitized uploads. The current evidence, frozen diagnostic inputs, known lower bounds, mean-quality checks and remaining requirements are in [G2_round2_self_review.md](G2_round2_self_review.md), generated by scripts/06_round2_report.py. The preceding round-1 selection is historical and is not permission to start full Experiment A before the round-2 requirements pass. Reviews remain unchanged.

The three frozen small-home arms are now complete: 128 cases each, 384 in total.
Every archived layout passes independent revalidation with zero score mismatches;
case coverage and provenance also agree. The 4-worker/120-second/full-anchor arm
meets the predeclared S2 mean criterion in both the complete cohort and NIA<=20
subset. The long arm reveals five S2>S1 pairs, including one absent in the short
arm, triggering the size-dependent-budget rule. This is a provisional small-home
selection, not formal-experiment acceptance. The full source-quality pilot must
be refreshed after the search changes, followed by current A/K runtime projections.
All comparison rows, layouts and hashes are linked from the generated report.
