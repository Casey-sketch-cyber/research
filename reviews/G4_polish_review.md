# G4 polish review (PR #6)

**Reviewer:** Claude, 2026-11-15. **Package:** PR #6 (`codex/phase-12c-polish`, commit ac8b449). **Verdict: APPROVED, merged.**

All six non-blocking items from `reviews/G4_review.md` are addressed:

1. **Table links.** No backslash links remain in T1–T7. T7 uses reader-facing comparator names.
2. **Comparator sources.** I checked both against the source documents:
   - Ulrich, K.T. (2025), "Minimum Spatial Housing Requirements for Human Flourishing", *Buildings* 15(15) 2623, doi:10.3390/buildings15152623. Its abstract proposes 30/45/60 m² for one-, two- and three-person households.
   - Basic Housing Units Ordinance (Ord. No. 41 of 2025), Schedule 1 s.1(1): "The internal floor area of the subdivided unit must be at least 8 m2". The bhu.gov.hk PDF is the cited source.
   - When writing, note that Ulrich's 60 m² applies to three persons, and that the Ordinance mostly commenced on 1 March 2026.
3. **F5 small bins.** Grey markers for bins with fewer than 10 pairs. The 16.6 m² lower bound versus the 8.2 m² pooled-reference sentence is in Results and matches `g3/area_summary.csv`.
4. **F9.** The axis now reads "median identified ΔEA", with a note that the improved subset is specific to each condition.
5. **Renders.**
   - The 10 m² cut-away now shows the furniture.
   - The 29.97 m² main-room details are readable.
   - Both captions state TB = 0.
6. **HK sentences.** The H1 (13.40 → 12.37 m²) and H4 (19.58 → 17.07 m²) S0 → S2 A_min values match `g3_review_k3/hk_scenario_summary.csv`.

Optional caption point for the author: in the 10 m² couple showcase, no double sleeping surface is deployed in any slot. The FCI of 0.58–0.69 reflects this, and saying so explains why switching cannot help there.

The computational package is complete. Further changes come from paper writing.
