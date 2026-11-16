# Writer handover notes (`gemini/paper-draft-v1`)

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
- **Figure S4** → `results/figures/g4/F8.pdf`
- **Figure S5** → `results/figures/g4/F9.pdf`
- **Figure S6** → `results/figures/g4/F11.pdf`
- **Table S1** → `results/tables/g4/T2.md`
- **Table S2** → `results/tables/g4/T5.md`
- **Table S3** → `results/tables/g4/T6.md` (D1 held-out test rows included directly; full D2 and D3 external transfer rows referenced in `results/tables/g4/T6.md` and `results/expC/metrics.csv`)

## 2. Explicit placeholders to resolve before submission

1. **`[NEEDS EVIDENCE: ...]` (1 tag, in `Results §2`):**
   - `[NEEDS EVIDENCE: committed table of the share with FCI = 1 and FCI ≥ 0.95 by household × strategy on observed plans, with unit-bootstrap CIs]` — corresponds to `docs/PAPER_STORY.md` §9 (open Codex task).
2. **`[CITE: ...]` (9 distinct items across 11 occurrences in `STAR Methods` and `References`):**
   - Software citations not listed in `docs/RESEARCH_PLAN.md` §10: `[CITE: Google OR-Tools CP-SAT solver]`, `[CITE: PyTorch]`, `[CITE: LightGBM]`, `[CITE: scikit-learn]`, `[CITE: GraphSAGE (Hamilton et al.)]`.
   - Incomplete metadata fields flagged for verification in `docs/RESEARCH_PLAN.md` §10 / `docs/REFERENCES_TASK.md`: `[CITE: verify dataset release year]` for Archilyse AG (Swiss Dwellings v3.0.0), `[CITE: verify volume and pages]` for Bu and Che Mat (2026), `[CITE: verify journal volume and pages]` for Elmurodov and Mametova (2026), and `[CITE: verify issue year and volume]` for Xiong et al. (2020).
   - Note: `Yunitsyna (2014)` is currently cited from `reports/novelty_check.md` (C4 table); if `codex/paper-refs` drops Epoka repository PDFs under `docs/REFERENCES_TASK.md` ("Skip theses, repository copies and low-quality venues"), remove `Yunitsyna, 2014` from the two parenthetical citation lists (`Introduction P2` and `Discussion P2`).
3. **Author / archive placeholders:**
   - `[AUTHOR TO FILL]` (author names, affiliations, lead contact, eTOC author name, acknowledgments, author contributions, declaration of interests) and `[TO MINT]` (Zenodo archive DOI).
