# Phase 10 — Grouped surrogate results

Geometry features and adjacency derive from interior polygon components and openings. The household indicator is the only non-geometric feature. D1 site/group IDs are exclusive to one split. D2 and generated D3 shells remain external tests.

| split       |   units |   groups |
|:------------|--------:|---------:|
| D1_test     |     172 |       70 |
| D2_external |     873 |      873 |
| D3_external |     510 |       30 |
| train       |     884 |      323 |
| val         |     180 |       69 |

## Held-out metrics

| test_set    | target    | model        |   mean_household_mae |   mean_household_spearman |
|:------------|:----------|:-------------|---------------------:|--------------------------:|
| D1_test     | fci_S0    | gbm_features |              0.04265 |                   0.40761 |
| D1_test     | fci_S0    | gnn_graph    |              0.04016 |                   0.36960 |
| D1_test     | fci_S0    | linear_area  |              0.05437 |                   0.28030 |
| D1_test     | fci_S0    | mlp_features |              0.06828 |                   0.17708 |
| D1_test     | fci_S2    | gbm_features |              0.02293 |                   0.18906 |
| D1_test     | fci_S2    | gnn_graph    |              0.01808 |                   0.34436 |
| D1_test     | fci_S2    | linear_area  |              0.02640 |                   0.23244 |
| D1_test     | fci_S2    | mlp_features |              0.05552 |                   0.13952 |
| D1_test     | saving_m2 | gbm_features |              1.56420 |                   0.44956 |
| D1_test     | saving_m2 | gnn_graph    |              1.76631 |                   0.39660 |
| D1_test     | saving_m2 | linear_area  |              1.88265 |                   0.33381 |
| D1_test     | saving_m2 | mlp_features |              1.80368 |                   0.31331 |
| D2_external | fci_S0    | gbm_features |              0.02146 |                   0.14836 |
| D2_external | fci_S0    | gnn_graph    |              0.01873 |                   0.11600 |
| D2_external | fci_S0    | linear_area  |              0.03509 |                   0.08452 |
| D2_external | fci_S0    | mlp_features |              0.19582 |                   0.04122 |
| D2_external | fci_S2    | gbm_features |              0.01461 |                   0.09473 |
| D2_external | fci_S2    | gnn_graph    |              0.01036 |                   0.15209 |
| D2_external | fci_S2    | linear_area  |              0.01802 |                   0.12680 |
| D2_external | fci_S2    | mlp_features |              0.17802 |                  -0.01230 |
| D2_external | saving_m2 | gbm_features |              0.67353 |                   0.12359 |
| D2_external | saving_m2 | gnn_graph    |              0.84605 |                   0.11588 |
| D2_external | saving_m2 | linear_area  |              1.12140 |                   0.15417 |
| D2_external | saving_m2 | mlp_features |              0.94429 |                   0.12516 |
| D3_external | fci_S0    | gbm_features |              0.15754 |                   0.75882 |
| D3_external | fci_S0    | gnn_graph    |              0.16510 |                   0.85579 |
| D3_external | fci_S0    | linear_area  |              0.19354 |                   0.88245 |
| D3_external | fci_S0    | mlp_features |              0.23303 |                 nan       |
| D3_external | fci_S2    | gbm_features |              0.15387 |                   0.41246 |
| D3_external | fci_S2    | gnn_graph    |              0.12883 |                   0.84444 |
| D3_external | fci_S2    | linear_area  |              0.15999 |                   0.08875 |
| D3_external | fci_S2    | mlp_features |              0.16717 |                 nan       |
| D3_external | saving_m2 | gbm_features |              2.67800 |                   0.23291 |
| D3_external | saving_m2 | gnn_graph    |              2.66691 |                   0.04212 |
| D3_external | saving_m2 | linear_area  |              3.18086 |                   0.37797 |
| D3_external | saving_m2 | mlp_features |              3.69370 |                   0.27756 |

The table averages the four household metrics within each test set. Full metrics and exact denominators are in metrics.csv. Inference time is median repeated prediction time per feature-ready unit for the three targets together, measured separately within each household and test set.

## Equivalent-area target support

| test_set    | household               |   n_total |   n_evaluated |   n_bound_only |   n_bound_violations |
|:------------|:------------------------|----------:|--------------:|---------------:|---------------------:|
| D1_test     | H1_single_commuter      |       172 |           155 |             17 |                   14 |
| D1_test     | H2_single_remote_worker |       172 |           167 |              5 |                    5 |
| D1_test     | H3_couple_one_remote    |       172 |           164 |              8 |                    4 |
| D1_test     | H4_parent_child         |       172 |           169 |              3 |                    0 |
| D2_external | H1_single_commuter      |       873 |           839 |             34 |                   32 |
| D2_external | H2_single_remote_worker |       873 |           873 |              0 |                    0 |
| D2_external | H3_couple_one_remote    |       873 |           872 |              1 |                    1 |
| D2_external | H4_parent_child         |       873 |           873 |              0 |                    0 |
| D3_external | H1_single_commuter      |       510 |           360 |            150 |                   67 |
| D3_external | H2_single_remote_worker |       510 |           380 |            130 |                   37 |
| D3_external | H3_couple_one_remote    |       510 |           331 |            179 |                   45 |
| D3_external | H4_parent_child         |       510 |           362 |            148 |                    0 |

The P1 static ruler is fitted to D1 training groups and applied consistently to all splits. Point errors use identified labels. Lower-bound cases retain a prediction and a bound-violation count. Source shifts and sparse positive, identified area gains limit the scope of these comparisons.

## Reproduction

Training, evaluation and figure export took 25.993 seconds. Run scripts/10_run_expC.py with the accepted phase-9 evidence and the reported software versions.
