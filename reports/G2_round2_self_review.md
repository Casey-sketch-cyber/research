# G2 round-2 self-review (formal-run acceptance pending)

The author delegates continuation and self-review. Publication instructions are recorded in DECISIONS.md. This file is an engineering self-review, not a replacement for the immutable reviewer records.

## Wall-flush lattice correction

Stride is applied along the wall only for wall-backed furniture. Perpendicular flush coordinates remain eligible. Free-standing items still use both axes. Translated-wall tests exercise all four orientations.

Arm `r2_wallflush_w1_s20_t30` completed 240 cases in 165.201 s; all 240 layouts pass independent validation. Mean FCI is 0.908132618.

| group   |   cases |   mean_fci |   reference_mean |   difference |   allowed_loss | passes   |
|:--------|--------:|-----------:|-----------------:|-------------:|---------------:|:---------|
| D1      |      96 |   0.944365 |         0.956454 |    -0.012089 |       0.020000 | True     |
| D2      |      72 |   0.970899 |         0.959809 |     0.011091 |       0.020000 | True     |
| D3      |      72 |   0.797056 |         0.797202 |    -0.000146 |       0.020000 | True     |
| NIA<=20 |      36 |   0.621890 |         0.636884 |    -0.014994 |       0.010000 | False    |

The full-anchor reference is the frozen earlier benchmark. At stride 0.10 m the wall correction is an identity; no full-anchor candidate changes. These earlier comparisons predate the final search corrections and cannot approve the current production setting. A fresh reference and size-dependent pilot are required. Positive differences are finite-budget outcomes, not dominance of a coarse domain.

## Known-answer diagnostic fixtures

Three hand-built rectangles have 9, 11 and 13 m² NIA. Each has a synthetic 0.8×0.8 m fixed pod and 0.4×0.6 m kitchen obstacle, deliberately separate from the D3 dwelling generator. These are algorithmic diagnostics, not habitable minimum dimensions or study-population observations. They must not enter A, K, minimum-area estimates or policy claims.

The hand-written table's deployed body intersects the bed's night footprint. The six schedules pass the independent validator, and fixing their poses/states yields feasible CP models. Simultaneous deployment and S1 relabelling are rejected. H1 cannot claim sleep_1 from the requested sleep_2 bed under the unchanged capability rules; its lower bound explicitly omits sleep. H3 exercises the sleep/lounge transformation mechanism.

| unit_key     |   nia_m2 | household            |   lower_bound |       tb | validator_pass   | h1_sleep2_does_not_satisfy_sleep1   | population_eligible   |
|:-------------|---------:|:---------------------|--------------:|---------:|:-----------------|:------------------------------------|:----------------------|
| mechanism:9  |        9 | H1_single_commuter   |      0.470899 | 2.800000 | True             | True                                | False                 |
| mechanism:9  |        9 | H3_couple_one_remote |      0.917577 | 2.800000 | True             | False                               | False                 |
| mechanism:11 |       11 | H1_single_commuter   |      0.523810 | 2.800000 | True             | True                                | False                 |
| mechanism:11 |       11 | H3_couple_one_remote |      0.936808 | 2.800000 | True             | False                               | False                 |
| mechanism:13 |       13 | H1_single_commuter   |      0.576720 | 2.800000 | True             | True                                | False                 |
| mechanism:13 |       13 | H3_couple_one_remote |      0.956038 | 2.800000 | True             | False                               | False                 |

Unconstrained searches never receive these witnesses as incumbents. Fixed-pose model tests establish expressiveness only, not search success.

## Completed search diagnostics

| arm                           | mode      |   completed_cases |   mean_s1 |   mean_s2 |   s2_improved_pairs |   s2_below_witness |   wall_time_s |
|:------------------------------|:----------|------------------:|----------:|----------:|--------------------:|-------------------:|--------------:|
| mechanism_final_w4_t120       | mechanism |                12 |  0.851647 |  0.941388 |                   3 |                  1 |    479.032614 |
| mechanism_original_w8_t300    | mechanism |                 2 |  0.725269 |  0.917577 |                   1 |                  0 |    409.723669 |
| mechanism_portfolio13_w4_t120 | mechanism |                 2 |  0.975269 |  0.975269 |                   0 |                  0 |    240.358316 |
| mechanism_probe_w4_t120       | mechanism |                 2 |  0.725269 |  0.725269 |                   0 |                  1 |    226.225759 |
| mechanism_verified_w4_t120    | mechanism |                12 |  0.838827 |  0.972526 |                   3 |                  0 |    268.341014 |
| small_final_w1_t30            | small     |               128 |  0.682489 |  0.707703 |                   9 |                  0 |    145.710469 |
| small_final_w4_t120           | small     |               128 |  0.697488 |  0.710809 |                   5 |                  0 |   1912.064505 |
| small_final_w8_t300           | small     |               128 |  0.696135 |  0.709112 |                   5 |                  0 |   8758.517807 |

Cross-run best independently validated scores (lower bounds, not one timed algorithm arm):

| unit_key     | household            |       S1 |       S2 |   best_observed_S2_minus_S1 |
|:-------------|:---------------------|---------:|---------:|----------------------------:|
| mechanism:11 | H1_single_commuter   | 1.000000 | 1.000000 |                    0.000000 |
| mechanism:11 | H3_couple_one_remote | 0.692308 | 0.994500 |                    0.302192 |
| mechanism:13 | H1_single_commuter   | 1.000000 | 1.000000 |                    0.000000 |
| mechanism:13 | H3_couple_one_remote | 0.975269 | 0.975269 |                    0.000000 |
| mechanism:9  | H1_single_commuter   | 1.000000 | 1.000000 |                    0.000000 |
| mechanism:9  | H3_couple_one_remote | 0.725269 | 0.917577 |                    0.192308 |

Do not infer physical S2 benefit from a weaker S1 search in one arm. Earlier valid S1 results remain evidence even when a later short search scores lower. In particular, the 13 m² fixture already has a stronger constant-state layout in an earlier arm. Mechanism success establishes representability and the ability to find sharing; it does not establish population-wide gains or optimality of every timed output.

## Small-home budget run status

| arm                 |   expected_cases |   saved_case_checkpoints | status   |   completed_validated_cases |
|:--------------------|-----------------:|-------------------------:|:---------|----------------------------:|
| small_final_w8_t300 |              128 |                      128 | complete |                         128 |
| small_final_w4_t120 |              128 |                      128 | complete |                         128 |
| small_final_w1_t30  |              128 |                      128 | complete |                         128 |

Snapshot observed at 2026-11-07T07:34:17+00:00. Saved checkpoints are not a completed-arm acceptance. No partial score means are reported.

## Completed budget comparison

| scope        | arm                 |   n_s2 |   mean_s2 |   difference_from_long |   mean_s1 |   s1_difference_from_long | within_001_of_long   |
|:-------------|:--------------------|-------:|----------:|-----------------------:|----------:|--------------------------:|:---------------------|
| all_16_units | small_final_w8_t300 |     64 |  0.709112 |               0.000000 |  0.696135 |                  0.000000 | True                 |
| all_16_units | small_final_w4_t120 |     64 |  0.710809 |               0.001697 |  0.697488 |                  0.001353 | True                 |
| all_16_units | small_final_w1_t30  |     64 |  0.707703 |              -0.001410 |  0.682489 |                 -0.013646 | True                 |
| NIA<=20      | small_final_w8_t300 |     60 |  0.692766 |               0.000000 |  0.678923 |                  0.000000 | True                 |
| NIA<=20      | small_final_w4_t120 |     60 |  0.692812 |               0.000046 |  0.678602 |                 -0.000321 | True                 |
| NIA<=20      | small_final_w1_t30  |     60 |  0.688216 |              -0.004550 |  0.661963 |                 -0.016960 | True                 |

Provisional small-home setting: 4 workers, 120 s, 0.10 m anchors. The predeclared rule compares S2 means with the long arm in both scopes. The long arm has 5 S2>S1 pairs; 1 of these gains is absent in the short arm. The 30-second arm's additional within-arm gains do not demonstrate a stronger physical effect: its S1 mean is lower. A medium-arm mean slightly above the long-arm mean is a finite-budget scheduling outcome, not method dominance. This selection does not authorize formal experiments; current source-quality and A/K runtime checks remain pending.

Independent saved-layout audit: 384/384 valid, 0 score mismatches, exact unit/household/strategy coverage. All layouts and their byte hashes are archived; see `completed_layout_audit.csv`. The validator is independent of solver constraint code but shares geometry rasterization.

## Remaining acceptance checks

- [x] All six S2 diagnostic searches reach their hand-written lower bounds; at least one shell has a demonstrated time-sharing improvement. Within-arm and cross-run comparisons are both retained above.
- [x] Freeze and solve every pilot NIA<=22 plus 12 seed-selected D3 shells of 9–15 m²; full anchors / 8 workers / 300 s for S1/S2 and all four households, with matched medium/short arms.
- [x] Independently revalidate and archive every completed small-home layout.
- [x] Apply the predeclared small-home mean-quality budget rule (provisional until hybrid acceptance).
- [ ] Rerun the full pilot reference and size-dependent candidate affected by the search correction; check source means.
- [ ] Reproject A and K; do not start formal A based on the superseded median rule.

Reproduce: `python scripts/06_round2.py --mode prepare`; use the explicit mode/arm/worker/limit arguments in each run.json; then run `06_round2_budget_report.py`, `06_round2_audit.py`, `06_round2_status.py` and `06_round2_report.py --render` under `scripts/`. After the round-3 metadata addition, pass `--base-config-snapshot results/pilot/round3/benchmark_base_config.json` to the historical round-2 layout audit.
