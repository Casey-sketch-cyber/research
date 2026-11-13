# Phase 11 — Hong Kong scenario results

The 13 prescribed size levels from 8 to 20 m² contain 390 eligible shells from 390 generated geometry combinations. The scenario evaluates H1, H3 and H4. The solver and evidence checks took 8.790 hours in this invocation.

## Adequacy and supported area estimates

| household            | strategy   |   n_shells |   adequate_share |     a_min | a_min_status                      |   delta_a_min_vs_S0_m2 |   delta_ci_lo |   delta_ci_hi |   mean_shell_gap_reduction_m2 |
|:---------------------|:-----------|-----------:|-----------------:|----------:|:----------------------------------|-----------------------:|--------------:|--------------:|------------------------------:|
| H1_single_commuter   | S0         |        390 |          0.54615 |  13.39993 | identified                        |                0.00000 |       0.00000 |       0.00000 |                       0.00000 |
| H1_single_commuter   | S1         |        390 |          0.62564 |  12.36640 | identified                        |                1.03353 |       0.70015 |       1.43354 |                       0.42828 |
| H1_single_commuter   | S2         |        390 |          0.62564 |  12.36640 | identified                        |                1.03353 |       0.70015 |       1.43354 |                       0.42828 |
| H1_single_commuter   | S2_kit     |        390 |          0.47179 |  14.38169 | identified                        |               -0.98176 |      -1.53222 |      -0.49512 |                      -0.48248 |
| H3_couple_one_remote | S0         |        390 |          0.06667 | nan       | crossing_outside_observed_support |              nan       |     nan       |     nan       |                     nan       |
| H3_couple_one_remote | S1         |        390 |          0.27692 |  16.90829 | identified                        |              nan       |     nan       |     nan       |                     nan       |
| H3_couple_one_remote | S2         |        390 |          0.46667 |  14.43359 | identified                        |              nan       |     nan       |     nan       |                     nan       |
| H3_couple_one_remote | S2_kit     |        390 |          0.39487 |  15.38740 | identified                        |              nan       |     nan       |     nan       |                     nan       |
| H4_parent_child      | S0         |        390 |          0.10256 |  19.58003 | identified                        |                0.00000 |       0.00000 |       0.00000 |                       0.00000 |
| H4_parent_child      | S1         |        390 |          0.30769 |  16.53022 | identified                        |                3.04981 |       2.33658 |       3.58391 |                       2.47603 |
| H4_parent_child      | S2         |        390 |          0.31026 |  16.49120 | identified                        |                3.08884 |       2.37394 |       3.61039 |                       2.50305 |

Estimates use the prescribed functional-adequacy threshold and the reviewed in-support logistic crossings. Intervals resample shape templates with all observed sizes and matched strategies together. The area gap averages the shortfall to the estimated minimum over model shells. Undefined crossings and gap changes remain empty.

The by-size table gives denominators for each 1 m² level. The form/time table reports S1−S0 and S2−S1 under the catalogue separately. S2_kit uses the quality-aware design for H1 and H3 and independent FCIq checks.

## D6 coverage

| dc_eng     |   sdu_pop |   sdu_dh |   sdu_oq |   sdu_n |
|:-----------|----------:|---------:|---------:|--------:|
| Land total |    215709 |   107371 |    33658 |  108202 |

D6 contains territory and district counts. The missing household-size and floor-area distributions prevent census-based weights, so the adequacy and floor-area gaps describe the equally weighted shell scenario. Area is reported in square metres because the carbon factor remains unverified.

Reproduce with scripts/11_scenario_hk.py after the accepted reduced K and corrected main experiments.
