# Phase 11c — G3 review implementation

[G3 review](../reviews/G3_review.md) accepts the original G3 record and requires a follow-up review before Phase 12.

- [x] B1. Add the accepted production S2 scores as a fourth benchmark row on the same 200 pairs. Sum recorded S0, S1 and S2 solve times for each pair. Report paired effects and the cases below the best observed score.
- [x] K1. Revalidate and rescore the saved catalogue layouts with the configured size curves. Reoptimize catalogue S2 on the frozen K cohorts using the independently checked catalogue chain as starting layouts and the reviewed per-solve budget.
- [x] K1/K2. Rank the original eight vectors and the catalogue vector on the same 30 training shells. Check the selected kit on the original cohorts, include both the catalogue and the confirmed kit in the per-shell bespoke comparator, and report the nine-vector coverage and quality frontier.
- [x] HK. Rescore all saved catalogue layouts, evaluate the selected kits on the prescribed shells, and inspect the regenerated F10. Reuse a saved kit layout only when its geometry, quality objective and checks agree. Retain the original catalogue-at-full-quality comparison as a sensitivity.
- [x] Report the paired H3 switching contrast, post-hoc C adequacy AUC, the pooled H2 support limit and the 8 m² rule's sample coverage. Update the G3 conclusions after the revised results are verified.

The catalogue dimensions and quality factors come from the existing furniture configuration and design curves. The revised outputs use separate review directories so the accepted G3 acceptance records and original sensitivity can still be checked.
The [G3 response](GATE_G3_response.md) links the completed checks and outputs.

## B1 benchmark with the production pipeline

| Method | Pairs | Valid | Mean FCI | Median FCI | Mean recorded time (s) |
| --- | --- | --- | --- | --- | --- |
| Standalone CP-SAT | 200 | 100.0% | 0.8675 | 0.9615 | 38.451 |
| Footprint greedy | 200 | 100.0% | 0.8612 | 1.0000 | 3.465 |
| Simulated annealing | 200 | 100.0% | 0.9341 | 1.0000 | 104.118 |
| Production pipeline (portfolio warm start and shared incumbents) | 200 | 100.0% | 0.9428 | 1.0000 | 53.860 |

The production time sums the three recorded solves per pair. Standalone times include S2 preparation, execution and validation. Production attains the highest mean FCI and reaches the best observed value on 189/200 pairs. The difference from the best observed layout averages 0.0034 FCI. The table lists every pair with a positive shortfall.

| Unit key | Household | NIA (m²) | Production FCI | Best observed FCI | Shortfall | Method |
| --- | --- | --- | --- | --- | --- | --- |
| D3:9721e0ad95be14abb006 | H2_single_remote_worker | 12.00 | 0.6923 | 0.9231 | 0.2308 | Simulated annealing |
| D1:1d12938c558b1c792652 | H4_parent_child | 21.54 | 0.8571 | 0.9762 | 0.1190 | Simulated annealing |
| D3:d02a60a29c4334eb74a0 | H2_single_remote_worker | 12.00 | 0.6923 | 0.8077 | 0.1154 | Simulated annealing |
| D3:4643602621234f7cb06a | H1_single_commuter | 36.00 | 0.8995 | 1.0000 | 0.1005 | Footprint greedy |
| D1:0e4e7e1b22c313eba684 | H4_parent_child | 45.12 | 0.9762 | 1.0000 | 0.0238 | Simulated annealing |
| D1:9f340dff8c72fa84f689 | H4_parent_child | 30.49 | 0.9762 | 1.0000 | 0.0238 | Simulated annealing |
| D3:8a81259f1f982bf3f65f | H4_parent_child | 13.00 | 0.4048 | 0.4286 | 0.0238 | Simulated annealing |
| D3:3bb1e1e3d757302d5179 | H3_couple_one_remote | 14.00 | 0.9368 | 0.9560 | 0.0192 | Simulated annealing |
| D1:b9467fb0fd9fe89637b5 | H3_couple_one_remote | 16.78 | 0.9808 | 0.9945 | 0.0137 | Simulated annealing |
| D1:0e4e7e1b22c313eba684 | H3_couple_one_remote | 45.12 | 0.9945 | 1.0000 | 0.0055 | Simulated annealing |
| D1:78672aaa2fa3faf97f0f | H3_couple_one_remote | 46.31 | 0.9945 | 1.0000 | 0.0055 | Simulated annealing |

[Pair-level results](../results/g3_review/benchmark/production_pairs.csv) · [Production contrasts](../results/g3_review/benchmark/production_paired_effects.csv) · [Original standalone benchmark](phase_08_B_results.md)
