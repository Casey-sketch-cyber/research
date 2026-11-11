# Phase 7 — F3 mirrored double-bed access

## Completed run and independent checks

Completed 2026-11-10T16:17:08+00:00: 1044 cases, 348 original small units, H3 only, all three strategies. Measured search wall time: 8.397508 hours. All saved F3 layouts and all paired corrected-F1 layouts independently revalidate. Every physical left/right mapping was repeated and matches the run records; no better valid mapped incumbent was discarded.

Zero invalid cases; zero strategy-ordering failures; 22 valid zero-score cases. Status counts: {"FEASIBLE": 336, "FEASIBLE_ACCESS_ADJUSTED": 44, "OPTIMAL": 236, "TIMEOUT_WITH_INCUMBENT": 428}. A time limit with a valid incumbent is a completed budgeted solve, not proof of optimality.

## Paired form and time effects

Main denotes the corrected F1 result for the same unit and household. Form = S1-S0; time = S2-S1. Each of 1,000 bootstrap draws resamples the entire paired unit vector; 95% percentile intervals describe this retained benchmark. Single-unit bins have no confidence interval. The side choice is fixed for each physical item across slots and aliases share the original family inventory cap.

| pooling    |   n_units |   form_main |   form_F3 |   delta_form |   delta_form_ci_lo |   delta_form_ci_hi |   time_main |   time_F3 |   delta_time |   delta_time_ci_lo |   delta_time_ci_hi |
|:-----------|----------:|------------:|----------:|-------------:|-------------------:|-------------------:|------------:|----------:|-------------:|-------------------:|-------------------:|
| pooled     |       348 |    0.106288 |  0.108411 |     0.002123 |          -0.005046 |           0.009663 |    0.059737 |  0.047556 |    -0.012181 |          -0.020338 |          -0.004002 |
| real_plans |        18 |    0.071425 |  0.080889 |     0.009464 |          -0.035869 |           0.059127 |    0.112182 |  0.078145 |    -0.034036 |          -0.086235 |           0.014659 |
| D1         |        18 |    0.071425 |  0.080889 |     0.009464 |          -0.037710 |           0.057848 |    0.112182 |  0.078145 |    -0.034036 |          -0.082599 |           0.016335 |
| D3         |       330 |    0.108190 |  0.109913 |     0.001723 |          -0.005379 |           0.008859 |    0.056877 |  0.045888 |    -0.010989 |          -0.019170 |          -0.002305 |

Source and 2 m²-bin estimates, positive time-effect shares and intervals are in effect_summary.csv; F4c_F3 displays the changes. These are sensitivity results; the main configuration and corrected F1/F2 estimates are unchanged.

## Negative results and scope

Retained all 59 negative case-level changes: 49 corrected main layouts have no valid physical side mapping, and 10 have a valid mapping whose service score falls under the exact variant. The latter retain at least their independently rescored mapped score. Details and both layout hashes are in negative_changes.csv and layout_revalidation.csv.

The main right clearance strip was 0.50 m; the variant uses 0.60 m on the chosen side. Sofa beds change from front 0.50 m to side 0.60 m. Thus mirrored side choices fix the fixed-left restriction, but this exact variant remains neither a universal geometric superset nor a guarantee of larger time effects. Main access uses the union of the clearance strips as a reachable service region; the side retained can change service. Negative effects are preserved without tuning or replacement (Q28).

Sample composition: {"D1": 18, "D3": 330}. Real plans contain D1 only in this small-unit subset; D3 shells dominate pooled estimates. Findings do not establish population-wide gains. E1/E2/E3 selection and the 0.10 m raster limitation are unchanged. Original fixed-left A2 remains a superseded historical run.

## Reproduction and completion

Run python scripts/07_f3_report.py after the frozen F3 solve. This audits results without new solves. Inspect F4c_F3, record its exact hash in config/f3_visual_review.json, then run the same script with --finalize. report_acceptance.json is numerical acceptance; package_acceptance.json is the final figure-and-evidence gate. B follows on the frozen 200-pair sample using the main corrected configuration; it is not covered by this report.
