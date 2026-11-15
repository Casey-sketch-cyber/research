# Gate G3 — Functional capacity, equivalent area and furniture design

The study asks how much additional daily activity demand transformable furniture can serve in the same dwelling, how to express that difference as an equivalent area, and what the modeled results imply for compact-home screening and furniture design. The corrected primary analysis uses the accepted F1 inventory and the P1 paired inversion. This revision adds the K3 comparison requested in the second G3 review.

| Research hypothesis | Evidence at G3 |
| --- | --- |
| H1 · Gains peak in the smallest dwellings and shrink as area grows | Partly supported. Transformable furniture raises modeled coverage for a minority of real plans and some small and intermediate D3 shells. The largest median gains for the two-person households occur at intermediate sizes in the generated set. The observed size relationship is nonmonotonic. |
| H2 · Equal-area plans differ in capacity and area rules disagree with adequacy | Supported within the model. The couple and parent-and-child cases show substantial within-bin FCI variation. On real plans, the 30/45 m² comparator disagrees with modeled S2 adequacy on 55.7% and 52.7% of these cases, respectively. |
| H3 · A graph model reaches rank correlation of at least 0.80 on held-out sites | Not supported. D1 held-out GraphSAGE rank correlations range from 0.087 to 0.661 for S0 and 0.088 to 0.588 for S2. |
| H4 · A standard kit improves adequacy over the catalogue and captures most of the bespoke gain | Not supported for H1. Mixed for H3, where H3_kit_02 leads by mean FCIq, with 5/30 adequate versus 2/30 and 7.4% of the observed bespoke gain. |

Hypothesis IDs refer to the research claims. Household IDs in the results below refer to the commuter, remote worker, couple and parent-and-child schedules.

## Experiment A and the paired equivalent-area analysis

The corrected main run has 31,428 cases for 2,619 evaluable plans and shells. The primary real-plan population comprises 2,109 D1 and D2 floor plans. S0 uses fixed items, S1 uses a single state for each transformable item, and S2 permits scheduled state changes at common positions. FCI describes the fraction of weighted activity demand served by the modeled layouts. [Corrected F1/F2 results](phase_07_F1_F2_results.md) · [P1 area results](phase_07_P1_results.md)

| Household | Full FCI under S0 | Form S1−S0 [95% CI] | Time S2−S1 [95% CI] | S2 improved |
| --- | --- | --- | --- | --- |
| H1 commuter | 90.8% | 0.0085 [0.0071, 0.0100] | 0.0002 [0.0000, 0.0003] | 159/2109 (7.5%) |
| H2 remote worker | 89.1% | 0.0107 [0.0090, 0.0125] | 0.0001 [0.0000, 0.0002] | 184/2109 (8.7%) |
| H3 couple | 72.7% | 0.0130 [0.0112, 0.0148] | 0.0112 [0.0094, 0.0130] | 496/2109 (23.5%) |
| H4 parent and child | 61.0% | 0.0271 [0.0249, 0.0292] | 0.0017 [0.0013, 0.0022] | 757/2109 (35.9%) |

Most real plans reach full coverage with S0. The couple shows the largest mean time effect, 0.0112 FCI, alongside a form effect of 0.0130. The parent-and-child mean gain comes mainly from form. In the reviewed one-side bed-access sensitivity, the couple's pooled mean time effect changes by −0.0122 FCI [−0.0203, −0.0040] on 348 units. The variant reduces reserved space and removes the second access side. The real-plan subset has 18 units and its interval crosses zero. [F3 sensitivity](phase_07_F3_results.md)

The paired area gain is EA(S2) − EA(S0) using the same fitted static capacity curve for both inverses. The P1 rule records a lower bound for an unequal-score pair when an inverse hits the lower support boundary or a score exceeds the upper supported capacity. Equal scores identify zero.

| Household | Identified positive n | Bound-only improved n | Positive bound n | Identified positive median m² [95% CI] | Median lower bound among FCI gains m² |
| --- | --- | --- | --- | --- | --- |
| H1 commuter | 0 | 159 | 143 | — | ≥ 2.00 |
| H2 remote worker | 160 | 24 | 20 | 1.33 [0.75, 3.11] | ≥ 1.33 |
| H3 couple | 448 | 48 | 36 | 6.21 [4.20, 10.00] | ≥ 6.21 |
| H4 parent and child | 721 | 36 | 26 | 5.00 [4.20, 8.00] | ≥ 5.00 |

The median gain over all real-plan pairs is 0 m² for each household. The commuter's ≥ 2.00 m² bound among improved pairs follows from the real-plan curve's 17–19 m² span, and its positive identified median is unavailable. The remote-worker value of ≥ 1.33 m² also includes support-limited pairs. Inverting the same real-plan scores against the pooled reference gives identified positive medians of 3.10, 2.57, 6.29 and 9.20 m² across H1–H4. The pooled curve draws its added small-area support from generated shells.

The full 2 m²-bin table gives the P1 identified-positive median and interval, the count and median lower bound for improved pairs, and the all-pair median bounds in square metres and as a percentage of observed NIA. In the D3 8–10 m² bin, the couple's all-pair median is 0.75 m² or 9.2% of NIA. It rises to 7.32 m² or 49.8% in the 14–16 m² bin and reaches zero in the evaluated bins from 24 m² onward. For parent and child, the corresponding 8–10 and 18–20 m² medians are 0.69 and 6.00 m². These changes identify intermediate-size peaks in the modeled shells. [All household and area bins](../results/g3/area_summary.csv) · [Paired estimates](../results/expA_f1/analysis_p1/paired_equivalent_area.csv)

### Minimum adequate area

A_min is the fitted area where the modeled probability of FCI ≥ 0.95 reaches 0.5. ΔA_min is S0 A_min minus S2 A_min. Values and paired bootstrap intervals are in m².

| Population | Household | S0 A_min [95% CI] | S2 A_min [95% CI] | ΔA_min [95% CI] |
| --- | --- | --- | --- | --- |
| Real plans | H1 commuter | — | — | — |
| Real plans | H2 remote worker | — | — | — |
| Real plans | H3 couple | 28.83 [27.64, 29.91] | — | — |
| Real plans | H4 parent and child | 33.96 [33.21, 34.67] | 23.18 [21.27, 24.73] | 10.78 [9.15, 12.70] |
| D3 shells | H1 commuter | 14.24 [13.47, 15.03] | 12.56 [11.97, 13.14] | 1.68 [1.12, 2.38] |
| D3 shells | H2 remote worker | 15.68 [14.84, 16.65] | 12.04 [11.50, 12.47] | 3.63 [2.78, 4.77] |
| D3 shells | H3 couple | 19.93 [19.37, 20.44] | 14.40 [14.07, 14.73] | 5.53 [4.90, 6.12] |
| D3 shells | H4 parent and child | 22.76 [21.54, 24.07] | 16.32 [15.85, 16.77] | 6.45 [5.19, 7.75] |
| Pooled | H1 commuter | 11.48 [9.22, 13.38] | 10.46 [8.70, 11.87] | 1.01 [-0.44, 2.45] |
| Pooled | H2 remote worker | 14.59 [12.46, 16.27] | 8.27 (boundary-limited) | 6.32 (boundary-limited) |
| Pooled | H3 couple | 27.03 [26.19, 27.82] | 16.26 [15.20, 17.27] | 10.77 [9.66, 11.94] |
| Pooled | H4 parent and child | 31.14 [30.39, 31.90] | 20.98 [20.08, 21.83] | 10.16 [9.28, 11.06] |

Dashes denote unidentified crossings. The pooled H2 S2 crossing sits near the lower support edge and too few bootstrap fits support its interval. The D3 H2 comparison has a supported estimate of 3.63 m² [2.78, 4.77]. The complete table includes thresholds 0.90 and 1.00 and the status of every fit. [Adequate-area estimates](../results/expA_f1/analysis/min_adequate_area.csv)

## Experiment B — solver benchmark

| Algorithm | Paired cases | Valid | Mean FCI | Median FCI | Mean recorded time (s) |
| --- | --- | --- | --- | --- | --- |
| CP-SAT | 200 | 100.0% | 0.8675 | 0.9615 | 38.451 |
| Greedy footprint | 200 | 100.0% | 0.8612 | 1.0000 | 3.465 |
| Simulated annealing | 200 | 100.0% | 0.9341 | 1.0000 | 104.118 |
| Production pipeline (portfolio warm start and shared incumbents) | 200 | 100.0% | 0.9428 | 1.0000 | 53.860 |

Standalone S2 CP-SAT scores below annealing under the recorded budgets. It uses the internal greedy initializer. The hybrid used for A attains the highest mean FCI on the 200 matched pairs, with portfolio initialization and shared S0/S1/S2 incumbents. Its time sums the three recorded solve times. The standalone times cover S2 preparation, execution and validation. [Revised benchmark](phase_11c_G3_review.md#b1-benchmark-with-the-production-pipeline) · [Four-method summary](../results/g3_review/benchmark/algorithm_summary.csv)

| Paired comparison | Mean FCI difference [95% CI] | Higher / equal / lower |
| --- | --- | --- |
| Production minus standalone CP-SAT | +0.0753 [0.0592, 0.0948] | 112 / 88 / 0 |
| Production minus footprint greedy | +0.0816 [0.0608, 0.1046] | 82 / 117 / 1 |
| Production minus simulated annealing | +0.0087 [0.0016, 0.0160] | 17 / 172 / 11 |

Production equals the best observed score on 189 pairs. The mean shortfall is 0.0034 FCI over all 200 pairs. The largest difference is 0.2308 on a D3 remote-worker shell. A's valid FCI scores give achievable lower bounds under the tested budgets. The 11 shortfalls are listed with the scores and the winning method. [Paired effects](../results/g3_review/benchmark/production_paired_effects.csv) · [Case-level shortfalls](../results/g3_review/benchmark/production_shortfalls.csv)

## Experiment D — area rules and functional adequacy

Within the real-plan 26–28 m² bin, the couple's S0 FCI IQR was 0.205 (52 layouts). The parent-and-child IQR was 0.190 in the 24–26 m² bin (33 layouts). Both comparisons use the same household demands within a narrow NIA band.

The table uses FCI ≥ 0.95 as the modeled adequacy criterion. Each row has 2,109 real plans. FP and FN count area-pass/model-fail and area-fail/model-pass cases.

| Household | Strategy | 30/45 m² threshold | Disagreement (FP/FN) | 8 m² rule disagreement (FP/FN) |
| --- | --- | --- | --- | --- |
| H1 commuter | S0 | 30 | 14.5% (135/171) | 7.2% (151/0) |
| H1 commuter | S2 | 30 | 10.4% (39/180) | 2.2% (46/0) |
| H2 remote worker | S0 | 30 | 16.4% (186/159) | 10.1% (214/0) |
| H2 remote worker | S2 | 30 | 11.1% (52/182) | 2.7% (57/0) |
| H3 couple | S0 | 45 | 47.0% (52/940) | 16.8% (355/0) |
| H3 couple | S2 | 45 | 55.7% (25/1150) | 5.6% (118/0) |
| H4 parent and child | S0 | 45 | 40.5% (66/789) | 24.7% (520/0) |
| H4 parent and child | S2 | 45 | 52.7% (22/1090) | 8.3% (175/0) |

The smallest sampled real plan has 16.75 m² NIA, so only the D3 and Hong Kong shells cover the 8 m² boundary. The 30/45 m² rule disagrees mainly by rejecting functional plans for the two-person households. The continuous area-per-person and rooms-per-person comparisons retain all observed threshold sweeps. [D results](phase_09_D_results.md) · [Misclassification tables](../results/expD/confusion.csv) · [Within-bin dispersion](../results/expD/dispersion.csv)

## Supporting analysis R — room-level activity area

The 4 × 3 m envelope comparison gave 7.60 m² of daytime body-free area under both strategies for each single-person household. Across the generated 12 m² analogues, differences range from −0.52 to +1.38 m². The published example deducts clearances and gives conflicting furniture dimensions in its text and Figure 10. This comparison preserves the two area definitions and uses the catalogued dimensions in the modeled envelope. [Source comparison](phase_09_R_results.md) · [Bu and Che Mat](https://doi.org/10.13189/cea.2026.140514)

The real-plan median body-free area change was 0 m² in both single-person households. About 3.2% of commuter and 2.5% of remote-worker cases had a negative change. The predeclared 55–65% descriptive band contains zero cases across the main real-plan and D3 analyses. R links body-free area to paired equivalent area with the P1 support bounds retained. [R results and F11](../results/g3/figures/F11_supporting_R.pdf) · [Paired bridge](../results/expR/bridge.csv)

## Ablations and sensitivity

The sensitivity run independently checked 14,835 layouts in 4,945 strategy triplets. It retained 552 structurally unreachable empty layouts with a zero score. The original attempt took 6.156 hours before stopping at the coarse-grid incompatibility. The 0.20 m collision grid requires a 0.20 m anchor stride on the 32 affected small-home triplets. The resumed run checked and inherited 4,725 complete triplets and took 0.708 hours. These cases retain their original digests and code fingerprints. [Ablation report](phase_09_ablation_results.md) · [Run and recovery evidence](../results/ablations/) · [F9](../results/figures/F9.pdf)

The table gives the largest absolute change in mean S2 FCI within each condition family. Each change uses the same units and household as its production control. The gain median uses the identified positive subset in each condition, whose membership can change. Dashes mark an area contrast without two supported crossings. F9 uses separate horizontal scales for the panels.

| Condition | Household | Pairs | Change in mean S2 FCI | Change in gain median (m²) | Change in ΔA_min (m²) |
| --- | --- | --- | --- | --- | --- |
| Remove drop-leaf table | H3 couple | 50 | −0.0267 | −1.18 | −6.17 |
| Clearance × 1.2 | H3 couple | 50 | −0.0160 | −0.29 | +0.90 |
| Walking width 0.90 m | H4 parent and child | 49 | −0.5151 | −2.13 | — |
| Collision grid 0.20 m | H4 parent and child | 50 | −0.0855 | −2.00 | −6.80 |
| Time limit 60 s | H4 parent and child | 50 | −0.0102 | −0.50 | −2.15 |

The wider walking requirement produces the largest losses across all four primary schedules. For H4 it makes 72 layouts structurally unreachable in the 49 matched triplets. The effect therefore includes failures to reach fixed services in an empty unit. H5, the older-adult schedule with its own walking and clearance requirements, reaches 30.7% S0 and 36.0% S2 adequacy on the same 189 physical B units, with 255 structural flags across the strategies. The H5 comparison changes both the schedule and geometry requirements. The coarse-grid contrast combines raster and anchor changes for the affected units. Report the finite-budget time comparisons as observed, including nonmonotonic changes.

At τ = 0.90, 0.95 and 1.00, the real-plan H4 ΔA_min estimates are 10.37, 10.78 and 9.13 m². In D3 the H3 estimates are 5.86, 5.53 and 3.54 m². For H3 real plans both crossings are identified at τ = 1.00, where ΔA_min is 6.75 m². The other two real-plan H3 thresholds lack an identified S2 crossing. The separate F3 sensitivity above uses its own paired small-home sample. [All conditions](../results/ablations/summary.csv) · [Adequacy thresholds](../results/ablations/tau_sensitivity.csv)

## Experiment C — predicting capacity from a floor plan

The geometry-only inputs include the configured household indicator. The D1 group split contains 884 training units from 323 groups, 180 validation units from 69 groups, and 172 test units from 70 held-out groups. The 873 D2 and 510 D3 units are external sets. The area target uses the static curve fitted on D1 training units and the P1 definition. All hyperparameter choices use the validation groups. [C report](phase_10_C_results.md) · [Split and metrics](../results/expC/) · [F8](../results/figures/F8.pdf)

Each D1 result below is the mean of the household metrics. MAE is in FCI units for S0/S2 and m² for the paired gain. The full table gives MAE, RMSE, R², rank correlation, timing and denominators by household and test set.

| Model | S0 MAE / ρ | S2 MAE / ρ | Gain MAE / ρ | Median inference ms per unit |
| --- | --- | --- | --- | --- |
| Area-only linear | 0.054 / 0.280 | 0.026 / 0.232 | 1.883 / 0.334 | 0.00070 |
| Histogram gradient boosting | 0.043 / 0.408 | 0.023 / 0.189 | 1.564 / 0.450 | 0.02306 |
| Tabular MLP | 0.068 / 0.177 | 0.056 / 0.140 | 1.804 / 0.313 | 0.00264 |
| GraphSAGE | 0.040 / 0.370 | 0.018 / 0.344 | 1.766 / 0.397 | 0.00409 |

The timing column summarizes the feature-ready batch measurements across all test sets and households. GraphSAGE has the lowest mean D1 S0 and S2 MAE, but the held-out D1 ranking does not meet the prespecified ρ ≥ 0.80 criterion for any household. The H1–H4 S0 correlations are 0.087, 0.142, 0.588 and 0.661; S2 correlations are 0.088, 0.223, 0.479 and 0.588. The negative mean S2 R² values and the many nearly full labels caution against using low absolute errors alone to select a stock screening model.

In D2, GraphSAGE's S0 and S2 ranking is weaker still. In D3 the S0 rank correlation reaches 0.924 for the couple, and the S0 MAE is 0.135–0.192 across households. The generated-shell rank result coexists with larger prediction errors. Gain MAE uses identified pairs, including exact zeros. The graph model fell below the retained gain lower bound in 23 of 33 D1 test cases with bound-only labels. The commuter's gain rank is undefined where the identified labels are constant. [All 144 metric rows](../results/expC/metrics.csv) · [Predictions and support flags](../results/expC/predictions.csv)

Post-hoc adequacy ROC AUC uses the frozen continuous predictions to rank cases against FCI ≥ 0.95. On D1 held-out S0, GraphSAGE versus the area-only model scores 0.796 versus 0.732 for the couple and 0.888 versus 0.821 for parent and child. The original Spearman criterion governs H3. Single-outcome groups have no ROC AUC. [All AUCs and denominators](../results/g3_review/benchmark/c_adequacy_auc.csv)

## Experiment K — reduced kit design

The comparison applies the same size–quality curves to catalogue furniture and all kits. K3 gives H1_kit_02 and H3_kit_02 the same extra warm-started S2 step as the catalogue, with a 120 s cap on each of their 30 frozen training shells. Each vector keeps the best validated S2 layout per shell. Ties in FCIq are resolved by time burden when choosing a saved layout. The other six vectors per household use their saved results. Selection uses mean training FCIq and the tables show adequacy at FCIq ≥ 0.95 alongside it.

| Household | Selected vector | Runner-up | Catalogue FCIq | Selected FCIq | Bespoke FCIq | Bespoke gain captured | Adequate: selected vs catalogue |
| --- | --- | --- | --- | --- | --- | --- | --- |
| H1 commuter | H1_kit_01 | catalogue | 0.7127 | 0.7141 | 0.7343 | 6.2% | 11/30 vs 13/30 |
| H3 couple | H3_kit_02 | catalogue | 0.6322 | 0.6344 | 0.6612 | 7.4% | 5/30 vs 2/30 |

In the equal-extra-search comparison, H1_kit_02 trails the catalogue by 0.0284 mean FCIq and reaches adequacy on 7/30 shells versus 13/30. Across all nine vectors, H1_kit_01 has the highest observed mean when its accepted confirmation layouts enter the best-per-shell pool. Its paired mean difference is +0.0013 [-0.0153, +0.0200], with 11/30 adequate versus 13/30. Its confirmation-stage effort differs from the two designs in the matched extra-search comparison. The H1 evidence fails the joint adequacy and bespoke-gain claim. The paired training interval includes zero, so mean FCIq does not distinguish the H3 designs. The larger H3 kit ranks first by training mean FCIq and captures 7.4% of the observed bespoke gain. The observed adequacy gain accompanies a smaller than majority share of the bespoke gain.

Bespoke selects the best checked S2 layout per training shell across the nine evaluated vectors. The captured share uses the optimized catalogue as reference. This finite set and the tested search budgets define the achievable comparisons.

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

The paired percentile intervals resample 1,000 matched shell pairs for K and matched shape templates for Hong Kong. H1_kit_02 has saved training layouts. Where the selected non-catalogue vector has original confirmation layouts, the table gives its training, held-out and real-plan contrasts. The ranking uses training results, and the other cohorts measure transfer.

For H3, the larger kit has a 1.20 × 0.55 m desk, a 1.00 × 0.75 m table and a 1.40 m wardrobe frontage. All three scored furniture factors equal one. The narrower H3 catalogue desk and table have q = 0.90. The size–quality frontier gives mean plain FCI and mean item q for all nine vectors.

[K3 frontier](../results/g3_review_k3/design_frontier.csv) · [Paired results](../results/g3_review_k3/paired_effects.csv) · [Bespoke layouts](../results/g3_review_k3/bespoke_choices.csv) · [F12 dimensions](../results/g3/figures/F12_kit.pdf)

The first G3 comparison credited the catalogue at full quality. Its original outcomes are available as a sensitivity. [Full-quality sensitivity](../results/g3_review/kit/catalogue_full_quality_sensitivity.csv)

## Hong Kong — modeled adequacy across compact shell sizes

The scenario evaluates 390 equally weighted templates at 13 sizes from 8 to 20 m². All 3,510 saved catalogue layouts were rescored, including the 540 layouts at 17 and 19 m². The quality curves lowered 1,436 catalogue scores. Round 2 evaluated optimized catalogue layouts on the same 780 matched cases. K3 adds the previously evaluated kit layouts after independent revalidation. S0, S1 and S2 in this scenario refer to the rescored saved catalogue layouts. The optimized catalogue uses a quality-weighted S2 search at catalogue dimensions. K3 adds a separate larger-item S2 strategy for the couple.

Each size entry counts layouts with FCIq ≥ 0.95. A_min is the fitted 50% adequacy crossing in the observed size range. ΔA_min compares with S0. The 95% intervals resample shape templates with sizes and strategies paired. The final column gives mean shortfall to A_min across the equally weighted templates.

| Household | Strategy | 8 m² | 10 m² | 12 m² | Adequate overall | A_min m² [95% CI] | ΔA_min m² [95% CI] | Mean shell shortfall m² |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| H1 commuter | S0 | 0/30 | 0/30 | 4/30 | 54.6% | 13.40 [13.03, 13.73] | Reference | 1.34 |
| H1 commuter | S1 | 0/30 | 0/30 | 12/30 | 62.6% | 12.37 [12.00, 12.70] | 1.03 [0.70, 1.43] | 0.91 |
| H1 commuter | S2 | 0/30 | 0/30 | 12/30 | 62.6% | 12.37 [12.00, 12.70] | 1.03 [0.70, 1.43] | 0.91 |
| H1 commuter | S2 optimized catalogue | 0/30 | 0/30 | 12/30 | 63.1% | 12.30 [11.90, 12.64] | 1.10 [0.73, 1.53] | 0.88 |
| H1 commuter | S2 compact kit (selected) | 0/30 | 0/30 | 5/30 | 47.2% | 14.38 [13.83, 14.98] | -0.98 [-1.53, -0.50] | 1.82 |
| H3 couple | S0 | 0/30 | 0/30 | 0/30 | 6.7% | — | Reference | — |
| H3 couple | S1 | 0/30 | 0/30 | 0/30 | 16.2% | 18.57 [18.18, 19.02] | — | 4.71 |
| H3 couple | S2 | 0/30 | 0/30 | 0/30 | 32.3% | 16.33 [15.87, 16.83] | — | 3.00 |
| H3 couple | S2 optimized catalogue | 0/30 | 0/30 | 0/30 | 33.8% | 16.12 [15.70, 16.57] | — | 2.85 |
| H3 couple | S2 larger kit (selected) | 0/30 | 0/30 | 0/30 | 39.5% | 15.39 [14.67, 16.19] | — | 2.39 |
| H4 parent and child | S0 | 0/30 | 0/30 | 0/30 | 10.3% | 19.58 [18.78, 19.96] | Reference | 5.61 |
| H4 parent and child | S1 | 0/30 | 0/30 | 0/30 | 26.2% | 17.15 [16.64, 17.77] | 2.43 [1.76, 2.97] | 3.58 |
| H4 parent and child | S2 | 0/30 | 0/30 | 0/30 | 26.7% | 17.07 [16.58, 17.64] | 2.51 [1.86, 3.03] | 3.52 |

For the couple, the separate S1-to-S2 area difference under the common quality rule is 2.24 [1.66, 2.82] m². With the catalogue credited at full quality it is 2.47 [2.07, 2.97] m². The switching table gives the number of paired shape resamples supporting each interval.

The larger kit reaches adequacy on 154/390 couple shells, compared with 132/390 for the optimized catalogue. At 13–16 m² it reaches 51 of 120 versus 30. Below 13 m², mean FCIq is 0.448 versus 0.500. A_min is 15.39 m² [14.67, 16.19] for the larger kit and 16.12 m² [15.70, 16.57] for the optimized catalogue. The larger kit uses the independently revalidated HK layouts for the same dimensions and quality factors. The couple's S0 crossing is outside the modeled range.

[Round-2 F10](../results/g3_review/hong_kong/F10.pdf) · [Extended by-size table](../results/g3_review_k3/hk_adequacy_by_size.csv) · [Extended area estimates](../results/g3_review_k3/hk_scenario_summary.csv) · [Couple switching contrast](../results/g3_review/hong_kong/couple_switching.csv) · [Catalogue credited at full quality](../results/g3_review/hong_kong/catalogue_full_quality_sensitivity.csv)

D6 reports 215,709 residents and 107,371 households in 108,202 subdivided units, with 33,658 quarters containing subdivided units. The counts give territory context. Household-size and floor-area distributions are unavailable, so the results describe the modeled templates. [D6 coverage](schemas/D6.md) · [Territory counts](../results/scenario_hk/territory_context.csv)

## Literature screening and study position

The retrieved snapshot has 3,006 deduplicated titles, 947 retained titles and 407 available abstracts that were all read. The abstract decisions include nine overlap records, 253 related records, 13 known references and 132 irrelevant records. The ledger records 540 retained titles without an available abstract after the planned retrieval and follow-up, including the outcomes of 203 targeted Crossref checks. Eight records in the retrieved set received full-text checks, including seven overlap records. Two overlap records remain at abstract or project-summary access. The closest studies include room-level activity-area measures and circulation-based spatial compression. The present analysis contributes the paired whole-dwelling comparison at a common functional endpoint, with switching, daily demand and support limits made explicit. [Search scope, inclusion flow and positioning](novelty_check.md#systematic-confirmation-task-l--g3) · [Screening decisions](../results/literature/screened.csv) · [Full-text evidence](../results/literature/fulltext_checks_g3.json)

The screening used one reviewer and a bounded four-source retrieval. The remaining abstract and full-text gaps, source query caps and versions with distinct identifiers limit claims about coverage. Two supplemental source checks sit outside the retrieval flow. The G3 review adopts the positioning and cites Zeng et al. and Bu and Che Mat as the closest antecedents.

## Known issues for review

- The F1 primary estimand covers 2,619 units that pass the predeclared empty-geometry check. The 123 excluded units remain documented; the 94 valid zero-score layouts remain in the corrected evidence. Generated shells supply most of the small-area coverage and are interpreted separately from actual floor plans. [Evaluability and coverage](phase_07_F1_F2_results.md)
- The equivalent-area ruler is sample and household specific. A support-bound result states an inequality. The old FEA-minus-own-area measure is superseded. Capacity crossings require data on both sides of the adequacy transition; finite samples and saturation leave some crossings and intervals unidentified.
- FCI and FCIq represent scheduled service under modeled geometric and household assumptions. The results do not measure residents' use, switching compliance, observed satisfaction or statutory compliance. Independent validators test the returned layouts. Solver budgets and the selected furniture inventory still constrain the available layouts.
- The mirrored-access check is a paired robustness comparison on its own sample. It changes the available access targets as well as the reserved space. The room-level R comparison uses an approximate envelope and a body-free-area measure; the source uses a clearance-inclusive measure.
- The Hong Kong area gaps refer to the prescribed modeled shells. The published D6 counts do not supply the joint household and floor-area distribution needed for city-scale totals. Any claim about territory-wide floor area or carbon would need further data.

Open questions and unresolved limitations are tracked in [QUESTIONS.md](QUESTIONS.md). The [evidence manifest](../results/g3/evidence_manifest.json) binds the phase acceptance receipts, the numeric outputs and reviewed figures. Check K3 and the original evidence with `python scripts/11d_report_k3.py --verify`. Check literature with `python scripts/11_complete_literature.py --verify`. The corrected compute version passed [183 tests and a three-layout coarse-grid trial](../results/g3/test_receipt.json). The [G3 response](GATE_G3_response.md) maps the reviewer requests to the revised evidence.

The [K3 response](phase_11d_K3.md) includes the HK counts for every area level. [K3 evidence manifest](../results/g3_review_k3/release_manifest.json)
