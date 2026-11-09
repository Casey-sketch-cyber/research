# Phase 7 review: A1 analysis and A2 sensitivity

Verdict: CHANGES_REQUESTED. **Re-solve H3 and H4** (configuration bug), revise the area-saving definition (analysis only), and redo A2 for H3 with mirrored access. Then continue with B, D, R, the ablations, C, K and HK without another stop before G3.

**Reviewer:** Claude, for the author · **Date:** 2026-11-09 · **Reviewed commit:** `9b18e35`

## 1. What's correct

- **E1–E4** are implemented as specified:
  - 123 units excluded (the 116 structural failures plus 7 with less than 50% of furnishable area reachable), 2,619 retained.
  - The rule was computed from empty rasters only.
  - The bias table shows excluded units are about 3 m² smaller.
  - The cause audit is honest: 8 of 20 sampled units are grid artefacts recoverable at 0.05 m. **Put this in the limitations:** at 0.10 m, oblique kitchen openings are disproportionately lost.
- The decomposition, bootstrap and figure code is correct. F4b now shows real plans and generated shells separately, as asked.
- A2's reporting of negative changes is exemplary.

## 2. Must-fix items

1. **[must] F1: Configuration bug (the reviewer's error): only one static single bed.**
   - `furniture.yaml` capped every item at one instance unless listed otherwise. Under S0, H4 (two separate `sleep_1` demands) can therefore never serve the second sleeper. Its S0 FCI is capped at 20/28 = 0.714 in every home. The reviewer confirmed it: the S0 curve maximum for H4 is 0.705–0.714 in every source, and no H4 unit reaches 1.0.
   - H4's "form effect" of about +0.26 at 30–50 m² in F4b is therefore mainly an **artefact**: S1/S2 get the second bed from `wall_bed_single`.
   - H3 is affected too, more mildly: S0 couldn't use two single beds.
   - **Fixed by the reviewer** in `config/furniture.yaml` (`single_bed: 2`, `wall_bed_single: 2`; D-40).
   - **Re-solve all evaluable units for H3 and H4 × S0/S1/S2** with the frozen production settings. H1/H2 need one sleeping place, so they're unaffected and need no re-solve; verify that by showing that their candidate tables and objective bounds are unchanged.
   - Then rerun every A1 analysis that involves H3/H4.

2. **[must] F2: Revise the area-saving definition (the reviewer's error in RESEARCH_PLAN §3; analysis only).**
   - As defined, FEA(u) = f₀⁻¹(FCI_S2(u)) − A(u) compares a unit's S2 score with the **average** static home. That has two consequences:
     - (a) most units with FCI = 1 are right-censored, because the mean curve tops out at 0.98–0.99;
     - (b) units that are worse than average get *negative* "savings" even when transformation helped. The reviewer recomputed this: the uncensored D1 single-person medians are −15 to −25 m².
   - Replace it with a **paired equivalent-area gain**: ΔEA(u) = f₀⁻¹(FCI_S2(u)) − f₀⁻¹(FCI_S0(u)). Both inverses are taken on the **same** curve, and ΔEA = 0 when the two scores are equal. The unit's own geometry cancels out.
   - Fit f₀ as the **median** S0 FCI per 2 m² NIA bin, made monotone with a cumulative maximum and linearly interpolated, so the curve can reach 1.0. Keep the mean isotonic curve as a sensitivity check.
   - Treat values above the curve's maximum as right-censored, with their lower bound reported.
   - Report:
     - the share of units already fully functional under S0 (no saving possible);
     - the share with a gain;
     - the median ΔEA among units with a gain, by household × source × 2 m² bin.
   - The reviewer is updating RESEARCH_PLAN §3 to match.

3. **[must] F3: Redo A2 for H3, with either-side access.**
   - The fixed-left implementation removes access options (no mirrored families), so it isn't a relaxation. That explains why H3's time effect *fell* (0.069 → 0.046).
   - Implement the intended variant: for each affected double sleeper, provide **left-access and right-access mirrored variants** (each with a 0.60 m strip on its own side only), and let the solver choose.
   - **H3 only:** H4 never deploys a double sleeper, so A2 doesn't affect it.
   - Run it on the same small-unit set after F1, with the small-home settings. Keep the current A2 results as a documented superseded run.

## 3. Should-fix items

- **[should] S1: Statistical tests.** S2 ≥ S1 ≥ S0 holds by construction, so the Wilcoxon p-values and rank-biserial = 1.0 carry no information. Report the mean difference with a bootstrap CI and the share of units improved as the primary statistics. Keep the tests in the supplement, with a note explaining this.
- **[should] S2: Minimum adequate area.** For single-person households, A_min can't be identified on the real plans, because almost every real home from 16.7 m² up is adequate with fixed furniture. **That is itself a result: report it.** Estimate A_min where inadequate units exist (D3, and pooled) and label it clearly as such.

## 4. Order of work

1. F1 re-solve (H3/H4)
2. F2 re-analysis
3. F3 A2 for H3
4. Exp. B (use the corrected configuration; the frozen B sample stays, with its H3/H4 instances taken from the re-solve)
5. D, R, ablations
6. C
7. K (H1 + H3, per D-39)
8. HK scenario
9. Literature screening
10. G3 package

**The substantive pattern so far** (to be confirmed after F1): for couples in real plans, the time effect dominates from 16 to 30 m². For single people, gains are small except in generated shells under 16 m².
