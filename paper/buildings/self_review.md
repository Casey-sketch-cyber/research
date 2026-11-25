# Adversarial self-review (`paper/buildings/manuscript.md`)

Prepared per `GEMINI.md`, `docs/WRITING_GUIDE.md` §9, and `docs/BUILDINGS_REWRITE_TASK.md` for the *Buildings* (MDPI) Stage 1 rewrite on branch `gemini/buildings-rewrite`. Each item is graded as **`pass`**, **`needs revision`**, or **`needs new analysis`**.

---

## 1. Contribution

### 1.1 What new knowledge do readers gain? — `pass`
- **Answer and evidence:** *Buildings* readers (architects, building scientists, housing researchers) learn that transformable furniture's floor-area savings are large where static arrangements bottleneck, yet strictly conditional on household composition and dwelling size. Across 2109 observed plans (`D1 + D2`) and 510 generated shells (`D3`), static furniture (`S0`) already serves 100% of scheduled daily activities in 61.0%–90.8% of observed plans (`Section 3.2`, `Table 3`), leaving all-pair median $\Delta\text{EA} = 0\text{ m}^2$. Gains concentrate in two-person households of intermediate compact size—median identified positive $\Delta\text{EA}$ of 6.21 m² [4.20, 10.00] for couples and 5.00 m² [4.20, 8.00] for parent-and-child households on observed plans, and generated-shell bin peaks of 7.32 m² (14–16 m²) and 6.00 m² (18–20 m²) (`Section 3.3`, `Figure 4`, `Table 3`). Readers also learn the physical mechanism split (couples: 0.0130 FCI form vs 0.0112 FCI switching; parent and child: 0.0271 vs 0.0017 FCI; `Section 3.4`), how fixed area cutoffs misclassify compact dwellings (55.7% and 52.7% disagreement at 45 m² on observed plans; 30.0%–49.6% at 8 m² on generated shells; `Section 3.5`, `Table 4`), and how daily switching (2.24 m² $A_{\min}$ reduction for couples) and size-band kit trade-offs operate in 390 Hong Kong model shells (`Section 3.6`, `Figure 6`, `Table S3`).

### 1.2 Is the failure we address meaningful and not trivial? — `pass`
- **Answer and evidence:** Yes. Minimum space regulations (Hong Kong's 8 m² Basic Housing Units Ordinance; Ulrich's 30/45/60 m² normative thresholds) directly shape urban housing supply, residential livability, and building-stock carbon (`Section 1`, P1). Existing area rules ignore plan geometry, static functional audits omit daily temporal reuse (`Section 1`, P2), single-room transformable studies conflate product capability with manual layout drawing (`Section 1`, P3), and computational generators lack 24-hour fixed-anchor scheduling, independent entrance-to-furniture walkability checks, and housing-scale m² translation (`Section 1`, P4).

### 1.3 Is the idea non-obvious, or is the gain predictable? — `pass`
- **Answer and evidence:** Three findings counter naive intuition: (1) **Nonmonotonic size profile**—equivalent-area savings do not peak in the smallest 8–10 m² micro-shells (0.69–0.75 m²) because operating clearances and wet-service access cannot fit; savings peak at 14–20 m² before returning to 0 m² (`Section 3.3`, `Figure 4`). (2) **Divergent two-person mechanisms**—couples rely heavily on day–night wall-bed switching (worth 2.24 m² in Hong Kong model shells), whereas parent-and-child households benefit almost entirely from compact static-state footprints (`Section 3.4`, `Section 3.6`). (3) **Size-band kit trade-off and surrogate failure**—downsized commuter kits hurt adequacy (184 vs 246/390), larger couple kits help at 13–16 m² (+21/120 shells) while reducing capacity below 13 m² (0.448 vs 0.500), and geometry-only GraphSAGE fails to reach $\rho \ge 0.80$ (`Section 3.6`, `Section 4.1`, `Figure S7`, `Table S4`).

### 1.4 Which novelty type do we claim? — `pass`
- **Answer and evidence:** Without using forbidden priority claims ("first", "novel", "unprecedented"), `Section 1` states three explicit research questions (`RQ1–RQ3`) and three concrete contributions: (1) verifiable schedule-aware capacity metric (`FCI`) and m² translation pipeline (`ΔEA`, `A_min`); (2) corpus-scale paired empirical evidence decomposing form and daily switching effects and reconciling single-room claims; and (3) empirical evaluation of area-only housing standards plus Hong Kong size-band furniture kit sizing.

---

## 2. Clarity

### 2.1 Is the work reproducible from the text? — `pass`
- **Answer and evidence:** `Section 2` (Materials and Methods, placed before Results in MDPI order) specifies all dataset versions, citations, sample counts, NIA zone classes, 0.10 m empty-geometry screening (and 94 valid zero-score empty layouts), all six daily time slots (`Table 2`), all 16 audited furniture types (`Table S1`), candidate strides and solver caps ($\le 20\text{ m}^2$: 0.10 m stride, 120 s; $> 20\text{ m}^2$: 0.20 m stride, 30 s), CP-SAT objective weights ($1000.0, -1.0, 0.01$), lazy reachability cuts (5.0 s rounds, up to 30 iterations), exact `FCI` and `TB` equations, support-bound inversion rules, logistic $A_{\min}$ withholding criteria, fixed seed `20261105`, locked software versions (`Section 2.11`), and public repository URL `https://github.com/liangdagongjue-code/research`.

### 2.2 Does every module have a motivation? — `pass`
- **Answer and evidence:** Every subsection `2.1`–`2.10` opens by stating the methodological failure it prevents (e.g., empty-geometry screening prevents conflating broken vectorizations with furniture failure; zero-shared-code validation prevents solver encoding bugs; monotone cumulative-maximum inversion with explicit support bounds prevents out-of-support extrapolation).

### 2.3 Are terms, notation, and MDPI formatting consistent? — `pass`
- **Answer and evidence:**
  - Terminology follows `docs/PAPER_STORY.md` §6 strictly (`functional capacity index (FCI)`, `static (S0)`, `form only (S1)`, `form + time (S2)`, `form effect`, `time effect` / `switching effect`, `equivalent-area gain (ΔEA)`, `minimum adequate area (A_min)`, `net internal area (NIA)`, `observed plans`, `generated shells`, `Hong Kong model shells`, `transformable furniture`).
  - MDPI conventions verified programmatically: Abstract ≤ 200 words (single paragraph, no headings, no citations), 7 semicolon-separated keywords, sections `1.`–`5.` in exact MDPI order, Back Matter in exact MDPI order (`Supplementary Materials` → `References`), verbatim Funding/Author Contributions/AI declaration, Pandoc citation keys (`[@key]`) throughout with zero author–year text or hand-numbered brackets, thousands comma only on 5+-digit integers (`31,428` vs `2619`), inline figure/table captions immediately after first citation, strict sequential numbering (`Figure 1–6`, `Table 1–4`, `Figure S1–S7`, `Table S1–S4`), and 3-zone acronym definitions (Abstract, Main text, first Figure/Table).

### 2.4 Does each paragraph carry one message? — `pass`
- **Answer and evidence:** `Section 1` progresses cleanly from housing-regulation problem → area/static standards gap → single-room transformable gap → computational layout gap & root cause → approach → RQ1–RQ3 + contributions + paper roadmap. `Section 3` trims definitions already given in `Section 2` and keeps six claim-headed subsections (`3.1`–`3.6`). `Section 4` separates prior-work interpretation (`4.1`), concrete design/policy implications grounded in Section 3 (`4.2`), and three explicit scope boundaries (`4.3`). `Section 5` concisely answers RQ1–RQ3 in two paragraphs (~250 words) with zero new numbers.

---

## 3. Strength of results

### 3.1 Is the gain or finding meaningful, not marginal? — `pass`
- **Answer and evidence:** Observed-plan median identified positive $\Delta\text{EA}$ reaches 6.21 m² [4.20, 10.00] (couples) and 5.00 m² [4.20, 8.00] (parent and child); generated-shell peaks reach 7.32 m² (49.8% NIA) and 6.00 m² (33.3% NIA); parent-and-child observed $\Delta A_{\min}$ is 10.78 m² [9.15, 12.70]; Hong Kong couple daily switching lowers $A_{\min}$ by 2.24 m² [1.66, 2.82]; and 45 m² cutoffs disagree on 55.7% and 52.7% of observed two-person cases (`Table 3`, `Table 4`, `Figure 4`, `Figure 6`).

### 3.2 Is it consistent across datasets and settings? — `pass`
- **Answer and evidence:** `D1` (Swiss Dwellings), `D2` (ResPlan), `D3` (generated shells), and the 390-shell Hong Kong grid all exhibit the same structural patterns: high static saturation in larger footprints, concentration of gains in two-person schedules, form dominance for single-person and parent-and-child schedules versus joint form + switching gains for couples, and large within-bin dispersion (`Table 3`, `Figure 3`, `Figure 5`).

### 3.3 Are failures and negative or bounded results reported? — `pass`
- **Answer and evidence:** Prominently reported in Results, Discussion, Conclusions, and Supplementary Tables: 0 m² all-pair median $\Delta\text{EA}$ on observed plans; support-bounded single-commuter observed gains ($\ge 2.00\text{ m}^2$); zero switching ($\text{TB} = 0.00$) in the 10.00 m² and 29.97 m² showcases; 11/200 benchmark cases with 0.0034 FCI mean shortfall; negative geometry-only surrogate results (`Table S4`, `Figure S7`); commuter kit non-improvement (`184/390` vs `246/390`); and couple kit degradation below 13 m² (`0.448` vs `0.500`; `Table S3`).

---

## 4. Completeness

### 4.1 Are the key comparisons, comparators, and metrics present? — `pass`
- **Answer and evidence:** Paired S0/S1/S2 comparisons (`Table 3`), four-solver benchmark (`Figure S3`, `Table S2`), statutory 8 m² and normative 30/45 m² area comparators (`Table 4`), single-room daytime body-free reconciliation (`Figure S6`), four geometry-only surrogate families (`Figure S7`, `Table S4`), and full parametric kit training/transfer/Hong Kong grids (`Figure 6`, `Figure S5`, `Table S3`). Zero `[NEEDS EVIDENCE]` placeholders remain.

### 4.2 Are the sensitivity analyses there? — `pass`
- **Answer and evidence:** `Section 2.9`, `Section 3.4`, and `Figure S4` cover mirrored one-side double-bed access (348 units $\le 20\text{ m}^2$), global clearance scaling ($0.8\times, 1.2\times$), drop-one transformable removals, 0.90 m walking width and older-adult schedule, grid resolution (0.05, 0.10, 0.20 m), solver caps (30, 60, 120 s), adequacy thresholds $\tau \in \{0.90, 0.95, 1.00\}$, and pooled-reference curve inversion (`Table 3`).

### 4.3 Is the data challenging and representative enough? — `pass`
- **Answer and evidence:** Combining 1236 Swiss Dwellings apartments, 873 ResPlan apartments, 510 parametric generated shells (8–40 m²), and 390 Hong Kong integer-area shells (8–20 m²) covers both real partitioned housing stocks and ultra-compact micro-housing footprints absent from public datasets (`Table 1`, `Figure S1`).

---

## 5. Soundness

### 5.1 Is the setting realistic? — `pass`
- **Answer and evidence:** All layouts enforce wall containment, tall-item window rules, door-swing keep-outs, ABO-audited dimensions (`Table S1`), zero body overlap, unobstructed directional clearances, continuous 0.60 m entrance-to-service and entrance-to-furniture reachability, and shared anchor positions across slots (`Section 2.4`–`2.6`, `Figure 2`).

### 5.2 Are any assumptions unreasonable? — `pass`
- **Answer and evidence:** Key assumptions (two-sided double-bed access, 0.60 m walking width, clearance scale, stylized schedules, and catalogue sizing) are directly stress-tested (`Section 3.4`, `Section 3.6`, `Figure S4`, `Table S3`), while unmodeled experiential comfort dimensions and census joint-distribution limits are explicitly bounded in `Section 4.3`.

### 5.3 Is it robust without per-case tuning? — `pass`
- **Answer and evidence:** One frozen configuration runs across all 2619 dwellings and four households (31,428 layouts) with 100% independent validator compliance, matching the best of four search methods on 189/200 benchmark pairs (`Section 3.1`, `Table S2`).

### 5.4 Do the benefits outweigh the new limitations? — `pass`
- **Answer and evidence:** Yes. Although explicit CP-SAT optimization takes seconds per dwelling rather than millisecond GNN inference and `FCI` scopes out subjective comfort, it delivers an auditable square-meter evaluation that exposes 52.7%–55.7% misclassification in fixed area cutoffs and pinpoints exact household and size bands where transformable furniture saves floor area.
