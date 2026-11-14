# G3 response to results review

The original G3 evidence was accepted and merged in PR #2. This follow-up addresses B1, K1, K2 and the four recommended reporting changes. [Claude review](../reviews/G3_review.md) · [Revised G3 report](GATE_G3.md)

| Review item | Change and verification |
| --- | --- |
| B1 | Added the accepted production result on all 200 matched pairs, the sum of S0/S1/S2 solve times, three paired contrasts and all 11 shortfalls. The standalone S2 CP-SAT implementation supplies no accepted cross-strategy layout and does use its internal greedy initializer. [Four-method summary](../results/g3_review/benchmark/algorithm_summary.csv) · [Paired effects](../results/g3_review/benchmark/production_paired_effects.csv) · [Shortfalls](../results/g3_review/benchmark/production_shortfalls.csv) |
| K1 | Used q = 0.9 for the catalogue fold-down desk and drop-leaf table, q = 1 for both catalogue wall beds and the configured wardrobe capacity. Revalidated and rescored 360 K and 3,510 HK catalogue layouts. Reoptimized 120 K S2 cases from the validated catalogue chain. [Saved K scores](../results/g3_review/catalogue/k_rescored.csv) · [Optimized K scores](../results/g3_review/catalogue/k_optimized.csv) · [Saved HK scores](../results/g3_review/catalogue/hk_rescored.csv) |
| K1 and K2 | Ranked the nine vectors on the frozen training shells, reevaluated the selected kit on all K cohorts, and included the optimized catalogue and confirmed kit in the per-shell bespoke comparator. Updated the H4 judgment and the HK result rows. The original comparison remains available as the catalogue-at-full-quality sensitivity. [Frontier and rankings](../results/g3_review/kit/design_frontier.csv) · [Kit comparisons](../results/g3_review/kit/comparison.csv) · [Revised Hong Kong results](../results/g3_review/hong_kong/scenario_summary.csv) |
| HK switching | Estimated the couple's S1-to-S2 area difference from paired shape resamples under both catalogue scoring rules. [Switching contrast](../results/g3_review/hong_kong/couple_switching.csv) |
| C | Added post-hoc adequacy ROC AUC from the frozen predictions. The prespecified Spearman criterion remains the basis for H3. [AUC table](../results/g3_review/benchmark/c_adequacy_auc.csv) |
| H2 and 8 m² rule | Flagged the pooled H2 estimate as boundary-limited, reported the supported D3 estimate and clarified that the real-plan sample does not reach the 8 m² boundary. [Area and indicator results](GATE_G3.md) |

The original experiment inputs, layouts and acceptance receipts remain available. The catalogue receipt records a path-only normalization of its execution driver. It preserves the recorded execution fingerprint and the exact result bytes. The four review acceptance files and the current figure checks are included in the G3 evidence manifest. [Manifest](../results/g3/evidence_manifest.json)

The revised package is ready for the follow-up review before Phase 12.
