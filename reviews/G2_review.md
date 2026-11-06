# Gate G2 review

Verdict: CHANGES_REQUESTED

**Reviewer:** Claude, for the author · **Date:** 2026-11-06 · **Reviewed commit:** `67af2ee`

## Summary

The G1 fixes are done well: NIA-based selection, complete-dwelling checks, deduplication and a frozen sample (D1 1,347 / D2 884 / D3 510). The solver/validator design is sound, and the report is unusually honest. Retaining invalid and zero-service cases, explaining every access failure, and running the downward-validation audit are exactly right.

The method itself is approved, apart from the points below. **Two things block Phase 7:**

1. **Too many failures come from the model rather than the dwellings.**
   - 3 of 6 D3 shells fail empty access. The contact sheet shows the generator placing the kitchenette so it blocks the toilet-pod door, or leaving entrance pockets narrower than the walking width. That's a generator defect, not a property of small homes.
   - In D1 and D2, whole-room fixed-service blocking and source-geometry gaps produce structural failures and zero-service "valid" layouts. These would bias FCI, and therefore FEA, downwards in ways unrelated to furniture.
2. **The runtime projection (264 h) is roughly 7× over budget.** It assumes one solve at a time with 8 threads each, on 14 effective cores. Throughput, not the per-solve limit, is the main lever. A weak search (60 s timeouts; an empty S2 layout in a 12 m² shell that passes access) is the second.

The fallback source caps of 153/100/57 are **not approved**: 57 D3 shells would gut the Hong Kong scenario and Exp. K. Fix the model and the throughput first (M1–M6), then apply the cap rule in M7 only if needed.

**How to continue:** implement M1–M9 (M8 and M9 come from the code review in §6), rerun the same 20-unit pilot (regenerating its D3 units with the same parameters) and update `reports/phase_06_pilot.md`. Then write `reports/GATE_G2_response.md`. **If every criterion in §3 passes, go straight on to Phase 7 without another stop.** Otherwise stop and report.

---

## 1. Must-fix items

1. **[must] M1: Fix the D3 shell generator.**
   - Place the toilet pod and kitchenette so that:
     - the pod door opens onto free floor reachable from the entrance;
     - every passage from the entrance to the pod door and to the main space has a clear width of at least 0.90 m, measured in continuous geometry before rasterization;
     - no service body touches the entrance door-swing keep-out.
   - Try the configured placements in order. If none works for a parameter combination, drop that shell with reason `generator_infeasible` and report the count.
   - A shell that fails the empty-access check is a generator failure: regenerate it or drop it. It must not enter the sample as `STRUCTURAL_UNREACHABLE`.
   - Re-draw the D3 part of `expA_sample.csv` with the same rules and seed, and record the old→new shell mapping.

2. **[must] M2: Kitchens are walkable; fixtures are not.**
   - Cells in `KITCHEN` and `KITCHEN_DINING` areas become **walkable but not furnishable**. Only kitchen fixtures (D1 features `KITCHEN`, `SINK`, `BUILT_IN_FURNITURE`, `WASHING_MACHINE`, and the D3 kitchenette) are blocked.
   - Bathrooms and other sanitary spaces stay blocked except for their door-approach band. A route may not pass through a bathroom.
   - The kitchen service target becomes "at least one walkable kitchen cell is reachable". The bathroom target stays as it is.
   - Rerun the `fixed_service_diagnostic` and report which pilot failures this resolves.

3. **[must] M3: Close source-geometry gaps that aren't walls.**
   - Before rasterizing, close gaps of up to 0.15 m between adjacent interior spaces when no wall/separator, railing or other blocking entity lies in the gap. A morphological close of the interior-space union, minus the blocking entities, is acceptable. Never close a gap that a wall occupies.
   - Report how many units change connectivity.
   - For each remaining zero-service valid case, record a cause: `source_gap_remaining`, `room_not_connected_in_source`, `search_fallback` or `genuinely_infeasible`.

4. **[must] M4: Run solves in parallel.**
   - Benchmark throughput on the 240 pilot cases with `num_workers` ∈ {1, 2, 4}, running ⌊14 / num_workers⌋ solves concurrently. Report the wall-clock time per 100 cases and the validated FCI distribution for each setting.
   - Choose the setting with the best throughput whose median FCI is within 0.01 of the 8-worker baseline. Update `solver.num_workers` and record the decision.

5. **[must] M5: Strengthen the search.**
   - **(a) Anchor stride:** place anchors on a 0.20 m lattice while collision and access stay on the 0.10 m raster. Report how FCI changes against the current exhaustive anchors on the pilot. The full-resolution check stays in the resolution ablation.
   - **(b) Greedy warm start:** implement the planned Exp. B greedy baseline now and pass its validated layout to CP-SAT as a solution hint.
   - **(c) Share incumbents downward:** whenever a strategy's validated layout is also feasible under a lower strategy (it uses only static items, or one state per variant-day), give it to that lower strategy as an incumbent and re-validate there. Report strategy differences only after this sharing, so the saving can't come from one strategy simply being searched harder than another. The 16 witness cases in `validation_audit.csv` show this is needed.
   - **(d)** Then benchmark `time_limit_s` ∈ {30, 60}, as PROCEDURES already prescribes.

6. **[must] M6: Report the projection properly.** Measure throughput with the parallel setting, project Exp. A (D1/D2/D3 sample × 4 households × 3 strategies) and Exp. K separately, and add a 15% margin.

7. **[must] M7: Rule for capping the sample (only if M6 still exceeds 36 h for Exp. A).**
   - Reduce in this order, keeping stratification by NIA bin and source, until the projection fits:
     1. D1 down to a minimum of 500 plans (it stays the surrogate training set).
     2. D2 down to a minimum of 200.
     3. D3: keep **every valid shell with NIA ≤ 20 m²** (needed by the HK scenario and Exp. K) and sample the larger shells down to at least 60.
   - If the minimums still don't fit, stop and report; don't go below them.

8. **[must] M8: Fix the walking-width test, a bug that biases FCI downwards.** Code review addendum. Both `validate._reachable` and `solve/reachability.check_connectivity` accept a cell as a walking-disc centre if `edt·res − res/√2 ≥ walking_width/2`. On a 0.10 m raster, **a 0.60 m corridor never passes this test; the narrowest passable corridor is 0.70 m.** The reviewer reproduced this with the same `distance_transform_edt` call.

   Consequences:
   - The effective walking width is about 0.70 m, not the configured 0.60 m.
   - A 0.60 m bed-side or desk clearance strip between the item and a wall or another body is never "reached", so the item gets no service, although the strip is exactly the access zone the config intends.
   - Small units are hit hardest. This feeds directly into FCI, FEA, A_min and the D3 `conservative_raster_loss` failures.

   Replace the test, in both modules, with an exact-width disc test: erode the free mask with a disc whose diameter is `walking_width / resolution` cells (even sizes allowed, e.g. a 6×6-cell disc for 0.60 m), run the BFS on the eroded reference positions, and dilate the reached set back by the same disc to get the area a walking person can cover. An item is accessible if its active clearance strip intersects that area.

   Add unit tests, shared by solver and validator expectations but implemented separately:
   - (a) a straight 0.60 m corridor is passable;
   - (b) a 0.50 m corridor is not;
   - (c) a 0.60 m clearance strip between a bed and a wall makes the bed accessible;
   - (d) the same cases at walking width 0.90 m (0.90 passes, 0.80 fails).

   The reviewer checked that an even-sized disc erosion separates 0.50 m from 0.60 m correctly. Rerun the pilot after this fix; it may resolve several of the access failures on its own.

9. **[must] M9: Use stronger access cuts in the solver.** When access fails, `Model.cut` forbids only the *exact* combination of present/x/y/orientation/state values of the blocking items. Each failure removes one point from a space of thousands of anchors, which explains the many 60 s timeouts and the empty fallback layouts. Replace or supplement it with a **geometric cut**:
   - identify the bottleneck cells (blocking bodies ∩ dilated border of the disconnected region) and their bounding rectangles;
   - add fixed optional intervals for those rectangles, enforced only when the failed assignment literal is true, into the slot's body NoOverlap2D;
   - that forbids **every** pose covering the bottleneck while that service is claimed.

   Also hint each iteration with the previous iteration's solution minus the offending items, so restarts don't begin cold. Report the change in iterations per case and in time to first valid solution.

## 2. Method decisions (answers to "Review decisions requested")

| Item | Decision |
|---|---|
| Interval and anchor-table encoding instead of expanded pose/cell Booleans | **Approved.** It's equivalent in feasibility and more efficient. Describe it as such in the methods. |
| S1 = one state per transformable item per variant-day | **Approved.** This matches the definition. |
| Access for multi-person items: one reachable point in the union of clearance strips | **Approved for the main runs**, as a stated simplification: compact homes commonly have a bed against a wall with access from one side. **[should]** On the Exp. B 200-instance sample, add a sensitivity check (`strict_access`) requiring both long sides of a double bed and every seat strip to be reachable, and report the change in FCI. |
| Fixed-service approach band = 0.3 m + one cell | **Approved.** For the 0.90 m walking-width ablation, scale the band with walking width / 2. |
| Early stop at the proved capacity bound with zero burden; window tie-break unoptimized | **Approved.** Report the share of cases stopped this way. The window preference stays secondary and is never interpreted. |
| Keeping the previous strategy's layout as an incumbent | **Approved, together with the downward sharing in M5c.** |
| Raw CP-SAT objective and bound fields | **Approved as documented.** Never present them as optimality gaps of the retained layout. |
| Endpoint states only; no motion or swept-volume check | **Approved.** This is a limitation in the paper. |
| Fixing balcony doors that were wrongly treated as service targets | **Approved.** |

## 3. Criteria for going straight to Phase 7

All of these must hold on the rerun pilot:

1. **Structural failures:** D3 has none (by construction, M1). In D1 and D2, `STRUCTURAL_UNREACHABLE` affects ≤ 1 of the 14 pilot units, and any remaining case has a diagnosis.
2. **Zero-service valid layouts:** none caused by `source_gap_remaining` or `search_fallback` in a unit that passes empty access. Any remaining case is explained.
3. **Ordering:** S2 ≥ S1 ≥ S0 holds after downward sharing. Any violation is explained.
4. **Validator agreement:** unchanged (100%).
5. **Budget:** the projected Exp. A wall-clock time with M4/M5 settings and the 15% margin is ≤ 36 h, after applying M7 if necessary.

If any criterion fails, stop, write `reports/GATE_G2_response.md` with the evidence, and wait for review.

## 4. Should-fix items

- **[should] S1:** add to `summary_by_group.csv` the share of cases ending at the proved bound, at timeout with an incumbent, and with zero-service fallbacks, per source × strategy.
- **[should] S2:** in the layout renders, draw kitchen cells as walkable (light grey hatch) after M2, so reviewers can see routes through kitchens.
- **[should] S3:** in the next report, include one rerun render each of the 8 m² and 12 m² D3 shells under S0 and S2 for H1. These are the key Hong Kong cases.

## 6. Code review notes

The reviewer read `validate.py`, `metrics.py`, `solve/cpsat.py` and `solve/reachability.py`. The tests could not be run in the review environment, so the 56-test result is Codex's.

- **Validator independence: good.** It imports no solver or candidate logic, reconstructs rectangles from the config, recomputes service, access, FCI and cyclic TB, and ignores credits supplied in the input. One limit to note in the methods: solver and validator share the rasterization (`geometry/raster.py`), so a raster defect such as the source gaps in M3 can't be caught by the validator.
- **Correct as implemented:**
  - CP-SAT NoOverlap2D encoding (bodies against bodies; each clearance strip against the other bodies)
  - S1 as one state per variant-day
  - cyclic burden in S2 only
  - the rational FCI coefficients
  - the forced-use constraint (`present ≤ Σ assignments`)
  - the relaxed capacity bound
  - `invert_monotone` (right-censoring rather than extrapolation)
- **Bug:** M8 (walking-width test).
- **Performance:** M9 (weak exact-value no-goods; cold restarts).
- **Minor [should]:** the window-distance cost uses the anchor cell, not the body centre. It's harmless as a tie-break, but say so in the methods.

## 5. Note for the author (not for Codex)

[Operational equipment details omitted under the author’s publication-privacy instruction.] The benchmark uses the 14-core concurrency budget specified in M4. Any future change to that budget requires a new measured throughput projection.
