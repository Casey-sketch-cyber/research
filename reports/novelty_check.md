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

> **Update:** the project has no Scopus or Web of Science access. Codex runs this confirmation instead, with free databases (OpenAlex, Semantic Scholar, Crossref, arXiv), as **task L** (`docs/LITERATURE_SEARCH.md`). The queries below are kept for reference if database access becomes available.

Run these and skim titles from 2015 onward. Add anything that matches the "appears novel" rows to §2.

**Scopus**
```
TITLE-ABS-KEY((transformable OR convertible OR multifunctional OR flexible OR reconfigurable) W/3 furniture AND (layout OR arrangement) AND (optimi* OR generat* OR plan*))
TITLE-ABS-KEY((dwelling OR housing OR apartment) AND furniture AND ("time use" OR "daily schedule" OR "activity schedule" OR "time of day" OR temporal) AND ("floor area" OR "space standard*" OR "minimum size"))
TITLE-ABS-KEY(("multifunctional furniture" OR "transformable furniture" OR "wall bed" OR "murphy bed" OR "convertible furniture") AND ("floor area" OR "space saving" OR "space efficiency") AND (quantif* OR simulat* OR model* OR optimi*))
```

**Web of Science:** the same queries with `TS=(...)`, and `NEAR/3` instead of `W/3`.

**CNKI** (Chinese literature, optional): 可变家具 AND 小户型 AND (优化 OR 量化 OR 布局)

## Systematic confirmation (task L)

**Status: STOP_REQUIRED_PARTIAL_SCREENING.**
The configured retrieval was run; screening stopped early after a full-text-confirmed C3 overlap triggered §5 of docs/LITERATURE_SEARCH.md. This is an interim evidence report, not a completed systematic review or an exhaustive novelty clearance.

### Retrieval and screening flow

| Step | Count |
|---|---:|
| Retrieved query records: arxiv (before deduplication) | 41 |
| Retrieved query records: crossref (before deduplication) | 3000 |
| Retrieved query records: openalex (before deduplication) | 406 |
| Retrieved query records: semantic_scholar (before deduplication) | 4 |
| After DOI / normalized-title-and-year deduplication | 2928 |
| Title decisions completed | 20 |
| Titles retained among those reviewed | 20 |
| Titles excluded among those reviewed | 0 |
| Titles still pending | 2908 |
| API abstracts actually read | 20 |
| Abstract-stage A_overlap | 1 |
| Abstract-stage B_related | 15 |
| Abstract-stage KNOWN | 0 |
| Abstract-stage C_irrelevant | 4 |
| Abstract-stage PENDING | 2908 |
| Abstract-stage NOT_APPLICABLE | 0 |
| Full texts checked | 1 |
| All retrieved records without an API abstract | 1859 |

Counts are produced from screening_decisions.json; pending records are not counted as irrelevant. The initial order prioritized titles/abstracts about transformable furniture, daily activity and quantified area. No automated keyword rule assigned a negative screening decision.

### Every reviewed A/B record

| Citation (API metadata) | DOI / source | Rating | Claim | Judgement |
|---|---|---|---|---|
| Hope Nolan (2026). A Review and Redesign of Multi-Functional Furniture. Iowa State University Digital Repository (Iowa State University) | [source](https://dr.lib.iastate.edu/handle/20.500.12876/107144) | B_related | C3 | The API abstract describes a folding lounge-chair prototype for dorm rooms, but gives no quantified room-area savings. |
| Taiwo O. Asonja (2022). Design of a Transformable Furniture: A Necessary Innovation for a Growing Population with a Fixed Land Mass. Journal of Material Sciences & Manfacturing Research | [10.47363/jmsmr/2022(3)127](https://doi.org/10.47363/jmsmr/2022(3)127) | B_related | C3 | The API abstract describes a multifunctional bed/table/cabinet design and prototype tests, but supplies no quantified floor-area saving or equivalent-area metric. |
| Nurfazlina Haris; Sheela Faizura Nik Fauzi; Aiza Johari (2023). Phronesis Table : transformable space saving furniture. UiTM Institutional Repositories (Universiti Teknologi MARA) | [source](https://ir.uitm.edu.my/id/eprint/130255/1/130255.pdf) | B_related | C3 | The API abstract describes an extendable table with storage and technology features, but does not quantify floor-area savings against a baseline. |
|  (2025). Mechanisms of Spatial Efficiency: How Multifunctional Furniture Drives Space-Saving in Shijiazhuang’s Urban Compact Homes. International Journal of Business and Technology Management | [10.55057/ijbtm.2025.7.6.13](https://doi.org/10.55057/ijbtm.2025.7.6.13) | B_related | C2;C3 | The API abstract identifies temporal adaptability through qualitative interviews, but does not describe schedule-driven layout optimization or quantified area gains. |
| Iman Khajehzadeh (2017). An investigation of the effects of large houses on occupant behaviour and resource-use in New Zealand.  | [10.26686/wgtn.17058221](https://doi.org/10.26686/wgtn.17058221) | B_related | C2;H2 | The API abstract links observed household time use, room provision and lifecycle resource demand, but does not optimize transformable furniture states or calculate their area equivalence. |
| Wang, Shiyao (2013). An analysis of transformable space saving furniture. cIRcle (University of British Columbia) | [10.14288/1.0103142](https://doi.org/10.14288/1.0103142) | B_related | C3 | The API abstract reviews transformable furniture designs, mechanisms and markets, but does not report an equivalent-area computation. |
| Guoming Xiong; Sisi Cai; Guoliang Luo (2026). MAFC ‐Driven Dynamic Layout Transformation System for Reconfigurable Furniture. Computer Animation and Virtual Worlds | [10.1002/cav.70113](https://doi.org/10.1002/cav.70113) | B_related | C2 | The API abstract describes coordinated collision-free furniture movement and navigation, but does not mention household time-of-day demand optimization with shared positions. |
| O. O AWOPETU; J. M OWOYEMI; T. P. BABATUNDE (2024). DEVELOPMENT OF A TRANSFORMABLE FURNITURE SYSTEM: FROM SHELVING UNIT TO FUNCTIONAL TABLETOP. FUTA JOURNAL OF ENGINEERING AND ENGINEERING TECHNOLOGY | [10.51459/futajeet.2024.18.1.522](https://doi.org/10.51459/futajeet.2024.18.1.522) | B_related | C3 | The API abstract measures available hostel space to size a shelf-to-table prototype, but does not report the floor-area gain against a conventional layout. |
|  (2025). Shaping Limited Residential Spaces with Multifunctional Furniture Design Language: Solutions and Ideas تشكيل الفضاءات السكنية المحدودة المساحة باستخدام لغة تصميم الأثاث المتعدد الوظائف، حلول وأفكار. Jordan Journal of the Arts | [10.47016/18.1.8](https://doi.org/10.47016/18.1.8) | B_related | C3 | The English API abstract analyzes six limited-space residential cases and flexible furniture ideas, but reports no numerical area-saving measure. |
| Architecture Department- College of Engineering - University of Sulaimani; Hazha Mahmood Tahir; Amjad Muhammad Ali Qaradaghi (2020). The Influence of Using Minimalist Furniture on the Efficiency of the Living Space - Residential Apartments in Sulaimani City as Case Study. Diyala Journal of Engineering Sciences | [10.24237/djes.2020.13210](https://doi.org/10.24237/djes.2020.13210) | B_related | C3;H2 | The API abstract uses a checklist to assess minimalist furniture and living-room efficiency, but does not state a transformable-furniture area-saving value or schedule model. |
| Mahimma Romadhona; Ahadiat Joedawinata (2023). The impact of apartment furniture design on children’s development and recommendations for multifunctional furniture. Dewa Ruci: Jurnal Pengkajian dan Penciptaan Seni | [10.33153/dewaruci.v18i1.5189](https://doi.org/10.33153/dewaruci.v18i1.5189) | B_related | H2 | The API abstract relates cramped apartment furniture to child development and design requirements, but does not test an area-only standard or quantified transformable-area gain. |
| Shuai Chen (2024). The Implication Of Transformable Space Saving Furniture On The Interior Design In Small Living Units.  | [10.26686/wgtn.25807507](https://doi.org/10.26686/wgtn.25807507) | B_related | C2;C3 | The API abstract reviews and designs small-apartment live/work transformations, but does not describe a schedule optimization algorithm or numerical area equivalence. |
| Saleh Hamed; Vladica Ristic (2025). MULTIFUNCTIONAL FURNITURE AND ITS IMPACT IN RESIDENTIAL BUILDINGS WITH LIMITED SPACE. IRASA International Scientific Conference SCIENCE, EDUCATION, TECHNOLOGY AND INNOVATION SETI VII 2025 | [10.62982/seti07.saha.54](https://doi.org/10.62982/seti07.saha.54) | B_related | C3 | The API abstract discusses multifunctional furniture for restricted residential space, but provides no numerical area-saving comparison. |
| Aditya Venkatesh; Niraj Karki; Fengfeng Xi (2024). Bio-Kinematic Modelling for Reconfigurable Furniture Design and Analysis. TSpace (University of Toronto) | [source](https://hdl.handle.net/1807/154150) | B_related | C3 | The API abstract develops kinematic and posture analysis for a reconfigurable prototype, but reports no dwelling-level area-equivalence calculation. |
| Shuai Bu; Ruzinoor Che Mat (2026). Research on Space Optimization Design Strategies for Compact Bedrooms Based on Smart Built Environment. Civil Engineering and Architecture | [10.13189/cea.2026.140514](https://doi.org/10.13189/cea.2026.140514) | A_overlap | C3 | Full-text §§3, 5–7, Fig. 10 and Table 2 quantify approximate activity-area gains from a wall bed, folding desk and storage modules; this overlaps broad C3, while a validated schedule-constrained optimizer and whole-dwelling FEA inversion are not demonstrated. |
| Aisha Saied; Rawaz Abdullah; جنان علي (2024). Impact of Flexible Furniture on Small Spaces in Residential Apartment with Smart Solutions. Nanotechnology Perceptions | [10.62441/nano-ntp.v20is3.61](https://doi.org/10.62441/nano-ntp.v20is3.61) | B_related | C3;H2 | The API abstract relates small-apartment furniture and well-being and mentions occupied floor space, but gives no comparative transformable-area gain. |

### Updated contribution assessment

| Claim | Verdict | Scope of judgement |
|---|---|---|
| C2 | weakened | The narrow shared-position schedule-constrained optimizer remains a candidate distinction, but Bu & Che Mat already connect daily needs, folding furniture and spatial states; screening is incomplete, so novelty is not cleared. |
| C3 | not novel | Broad quantification of transformable-furniture floor-area gains is preceded by the full-text-confirmed Bu & Che Mat study; whole-dwelling FEA inversion may be narrower, but requires reframing and review. |
| C4 | weakened | The reviewed subset does not establish a direct minimum-standard overlap; incomplete screening cannot confirm novelty, and the combined claim must be reconsidered with C3. |
| H2 | not novel | Retain the already acknowledged Ozer & Jacoby precedent from the earlier report; this interim subset does not independently revalidate that known reference. |

### Full-text overlap evidence

Bu and Che Mat (2026), DOI 10.13189/cea.2026.140514, compare three conceptual layouts within a 12 m² bedroom. PDF pp. 12–14 (§6.1–6.3, Fig. 10, Table 2) report approximately 5–5.5 m² of activity area for fixed furniture and approximately 8 m² when a wall bed is folded, described by the authors as roughly 60% improvement. The authors explicitly describe an analytical comparison, not measured performance in occupied dwellings (§3.3, §6.1, §7). Their time-based zoning is relevant to C2, but no shared-position schedule-constrained optimization algorithm, independent reachability validator or whole-dwelling FEA inversion is demonstrated in the checked methods/results. This is sufficient overlap with the broad C3 wording to activate the protocol stop; it does not establish that the entire proposed project has been done. These are the paper’s reported values, not results of our experiments. The full-text download URL, checksum, checked sections and evidence classification are recorded in fulltext_checks.json.

### Proposed citation additions

For reviewer consideration: add Bu & Che Mat as a C3 antecedent; MAFC-Driven Dynamic Layout Transformation System (10.1002/cav.70113) as a motion-coordination distinction for C2; and Mechanisms of Spatial Efficiency (10.55057/ijbtm.2025.7.6.13) as qualitative evidence on temporal adaptability. RESEARCH_PLAN has not been edited. Proposed narrower framing: quantify household-specific, time-weighted whole-dwelling functional equivalence on real plans with independently validated clearance and reachability, rather than claim the first numerical area benefit of transformable furniture. The reviewer must decide whether this distinction is sufficient.

### Limits and reproducibility

Screening was deliberately interrupted when the explicit C3 stop rule was met; the pending majority has not been screened, and neither citation saturation nor absence of other overlaps can be claimed. OpenAlex and Semantic Scholar returned HTTP 429 responses. OpenAlex cursor continuation required a key (HTTP 401); a retry used documented public basic paging with 100 records per page, but repeated rate limiting left Q1 incomplete. Completed earlier responses were retained even when a later retry failed. All six Crossref keyword queries reached the configured 500-record cap and are relevance-ranked, not exhaustive Boolean searches. Semantic Scholar zero totals are retained as returned and do not demonstrate absence of literature. Crossref metadata was merged only where DOI or normalized title/year matched; unresolved field completion remains pending. OpenAlex applied language:en; other providers expose inconsistent language metadata, so the English-language restriction is not fully verified and non-English records remain unscreened. arXiv used HTTPS for the configured endpoint. The optional Chinese search was not run. One reviewer (Codex) made the explicit judgements. Full-text TLS validation succeeded using the operating system trust store after the Python client could not validate the publisher chain; no certificate checks were disabled.

Query-level totals, dates, URLs and retry outcomes are in results/literature/retrieval_queries.csv and request_manifest.json. Raw responses and the paper remain in ignored data/interim/lit_cache/; abstracts and full texts are not republished.

Reproduce retrieval: `python scripts/00b_lit_search.py`. Reproduce this interim report from the saved cache: `python scripts/00b_lit_search.py --cached-only --screening-decisions results/literature/screening_decisions.json`. Resume by extending explicit screening decisions after reviewer guidance. Do not interpret a successful script exit as permission to cross the research gate.

Config hash: `a5d6bc0e20a07cce43e51c76759eec561b2b56b8c863af5a52435b1aca1ae0f4`. Screening decision hash: `ad23e9d95e4c7344b992bf0bb367e3ff53700c39e842f6a9e4e14a0835c384ef`.
