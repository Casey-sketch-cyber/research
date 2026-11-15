# Phase 11d — K3 kit comparison

[G3 round 2](../reviews/G3_review_round2.md) accepts PR #3 and requests an equal-effort comparison between the catalogue and H1_kit_02 and H3_kit_02 before Phase 12.

- [x] Keep the 30 frozen training shells per household and give each specified candidate one additional 120 s S2 solve, warm-started from its best validated saved layout on that shell.
- [x] Rank the nine vectors by mean validated FCIq, retaining one best layout per vector and shell. Recompute the coverage–quality frontier and the observed bespoke comparator.
- [x] Report paired FCIq differences, intervals, win/tie/loss counts and adequacy counts for the training and available transfer cohorts.
- [x] Add the validated larger H3 kit to the HK scenario. If it becomes the selected vector, use it in that role and retain the optimized catalogue as a comparison.
- [x] Update the G3 judgment, check the published evidence and submit the K3 follow-up for review.

The additional search is limited to the two candidates named in the review. Selection uses mean FCIq on the training shells. Adequacy is reported alongside that criterion at FCIq ≥ 0.95.

## Equal additional search

All 60 starting layouts and retained results passed independent validation. The additional solve stage took 20.82 minutes. Every original vector contributes one best validated result per training shell to the ranking and bespoke comparator. The training results and adequacy counts are in the revised G3 report.

| Household | Selected vector | Runner-up | Catalogue FCIq | Selected FCIq | Bespoke FCIq | Bespoke gain captured | Adequate: selected vs catalogue |
| --- | --- | --- | --- | --- | --- | --- | --- |
| H1 commuter | H1_kit_01 | catalogue | 0.7127 | 0.7141 | 0.7343 | 6.2% | 11/30 vs 13/30 |
| H3 couple | H3_kit_02 | catalogue | 0.6322 | 0.6344 | 0.6612 | 7.4% | 5/30 vs 2/30 |

| Household | Vector | Cohort | n | Mean FCIq: kit − catalogue [95% CI] | Kit higher / equal / lower | Adequate: kit vs catalogue | Adequate only on kit / only on catalogue |
| --- | --- | --- | --- | --- | --- | --- | --- |
| H1 commuter | H1_kit_02 | Training, matched extra search | 30 | -0.0284 [-0.0557, -0.0042] | 14 / 7 / 9 | 7 vs 13 | 0 / 6 |
| H3 couple | H3_kit_02 | Training, matched extra search | 30 | +0.0021 [-0.0336, +0.0279] | 21 / 3 / 6 | 5 vs 2 | 3 / 0 |
| H1 commuter | H1_kit_01 | Training, best saved | 30 | +0.0013 [-0.0153, +0.0200] | 8 / 7 / 15 | 11 vs 13 | 0 / 2 |
| H1 commuter | H1_kit_01 | Training, original confirmation | 30 | +0.0009 [-0.0156, +0.0195] | 8 / 7 / 15 | 11 vs 13 | 0 / 2 |
| H1 commuter | H1_kit_01 | Held-out shells | 15 | +0.0185 [-0.0166, +0.0551] | 3 / 9 / 3 | 7 vs 6 | 2 / 1 |
| H1 commuter | H1_kit_01 | Real plans ≤ 20 m² | 15 | +0.0036 [-0.0055, +0.0121] | 4 / 10 / 1 | 13 vs 13 | 0 / 0 |
| H3 couple | H3_kit_02 | Training, original confirmation | 30 | -0.0044 [-0.0395, +0.0220] | 20 / 3 / 7 | 4 vs 2 | 2 / 0 |
| H3 couple | H3_kit_02 | Held-out shells | 15 | -0.0242 [-0.0946, +0.0315] | 9 / 2 / 4 | 3 vs 0 | 3 / 0 |
| H3 couple | H3_kit_02 | Real plans ≤ 20 m² | 15 | +0.0066 [-0.0040, +0.0181] | 7 / 3 / 5 | 10 vs 8 | 2 / 0 |
| H1 commuter | H1_kit_01 | Hong Kong templates | 390 | -0.0389 [-0.0564, -0.0230] | 54 / 168 / 168 | 184 vs 246 | 5 / 67 |
| H3 couple | H3_kit_02 | Hong Kong templates | 390 | -0.0228 [-0.0345, -0.0120] | 184 / 71 / 135 | 154 vs 132 | 35 / 13 |

Not supported for H1. Mixed for H3, where H3_kit_02 leads by mean FCIq, with 5/30 adequate versus 2/30 and 7.4% of the observed bespoke gain. In the equal-extra-search comparison, H1_kit_02 trails the catalogue by 0.0284 mean FCIq and reaches adequacy on 7/30 shells versus 13/30. Across all nine vectors, H1_kit_01 has the highest observed mean when its accepted confirmation layouts enter the best-per-shell pool. Its paired mean difference is +0.0013 [-0.0153, +0.0200], with 11/30 adequate versus 13/30. Its confirmation-stage effort differs from the two designs in the matched extra-search comparison. The H1 evidence fails the joint adequacy and bespoke-gain claim. The paired training interval includes zero, so mean FCIq does not distinguish the H3 designs.

H3_kit_02 averages 0.6344 across the checked starting layouts and 0.6344 after the extra search. The starting layouts are the per-shell maxima across the accepted S2 search and confirmation records at the same dimensions.

## Hong Kong larger-kit row

The larger kit reaches adequacy on 154/390 couple shells, compared with 132/390 for the optimized catalogue. At 13–16 m² it reaches 51 of 120 versus 30. Below 13 m², mean FCIq is 0.448 versus 0.500. A_min is 15.39 m² [14.67, 16.19] for the larger kit and 16.12 m² [15.70, 16.57] for the optimized catalogue. The larger kit uses the independently revalidated HK layouts for the same dimensions and quality factors.

| NIA (m²) | Rescored catalogue S2 | Optimized catalogue S2 | Larger-item S2 |
| --- | --- | --- | --- |
| 8 | 0/30 | 0/30 | 0/30 |
| 9 | 0/30 | 0/30 | 0/30 |
| 10 | 0/30 | 0/30 | 0/30 |
| 11 | 0/30 | 0/30 | 0/30 |
| 12 | 0/30 | 0/30 | 0/30 |
| 13 | 0/30 | 0/30 | 4/30 |
| 14 | 2/30 | 2/30 | 7/30 |
| 15 | 9/30 | 10/30 | 16/30 |
| 16 | 16/30 | 18/30 | 24/30 |
| 17 | 23/30 | 23/30 | 24/30 |
| 18 | 24/30 | 25/30 | 26/30 |
| 19 | 26/30 | 27/30 | 26/30 |
| 20 | 26/30 | 27/30 | 27/30 |

[Area estimates](../results/g3_review_k3/hk_scenario_summary.csv) · [Paired layouts](../results/g3_review_k3/paired_cases.csv) · [Revised G3 report](GATE_G3.md)

## Reproduce

Run `python scripts/11d_run_k3.py` with the accepted saved layouts and corpus. Run `python scripts/11d_report_k3.py` to compute the numerical addendum. Use `python scripts/11d_report_k3.py --verify` to check the published evidence. The round-2 report is available at its reviewed commit. [PR #3](https://github.com/Casey-sketch-cyber/research/pull/3)
