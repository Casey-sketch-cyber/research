# Submission package v1 review (PR #17)

**Reviewer:** Claude, 2026-11-19. **Verdict: APPROVED as v1, merged.**

The package is well built:

- native Word equations (267), editable tables, line numbers;
- every citation matched in both directions;
- no stray placeholders;
- separate figure files under 2 MB;
- a regenerable build (`scripts/13_*`);
- an honest ISSUES.md.

Several issues need **package v2** on `codex/submission-package-v2`.

## Text fixes already made by Claude on `main` (commit after 133cd97)

Rebuild from the current `paper/manuscript.md`:

- The title options are removed from the title page (ISSUES 1).
- Former Figure 6 panel G (kit dimensions and training/transfer tables) moves to the supplement as **Figure S5**. Figure 6 now has panels A–F and points to Figure S5 and Table S3.
- **Supplements are renumbered in order of first citation** (ISSUES 4–5):

  | Old number | New number |
  |---|---|
  | Figure S5 (sensitivity) | Figure S4 |
  | Figure 6G (kit) | Figure S5 |
  | Figure S6 (room comparison) | Figure S6 (unchanged) |
  | Figure S4 (surrogate) | Figure S7 |
  | Table S4 (kits) | Table S3 |
  | Table S3 (surrogate) | Table S4 |

  The legend blocks are reordered to match. I checked that first-citation order is now S1→S7 and Table S1→S4. No result number changed.
- The sensitivity legend (now Figure S4) lists the solver limits as 30, 60 and 120 s (ISSUES 3).

## Required in package v2

1. **Figure 6.**
   - Drop panel G. Figure 6 = panels A–F only, 174 mm wide, at most about 200 mm tall.
   - Put panel G in the supplement as Figure S5.
   - In that panel, replace the internal IDs ("H1 H1_kit_01 · ranking only, retain catalogue", "H3 H3_kit_02 · largest observed mean") with reader labels: "Single commuter: top-ranked compact kit (not adopted)" and "Couple: larger kit".
2. **Figure text size** (ISSUES 8). Labels of 3.8–5.7 pt are too small for print. Re-render Figures 2–6 and the supplementary data figures from the committed plotting code at their final width (174 mm, or 85 mm for single-column panels), so that every label, tick and legend entry is 6.5–7 pt (minimum 6 pt). The data, colours and layouts stay the same; only the size and font scaling change. Do not upscale raster images of the old plots.
3. **Graphical abstract fonts** (ISSUES 7). Follow the Cell Press guide: Arial at 12–16 pt on the 5.5-inch canvas.
   - Body text and card text at least 12 pt (≈50 px at 300 dpi).
   - Column headers 14 pt.
   - Title 16 pt.
   - "+3.5 m²" may stay larger as the single highlighted callout.

   Keep the approved layout and wording. Allow line wraps. Update the PPTX in `paper/figures/fig1/` and the submission copies.
4. **Rebuild everything** from the updated manuscript: Manuscript.docx/pdf (with the review copies of Figures 1–6 at the end), SupplementalInformation.pdf in the new S1–S7 / S1–S4 order, CHECKLIST.md and ISSUES.md.

The rule from v1 still holds: do not change wording or numbers. Report anything else in ISSUES.md.
