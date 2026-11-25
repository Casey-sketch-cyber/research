# Notes from the Writer (`paper/buildings/`)

Prepared for the *Buildings* (MDPI) Stage 1 rewrite (`gemini/buildings-rewrite`) per `docs/BUILDINGS_REWRITE_TASK.md`.

## 1. Title Alternatives for *Buildings* (Author Decision)

The active manuscript title in `paper/buildings/manuscript.md` remains unchanged from the iScience submission:
- **Current title:** *Translating furniture into floor area shows where compact homes gain space*

Three more descriptive alternatives tailored to *Buildings* readers (naming compact housing, space standards, and transformable furniture):
1. *Evaluating Transformable Furniture in Compact Housing: Schedule-Aware Equivalent Floor Area and Implications for Minimum Space Standards*
2. *Where Transformable Furniture Saves Floor Area in Compact Housing: Verified Schedule-Aware Layout Optimization Across 2619 Dwellings*
3. *Beyond Minimum Floor Area: Quantifying the Equivalent-Area Gains of Transformable Furniture Across Compact Dwellings and Space Standards*

## 2. Summary of Structural and Editorial Changes from `paper/manuscript.md`

- **Base record preserved:** `paper/manuscript.md` on `main` (PR #19) and all figure files under `paper/figures/` were left completely untouched. All new files reside exclusively under `paper/buildings/`.
- **Journal-fit rewrite (not a mechanical reformat):**
  - **Section order:** Reordered into MDPI structure: Title page → Abstract (≤ 200 words, one paragraph, no citations) → Keywords (7 semicolon-separated terms) → `1. Introduction` → `2. Materials and Methods` (`2.1`–`2.11`) → `3. Results` (`3.1`–`3.6`) → `4. Discussion` (`4.1`–`4.3`) → `5. Conclusions` → MDPI Back Matter in exact required order (`Supplementary Materials`, `Author Contributions`, `Funding`, `Institutional Review Board Statement`, `Informed Consent Statement`, `Data Availability Statement`, `Acknowledgments`, `Conflicts of Interest`, `References`).
  - **Removed Cell Press–only sections:** Dropped `Highlights`, `eTOC blurb`, `Lead contact`, `Materials availability`, and the `Key resources table` (folded software names, locked versions, and code URL into `Section 2.11. Software and Code Availability`).
  - **Reframed Introduction for *Buildings*:** Opened from residential space regulation and compact housing supply; organized prior literature into three strands by what each cannot answer (space standards & static audits; single-room transformable studies; computational layout generators); closed with explicit `RQ1–RQ3`, three concrete contributions (no "first"/"novel"/"unprecedented"), and a paper-organization roadmap sentence.
  - **Methods-before-Results de-duplication:** Moved metric, corpus, strategy, validator, and statistical definitions into `Section 2`, then streamlined `Section 3` (`3.1`–`3.6`) to point back to `Section 2.x` instead of re-defining terms inline.
  - **Inline figures and tables:** Placed MDPI-styled `**Figure 1.**`–`**Figure 6.**` captions and `**Table 1.**`–`**Table 4.**` immediately after the paragraph that first cites each item, preserving strict sequential order (`Figure 1` → `Figure 6`, `Table 1` → `Table 4`, `Figure S1` → `Figure S7`, `Table S1` → `Table S4`).
  - **Expanded Discussion §4.2 for *Buildings*:** Separated `4.1 Interpretation Against Prior Work`, `4.2 Implications for Architectural Design and Housing Regulation` (targeted guidance for regulators, architects/developers, and furniture manufacturers with every statement grounded in `Section 3`), and `4.3 Limitations and Future Work` (keeping the three scope boundaries).
  - **Added Section 5 (Conclusions):** Concise two-paragraph synthesis (~250 words) answering `RQ1–RQ3` and restating the conditional message with zero new numbers.
- **Formatting & citation standards:**
  - Converted all in-text citations to Pandoc keys (`[@key]`) drawn strictly from `paper/references.bib` (zero author–year citations, zero hand-numbered brackets) so Stage 2 (Codex) can generate ACS numbered references via `mdpi.bst`.
  - Applied MDPI thousands-comma formatting strictly: commas only in numbers of 5 or more digits (`31,428`, `46,830`, `147,702`, `108,202`, `215,709`, `33,658`, `20,000`), and no commas in 4-digit integers (`2619`, `2109`, `1236`, `1000`, `1150`, `1090`, etc.).
  - Enforced 3-zone acronym definitions (Abstract, Main text, and first Figure/Table caption).
  - Kept all scientific numbers, sample sizes, confidence intervals, author metadata, verbatim Funding (`6026331014K`), verbatim Author Contributions, verbatim AI declaration (placed in `Acknowledgments` per MDPI rules), and public repository URL (`https://github.com/liangdagongjue-code/research`) exact.
- **Supplementary legends separated:** Placed full legends and Markdown tables for `Figure S1`–`Figure S7` and `Table S1`–`Table S4` in `paper/buildings/supplementary_legends.md` using MDPI `**Figure S1:** title` and `**Table S1:** title` formatting, with concise titles listed in the manuscript's `Supplementary Materials` back-matter statement.

## 3. Unused Entries in `paper/references.bib`

Exactly **30 of 32** entries in `paper/references.bib` are cited in `paper/buildings/manuscript.md` (and both citations inside `paper/buildings/supplementary_legends.md`—`@bu2026compact` and `@collins2022abo`—appear in the main manuscript). The following **2 entries** in `paper/references.bib` remain intentionally unused (matching the iScience submission):
- `johanes2026adaptable`
- `yunitsyna2014universal`

## 4. Note for Stage 2 (Codex) on Graphical Abstract

The existing graphical abstract (`paper/figures/fig1/GraphicalAbstract.*`) is unchanged and meets MDPI's optional upload criteria (verify ≥ 1100 × 560 px during Stage 2 packaging). For traceability, the `+3.5 m²` callout drawn on the graphical abstract is the one-decimal rounding of the `18.00 m²` couple showcase equivalent-area gain ($\Delta\text{EA} = 3.48\text{ m}^2$) reported in `Section 3.1` and `Figure 2`.

## 5. `[NEEDS EVIDENCE]` Items

None (`0` occurrences). Every number in `paper/buildings/manuscript.md`, `paper/buildings/supplementary_legends.md`, and `paper/buildings/cover_letter.md` is verbatim from `paper/manuscript.md` and its committed result files.

## 6. Title decision (authors, 2026-11-25)

The authors chose alternative 1: *Evaluating Transformable Furniture in Compact Housing: Schedule-Aware Equivalent Floor Area and Implications for Minimum Space Standards*. It is now the title in `manuscript.md` and `cover_letter.md`.
