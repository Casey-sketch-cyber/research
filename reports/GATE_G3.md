# Gate G3 — Functional capacity, equivalent area and furniture design

The study asks how much additional daily activity demand transformable furniture can serve in the same dwelling, how to express that difference as an equivalent area, and what the modeled results imply for compact-home screening and furniture design. The corrected primary analysis uses the accepted F1 inventory and the P1 paired inversion. This package is ready for results review.

| Research hypothesis | Evidence at G3 |
| --- | --- |
| H1 · Gains peak in the smallest dwellings and shrink as area grows | Partly supported. Transformable furniture raises modeled coverage for a minority of real plans and some small and intermediate D3 shells. The largest median gains for the two-person households occur at intermediate sizes in the generated set. The observed size relationship is nonmonotonic. |
| H2 · Equal-area plans differ in capacity and area rules disagree with adequacy | Supported within the model. The couple and parent-and-child cases show substantial within-bin FCI variation. On real plans, the 30/45 m² comparator disagrees with modeled S2 adequacy on 55.7% and 52.7% of these cases, respectively. |
| H3 · A graph model reaches rank correlation of at least 0.80 on held-out sites | Not supported. D1 held-out GraphSAGE rank correlations range from 0.087 to 0.661 for S0 and 0.088 to 0.588 for S2. |
| H4 · A standard kit improves adequacy over the catalogue and captures most of the bespoke gain | Not supported in the reduced test. Training adequacy falls for both schedules; the two positive transfer results are one net case each. No majority share of a positive bespoke FCIq gain is identified for the selected kit. |

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
| Pooled | H2 remote worker | 14.59 [12.46, 16.27] | 8.27 | 6.32 |
| Pooled | H3 couple | 27.03 [26.19, 27.82] | 16.26 [15.20, 17.27] | 10.77 [9.66, 11.94] |
| Pooled | H4 parent and child | 31.14 [30.39, 31.90] | 20.98 [20.08, 21.83] | 10.16 [9.28, 11.06] |

Dashes denote crossings outside observed support or with nonincreasing probability. The pooled H2 point difference is identified, and too few bootstrap fits support an interval. The complete table includes thresholds 0.90 and 1.00 and the status of every fit. [Adequate-area estimates](../results/expA_f1/analysis/min_adequate_area.csv)

## Experiment B — solver benchmark

| Algorithm | Paired cases | Valid | Mean FCI | Median FCI | Mean elapsed s |
| --- | --- | --- | --- | --- | --- |
| CP-SAT | 200 | 100.0% | 0.8675 | 0.9615 | 38.451 |
| Greedy footprint | 200 | 100.0% | 0.8612 | 1.0000 | 3.465 |
| Simulated annealing | 200 | 100.0% | 0.9341 | 1.0000 | 104.118 |

All 600 outputs passed the independent validator. The paired mean CP-SAT difference from greedy was +0.0063 FCI [−0.0263, +0.0356]. Simulated annealing started from the greedy layout and used the longest mean elapsed time. Interpret quality together with the measured runtime and tested settings. [Benchmark report](phase_08_B_results.md) · [Algorithm results](../results/expB/algorithm_summary.csv) · [Paired differences](../results/expB/paired_algorithm_effects.csv)

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

The 8 m² threshold accepts every real-plan unit in this sample. For the 30/45 m² rule, most disagreement for the two-person households is from functional layouts below the fixed area rule. Continuous area-per-person and rooms-per-person comparisons retain the complete threshold sweeps, with no selected decision threshold. [D results](phase_09_D_results.md) · [Misclassification tables](../results/expD/confusion.csv) · [Within-bin dispersion](../results/expD/dispersion.csv)

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

## Experiment K — reduced kit design

The approved exploratory run screened eight vectors per household for H1 (commuter) and H3 (couple). A 16-layout pilot projected 30.39 hours for the full reduced sample. It retained 30 generated training shells, 15 generated held-out shells and 15 eligible real plans per household. The completed run took 11.36 hours including the pilot and independently validated all 1,803 layouts, including 1,080 matched confirmations. The full K grid was not run. [K report](phase_11b_K_results.md) · [Choices and comparisons](../results/expK/) · [F12 dimensions](../results/g3/figures/F12_kit.pdf)

The table compares S2 on identical shells. Adequacy means FCIq ≥ 0.95 using the configured quality factors. “Flat” refers to kit selection and layout search with quality set to one; its outcomes are rescored with the configured quality factors. The bespoke comparator is available only on the training shells.

| Household | Cohort | n | Mean FCIq: catalogue → kit | Adequate: catalogue → kit | Adequate with flat selection | Kit gains / losses |
| --- | --- | --- | --- | --- | --- | --- |
| H1 commuter | Training | 30 | 0.727 → 0.714 | 43.3% → 36.7% | 20.0% | 0 / 2 |
| H1 commuter | Held out | 15 | 0.724 → 0.738 | 40.0% → 46.7% | 20.0% | 2 / 1 |
| H1 commuter | Real | 15 | 0.965 → 0.963 | 86.7% → 86.7% | 73.3% | 0 / 0 |
| H3 couple | Training | 30 | 0.657 → 0.628 | 16.7% → 13.3% | 3.3% | 1 / 2 |
| H3 couple | Held out | 15 | 0.724 → 0.669 | 20.0% → 20.0% | 0.0% | 0 / 0 |
| H3 couple | Real | 15 | 0.892 → 0.888 | 60.0% → 66.7% | 33.3% | 1 / 0 |

H1 chose a 0.80 m wall bed, 0.80 × 0.45 m desk, 0.70 × 0.60 m table and 0.60 m wardrobe frontage. Its bed, desk and table quality factors are 0.60, 0.70 and 0.80. Flat selection chose those same dimensions with a different optimization objective. H3 chose a 1.50 m bed, 1.20 × 0.55 m desk, 1.00 × 0.75 m table and 1.40 m wardrobe frontage, with the three quality factors equal to one. Flat selection for H3 chose a 1.20 m bed and the smaller desk, table and wardrobe dimensions above. F12 redraws the accepted selected dimensions and moves storage labels out of the dimension arrows.

The matched form and time effects differ by schedule. On real plans the catalogue S1−S0 and S2−S1 mean FCIq effects are +0.013 and 0.000 for H1, versus +0.061 and +0.141 for H3. With the selected kits these are +0.018 and +0.006 for H1, and +0.078 and +0.141 for H3. [Complete paired effects](../results/expK/form_time_effects.csv)

The bespoke comparator selects the best observed S2 FCIq per training shell from the finite kit grid, including the confirmed selected-kit layout. H1 bespoke mean FCIq is 0.731 and its adequacy is 40.0%. The small positive FCIq difference over the catalogue gives a negative captured share (−419.5%) because the selected kit scores below the catalogue. H3 bespoke mean FCIq is 0.652 with 16.7% adequacy; its difference from the catalogue is nonpositive, so the gain share is undefined. This comparator bounds the confirmed kit on these shells within the evaluated layouts. The H4 hypothesis is unsupported in this reduced experiment: the selected kit does not improve training adequacy over the catalogue or capture a majority of a positive bespoke gain. The two positive transfer changes are each a net gain of one shell out of 15.

## Hong Kong — modeled adequacy across compact shell sizes

The scenario uses 390 equally weighted templates: 30 shapes at each integer size from 8 to 20 m². It reuses 2,970 corrected catalogue layouts and adds 540 catalogue layouts for 17 and 19 m². The 780 kit layouts include 90 exact accepted K layouts and 98 catalogue layouts independently confirmed to attain FCIq = 1 with zero time burden in the kit configuration. The remaining 592 use new kit solves. All 4,290 scenario records passed. The kit scenario covers H1 and H3; its exact K overlaps include both training and held-out shells. [Scenario report](phase_11_HK_results.md) · [F10](../results/figures/F10.pdf)

Each size entry is the number meeting FCIq ≥ 0.95 out of 30. A_min is the fitted 50% adequacy crossing; ΔA_min compares each strategy with its matched catalogue S0 baseline. The 95% intervals use 1,000 paired resamples of shape templates, keeping their sizes and strategies together. The last column averages the shortfall to the fitted A_min over all 390 shells.

| Household | Strategy | 8 m² | 10 m² | 12 m² | Adequate overall | A_min m² [95% CI] | ΔA_min m² [95% CI] | Mean shell shortfall m² |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| H1 commuter | S0 | 0/30 | 0/30 | 4/30 | 54.6% | 13.40 [13.03, 13.73] | Reference | 1.34 |
| H1 commuter | S1 | 0/30 | 0/30 | 12/30 | 62.6% | 12.37 [12.00, 12.70] | 1.03 [0.70, 1.43] | 0.91 |
| H1 commuter | S2 | 0/30 | 0/30 | 12/30 | 62.6% | 12.37 [12.00, 12.70] | 1.03 [0.70, 1.43] | 0.91 |
| H1 commuter | S2 kit | 0/30 | 0/30 | 5/30 | 47.2% | 14.38 [13.83, 14.98] | −0.98 [−1.53, −0.50] | 1.82 |
| H3 couple | S0 | 0/30 | 0/30 | 0/30 | 6.7% | — | Reference | — |
| H3 couple | S1 | 0/30 | 0/30 | 0/30 | 27.7% | 16.91 [16.60, 17.21] | — | 3.40 |
| H3 couple | S2 | 0/30 | 0/30 | 0/30 | 46.7% | 14.43 [14.00, 14.90] | — | 1.85 |
| H3 couple | S2 kit | 0/30 | 0/30 | 0/30 | 39.5% | 15.39 [14.67, 16.19] | — | 2.39 |
| H4 parent and child | S0 | 0/30 | 0/30 | 0/30 | 10.3% | 19.58 [18.78, 19.96] | Reference | 5.61 |
| H4 parent and child | S1 | 0/30 | 0/30 | 0/30 | 30.8% | 16.53 [15.97, 17.18] | 3.05 [2.34, 3.58] | 3.14 |
| H4 parent and child | S2 | 0/30 | 0/30 | 0/30 | 31.0% | 16.49 [15.95, 17.07] | 3.09 [2.37, 3.61] | 3.11 |

The catalogue S2 mean shortfall falls by 0.43 m² for the commuter and 2.50 m² for parent and child relative to S0. The couple's static crossing is outside the observed 8–20 m² range, leaving its baseline contrast unidentified. The parent-and-child S0 crossing is close to the upper edge; 812 of 1,000 bootstrap draws support its paired S2 interval. The S2 kits have lower aggregate adequacy than the catalogue S2 for both tested households on this grid.

The matched mean catalogue form and time effects in FCIq are +0.033 and +0.003 for H1, +0.107 and +0.056 for H3, and +0.078 and +0.007 for H4. The commuter's S1 and S2 share is identical at each size even though switching improves ten individual FCIq scores. The couple's largest pooled contribution is form, with a further time effect visible in the S2 curve. [All sizes and denominators](../results/scenario_hk/adequacy_by_size.csv) · [Crossing and gap support](../results/scenario_hk/scenario_summary.csv) · [Separate form and time effects](../results/scenario_hk/form_time_effects.csv)

The D6 territory aggregate reports 215,709 residents and 107,371 households in 108,202 subdivided units, with 33,658 quarters containing subdivided units. These counts give context. D6 lacks the household-size and area distributions needed to weight the modeled templates. The scenario illustrates functional differences at the same area; it does not estimate stock adequacy, territory-wide floor area or carbon, or set a statutory minimum. [D6 coverage and field definitions](schemas/D6.md) · [Territory counts](../results/scenario_hk/territory_context.csv)

## Literature screening and study position

The retrieved snapshot has 3,006 deduplicated titles, 947 retained titles and 407 available abstracts that were all read. The abstract decisions include nine overlap records, 253 related records, 13 known references and 132 irrelevant records. The ledger records 540 retained titles without an available abstract after the planned retrieval and follow-up, including the outcomes of 203 targeted Crossref checks. Eight records in the retrieved set received full-text checks, including seven overlap records. Two overlap records remain at abstract or project-summary access. The closest studies include room-level activity-area measures and circulation-based spatial compression. The present analysis contributes the paired whole-dwelling comparison at a common functional endpoint, with switching, daily demand and support limits made explicit. [Search scope, inclusion flow and positioning](novelty_check.md#systematic-confirmation-task-l--g3) · [Screening decisions](../results/literature/screened.csv) · [Full-text evidence](../results/literature/fulltext_checks_g3.json)

The screening used one reviewer and a bounded four-source retrieval. The remaining abstract and full-text gaps, source query caps and versions with distinct identifiers limit claims about coverage. Two supplemental source checks sit outside the retrieval flow. Q34 records the citation and positioning questions for review.

## Known issues for review

- The F1 primary estimand covers 2,619 units that pass the predeclared empty-geometry check. The 123 excluded units remain documented; the 94 valid zero-score layouts remain in the corrected evidence. Generated shells supply most of the small-area coverage and are interpreted separately from actual floor plans. [Evaluability and coverage](phase_07_F1_F2_results.md)
- The equivalent-area ruler is sample and household specific. A support-bound result states an inequality. The old FEA-minus-own-area measure is superseded. Capacity crossings require data on both sides of the adequacy transition; finite samples and saturation leave some crossings and intervals unidentified.
- FCI and FCIq represent scheduled service under modeled geometric and household assumptions. The results do not measure residents' use, switching compliance, observed satisfaction or statutory compliance. Independent validators test the returned layouts. Solver budgets and the selected furniture inventory still constrain the available layouts.
- The mirrored-access check is a paired robustness comparison on its own sample. It changes the available access targets as well as the reserved space. The room-level R comparison uses an approximate envelope and a body-free-area measure; the source uses a clearance-inclusive measure.
- The Hong Kong area gaps refer to the prescribed modeled shells. The published D6 counts do not supply the joint household and floor-area distribution needed for city-scale totals. Any claim about territory-wide floor area or carbon would need further data.

Open questions and unresolved limitations are tracked in [QUESTIONS.md](QUESTIONS.md). The [evidence manifest](../results/g3/evidence_manifest.json) binds the phase acceptance receipts, the numeric outputs and reviewed figures. Recheck the package with `python scripts/11_make_G3.py --verify` and `python scripts/11_complete_literature.py --verify` from the repository root after installing the project. The corrected compute version passed [183 tests and a three-layout coarse-grid trial](../results/g3/test_receipt.json). The results-review record is the next gate before the final package.
