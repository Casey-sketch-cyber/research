# Rewrite for *Buildings* (MDPI)

**From:** Claude, 2026-11-25.

iScience declined the manuscript at the editorial stage because of journal fit, not because of a problem with the science. The authors have decided to submit to ***Buildings*** (MDPI), section **"Architectural Design, Urban Science, and Real Estate"**. This is a regular submission to a standing journal section, **not a special issue**. Do not mention any special issue in the manuscript or the cover letter.

The work has two stages, each followed by a Claude review:

1. **Gemini:** rewrite the paper for *Buildings*.
2. **Codex:** build it into the official MDPI template and check the format.

**The base text** is `paper/manuscript.md` on `main`, as submitted to iScience (PR #19 merged). Keep that file unchanged as the record. All new files go in `paper/buildings/`.

## What stays fixed (both stages)

- **The science:** every number, sample, method and finding stays as it is. Every number must already appear in `paper/manuscript.md` or in a committed file it cites. Do not compute, round differently or add numbers. If a number you need is missing, write `[NEEDS EVIDENCE: …]`.
- **References:** use only `paper/references.bib` (32 entries). Do not add, invent or "complete" references.
- **Authors:** keep the authors, affiliations, corresponding author and email as on the title page.
- **Funding:** keep the funder and grant number exactly: "Shenzhen Polytechnic University Postdoctoral Fund", grant number 6026331014K. Only the sentence frame changes to MDPI's (see Back matter below).
- **AI declaration:** keep it word for word as in `paper/manuscript.md`:
  > "During the preparation of this work the authors used GPT-6 in order to undertake the translation and polishing of part of the text. After using this tool, the authors have reviewed and edited the content as needed and take full responsibility for the content of the published article."

  MDPI places it in **Acknowledgments**.
- **Figures:** Figures 1–6 and the supplements are final. Do not redraw them.

## MDPI *Buildings* requirements

Checked against https://www.mdpi.com/journal/buildings/instructions on 2026-11-25.

- **Templates:** the official MDPI Word or LaTeX template is recommended; free format is also accepted.
- **Abstract:** about 200 words at most, one paragraph with no headings, covering background, methods, results and conclusions.
- **Keywords:** 3 to 10, placed after the abstract.
- **Acronyms:** define each one at its first use in each of three places: the abstract, the main text, and the first figure or table.
- **Section order:**
  1. Introduction
  2. Materials and Methods
  3. Results
  4. Discussion
  5. Conclusions (optional; we include one)
- **Methods:** name software and versions, and say whether the code is available.
- **Back matter, in this order:**
  1. Supplementary Materials
  2. Author Contributions
  3. Funding
  4. Institutional Review Board Statement
  5. Informed Consent Statement
  6. Data Availability Statement (mandatory)
  7. Acknowledgments
  8. Conflicts of Interest (just before the references)
  9. References
- **References:** numbered in order of first appearance, cited in square brackets before punctuation ([1], [1–3], [1,3]), in ACS style with full titles.
- **Figures and tables:** placed in the text near their first citation, numbered in order of appearance. Each needs a short title and a caption. Figures at 600 dpi or more (PNG, JPEG or TIFF). Table fonts no smaller than 8 pt. Use a thousands comma only in numbers of five or more digits ("31,428" but "2619").
- **Supplementary items:** labelled "Figure S1: title", "Table S1: title". Every citation in a supplement must also appear in the main reference list.
- **No Highlights, eTOC blurb or Key resources table.** A graphical abstract is optional; we upload the existing one, which must be at least 1100 × 560 px.
- **Cover letter:** required. It explains significance and fit with the journal's scope, and includes two statements:
  - "We confirm that neither the manuscript nor any parts of its content are currently under consideration or published in another journal."
  - "All authors have approved the manuscript and agree with its submission to *Buildings*."

---

## Stage 1: Gemini rewrites the manuscript

**Branch:** `gemini/buildings-rewrite`. Open a PR against `main`. **Do not merge.**

**Read first:**
- `GEMINI.md`, `docs/WRITING_GUIDE.md` and `docs/PAPER_STORY.md` (story, terminology, claims to avoid);
- `paper/manuscript.md`;
- the reviews in `reviews/paper_*.md`, which record why the current wording is as it is.

### Why this is a rewrite, not a reformat

Cell Press puts the methods at the end, so the Results had to define FCI, ΔEA, the strategies and the validator as they went. MDPI puts Materials and Methods **before** the Results, and *Buildings* readers are architects, building scientists and housing researchers rather than a general-science audience. Tell the same story in a different order, for a different reader.

### Section-by-section brief

**Title.** Keep "Translating furniture into floor area shows where compact homes gain space". In `paper/buildings/NOTES_FROM_WRITER.md`, propose up to three more descriptive alternatives that suit *Buildings* (e.g. naming compact housing, space standards and transformable furniture). The authors decide.

**Abstract (≤200 words, one paragraph).**
- Background: area-only regulation and the claims made for transformable furniture.
- Methods: 2619 plans, four household schedules, three furniture strategies, constraint optimization with an independent validator, conversion to equivalent floor area.
- Results: the 3–4 headline numbers in the Summary.
- Conclusion: the value is conditional. State what it means for designers and regulators.

**Keywords:** 6–8, starting from the current list.

**1. Introduction.** Keep the backward-then-forward logic and the gap → root cause → approach chain from the current Introduction. For *Buildings* readers:
- **Opening:** start from the building and housing problem: shrinking dwellings, minimum space standards, how floor area is regulated.
- **Literature:** cover space standards, transformable interiors and computational layout generation. Organize it by what each strand cannot answer, not author by author. This can be slightly longer than the iScience version.
- **Ending:** close with two or three explicit research questions, a short contributions list (no "first" or "novel"), and one sentence on how the paper is organized.

**2. Materials and Methods.** Move all of STAR Methods here, as numbered subsections:
- 2.1 Overview of the framework (cite Figure 1)
- 2.2 Dwelling corpus and net internal area
- 2.3 Household activity schedules
- 2.4 Furniture library, clearances and the three strategies
- 2.5 Schedule-constrained layout optimization
- 2.6 Independent geometric and reachability validator
- 2.7 Functional capacity index and transformation burden
- 2.8 Equivalent-area gain and minimum adequate area
- 2.9 Sensitivity analyses, benchmarks, kits and the Hong Kong scenario
- 2.10 Statistical analysis
- 2.11 Software and code availability

Fold the Key resources table into 2.11 as running text, or as a short software table with versions. Remove the "Lead contact" and "Materials availability" subsections. Move the definitional sentences out of the current Results and into these subsections.

**3. Results.** Keep the claim-style subsection headings and the order of findings. Number them 3.1, 3.2, and so on. Each paragraph carries one message:
- Since terms are now defined in Methods, cut the definitions and point back to the relevant subsection ("Section 2.8").
- Keep every figure and table callout.
- Place each figure and table caption block right after the paragraph that first cites it.

**4. Discussion.**
- 4.1 Interpretation against prior work (single-room claims, space standards, layout generators).
- 4.2 **Implications for design and regulation:** what designers, developers and regulators can do with ΔEA and A_min. Write this for *Buildings* readers; every sentence must rest on results already in the paper.
- 4.3 **Limitations and future work:** keep the current scope-boundary framing (task scope, setting scope). Do not turn it into an apology list.

**5. Conclusions** (about 200–300 words). Restate the answer to each research question and the conditional message. No new numbers, nothing that is not in the Results.

**Captions.** Use MDPI style: "**Figure 1.** Short title. Explanation…". Keep the panel letters exactly as drawn in the figure files (A, B, …). Supplementary captions go in a "Supplementary Materials" list ("Figure S1: title"). Keep the full supplementary legends in `paper/buildings/supplementary_legends.md` for Codex.

**Back matter.**
- **Supplementary Materials:** "The following supporting information can be downloaded at: www.mdpi.com/xxx/s1, Figure S1: …; …; Table S4: …".
- **Author Contributions:** "Conceptualization, Z.L.; investigation, F.H. and D.Z.; writing—original draft preparation, F.H.; supervision, Z.L. All authors have read and agreed to the published version of the manuscript."
- **Funding:** "This research was funded by the Shenzhen Polytechnic University Postdoctoral Fund, grant number 6026331014K."
- **Institutional Review Board Statement:** "Not applicable."
- **Informed Consent Statement:** "Not applicable."
- **Data Availability Statement:** condense the current Data and Code availability text. Keep every dataset link and the code link https://github.com/liangdagongjue-code/research.
- **Acknowledgments:** the AI declaration, verbatim (see above).
- **Conflicts of Interest:** "The authors declare no conflicts of interest."

**Citations.** Cite with Pandoc keys from `paper/references.bib` (`[@perron2023cpsat]`, `[@key1; @key2]`), not author–year text and not hand-numbered brackets. Codex generates the numbered ACS list from the keys. Use an author's name in the text only where the sentence needs it ("Özer and Jacoby [@key] found …").

**Style.**
- Follow `docs/WRITING_GUIDE.md`: one message per paragraph, calibrated verbs, terminology from PAPER_STORY §6.
- American English.
- Number format per MDPI: thousands comma only from five digits.
- Length: there is no limit. Do not pad. Main text (Introduction to Conclusions, including Methods) of about 6,500–8,000 words is expected.

### Stage 1 deliverables (`paper/buildings/`)

- `manuscript.md`: the full rewritten manuscript in MDPI section order, with the title page, abstract, keywords, sections 1–5, captions and back matter.
- `supplementary_legends.md`
- `cover_letter.md`, addressed to the *Buildings* editors, dated on the submission day, signed by Zhantu Liang. It covers:
  - the problem;
  - what we did;
  - the four key findings;
  - **why the paper fits *Buildings*:** residential architectural design, space standards and housing regulation, layout methods. Name the section "Architectural Design, Urban Science, and Real Estate".
  - the two required statements;
  - "The authors declare no conflicts of interest."
- `claims_map.md` and `self_review.md`, updated as before: every claim mapped to evidence, plus the five-dimension self-review.
- `NOTES_FROM_WRITER.md`: title alternatives; anything moved or cut; any `[NEEDS EVIDENCE]`.

Commit in stages: Methods → Results → Introduction and Discussion → Abstract, Conclusions, back matter → cover letter.

---

## Stage 2: Codex builds the package and checks the format

**Starts only after Claude has merged Stage 1. Do not change wording or numbers.** List any text problem in `paper/buildings/submission/ISSUES.md` instead.

**Branch:** `codex/buildings-package`. Open a PR against `main`.

1. Download the current official MDPI LaTeX template from https://www.mdpi.com/authors/latex, with journal `buildings` and article type `article`. Record the template version and date in the checklist.
2. Build `paper/buildings/submission/manuscript.tex` and `.pdf`:
   - references numbered from `paper/references.bib` with the template's ACS style (`mdpi.bst`), in order of first citation;
   - figures inserted near their first citation.
3. Produce a Word version from the official MDPI Word template (`manuscript.docx`), for authors who prefer Word upload. The LaTeX PDF is the reference build.
4. **Figures:** export Figures 1–6 as TIFF or PNG at 600 dpi or more, plus PDF. Do not change the design. The graphical abstract must be at least 1100 × 560 px.
5. **`SupplementaryMaterials.pdf`:** Figures S1–S7 and Tables S1–S4 with legends from `supplementary_legends.md`, as in the iScience package. Ship `TableS4.xlsx` as before.
6. **`CoverLetter.docx`** from `cover_letter.md`.
7. **`CHECKLIST.md`**, covering:
   - every requirement in "MDPI *Buildings* requirements" above, as pass/fail;
   - section and back-matter order;
   - abstract word count ≤200;
   - keywords count;
   - every acronym defined in the abstract, main text and first figure or table;
   - every figure, table and supplement cited in order;
   - every cited key in the `.bib` and every `.bib` entry cited (or listed as unused);
   - number-comma style;
   - no `[CITE`, `[NEEDS`, `@` keys or repository paths left in the PDF;
   - **that https://github.com/liangdagongjue-code/research opens publicly** (if it does not, report it in ISSUES.md; do not change the link);
   - a file list with sizes.
8. Commit the build script (e.g. `scripts/15_build_buildings.py`).

Claude then reviews the PR by opening the PDF, the docx and the figures.

## Author actions (not for Gemini or Codex)

- Do not accept the iScience → Heliyon transfer offer. Let it lapse or decline it, so the manuscript is not under consideration elsewhere.
- Submit through https://susy.mdpi.com, choosing the section "Architectural Design, Urban Science, and Real Estate". Suggested reviewers go in the system, not in the cover letter.
