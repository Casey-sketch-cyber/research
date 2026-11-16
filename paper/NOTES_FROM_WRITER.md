# Writer handover notes (`gemini/paper-draft-v3`)

## 1. Manuscript-to-artifact mapping

### Main figures and graphical abstract
- **Graphical Abstract** → `paper/figures/fig1/GraphicalAbstract.pdf` (`paper/figures/fig1/GraphicalAbstract.png`)
- **Figure 1** → `paper/figures/fig1/Figure1.pdf` (`paper/figures/fig1/Figure1.png`; four-panel layout `A–D`)
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

1. **`[NEEDS EVIDENCE: ...]`:** **0 tags remaining.**
2. **`[CITE: ...]`:** **0 tags remaining.**
   - `## References` contains 30 cited entries generated solely from `paper/references.bib` (out of 32 entries in `paper/references.bib`; `johanes2026adaptable` and `yunitsyna2014universal` remain uncited per `reviews/paper_draft_v1_review.md` Items 2 & 5 and `reviews/paper_round2_review.md`).
   - Per `reviews/paper_round2_review.md` ("Draft v3" items 2–3), `qaradaghi2022area` is rendered with Crossref's author names (`Mustafa, C., and Ali, A., 2022`) for citation matching, while `PyTorch 2.7.1`, `LightGBM 4.7.0`, `scikit-learn 1.9.1`, and `GraphSAGE` are documented with versions and URLs in the `Key resources table` without bibliography entries.
3. **Author / archive placeholders:**
   - `[AUTHOR TO FILL]` (author names, affiliations, lead contact, eTOC author name, acknowledgments, author contributions, declaration of interests) and `[TO MINT]` (Zenodo archive DOI).

## 3. Changes in draft v3 (`gemini/paper-draft-v3`, addressing `reviews/paper_round2_review.md` "Draft v3")

- **Item 1 (`## References` regenerated from `paper/references.bib` only):** Regenerated all 30 cited bibliography entries directly from `paper/references.bib`, resolving all volume, issue, page, author-list, and DOI details and removing `[CITE: verify …]` from `Ulrich (2025)`, `Bu and Che Mat (2026)`, `Elmurodov and Mametova (2026)`, and `Xiong et al. (2021)`, while updating inline publication years (`Ashkevari and Farhady, 2023`; `Xiang et al., 2026`; `Xiong et al., 2021`) and corporate/dataset attributions (`Government of the Hong Kong Special Administrative Region, 2025`; `Abouagour and Garyfallidis, 2025`) to match `paper/references.bib`.
- **Item 2 (New `.bib` entries & software table):** Cited `Perron et al. (2023)` (`perron2023cpsat`) for Google OR-Tools CP-SAT, `Standfest et al. (2022)` (`standfest2022swiss`) for Swiss Dwellings v3.0.0, and `Fu et al. (2024)` (`fu2024magic`), `Li et al. (2026)` (`li2026homeworld`), and `Nieciecki et al. (2026)` (`nieciecki2026comfortable`) in `Introduction P3`; removed `[CITE: …]` tags from `PyTorch`, `LightGBM`, `scikit-learn`, and `GraphSAGE`, listing their versions and URLs in the `Key resources table` without bibliography entries.
- **Item 3 (Crossref author form):** Retained `Mustafa and Ali (2022)` in inline citations and `## References` (`Mustafa, C., and Ali, A. (2022)` with `9(2), 23–37` and `https://doi.org/10.17656/sjes.10154` from `qaradaghi2022area`).
- **Item 4 (`Figure 1` legend rewritten for Figure 1 v2):** Rewrote the `Figure 1` legend (`paper/figures/fig1/Figure1.pdf`) for the decluttered four-panel layout (`A Inputs`, `B Strategies`, `C Verified optimization`, `D Function → area`), incorporating all corpus, strategy, validator, FCI, $\Delta\text{EA}$, $A_{\min}$, and form/time decomposition definitions moved out of the figure.
- **Item 5 (Preserve everything else):** Kept all quantitative results, tables, and prose outside the requested reference and `Figure 1` legend updates unchanged.
