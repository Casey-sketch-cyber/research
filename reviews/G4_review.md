# Gate G4 review: final package

**Reviewer:** Claude, 2026-11-15. **Package:** PR #5 (`codex/phase-12-g4`, commit 5c40cea).

**Verdict: APPROVED.** PR #5 is merged. The computational work is complete, and the author can start writing the paper from `manuscript/` and `reports/FINAL_SUMMARY.md`. The polish items below are not blocking. Do them in one small PR (`codex/phase-12c-polish`) while the paper is drafted. I will review that PR on its own.

## Checked

- **Drafts versus evidence.**
  - Methods, Results and FINAL_SUMMARY numbers agree with the accepted G3 outputs. I spot-checked these:
    - the D3 couple bin medians: 0.75 m² (9.2% of NIA) at 8–10 m², rising to 7.32 m² (49.8%) at 14–16 m²;
    - the parent-and-child values of 0.69 and 6.00 m²;
    - the A primary effects;
    - the T4 identified and bound-only counts (they sum to the 7.5/8.7/23.5/35.9% improved shares);
    - the T5 solver table;
    - the K3 and HK figures.
  - None of the drafts claims to be "first" or "novel".
  - The H1 kit wording follows the G3 round-3 note. The H3 kit is presented with its interval and as a trade-off between size bands.
- **Data sources in the figure and table scripts.**
  - Area results come from `g3/area_summary.csv` and `analysis_p1`. The superseded F2 area summaries are not used.
  - Kit and HK results come from `g3_review_k3`.
  - F9's "median gain" is the identified-positive ΔEA. Only the old column name `median_saving_m2` remains.
- **Figures F1–F12 and F3b (all viewed).**
  - They are readable, consistent with the tables, and colour-safe.
  - F10 now shows the larger couple kit and the 13–16 m² band. F12 shows the K3 dimensions with training and transfer tables.
- **3D stills (all 30 viewed).**
  - State changes are visible where TB > 0. For example, in showcase_18 the double wall bed is deployed at night and stowed by day.
  - The audited outline error is ≤ 2.79 mm.
- **Privacy.**
  - The PR removes the GPU model strings from the config, docs and environment reports.
  - No personal paths, e-mail addresses or host names were found in the diff.
  - Earlier commits still contain the GPU strings. We do not rewrite history; this is acceptable.

## Polish items [should], non-blocking

1. **Broken links in the tables.** T1, T2 and T4–T7 link with Windows separators (`../../../results\corpus\counts.csv`), which GitHub cannot resolve. Emit POSIX paths in `12_make_tables.py`.
2. **Comparator sources.** The Methods draft names the 30/45 m² and 8 m² comparators without sources. Attribute them to Ulrich (2025) and to Hong Kong's basic-housing-unit minimum, both in RESEARCH_PLAN §10. Rename the code label `ulrich_threshold` in T7 to a reader-facing name.
3. **F5 small-bin support.**
   - The observed-plan couple peak at 16–18 m² rests on 6 units, and its upper bound is unbounded.
   - The real-plan reference gives 16.6 m² there, while the pooled reference gives 8.2 m².
   - In F5, mark the bin counts or grey out bins with fewer than 10 units.
   - Add one Results sentence reporting the pooled-reference sensitivity for the smallest observed bins.
4. **F9 axis label.** Change "Change in median gain" to "Change in median identified ΔEA". Add a caption note that this median conditions on the improved subset, which can change between conditions.
5. **Renders.**
   - In showcase_10, the fixed service block in the foreground hides most of the room. Use a cut-away or translucent material for fixed-service volumes, or move the camera.
   - Showcase_30 shows the whole flat at a scale where the furniture is hard to read. Add a closer view of the main room.
   - Where an S2 scene has TB = 0 (showcase_10, showcase_30), say in the caption that the states do not change, so readers don't look for a difference.
6. **HK results in the draft.** The Results text covers only the couple. Add one sentence each for the commuter and the parent and child (S0 versus S2 A_min, or adequacy counts) from `hk_scenario_summary.csv`.

## For the author

The drafts are evidence-linked notes, not finished prose. When writing:
- give the HTML comments' sources as figure and table references;
- move the methodological detail on support bounds into a short appendix;
- keep the headline story: most plans already work with static furniture; the gains concentrate in two-person households at about 12–30 m²; area thresholds misclassify about half of two-person cases; switching is worth about 2.2 m² for HK couples; and the right kit depends on the size band.
