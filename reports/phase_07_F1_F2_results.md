# Corrected F1/F2 results and acceptance

F1 completed 15714 corrected cases in 18.498 hours; all passed independent validation, with zero ordering failures. Joined evidence has 31428 cases from 2619 evaluable units. Original raw results remain unchanged.

F2 completed all 20 household/evidence groups and both reference methods, using 1000 paired unit resamples. Both summary figures and the same 33 original examples were visually inspected; all saved examples were independently rescored again after the optional F3 family-count guard was added. Numerical analysis and complete-package acceptance remain separate records.

## Effect of the reviewed configuration correction

| household            | strategy   |   units |   old_mean_fci |   corrected_mean_fci |   old_max_fci |   corrected_max_fci |
|:---------------------|:-----------|--------:|---------------:|---------------------:|--------------:|--------------------:|
| H3_couple_one_remote | S0         |    2619 |        0.90797 |              0.91363 |       1.00000 |             1.00000 |
| H3_couple_one_remote | S1         |    2619 |        0.93297 |              0.93790 |       1.00000 |             1.00000 |
| H3_couple_one_remote | S2         |    2619 |        0.95153 |              0.95414 |       1.00000 |             1.00000 |
| H4_parent_child      | S0         |    2619 |        0.67162 |              0.89888 |       0.71429 |             1.00000 |
| H4_parent_child      | S1         |    2619 |        0.92103 |              0.93227 |       1.00000 |             1.00000 |
| H4_parent_child      | S2         |    2619 |        0.92430 |              0.93467 |       1.00000 |             1.00000 |

## Primary paired effects in real plans (D1+D2)

| household               | comparison   |   mean_difference |   mean_difference_ci_lo |   mean_difference_ci_hi |   share_improved |
|:------------------------|:-------------|------------------:|------------------------:|------------------------:|-----------------:|
| H1_single_commuter      | S2-S0        |           0.00865 |                 0.00719 |                 0.01006 |          0.07539 |
| H1_single_commuter      | S2-S1        |           0.00015 |                 0.00003 |                 0.00033 |          0.00190 |
| H1_single_commuter      | S1-S0        |           0.00850 |                 0.00706 |                 0.00997 |          0.07397 |
| H2_single_remote_worker | S2-S0        |           0.01080 |                 0.00910 |                 0.01260 |          0.08725 |
| H2_single_remote_worker | S2-S1        |           0.00007 |                 0.00000 |                 0.00018 |          0.00095 |
| H2_single_remote_worker | S1-S0        |           0.01072 |                 0.00903 |                 0.01251 |          0.08630 |
| H3_couple_one_remote    | S2-S0        |           0.02415 |                 0.02142 |                 0.02705 |          0.23518 |
| H3_couple_one_remote    | S2-S1        |           0.01117 |                 0.00944 |                 0.01297 |          0.14651 |
| H3_couple_one_remote    | S1-S0        |           0.01299 |                 0.01121 |                 0.01484 |          0.16501 |
| H4_parent_child         | S2-S0        |           0.02879 |                 0.02656 |                 0.03100 |          0.35894 |
| H4_parent_child         | S2-S1        |           0.00173 |                 0.00129 |                 0.00223 |          0.03509 |
| H4_parent_child         | S1-S0        |           0.02706 |                 0.02491 |                 0.02916 |          0.34993 |

Mean paired differences, bootstrap intervals and shares improved are primary. S2 ≥ S1 ≥ S0 is enforced through validated incumbent reuse, so Wilcoxon and rank-biserial statistics are only supplementary.

## Paired area gains in real plans

| household               |   share_fully_functional_S0 |   share_fci_improved |   share_known_positive_area_gain |   median_delta_ea_positive_uncensored_m2 |   share_delta_right_censored |
|:------------------------|----------------------------:|---------------------:|---------------------------------:|-----------------------------------------:|-----------------------------:|
| H1_single_commuter      |                     0.90801 |              0.07539 |                          0.06780 |                                  2.00000 |                      0.00000 |
| H2_single_remote_worker |                     0.89094 |              0.08725 |                          0.08535 |                                  1.33333 |                      0.00000 |
| H3_couple_one_remote    |                     0.72736 |              0.23518 |                          0.22949 |                                  6.21076 |                      0.00000 |
| H4_parent_child         |                     0.61024 |              0.35894 |                          0.35420 |                                  5.00000 |                      0.00000 |

The positive-area median conditions on positive uncensored gains; it is not the median over all homes or all possibly censored gainers. Tables also provide censoring bounds and lower-support flags. Equal capacity scores give zero paired gain. Pooled, real-plan, D1, D2 and designed-shell results remain separate; neither D3 nor the pooled mixture is a population sample.

## Single-person real-plan adequate-area support

| household               | strategy   |   n_units |   adequate_units |   min_observed_nia_m2 |   a_min_m2 | status                            |
|:------------------------|:-----------|----------:|-----------------:|----------------------:|-----------:|:----------------------------------|
| H1_single_commuter      | S0         |      2109 |             1958 |               16.7496 |        nan | crossing_outside_observed_support |
| H1_single_commuter      | S1         |      2109 |             2061 |               16.7496 |        nan | crossing_outside_observed_support |
| H1_single_commuter      | S2         |      2109 |             2063 |               16.7496 |        nan | crossing_outside_observed_support |
| H2_single_remote_worker | S0         |      2109 |             1895 |               16.7496 |        nan | crossing_outside_observed_support |
| H2_single_remote_worker | S1         |      2109 |             2050 |               16.7496 |        nan | nonincreasing_probability         |
| H2_single_remote_worker | S2         |      2109 |             2052 |               16.7496 |        nan | nonincreasing_probability         |

With almost all observed real homes adequate, minimum adequate area can be unidentified or outside observed support. These outcomes are retained as findings. D3 and pooled estimates are explicitly labelled in min_adequate_area.csv; independent logistic fits may show ordering reversals, which are retained.

## Limits and next experiment

The original E1 exclusions and E2 audit are unchanged: at the fixed 0.10 m raster, oblique kitchen openings can be lost. Valid zero-score units remain included. Old H3/H4 results and fixed-left A2 are historical; the old FEA-minus-own-area metric is retired.

F3 follows on the same 348 small units for H3 only, with mirrored left/right 0.60 m choices and shared family inventory. Main right strips were 0.50 m and sofa_bed used front 0.50 m, so the exact reviewed sensitivity is not a universal geometric superset. Original layouts are remapped and independently rescored; any losses are reported, not removed. Full K remains disabled; B and later phases follow the approved order.
