# Gate G2 review, round 2

Verdict: CHANGES_REQUESTED (two focused items; then Phase 7 may start without another stop unless R1 triggers the stop condition)

**Reviewer:** Claude, for the author · **Date:** 2026-11-06 · **Reviewed commit:** `5382e33`

## Summary

This is excellent work. M1–M9 are implemented, and the reviewer checked the most important ones independently:

- **M8 (walking width):** the validator's new `_reachable` and the solver's `walking_masks` were both rerun on synthetic corridors. A 0.60 m corridor passes and a 0.50 m one fails; 0.90 m passes and 0.80 m fails at a 0.90 m walking width. A 0.60 m strip between a body and a wall is reachable; a 0.50 m strip is not. The two implementations agree.
- **M9 (geometric cuts):** the guarded disjunction is a **valid** cut. If every witness cell stays covered by its owner, no frontier reference can open, so the reached component can't grow. It removes only layouts that would still be blocked, and it keeps alternate routes. Approved.
- **M1–M3:** the D3 generator, walkable kitchens and wall-aware gap closing are approved. All 240 pilot cases are valid, there are 0 valid zero-service layouts, and validator agreement is 100%.
- The throughput gain (264 h → 9.5 h projected) is real and well documented.

Two issues remain before Phase 7. The first concerns the **core claim of the paper**.

---

## R1 [must]: Check that S2 can actually find time-of-day transformation (stop condition below)

In the final pilot, **S2 beats S1 in only 1 of 80 unit-household pairs, and S2 has non-zero transformation burden in only 1 case.** This holds even in the 8 m² and 12 m² shells, where time-sharing should matter most. It holds in the 8-worker full-anchor reference too: `anchor_stride_summary.csv` has identical S1 and S2 means in every source.

There are two possible explanations, and they lead to very different papers:

- **(a) Search failure.** In the small shells, S2 runs often end at the time limit (e.g. `D3:384eb538…` with H3 and H4 at 12 m², and H3/H4 at 16 m²: 30 s, no proof) and return S1's layout. The rendered H3/S2 layout at 12 m² places no bed, so 8 h of sleep goes unserved.
- **(b) A genuine result under the current furniture assumptions.** Deployed double beds need clearance on *both* long sides (0.6 + 0.5 m), so in a 2.8 m-wide shell a double wall bed or sofa bed may simply not fit. Time-sharing then can't help, and nearly all the gain comes from compact transformable pieces used in one state (S1 − S0), not from switching them during the day (S2 − S1).

Do the following and report it in `reports/GATE_G2_response.md` (round 2 section), with all case-level data:

1. **Known-answer mechanism tests** (unit tests plus a small report table). Hand-build 3 shells (about 9, 11 and 13 m²; rectangular; one clear 1.7 m+ solid wall; a toilet pod and kitchenette placed away from that wall). For each, write a hand-made layout by hand: `wall_bed_over_sofa` against the clear wall plus a `drop_leaf_table` whose deployed footprint lies inside the bed's night-time footprint, and the rest of the household's items. The layout must use time-sharing: the table deployed by day, the bed deployed at night. Validate it with the validator and record its FCI as a **known lower bound**. Then solve S1 and S2 for H1 and H3.
   - Pass condition: S2 ≥ the known lower bound, and S2 > S1 in at least one shell.
   - If S2 falls below the hand-made layout, the search is failing: diagnose it (search budget, anchors, cuts, hints) and fix it.
2. **Long-budget rerun of the small units.** For every pilot unit with NIA ≤ 22 m², plus 12 additional D3 shells of 9–15 m² drawn from `expA_sample.csv` (fixed seed), solve S1 and S2 for all four households with 8 workers, full 0.10 m anchors and 300 s. Report S2 − S1 per case against the production setting.
3. **Decision rule:**
   - **If long budgets reveal S2 > S1 where the production setting doesn't:** the production setting is inadequate for small homes. Use a **size-dependent budget**: for NIA ≤ 20 m², the cheapest setting among {4 workers, 120 s, full anchors} and {8 workers, 300 s, full anchors} that reaches the long-budget S2 mean within 0.01. Re-project Exp. A and Exp. K. You may start Phase 7 if Exp. A ≤ 36 h.
   - **If S2 ≈ S1 even with long budgets and the known-answer tests pass:** the result is genuine under current assumptions. **Stop before Phase 7** and report. This changes the paper's framing, so the author must decide.
   - **If the known-answer tests fail:** fix the search, then repeat 1–2.

## R2 [must]: Keep wall-flush anchors on the coarse lattice, and fix the selection rule

`generate_candidates` filters anchors on a global 0.20 m lattice in **both** axes. For wall-backed items this deletes every flush position along walls whose coordinates aren't on the lattice, and D1 walls are at arbitrary positions. That explains the D1 loss: mean FCI −0.114 against the full-anchor reference, with reductions down to −0.69 per case.

- Apply the stride only **along** the wall for wall-backed items; perpendicular to the wall, keep every flush (wall-touching) anchor. Free-standing items keep the stride in both axes.
- **The reviewer's median rule (G2 M4) was a poor criterion,** because most medians sit at the 1.0 ceiling, so it can't tell settings apart. Replace it with: per-source **mean** FCI within 0.02 of the 8-worker full-anchor reference, and mean FCI for units with NIA ≤ 20 m² within 0.01 (after the R1 size-dependent budget, if adopted). Re-benchmark and re-select.
- The projection has headroom (9.5 h against 36 h), so trade it for quality.

## Other items

- **[should] R3: Don't edit files in `reviews/`.** Removing operational details from the G2 note followed the author's privacy instruction, and it is accepted. In future, though, log the need in `reports/QUESTIONS.md` and let the reviewer change the file. (Rule added to AGENTS.md.)
- **[should] R4: Exp. K projection.** K runs on exactly the small shells where R1 matters. Re-project it with whatever R1 decides for NIA ≤ 20 m² before the K pilot. If it no longer fits the 2-day time box, report options (a smaller grid or fewer shells at stage 1) rather than shortening per-solve budgets.
- **Approved without changes:** greedy warm start; adaptive slicing of solver rounds; hints refreshed at each restart; downward sharing; empty-incumbent handling; walkable kitchens with separate kitchen targets; gap closing that keeps NIA unchanged; the D3 mapping with 0 exclusions; strict_access deferred to Exp. B.

## Order of work

R2 → R1 → (decision rule) → Phase 7, or stop. Write a short round-2 section in `reports/GATE_G2_response.md` either way.
