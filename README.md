# Functionally Equivalent Area

**How much floor area does transformable furniture save in compact dwellings, and what does that mean for minimum dwelling standards?**

Research project for a submission to *Urban Science* (MDPI), Special Issue "Urban Transformation and Sustainable Cities".

## Where to start

| Document | For whom | What it is |
|---|---|---|
| [`docs/RESEARCH_PLAN.md`](docs/RESEARCH_PLAN.md) | Everyone | Research questions, hypotheses, metric definitions, data, method, experiments, schedule |
| [`docs/PROCEDURES.md`](docs/PROCEDURES.md) | Codex / engineer | Step-by-step operating procedures per phase, with acceptance checks |
| [`docs/DELIVERABLES.md`](docs/DELIVERABLES.md) | Codex and reviewer | What to push, file schemas, review gates G1–G4 |
| [`AGENTS.md`](AGENTS.md) | Codex | Working rules, integrity rules, conventions (Codex reads this automatically) |
| [`config/`](config/) | Codex | All parameters: project, furniture library, household schedules |
| [`data/README.md`](data/README.md) | Codex / author | Dataset sources and download paths (all open, no application needed) |

## Workflow

The current review gate is G3. The [results report](reports/GATE_G3.md) links the accepted outputs, evidence manifest and remaining limitations.

```
Codex: Phases 0–4  → push → GATE G1 (data & corpus)  → review in reviews/G1_review.md
Codex: Phases 5–6  → push → GATE G2 (method & pilot) → review
Codex: Phases 7–11 → push → GATE G3 (results)        → review
Codex: Phase 12    → push → GATE G4 (final package)  → review → author writes the paper
```

## Kick-off prompt for Codex

> Read `AGENTS.md`, then `docs/RESEARCH_PLAN.md`, `docs/PROCEDURES.md` and `docs/DELIVERABLES.md`. Start at Phase 0 and work through Phase 4, following the acceptance checks. Push after each phase, write `reports/GATE_G1.md`, then stop and tell me Gate G1 is ready for review.

After each review, tell Codex: *"Pull, read `reviews/Gx_review.md`, address the [must] items, write `reports/GATE_Gx_response.md`, then continue to the next gate."*

## Status

The [2026-11-11 F1/F2/F3 review](reviews/phase07_review_F.md) approves corrected experiments and continuation to G3. Its P1 support-boundary reporting correction is now complete. Follow the [current implementation and evidence status](reports/phase_07_F1_F2_F3.md).

F1 has completed all 15,714 corrected H3/H4 solves in 18.498 hours. The combined 31,428-case evidence validates. F2 numerical analysis, both figures and all 33 original layout examples are accepted; see the [F1/F2 results report](reports/phase_07_F1_F2_results.md). F3 completed all 1,044 H3 cases over the same 348 small units in 8.398 hours; saved-layout checks, paired sensitivity analysis and figure review passed. See the [F3 results report](reports/phase_07_F3_results.md). The B benchmark independently validated all 600 outputs across 200 pairs and three algorithms. The D indicator analysis passed on 2,619 units and 10,476 unit–household pairs. See the [B results](reports/phase_08_B_results.md) and [D results](reports/phase_09_D_results.md). The R supporting analysis passed independent checks on 16 approximate reproduction cases and 10,476 main layouts. F11 has been visually checked. [R results](reports/phase_09_R_results.md).

The fixed-sample [ablations](reports/phase_09_ablation_results.md), grouped [surrogate evaluation](reports/phase_10_C_results.md), reduced H1/H3 [kit design](reports/phase_11b_K_results.md) and [Hong Kong shell scenario](reports/phase_11_HK_results.md) all passed their acceptance checks. The scenario covers 390 templates at 13 integer sizes.

**Current area-gain tables and figure:** use the [P1 results](reports/phase_07_P1_results.md) and [analysis_p1](results/expA_f1/analysis_p1/). Identified gains and lower bounds are separated; the frozen F2 area summaries and area figure are superseded. FCI effects, adequate-area estimates and layout checks are unchanged.

Original A/A1 and fixed-left A2 remain historical records. Their H3/H4 results are superseded by F1, and the old FEA-minus-own-area saving metric is retired for all households. Their reports retain historical statements and hashes; do not use those statements as the current execution status. E1–E3 evidence and compatible H1/H2 scores remain available.

| Gate | Status |
|---|---|
| Task L literature | [Retrieved snapshot screened](reports/novelty_check.md#systematic-confirmation-task-l--g3); access gaps documented |
| G1 data & corpus | Reviewed; geometry refresh and E1 selection are documented |
| G2 method & pilot | Approved continuation; frozen production settings retained |
| G3 results | [Ready for review](reports/GATE_G3.md) |
| G4 final package | Not started |

The [execution budget](reports/COMPUTE_BUDGET.md) records measured times and the reduced K scope. G4 follows G3 review.

## License

Code: MIT (see `LICENSE`). Datasets keep their own licenses (see `data/README.md`).
