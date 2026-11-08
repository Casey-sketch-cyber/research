# Phase 7 review: Experiment A acceptance

Verdict: CHANGES_REQUESTED, but no re-solve is needed. Apply the evaluability rule below, then continue with the analysis and the remaining experiments without another stop before G3.

**Reviewer:** Claude, for the author · **Date:** 2026-11-08 · **Reviewed commit:** `0e93aa4`

## 1. Assessment

The run was executed well, and stopping at final acceptance was correct:
- 32,904/32,904 solves finished in 25.4 h, within the 26.1 h projection and the 36 h budget.
- The round-3 launch acceptance passed with a fresh reference: per-source mean loss ≤ 0.006, and small homes +0.003.
- There are **0 strategy-ordering failures**.
- All 1,392 invalid cases are confined to **116 units** (D1 105, D2 11; 4.2% of 2,742). In each of them, every case is empty, structurally unreachable, and fails only fixed-service access. The set matches exactly the units flagged by the earlier full-sample connectivity audit.

The reviewer recomputed these facts from `solutions.csv` and `structural_failure_units.csv`. There are no invalid cases outside the 116 units, and no valid cases inside them.

The failure is in **evaluability**, not in the method. If a dwelling's bathroom or kitchen can't be reached even when it's empty, the dwelling can't be scored for any strategy. Not checking the full-sample connectivity record before launch was an oversight in the launch gate, as Codex itself notes. It costs nothing scientifically, because exclusion is independent of furniture and applies identically to all strategies.

**Valid zero-score cases (154):** the reviewer checked these too.
- **D3 8–9 m² shells** (67 cases): genuine. Their relaxed capacity bound is low (0–0.26) and the essential furniture doesn't fit. **Keep them**: they matter for the Hong Kong 8 m² question.
- **Seven D1 units** (NIA 16–50 m²) score 0 for every household and strategy, although their relaxed bound is mostly > 0. This points to furnishable rooms that are disconnected from the entrance in the empty raster, which is the same family of problem as the 116 units.

## 2. Must-fix items

1. **[must] E1: An evaluability rule, decided before any outcome analysis.** A unit is **evaluable** if, in the **empty** dwelling at the main walking width (0.60 m):
   - (a) every fixed-service target (sanitary approach and kitchen walkable cells) is reachable from the entrance, and
   - (b) at least 50% of the furnishable floor area is reachable (covered by the walking disc, or adjacent to covered cells within one clearance depth of 0.60 m).

   Compute it from the empty raster only: no furniture, no solver outputs, no FCI. Apply it to every unit in the frozen sample. Write `results/expA/evaluability.csv` (unit_key, source, nia_m2, a_pass, b_reachable_share, evaluable, reason).

   Analyses use evaluable units only, with all strategies and households of an excluded unit dropped together. The 116 units must fail (a); report how many of the seven D1 zero units fail (b). Units that pass E1 but still score zero stay in the analysis as genuine zeros.

2. **[must] E2: Cause audit, with no repair.** Draw a fixed-seed random sample of 20 excluded units (or all of them, if fewer than 20). Render the empty raster with the entrance, the walking coverage and the unreachable targets. Classify each cause as one of:
   - conversion of doors or openings
   - rasterization (a passage that narrows below 0.60 m only on the grid)
   - a genuinely narrow passage in the source drawing
   - other

   Report the counts in the paper's limitations. **Don't repair geometry or relax rules for this paper**, because there isn't time. A repair can come in follow-up work.

3. **[must] E3: Bias check on the exclusion.** Excluded units are somewhat smaller. The reviewer computed mean NIA of 36.5 m² for excluded D1 units against 39.2 m² retained, and 34.8 against 44.5 m² for D2 (n = 11). Report the NIA, room-count and source distributions of excluded against retained units (table plus histogram). Results are reported by 2 m² NIA bin, so the bin-level estimates are protected. Pooled means must state the composition shift.

4. **[must] E4: Make the analysis gate read the evaluability list.** `07_decomposition.py` and the FEA/A_min scripts currently require every case to be valid and the full expected count. Change them to require: (i) every *evaluable* unit has all 3 strategies × 4 households and passes the validator; (ii) the number excluded equals the E1 count. Fail loudly otherwise. Keep the strict ordering check.

## 3. Then continue (no stop before G3)

In this order:
1. **A1 analysis on evaluable units:** f₀ curves, FEA, saving curves, A_min with bootstrap CIs, paired tests, the form/time decomposition with F4b, and showcase layouts.
2. **A2:** the one-side double-bed sensitivity.
3. **Exp. B (footprint greedy only, per B1), Exp. D, analysis R and the ablations.**
4. **Exp. C.**
5. **Exp. K** (scope as the author decides; see §4).
6. **The HK scenario.**
7. **Remaining literature screening, then the G3 package.**

The time budget is ahead of plan: day 4 of 21, with A's solves done.

**[should] S1:** in F4b and the saving curves, show real plans (D1 + D2) and generated shells (D3) as separate panels or series alongside the pooled result. D3 is a designed grid, not a population sample, so pooled means mix the two kinds of evidence.

## 4. Experiment K scope (for the author)

D-38 restricts K to H1/H2 (both single-person households). The round-2 pilot found the **time effect only in two-person households** (H3, H4). With H1/H2 only, K can't show how kit dimensions interact with time-sharing, which is the most interesting design question.

**Reviewer recommendation:** use **H1 + H3** instead of H1 + H2, at about the same workload, so the kit is tested for a single person and a couple. This needs the author's confirmation, because D-38 is an author decision. Until the author confirms, keep D-38 as recorded.

**Author decision (2026-11-09):** confirmed. Exp. K uses **H1 + H3** (D-39, `config/execution_policy.yaml`). If the K runtime pilot exceeds the two-day limit, reduce the training shells (30 → 24 → 18) before dropping H3.
