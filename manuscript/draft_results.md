# Results

## Experiment A · Coverage and equivalent area

The 2,619 evaluable units comprised 1,236 Swiss Dwellings plans, 873 ResPlan plans and 510 generated shells. The empty-geometry screen excluded 123 of the 2,742 selected units. The corrected dataset contained 31,428 independently valid layouts and retained 94 valid zero-score layouts. The smallest observed plan was 16.75 m² NIA. <!-- results/corpus/counts.csv; results/expA_f1/sample.csv; results/expA_f1/acceptance.json; results/expA_f1/solutions.csv -->

In the observed plans, the static layouts provided full FCI for 90.8% of commuters, 89.1% of remote workers, 72.7% of couples and 61.0% of parents with a child. Allowing form and time improved FCI for 7.5%, 8.7%, 23.5% and 35.9%, respectively. The couple had the largest mean time effect, while the parent-and-child schedule had the largest mean form effect. <!-- results/g3/area_summary.csv; results/expA_f1/analysis/primary_effects.csv -->

| Household | Mean form effect (95% CI) | Mean time effect (95% CI) |
| --- | --- | --- |
| H1 · Commuter | 0.0085 [0.0071, 0.0100] | 0.0002 [0.0000, 0.0003] |
| H2 · Remote worker | 0.0107 [0.0090, 0.0125] | 0.0001 [0.0000, 0.0002] |
| H3 · Couple | 0.0130 [0.0112, 0.0148] | 0.0112 [0.0094, 0.0130] |
| H4 · Parent and child | 0.0271 [0.0249, 0.0292] | 0.0017 [0.0013, 0.0022] |

<!-- results/expA_f1/analysis/primary_effects.csv, real_plans overall -->

The all-pair median equivalent-area gain was 0 m² for each household in observed plans. Among identified positive gains, the median was 1.33 m² [0.75, 3.11] for the remote worker, 6.21 m² [4.20, 10.00] for the couple and 5.00 m² [4.20, 8.00] for the parent and child. All improved commuter pairs were support-limited, with a median gain lower bound of ≥2.00 m². The comparable lower bound across all improved remote-worker pairs was ≥1.33 m². The commuter identified-positive median was unavailable on the observed-plan reference. <!-- results/g3/area_summary.csv; results/expA_f1/analysis_p1/paired_equivalent_area.csv -->

In D3, the couple's all-pair median gain rose from 0.75 m² (9.2% of NIA) in the 8–10 m² bin to 7.32 m² (49.8%) in the 14–16 m² bin. The median reached zero in the evaluated bins from 24 m² onward. The parent-and-child median increased from 0.69 m² at 8–10 m² to 6.00 m² at 18–20 m². <!-- results/g3/area_summary.csv -->

The observed-plan estimate of ΔAₘᵢₙ at FCI ≥ 0.95 was supported for the parent-and-child schedule, 10.78 m² [9.15, 12.70]. The other observed-plan contrasts had at least one unsupported crossing. The D3 reductions were 1.68 m² [1.12, 2.38] for the commuter, 3.63 m² [2.78, 4.77] for the remote worker, 5.53 m² [4.90, 6.12] for the couple and 6.45 m² [5.19, 7.75] for the parent and child. The pooled remote-worker point contrast was 6.32 m², with too few supported resamples for an interval. <!-- results/expA_f1/analysis/min_adequate_area.csv -->

## Experiment B · Feasible search under finite budgets

All four methods returned valid layouts on the 200 benchmark pairs. Mean FCI was 0.8675 for standalone CP-SAT, 0.8612 for greedy, 0.9341 for annealing and 0.9428 for the production pipeline. Production matched the highest observed score on 189 of 200 pairs, with a mean shortfall of 0.0034 FCI. Production's mean summed solve time was 53.86 s. The standalone annealing mean, including preparation and validation, was 104.12 s. <!-- results/g3_review/benchmark/algorithm_summary.csv; results/g3_review/benchmark/production_pairs.csv; results/g3_review/benchmark/production_shortfalls.csv -->

## Experiment D · Within-bin dispersion and area proxies

In observed plans, static FCI had an interquartile range of 0.205 for couples at 26–28 m² and 0.190 for parents with a child at 24–26 m². At FCI ≥ 0.95, the 45 m² comparator disagreed with S2 adequacy for 55.7% of couple cases and 52.7% of parent-and-child cases. Most disagreements for these two schedules were area failures with an adequate layout. All observed plans exceeded the 8 m² comparator. The generated shells and the scenario grid covered that threshold. <!-- results/expD/dispersion.csv; results/expD/confusion.csv; results/expA_f1/sample.csv; results/g3_review_k3/hk_adequacy_by_size.csv -->

## Sensitivity and room comparison

Increasing required walking width to 0.90 m reduced mean S2 FCI by 0.5151 for the parent-and-child schedule in 49 matched units. Under the separate mirrored double-bed access variant, the couple's mean time effect changed by −0.0122 FCI [−0.0203, −0.0040] across 348 small units. The observed-plan subset had 18 units and its interval included zero. The variant changes both clearance and the location of the access target. <!-- results/ablations/summary.csv; results/expA_f3/effect_summary.csv; reports/phase_07_F3_results.md -->

The approximate room envelope had 7.60 m² of body-free daytime area under both strategies and both single-person schedules. The generated analogues gave changes from −0.52 to +1.38 m². The main observed-plan and D3 comparisons had median daytime body-free area changes of 0 m² for both schedules. The source reports clearance-inclusive activity area under its own furniture arrangement. <!-- results/expR/reproduction.csv; results/expR/generalization_summary.csv; results/expR/source_values.csv -->

## Experiment C · Held-out prediction

GraphSAGE's mean D1 test MAE was 0.040 for S0 and 0.018 for S2. Across households, Spearman correlations ranged from 0.087 to 0.661 for S0 and 0.088 to 0.588 for S2. None reached the prespecified 0.80 mark on D1. The post-hoc D1 S0 adequacy AUC for GraphSAGE versus area-only regression was 0.796 versus 0.732 for the couple and 0.888 versus 0.821 for the parent and child. The highest D3 GraphSAGE S0 rank correlation, 0.924, occurred for the couple. In the held-out D1 gain task, GraphSAGE fell below the retained bound in 23 of 33 bound-only cases. <!-- results/expC/metrics.csv; results/expC/predictions.csv; results/g3_review/benchmark/c_adequacy_auc.csv -->

## Experiment K · Furniture dimensions

No tested kit established an improvement over the optimized catalogue for the single commuter. H1_kit_01 had the highest observed training mean by +0.0013 FCIq [−0.0153, +0.0200], with 11 of 30 shells adequate versus 13 of 30 for the catalogue. Under matched additional search, H1_kit_02 had a mean difference of −0.0284 [−0.0557, −0.0042] and 7 adequate shells versus 13. In the Hong Kong scenario, the highest-ranking commuter candidate reached adequacy in 184 of 390 shells versus 246 for the optimized catalogue. The catalogue is the supported fit-out choice for the single commuter in these comparisons. <!-- results/g3_review_k3/kit.yaml; results/g3_review_k3/paired_effects.csv -->

For the couple, the larger H3_kit_02 ranked first by mean FCIq under matched additional search. Its paired mean difference was +0.0021 [−0.0336, +0.0279], with a higher score in 21 shells, a tie in 3 and a lower score in 6. It reached adequacy in 5 of 30 training shells versus 2 for the catalogue and captured 7.4% of the observed bespoke gain. The couple's fixed kit reached adequacy on 3 of 15 held-out shells versus 0 for the catalogue, and 10 of 15 small observed plans versus 8. The corresponding mean FCIq contrasts were −0.0242 [−0.0946, +0.0315] and +0.0066 [−0.0040, +0.0181]. <!-- results/g3_review_k3/kit.yaml; results/g3_review_k3/paired_effects.csv -->

## Hong Kong scenario · Size-dependent adequacy

The couple's S1-to-S2 switching contrast under the shared quality rule was 2.24 m² [1.66, 2.82]. With the larger kit, the modeled Aₘᵢₙ was 15.39 m² [14.67, 16.19], versus 16.12 m² [15.70, 16.57] for the optimized catalogue. The two point estimates differ by 0.73 m². Across the modeled grid, 154 of 390 shells were adequate with the larger kit versus 132 with the optimized catalogue. <!-- results/g3_review/hong_kong/couple_switching.csv; results/g3_review_k3/hk_scenario_summary.csv; results/g3_review_k3/paired_effects.csv -->

At 13–16 m², the larger kit reached adequacy in 51 of 120 shells versus 30 of 120, a net gain of 21 adequate layouts. The counts for larger kit versus catalogue were 4 versus 0 at 13 m², 7 versus 2 at 14 m², 16 versus 10 at 15 m², and 24 versus 18 at 16 m². In the 8–12 m² band, both fit-outs reached adequacy on zero of 150 shells. The larger kit had lower mean FCIq there, 0.448 versus 0.500. At 17–20 m² the corresponding adequacy counts were 103 versus 102 out of 120. These size bands locate the adequacy gain and the loss of capacity in the smaller shells. <!-- results/g3_review_k3/hk_h3_size_bands.csv; results/g3_review_k3/hk_adequacy_by_size.csv -->

The census source records 215,709 residents, 107,371 households and 108,202 subdivided units in 33,658 quarters containing subdivided units. The scenario estimates describe the modeled shapes. <!-- results/scenario_hk/territory_context.csv; reports/schemas/D6.md -->
