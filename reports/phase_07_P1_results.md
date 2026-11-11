# Phase 7 — P1 support-aware equivalent-area results

## Current reporting status

This analysis supersedes the area-gain tables, F4 area figure and area-gain summaries in the frozen F2 package. F1 scores, primary FCI effects, adequate-area analysis, layout checks and F3 sensitivity are unchanged. Historical F2 files retain their original hashes for provenance; their positive-uncensored area medians are not current identified estimates. Use results/expA_f1/analysis_p1/area_gain_summary.csv and F4_paired_area_gain_P1 for current reporting.

For unequal scores, an inverse at/below the lowest supported capacity or above the highest supported capacity makes the paired area difference a lower bound. Such observations are excluded from identified-positive medians. Equal scores still identify zero. Counts distinguish all support-limited improved units, strictly positive bounds and identified positive gains. The stored clamped comparison is diagnostic, not an identified estimate.

## Real-plan primary reference (D1+D2)

The last column is a lower bound on the median among all FCI-improved units; it is distinct from the median conditional on identified positive gains. Bound-only counts include cases whose known lower bound is zero; positive-lower-bound counts omit those cases. Thus FCI improvement does not always identify a positive area gain. In particular, single-person values must retain the ≥ sign and their support explanation.

| household               |   fci_improved |   identified_positive |   bound_only_improved |   positive_lower_bound | median_identified_positive_m2   | median_among_improved_lower_bound_m2   |
|:------------------------|---------------:|----------------------:|----------------------:|-----------------------:|:--------------------------------|:---------------------------------------|
| H1_single_commuter      |            159 |                     0 |                   159 |                    143 | not identified                  | ≥ 2.0000                               |
| H2_single_remote_worker |            184 |                   160 |                    24 |                     20 | 1.3333                          | ≥ 1.3333                               |
| H3_couple_one_remote    |            496 |                   448 |                    48 |                     36 | 6.2108                          | ≥ 6.2108                               |
| H4_parent_child         |            757 |                   721 |                    36 |                     26 | 5.0000                          | ≥ 5.0000                               |

H1 has no identified positive area gains on the real-plan median curve: its bound is the span between the lowest supported bin and full-capacity crossing. H2 has a mixture of identified and lower-bound cases. No missing smaller real plans are invented or extrapolated.

## Pooled-curve sensitivity for the same real plans

Refit the reference using pooled D1+D2+D3 units, then invert the same real-plan S0/S2 scores. This broadens observed NIA coverage through designed shells. The median-bin interpolation uses observed 2 m² bin midpoints, so its knot support is reported explicitly in f0_curves.csv and must not be confused with raw NIA endpoints. This sensitivity changes the reference population; generated small shells are not additional real homes.

| household               |   fci_improved |   identified_positive |   bound_only_improved |   positive_lower_bound |   median_identified_positive_m2 | median_among_improved_lower_bound_m2   |
|:------------------------|---------------:|----------------------:|----------------------:|-----------------------:|--------------------------------:|:---------------------------------------|
| H1_single_commuter      |            159 |                   158 |                     1 |                      1 |                          3.1    | ≥ 3.1000                               |
| H2_single_remote_worker |            184 |                   183 |                     1 |                      1 |                          2.5714 | ≥ 2.5714                               |
| H3_couple_one_remote    |            496 |                   496 |                     0 |                      0 |                          6.2857 | ≥ 6.2857                               |
| H4_parent_child         |            757 |                   757 |                     0 |                      0 |                          9.2    | ≥ 9.2000                               |

## Resampling, figures and boundaries

Each of 1000 paired unit resamples refits the static curve. Pooled-reference sensitivity resamples the entire pooled set and evaluates its resampled real-plan subset, preserving overlap between the reference and target samples. Both median-bin cumulative-maximum and mean-isotonic methods are retained. Source-specific and 2 m²-bin tables accompany pooled, real-plan and D3 tables. Identified-median intervals require at least two units, an identified point estimate and at least 80% supported bootstrap draws. Bound-statistic intervals describe uncertainty in the bound, not identification of the underlying gain.

F4 uses blue circles/intervals only for identified positive medians and orange triangles for lower-bound positive medians. Every panel states the corresponding counts. A missing blue point means no identified positive median.

P1 is analysis only. The main right/left access rules, F1/F3 layouts, E1 selection and all B inputs remain unchanged. The 0.10 m raster can lose oblique kitchen openings; support restrictions and source composition remain interpretation limits.

Reproduce with python scripts/07_p1_analysis.py, inspect the new figure, record its hash in config/p1_visual_review.json, and run with --finalize. Numerical and complete-package acceptance are distinct.
