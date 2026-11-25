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

## 7. Stage 1b: Numbers Trim (`gemini/buildings-numbers-trim`, 2026-11-25)

Completed per `docs/BUILDINGS_NUMBERS_TRIM_TASK.md`.

### 7.1 Summary of changes
- **Results (`3.1`–`3.6`):** Rewrote paragraph openings so each Results paragraph leads with its message in words, trimmed secondary counts/intervals/bounds already present in main tables, figures, figure captions, or the supplement, kept all required headline point estimates and only the four required 95% CIs (the three median identified $\Delta\text{EA}$ values in `3.3` and the Hong Kong switching reduction `2.24 m² [1.66, 2.82]` in `3.6`).
- **Discussion (`4.1`–`4.3`) and Conclusions (`5.`):** Stated findings in words pointing back to `Sections 3.1–3.6`, retaining only the few headline numbers a reader would quote (`60%`, `7.60 m²`, `−0.52` to `+1.38 m²`, `0 m²`, `Spearman ρ ≥ 0.80`, `45 m²`, `8 m²`, `2.24 m²`, `12–30 m²`, `0.60 m` to `0.90 m`, `8–20 m²`, `2619`, `6.21 m²`, `5.00 m²`).
- **Acronym expansion (`CP-SAT`):** Expanded once at first use in the main text (`Section 2.5`) verbatim as `"the CP-SAT (constraint programming–Boolean satisfiability) solver of Google OR-Tools"`, and aligned `Figure 1` caption (`"A constraint programming–Boolean satisfiability (CP-SAT) optimizer"`). Left `"LTS"` in `"Blender 4.5.3 LTS"` unchanged.
- **Abstract, Methods, and Cover Letter:** Abstract (`187` words) left unchanged; Methods left unchanged except the `CP-SAT` expansion in `2.5`; `cover_letter.md` required no edits because every headline number cited there remains in the trimmed manuscript.

### 7.2 Numbers per 100 words (before vs after, prose only excluding tables and captions)

Reported both for **all numeric tokens** (matching the audit script in `docs/BUILDINGS_NUMBERS_TRIM_TASK.md`, including section/figure/table callouts) and **data numbers only** (`NoRef`, excluding `Section`/`Figure`/`Table` callout numbers and `S0–S2`/`D1–D6`/`RQ1–RQ3` codes).

| Section | Words (before → after) | All numbers / 100w (before → after) | Data numbers / 100w (before → after) | Target |
| :--- | ---: | ---: | ---: | :--- |
| 1. Introduction | 967 → 967 | 2.6 → 2.6 | 2.2 → 2.2 | keep |
| 2.1–2.11 Methods (combined) | 3883 → 3886 | 9.8 → 9.8 | 9.3 → 9.3 | keep |
| 3.1 Verified comparison | 411 → 336 | 13.4 → 7.7 | 10.7 → 4.8 | ≤ 8 |
| 3.2 Static saturation | 222 → 174 | 16.2 → 7.5 | 13.5 → 4.0 | ≤ 8 |
| 3.3 Intermediate two-person gains | 515 → 332 | 20.0 → 12.7 | 17.7 → 8.7 | ~8 (all remaining numbers are Rule 2/3 required headlines + 3 CIs) |
| 3.4 Form vs time & sensitivity | 423 → 287 | 14.9 → 6.6 | 13.5 → 4.2 | ≤ 8 |
| 3.5 Area cutoffs & dispersion | 344 → 236 | 15.4 → 6.8 | 12.5 → 4.2 | ≤ 8 |
| 3.6 Hong Kong & kits | 553 → 361 | 21.9 → 8.0 | 19.9 → 5.0 | ≤ 8 |
| **Results 3.1–3.6 (combined)** | **2468 → 1726** | **17.5 → 8.4** | **15.2 → 5.3** | **~8 or fewer** |
| 4.1 Prior work | 606 → 552 | 6.3 → 3.8 | 5.1 → 2.0 | ≤ 5 |
| 4.2 Design & regulation | 607 → 457 | 11.2 → 3.9 | 9.7 → 1.5 | ≤ 5 |
| 4.3 Limitations & future work | 238 → 231 | 5.5 → 3.9 | 5.0 → 3.0 | ≤ 5 |
| **Discussion 4.1–4.3 (combined)** | **1451 → 1240** | **8.2 → 3.9** | **7.0 → 2.0** | **≤ 5** |
| **5. Conclusions** | **270 → 235** | **10.4 → 4.3** | **10.4 → 2.6** | **≤ 5** |

### 7.3 Numbers moved out of running prose and where each still appears

| Section | Numbers moved out of prose | Where they still appear |
| :--- | :--- | :--- |
| 3.1 | `510`, `16.75 m²` | Section 2.2; Table 1; Figure S1 |
| 3.1 | `0.937`, `0.942`, `1.000`, `TB = 0.00`, `TB = 3.00`, `0.577`, `0.687`, `0.668` | Figure 2 (panels A–B and caption); Figure S2 |
| 3.1 | `1.0000`, `53.86 s`, `10.68 s`, `0.8612`, `3.47 s`, `0.8675`, `38.45 s`, `0.9341`, `104.12 s`, `108.33 s`, `95% CI [0.0016, 0.0160]`, `11` | Table S2; Figure S3 (paired CI `[0.0016, 0.0160]` is a secondary CI per Rule 3) |
| 3.2 | `2109`, `88.5%`, `85.9%`, `59.1%`, `43.2%`, `94.0%`, `93.6%`, `92.1%`, `86.3%`, `0.00–0.00 m²`, `510`, `8–16 m²`, `54.9%`, `53.9%`, `31.6%`, `26.7%`, `0.83–0.86 m²` | Table 3; Table 1; Section 2.2 |
| 3.3 | Bracketed counts `159 of 2109`, `184 of 2109`, `496 of 2109`, `757 of 2109`; identified/bounded counts `n = 160 / 24`, `448 / 48`, `721 / 36`; lower bounds `≥1.33`, `≥6.21`, `≥5.00`, `≥2.00 m²`, `16.75 m²` | Table 3; Table 1 |
| 3.3 | Sparse smallest-bin couple values (`n = 6`, `16–18 m²`, `≥16.6 m²`, `8.2 m²`); generated-shell percentage and zero-threshold bin values (`8.00–40.00 m²`, `9.2%`, `49.8%`, `24 m²`, `7.6%`, `33.3%`, `28 m²`) | Figure 4 (panels and caption); Section 2.2 |
| 3.3 | Secondary $A_{\min}$ CIs (`[9.15, 12.70]`, `[33.21, 34.67]`, `[21.27, 24.73]`, `[1.12, 2.38]`, `[2.78, 4.77]`, `[4.90, 6.12]`, `[5.19, 7.75]`), `33.96 m²`, `23.18 m²`, `50%`, `FCI ≥ 0.95` | Table 3; Section 2.8 (start/end $A_{\min}$ CIs are secondary CIs per Rule 3) |
| 3.4 | Single-person observed form/time means (`0.0085`, `0.0002`, `0.0107`, `0.0001`), generated-shell couple form/time means (`0.0709`, `0.0372`), and all eight secondary form/time 95% CIs | Table 3 |
| 3.4 | Sensitivity subsample counts and settings (`348`, `≤20 m²`, `18`, `200`, `50`, `49`, `0.8×`, `1.2×`, `30, 60, and 120 s`), secondary CI `[−0.0203, −0.0040]` | Section 2.9; Figure S4 |
| 3.5 | `2109`, `FCI ≥ 0.95`, `95%`, `1150`, `25`, `1090`, `22`, `47.0%`, `940`, `52`, `40.5%`, `789`, `66`, `30 m²`, `10.4%`, `11.1%`, `14.5%`, `16.4%`, `2 m²`, `26–28 m²`, `24–26 m²`, `16.75 m²`, `510`, `8.00–40.00 m²`, `206`, `253` | Table 4; Figure 5; Table 1; Section 2.2; Section 2.8 |
| 3.6 | Census counts (`215,709`, `107,371`, `108,202`, `33,658`), `8–20 m²`, `FCI_q ≥ 0.95`, `12.30 m²`, `11 of 30`, secondary $A_{\min}$ CIs (`[13.03, 13.73]`, `[12.00, 12.70]`, `[11.90, 12.64]`, `[18.78, 19.96]`, `[16.58, 17.64]`, `[1.86, 3.03]`, `[18.18, 19.02]`, `[15.87, 16.83]`) | Section 2.9; Table 1; Figure 6 (panels A–E); Table S3 |
| 3.6 | Kit dimensions, cohort counts, mean differences, secondary CIs, and per-band shell counts (`30`, `8–15 m²`, `15`, `≤20 m²`, `0.80 m`, `0.80 × 0.45 m`, `0.70 × 0.60 m`, `0.60 m`, `+0.0013 [−0.0153, +0.0200]`, `11/30 vs 13/30`, `184 vs 246`, `−0.0389 [−0.0564, −0.0230]`, `1.50 m`, `1.20 × 0.55 m`, `1.00 × 0.75 m`, `1.40 m`, `+0.0021 [−0.0336, +0.0279]`, `5/30 vs 2/30`, `[14.67, 16.19]`, `[15.70, 16.57]`, `154 vs 132`, `30/120 to 51/120 (+21)`, `0/150`, `8–12 m²`, `0.500 to 0.448`) | Figure 6 (panels A–F and caption); Figure S5; Table S3 (Parts A–C); Section 2.9 |
| 4.1 | `2619`, `61.0%–90.8%`, `5–5.5 m²`, `8 m²`, `35 m²`, `2109`, `510`, `24 h`, GraphSAGE metrics (`0.087–0.661`, `0.088–0.588`, `23 of 33`, `0.796`, `0.888`) | Section 2.2; Section 3.2; Table 3; Figure S6; Figure S7; Table S4 |
| 4.2 | Repeated Results figures (`1150`, `1090`, `55.7%`, `52.7%`, `95%`, `206`, `253`, `40.4%`, `49.6%`, `0.205`, `26–28 m²`, `0.190`, `24–26 m²`, `29.97 m²`, `30 m²`, `18.00 m²`, `6.21 m²`, `5.00 m²`, `7.32 m²`, `14–16 m²`, `6.00 m²`, `18–20 m²`, `89.1%–90.8%`, `10 m²`, `0.5151`, `0.0130`, `0.0112`, `0.0709`, `0.0372`, `0.0271`, `0.0017`, `−0.0267`, `−0.0199`, `13–16 m²`, `30/120`, `51/120`, `+21`, `0.500`, `0.448`, `8–20 m²`, `184`, `246`) | Sections 3.1–3.6; Tables 3–4; Figures 2, 4, 5, 6; Figures S2, S4, S5; Table S3 |
| 4.3 | `16-item`, `108,202`, `215,709`, `107,371`, `390-shell` | Section 2.4; Section 2.9; Table 1; Section 3.6 |
| 5 | Repeated Results figures (`24-hour`, `31,428`, `61.0%–90.8%`, `7.32 m²`, `14–16 m²`, `6.00 m²`, `18–20 m²`, `8–10 m²`, `55.7%`, `52.7%`, `30.0%–49.6%`, `390`, `8–20 m²`, `18.57 m²`, `16.33 m²`) | Abstract; Sections 3.1–3.6; Tables 3–4; Figures 4, 6 |
