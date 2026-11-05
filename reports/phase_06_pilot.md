# Phase 06: Solver, independent validator and pilot

**Status: IMPLEMENTED; frozen pilot running, G2 not yet ready.**

## Checklist
- [x] Shared furniture anchors and S0/S1/S2 state rules.
- [x] Body, active-clearance, backing and window constraints.
- [x] Distinct-instance service assignment, capability alternatives and partial storage capacity.
- [x] Frequency-weighted per-variant FCI and cyclic transformation burden.
- [x] Reachability through radius-eroded free space, fixed-service approaches and no-good cuts.
- [x] Independent validator that imports no solver code; adversarial geometry/service tests.
- [x] Tiny end-to-end solve and hand-computed FCI/monotone FEA tests.
- [x] Freeze 20 pilot units from expA_sample (8 D1, 6 D2, 6 D3 including 8/12 m²).
- [ ] Run all 4 households × 3 strategies, preserve status, bounds, timings and validator results.
- [ ] Commit all pilot JSONs/renders; inspect at least six renders.
- [ ] Report ordering exceptions and project Exp. A runtime; reduce D1 cap first if over 36 h.
- [ ] Publish the G2 package and stop for review.

## Actual implementation
Candidate anchors remain exhaustive at the configured raster resolution. Integer tables select an absent sentinel or one anchor/orientation; optional rectangle intervals impose body/body and active-clearance/body exclusions. Clearance strips may overlap each other. Every state must fit at the shared anchor, while collisions use only the active state. This replaces the plan's explicit pose/cell Boolean expansion without removing grid poses. Identical-instance ordering removes permutation symmetry; unused furniture is dominated and omitted.

S0 admits static items; S1 fixes each transformable state throughout each variant-day; S2 permits slot-specific states. Variant-days share furniture anchors. Demands are assigned to distinct instances, including multi-token alternatives and duplicate simultaneous demands. Storage credits are capacity fractions. Exact rational coefficients implement frequency-weighted per-variant FCI; lexicographic scaling prioritizes FCI over cyclic transformation burden and then anchor distance to windows.

Reachability erodes the free raster by half the walking width. The distance-to-blocked-centre transform subtracts the blocked cell's half diagonal, giving a conservative walking-disc test. The solver uses connected components; the independent validator reconstructs rectangles from original configuration and uses an explicit four-neighbour BFS. It imports no solver or candidate logic. Fixed-service approaches must be reachable. Unreachable furniture assignments receive no credit; structural geometry or fixed-service failures invalidate the layout.

After a failed access check, a no-good excludes the boundary-blocker pose/state combination while the failed service remains assigned. Adding assignment bits allows furniture to remain useful in other slots without forcing an unreachable service claim. The best independently valid layout survives time/iteration limits. A preceding strategy's validated layout is a warm start and retained incumbent, so finite-budget ordering is partly enforced by this protocol and is not evidence that every strategy optimum was found.

The early-stop capacity bound removes geometry and day-wide state consistency, enumerating distinct-instance capability assignments. Early termination is allowed only at that upper FCI bound with zero transformation burden; the window tie-break remains explicitly unoptimized. Raw CP-SAT objective/bound fields refer to the last search, which may differ from the retained validated layout. They must not be interpreted as a final-layout optimality gap.

All solver budgets include model construction and reachability checks; raster/candidate generation shared across the household/strategy cases is accounted separately. One solve runs at a time to respect the effective concurrency limit. The fixed seed does not guarantee byte-identical multi-threaded CP-SAT incumbents or runtimes across reruns.

Empty-layout access failures remain in the frozen sample with `STRUCTURAL_UNREACHABLE` status and zero FCI. This is a failure under conservative source classification and raster geometry, not a claim that the original dwelling is physically unusable. The G2 report will diagnose each affected unit.

Experiments R/K and remaining literature screening are later phases, not part of this pilot. There are no full-experiment FEA or area-saving conclusions yet.
