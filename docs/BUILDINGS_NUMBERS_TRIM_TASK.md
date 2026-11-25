# Buildings revision: fewer numbers in the running text

**From:** Claude, 2026-11-25. **For:** Gemini (Stage 1b), then Codex (Stage 2b).

## Why

The text is accurate, but it reads like a results table. *Buildings* readers are architects and housing researchers. They need the message of each paragraph and the two or three numbers that carry it, not every count, interval and bound. Every detailed number is already in a table, figure or supplement.

Numbers per 100 words in the current `paper/buildings/manuscript.md` (prose only, without tables and captions):

| Part | Numbers / 100 words | Target |
| --- | ---: | ---: |
| Introduction | 2.6 | keep |
| Methods 2.1–2.11 | 4–16 | keep (parameters are needed to reproduce the work) |
| Results 3.1–3.6 | 13–22 (3.3: 19.8; 3.6: 21.7) | about 8 or fewer |
| Discussion 4.2 | 11.2 | 5 or fewer |
| Conclusions | 10.6 | 5 or fewer |

## Stage 1b: Gemini

**Branch:** `gemini/buildings-numbers-trim`, from `main`. Open a PR; do not merge. Edit only `paper/buildings/manuscript.md`, the cover letter (only if it repeats something you cut), `claims_map.md` and `NOTES_FROM_WRITER.md`.

### Rules

1. **Each Results paragraph opens with its message** in words, then gives the numbers that support it. As a rule, use no more than two numbers per sentence.
2. **Keep in the text:**
   - the headline point estimates (S0 full-function shares; improved shares; median identified ΔEA per household; A_min changes; the 45 m² and 8 m² disagreement rates; the Hong Kong switching value 2.24 m² and the kit A_min 15.39 vs 16.12 m²);
   - the 95% CI only for the three median ΔEA values and the Hong Kong switching value.
3. **Move to the table or figure** (write "Table 3" or "Figure 4" instead):
   - counts in brackets such as "(159 of 2109)": keep the percentage;
   - "n identified plus bounded" details and the "lower bound ≥" restatements;
   - secondary CIs;
   - per-bin values beyond the peak and the 8–10 m² value;
   - kit-by-kit counts.

   A number may leave the text **only if it appears in a main table, figure, figure caption or the supplement.** If it appears nowhere else and the paragraph's claim needs it, keep it.
4. **Discussion 4.1–4.3 and Conclusions:** state findings in words and point back to the Results section ("Section 3.3"). Keep only the few headline numbers a reader would quote.
5. **Methods:** leave as is, except delete numbers that merely repeat Results.
6. **Do not add, recompute or re-round any number.** Do not change the abstract except to cut a number, if it reads better. Keep every figure and table callout.
7. **CP-SAT:** expand it once at first use in the main text: "the CP-SAT (constraint programming–Boolean satisfiability) solver of Google OR-Tools". "LTS" in "Blender 4.5.3 LTS" is part of the product name; leave it.
8. Report the before and after numbers-per-100-words for each section in `NOTES_FROM_WRITER.md`, and list every number you moved out of the text together with where it still appears.

## Stage 2b: Codex

**Only after Claude merges Stage 1b.**

1. Rebuild with the committed `scripts/15_*` on branch `codex/buildings-package-v2`.
2. **Commit the built outputs so they can be reviewed on GitHub:** `manuscript.pdf`, `manuscript.docx`, `SupplementaryMaterials.pdf`, `CoverLetter.docx`, `TableS4.xlsx`, `figures/*`. These are our own content. The MDPI class files (`Definitions/`) and `LaTeX_Source.zip` may stay untracked; adjust `.gitignore` accordingly.
3. Update `CHECKLIST.md` and `ISSUES.md`. Do not change wording or numbers.
