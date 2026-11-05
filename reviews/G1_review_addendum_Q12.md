# G1 review addendum: decision on Q-12 (task L stop)

Verdict on Q-12: **CONTINUE, with narrowed claims.** **G1 status:** unchanged (CHANGES_REQUESTED; M1–M6 still apply). **Date:** 2026-11-05

## Assessment

The stop was correct under the rule as written, and the evidence record is good: DOI, checksum, pages checked, and a clear line between the authors' analytical comparison and measured results.

Bu & Che Mat (2026) quantify the activity area of conceptual layouts in **one 12 m² bedroom**: about 5–5.5 m² with fixed furniture against about 8 m² with the wall bed folded, roughly 60%. This makes the broad wording "first quantification of how much floor area transformable furniture is worth" untenable, so that wording is **withdrawn**.

It doesn't touch the narrower contribution. Their work has no optimization, no activity-schedule-driven state assignment, no clearance or reachability guarantee, no multi-dwelling corpus, and no whole-dwelling equivalent area. *(The reviewer could not open the PDF independently, because the publisher blocks automated access. This decision relies on Codex's full-text record in `results/literature/fulltext_checks.json`.)*

## Decisions

1. **Claim wording.** C3 is now: *the first large-sample, schedule- and household-specific, feasibility-guaranteed estimate of transformable furniture's benefit, expressed as whole-dwelling functionally equivalent area.* C2 is narrowed to *a computational method that assigns furniture states from time-of-day activity demand, with positions shared across slots.* Both are updated in `config/lit_search.yaml` and RESEARCH_PLAN §1.
2. **Citations.** Add Bu & Che Mat (2026) as the C3 antecedent. Their single-room ~60% figure becomes a comparison point in the Discussion: report how our per-unit relative saving at about 12 m² compares, without implying the two measures are identical. Add Xiong, Cai & Luo (2026, CAVW) as a C2 distinction (motion coordination, not schedule-driven states). Cite *Mechanisms of Spatial Efficiency* (2025) as qualitative evidence of temporal adaptability. All three are in RESEARCH_PLAN §10 now; the missing volume and page details need verifying.
3. **Stop rule revised** (LITERATURE_SEARCH §5): only the narrowed C2/C3 trigger it, and even then it's logged without stopping the engineering work.
4. **Remaining screening** (LITERATURE_SEARCH §5a): finish it in the background of Phase 7 and report it at G3. It must not delay the G1 fixes.

## What to do now

1. Pull.
2. Implement G1 items M1–M6 (and S1–S4 if time allows). Update `reports/GATE_G1_response.md`.
3. Continue with Phases 5–6 and stop at Gate G2, as authorized in `reviews/G1_review.md`.
4. During the Phase 7 runs, complete the task L screening (§5a).
