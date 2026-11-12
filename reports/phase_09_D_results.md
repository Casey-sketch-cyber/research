# Phase 9 — Conventional-indicator comparison results

## Completed analyses

All 2619 evaluable units and 10476 unit-household pairs are retained from corrected F1. S0 and S2 use independent-validator FCI, with valid zero scores retained. No new solves were performed. Numerical analysis took 3.296 seconds after B acceptance.

- PASS: full B saved-layout audit and its hashes verified before analysis.
- PASS: corrected F1 acceptance, configuration, sample membership and geometry metadata verified.
- PASS: continuous associations, 2 m²-bin IQR, configured fixed-threshold confusion matrices and complete unselected threshold sweeps exported.
- PASS: every confusion row sums to its available sample; missing continuous values are counted explicitly.

## Real-plan NIA correlations

| household               | strategy   |   n_valid |   spearman |
|:------------------------|:-----------|----------:|-----------:|
| H1_single_commuter      | S0         |      2109 |   0.040572 |
| H1_single_commuter      | S2         |      2109 |  -0.012229 |
| H2_single_remote_worker | S0         |      2109 |   0.078358 |
| H2_single_remote_worker | S2         |      2109 |  -0.055681 |
| H3_couple_one_remote    | S0         |      2109 |   0.464685 |
| H3_couple_one_remote    | S2         |      2109 |   0.345993 |
| H4_parent_child         | S0         |      2109 |   0.546433 |
| H4_parent_child         | S2         |      2109 |   0.416279 |

## Real-plan fixed-threshold confusion

Truth-positive means model FCI ≥ 0.95; predicted-positive means NIA at or above the configured area rule. TP/TN/FP/FN use this orientation. These are model-agreement comparisons, not legal compliance findings.

| household               | strategy   | indicator        |   threshold_m2 |    n |   tp |   tn |   fp |   fn |   misclassification_rate |
|:------------------------|:-----------|:-----------------|---------------:|-----:|-----:|-----:|-----:|-----:|-------------------------:|
| H1_single_commuter      | S0         | ulrich_threshold |      30.000000 | 2109 | 1787 |   16 |  135 |  171 |                 0.145092 |
| H1_single_commuter      | S0         | hk_bhu_8m2       |       8.000000 | 2109 | 1958 |    0 |  151 |    0 |                 0.071598 |
| H1_single_commuter      | S2         | ulrich_threshold |      30.000000 | 2109 | 1883 |    7 |   39 |  180 |                 0.103841 |
| H1_single_commuter      | S2         | hk_bhu_8m2       |       8.000000 | 2109 | 2063 |    0 |   46 |    0 |                 0.021811 |
| H2_single_remote_worker | S0         | ulrich_threshold |      30.000000 | 2109 | 1736 |   28 |  186 |  159 |                 0.163585 |
| H2_single_remote_worker | S0         | hk_bhu_8m2       |       8.000000 | 2109 | 1895 |    0 |  214 |    0 |                 0.101470 |
| H2_single_remote_worker | S2         | ulrich_threshold |      30.000000 | 2109 | 1870 |    5 |   52 |  182 |                 0.110953 |
| H2_single_remote_worker | S2         | hk_bhu_8m2       |       8.000000 | 2109 | 2052 |    0 |   57 |    0 |                 0.027027 |
| H3_couple_one_remote    | S0         | ulrich_threshold |      45.000000 | 2109 |  814 |  303 |   52 |  940 |                 0.470365 |
| H3_couple_one_remote    | S0         | hk_bhu_8m2       |       8.000000 | 2109 | 1754 |    0 |  355 |    0 |                 0.168326 |
| H3_couple_one_remote    | S2         | ulrich_threshold |      45.000000 | 2109 |  841 |   93 |   25 | 1150 |                 0.557136 |
| H3_couple_one_remote    | S2         | hk_bhu_8m2       |       8.000000 | 2109 | 1991 |    0 |  118 |    0 |                 0.055951 |
| H4_parent_child         | S0         | ulrich_threshold |      45.000000 | 2109 |  800 |  454 |   66 |  789 |                 0.405405 |
| H4_parent_child         | S0         | hk_bhu_8m2       |       8.000000 | 2109 | 1589 |    0 |  520 |    0 |                 0.246562 |
| H4_parent_child         | S2         | ulrich_threshold |      45.000000 | 2109 |  844 |  153 |   22 | 1090 |                 0.527264 |
| H4_parent_child         | S2         | hk_bhu_8m2       |       8.000000 | 2109 | 1934 |    0 |  175 |    0 |                 0.082978 |

## Scope, missing cutoffs and limitations

Pooled, D1+D2 real-plan, D1, D2 and D3 tables remain separate. Pooled observations combine actual homes and generated shells and are not population weights. Spearman is undefined for constant inputs or fewer than three observations; no zero correlation is fabricated. IQR uses linear empirical quartiles, with singleton bins flagged.

The plan supplies 30/45/60 m² household-size thresholds and an 8 m² total-area comparison, but does not supply adequacy cutoffs for area/person or rooms/person. The latter are reported continuously and as all distinct observed-threshold confusion sweeps at the primary FCI threshold, plus the all-negative endpoint. No optimal cutoff is selected, and no unsourced housing rule is invented. The two specified rules are also evaluated at the configured FCI threshold sensitivities.

The corpus starts at approximately 8 m², so the 8 m² rule has essentially no negative-prediction support in this selected corpus; its limitations are visible in the confusion matrices. Rooms mean harmonized furnishable/habitable spaces, not bedrooms or a jurisdiction-specific census definition. Within a household, NIA and NIA/person have identical rank ordering by construction. These comparisons do not establish causal superiority or independent real-world validation of the FCI model.

No project/furniture/household defaults changed. Q31 records the threshold gap. Next: R and the prespecified ablations, then C, reduced K, HK and remaining literature screening before G3.

Reproduce: PYTHONPATH=src:scripts python scripts/09_run_expD.py
