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
| G1 data & corpus | M1–M6/S1–S4 corpus revisions complete; 28 acceptance checks and 40 tests pass |
| G2 method & pilot | 240-case pilot complete; 56 tests pass; ready for review |
| G3 results | not started |
| G4 final package | not started |

Start the review with [`reports/GATE_G2.md`](reports/GATE_G2.md), which opens with the revised G1 corpus, F2 and contact sheet. [Reproduction commands](docs/REPRODUCING.md), the [complete artifact manifest](results/pilot/layout_manifest.csv) and [independent audit](reports/pilot_audit.json) accompany the package. The current full suite passes all 56 tests.

The pilot contains 180 valid layouts and 60 explained invalid cases. Search-quality limitations, conservative access failures and the 264.08 h Exp. A projection against a 36 h budget require G2 review. Proposed scope adjustments have not been applied. Phase 7 has not started, and no full-experiment FEA or area-saving conclusion is claimed. Task L literature screening remains explicitly incomplete and is due at G3.

## License

Code: MIT (see `LICENSE`). Datasets keep their own licenses (see `data/README.md`).
