# Paper story and outline (iScience)

**Status:** v1, 2026-11-16, Claude. This is the brief for whoever drafts the manuscript (Gemini, Codex or a person).

Read [`docs/WRITING_GUIDE.md`](WRITING_GUIDE.md) for *how* to write. This file says *what* to write.

**Evidence rule:** every number in the paper must come from a committed result file. The files are listed in §8. If a needed number has no file, write `[NEEDS EVIDENCE: …]` and do not compute it yourself.

---

## 1. The story in five sentences

1. Cities are letting homes get smaller and regulate them by floor area alone. Transformable furniture is promoted as the way to make small homes work.
2. Nobody can say how much usable space such furniture actually adds across real homes and households. The reason: area rules ignore furniture, functional standards use fixed hand-drawn layouts, design studies examine single rooms, and layout generators do not check that a layout is physically usable or matches how a household spends its day.
3. We compare each home with itself under three furniture strategies:
   - static;
   - transformable;
   - transformable and switched between times of day.

   Each strategy gets its best arrangement found by optimisation, and every arrangement passes an independent geometric check. The difference is expressed as the floor area a static home would need to work equally well.
4. Across 2,619 compact plans and four household types, most plans already work with static furniture. The gains are concentrated in two-person households in mid-sized homes, and floor-area cutoffs misclassify about half of two-person homes.
5. Floor area is therefore a weak proxy for whether a compact home works. A schedule-aware, verifiable measure can show regulators and designers where furniture can substitute for space, and where it cannot.

**New understanding (the paper's core message):** the space-saving value of transformable furniture is real but *conditional*. It depends on who lives in the home and how large it is. Area-only rules cannot see this.

## 2. Key content map

| Key content | This paper |
|---|---|
| Task / question | How much usable floor area do transformable furniture and time-based switching add in compact homes? Does floor area alone tell us whether a household can live there? |
| Target quantity | Functional adequacy of a home for a household, expressed in m², the unit regulators use |
| Surface failure of current approaches | (a) Minimum standards are set by area only, e.g. Hong Kong's 8 m² basic housing units and 30/45 m² proposals. (b) Functional space standards derive area from static furniture lists and fixed layouts. (c) Transformable-furniture studies report large gains from single rooms, such as ~60% more activity area in one 12 m² bedroom. (d) Computational layout generators produce plausible layouts but rarely check reachability or daily schedules. |
| Root cause | No method jointly represents (i) who uses the home and when, (ii) which furniture can change state, and (iii) whether each arrangement is physically feasible and reachable, at corpus scale and in m². Hand-drawn or single-case comparisons also mix furniture capability with designer skill. |
| Our solution | A functional capacity index (FCI) over a household's daily schedule; three furniture strategies (S0 static, S1 form only, S2 form + time); best arrangements by constraint optimisation; an independent validator; and conversion of paired differences into an equivalent-area gain and an adequate area A_min. |
| Why it works | Optimisation gives each strategy its best arrangement, so differences reflect furniture capability, not drawing skill. The independent validator makes every layout checkable. The paired within-home design isolates the furniture effect. The m² translation speaks the regulator's language. The S1/S2 split separates *changing form* from *changing over time*. |
| Extra contributions | Area-cutoff misclassification; Hong Kong scenario; size-band-dependent furniture dimensions; solver benchmark; an honest negative result for a learned surrogate. |
| Evidence | §8 |

## 3. Title, Summary, Highlights, eTOC

**Title options.** Cell Press style favours a declarative finding.

1. *Transformable furniture saves floor area mainly for two-person households in mid-sized compact homes*
2. *Floor area alone misjudges how well compact homes work*
3. *How much floor area can transformable furniture save? Evidence from 2,619 compact homes*

Pick one after the Results are drafted. Keywords: compact housing, minimum space standards, transformable furniture, functional capacity, layout optimisation, equivalent area.

**Summary.** About 150 words, one paragraph, written last. Structure, following WRITING_GUIDE §4, template V2:

1. Context: shrinking homes are regulated by area, and transformable furniture is promoted.
2. Gap: no corpus-scale, verifiable estimate of the area such furniture saves for real households.
3. Insight: compare each home with itself under static, transformable and time-switched furniture, each optimally arranged and independently checked, and translate differences into m².
4. Data: 2,619 compact plans, four household types.
5. Findings:
   - most plans already function with static furniture;
   - gains concentrate in two-person households (median identified gain 6.21 m² for couples, 5.00 m² for parent–child);
   - 45 m² cutoffs disagree with modelled adequacy for 53–56% of two-person cases;
   - in Hong Kong model shells, switching is worth 2.24 m² for couples.
6. Implication: performance-based supplements to area rules.

**Highlights** (≤85 characters each; already checked):

- Verified layouts for 2,619 compact plans and four household types
- Transformable furniture helps a minority of plans, mostly two-person households
- Floor-area cutoffs misclassify about half of two-person homes in our model
- Switching furniture states is worth about 2.2 m2 for couples in Hong Kong shells

**eTOC blurb** (~50 words). Draft after the Summary.

## 4. Section outline

### Introduction (4–5 paragraphs, ~800 words)

Use opening V3 (general importance, then the specific setting) and the challenge pattern from WRITING_GUIDE §3.

- **P1. Context and stakes.**
  - Urban housing pressure is producing smaller homes.
  - Regulators respond with area minimums: Hong Kong's Basic Housing Units Ordinance sets 8 m², and Ulrich (2025) proposes 30/45/60 m² by household size.
  - Effective use of existing space also matters for resource and carbon outcomes (Weber et al. 2024).
  - Transformable furniture is widely promoted as a way to make small homes work.
- **P2. How the question is answered today, and why that is not enough.**
  - Area rules count m², not whether activities fit.
  - Functional standards (Pedro 2009; Ulrich 2025) derive area from static furniture and fixed layouts. They are neither time-aware nor transformation-aware.
  - Design studies of transformable furniture (Bu & Che Mat 2026; Zeng et al. 2026, see `reports/novelty_check.md`; Daglio et al. 2023) examine single rooms or products with designer-chosen arrangements.
  - Computational layout methods (Merrell et al. 2011; Yu et al. 2011; DIFF; SceneExplorer; Xiong et al. 2026) generate or schedule layouts. They are not used to estimate how much area transformability saves across housing stocks, and they do not guarantee walkable access.
  - End with the root cause (§2) in one or two sentences.
- **P3. Our approach.**
  - "In this paper, we quantify …"
  - Key idea in one sentence: compare each home with itself under three furniture strategies, each optimally arranged and independently verified, and express the difference as floor area.
  - Then the specifics (FCI, S0/S1/S2, validator, equivalent area, A_min) and why this design isolates furniture capability.
  - Refer to Figure 1.
- **P4. What we find.** The new understanding, with 3–4 headline numbers. Use no more numbers than the Summary.
- **P5. Contributions** (prose or three short items):
  1. a schedule-aware, verifiable measure of functional capacity that is translatable to m²;
  2. corpus-scale evidence of where transformable furniture saves area and where it does not;
  3. a test of area-only minimum standards, with a Hong Kong scenario and design implications for furniture dimensions.

Avoid: "first", "novel", and naive-baseline-then-patch storytelling.

### Results (each subsection heading is a claim)

1. **A verified, schedule-aware comparison of furniture strategies** (Figure 1, Figure 2)
   - Data and household types (T1, T3); strategies and an example home across time slots (F3, F3b_18).
   - The solver is trustworthy: the production pipeline matched the best-known value in 189/200 benchmark pairs (T5); the details go in STAR Methods and Figure S-B.
2. **Most compact plans already function with static furniture** (F4)
   - Share of plans fully functional under S0, by household: `[NEEDS EVIDENCE: committed table of the share with FCI = 1 and FCI ≥ 0.95 by household × strategy on observed plans. Codex task, see §9]`.
   - The all-pair median ΔEA is 0 for every household (T4).
3. **Gains concentrate in two-person households at intermediate sizes** (F4, F5, T4)
   - Shares improved: 7.5 / 8.7 / 23.5 / 35.9%.
   - Identified ΔEA medians: remote worker 1.33 m², couple 6.21 m², parent–child 5.00 m², with CIs.
   - Commuter: lower bound only (≥ 2.00 m²).
   - D3 bins: couple peak 7.32 m² at 14–16 m²; parent–child rises from 0.69 to 6.00 m².
   - Smallest homes gain little because even transformable pieces do not fit. This is the nonmonotonic pattern (H1 partly supported).
4. **Changing form and changing over time help different households** (F4, T4)
   - Couple: form 0.0130 and time 0.0112 FCI, about equal.
   - Parent–child: form 0.0271, time small.
   - Robust to mirrored one-side bed access: the time effect changes by −0.0122 FCI.
5. **Floor area alone misjudges functional adequacy** (F6, T7)
   - The 45 m² cutoff disagrees with S2 adequacy on 55.7% of couple and 52.7% of parent–child cases, mostly by rejecting homes that work.
   - Within-bin dispersion is large.
   - The 8 m² rule is only informative for D3/HK shells (no observed plan is below 16.75 m²).
6. **What this means for Hong Kong's smallest homes** (F10, F12)
   - A_min by household and strategy: commuter 13.40 → 12.37 m²; parent–child 19.58 → 17.07 m².
   - Couple switching: 2.24 [1.66, 2.82] m².
   - A larger couple kit is adequate on 51 vs 30 of 120 shells at 13–16 m² but loses capacity below 13 m². Furniture dimensions should be chosen per size band.
   - No tested kit beats standard dimensions for the commuter.

### Discussion (~900 words)

- **D1. Restate the new understanding:** conditional value; floor area as a weak proxy.
- **D2. Relation to prior claims.**
  - Single-room gains (~60%) rest on clearance-inclusive activity area in a fixed arrangement. Under scheduled demand and whole-home accounting, the median daytime body-free area change is 0 m² (R analysis; supplement F11). Present this as a difference in measure and scope, not as a refutation.
  - Functional standards are extended here with time and transformation.
- **D3. Implications.**
  - *Regulators:* performance-based checks can supplement area minimums, for example a verified-layout test for a target household.
  - *Designers and manufacturers:* target two-person homes of roughly 12–30 m²; size kits by band.
  - *Researchers:* the framework transfers to other cities and households.
- **D4. Limitations of the study.** Two or three items, written as scope boundaries per WRITING_GUIDE §7:
  1. FCI measures whether activities fit and are reachable, not comfort, privacy or preference. Define this scope in Methods; here, one sentence plus future work linking FCI to occupant evaluation.
  2. Households and furniture are representative configurations. The framework accepts other schedules and catalogues.
  3. Hong Kong results are a scenario on model shells, not stock totals.

  Do not list implementation defects.

### STAR Methods

Adapt `manuscript/draft_methods.md`. Required sub-blocks:

- Key resources table: datasets, software, code repository.
- Resource availability:
  - lead contact: `[AUTHOR TO FILL]`;
  - materials: none;
  - data and code: the GitHub repository plus a Zenodo DOI `[TO MINT]`, and dataset sources.
- Method details:
  - corpus and evaluability;
  - households;
  - furniture library;
  - strategies;
  - optimisation (CP-SAT, greedy portfolio warm start, lazy reachability);
  - independent validator;
  - FCI;
  - equivalent area (median-bin cumulative-max reference curve, support bounds);
  - A_min (logistic, τ = 0.95);
  - Hong Kong scenario;
  - kit design.
- Quantification and statistical analysis: unit bootstrap CIs, paired contrasts, support labelling.

### Supplemental information

Supplementary figures and tables:

- B solver benchmark (F7, T5);
- C surrogate as a negative result (F8, T6; adequacy AUC labelled post hoc);
- ablations (F9);
- room comparison R (F11);
- furniture table (T2);
- example layouts (F2);
- 3D stills (F3b_10, F3b_30).

## 5. Figures

| Main figure | Content | Source |
|---|---|---|
| 1 | Framework (new, PowerPoint) | `docs/FIGURE1_SPEC.md` |
| 2 | One home across slots and strategies, 2D plus 3D | F3 + F3b_18 |
| 3 | Capacity and strategy effects by household and area | F4 |
| 4 | Equivalent-area gains | F5 |
| 5 | Area cutoffs versus modelled adequacy | F6 (+ T7) |
| 6 | Hong Kong scenario and kit size bands | F10 + F12 |

The graphical abstract is specified in `docs/FIGURE1_SPEC.md` §B.

## 6. Terminology (use exactly these words)

| Term | Use | Never |
|---|---|---|
| functional capacity index (FCI) | share of scheduled activity-hours a layout serves | "efficiency score" |
| static (S0) / form only (S1) / form + time (S2) | the three strategies | "baseline / ours" |
| form effect (S1 − S0), time effect or switching effect (S2 − S1) | the decomposition | |
| equivalent-area gain (ΔEA) | m² a static home would need to match S2 | "area saved" without definition |
| adequate area (A_min) | area where modelled adequacy crosses τ = 0.95 | |
| net internal area (NIA) | the area axis; compact = 8–50 m² NIA | "floor area" without definition in Methods |
| observed plans (Swiss Dwellings, ResPlan), generated shells, Hong Kong model shells | data sources | "real data" |
| single commuter, single remote worker, couple, parent and child | households | H1–H4 in main text |
| transformable furniture | wall bed, fold-down desk, drop-leaf table | "convertible", "smart" |

## 7. Claims to avoid or bound

- No "first", "novel" or "unprecedented".
- No territory-wide Hong Kong totals.
- Do not say FCI measures comfort or liveability.
- The commuter ΔEA is a lower bound only.
- The C surrogate is not a contribution; report it only as a negative result in the supplement.
- The room comparison is approximate, not a replication.
- Kit results: the commuter has "no improvement"; the couple result is "a size-band trade-off", and its mean-FCIq interval includes zero.

## 8. Evidence map (claim → file)

| Claim | Evidence |
|---|---|
| Shares improved; mean form and time effects | `results/tables/g4/T4.md`, `results/expA_f1/analysis/primary_effects.csv` |
| Identified ΔEA medians and lower bounds | `results/g3/area_summary.csv`, `reports/phase_07_P1_results.md` |
| D3 bin peaks | `results/g3/area_summary.csv` (pooling D3, median_bin_cummax, area_bin) |
| A_min and ΔA_min | `results/expA_f1/analysis/min_adequate_area.csv` |
| Area-cutoff disagreement | `results/expD/confusion.csv`, `results/tables/g4/T7.md` |
| Solver benchmark | `results/tables/g4/T5.md`, `results/g3_review/benchmark/production_paired_effects.csv` |
| Mirrored-access sensitivity | `results/expA_f3/effect_summary.csv` |
| HK switching and A_min | `results/g3_review/hong_kong/couple_switching.csv`, `results/g3_review_k3/hk_scenario_summary.csv` |
| HK kit size bands | `results/g3_review_k3/hk_h3_size_bands.csv` |
| Kit paired effects | `results/g3_review_k3/paired_effects.csv` |
| Room comparison | `results/expR/reproduction.csv`, `results/expR/generalization_summary.csv` |
| Surrogate | `results/expC/metrics.csv`, `results/tables/g4/T6.md` |
| Data coverage | `results/tables/g4/T1.md` |
| Overall summary | `reports/FINAL_SUMMARY.md`, `manuscript/draft_results.md` |

**References:** use only `docs/RESEARCH_PLAN.md` §10 and the screened records in `reports/novelty_check.md`. For anything else, write `[CITE: what is needed]`. Never invent a reference or a DOI.

## 9. Open evidence tasks (Codex)

1. Add a committed table: share of observed plans with FCI = 1 and FCI ≥ 0.95, by household × strategy, with unit-bootstrap CIs. It supports Results §2 and the Summary.
