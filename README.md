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

| Gate | Status |
|---|---|
| Task L literature | Q-12 permits continuation with narrowed C2/C3; remaining screening due at G3 |
| G1 data & corpus | G1 review completed; G2 geometry refresh is recorded in current corpus artifacts |
| G2 method & pilot | Revision complete; awaiting the author-requested Claude review; see reports/GATE_G2_response.md |
| G3 results | not started |
| G4 final package | not started |

Start the review with [reports/GATE_G2_response.md](reports/GATE_G2_response.md). The corrected pilot has 240 valid and 0 invalid layouts out of 240, 100% independent FCI agreement, and 79 passing tests. The [artifact manifest](results/pilot/layout_manifest.csv), [audit](reports/g2_revision_audit.json), [benchmarks](results/pilot/benchmark_comparison.csv) and [reproduction instructions](docs/REPRODUCING.md) accompany the package.

Selected configuration: w1_s20_t30. Exp. A projects to 9.510 h including the 15% margin; Exp. K is estimated separately. All five G2 continuation criteria pass: True. The author requested another Claude review before proceeding. Phase 7, K and R remain unstarted; no FEA or hypothesis conclusion is claimed. Literature screening remains due at G3.

## License

Code: MIT (see `LICENSE`). Datasets keep their own licenses (see `data/README.md`).
