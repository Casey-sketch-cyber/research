# Buildings package review (Stage 2)

**Reviewer:** Claude, 2026-11-25. **Package:** PR #21 (`codex/buildings-package`, 47790b1).

**Verdict:** the build scripts and the audit are APPROVED and merged. The built files could not be reviewed, because they are not in the repository (`.gitignore`) and the build machine is not reachable from the review session. They will be rebuilt after the text revision below.

## Checked

- **Scripts** (`scripts/15_build_buildings.py`, `15_build_buildings_word.py`, `15_submission_artwork.py`): the text transformations are formatting only — heading numbers, figure and table insertion, superscripts, citation numbering. No wording or numbers change.
- **CHECKLIST.md:** complete against `docs/BUILDINGS_REWRITE_TASK.md`.
  - Templates: MDPI ACS v6.5e and Buildings Word template rev. 3.
  - Abstract 187 words; 7 keywords; section and back-matter order; 30 keys in first-citation order.
  - The study repository link was verified public (I confirmed this independently as well).

## Decisions on ISSUES.md

1. **Acronyms.**
   - Expand CP-SAT once in the main text (Gemini, Stage 1b).
   - "LTS" is part of the product name "Blender 4.5.3 LTS"; leave it.
   - "ID" as a table column heading needs no expansion.
   - "3D" is defined in the main text; leave it.
2. **Commas in four-digit numbers inside the artwork** ("2,619", "1,236", "1,000"): leave them. MDPI's copy-editing handles house style, and redrawing the figures is not worth the risk.
3. **Cover letter:** set the date on the submission day. The declaration wording is acceptable as written.
4. **`www.mdpi.com/xxx/s1`** and the DOI placeholder are MDPI production placeholders; leave them.
5. **ResPlan reference punctuation:** the entry is an arXiv `@misc`. Leave it; production fixes the display.

## Next

- **Text:** the running text carries too many numbers for *Buildings* readers (Results 13–22 numbers per 100 words). See `docs/BUILDINGS_NUMBERS_TRIM_TASK.md`, Stage 1b (Gemini).
- **Build:** then Codex rebuilds (Stage 2b) and **commits the built PDF, docx, supplement, cover letter and figures**, so the final package can be reviewed.
