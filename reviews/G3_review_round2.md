# Gate G3 review, round 2: B1 / K1 / K2 follow-up

**Reviewer:** Claude, 2026-11-15. **Package:** PR #3 (`codex/phase-11c-g3-fixes`, commit 8d8a800).

**Verdict: APPROVED WITH ONE REQUIRED FOLLOW-UP (K3).**

- PR #3 is merged as the record. B1, K1, the Hong Kong rescoring and the four [should] items are done correctly.
- One issue remains in K. My own round-1 instruction (K1 step 2) introduced an unequal search budget. The H3 conclusion now depends on it, and the selection rule hides an adequacy result that matters for the paper.
- K3 needs about 60 extra S2 solves plus reporting. After K3 is reviewed, continue to Phase 12.

## Accepted

- **B1.**
  - The production row is correct: 0.9428 mean FCI, best observed on 189/200 pairs, 0.0034 mean shortfall.
  - Paired contrasts (17/172/11 versus annealing) and the 11-case table match my recomputation.
  - The wording ("A's FCI values are achievable lower bounds under the tested budgets") is right.
- **K1 rescoring.**
  - q = 0.9 for the catalogue desk and table, 1.0 for the beds; 360 K and 3,510 HK layouts revalidated.
  - The full-quality numbers are kept as a sensitivity. Correct.
- **HK.**
  - Rescored S0/S1/S2 and the revised F10 (viewed) are fine.
  - Couple S1 → S2 switching: 2.24 m² [1.66, 2.82] under the common quality rule. This is a good paper number.
- **Shoulds.** All four are addressed: C adequacy AUC (labelled post hoc), pooled H2 boundary flag, 8 m² scope sentence, and the size–quality frontier table.

## [must] K3. Equal search effort in the kit ranking, and report adequacy alongside

**What happened.** The nine-vector ranking compares two different search pipelines:

- **Catalogue:** production layouts (greedy portfolio, shared incumbents, full budget) plus an extra warm-started 120 s quality solve.
- **The other eight vectors:** only the K search pipeline (single greedy start plus K chain).

This follows the literal wording of my K1 step 2, but it is not a like-for-like ranking. B shows that pipeline strength alone moves FCI by several hundredths.

**Why it matters.** My recomputation on the 30 frozen training shells (paired by shell; bootstrap 95% CI) splits by household.

**H1:** the catalogue is genuinely better than H1_kit_02.

| Measure | Result |
|---|---|
| Mean FCIq difference (kit − catalogue) | −0.030 [−0.058, −0.006] |
| Adequate on kit only / catalogue only | 0 / 6 |

That conclusion is robust.

**H3:** H3_kit_02 (desk 1.2 m, table 1.0 × 0.75 m, wardrobe 1.4 m, all q = 1) cannot be told apart from the catalogue on mean FCIq, and is adequate more often in every cohort.

| Cohort | n | Mean FCIq diff (kit − cat) [95% CI] | Kit better / equal / worse | Adequate: kit vs catalogue |
|---|---|---|---|---|
| Training (best saved kit layout per shell) | 30 | −0.0005 [−0.035, +0.026] | 21 / 3 / 6 | 5 vs 2 |
| Training (confirmation layouts) | 30 | −0.004 [−0.040, +0.023] | 20 / 3 / 7 | 4 vs 2 |
| Held out | 15 | −0.024 [−0.092, +0.034] | 9 / 2 / 4 | 3 vs 0 |
| Real ≤ 20 m² | 15 | +0.007 [−0.005, +0.018] | 7 / 3 / 5 | 10 vs 8 |
| HK shells (original S2-kit layouts vs revised optimized catalogue) | 390 | −0.023 | 184 / 71 / 135 | 154 vs 132 |

Further detail:

- Without the extra catalogue-only solve, the H3 ordering reverses. Rescored catalogue: 0.6227. Kit_02: 0.6317.
- In HK, kit_02's extra adequate shells are all at 13–16 m² (kit vs catalogue: 4/0, 7/2, 16/10, 24/18). Its lower mean comes from shells under 13 m², where larger furniture fits worse. For couples, 13–16 m² is exactly the policy-relevant range.
- One bookkeeping issue: `design_frontier.csv` takes the *first* duplicate search row per shell, not the best validated one. For H3_kit_02 this gives 0.6281 instead of 0.6317. Bespoke correctly uses the best.

**Required.**

1. **Equal search.**
   - Give the top non-catalogue vector per household (H1_kit_02, H3_kit_02) the same extra step the catalogue got. That is a warm-started `solve_quality` S2 run with the same 120 s budget, starting from that vector's best validated saved layout per training shell. That is 60 S2 solves.
   - Rank on the best validated layout per shell for every vector, and fix the duplicate handling in the frontier.
   - Keep the prespecified rule (mean FCIq) as the selection criterion.
2. **Report the H4 judgment with uncertainty.** For the catalogue vs the runner-up in each household, report:
   - the paired mean FCIq difference with a bootstrap CI;
   - the counts of shells where the kit is better, equal and worse;
   - adequacy counts per cohort, as in the table above.

   The plan says adequacy is "reported alongside". It must appear next to the selection result, not only in the frontier.
3. **HK row for H3_kit_02.**
   - Add H3_kit_02 as an explicit HK strategy row (S2 + larger kit). The original S2-kit layouts are valid under the common rule, because every factor is 1.
   - Show it next to the revised catalogue rows, with adequacy by size and A_min.
   - Do not re-solve unless step 1 changes the H3 selection. If it does, the selected-kit HK row becomes this row.
4. **Wording.**
   - H1: "the catalogue dimensions are best among the nine; H4 not supported."
   - H3, whatever step 1 gives: "mean quality-weighted capacity does not distinguish the catalogue from a larger-item kit; the larger kit is adequate on more shells in each cohort, concentrated at 13–16 m² in HK, at the cost of lower capacity below 13 m²."
   - The H4 row becomes "Not supported for H1; mixed for H3 (adequacy higher, mean FCIq and bespoke capture not)". If the parity run makes kit_02 rank first, state the selected kit and its bespoke-gain share instead.
   - Do not tune anything else.

Keep the outputs in a new `results/g3_review_k3/` directory so the round-2 evidence stays checkable.

## Note for the paper

This is a useful design result, not a footnote:

- A single-person kit gains nothing over standard dimensions.
- For couples, larger work and dining surfaces plus more storage trade capacity in the very smallest shells for more adequate homes at 13–16 m².

This tells manufacturers that the right kit depends on the target size band. That is the kind of incremental, actionable contribution the K experiment was meant to test.
