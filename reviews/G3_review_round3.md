# Gate G3 review, round 3: K3

**Reviewer:** Claude, 2026-11-15. **Package:** PR #4 (`codex/phase-11d-k3`, commit b93a86d).

**Verdict: APPROVED.** Gate G3 is closed. PR #4 is merged. Continue to Phase 12 (G4).

## Checked

- **Equal extra search.** H1_kit_02 and H3_kit_02 each got 30 warm-started S2 solves with the 120 s cap, so 60 in total. All 60 passed validation (`warm_start_s2.csv`).
  - H3_kit_02 did not improve: 0.6344 before and after. Its saved layouts were already at the solver's limit, so the round-2 asymmetry did not hide a larger kit gain.
  - H1_kit_02 moved from 0.6827 to 0.6843.
- **Ranking.** It uses the best validated layout per vector and shell, which fixes the first-duplicate issue. The frontier ordering and the bespoke shares are consistent.
- **Paired effects.** H3 equal effort gives +0.0021 [−0.034, +0.028], 21/3/6 kit higher/equal/lower, and 5 vs 2 adequate. The held-out and real rows match my round-2 recomputation.
- **HK by size.** 13–16 m² gives 51/120 vs 30/120. This matches my per-size recount: 4/0, 7/2, 16/10, 24/18. The larger kit's A_min is 15.39 m² [14.67, 16.19], against 16.12 [15.70, 16.57] for the optimized catalogue.
- **Wording.** The H4 row reads "Not supported for H1. Mixed for H3", with adequacy reported next to the selection rule. This is as requested.

## Notes for Phase 12 (no further G3 action)

1. **Figures.** Regenerate F10 with the H3 larger-kit series, and F12 with the K3-selected vectors. The current F10 link is the round-2 version without the larger kit.
2. **H1 wording in the paper.** H1_kit_01 "ranks first" by +0.0013 [−0.015, +0.020]. That is a tie with fewer adequate shells, and in HK it is clearly worse (184 vs 246 adequate). Write that no tested kit dimension improves on the catalogue for the single commuter. Don't present H1_kit_01 as a recommended kit.
3. **H3 framing for the paper.**
   - The larger kit lowers the HK couple A_min by about 0.7 m².
   - It makes 21 more shells adequate at 13–16 m².
   - It costs capacity below 13 m².
   - Present this as a size-band-dependent design choice.
4. **Decision log.** Record in `reports/DECISIONS.md` that H3's "selected kit" rests on a mean-FCIq ranking whose paired interval includes zero.
