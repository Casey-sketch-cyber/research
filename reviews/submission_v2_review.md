# Submission package v2 review (PR #18)

**Reviewer:** Claude, 2026-11-19. **Verdict: APPROVED, merged.** The upload set in `paper/submission-v2/upload/` is ready, pending the author confirmations below.

Checked:

- **Figure 6** has A–F at 174 × 132 mm. Former panel G is now Figure S5, with reader-facing kit labels.
- **Figures 3–6** were re-rendered from the plotting code at final size, with labels at about 6.5–7 pt. I viewed Figures 3 and 6: they are readable, and the data are unchanged.
- **Graphical abstract:** 1,200 × 1,200 px at 300 dpi per the iScience final-file checklist; 16/14/12 pt text. The layout and wording are as approved.
- **Main manuscript:** built on the official Cell Press LaTeX template v1.10, with numbered references in first-citation order (the publisher style) and 30 entries. The title page, affiliations, lead contact and correspondence are correct.
- **Supplement:** S1–S7 and S1–S4 in citation order. Table S4 is an editable spreadsheet.
- **Attachments:** Key Resources Table, Highlights and Cover Letter as separate files.

## Author confirmations needed before upload

1. **Funding line.** The PR adds "Shenzhen Polytechnic University Postdoctoral Fund (Grant No. 6026331014K)" to the Acknowledgments. The reviewer did not receive this from the author in the review thread, so the author must confirm the fund name and grant number exactly.
2. **Generative-AI declaration.** Elsevier/Cell Press policy asks for a statement of the tools used, why, and the authors' responsibility. Replace the current one-sentence version with:

   > During the preparation of this work, the authors used Claude (Anthropic) for research planning, review and editing, Gemini (Google) for drafting text, and OpenAI Codex for implementing analysis code and preparing submission files. After using these tools, the authors reviewed and edited the content as needed and take full responsibility for the content of the publication.

   Because AI tools also wrote analysis code, add one sentence to STAR Methods (Quantification and statistical analysis, or Software):

   > Analysis code was developed with assistance from an AI coding tool (OpenAI Codex) under author supervision; all reported layouts were checked by the independent validator and all reported numbers were regenerated from the committed code and data.

   Both texts are proposals. The authors decide the final wording.
3. **Declaration of Interests form:** complete `author/DeclarationOfInterestsForm_pending.pdf` (the corresponding author signs).
4. **Upload format:** use the LaTeX PDF and sources in `upload/` (numbered references, as the template requires). The Word reading copy in `review/` is for checking only, because its citation style differs. Do not upload both.

After items 1–2 are confirmed, Codex rebuilds `Manuscript.tex/.pdf` once (`codex/submission-package-v3`). No other changes are needed.
