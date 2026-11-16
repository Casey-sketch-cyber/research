# Writer handover notes (`gemini/paper-draft-v2`)

## 1. Manuscript-to-artifact mapping

### Main figures
- **Figure 1** → `docs/FIGURE1_SPEC.md` (`paper/figures/fig1/Figure1.pdf`, in progress on `codex/paper-fig1`; programmatic schematic in `results/figures/g4/F1.pdf`)
- **Figure 2** → `results/figures/g4/F3.pdf` (Panel A: 2D plans across Night, Workday, Dinner for 10.00, 18.00, and 29.97 m²) + `results/figures/g4/F3b_18.pdf` (Panel B: 3D renders of 18.00 m² couple shell)
- **Figure 3** → `results/figures/g4/F4.pdf` (Median FCI by 2 m² NIA bin and fitted monotone static reference)
- **Figure 4** → `results/figures/g4/F5.pdf` (All-pair median ΔEA in m² and % of NIA with support bounds)
- **Figure 5** → `results/figures/g4/F6.pdf` (Within-bin FCI interquartile range across 2 m² NIA bins)
- **Figure 6** → `results/figures/g4/F10.pdf` (Panels A–F: Hong Kong 390-shell adequacy, switching, and size-band trade-offs) + `results/figures/g4/F12.pdf` (Panel G: K3 furniture kit footprints and training/transfer tables)

### Main tables
- **Table 1** → `results/tables/g4/T1.md` (Datasets and analysis coverage)
- **Table 2** → `results/tables/g4/T3.md` (Household daily activity schedules; reader-facing household names)
- **Table 3** → `results/tables/g4/T4.md` (Matched effects, equivalent-area gains, and minimum adequate area reductions; `Observed plans` naming)
- **Table 4** → `results/tables/g4/T7.md` (Classification disagreement between fixed floor-area cutoffs and modeled adequacy)

### Supplemental figures and tables
- **Figure S1** → `results/figures/g4/F2.pdf`
- **Figure S2** → `results/figures/g4/F3b_10.pdf` (Panel A: 10.00 m² cutaway) + `results/figures/g4/F3b_30.pdf` (Panel B: 29.97 m² whole-flat + daytime detail)
- **Figure S3** → `results/figures/g4/F7.pdf`
- **Figure S4** → `results/figures/g4/F8.pdf` (with held-out Swiss Dwellings Spearman $\rho$, bound-violation counts, and post-hoc ROC AUCs in the legend)
- **Figure S5** → `results/figures/g4/F9.pdf`
- **Figure S6** → `results/figures/g4/F11.pdf`
- **Table S1** → `results/tables/g4/T2.md`
- **Table S2** → `results/tables/g4/T5.md`
- **Table S3** → `results/tables/g4/T6.md` (D1 held-out test rows included directly; full D2 and D3 external transfer rows referenced in `results/tables/g4/T6.md` and `results/expC/metrics.csv`)
- **Table S4** → `results/g3_review_k3/kit.yaml`, `results/g3_review_k3/paired_effects.csv`, `results/g3_review_k3/hk_h3_size_bands.csv`, `results/g3_review_k3/hk_adequacy_by_size.csv`, and `reports/phase_11d_K3.md` (Kit comparisons: training selection & bespoke capture, paired cohort contrasts, and Hong Kong per-size adequacy counts)

## 2. Explicit placeholders to resolve before submission

1. **`[NEEDS EVIDENCE: ...]` (0 tags):**
   - Resolved in draft v2: the `[NEEDS EVIDENCE]` tag in `Results §2` was removed because all cited S0 full-function shares are supported directly by `Table 3` (`results/tables/g4/T4.md`, "Full S0" column).
2. **`[CITE: ...]` (10 distinct items across 12 occurrences in `STAR Methods` and `References`):**
   - Software/model citations not listed in `docs/RESEARCH_PLAN.md` §10: `[CITE: Google OR-Tools CP-SAT solver]`, `[CITE: PyTorch]`, `[CITE: LightGBM]`, `[CITE: scikit-learn]`, `[CITE: GraphSAGE (Hamilton et al.)]`.
   - Incomplete metadata fields flagged for verification until `codex/paper-refs` merges: `[CITE: verify dataset release year]` for Archilyse AG (Swiss Dwellings v3.0.0), `[CITE: verify volume and pages]` for Bu and Che Mat (2026), `[CITE: verify journal volume and pages]` for Elmurodov and Mametova (2026), `[CITE: verify issue number and DOI]` for Ulrich (2025), and `[CITE: verify issue year and volume]` for Xiong et al. (2020).
   - Per `reviews/paper_draft_v1_review.md` Item 5, truncated DOIs from upstream screening files (`Zeng et al. 2026`, `Xiong et al. 2020`, `Mustafa and Ali 2022`) were **not** repaired by hand; once `codex/paper-refs` merges, regenerate the entire `## References` section solely from `paper/references.bib`.
3. **Author / archive placeholders:**
   - `[AUTHOR TO FILL]` (author names, affiliations, lead contact, eTOC author name, acknowledgments, author contributions, declaration of interests) and `[TO MINT]` (Zenodo archive DOI).

## 3. Changes in draft v2 (`gemini/paper-draft-v2`, addressing `reviews/paper_draft_v1_review.md`)

- **[must] Item 1 (`Results §2`):** Removed the `[NEEDS EVIDENCE]` tag after the `S0` full-capacity shares (`Table 3` "Full S0" column already supports every cited figure) without adding unsupported adequacy shares or CIs.
- **[must] Item 2 (`Discussion P4` & `References`):** Removed the misused `(Johanes et al., 2026)` citation from the `0.90 m wheelchair circulation` clause, cited `(Figure S5)` instead, and removed the uncited `Johanes et al. (2026)` entry from `## References`.
- **[must] Item 3 (`Results §4, P2`):** Replaced the unsupported phrase `"preserved household rankings"` with the exact committed per-condition maximum absolute changes in mean S2 FCI (`−0.0160` across $0.8\times/1.2\times$ clearance scaling, `−0.0102` across 30/60/120 s solver caps, and `−0.0267` for couples / `−0.0199` for parent and child when dropping the drop-leaf table; `Figure S5`, `reports/GATE_G3.md`, `reports/phase_09_ablation_results.md`).
- **[must] Item 4 (`Introduction P1`):** Revised the Weber et al. (2024) sentence from `"across many urban building types"` to `"for many buildings in the cities studied"` (`reports/novelty_check.md` row 7).
- **[must] Item 5 + Addendum (`References` & inline citations):** Dropped `Yunitsyna (2014)` from `Introduction P2`, `Discussion P2`, and `## References`; replaced constructed issue/DOI on `Ulrich (2025)` with `*Buildings*, 15, 2623. [CITE: verify issue number and DOI]`; aligned `Collins et al. (2022)` and `Sun et al. (2025)` venue strings verbatim with `docs/RESEARCH_PLAN.md` §10 (`*CVPR*`); left truncated DOIs (`Zeng et al.`, `Xiong et al. 2020`, `Mustafa and Ali`) untouched pending regeneration from `paper/references.bib`.
- **[must] Item 6 (`Results §6` & `Table S4`):** Split the second paragraph of `Results §6` into two focused paragraphs—(a) single commuter (`no improvement`, `184` vs `246` of 390 Hong Kong shells) and (b) couple (`size-band trade-off`, training `+0.0021` [−0.0336, +0.0279] and `5` vs `2` of 30; Hong Kong $A_{\min}$ `15.39` vs `16.12` m²; `51` vs `30` of 120 at 13–16 m²; `0` of 150 and `0.448` vs `0.500` mean $\text{FCI}_q$ below 13 m²)—and moved matched-search variants, held-out and observed-plan contrasts, bespoke capture, and per-size counts into new Supplementary **Table S4**.
- **[should] Item 7 (`Discussion P4` & `Figure S4` legend):** Shortened the GraphSAGE negative-result discussion in `Discussion P4` to one concise sentence and moved the held-out Spearman $\rho$ ranges (`0.087–0.661`, `0.088–0.588`), bound-violation count (`23 of 33`), and post-hoc ROC AUCs (`0.796`, `0.888`) into the `Figure S4` legend.
- **[should] Item 8 (`Results §1, P1`):** Removed the ABO product-listing counts (`43,002` of `147,702`) and `94` zero-score layouts from `Results §1, P1` (retaining them in `STAR Methods`).
- **[should] Item 9 (`Introduction P2–P3`):** Split `Introduction P2` into two focused paragraphs—(P2) area rules and static functional standards, and (P3) transformable-interior studies and computational layout methods ending with the root-cause sentence.
- **[should] Item 10 (Calibrated word choice):** Changed `"strictly conditional"` → `"conditional"`, `"confirming Özer and Jacoby's (2022)"` → `"consistent with Özer and Jacoby's (2022)"`, and calibrated `"confirm"`/`"demonstrates"` in `Results`.
- **[should] Item 11 (Main-text word count):** Kept `Summary` → `Discussion` well below 4,800 words (~4,480 words).
