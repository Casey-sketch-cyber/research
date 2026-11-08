# Phase 7 review response and A1 evidence

E1--E4 and A1 are complete. Original A solve acceptance remains failed; the separate, reviewed evaluability analysis gate passes. No A re-solve, geometry repair or main numerical-configuration change was made.

E1: 2742 frozen units; 2619 retained and 123 excluded. All 31428 retained cases validate with zero strategy-ordering failures. All 116 structural-failure units fail condition (a). Five of seven all-zero D1 units fail (b); the two that pass E1 and 67 valid D3 zero cases remain.

E2: fixed-seed 20 excluded units: 8 rasterization, 1 genuinely narrow passage in the supplied drawing, 11 other/ambiguous topology, 0 confirmed conversion. This sample happened to contain only D1. These are audit classifications, not verified real-building causes. See [cause audit](expA_exclusion_causes.md).

E3: [composition table and histogram](expA_evaluability.md) report NIA, room count and source shifts. Retained D1/D2/D3 counts are 1236/873/510. Binning does not remove all within-bin selection bias. D3 is a designed grid, not a population sample.

E4: all retained units have four households by three strategies. Exclusions match E1 as whole units. A1 has 20 source/household groups, 1,000 paired unit bootstrap draws per group, supported f0 inversions, adequate-area fits, paired tests with Holm adjustments, F4b, and 33 revalidated, visually inspected layouts. Saving and decomposition figures show pooled, real-plan and designed-shell panels (S1).

## Interpretation limits discovered during A1

**H4 static catalogue ceiling:** S0 permits one static single bed, while H4 requires two separate sleep_1 tokens. A double-bed sleep_2 token cannot satisfy a sleep_1 demand. At least 8 of 28 weighted hours are unserved regardless of floor area, giving FCI <= 0.714285714, exactly the observed maximum. The H4 S0 adequate-area crossing is therefore unidentified, and its form gain combines catalogue availability with geometry. Do not interpret it as a time-sharing or housing-policy effect. Main counts and capability rules remain unchanged; see Q24.

Separate logistic models have 3 fitted ordering reversals, recorded in adequacy_fit_reversals.csv. These reflect independently fitted probability curves; all raw paired capacities retain strict ordering. Do not claim that time sharing harms capacity or force fitted crossings into order after seeing the results.

FEA is inversion of a pooled static reference, not a spatial counterfactual for the same household. A high-performing small unit or a low-performing large unit may yield a negative equivalent-area difference; flat or saturated curves can leave targets unsupported. The table below reports the uncensored median and censoring share together. No unconditional positive saving claim is supported merely by nonnegative FCI gains. Wide, unidentified and insufficient-bootstrap intervals are explicitly retained.

| pooling    | household               |   units |   uncensored |   right_censored_fraction |   lower_boundary_fraction |   median_saving_m2 |   negative_savings |
|:-----------|:------------------------|--------:|-------------:|--------------------------:|--------------------------:|-------------------:|-------------------:|
| D1         | H1_single_commuter      |    1236 |           31 |                    0.9749 |                    0.0170 |           -15.2918 |                 31 |
| D1         | H2_single_remote_worker |    1236 |           31 |                    0.9749 |                    0.0129 |           -24.6474 |                 30 |
| D1         | H3_couple_one_remote    |    1236 |          225 |                    0.8180 |                    0.0178 |             4.8816 |                 87 |
| D1         | H4_parent_child         |    1236 |           49 |                    0.9604 |                    0.0170 |           -14.7705 |                 42 |
| D2         | H1_single_commuter      |     873 |          873 |                    0.0000 |                    0.0229 |             4.3954 |                 25 |
| D2         | H2_single_remote_worker |     873 |          873 |                    0.0000 |                    0.0332 |             4.3783 |                 34 |
| D2         | H3_couple_one_remote    |     873 |          873 |                    0.0000 |                    0.0183 |             3.9847 |                 47 |
| D2         | H4_parent_child         |     873 |            7 |                    0.9920 |                    0.0023 |            13.5084 |                  3 |
| D3         | H1_single_commuter      |     510 |          156 |                    0.6941 |                    0.0314 |             0.0000 |                 46 |
| D3         | H2_single_remote_worker |     510 |          152 |                    0.7020 |                    0.0314 |             1.0000 |                 26 |
| D3         | H3_couple_one_remote    |     510 |          304 |                    0.4039 |                    0.0353 |             2.2624 |                 29 |
| D3         | H4_parent_child         |     510 |          227 |                    0.5549 |                    0.0353 |             1.0311 |                 23 |
| pooled     | H1_single_commuter      |    2619 |          207 |                    0.9210 |                    0.0069 |            -0.0000 |                 97 |
| pooled     | H2_single_remote_worker |    2619 |          212 |                    0.9191 |                    0.0069 |             0.0000 |                 86 |
| pooled     | H3_couple_one_remote    |    2619 |          539 |                    0.7942 |                    0.0080 |             2.0000 |                150 |
| pooled     | H4_parent_child         |    2619 |          253 |                    0.9034 |                    0.0080 |             1.0000 |                 72 |
| real_plans | H1_single_commuter      |    2109 |           51 |                    0.9758 |                    0.0180 |           -28.2293 |                 51 |
| real_plans | H2_single_remote_worker |    2109 |           60 |                    0.9716 |                    0.0081 |           -29.7322 |                 59 |
| real_plans | H3_couple_one_remote    |    2109 |          251 |                    0.8810 |                    0.0109 |             0.3817 |                121 |
| real_plans | H4_parent_child         |    2109 |           52 |                    0.9753 |                    0.0104 |           -14.8666 |                 45 |

## Continuation

A2 uses all evaluable units at NIA <=20 m2, H3/H4 and S0/S1/S2, with explicit one-side double-bed overrides and unchanged 120-second/four-worker full-anchor solves. Original sofa_bed clearance was front-only 0.50 m, so the override also changes direction for that family; this is not a uniform relaxation. The fixed local-left side and four rotations are stated, without an added mirrored family. Revalidate original layouts before using warm starts.

Then B (footprint greedy), D/R/ablations, C, reduced K, HK, literature and G3 follow the review order. K uses H1+H3 and retains the 48-hour limit. No intermediate reviewer stop is required. These future experiments are not claimed complete by this report.
