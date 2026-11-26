# Buildings package v2 review (Stage 2b)

**Reviewer:** Claude, 2026-11-26. **Package:** PR #23 (`codex/buildings-package-v2`, 61dc44d).

**Verdict: APPROVED, merged.** The package is ready to submit.

## Checked

- **`manuscript.pdf`** (24 pages, standard formatting) — opened and inspected the title page, the tables, Figure 4 with its caption, the Methods and the references.
  - Its text contains the author-chosen title, all Stage 1b wording and the three review edits:
    - "not driven by bed-clearance conventions";
    - "184 versus 246 of 390";
    - "51 versus 30 of 120".
  - Also present: the CP-SAT expansion, "Yet none ties"; the funder and grant 6026331014K; the verbatim AI declaration; the code link; the IRB and Informed Consent statements ("Not applicable"); and Conflicts of Interest.
  - No leftover citation keys, `[CITE` or `[NEEDS`. References are numbered 1–30 in order of first citation.
- **`manuscript.docx`:** opens; it has the title, 4 tables and 6 figures.
- **`SupplementaryMaterials.pdf`** (18 pages), the figures, `TableS4.xlsx` and `CoverLetter.docx` are unchanged from Stage 2, as expected.

## Notes

1. **Which files to upload.** MDPI accepts a free-format first submission, so the public `manuscript.pdf`/`.docx` on GitHub can be uploaded as they are. The official-template PDF and LaTeX source (`LaTeX_Source.zip`) exist only in Codex's local build. They are optional now and become useful at revision or production.
2. **Reference display.** Two `.bib` entries had brace-protected full names, so the style printed "Nieciecki, Piotr." and "Standfest, Matthias.; …". Fixed in `paper/references.bib`, with names checked against the Zenodo record for Swiss Dwellings. A rebuild picks this up. MDPI production also re-typesets references, so a rebuild before submission is optional. The duplicated arXiv URL in the ResPlan entry is the same known display issue.
3. **Table 1 header** in the public PDF wraps "Evaluable" as "Evaluabl/e". This is cosmetic, and only in the standard-format build.
4. **Cover letter date:** 25 November 2026. Change it to the submission day.
