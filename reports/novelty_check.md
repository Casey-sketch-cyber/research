# Novelty check (answers Q-01)

**Date:** 2026-11-05 · **Done by:** Claude for the author · **Status:** web-based search complete; confirmation in Scopus or Web of Science recommended (§5)

## 1. Method and limits

Claude had no Scopus or Web of Science access. The search used general and scholarly web search (about 25 queries, English plus one Chinese query), then read the abstracts or full text of the closest hits. It covered five strands:

1. Computational furniture layout, including transformable, convertible and multi-state layouts
2. Quantified space savings from multifunctional or transformable furniture
3. Minimum dwelling-size standards derived from furniture and activities
4. Data-driven dwelling usability and space efficiency at scale
5. Flexible, adaptive and smart homes

A web search can miss paywalled or non-English work. Treat this report as a strong first pass, not a systematic review. §5 gives three database queries that confirm it in about 15 minutes.

## 2. Closest prior work found

| # | Work | What it does | What it does **not** do (relative to this project) |
|---|---|---|---|
| 1 | Xiong, Fu, Fu, Zhou, Luo, Deng. *Motion Planning for Convertible Indoor Scene Layout Design.* IEEE TVCG (2020, per the authors' file; verify) | Plans mechanical motions (rails, shafts) to convert one furniture layout into another, e.g. for multi-purpose rooms | No time-of-day schedule, no functional-capacity or area metric, no corpus of real dwellings. Its metrics are mechanism complexity and conversion time. |
| 2 | Fu, Zhang, Li, Fu. *Magic Furniture: Design Paradigm of Multi-function Assembly.* IEEE TVCG (2023, per the authors' file; verify) | Designs single reconfigurable board assemblies that approximate several furniture pieces | Object-level only; no room layouts; space saving is stated as motivation but not measured |
| 3 | Liu, Zhang, Sun, Wang, Zhang. *DIFF: A dataset for indoor flexible furniture.* Graphical Models 141 (2025) | Dataset of furniture modules that transform between states, plus a method that generates flexible layouts by minimizing a transition cost | Not tied to household activity schedules; no ergonomic clearance or reachability guarantee; no area-equivalence or policy metric |
| 4 | Zhang, Liu, Huang, Chi, Tam, Yang, Zhang. *SceneExplorer: An Interactive System for Expanding, Scheduling, and Organizing Transformable Layouts.* IEEE TVCG 31(9):6008–6021 (2025). doi:10.1109/TVCG.2024.3488744 | From one scene with transformable modules, generates further functional layouts and organizes them in a graph. "Scheduling" means the order of physical moves. | Not daily activity scheduling; no clearances, no real-plan corpus, no quantified capacity or area savings; an interactive design-exploration tool |
| 5 | Garg, Jacobson, Grinspun. *Computational Design of Reconfigurables.* ACM TOG / SIGGRAPH (2016) | Designs reconfigurable objects | Object-level only (already cited) |
| 6 | Özer & Jacoby. *Dwelling size and usability in London: a study of floor plan data using machine learning.* Building Research & Information (2022) | 2,283 London plans extracted by machine learning; usability tested by fitting **static** furniture and activity zones. 27% meet the minimum dwelling size but fail desirable room sizes; size is "an incomplete measure of usability" | No transformable furniture, no time of day, no optimization. **This directly precedes H2.** |
| 7 | Weber, Mueller, Reinhart. *A hypergraph model shows the carbon reduction potential of effective space use in housing.* Nature Communications 15 (2024). doi:10.1038/s41467-024-52506-z | "Excess area" = apartment area minus the furniture-based need (furniture area × 1.6). Space efficiency beats envelope upgrades for 72% / 61% / 33% of buildings in Zurich / New York / Singapore. | Static furniture, no time dimension, no transformable furniture. **The precedent for our carbon framing.** |
| 8 | Goessler & Kaluarachchi. *Smart Adaptive Homes and Their Potential to Improve Space Efficiency and Personalisation.* Buildings 13(5):1132 (2023). doi:10.3390/buildings13051132 | Literature review and case studies; proposes that adaptive homes could raise space efficiency "up to two to three times" | **The claim isn't quantified.** Our study can test it. |
| 9 | Ulrich. *Minimum Spatial Housing Requirements for Human Flourishing.* Buildings 15:2623 (2025) | Minimum areas of 30/45/60 m²; mentions multifunctional furniture and temporal zoning | Doesn't credit either in the minimums (already cited) |
| 10 | Pedro. *How small can a dwelling be?* Structural Survey 27(5) (2009) | Minimum areas derived from furniture and functional spaces | Static, manual, no time dimension (already cited) |
| 11 | Daglio, Ginelli, Vignati. *Housing Design: Furniture or Fixtures?* Buildings 13(7):1862 (2023) | Case-study review of integrated fit-out and furniture systems in housing | Qualitative; no measured savings |
| 12 | Co-Layout (Xiang et al., arXiv:2511.12474, 2025); Architect-Ant (Rodionov et al., arXiv:2606.10953, 2026); RenoLayout (Liu et al., arXiv:2610.21366, 2026) | Recent constraint- or LLM-based furniture layout; Co-Layout uses integer programming on a grid | Static furniture only; no schedules or multi-state items |
| 13 | Johanes, Kocour, Tang, De Wolf. *Exploring Adaptable Office Fit-Out Layouts Using Configurable Floor Plan Graphs and LLMs.* EC³ 2026 | Multi-scenario office layouts; compares CP-SAT with LLMs (CP-SAT best on hypervolume) | Offices and partitions, not dwellings or furniture. **A useful precedent for Exp. B** (CP-SAT vs LLM). |
| 14 | Ma et al. *Action-driven 3D Indoor Scene Evolution.* ACM TOG / SIGGRAPH Asia (2016) | Scenes evolve over time through human actions (object placement and clutter) | Synthesis for graphics; no functional adequacy or area measure |

The phrase "functionally equivalent area" was not found in this sense.

## 3. Verdict on each claimed contribution

| Claim (RESEARCH_PLAN) | Verdict | How to word it in the paper |
|---|---|---|
| "Computational layout produces one static arrangement" (§1) | **Not true. Corrected.** Works 1–4 generate or plan transformable layouts. | "Recent graphics work generates and sequences transformable layouts for design exploration [1–4], but does not tie furniture states to a household's daily activity demand, guarantee ergonomic clearance and reachability, or measure what the transformation is worth in floor area." |
| Schedule-aware multi-state layout optimization, with positions shared across slots and states driven by time-of-day activity demand | **Appears novel.** No match found. | State it as the method contribution; cite 1–4 as the closest work. |
| Functional Capacity Index over a 24-hour schedule, and **functionally equivalent area** (transformable gain expressed in m²) | **Appears novel.** Goessler & Kaluarachchi (2023) and Ulrich (2025) raise the idea without quantifying it. | "To our knowledge, the first quantification of how much floor area transformable furniture is worth"; cite 8 and 9 as the unquantified claims being tested. |
| H2: size is a poor proxy for functional adequacy | **Not novel on its own.** Özer & Jacoby (2022) showed it with static furniture. | Present it as **confirmation and extension**: the gap persists when function is measured over time, and it changes when transformable furniture is allowed. |
| City-scale screening of real plan corpora | **Not novel on its own** (Weber et al. 2024; Özer & Jacoby 2022 work at scale with static furniture) | A supporting contribution, not a headline one |
| Carbon framing (avoided floor area) | **Follows Weber et al. (2024)** | Cite as the basis; our addition is that transformable furniture lowers the *needed* area, which complements their "excess area" |
| Policy test against an area-only minimum (HK 8 m²) | **Appears novel** in combination with the above | Keep as the urban contribution |

**Overall:** the project is novel in the **combination** of time-of-day activity demand, transformable states with guaranteed clearance, a large real-plan corpus, and translation into floor-area and policy terms. It is not novel in "transformable layouts" alone, nor in "size ≠ usability" alone. The paper must cite works 1–4, 6, 7 and 8 explicitly.

## 4. Changes made to the plan

- RESEARCH_PLAN §1: the "computational layout" bullet and the gap statement are corrected; new related work is added.
- RESEARCH_PLAN §2: H2 is reframed as confirmation and extension of Özer & Jacoby (2022).
- RESEARCH_PLAN §10: the verified references above are added. Years marked "verify" must be checked against the publisher's page before submission.

## 5. Confirmation in Scopus or Web of Science (author, about 15 minutes)

Run these and skim titles from 2015 onward. Add anything that matches the "appears novel" rows to §2.

**Scopus**
```
TITLE-ABS-KEY((transformable OR convertible OR multifunctional OR flexible OR reconfigurable) W/3 furniture AND (layout OR arrangement) AND (optimi* OR generat* OR plan*))
TITLE-ABS-KEY((dwelling OR housing OR apartment) AND furniture AND ("time use" OR "daily schedule" OR "activity schedule" OR "time of day" OR temporal) AND ("floor area" OR "space standard*" OR "minimum size"))
TITLE-ABS-KEY(("multifunctional furniture" OR "transformable furniture" OR "wall bed" OR "murphy bed" OR "convertible furniture") AND ("floor area" OR "space saving" OR "space efficiency") AND (quantif* OR simulat* OR model* OR optimi*))
```

**Web of Science:** the same queries with `TS=(...)`, and `NEAR/3` instead of `W/3`.

**CNKI** (Chinese literature, optional): 可变家具 AND 小户型 AND (优化 OR 量化 OR 布局)
