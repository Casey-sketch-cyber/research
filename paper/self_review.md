# Adversarial self-review (`paper/manuscript.md`)

Prepared per `GEMINI.md` and `docs/WRITING_GUIDE.md` §9. Each item is answered with specific evidence from `paper/manuscript.md` and the committed result files, and graded as **`pass`**, **`needs revision`**, or **`needs new analysis`**.

---

## 1. Contribution

### 1.1 What new knowledge do readers gain? — `pass`
- **Answer and evidence:** Readers learn that the floor-area savings of transformable furniture are substantial where static furniture hits geometric bottlenecks, yet strictly **conditional** on household composition and dwelling size rather than universal across small homes. Specifically, across 2,109 observed plans (`D1` + `D2`) and 510 generated shells (`D3`), static furniture (`S0`) already serves the full 24-hour schedule in 61.0%–90.8% of observed plans (`Table 3`), concentrating gains in two-person households at intermediate compact sizes (median identified positive $\Delta\text{EA}$ of 6.21 m² [4.20, 10.00] for couples and 5.00 m² [4.20, 8.00] for parent-and-child households on observed plans; all-pair bin peaks of 7.32 m² at 14–16 m² and 6.00 m² at 18–20 m² on generated shells; `Results §2–§3`, `Figure 4`, `Table 3`). Readers also learn *how* households gain—nearly equally via compact form (0.0130 FCI) and daily switching (0.0112 FCI) for couples, versus predominantly compact form (0.0271 versus 0.0017 FCI) for parent-and-child households (`Results §4`)—and that fixed 45 m² two-person area cutoffs disagree with modeled S2 adequacy on 55.7% of couple and 52.7% of parent-and-child cases (`Results §5`, `Table 4`).

### 1.2 Is the failure we address meaningful and not trivial? — `pass`
- **Answer and evidence:** Yes. Statutory housing standards (such as Hong Kong's 8 m² Basic Housing Units Ordinance minimum) and normative flourishing standards (such as Ulrich's 30/45/60 m² benchmarks) govern urban housing supply, overcrowding enforcement, and embodied carbon (`Introduction P1`). Yet area-only rules ignore furniture fit and walkability, static functional standards omit daily temporal sharing, single-room studies mix furniture capability with manual layout drawing on isolated rooms, and generative layout models do not verify multi-slot pedestrian reachability or translate functional gains into m² across housing stocks (`Introduction P2`, `Discussion P2`).

### 1.3 Is the idea non-obvious, or is the gain predictable? — `pass`
- **Answer and evidence:** Neither the empirical outcome nor the computational requirement is predictable a priori:
  1. **Nonmonotonic size profile:** Contrary to the intuitive expectation that the smallest micro-units benefit most (`H1` in `reports/FINAL_SUMMARY.md`), two-person equivalent-area gains start small at 8–10 m² (0.75 m² for couples, 0.69 m² for parent and child), peak at intermediate compact sizes (14–20 m²), and return to 0 m² once static layouts fit (`Results §3`, `Figure 4`), because ultra-small shells cannot fit even stowed/deployed clearances alongside wet-service access (`Figure 2`, `Figure S2`).
  2. **Divergent mechanisms across two-person households:** Two-person schedules do not behave alike—couples rely on day–night wall-bed switching (worth 2.24 m² [1.66, 2.82] in Hong Kong model shells), whereas parent-and-child households gain mainly from static-state compact footprints (`Results §4`, `Results §6`).
  3. **Size-band furniture trade-offs and surrogate failure:** Custom downsized kits fail to improve commuter capacity, larger couple kits help at 13–16 m² (+21/120 adequate shells) while hurting below 13 m² (`Results §6`, `Figure 6`), and GraphSAGE surrogates fail to reach $\rho \ge 0.80$ on held-out observed sites (`Discussion P4`, `Figure S4`, `Table S3`), proving that explicit geometric optimization and validation cannot be trivially replaced by polygon summary features.

### 1.4 Which novelty type do we claim: task, metric, pipeline, module, design choice, finding, or insight? — `pass`
- **Answer and evidence:** Without using forbidden priority claims ("first", "novel", "unprecedented"), `Introduction P5` explicitly states three concrete contributions: (1) **metric + pipeline**—a schedule-aware, independently verifiable measure of functional capacity (`FCI`) translatable into equivalent floor area ($\Delta\text{EA}$) and adequate area ($A_{\min}$); (2) **empirical finding / insight**—corpus-scale paired evidence decomposing form and daily switching effects and revealing the nonmonotonic size profile; and (3) **policy and design finding**—quantifying area-cutoff misclassification and demonstrating size-band-dependent furniture kit trade-offs in Hong Kong model shells.

---

## 2. Clarity

### 2.1 Is the work reproducible from the text? — `pass` (with pending reference BibTeX & Zenodo DOI noted below)
- **Answer and evidence:** `STAR Methods` specifies exact dataset versions and filters (`D1` $n=1,236$, `D2` $n=873$, `D3` $n=510$, `D4` 43,002 triples, `D6` 108,202 subdivided units), NIA zone classes, the 0.10 m empty-geometry screen, all six daily slots and capability rules (`Table 2`), all 16 static and transformable items with footprints, clearances, instance caps, and effort weights (`Table S1`), anchor strides and solver caps ($\le 20\text{ m}^2$: 0.10 m stride, 120 s; $> 20\text{ m}^2$: 0.20 m stride, 30 s), objective weights ($1000.0, -1.0, 0.01$), lazy reachability settings (5.0 s rounds, up to 30 iterations), exact `FCI` and `TB` equations, support-bound inversion rules, logistic $A_{\min}$ withholding criteria, `Key resources table` locked package versions (`Python 3.11.18`, `ortools 9.15.6755`, `torch 2.7.1`, `lightgbm 4.7.0`, `scikit-learn 1.9.1`, `Blender 4.5.3 LTS`), and seed `20261105`.

### 2.2 Does every module have a motivation? — `pass`
- **Answer and evidence:** Every subsection of `STAR Methods` (`Method details`) opens with the specific methodological problem it resolves—for example, why NIA normalization and an unfurnished walkability screen prevent conflating broken vectorizations with furniture failure, why automated per-strategy optimization removes manual drawing bias, why a zero-shared-code validator prevents discretization bugs, and why cumulative-maximum bin-median inversion avoids parametric extrapolation outside NIA support.

### 2.3 Are terms and notation consistent? — `pass`
- **Answer and evidence:** Checked programmatically across the entire manuscript against `docs/PAPER_STORY.md` §6:
  - Uses `functional capacity index (FCI)`, `static (S0)`, `form only (S1)`, `form + time (S2)`, `form effect`, `time effect` / `switching effect`, `equivalent-area gain (ΔEA)`, `adequate area (A_min)`, `net internal area (NIA)`, `observed plans`, `generated shells`, `Hong Kong model shells`, `single commuter`, `single remote worker`, `couple`, `parent and child`, and `transformable furniture`.
  - Zero occurrences in prose or tables of `efficiency score`, `baseline`, `ours`, `real data`, `H1–H5` household codes, `novel`, `unprecedented`, or `convertible`/`smart` (outside verbatim cited paper titles in `References`).

### 2.4 Does each paragraph carry one message? — `pass`
- **Answer and evidence:** Reverse-outlined across `Introduction` (5 paragraphs: P1 stakes → P2 gap & root cause → P3 approach & why it works → P4 headline findings → P5 contributions), `Results` (6 claim-headed subsections, 12 topic-led paragraphs), and `Discussion` (4 paragraphs + `Limitations of the study`: D1 core synthesis → D2 reconciliation with single-room literature & standards → D3 implications for regulators/designers/manufacturers → D4 transferability & negative surrogate lesson → Limitations 3 scope boundaries). Every paragraph opens with a declarative topic sentence supported by linked quantitative evidence.

---

## 3. Strength of results

### 3.1 Is the gain or finding meaningful, not marginal? — `pass`
- **Answer and evidence:** Where static layouts bottleneck, gains are large in architectural and regulatory terms: median identified positive $\Delta\text{EA}$ is 6.21 m² [4.20, 10.00] for couples and 5.00 m² [4.20, 8.00] for parent-and-child households on observed plans (`Table 3`); generated-shell bin medians peak at 7.32 m² (49.8% of NIA) for couples at 14–16 m² and 6.00 m² (33.3% of NIA) for parent and child at 18–20 m² (`Figure 4`); parent-and-child observed-plan $\Delta A_{\min}$ is 10.78 m² [9.15, 12.70] (`Table 3`); and daily switching lowers couple $A_{\min}$ by 2.24 m² [1.66, 2.82] in Hong Kong model shells (`Figure 6`). Equally meaningful is the policy finding that a 45 m² cutoff misclassifies 55.7% and 52.7% of observed two-person cases (`Table 4`).

### 3.2 Is it consistent across datasets and settings? — `pass`
- **Answer and evidence:** Both observed repositories (`D1` Swiss Dwellings and `D2` ResPlan) and controlled `D3` shells show the same structural ordering: high static saturation in larger footprints (`D2` > `D1` > `D3`), larger improvements for two-person than one-person schedules (`Table 3`), dominance of the form effect for single-person and parent-and-child schedules versus near-equal form and switching effects for couples (`Table 3`), and wide within-bin FCI dispersion (`Figure 5`).

### 3.3 Are failures and negative or bounded results reported? — `pass`
- **Answer and evidence:** Yes, prominently and transparently:
  - Zero all-pair median $\Delta\text{EA}$ across all four households on observed plans (`Results §2`, `Table 3`).
  - Support-bounded (unidentified point median, $\ge 2.00\text{ m}^2$) $\Delta\text{EA}$ for observed-plan single commuters (`Results §3`, `Table 3`).
  - Zero switching benefit ($\text{TB} = 0.00$) in both the 10.00 m² shell (where no double bed fits) and the 29.97 m² partitioned flat (`Results §1`, `Figure 2`, `Figure S2`).
  - 11 of 200 benchmark cases where another search arm slightly exceeded production (mean shortfall 0.0034 FCI; `Results §1`).
  - Negative result for geometry-only surrogates (`GraphSAGE` $\rho = 0.087\text{–}0.661$ on S0 and $0.088\text{–}0.588$ on S2, plus 23/33 bound violations on held-out `D1` sites; `Discussion P4`, `Figure S4`, `Table S3`).
  - No improvement from parametric commuter kits, confidence intervals crossing zero on the 30-shell couple kit training mean ($+0.0021$ [$-0.0336$, $+0.0279$]), only 7.4% of bespoke gain captured, and reduced couple $\text{FCI}_q$ below 13 m² (0.448 versus 0.500; `Results §6`, `Figure 6`).

---

## 4. Completeness

### 4.1 Are the key comparisons, comparators, and metrics present? — `pass` (with one open supplementary summary table flagged `needs new analysis`)
- **Answer and evidence:** The manuscript compares `S0`, `S1`, and `S2` within every dwelling; benchmarks four layout search algorithms (`Table S2`, `Figure S3`); compares modeled adequacy against both Ulrich's (2025) 30/45 m² flourishing cutoffs and Hong Kong's statutory 8 m² minimum (`Table 4`); bridges room-level body-free area to Bu and Che Mat (2026) (`Discussion P2`, `Figure S6`); and compares four learned surrogate families (`Table S3`, `Figure S4`).
- **Flagged `needs new analysis` item (`docs/PAPER_STORY.md` §9):** `Results §2` carries the explicit placeholder `[NEEDS EVIDENCE: committed table of the share with FCI = 1 and FCI ≥ 0.95 by household × strategy on observed plans, with unit-bootstrap CIs]`, awaiting the scheduled Codex task in `docs/PAPER_STORY.md` §9.

### 4.2 Are the sensitivity analyses there? — `pass`
- **Answer and evidence:** `Results §4`, `STAR Methods`, and `Figure S5` report: (i) mirrored one-side double-bed access across 348 small units ($\le 20\text{ m}^2$ NIA); (ii) global clearance scaling ($0.8\times, 1.2\times$); (iii) single-item drop-one transformable ablations; (iv) walking-width widening from 0.60 m to 0.90 m (and the older-adult sensitivity schedule); (v) raster/anchor grid resolution ($0.05\text{ m}, 0.20\text{ m}$) and solver time caps ($30, 60, 120\text{ s}$); (vi) adequacy thresholds $\tau \in \{0.90, 0.95, 1.00\}$; and (vii) pooled-reference static curve re-inversion (`Table 3`, `Results §3`).

### 4.3 Is the data challenging and representative enough? — `pass`
- **Answer and evidence:** Combining 1,236 European apartments (`D1` Swiss Dwellings), 873 floor plans from `D2` (ResPlan), 510 controlled shells (`D3`, 8–40 m²), and 390 Hong Kong integer-area shells (`8–20 m²`) spans both real-world multi-room irregularities (corridors, oblique walls, doorway keep-outs) and the 8–16 m² micro-housing regime absent from public floor-plan repositories (`Table 1`, `Figure S1`).

---

## 5. Soundness

### 5.1 Is the setting realistic? — `pass`
- **Answer and evidence:** Every layout enforces wall containment, tall-item window restrictions, door-swing keep-outs, audited furniture dimensions checked against 43,002 ABO product triples, non-overlapping furniture bodies, unobstructed directional clearances, continuous 0.60 m walkable access from the entrance to fixed wet services and active clearances, and shared anchor positions across slots (`STAR Methods`, `Figure 2`, `Table S1`).

### 5.2 Are any assumptions unreasonable? — `pass`
- **Answer and evidence:** Key modeling choices—two-sided access on double beds, 0.60 m walking width, stylized schedules, and catalogue dimensions—are explicitly tested in sensitivity analyses (`Results §4`, `Figure S5`) and parametric kit experiments (`Results §6`, `Figure 6`), while non-modeled experiential dimensions (privacy, daylight, acoustics, comfort) and unweighted Hong Kong census context are explicitly bounded in `STAR Methods` and `Limitations of the study`.

### 5.3 Is it robust without per-case tuning? — `pass`
- **Answer and evidence:** A single frozen configuration (`config/project.yaml`, `config/furniture.yaml`, `config/households.yaml`) with size-stratified solver budgets ($\le 20\text{ m}^2$ versus $> 20\text{ m}^2$) runs across all 2,619 dwellings and four households (31,428 layouts) with 100% independent validator compliance and matches the best score across four search algorithms on 189 of 200 benchmark pairs (`Results §1`, `Table S2`).

### 5.4 Do the benefits outweigh the new limitations? — `pass`
- **Answer and evidence:** Yes. While `FCI` deliberately scopes out subjective comfort and requires 10–120 s of CP-SAT optimization per dwelling rather than millisecond GNN inference, it provides an objective, auditable m² ruler that exposes 52.7%–55.7% two-person misclassification by area-only rules and identifies the exact household and size bands where transformable furniture works.

---

## Unresolved items before journal submission

1. **`needs new analysis` (Codex task, `docs/PAPER_STORY.md` §9):** Generate and commit the table of observed-plan shares achieving $\text{FCI} = 1$ and $\text{FCI} \ge 0.95$ across all `household × strategy` (`S0`, `S1`, `S2`) cells with 1,000-resample unit-bootstrap 95% CIs, then replace the `[NEEDS EVIDENCE: ...]` tag in `Results §2`.
2. **`needs revision` once `codex/paper-refs` merges (`docs/REFERENCES_TASK.md`):** Replace inline author–year strings and the nine `[CITE: ...]` items (`Google OR-Tools CP-SAT solver`, `PyTorch`, `LightGBM`, `scikit-learn`, `GraphSAGE (Hamilton et al.)`, `Archilyse AG` release year, `Bu and Che Mat 2026` volume/pages, `Elmurodov and Mametova 2026` journal/volume/pages, and `Xiong et al. 2020` issue year/volume) from the verified `paper/references.bib`.
3. **`needs revision` once `codex/paper-fig1` merges (`docs/FIGURE1_SPEC.md`):** Pair `Figure 1` and the iScience **Graphical Abstract** (`paper/figures/fig1/Figure1.pdf`, `GraphicalAbstract.png`) with the `Figure 1` legend in `paper/manuscript.md`.
4. **Author metadata (`[AUTHOR TO FILL]` / `[TO MINT]`):** Fill author names, affiliations, lead contact email, acknowledgments, author contributions, declaration of interests, and the minted Zenodo archive DOI in `paper/manuscript.md`.
