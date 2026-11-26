# Final Buildings package and submission sheet (Stage 2c)

**For:** Codex. **From:** Claude, 2026-11-26.

**Branch:** `codex/buildings-package-v3`. Open a PR against `main`; do not merge.

**Do not submit the manuscript, log in to susy.mdpi.com or create accounts.** The corresponding author submits.

**Do not change wording or numbers.** List any text problem in `ISSUES.md` instead.

## Changes since v2 (already on `main`)

- `paper/references.bib`: author names fixed in `nieciecki2026comfortable` and `standfest2022swiss`.
- `paper/buildings/cover_letter.md`: dated 26 November 2026. If the author tells you a different submission day, use that date instead.

## Tasks

1. **Rebuild everything** with the committed `scripts/15_*`:
   - the public `manuscript.pdf` and `.docx`;
   - `CoverLetter.docx`;
   - the local official-template PDF and `LaTeX_Source.zip`.

   Check in the PDF that references 19 and 27 now show abbreviated given names ("Nieciecki, P.; …", "Standfest, M.; …").
2. **Table 1 header:** in the public PDF, "Evaluable" wraps as "Evaluabl/e". Fix it through column widths or a hyphenation hint only; do not change the header text.
3. **Commit the rebuilt outputs** to `paper/buildings/submission/`, as in v2.
4. **Write `paper/buildings/submission/SUBMISSION_FORM.md`.** It is a copy-paste sheet for the susy.mdpi.com form, with every field taken verbatim from the approved files:
   - Journal *Buildings*; article type Article; section "Architectural Design, Urban Science, and Real Estate"; regular submission (no special issue).
   - Title, abstract and keywords.
   - Authors in order, with affiliations. Mark the corresponding author with the email in the manuscript. For the other authors' emails and ORCIDs, write `[AUTHOR TO FILL]`; do not guess.
   - Funding statement, Conflicts of Interest, Data Availability Statement and the AI-use declaration, verbatim.
   - **Suggested reviewers:** `[AUTHOR TO FILL]`. Do not propose names.
   - The upload list in the order susy asks for it, with file names and types:
     - manuscript (PDF and/or DOCX);
     - Supplementary Materials (`SupplementaryMaterials.pdf`, `TableS4.xlsx`);
     - figures (`figures/Figure1–6`);
     - optional graphical abstract;
     - cover letter.
   - A short pre-submit checklist for the author:
     - decline or let lapse the iScience → Heliyon transfer offer;
     - check the cover letter date;
     - all authors have approved the submission.
5. **Update `CHECKLIST.md`** and the file inventory.

Claude reviews the PR.
