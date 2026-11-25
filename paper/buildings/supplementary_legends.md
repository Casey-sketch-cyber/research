# Supplementary Materials Legends and Tables

Supporting information for *"Translating furniture into floor area shows where compact homes gain space"* (submitted to *Buildings*, MDPI). All supplementary citations appear in the main reference list (`paper/references.bib`).

## Supplementary Figures

**Figure S1:** Net internal area distributions and normalized plan examples across the evaluable dwelling corpus. Top: step histograms of net internal area (NIA, in 2 m² bins from 8 to 50 m²) across evaluable units in Swiss Dwellings (D1, $n = 1236$), ResPlan (D2, $n = 873$), and generated shells (D3, $n = 510$). Bottom: representative normalized geometries from D1 (42.8 m² NIA), D2 (46.5 m² NIA), and D3 (11.0 m² NIA) showing furnishable, storage-only, walkable-only, and fixed-service zones alongside entrance and window segments. Observed plans supply larger compact units ($\ge 16.75\text{ m}^2$), while generated shells extend systematic coverage down to 8.00 m².

**Figure S2:** Orthographic 3D renders of showcase dwellings where multi-state furniture remains fixed across the day. (A) Blender Cycles three-dimensional (3D) cutaway renders of the 10.00 m² generated shell for a couple on a normal day across Night, Workday, and Dinner under static (S0; functional capacity index, $\text{FCI} = 0.577$; transformation burden, $\text{TB} = 0.00$) and form + time (S2; $\text{FCI} = 0.687$, $\text{TB} = 0.00$), with the foreground toilet enclosure cut away to expose the room interior. No double sleeping surface is deployed in any slot because operating clearances and wet-service access cannot fit simultaneously, and S2 furniture states remain fixed across all slots ($\text{TB} = 0.00$). (B) Whole-flat 3D orthographic renders across Night, Workday, and Dinner (top two rows) and low-wall daytime main-room close-ups (bottom row) of the 29.97 m² Swiss Dwellings observed plan for a couple under S0 ($\text{FCI} = 0.668$, $\text{TB} = 0.00$) and S2 ($\text{FCI} = 0.687$, $\text{TB} = 0.00$), with shared camera, lighting, and scale across whole-flat views. S2 furniture states do not change across slots ($\text{TB} = 0.00$), illustrating how narrow partitioned room geometry restricts multi-state gains even near 30 m² NIA.

**Figure S3:** Layout validity, functional capacity, and runtime across four search methods on the 200-pair S2 benchmark. Horizontal bar comparisons across $n = 200$ stratified unit–household pairs comparing standalone constraint programming (CP-SAT), descending-footprint greedy placement, standalone simulated annealing (20,000 proposals $\times$ 3 restarts), and the warm-started production pipeline on (left) share of independently valid layouts (%), (middle) mean validator FCI under S2, and (right) mean elapsed runtime (s; summing recorded S0 + S1 + S2 solve times for production and including S2 preparation plus validation for standalone methods). All methods return 100% valid layouts, and the warm-started production pipeline achieves the highest mean FCI at half the mean runtime of simulated annealing (see also Table S2).

**Figure S4:** Sensitivity of equivalent-area gains and adequate-area reductions to geometric, furniture, and solver parameters. Paired changes relative to matched production controls in median identified positive equivalent-area gain ($\Delta\text{EA}$, in m², top row) and minimum adequate area reduction ($\Delta A_{\min}$ at $\tau = 0.95$, in m², bottom row; × marks contrasts where at least one logistic crossing is unsupported) across the four primary households when varying global clearance scale ($0.8\times, 1.2\times$; $n = 200$ pairs), grid/anchor resolution (0.05 m, 0.20 m; $n = 50$ units), solver time limit (30 s, 60 s, 120 s; $n = 50$ units), single-item transformable removals ($n = 200$ pairs), and required walking width (0.90 m; $n = 200$ pairs). Note that changes in median identified $\Delta\text{EA}$ condition on each run's own subset of pairs with an identified positive gain, which can shift between conditions. Widening required walking circulation from 0.60 m to 0.90 m causes the largest capacity and adequacy shifts across all households.

**Figure S5:** Dimensions and training and transfer summaries of the top-ranked parametric kits. Plan-view body footprints (deployed and stowed states at common scale, in meters) and training ($n = 30$ shells, 8–15 m²) plus transfer ($n = 15$ held-out shells and $n = 15$ observed plans $\le 20\text{ m}^2$) summary tables for the top-ranked commuter (left) and couple (right) parametric kits. Larger couple furniture expands adequacy at 13–16 m² while reducing capacity below 13 m², whereas downsized commuter furniture does not improve on the standard catalogue (see also Table S3).

**Figure S6:** Room-level daytime body-free area versus whole-dwelling equivalent-area gains. (A) Daytime body-free floor area (m²) under S0 and S2 for single commuter and single remote worker schedules in an approximate $4 \times 3\text{ m}$ bedroom envelope using the study furniture catalogue, plotted alongside Bu and Che Mat's [@bu2026compact] clearance-deducted static band (shaded, ~5–5.5 m²) and folded-bed value (dashed line, ~8 m²) (left). (B) Proportions of single-person dwelling–household pairs in observed plans ($n = 2109$) and generated shells ($n = 510$) whose daytime body-free floor area decreased, stayed equal, or increased from S0 to S2 (middle). (C) Paired equivalent-area gain ($\Delta\text{EA}$, m²; filled circles for point-identified pairs, open upward triangles for lower-bounded pairs) plotted against the $\text{S2} - \text{S0}$ change in daytime body-free area across observed single-person plans (right). Under scheduled whole-home optimization, daytime body-free area remains unchanged in the median single-person dwelling because static arrangements already satisfy daily demand without folding.

**Figure S7:** Parity plots of geometry-only GraphSAGE predictions against solver-validated labels. Scatter plots comparing GraphSAGE predictions (trained on grouped Swiss Dwellings training sites, $n = 884$ units across 323 sites) against solver-validated labels for static FCI (top row), form + time FCI (middle row), and point-identified equivalent-area gain $\Delta\text{EA}$ in m² (bottom row; excluding bound-only labels) across held-out Swiss Dwellings test sites ($n = 172$ units across 70 sites; left column), external ResPlan transfer ($n = 873$ units; middle column), and external generated shells ($n = 510$ units; right column), colored by household schedule around the dashed $y = x$ parity line. On held-out Swiss Dwellings sites, GraphSAGE Spearman rank correlations ranged from 0.087 to 0.661 for S0 FCI and from 0.088 to 0.588 for S2 FCI—below the prespecified $\rho \ge 0.80$ criterion—and predictions fell below retained lower bounds in 23 of 33 bound-only $\Delta\text{EA}$ cases (despite post-hoc S0 adequacy receiver operating characteristic area under the curve [ROC AUC] values of 0.796 for couples and 0.888 for parent and child; see Table S4).

---

## Supplementary Tables

**Table S1:** Audited furniture library: body footprints, operating clearances, capabilities, and Amazon Berkeley Objects check. Dimensions (width along wall $\times$ depth into room, in meters), required directional clearance depths, served activity capabilities, allowed strategies, per-unit instance caps, and dimensional comparison flags against 43,002 Amazon Berkeley Objects (ABO) [@collins2022abo] product triples (IQR denotes interquartile range; full anchoring, height-class, storage-unit, and transition-effort attributes are archived in the study repository).

| Item | State | Body (m) | Clearance (m) | Capabilities | Strategies | Max. count | ABO check flag |
| :--- | :--- | :--- | :--- | :--- | :--- | ---: | :--- |
| single bed | static | 0.90 × 2.00 | left 0.60 | Single sleeping | S0, S1, S2 | 2 | Outside IQR |
| double bed | static | 1.40 × 2.00 | left 0.60, right 0.50 | Double-occupancy sleeping | S0, S1, S2 | 1 | Within IQR |
| wardrobe | static | 1.00 × 0.60 | front 0.70 | Storage | S0, S1, S2 | 2 | Outside IQR |
| shelving | static | 0.80 × 0.35 | front 0.60 | Storage | S0, S1, S2 | 2 | Within IQR |
| desk | static | 1.20 × 0.60 | front 0.75 | Individual work | S0, S1, S2 | 2 | Within IQR |
| dining table 2 | static | 0.75 × 0.75 | front 0.60, back 0.60 | Two-person dining | S0, S1, S2 | 1 | Outside IQR |
| dining table 4 | static | 1.20 × 0.80 | front 0.60, back 0.60 | Four- or two-person dining | S0, S1, S2 | 1 | Outside IQR |
| sofa 2 | static | 1.60 × 0.85 | front 0.60 | Two-person lounging | S0, S1, S2 | 1 | Outside IQR |
| armchair | static | 0.80 × 0.80 | front 0.50 | One-person lounging | S0, S1, S2 | 2 | Within IQR |
| wall bed single | stowed | 1.00 × 0.45 | front 0.40 | — | S1, S2 | 2 | No match; unvalidated state |
| wall bed single | deployed | 1.00 × 2.10 | left 0.60 | Single sleeping | S1, S2 | 2 | Outside IQR; unvalidated state |
| wall bed double | stowed | 1.50 × 0.45 | front 0.40 | — | S1, S2 | 1 | No match; unvalidated state |
| wall bed double | deployed | 1.50 × 2.15 | left 0.60, right 0.50 | Double-occupancy sleeping | S1, S2 | 1 | Unvalidated state |
| wall bed over sofa | stowed | 1.60 × 0.90 | front 0.60 | Two-person lounging | S1, S2 | 1 | Outside IQR; unvalidated state |
| wall bed over sofa | deployed | 1.60 × 2.15 | left 0.60, right 0.50 | Double-occupancy sleeping | S1, S2 | 1 | Unvalidated state |
| sofa bed | stowed | 1.90 × 0.90 | front 0.60 | Two-person lounging | S1, S2 | 1 | Unvalidated state |
| sofa bed | deployed | 1.90 × 2.00 | front 0.50 | Double-occupancy sleeping | S1, S2 | 1 | Unvalidated state |
| drop leaf table | stowed | 0.80 × 0.20 | — | — | S1, S2 | 1 | No match; unvalidated state |
| drop leaf table | deployed | 0.80 × 0.75 | front 0.60 | Two-person dining, individual work | S1, S2 | 1 | Outside IQR; unvalidated state |
| fold down desk | stowed | 1.00 × 0.25 | front 0.40 | — | S1, S2 | 1 | No match; unvalidated state |
| fold down desk | deployed | 1.00 × 0.55 | front 0.75 | Individual work | S1, S2 | 1 | Unvalidated state |
| extendable table | stowed | 0.80 × 0.80 | front 0.60, back 0.60 | Two-person dining | S1, S2 | 1 | Outside IQR; unvalidated state |
| extendable table | deployed | 1.60 × 0.80 | front 0.60, back 0.60 | Four- or two-person dining, individual work | S1, S2 | 1 | Outside IQR; unvalidated state |

**Table S2:** Solver benchmark across 200 stratified unit–household pairs under S2. Independent validator pass rate, mean and median S2 FCI, and mean and median elapsed runtime across four search methods (see also Figure S3).

| Search method | Matched cases ($n$) | Independently valid (↑) | Mean S2 FCI (↑) | Median S2 FCI (↑) | Mean time (s ↓) | Median time (s ↓) | Runtime accounting basis |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | :--- |
| Standalone CP-SAT | 200 | 100.0% | 0.8675 | 0.9615 | 38.45 | 30.44 | Standalone S2 elapsed including preparation and validation |
| Greedy footprint | 200 | 100.0% | 0.8612 | 1.0000 | 3.47 | 1.94 | Standalone S2 elapsed including preparation and validation |
| Simulated annealing | 200 | 100.0% | 0.9341 | 1.0000 | 104.12 | 108.33 | Standalone S2 elapsed including preparation and validation |
| Production pipeline (S0–S2) | 200 | 100.0% | 0.9428 | 1.0000 | 53.86 | 10.68 | Accepted production S0 + S1 + S2 recorded solve time |

**Table S3:** Kit comparisons: training selection, transfer cohorts, and Hong Kong per-size adequacy. Quality-scored capacity ($\text{FCI}_q$) and adequacy ($\text{FCI}_q \ge 0.95$) comparisons between parametric furniture kits and standard catalogue dimensions. Part A compares the top-ranked fixed kit per household against the optimized catalogue and the per-shell bespoke upper bound across the 30 frozen 8–15 m² generated training shells (compact commuter kit: 0.80 m single wall bed, $0.80 \times 0.45\text{ m}$ fold-down desk, $0.70 \times 0.60\text{ m}$ drop-leaf table, 0.60 m wardrobe; larger couple kit: 1.50 m double wall bed, $1.20 \times 0.55\text{ m}$ fold-down desk, $1.00 \times 0.75\text{ m}$ drop-leaf table, 1.40 m wardrobe; matched-search commuter parity candidate: 1.00 m single wall bed, $1.20 \times 0.55\text{ m}$ fold-down desk, $1.00 \times 0.75\text{ m}$ drop-leaf table, 1.40 m wardrobe). Part B reports paired kit-minus-catalogue differences with 95% bootstrap confidence intervals (CI; 1000 resamples of shell pairs for training, held-out, and observed cohorts; 1000 resamples of the 30 shape templates for Hong Kong). Part C enumerates adequate shells ($n = 30$ templates per integer m²) across the 8–20 m² Hong Kong grid; for the couple, band totals (larger kit S2 versus optimized catalogue S2) are 0/150 versus 0/150 at 8–12 m² (mean $\text{FCI}_q$ 0.448 versus 0.500), 51/120 versus 30/120 at 13–16 m², and 103/120 versus 102/120 at 17–20 m² (modeled $A_{\min}$ 15.39 [14.67, 16.19] versus 16.12 [15.70, 16.57] m², a 0.73 m² point difference; single commuter compact kit $A_{\min}$ 14.38 [13.83, 14.98] versus 12.30 [11.90, 12.64] m²).

*Part A. Training selection and bespoke upper bound ($n = 30$ generated shells, 8–15 m² NIA)*

| Household | Selected kit | Runner-up | Catalogue mean $\text{FCI}_q$ (↑) | Selected kit mean $\text{FCI}_q$ (↑) | Bespoke mean $\text{FCI}_q$ (↑) | Bespoke gain captured (↑) | Adequate ($\text{FCI}_q \ge 0.95$): kit vs catalogue (bespoke) |
| :--- | :--- | :--- | ---: | ---: | ---: | ---: | :--- |
| Single commuter | Compact commuter kit | Catalogue | 0.7127 | 0.7141 | 0.7343 | 6.2% | 11/30 vs 13/30 (13/30) |
| Couple | Larger couple kit | Catalogue | 0.6322 | 0.6344 | 0.6612 | 7.4% | 5/30 vs 2/30 (6/30) |

*Part B. Paired kit-versus-catalogue comparisons across training, transfer, and Hong Kong cohorts*

| Household | Candidate kit | Cohort | Pairs ($n$) | Mean $\text{FCI}_q$: kit − catalogue [95% CI] | Kit higher / equal / lower | Adequate: kit vs catalogue | Adequate only on kit / only on catalogue |
| :--- | :--- | :--- | ---: | :--- | ---: | ---: | ---: |
| Single commuter | Matched-search commuter kit | Training, matched extra search | 30 | −0.0284 [−0.0557, −0.0042] | 14 / 7 / 9 | 7 vs 13 | 0 / 6 |
| Single commuter | Compact commuter kit | Training, best saved | 30 | +0.0013 [−0.0153, +0.0200] | 8 / 7 / 15 | 11 vs 13 | 0 / 2 |
| Single commuter | Compact commuter kit | Training, original confirmation | 30 | +0.0009 [−0.0156, +0.0195] | 8 / 7 / 15 | 11 vs 13 | 0 / 2 |
| Single commuter | Compact commuter kit | Held-out generated shells | 15 | +0.0185 [−0.0166, +0.0551] | 3 / 9 / 3 | 7 vs 6 | 2 / 1 |
| Single commuter | Compact commuter kit | Observed plans ($\le 20\text{ m}^2$) | 15 | +0.0036 [−0.0055, +0.0121] | 4 / 10 / 1 | 13 vs 13 | 0 / 0 |
| Single commuter | Compact commuter kit | Hong Kong model shells | 390 | −0.0389 [−0.0564, −0.0230] | 54 / 168 / 168 | 184 vs 246 | 5 / 67 |
| Couple | Larger couple kit | Training, matched extra search | 30 | +0.0021 [−0.0336, +0.0279] | 21 / 3 / 6 | 5 vs 2 | 3 / 0 |
| Couple | Larger couple kit | Training, original confirmation | 30 | −0.0044 [−0.0395, +0.0220] | 20 / 3 / 7 | 4 vs 2 | 2 / 0 |
| Couple | Larger couple kit | Held-out generated shells | 15 | −0.0242 [−0.0946, +0.0315] | 9 / 2 / 4 | 3 vs 0 | 3 / 0 |
| Couple | Larger couple kit | Observed plans ($\le 20\text{ m}^2$) | 15 | +0.0066 [−0.0040, +0.0181] | 7 / 3 / 5 | 10 vs 8 | 2 / 0 |
| Couple | Larger couple kit | Hong Kong model shells | 390 | −0.0228 [−0.0345, −0.0120] | 184 / 71 / 135 | 154 vs 132 | 35 / 13 |

*Part C. Per-size adequacy counts ($\text{FCI}_q \ge 0.95$) across Hong Kong model shells ($n = 30$ templates per integer m²)*

| NIA (m²) | Commuter S0 | Commuter rescored S2 | Commuter optimized catalogue S2 | Commuter compact kit S2 | Couple S0 | Couple S1 | Couple rescored S2 | Couple optimized catalogue S2 | Couple larger kit S2 |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 8 | 0/30 | 0/30 | 0/30 | 0/30 | 0/30 | 0/30 | 0/30 | 0/30 | 0/30 |
| 9 | 0/30 | 0/30 | 0/30 | 0/30 | 0/30 | 0/30 | 0/30 | 0/30 | 0/30 |
| 10 | 0/30 | 0/30 | 0/30 | 0/30 | 0/30 | 0/30 | 0/30 | 0/30 | 0/30 |
| 11 | 0/30 | 4/30 | 4/30 | 3/30 | 0/30 | 0/30 | 0/30 | 0/30 | 0/30 |
| 12 | 4/30 | 12/30 | 12/30 | 5/30 | 0/30 | 0/30 | 0/30 | 0/30 | 0/30 |
| 13 | 11/30 | 21/30 | 21/30 | 12/30 | 0/30 | 0/30 | 0/30 | 0/30 | 4/30 |
| 14 | 22/30 | 27/30 | 29/30 | 18/30 | 0/30 | 0/30 | 2/30 | 2/30 | 7/30 |
| 15 | 27/30 | 30/30 | 30/30 | 19/30 | 0/30 | 0/30 | 9/30 | 10/30 | 16/30 |
| 16 | 29/30 | 30/30 | 30/30 | 22/30 | 1/30 | 4/30 | 16/30 | 18/30 | 24/30 |
| 17 | 30/30 | 30/30 | 30/30 | 26/30 | 2/30 | 5/30 | 23/30 | 23/30 | 24/30 |
| 18 | 30/30 | 30/30 | 30/30 | 24/30 | 8/30 | 17/30 | 24/30 | 25/30 | 26/30 |
| 19 | 30/30 | 30/30 | 30/30 | 26/30 | 4/30 | 14/30 | 26/30 | 27/30 | 26/30 |
| 20 | 30/30 | 30/30 | 30/30 | 29/30 | 11/30 | 23/30 | 26/30 | 27/30 | 27/30 |
| **Overall (8–20, $n = 390$)** | **54.6%** | **62.6%** | **63.1% (246/390)** | **47.2% (184/390)** | **6.7%** | **16.2%** | **32.3%** | **33.8% (132/390)** | **39.5% (154/390)** |

**Table S4:** Geometry-only surrogate accuracy on held-out Swiss Dwellings sites and external transfer sets. Held-out Swiss Dwellings site-group test performance ($n = 172$ units across 70 sites) for predicting static FCI (S0 FCI), form + time FCI (S2 FCI), and D1-training-referenced equivalent-area gain ($\Delta\text{EA}$, in m²) across area-only linear, LightGBM, tabular multilayer perceptron (MLP), and GraphSAGE models (full external transfer tables for ResPlan [$n = 873$] and generated shells [$n = 510$] are archived in the study repository). Point errors—mean absolute error (MAE), root mean square error (RMSE), coefficient of determination ($R^2$), and Spearman rank correlation ($\rho$)—evaluate point-identified labels including exact zeros; Bounds $n$ counts left- or right-bounded equivalent-area cases evaluated separately against lower bounds. Post-hoc adequacy ROC AUC evaluates whether continuous FCI predictions rank cases at or above $\text{FCI} \ge 0.95$ (see also Figure S7).

| Household | Target | Model | Evaluated $n$ | Bounds $n$ | MAE (↓) | RMSE (↓) | $R^2$ (↑) | Spearman $\rho$ (↑) | Inference (ms/unit ↓) | Post-hoc adequacy ROC AUC (↑) |
| :--- | :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Single commuter | S0 FCI | Area-only linear | 172 | 0 | 0.032 | 0.048 | −0.048 | −0.019 | 0.0022 | 0.398 |
| Single commuter | S0 FCI | LightGBM | 172 | 0 | 0.028 | 0.052 | −0.241 | 0.153 | 0.0395 | 0.598 |
| Single commuter | S0 FCI | Tabular MLP | 172 | 0 | 0.052 | 0.081 | −2.031 | −0.101 | 0.0068 | 0.367 |
| Single commuter | S0 FCI | GraphSAGE | 172 | 0 | 0.022 | 0.052 | −0.279 | 0.087 | 0.0041 | 0.528 |
| Single commuter | S2 FCI | Area-only linear | 172 | 0 | 0.011 | 0.015 | −0.368 | 0.056 | 0.0022 | 0.734 |
| Single commuter | S2 FCI | LightGBM | 172 | 0 | 0.010 | 0.025 | −2.885 | −0.032 | 0.0395 | 0.406 |
| Single commuter | S2 FCI | Tabular MLP | 172 | 0 | 0.040 | 0.069 | −29.417 | −0.017 | 0.0068 | 0.452 |
| Single commuter | S2 FCI | GraphSAGE | 172 | 0 | 0.006 | 0.025 | −3.056 | 0.088 | 0.0041 | 0.742 |
| Single commuter | ΔEA (m²) | Area-only linear | 155 | 17 | 0.000 | 0.000 | — | — | 0.0022 | — |
| Single commuter | ΔEA (m²) | LightGBM | 155 | 17 | 0.180 | 0.330 | — | — | 0.0395 | — |
| Single commuter | ΔEA (m²) | Tabular MLP | 155 | 17 | 0.343 | 0.645 | — | — | 0.0068 | — |
| Single commuter | ΔEA (m²) | GraphSAGE | 155 | 17 | 0.199 | 0.428 | — | — | 0.0041 | — |
| Single remote worker | S0 FCI | Area-only linear | 172 | 0 | 0.038 | 0.065 | −0.004 | 0.084 | 0.0021 | 0.555 |
| Single remote worker | S0 FCI | LightGBM | 172 | 0 | 0.031 | 0.064 | 0.040 | 0.265 | 0.0408 | 0.721 |
| Single remote worker | S0 FCI | Tabular MLP | 172 | 0 | 0.060 | 0.096 | −1.173 | 0.021 | 0.0062 | 0.512 |
| Single remote worker | S0 FCI | GraphSAGE | 172 | 0 | 0.028 | 0.067 | −0.082 | 0.142 | 0.0041 | 0.602 |
| Single remote worker | S2 FCI | Area-only linear | 172 | 0 | 0.009 | 0.013 | −0.258 | 0.015 | 0.0021 | 0.560 |
| Single remote worker | S2 FCI | LightGBM | 172 | 0 | 0.009 | 0.023 | −2.795 | 0.002 | 0.0408 | 0.555 |
| Single remote worker | S2 FCI | Tabular MLP | 172 | 0 | 0.050 | 0.079 | −43.064 | 0.037 | 0.0062 | 0.499 |
| Single remote worker | S2 FCI | GraphSAGE | 172 | 0 | 0.006 | 0.022 | −2.420 | 0.223 | 0.0041 | 0.783 |
| Single remote worker | ΔEA (m²) | Area-only linear | 167 | 5 | 0.206 | 0.358 | 0.010 | 0.079 | 0.0021 | — |
| Single remote worker | ΔEA (m²) | LightGBM | 167 | 5 | 0.267 | 0.446 | −0.536 | 0.208 | 0.0408 | — |
| Single remote worker | ΔEA (m²) | Tabular MLP | 167 | 5 | 0.432 | 0.822 | −4.212 | −0.010 | 0.0062 | — |
| Single remote worker | ΔEA (m²) | GraphSAGE | 167 | 5 | 0.277 | 0.522 | −1.102 | 0.098 | 0.0041 | — |
| Couple | S0 FCI | Area-only linear | 172 | 0 | 0.082 | 0.131 | 0.089 | 0.469 | 0.0020 | 0.732 |
| Couple | S0 FCI | LightGBM | 172 | 0 | 0.064 | 0.124 | 0.177 | 0.523 | 0.0432 | 0.794 |
| Couple | S0 FCI | Tabular MLP | 172 | 0 | 0.083 | 0.140 | −0.040 | 0.402 | 0.0068 | 0.725 |
| Couple | S0 FCI | GraphSAGE | 172 | 0 | 0.063 | 0.131 | 0.090 | 0.588 | 0.0043 | 0.796 |
| Couple | S2 FCI | Area-only linear | 172 | 0 | 0.045 | 0.090 | 0.020 | 0.373 | 0.0020 | 0.620 |
| Couple | S2 FCI | LightGBM | 172 | 0 | 0.042 | 0.093 | −0.052 | 0.343 | 0.0432 | 0.672 |
| Couple | S2 FCI | Tabular MLP | 172 | 0 | 0.071 | 0.113 | −0.551 | 0.287 | 0.0068 | 0.565 |
| Couple | S2 FCI | GraphSAGE | 172 | 0 | 0.035 | 0.093 | −0.048 | 0.479 | 0.0043 | 0.722 |
| Couple | ΔEA (m²) | Area-only linear | 164 | 8 | 3.267 | 4.583 | 0.094 | 0.441 | 0.0020 | — |
| Couple | ΔEA (m²) | LightGBM | 164 | 8 | 2.865 | 4.286 | 0.208 | 0.510 | 0.0432 | — |
| Couple | ΔEA (m²) | Tabular MLP | 164 | 8 | 2.972 | 4.710 | 0.043 | 0.388 | 0.0068 | — |
| Couple | ΔEA (m²) | GraphSAGE | 164 | 8 | 2.834 | 4.195 | 0.241 | 0.533 | 0.0043 | — |
| Parent and child | S0 FCI | Area-only linear | 172 | 0 | 0.066 | 0.087 | 0.257 | 0.588 | 0.0021 | 0.821 |
| Parent and child | S0 FCI | LightGBM | 172 | 0 | 0.048 | 0.077 | 0.421 | 0.688 | 0.0419 | 0.901 |
| Parent and child | S0 FCI | Tabular MLP | 172 | 0 | 0.078 | 0.112 | −0.229 | 0.386 | 0.0063 | 0.722 |
| Parent and child | S0 FCI | GraphSAGE | 172 | 0 | 0.048 | 0.077 | 0.420 | 0.661 | 0.0041 | 0.888 |
| Parent and child | S2 FCI | Area-only linear | 172 | 0 | 0.040 | 0.059 | 0.091 | 0.485 | 0.0021 | 0.771 |
| Parent and child | S2 FCI | LightGBM | 172 | 0 | 0.031 | 0.062 | −0.020 | 0.443 | 0.0419 | 0.767 |
| Parent and child | S2 FCI | Tabular MLP | 172 | 0 | 0.061 | 0.093 | −1.269 | 0.251 | 0.0063 | 0.627 |
| Parent and child | S2 FCI | GraphSAGE | 172 | 0 | 0.025 | 0.056 | 0.170 | 0.588 | 0.0041 | 0.835 |
| Parent and child | ΔEA (m²) | Area-only linear | 169 | 3 | 4.058 | 5.147 | 0.187 | 0.482 | 0.0021 | — |
| Parent and child | ΔEA (m²) | LightGBM | 169 | 3 | 2.945 | 4.259 | 0.443 | 0.630 | 0.0419 | — |
| Parent and child | ΔEA (m²) | Tabular MLP | 169 | 3 | 3.467 | 4.717 | 0.317 | 0.562 | 0.0063 | — |
| Parent and child | ΔEA (m²) | GraphSAGE | 169 | 3 | 3.755 | 4.951 | 0.248 | 0.558 | 0.0041 | — |
