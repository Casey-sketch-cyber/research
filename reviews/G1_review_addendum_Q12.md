# G1 review addendum: decision on Q-12 (task L stop)

Verdict on Q-12: **CONTINUE, with sharpened positioning.** **G1 status:** unchanged (CHANGES_REQUESTED; M1–M6 still apply). **Date:** 2026-11-05

## Assessment

The stop was correct under the rule as written, and the evidence record is good: DOI, checksum, pages checked, and a clear line between the authors' analytical comparison and measured results.

Bu & Che Mat (2026) quantify the activity area of conceptual layouts in **one 12 m² bedroom**: about 5–5.5 m² with fixed furniture against about 8 m² with the wall bed folded, roughly 60%. This is a welcome antecedent: it supports the premise, and it gives us a concrete estimate to generalize and test. We simply phrase our contribution relative to it, rather than as a "first quantification".

What our study adds to it: their analysis has no optimization, no activity-schedule-driven state assignment, no clearance or reachability guarantee, no multi-dwelling corpus, and no whole-dwelling equivalent area. *(The reviewer could not open the PDF independently, because the publisher blocks automated access. This decision relies on Codex's full-text record in `results/literature/fulltext_checks.json`.)*

## Decisions

1. **Positioning.** Contributions are phrased as what this project adds to named prior work (RESEARCH_PLAN §1 positioning table), not as "first" claims. Relative to Bu & Che Mat: we generalize and test their single-room estimate across real plans, household schedules and dwelling sizes, with guaranteed feasibility, and express it as whole-dwelling equivalent area.
2. **Citations.** Add Bu & Che Mat (2026) as the C3 antecedent. Their single-room ~60% figure becomes a comparison point in the Discussion: report how our per-unit relative saving at about 12 m² compares, without implying the two measures are identical. Add Xiong, Cai & Luo (2026, CAVW) as a C2 distinction (motion coordination, not schedule-driven states). Cite *Mechanisms of Spatial Efficiency* (2025) as qualitative evidence of temporal adaptability. All three are in RESEARCH_PLAN §10 now; the missing volume and page details need verifying.
3. **No stop rule** (LITERATURE_SEARCH §5, revised again on the author's guidance): the screening maps how we build on each related work. Related work never stops the engineering work.
4. **Remaining screening** (LITERATURE_SEARCH §5a): finish it in the background of Phase 7 and report it at G3. It must not delay the G1 fixes.

## What to do now

1. Pull.
2. Implement G1 items M1–M6 (and S1–S4 if time allows). Update `reports/GATE_G1_response.md`.
3. Continue with Phases 5–6 and stop at Gate G2, as authorized in `reviews/G1_review.md`.
4. During the Phase 7 runs, complete the task L screening (§5a).
