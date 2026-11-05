# Gate G1 review

Verdict: CHANGES_REQUESTED

**Reviewer:** Claude, for the author · **Date:** 2026-11-05 · **Reviewed commit:** `5116f3c`

## Summary

This is careful, well-documented work. The provenance and checksums, the refusal to invent a D1 gross area or trust the D2 `net_area`, the explicit exclusion reasons, the area-preservation checks and the open-question log are exactly what was asked for. The D1 subtype mapping is sound, and the D2 scale calibration passes an independent check (see A2).

One substantive problem must be fixed before the solver runs. It comes from the plan itself, not from your implementation: **filtering on furnishable area does not select compact dwellings.** In the included D1 set, the median net internal area (`known_interior_area_m2`) is **54.2 m²** (IQR 41–62), and 2,619 units have three habitable rooms. D2 included units have a median gross area of **59 m²**, all with 2–5 rooms. Furnishable area excludes kitchens, bathrooms and circulation, so ordinary two- and three-room flats pass a 45 m² furnishable cap. The paper is about compact dwellings and minimum-size standards, which are stated in internal floor area, so the filter and the area axis must change (M1).

The reviewer has already updated `config/project.yaml` (corpus section, D1 classes, `expA_sample`) and `docs/RESEARCH_PLAN.md` §3–§5 to reflect the decisions below. Pull before working.

**How to continue:** implement M1–M6, regenerate the Phase 2 outputs, and write `reports/GATE_G1_response.md`. **Then proceed directly to Phases 5–6 without a separate G1 re-review.** The G2 package must open with the revised corpus summary (counts, F2, new contact sheet), so the reviewer can check M1–M6 there.

---

## Must-fix items

1. **[must] M1: Define "compact" by net internal area (NIA).**
   - NIA = union of the furnishable, storage_only, walkable_only and fixed_service spaces. It excludes walls, balconies and other excluded classes.
     - For D1 this is the existing `known_interior_area_m2`. Rename it `nia_m2` in outputs (it is not gross area, and Q-08's position of leaving gross area missing is approved).
     - For D2, compute the same union after calibration.
     - For D3, NIA is the shell's internal area, including the toilet pod and kitchenette.
   - Filter on `corpus.min_nia_m2`–`max_nia_m2` (8–50 m²). The furnishable-area thresholds are kept in the config for traceability only.
   - NIA is the **primary area axis** for f₀, FEA, the area-saving curve and A_min. Report furnishable area alongside as a secondary measure.
   - For reference, the current included D1 set has 4,505 units with NIA ≤ 50 m². D2 will be small (≈ 231 plans have gross ≤ 50 m²). That's acceptable: D2 is a robustness set. Report the count, and don't relax the threshold to enlarge it.

2. **[must] M2: Require a minimally complete dwelling.**
   - At least one habitable (furnishable) room.
   - A sanitary space (BATHROOM or SANITARY_ROOMS area, or a TOILET feature).
   - A kitchen (KITCHEN or KITCHEN_DINING area, or a KITCHEN feature, to allow open-plan kitchens).

   Contact-sheet sample D1-01 (16.4 m², no sanitary space, only a column as fixed service) is the kind of unit this removes. The 21 included D1 units with `n_rooms = 0` must also go. Add exclusion reasons `no_habitable_room`, `no_sanitary`, `no_kitchen` and report the counts.

3. **[must] M3: Storage rooms are not furnishable.** `STOREROOM` and `CLOAKROOM` move to a new class `storage_only` (already in the config). In Phase 5, cells of this class accept only items whose `serves` is `storage` (wardrobe, shelving), are walkable, and count towards NIA. They may not host beds, tables, desks or seating.

4. **[must] M4: Deduplicate repeated plans.** Identical plans repeat across floors and sites; contact-sheet samples D1-06 and D1-07 are the same layout. A rough check (same site, rooms, windows, doors and areas to 0.01 m²) collapses 11,598 included D1 units to about 6,864.
   - Hash the normalized geometry and keep one representative per hash, recording `n_duplicates`.
   - All experiments run on unique plans. Grouped splits still use `site_id`.

5. **[must] M5: Freeze the experiment sample before the pilot.** Write `results/corpus/expA_sample.csv` using `corpus.expA_sample`:
   - D1: up to 1,500 unique plans, stratified by 2 m² NIA bin × room count, at most 5 per site, with a fixed seed.
   - All compact D2 plans and all D3 shells.

   Pilot units (Phase 6) are drawn from this sample. If the Phase 6 projection exceeds 36 h, lower the D1 `n_max` first and report it. Report the sample's NIA histogram against the full compact corpus, to show the stratification is faithful.

6. **[must] M6: Regenerate the G1 artefacts** under the new definitions:
   - `corpus_units.csv`, with new columns `nia_m2`, `has_sanitary`, `has_kitchen`, `n_duplicates`, `in_expA_sample`
   - `counts.csv` and `exclusion_reasons.csv`
   - F2, with NIA on the x-axis and furnishable area as a second panel
   - A new 24-unit contact sheet drawn from `expA_sample.csv`, with NIA and furnishable area in each panel title

## Should-fix items

7. **[should] S1: D2 scale, corpus-wide sanity check.** The calibration is approved (Q-06, D-07). An independent spot check on the eight D2 sample plans gives calibrated door spans with medians of 0.82–1.06 m and wall thicknesses of 0.17–0.24 m, both plausible. Make this corpus-wide: report the distributions of calibrated door span and wall thickness (the release also has a `wall_depth` field to compare). Exclude plans whose median door span falls outside 0.6–1.3 m, or whose median wall thickness falls outside 0.05–0.50 m, as `implausible_scale`.
8. **[should] S2: Compare ABO dimensions regardless of orientation.** ABO `length`/`width` don't map consistently onto our width-along-the-wall/depth convention: for `desk`, ABO width 0.71 and length 0.95 look swapped relative to a 1.2 × 0.6 m desk. Compare sorted dimensions (long side, short side) instead. This is context for an appendix only; **no furniture value changes** (see Q-10).
9. **[should] S3: Check for bias from strict entrance exclusion.** Keep the strict contact tolerance (Q-11 approved). Report the NIA and room-count distributions of units excluded only for `entrance_not_touching_known_spaces` or `missing_entrance`, against included units, so the paper can state whether the exclusion is size-neutral.
10. **[should] S4: D3 service placement against the entrance.** In contact-sheet D3 sample 1 (10.48 m² furnishable), the kitchenette appears to start within about 5 cm of the entrance span on the same wall. Verify that no service body intrudes into the entrance door-swing keep-out in any shell. Record the service placement (`near_entrance` / `far_end`) as a shell attribute, so it can serve as a covariate.

## Answers to open questions

| Q | Decision |
|---|---|
| Q-01 Novelty check | The author's task, still outstanding. Engineering continues; make no novelty claim in drafts until it's done. |
| Q-02 D3 opening widths | **Approved:** D1 measured medians, labelled as geometric spans. |
| Q-03 Keep all shells with flags | **Approved.** The main-corpus filter and the HK scenario selection stay separate. |
| Q-04 Three-person households | **No new household.** The plan text now says one- and two-person households; larger households are a stated limitation. |
| Q-05 Splits | **Approved:** D1 grouped by site; D2 and D3 as external test sets. |
| Q-06 / D-07 D2 calibration | **Approved**, with the S1 sanity check. |
| Q-07 D6 lacks distributions | **Approved:** territory-level fallback; no inferred distributions. |
| Q-08 D1 gross area | **Approved** to leave gross area missing. NIA (M1) is the primary measure instead. |
| Q-09 Detached D2 components | **Approved:** exclude. |
| Q-10 Furniture defaults | **Approved as stated design assumptions**, unchanged. The paper will say so, and the clearance-scale sensitivity analysis bounds their effect. |
| Q-11 Entrance tolerance | **Approved:** keep strict, plus the S3 bias report. |
| D-05 KITCHEN_DINING as fixed service | **Approved** (conservative). Report how many units in `expA_sample` contain it. |
| D-12 FCI over variants | **Approved:** frequency-weighted average of per-variant FCI, with duplicate demands kept and storage credited by capacity. |

## Notes for Phase 5–6 (no action now)

- `storage_only` (M3) is a new cell class for the rasterizer and candidates.
- Use `nia_m2` everywhere an area appears in the solver outputs and metrics.
- D1 features `KITCHEN`, `BUILT_IN_FURNITURE`, `SINK`, `TOILET`, `BATHTUB`, `SHOWER` and `WASHING_MACHINE` are blocked cells. This is consistent with your mapping.
