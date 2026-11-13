# Phase 9 — Completed ablations

Audited 14,835 layouts in 4,945 three-strategy triplets. The final invocation took 0.708 hours. Exact accepted and saturated layouts are traced in the case table. Structurally unreachable empty-shell results: 552. They retain zero validator score and an explicit structural status.

The initial attempt stopped after 6.156 hours because the 0.20 m raster cannot represent the production 0.10 m small-home anchors. In that arm the smallest compatible stride is 0.20 m. The correction affected 32 triplets. The resumed run verified and reused 4,725 complete configuration-identical triplets with unchanged layout hashes. The coarse-grid contrast for affected units combines coarser collision and anchor grids.

Resolution and time-limit conditions share the fixed 50-unit sample. Item removal, walking width and clearance use the B pairs. H5 and all main households are also tabulated on the same distinct B units. F3 remains the accepted mirrored-access result on its separately defined small-home cohort.

## Largest matched differences in mean S2 FCI

| household               | ablation      | value           |   n |   paired_mean_fci_S2_change |   change_median_saving_m2 |   change_delta_a_min_m2 |   structural_unreachable_layouts |
|:------------------------|:--------------|:----------------|----:|----------------------------:|--------------------------:|------------------------:|---------------------------------:|
| H4_parent_child         | walking_width | 0.9             |  49 |                   -0.515063 |                 -2.133333 |              nan        |                               72 |
| H3_couple_one_remote    | walking_width | 0.9             |  50 |                   -0.476758 |                 -0.388000 |              nan        |                               69 |
| H1_single_commuter      | walking_width | 0.9             |  49 |                   -0.451355 |                  0.000000 |              nan        |                               63 |
| H2_single_remote_worker | walking_width | 0.9             |  52 |                   -0.384615 |                 -0.663866 |              nan        |                               57 |
| H4_parent_child         | resolution_m  | 0.2             |  50 |                   -0.085476 |                 -2.000000 |               -6.795651 |                                9 |
| H3_couple_one_remote    | resolution_m  | 0.2             |  50 |                   -0.071923 |                 -3.028600 |                5.495582 |                                9 |
| H1_single_commuter      | resolution_m  | 0.2             |  50 |                   -0.068466 |                  0.000000 |              nan        |                                9 |
| H2_single_remote_worker | resolution_m  | 0.2             |  50 |                   -0.057692 |                 -0.235294 |              nan        |                                9 |
| H1_single_commuter      | resolution_m  | 0.05            |  50 |                   -0.039788 |                 -0.400000 |              nan        |                                0 |
| H2_single_remote_worker | resolution_m  | 0.05            |  50 |                   -0.030000 |                  0.050420 |              nan        |                                0 |
| H3_couple_one_remote    | drop_one      | drop_leaf_table |  50 |                   -0.026702 |                 -1.175596 |               -6.171217 |                                0 |
| H4_parent_child         | drop_one      | drop_leaf_table |  49 |                   -0.019922 |                  0.000000 |               -6.180027 |                                0 |

Positive and negative results are retained. The pooled static curve from corrected main evidence is held fixed per household. Area summaries use identified positive gains and state support-limited counts separately. The median contrast compares the observed identified subsets. Adequate-area differences require two supported crossings. Both finite solver budgets and structural feasibility can contribute to observed differences.

## Reproduction

Run scripts/09_run_ablations.py in a fresh results directory, or use --resume-grid-fix with the archived recovery state. Run scripts/09_report_ablations.py to generate F9 and the threshold table from the accepted cases and corrected main scores.
