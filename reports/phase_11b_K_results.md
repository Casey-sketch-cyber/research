# Phase 11b — Reduced furniture-kit results

Validated 1,803 saved layouts. H1 and H3 used eight frozen dimension vectors each. The active sets comprise 30 training shells, 15 held-out shells and 15 real plans. All cases use the reviewed small-home time limit and anchor setting. The runtime pilot and its projected time-box checks are archived.

## S2 comparison

| household            | condition    | test_set   |   n |   fciq_mean |   adequate_share |   mean_fciq_gain_vs_catalogue_same_strategy |   a_min_m2 |   share_of_bespoke_gain |
|:---------------------|:-------------|:-----------|----:|------------:|-----------------:|--------------------------------------------:|-----------:|------------------------:|
| H1_single_commuter   | bespoke      | train      |  30 |    0.730600 |         0.400000 |                                    0.003263 | nan        |                1.000000 |
| H1_single_commuter   | catalogue    | heldout    |  15 |    0.723810 |         0.400000 |                                    0.000000 | nan        |              nan        |
| H1_single_commuter   | catalogue    | real       |  15 |    0.964727 |         0.866667 |                                    0.000000 | nan        |              nan        |
| H1_single_commuter   | catalogue    | train      |  30 |    0.727337 |         0.433333 |                                    0.000000 |  12.000000 |                0.000000 |
| H1_single_commuter   | flat_quality | heldout    |  15 |    0.662787 |         0.200000 |                                   -0.061023 |  14.609435 |              nan        |
| H1_single_commuter   | flat_quality | real       |  15 |    0.921411 |         0.733333 |                                   -0.043316 |  16.993408 |              nan        |
| H1_single_commuter   | flat_quality | train      |  30 |    0.673104 |         0.200000 |                                   -0.054233 |  14.026126 |              -16.621622 |
| H1_single_commuter   | kit          | heldout    |  15 |    0.738201 |         0.466667 |                                    0.014392 |  12.012629 |              nan        |
| H1_single_commuter   | kit          | real       |  15 |    0.962822 |         0.866667 |                                   -0.001905 | nan        |              nan        |
| H1_single_commuter   | kit          | train      |  30 |    0.713651 |         0.366667 |                                   -0.013686 |  12.556955 |               -4.194595 |
| H3_couple_one_remote | bespoke      | train      |  30 |    0.652157 |         0.166667 |                                   -0.005256 |  14.052387 |              nan        |
| H3_couple_one_remote | catalogue    | heldout    |  15 |    0.724172 |         0.200000 |                                    0.000000 |  14.272891 |              nan        |
| H3_couple_one_remote | catalogue    | real       |  15 |    0.891938 |         0.600000 |                                    0.000000 | nan        |              nan        |
| H3_couple_one_remote | catalogue    | train      |  30 |    0.657413 |         0.166667 |                                    0.000000 |  14.262614 |              nan        |
| H3_couple_one_remote | flat_quality | heldout    |  15 |    0.678788 |         0.000000 |                                   -0.045384 | nan        |              nan        |
| H3_couple_one_remote | flat_quality | real       |  15 |    0.857103 |         0.333333 |                                   -0.034835 | nan        |              nan        |
| H3_couple_one_remote | flat_quality | train      |  30 |    0.591076 |         0.033333 |                                   -0.066336 | nan        |              nan        |
| H3_couple_one_remote | kit          | heldout    |  15 |    0.669336 |         0.200000 |                                   -0.054836 |  14.272891 |              nan        |
| H3_couple_one_remote | kit          | real       |  15 |    0.887946 |         0.666667 |                                   -0.003993 | nan        |              nan        |
| H3_couple_one_remote | kit          | train      |  30 |    0.627817 |         0.133333 |                                   -0.029596 |  14.520546 |              nan        |

The quality-aware objective takes minimum reachable service quality and retains the storage capacity cap. Catalogue service quality is one. Flat-quality search uses ordinary FCI, and its evaluated FCIq uses the selected physical dimensions. The bespoke result is the best observed candidate per training shell, with the confirmed selected-kit layout available as an incumbent. Its scope is the frozen eight-vector grid and the recorded search budget.

## Separate form and time effects

| household            | condition    | test_set   |   n |   form_effect_fci |   time_effect_fci |   form_effect_fciq |   time_effect_fciq | base_config_hash                                                 |
|:---------------------|:-------------|:-----------|----:|------------------:|------------------:|-------------------:|-------------------:|:-----------------------------------------------------------------|
| H1_single_commuter   | catalogue    | heldout    |  15 |          0.023633 |          0.000000 |           0.023633 |           0.000000 | a358ba5619fc368359be0e05928c7114df40e06dd29c27a41f8ba1488ae71474 |
| H1_single_commuter   | catalogue    | real       |  15 |          0.012698 |          0.000000 |           0.012698 |           0.000000 | a358ba5619fc368359be0e05928c7114df40e06dd29c27a41f8ba1488ae71474 |
| H1_single_commuter   | catalogue    | train      |  30 |          0.077249 |          0.003527 |           0.077249 |           0.003527 | a358ba5619fc368359be0e05928c7114df40e06dd29c27a41f8ba1488ae71474 |
| H1_single_commuter   | flat_quality | heldout    |  15 |          0.071605 |          0.014109 |          -0.023633 |           0.002822 | a358ba5619fc368359be0e05928c7114df40e06dd29c27a41f8ba1488ae71474 |
| H1_single_commuter   | flat_quality | real       |  15 |          0.029277 |          0.000000 |          -0.021093 |           0.000000 | a358ba5619fc368359be0e05928c7114df40e06dd29c27a41f8ba1488ae71474 |
| H1_single_commuter   | flat_quality | train      |  30 |          0.079541 |          0.007937 |           0.021217 |          -0.009312 | a358ba5619fc368359be0e05928c7114df40e06dd29c27a41f8ba1488ae71474 |
| H1_single_commuter   | kit          | heldout    |  15 |          0.050441 |          0.003175 |           0.039436 |           0.001058 | a358ba5619fc368359be0e05928c7114df40e06dd29c27a41f8ba1488ae71474 |
| H1_single_commuter   | kit          | real       |  15 |          0.019048 |          0.010582 |           0.017778 |           0.005714 | a358ba5619fc368359be0e05928c7114df40e06dd29c27a41f8ba1488ae71474 |
| H1_single_commuter   | kit          | train      |  30 |          0.068254 |          0.000000 |           0.048042 |           0.000000 | a358ba5619fc368359be0e05928c7114df40e06dd29c27a41f8ba1488ae71474 |
| H3_couple_one_remote | catalogue    | heldout    |  15 |          0.099815 |          0.111172 |           0.099815 |           0.111172 | a358ba5619fc368359be0e05928c7114df40e06dd29c27a41f8ba1488ae71474 |
| H3_couple_one_remote | catalogue    | real       |  15 |          0.060804 |          0.140659 |           0.060804 |           0.140659 | a358ba5619fc368359be0e05928c7114df40e06dd29c27a41f8ba1488ae71474 |
| H3_couple_one_remote | catalogue    | train      |  30 |          0.121700 |          0.063462 |           0.121700 |           0.063462 | a358ba5619fc368359be0e05928c7114df40e06dd29c27a41f8ba1488ae71474 |
| H3_couple_one_remote | flat_quality | heldout    |  15 |          0.128679 |          0.122564 |           0.053955 |           0.130476 | a358ba5619fc368359be0e05928c7114df40e06dd29c27a41f8ba1488ae71474 |
| H3_couple_one_remote | flat_quality | real       |  15 |          0.082379 |          0.144284 |           0.022893 |           0.158644 | a358ba5619fc368359be0e05928c7114df40e06dd29c27a41f8ba1488ae71474 |
| H3_couple_one_remote | flat_quality | train      |  30 |          0.130015 |          0.059450 |           0.054998 |           0.057985 | a358ba5619fc368359be0e05928c7114df40e06dd29c27a41f8ba1488ae71474 |
| H3_couple_one_remote | kit          | heldout    |  15 |          0.056079 |          0.118277 |           0.056079 |           0.118277 | a358ba5619fc368359be0e05928c7114df40e06dd29c27a41f8ba1488ae71474 |
| H3_couple_one_remote | kit          | real       |  15 |          0.078313 |          0.140989 |           0.078313 |           0.140989 | a358ba5619fc368359be0e05928c7114df40e06dd29c27a41f8ba1488ae71474 |
| H3_couple_one_remote | kit          | train      |  30 |          0.093844 |          0.070458 |           0.093844 |           0.070458 | a358ba5619fc368359be0e05928c7114df40e06dd29c27a41f8ba1488ae71474 |

Adequate-area crossings are shown where identified within sample support. Rates at 8, 10 and 12 m² include their denominators. Any decrease versus the catalogue remains in the comparison. The H1 and H3 dimensions and qualities are supplied to the HK solver scenario.

Reproduce with scripts/11b_run_expK.py after the accepted Exp. C run.
