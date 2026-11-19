# Submission package task (iScience)

**For:** Codex. **Branch:** `codex/submission-package`, with a PR against `main`. **From:** Claude, 2026-11-19.

The text is final: `paper/manuscript.md` (draft v4 plus author fields) and `paper/cover_letter.md`. Figure 1 and the graphical abstract are final. Your job is to **integrate and convert** them into the files uploaded to the iScience submission system.

**Do not change any wording or any number.** If you find an inconsistency, list it in `paper/submission/ISSUES.md` and leave the text unchanged.

## Ground rules

- **Format:** iScience accepts a format-free first submission (one Word or PDF file with figures), with figure files as TIFF or PDF, ideally under 2 MB each. Check the current iScience "Information for authors" page and record what you checked, with the date, in `paper/submission/CHECKLIST.md`. If it disagrees with this brief, follow the journal and note the difference.
- **Figure style:** text about 7 pt at final size; sans-serif (Arial is fine). Keep the existing figures' design; only compose, rescale and export.
- **Inputs:** use only files already committed. Do not re-run analyses.

## Deliverables in `paper/submission/`

1. **`Manuscript.docx`**, generated with pandoc from `paper/manuscript.md`, in this order:
   - title page (title, authors, affiliations, lead contact, correspondence, keywords)
   - Summary, Highlights, eTOC blurb
   - Introduction, Results, Discussion (with Limitations of the study)
   - STAR Methods, including the Key resources table as a real Word table
   - Acknowledgments, Author contributions, Declaration of interests
   - References
   - Figure legends
   - main Tables 1–4

   Then, for reviewers' convenience, one page per main Figure 1–6 at the end, each with its title.

   Requirements:
   - Equations (`$...$`) must become native Word equations. Check every one: ΔEA, A_min, FCI, f̂₀, and so on.
   - Use line numbers and 1.5 line spacing.
   - Cell Press citation style: (Author, year) in the text and an alphabetical list, as in the Markdown.
   - Keep the remaining `[AUTHOR TO FILL: funding …]` placeholder visible, highlighted in yellow.
   - Also export `Manuscript.pdf` from the docx for checking.
2. **Main figure files** `Figure1.pdf/.tif` … `Figure6.pdf/.tif`, one file per figure, matching the legends in the manuscript:
   - **Figure 1:** `paper/figures/fig1/Figure1.pdf` (final).
   - **Figure 2:** the 2D slot × strategy plans of the 18.00 m² couple shell plus its 3D orthographic views. Compose them from `results/figures/g4/F3.*` and `F3b_18.*` as described in the Figure 2 legend.
   - **Figures 3–6:** map them to `results/figures/g4/` (F4, F5, F6, and F10 + F12 for Figure 6) **by reading each legend**. If a legend describes panels that no existing figure contains, report it in ISSUES.md; do not draw new data plots.
   - Panel letters A, B, … must match the legends. Width 174 mm (full) or 85 mm (single column). TIFF at 300 dpi or higher, LZW compressed.
3. **`GraphicalAbstract.tif`/`.pdf`**, from `paper/figures/fig1/GraphicalAbstract.*` (final). Use a square canvas; check the journal's current pixel requirement.
4. **`Highlights.txt`**: the four highlights, one per line.
5. **`SupplementalInformation.pdf`**: Figures S1–S6 and Tables S1–S4, each with its legend from the manuscript's Supplemental information section. Map them to the existing `results/figures/g4/` and `results/tables/g4/` files by legend, and report any mismatch.
6. **`CoverLetter.docx`** from `paper/cover_letter.md`.
7. **`CHECKLIST.md`**:
   - the journal requirements checked (with URL and date);
   - every file, with its size;
   - a cross-reference check: every Figure, Table and Figure S/Table S cited in the text exists and is numbered in order of first citation;
   - every in-text citation is in the reference list and the other way round;
   - no `[CITE`, `[NEEDS`, `TO MINT` or repository paths in legends;
   - the only remaining placeholder is the acknowledgments line.
8. **`ISSUES.md`**: anything you could not resolve without changing text or numbers.

Commit the build script (e.g. `scripts/13_build_submission.py`) so that the package can be regenerated. Claude reviews the PR by opening the docx/PDF and the figures.
