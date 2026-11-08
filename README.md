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

Experiment A has completed all solves but failed final validation. Downstream
execution stopped before A1; see the [completion audit](reports/expA_completion_audit.md).
The affected units exactly match failures in the earlier full-sample connectivity
record. Cause diagnosis and correction validation remain pending.

| Gate | Status |
|---|---|
| Task L literature | Q-12 permits continuation with narrowed C2/C3; remaining screening due at G3 |
| G1 data & corpus | G1 review completed; G2 geometry refresh is recorded in current corpus artifacts |
| G2 method & pilot | Round 3: APPROVED to start Phase 7 once §3 checks pass (see `reviews/G2_review_round3.md`) |
| G3 results | not started |
| G4 final package | not started |

Current work is recorded in [G2 round-2 self-review](reports/G2_round2_self_review.md).
The [round-3 implementation and dated status](reports/G2_round3_status.md) records
the current conditional approval, fresh pilot, A/K projections and automatic
continuation checks. The updated [Phase 7 checklist](reports/phase_07_expA.md)
includes paired form/time decomposition and the later double-bed sensitivity.
The author has restored K's two-day cap and withdrawn the full grid (D-38).
The [execution budget](reports/COMPUTE_BUDGET.md)
separates pilot-calibrated estimates, full-cap workload projections and work that
has not yet been timed. The reduced exploratory K scope requires a frozen grid
and a confirming runtime pilot; the main experiments are unchanged.
The budget now reports experimental compute time only. The earlier calendar ETA
with an unmeasured analysis/development reserve is retired; uncalibrated experiments
remain explicit rather than receiving arbitrary extra days.
The wall-flush correction has been benchmarked on the unchanged 240 cases. The
six hand-written witnesses and unconstrained mechanism comparisons now pass;
unsuccessful development arms remain visible. The numerical suite passes 103
tests, with a separate additional budget-comparison integration test.

The old w1_s20_t30 selection and its A/K projections are historical and must be
replaced using the round-2 mean-quality and small-home budget checks. The frozen
16-unit small-home comparisons are complete: 384/384 layouts independently
revalidated, with no score mismatches. The provisional small-home setting is
4 workers / 120 s / full anchors, satisfying the predeclared S2 mean criterion
against the 300 s reference in both scopes. See the dated
[progress snapshot](results/pilot/round2/progress_snapshot.json). A guarded Phase 7 runner exists
but refuses to start without accepted current settings and a <=36-hour projection.
Formal A has started after passing the fresh quality and runtime checks; K and R
remain unstarted. No FEA or population-level hypothesis conclusion is claimed
from the unfinished A run. Its dated progress snapshot is in
`results/expA/progress_snapshot.json`; continuation state is in
`results/pilot/round3/execution_status.json`. Literature screening remains due at G3. Uploads have been reauthorized; the current review package includes completed
mechanism evidence, all 384 small-home layouts with hashes, and completed budget
comparisons. The fresh pilot and source-quality checks are complete; A retains
all 2742 units with a 26.074-hour projection including margin. The pilot plan and
completion state are in
[pilot_refresh_status.json](results/pilot/round2/pilot_refresh_status.json).

## License

Code: MIT (see `LICENSE`). Datasets keep their own licenses (see `data/README.md`).
