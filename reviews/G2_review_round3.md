# Gate G2 review, round 3

Verdict: APPROVED to start Phase 7, once the two pending checks in §3 pass (no further stop needed if they pass)

**Reviewer:** Claude, for the author · **Date:** 2026-11-07 · **Reviewed commit:** `24fb678`

## 1. What the round-2 evidence shows

R1 and R2 are done carefully, and the reporting is admirably cautious:
- The known-answer fixtures are kept out of the study population.
- Within-arm and cross-run evidence are separated.
- A coarse arm that scores higher than the long arm isn't read as a better method.

**The mechanism works.** In the hand-built rooms, S2 finds time-sharing layouts and reaches every hand-made lower bound. For a couple, the score rose from 0.69 (S1) to 0.99 (S2) at 11 m² and from 0.73 to 0.92 at 9 m².

**Long budgets don't change the population picture.** With 8 workers, full anchors and 300 s per solve, S2 beat S1 in **5 of 64** small-home pairs. The S2 mean was 0.709 against an S1 mean of 0.696. The reviewer recomputed `small_final_w8_t300/pairs.csv` and confirmed:

| Household | Mean S1 | Mean S2 | Pairs where S2 > S1 |
|---|---|---|---|
| H1 single commuter | 0.763 | 0.763 | 0 / 16 |
| H2 single remote worker | 0.822 | 0.822 | 0 / 16 |
| H3 couple | 0.653 | 0.700 | 4 / 16 (+0.17, +0.27, +0.28 at 13–14 m²; +0.02 at 10 m²) |
| H4 parent and child | 0.547 | 0.552 | 1 / 16 (+0.08 at 13 m²) |

**Reading:** under the current assumptions, switching furniture during the day matters only for **two-person households in a narrow size band (about 12–15 m²)**. Below that band the essential pieces don't fit at all; above it, everything fits in one state. Where it does apply, the effect is large. This is a **genuine finding, not a search failure**: the decision rule's long-budget branch applies (gains are real and partly missed by short budgets), and the known-answer tests pass.

**Framing decision (reviewer, with the author informed):**
- Keep S2 in the study.
- Report the total gain decomposed into a **form effect** (S1 − S0) and a **time effect** (S2 − S1) by household and NIA bin. This is now in RESEARCH_PLAN §3.
- The "squeeze band" is labelled an exploratory pattern from the pilot that the full run tests. It is not a pre-registered hypothesis.

## 2. Code review (since `2eb8e27`)

The reviewer read `furniture/candidates.py`, `solve/cpsat.py`, `solve/greedy.py` and `diagnostics.py`.

- **Wall-flush lattice (R2): correct.** At orientations 0/180 the back side lies along x, so the stride is applied along x only; at 90/270 it's applied along y. Flush perpendicular coordinates are kept. Free-standing items keep both strides. Approved.
- **Pose, state and assignment hints: correct.** They are hints only; no domain is restricted, and an off-lattice pose hint is simply skipped. Approved.
- **Greedy portfolio warm start:** valid, because every accepted layout is checked by the validator and no fixture or result is passed in. **[must] B1:** in Exp. B, the "greedy" baseline must be the specified `footprint` policy alone (as RESEARCH_PLAN §5.3 describes), not the three-policy portfolio. Report the portfolio separately, if at all, as the CP-SAT warm start.
- **Audit:** 384/384 saved small-home layouts are valid, with 0 score mismatches (reviewer checked `completed_layout_audit.csv`).
- The validator still shares rasterization with the solver; that is already a stated limitation.

## 3. Conditions for starting Phase 7

Codex lists these as pending. Complete them, report them in `reports/phase_07_expA.md`, and **start Exp. A without another stop if both pass**:

1. **Hybrid quality check:** production settings are 1 worker / 0.20 m wall-aware anchors / 30 s for NIA > 20 m², and 4 workers / 0.10 m / 120 s for NIA ≤ 20 m². Run them against a **fresh** 8-worker full-anchor 60 s reference on the 240-case pilot, using the current code. Criteria: per-source mean FCI within 0.02, and NIA ≤ 20 m² mean within 0.01. If the larger-home setting fails, step up to 2 workers / 60 s and recheck.
2. **Runtime reprojection:** Exp. A (S0/S1/S2 × 4 households, the frozen sample) with a 15% margin must be ≤ 36 h. Apply the G2 M7 cap rule if needed. Reproject Exp. K under the small-home setting; if it exceeds its 2-day time box, report options before starting K.

If either fails after the stated fallback, stop and report.

## 4. Additions to Phase 7 and later

- **[must] A1: Decomposition.** Exp. A outputs must include, per household × 2 m² NIA bin: mean and bootstrap CI of S1 − S0 and of S2 − S1, plus the share of units with S2 > S1. Add figure F4b (stacked form and time effects against NIA, by household).
- **[must] A2: Double-bed access sensitivity.** Run `ablations.double_bed_one_side_access` (in `config/project.yaml`) after Exp. A, on all Exp. A sample units with NIA ≤ 20 m², for H3 and H4, under S0/S1/S2 with the small-home setting. Report the change in the form and time effects. The main runs keep the current furniture configuration unless the author decides otherwise.
- **[should] A3:** In the HK scenario and in Exp. K, report the time effect separately too. Both work in the size band where it appears.
- **B1** (above) applies when Exp. B is run.
