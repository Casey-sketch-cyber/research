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

**Current author instruction (2026-11-06):** continue under self-review and resume
sanitized GitHub uploads for review. Preserve the methodological checks and
immutable review records; unfinished experiments are explicitly labelled.

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

F1 has completed all 15,714 corrected H3/H4 solves in 18.498 hours. The combined 31,428-case evidence validates. F2 numerical analysis, both figures and all 33 original layout examples are accepted; see the [F1/F2 results report](reports/phase_07_F1_F2_results.md). F3 completed all 1,044 H3 cases over the same 348 small units in 8.398 hours; saved-layout checks, paired sensitivity analysis and figure review passed. See the [F3 results report](reports/phase_07_F3_results.md). The 12-pair B timing pilot passed all 36 outputs; the full 200-pair, three-algorithm benchmark is now running. Its saved-output audit and analysis will run automatically after completion. See [B status and settings](reports/phase_08_expB.md). Dated evidence is in [results/expA_f1](results/expA_f1/) and [results/expA_f3](results/expA_f3/).

**Current area-gain tables and figure:** use the [P1 results](reports/phase_07_P1_results.md) and [analysis_p1](results/expA_f1/analysis_p1/). Identified gains and lower bounds are separated; the frozen F2 area summaries and area figure are superseded. FCI effects, adequate-area estimates and layout checks are unchanged.

Original A/A1 and fixed-left A2 remain historical records. Their H3/H4 results are superseded by F1, and the old FEA-minus-own-area saving metric is retired for all households. Their reports retain historical statements and hashes; do not use those statements as the current execution status. E1–E3 evidence and compatible H1/H2 scores remain available.

| Gate | Status |
|---|---|
| Task L literature | Q-12 permits continuation with narrowed C2/C3; remaining screening due at G3 |
| G1 data & corpus | Reviewed; geometry refresh and E1 selection are documented |
| G2 method & pilot | Approved continuation; frozen production settings retained |
| G3 results | Pending completion of corrected experiments and later phases |
| G4 final package | Not started |

The approved order is F1 → F2 → F3 → B → D/R/ablations → C → K → HK → literature → G3, with no further intermediate reviewer stop. K retains H1+H3 and its 48-hour cap; the full grid remains disabled. The [execution budget](reports/COMPUTE_BUDGET.md) distinguishes historical measured time from new workload allocations and unmeasured experiments. The former 10–14-day calendar estimate is retired. Uploads remain authorized after privacy checks.

## License

Code: MIT (see `LICENSE`). Datasets keep their own licenses (see `data/README.md`).
