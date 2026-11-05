# Research Plan

**Working title:** *Functionally Equivalent Area: How Much Space Does Transformable Furniture Save, and What It Means for Minimum Dwelling Standards*

**Target venue:** *Urban Science* (MDPI), Special Issue "Urban Transformation and Sustainable Cities". Relevant topics in the call: AI and data-driven approaches; resource efficiency and circular economy; social equity, accessibility and quality of urban life; sustainable land use; urban governance and policy innovation.

**Time budget:** 3 weeks from start to submission. Computation (Codex) has about 2 weeks; the last week is for writing and revision.

---

## 1. Background and gap

Cities facing housing shortages keep producing very small dwellings: micro-apartments, co-living rooms and subdivided units. Policymakers regulate them with **minimum floor-area standards**. One example is Hong Kong's Basic Housing Units Ordinance (in force 1 March 2026), which requires at least 8 m² internal floor area, a separate toilet, a sink outside the toilet, minimum headroom, and adequate lighting and ventilation.

Floor area is a proxy. What a household needs is the ability to **carry out daily activities** (sleep, eat, work, rest, store belongings, receive a guest) with adequate ergonomic clearance. Transformable furniture (wall beds, sofa beds, drop-leaf tables, fold-down desks) lets the same floor area serve different activities at different times of day.

### Positioning: what this project builds on and what it adds

The aim isn't to be "first" at any one element. It is to combine what several strands have established into a tool that answers a question none of them answers alone: **how much dwelling area is transformable furniture worth for a given household, and what does that mean for minimum-size standards?**

| Strand | What it has established (we build on it) | Its limitation for our question | What this project adds |
|---|---|---|---|
| Functional space standards: Pedro (2009); Ulrich (2025) | Minimum areas can be derived from furniture and activities; multifunctional furniture and "temporal zoning" matter | Static, hand-made arrangements; time and transformable furniture are acknowledged but not quantified | Brings time of day and transformable states into a functional measure of the dwelling (FCI) |
| Single-room analysis: Bu & Che Mat (2026) | A folded wall bed can raise a 12 m² bedroom's activity area from about 5–5.5 m² to about 8 m² (≈60%) | One hand-drawn room, analytical; no household schedule or feasibility check | **Generalizes and tests** their estimate across thousands of real plans, household types and dwelling sizes. Does ~60% hold, and where does it shrink? |
| Transformable-layout graphics: Xiong et al.; Fu et al.; Liu et al. 2025 (DIFF); Zhang et al. 2025 (SceneExplorer); Xiong, Cai & Luo 2026; Garg et al. 2016 | How to represent, generate, sequence and animate multi-state furniture and layouts | Design-exploration tools; states aren't driven by household activity demand; no clearance/reachability guarantee or dwelling-level metric | A schedule-driven, constraint-guaranteed optimization with an independent validator, applied to real dwellings |
| Static layout optimization: Merrell 2011; Yu 2011; LayoutVLM 2025; HomeWorld 2026; Co-Layout 2025 | Effective constraint, IP and LLM methods for furniture placement | One static arrangement | Extends constraint-based placement to several time slots with shared anchors |
| Usability and efficiency at scale: Özer & Jacoby (2022); Weber et al. (2024); Goessler & Kaluarachchi (2023) | Size is an incomplete measure of usability; furniture-based "excess area" carries a carbon cost; adaptive homes may use space 2–3× more efficiently | Static furniture (Özer & Jacoby; Weber et al.); the 2–3× is a proposal without measurement (Goessler & Kaluarachchi) | Extends the usability argument to time-of-day use; puts a measured, distributional number on the adaptive-home efficiency proposal; complements "excess area" with "area that transformable furniture makes unnecessary" |
| Policy | Area-only minimums, e.g. Hong Kong's 8 m² basic housing units | Area says little about function | Tests an area-only minimum against functional adequacy and proposes a performance-based reading of minimum standards |

**Value proposition in one sentence:** we turn a design intuition ("transformable furniture makes small homes work like bigger ones"), so far supported by single-room analyses and proposals, into a measured, household-specific and policy-ready quantity across real housing stock.

See `reports/novelty_check.md` for the evidence behind this table.

## 2. Research questions and hypotheses

- **RQ1.** For a compact dwelling and a given household, how much more of the household's daily activity demand can be served with transformable furniture laid out per time slot, compared with static furniture?
- **RQ2.** What static-furniture floor area gives the same functional capacity as a transformable dwelling of area *A*? This is the **functionally equivalent area (FEA)**, and FEA − *A* is the **area saving**.
- **RQ3.** What does this imply at city scale for minimum-area standards, using Hong Kong's subdivided and basic housing units as the case?

| ID | Hypothesis | Tested in |
|---|---|---|
| H1 | Area saving is positive and largest, in both absolute and relative terms, in the smallest units, and it shrinks as area increases. | Exp. A |
| H2 | Functional capacity varies substantially among units of equal area, so area-only standards misclassify adequacy for a non-trivial share of units. This confirms and extends Özer & Jacoby (2022) to time-of-day use and transformable furniture. | Exp. D |
| H3 | A graph-based model predicts functional capacity from the plan accurately enough (Spearman ρ ≥ 0.8 on held-out sites) to screen a housing stock. | Exp. C |

## 3. Key definitions

All parameters live in `config/*.yaml`.

- **Household type *h*:** a set of members and a daily schedule over time slots *t ∈ T*, each slot with duration *d_t* in hours (`config/households.yaml`).
- **Activity *a*:** something a household does in a slot. Each furniture-dependent activity needs a set of furniture items in a *deployed* state, plus their clearance zones and access from the entrance (`config/furniture.yaml`). Activities served by fixed rooms (cooking in a kitchen, hygiene in a bathroom) are recorded but excluded from FCI.
- **Strategy *s*:**
  - **S0 static:** only static items; one footprint all day.
  - **S1 multifunctional, unscheduled:** transformable items allowed, but each item keeps one state for the whole day.
  - **S2 schedule-aware (proposed):** transformable items keep a fixed position and orientation but change state per slot.
- **Functional Capacity Index:**

  FCI(u, h, s) = Σ_t Σ_{a∈A_t(h)} w_a · d_t · served(a, t) / Σ_t Σ_{a∈A_t(h)} w_a · d_t

  where served(a, t) = 1 if every required item for *a* is placed, deployed in *t*, clear of collisions, and reachable from the entrance in *t*. The default weight is *w_a* = 1; occasional activities such as hosting guests are weighted by frequency.
- **Area measure *A* (revised at G1):** net internal area (NIA), the internal floor area of the dwelling including kitchen, bathroom and circulation, excluding walls and balconies. This is the unit that minimum-size standards use. Furnishable area is reported as a secondary measure.
- **Static capacity curve:** f₀,h(A) = the expected FCI under S0 as a function of NIA *A*, fitted by isotonic regression (monotone non-decreasing) across the corpus for household *h*.
- **Functionally equivalent area:** FEA(u, h) = min { A* : f₀,h(A*) ≥ FCI(u, h, S2) }. **Area saving** = FEA − A(u). **Relative saving** = (FEA − A(u)) / A(u). If the S2 FCI exceeds the curve's maximum, mark the value as right-censored.
- **Adequacy:** a unit is adequate for *h* under *s* if FCI ≥ τ (default τ = 0.95; sensitivity at 0.90 and 1.00). **Minimum adequate area** A_min,h,s = the area at which a logistic fit of P(adequate | A) crosses 0.5. **ΔA_min** = A_min(S0) − A_min(S2) is the headline policy number.
- **Transformation burden:** TB(u, h) = Σ_items Σ_t e_i · 1[state changes between t−1 and t], cyclic over the day, with effort weights *e_i* from the config. It is reported alongside FCI, and S2 minimizes it as a secondary objective.

## 4. Data

All datasets are open and downloadable without an application.

| ID | Dataset | Use | License |
|---|---|---|---|
| D1 | Swiss Dwellings v3.0.0 (Zenodo 10.5281/zenodo.7788422; ~0.93 GB) | Main real-plan corpus: compact residential units, geometry plus area-level simulations (daylight, noise, view) | CC BY 4.0 |
| D2 | ResPlan (github.com/m-agour/ResPlan; Kaggle mirror) | Second corpus from a different housing market, for robustness | CC BY 4.0 (data), MIT (code) |
| D3 | **Parametric compact shells** (generated in this project) | Covers 8–40 m², the range of Hong Kong subdivided and basic housing units that D1/D2 under-represent: rectangular shells with varied aspect ratio, door and window position, a fixed toilet pod and a kitchenette | Own |
| D4 | Amazon Berkeley Objects, `abo-listings.tar` only (83 MB) | Check furniture dimensions in the library against real products | CC BY 4.0 |
| D5 | American Time Use Survey multi-year microdata (BLS) | *Optional:* calibrate slot durations per household type | Public domain |
| D6 | HK 2021 Population Census, subdivided units by District Council district (data.gov.hk) | Hong Kong scenario weights | Free reuse (DATA.GOV.HK terms) |

**Corpus filter (revised at G1):** residential units with NIA 8–50 m², valid geometry, an entrance door, a window, at least one habitable room, a sanitary space and a kitchen (room or fixture). Repeated identical plans are deduplicated. For Exp. A, a frozen stratified sample is drawn: up to 1,500 D1 plans (stratified by NIA bin and room count, at most 5 per site), all compact D2 plans and all D3 shells.

## 5. Method

### 5.1 Pipeline

```
plans (D1, D2, D3) → normalize & rasterize → candidate placements
households (config) ─┐                                  │
furniture (config) ──┴→ CP-SAT layout per (unit, household, strategy) → independent validator
                                                         │
                       FCI, TB, layouts ─→ f0 curve → FEA, saving, A_min
                                         └→ graph surrogate (Exp. C) → HK scenario
```

### 5.2 Layout optimization (core method)

- **Representation:** each unit is rasterized at grid resolution *r* (default 0.10 m). Cell classes: walkable-and-furnishable (rooms), walkable-only (corridors, door openings, configurable), blocked (walls, fixed features, bathrooms and kitchens unless configured otherwise), and door-swing keep-out.
- **Candidates:** for every item, orientation (0/90/180/270°) and state, precompute the anchor positions where the body and the clearance zone fit inside allowed cells, and where wall-backed items have wall cells directly behind them. Use numpy/scipy convolution or integral images. Tall items may not back onto window segments.
- **Variables:** one Boolean per (item instance, candidate pose). Pose is shared across slots, which is the anchoring constraint. Per-slot state is derived from the schedule: an item is deployed in slot *t* if it serves an activity scheduled in *t*. Under S1, state is a day-wide Boolean.
- **Hard constraints, per slot:**
  - Item bodies do not overlap.
  - No body overlaps another item's active clearance zone; clearance zones may overlap each other.
  - Door-swing keep-outs stay free.
- **Reachability:** the entrance and every deployed item's access zone must be connected through free cells eroded by the walking radius (default 0.30 m, i.e. a 0.60 m path). Enforce it with a lazy loop: solve, check by BFS, add a no-good cut on the offending pose combination, re-solve. Cap at 30 iterations. If the cap is reached, keep the best layout that passes validation and log it.
- **Objective (lexicographic):**
  1. Maximize the weighted served activity-hours (the FCI numerator).
  2. Minimize transformation burden.
  3. Soft preference: desk and dining items closer to windows (distance to the nearest window cell).

  Implement 1–2 as a weighted sum with a large weight on 1, or as two solves.
- **Solver:** OR-Tools CP-SAT, default 60 s per instance, 8 workers, fixed seed. Record status, objective, bound and time.
- **Independent validator:** a separate module, sharing no constraint code with the solver, that re-checks any layout JSON on the raster: geometry inside allowed cells, overlaps, clearances, door swings, reachability and wall backing. Its result is the source of truth for every algorithm in Exp. B.

### 5.3 Baseline algorithms (Exp. B)

1. **Greedy:** items sorted by footprint descending; each takes the first feasible wall-adjacent pose.
2. **Simulated annealing:** same candidates; cost = −FCI + penalties; 20k iterations, 3 restarts.
3. *(Optional, only if time allows)* **Local LLM:** Qwen2.5-7B-Instruct or similar, run locally, given room geometry and the item list as JSON and asked for placements. Run on a stratified subset of 100 instances.
4. **CP-SAT:** the proposed method.

### 5.4 Surrogate (Exp. C)

- **Input:** a plan graph. Nodes are rooms or spaces with features: area, width, depth, aspect ratio, compactness, type one-hot, window count and length, door count. Edges are door or adjacency links. Also global features: net area and the household one-hot.
- **Targets:** FCI under S0 and S2, and area saving.
- **Models:**
  - Linear regression on area only
  - Gradient boosting (LightGBM, or sklearn HistGradientBoosting) on hand-made features
  - MLP on the same features
  - GNN (GraphSAGE or GIN via PyTorch Geometric, or a plain PyTorch implementation if PyG doesn't install)
- **Split:** grouped by `site_id` (D1) or plan ID (D2) to prevent leakage: 70/15/15. D3 shells form a separate test set. Report MAE, RMSE, R², Spearman ρ, and inference time per unit.

### 5.5 Metric validity (Exp. D)

Compare FCI-based adequacy (FCI ≥ τ) with these conventional indicators:

- Floor area per person
- Rooms per person
- Ulrich's 30/45/60 m² thresholds
- Hong Kong's 8 m² basic-housing-unit minimum

Report Spearman correlation, FCI dispersion (interquartile range) within area bins, and confusion matrices or misclassification rates.

### 5.6 Hong Kong scenario (RQ3)

- Use D3 shells at 8–20 m² (step 1 m², several aspect ratios) with the configured one- and two-person households (H1, H3, H4). Larger households are out of scope and stated as a limitation.
- For each strategy, compute the share of shells that are adequate, A_min and ΔA_min.
- Weight results by district counts and household-size distributions from D6, using whatever fields D6 provides; Codex reports the available fields first.
- Report:
  - The share of units below adequacy under S0 compared with S2
  - The district-level "functional floor-area gap" in m²
  - The embodied carbon of floor area avoided, as a parameter range. Every carbon factor must cite a source that the human author has verified; until then it stays `TODO_VERIFY`.

### 5.7 Ablations and sensitivity

- Remove one transformable item type at a time.
- Each household type separately.
- Clearance scale ×0.8 / 1.0 / 1.2.
- Walking width 0.60 m compared with 0.90 m (accessibility).
- Grid resolution 0.05 / 0.10 / 0.20 m, on a subset of 50 units.
- τ ∈ {0.90, 0.95, 1.00}.
- Solver time limit 30 / 60 / 120 s, on a subset.

## 6. Planned figures and tables

| ID | Content |
|---|---|
| F1 | Framework diagram (schematic; the author may redraw) |
| F2 | Corpus: area distribution by source; example plans |
| F3 | Example layouts across slots for S0 / S1 / S2 in three units (small, medium, large) |
| F3b | 3D axonometric renders (Blender) of the same units, S0 vs S2 across night/day/dinner; also the graphical abstract. Optional: a transformation animation as supplementary material |
| F4 | FCI vs area for each strategy, with fitted f₀ curves, faceted by household |
| F5 | Area-saving curve (absolute and relative) with bootstrap 95% CIs |
| F6 | FCI dispersion within area bins (H2) |
| F7 | Algorithm comparison: validity rate, FCI, runtime |
| F8 | Surrogate parity plots and metrics |
| F9 | Ablation and sensitivity tornado plot |
| F10 | Hong Kong scenario: adequacy share and ΔA_min; district bars |
| T1–T7 | Datasets; furniture library; household schedules; Exp. A–D summaries |

## 7. Threats to validity (write these up in the paper)

- No human evaluation of the layouts; transformation burden is modelled, not observed.
- The real plans are Swiss and South Asian, not from Hong Kong; parametric shells stand in for subdivided units.
- FCI measures functional fit, not wellbeing or psychological adequacy (see Ulrich 2025). Present it as a complement to area standards, not a replacement.
- Furniture dimensions and clearances are design defaults; sensitivity analysis bounds their effect.
- The 2D model ignores ceiling height, except for an optional loft-bed extension.

## 8. Paper outline

1. Introduction: the urban housing squeeze, minimum standards, and the role of time.
2. Related work: space standards; computational layout; transformable furniture.
3. Framework and metrics: FCI, FEA, TB.
4. Data.
5. Optimization method and validation.
6. Results: Exp. A–D, ablations.
7. Hong Kong scenario and policy implications.
8. Discussion and limitations.
9. Conclusion.

## 9. Schedule

| Days | Work | Gate |
|---|---|---|
| 1 | Environment; downloads; schema inspection | |
| 2–3 | Corpus building (D1, D2, D3); configs checked against ABO | **G1:** data and corpus review |
| 4–7 | Rasterizer, candidates, CP-SAT, validator; pilot on 20 units | **G2:** method review |
| 8–10 | Full Exp. A, then B, D; ablations | |
| 11–12 | Exp. C surrogate; Hong Kong scenario | **G3:** results review |
| 13–14 | Figures, tables, 3D renders, draft of the methods and results sections | **G4:** final package |
| 15–21 | Author writes and revises; reviewer feedback; submission | |

## 10. References (verify full details before citing)

- Pedro, J.B. (2009). How small can a dwelling be? A revision of Portuguese building regulations. *Structural Survey*, 27(5), 390–410. doi:10.1108/02630800911002648
- Ulrich, K.T. (2025). Minimum Spatial Housing Requirements for Human Flourishing. *Buildings*, 15, 2623.
- Garg, A., Jacobson, A., Grinspun, E. (2016). Computational Design of Reconfigurables. *ACM Transactions on Graphics (SIGGRAPH)*.
- Merrell, P., Schkufza, E., Li, Z., Agrawala, M., Koltun, V. (2011). Interactive furniture layout using interior design guidelines. *ACM TOG (SIGGRAPH)*.
- Yu, L.-F., Yeung, S.-K., Tang, C.-K., Terzopoulos, D., Chan, T.F., Osher, S.J. (2011). Make it home: automatic optimization of furniture arrangement. *ACM TOG (SIGGRAPH)*.
- Sun, F.-Y., et al. (2025). LayoutVLM: Differentiable Optimization of 3D Layout via Vision-Language Models. *CVPR*. arXiv:2412.02193
- HomeWorld (2026). arXiv:2606.06390
- What a Comfortable World: Ergonomic Principles Guided Apartment Layout Generation (2026). arXiv:2604.08411
- Archilyse AG. Swiss Dwellings v3.0.0. Zenodo. doi:10.5281/zenodo.7788422
- ResPlan: A Large-Scale Vector-Graph Dataset of 17,000 Residential Floor Plans (2025). arXiv:2508.14006
- Collins, J., et al. (2022). ABO: Dataset and Benchmarks for Real-World 3D Object Understanding. *CVPR*.
- Hong Kong SAR Government (2025). Basic Housing Units Ordinance; commencement 1 March 2026.
- Xiong, G., Fu, Q., Fu, H., Zhou, B., Luo, G., Deng, Z. Motion Planning for Convertible Indoor Scene Layout Design. *IEEE TVCG* (year and volume to verify).
- Fu, Q., Zhang, F., Li, X., Fu, H. Magic Furniture: Design Paradigm of Multi-function Assembly. *IEEE TVCG* (year and volume to verify).
- Liu, J.-H., Zhang, S.-K., Sun, S., Wang, Z., Zhang, S.-H. (2025). DIFF: A dataset for indoor flexible furniture. *Graphical Models*, 141.
- Zhang, S.-K., Liu, J.-H., Huang, J., Chi, Z., Tam, H., Yang, Y., Zhang, S.-H. (2025). SceneExplorer: An Interactive System for Expanding, Scheduling, and Organizing Transformable Layouts. *IEEE TVCG*, 31(9), 6008–6021. doi:10.1109/TVCG.2024.3488744
- Özer, S., Jacoby, S. (2022). Dwelling size and usability in London: a study of floor plan data using machine learning. *Building Research & Information*.
- Weber, R.E., Mueller, C., Reinhart, C. (2024). A hypergraph model shows the carbon reduction potential of effective space use in housing. *Nature Communications*, 15. doi:10.1038/s41467-024-52506-z
- Goessler, T., Kaluarachchi, Y. (2023). Smart Adaptive Homes and Their Potential to Improve Space Efficiency and Personalisation. *Buildings*, 13(5), 1132. doi:10.3390/buildings13051132
- Daglio, L., Ginelli, E., Vignati, G. (2023). Housing Design: Furniture or Fixtures? Accommodating Change through Technological and Typological Innovation. *Buildings*, 13(7), 1862.
- Xiang, C., et al. (2025). Co-Layout: LLM-driven Co-optimization for Interior Layout. arXiv:2511.12474
- Bu, S., Che Mat, R. (2026). Research on Space Optimization Design Strategies for Compact Bedrooms Based on Smart Built Environment. *Civil Engineering and Architecture*. doi:10.13189/cea.2026.140514 (volume and pages to verify)
- Xiong, G., Cai, S., Luo, G. (2026). MAFC-Driven Dynamic Layout Transformation System for Reconfigurable Furniture. *Computer Animation and Virtual Worlds*. doi:10.1002/cav.70113
- Johanes, M., Kocour, S., Tang, S., De Wolf, C. (2026). Exploring Adaptable Office Fit-Out Layouts Using Configurable Floor Plan Graphs and Large Language Models. *EC³ 2026*.
