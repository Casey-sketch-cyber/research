# Phase 7 review: corrected F1/F2/F3

Verdict: APPROVED. Continue with B → D, R, ablations → C → K → HK → literature screening → G3, without stopping. One reporting fix (P1) is required in the A1 tables before G3.

**Reviewer:** Claude, for the author · **Date:** 2026-11-11 · **Reviewed commit:** `40c07a0`

## 1. Verified independently

- **F1 (H3/H4 re-solve):** the reviewer recomputed from `results/expA_f1/solutions.csv`: 31,428 cases on 2,619 evaluable units, all valid, 0 ordering failures. H4's S0 mean rose from 0.672 to 0.899 and its maximum now reaches 1.0, so the single-bed cap is gone.
- **Real-plan primary effects** (D1+D2) match the report exactly:

| Household | Fully functional under S0 | Form (S1 − S0) | Time (S2 − S1) | Share improved |
|---|---|---|---|---|
| H1 single commuter | 90.8% | 0.0085 | 0.0002 | 7.5% |
| H2 single remote worker | 89.1% | 0.0107 | 0.0001 | 8.7% |
| H3 couple | 72.7% | 0.0130 | 0.0112 | 23.5% |
| H4 parent and child | 61.0% | 0.0271 | 0.0017 | 35.9% |

- **Code:** the `instance_groups` family cap is enforced separately in the solver (`cpsat.py`) and in the validator (`validate.py`), so the validator stays independent. Approved.
- **F3 (mirrored access):** the analysis is correct and honestly reported. **Interpretation:** allowing one-side access does **not** increase the time effect. Pooled it falls slightly (−0.012; CI −0.020 to −0.004), because the variant reserves less space but also removes the second access side. Conclusion for the paper: **the main results are not an artefact of the strict two-side double-bed rule.** Report F3 as a robustness check, and state that the variant changes both reserved space and access options. No further variants.

## 2. Must-fix item

**[must] P1: Label lower-bound area gains.** When a unit's S0 score lies below the curve's lowest observed point, `ea_S0` sits at the **lower support boundary**, and ΔEA is then only a **lower bound**. The summary currently counts these values as "uncensored". The reviewer's check (real plans, median curve):

| Household | Units with a gain | Gains at the lower boundary | Median ΔEA |
|---|---|---|---|
| H1 single commuter | 143 | **143 (100%)** | 2.0 m² (all of these are the curve span of 17–19 m²) |
| H2 single remote worker | 180 | 20 | 1.33 m² |
| H3 couple | 484 | 36 | 6.21 m² |
| H4 parent and child | 747 | 26 | 5.00 m² |

So for H1 on real plans, "2.0 m²" is an artefact of support: there are no real homes below about 17 m², and the median static curve reaches 1.0 at 19 m².

In `area_gain_summary.csv` and in every report or figure:
- split gains into *identified* and *lower bound*;
- report the median ΔEA over identified gains only, plus the count of lower-bound gains;
- write H1/H2 real-plan values as "≥" with an explanation.

Also add the pooled-curve inversion (support 8–50 m²) as a sensitivity check for real-plan units. Analysis only; no re-solve.

## 3. Findings to carry into the paper (subject to the remaining experiments)

- In real compact homes (17–50 m²), **most homes are already fully functional with fixed furniture**: 61–91% depending on household. Transformable furniture matters for a minority, and that minority is larger for two-person households.
- **Couples** are the only household where switching during the day (the time effect) is as large as the gain from compact pieces (the form effect): 0.011 against 0.013 on average. Among homes with a gain, the median equivalent-area gain is about 6 m².
- **Parent and child:** almost all of the gain comes from compact transformable pieces (form 0.027, time 0.002). The median equivalent-area gain is about 5 m².
- **Single people:** gains are rare (7–9% of real homes) and small. Larger effects appear only in generated shells under about 16 m².

## 4. Continue

Follow the order in `phase07_review_A1A2.md` §4 from Exp. B onwards. P1 can be done alongside B. G3 is the next stop.
