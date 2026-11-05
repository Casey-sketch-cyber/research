# Gate G2: revised corpus, method and pilot

**Status: READY FOR REVIEW. Phase 7 has not started.**

## Revised G1 corpus first

| source | eligible_before_dedup | included | duplicate_copies_removed | expA_sample |
| --- | --- | --- | --- | --- |
| D1 | 3533 | 2326 | 1207 | 1347 |
| D2 | 892 | 884 | 8 | 884 |
| D3 | 510 | 510 | 0 | 510 |

NIA is the primary area measure; complete dwellings, storage-only classes, geometric deduplication and the frozen sample follow G1 M1–M6. Read [G1 response](GATE_G1_response.md), [F2](../results/figures/F2_corpus_area.png) and the [new contact sheet](../results/corpus/sample_contact_sheet.png) first. D1's site cap prevents filling its nominal maximum; source and area coverage limitations remain in the G1 response.

## Method review

The implemented solver, independent validator, simplifications and full result interpretation are in [phase_06_pilot.md](phase_06_pilot.md). The principal implementation differences are exhaustive integer anchor tables and optional rectangle intervals in place of expanded pose/cell Booleans; one S1 state per variant-day; a conservative walking-disc raster; retained nested-strategy incumbents; and early stopping at a proven primary capacity bound with zero burden, leaving window preference unoptimized. Geometry, storage and household defaults remain unchanged.

## Pilot results

All 240 cases from 20 frozen units are present. Independent revalidation found 180 valid layouts and 60 explained invalid cases from 5 units failing empty-layout access. There are 163 valid nonempty layouts and 17 valid empty layouts. Among valid layouts, 29 score zero service, including 12 with furniture present but no credited service. These fallbacks are reported separately so geometric validity or furniture count cannot conceal poor search performance or disconnected access.

| status | cases |
| --- | --- |
| FEASIBLE | 80 |
| FEASIBLE_ACCESS_ADJUSTED | 60 |
| STRUCTURAL_UNREACHABLE | 60 |
| TIMEOUT_WITH_INCUMBENT | 32 |
| OPTIMAL | 8 |

The 80 unit/household triples have 0 violations of S2 ≥ S1 ≥ S0. Retaining prior-strategy incumbents contributes to this property: 66 cases retained one, including 45 stopped at a proved primary bound. This is a finite-budget method check, not evidence that all strategy optima were solved. Strategy differences can include unequal search difficulty or a poor static incumbent; they must not yet be interpreted as furniture-caused area savings.

In 16 observed adjacent-strategy improvements, the improved saved layout also passes the independent validator under the lower strategy with the same score. These are explicit witnesses of a weaker lower-strategy search result, not evidence that its furniture restrictions prevent that score. The per-case diagnostic is retained in [validation_audit.csv](../results/pilot/validation_audit.csv); this check does not alter any selected layout or score.

Retained-assignment FCI agreement and every saved config/code hash passed the independent audit. Agreement compares the separately recomputed, access-adjusted assignment score (`fci_solver`) with the validator, not the raw CP-SAT relaxation; raw scores and access failures remain in each solver trace. The saved objective/bound values describe the last raw CP-SAT search, not necessarily the retained validated layout. Tests: `56 passed in 42.08s`. Detailed checks and final/raw search-status counts: [pilot_audit.json](pilot_audit.json); every layout and image: [layout_manifest.csv](../results/pilot/layout_manifest.csv).

The [per-unit summary](../results/pilot/summary_by_unit.csv) includes zero-service counts and runtimes; the [source/household/strategy summary](../results/pilot/summary_by_group.csv) preserves all cases, including failures.

## Access failures and interpretation

| unit_key | target_index | continuous_diagnostic_reachable | reason |
| --- | --- | --- | --- |
| D1:49816767142d653310ef | 0 | False | fixed_classification_or_source_geometry_blocks_continuous_approach |
| D2:08f1c19ec3fae64971ce | 2 | False | fixed_classification_or_source_geometry_blocks_continuous_approach |
| D3:c664e38ee8ad7512e30e | 0 | True | conservative_raster_loss |
| D3:3039fa9dc0ece06809b4 | 0 | False | fixed_classification_or_source_geometry_blocks_continuous_approach |
| D3:bef90434d4b523903474 | 0 | True | conservative_raster_loss |

- `D1:49816767142d653310ef`: The entrance component reaches the upper service approach. The lower service approach lies beyond the region blocked by the whole-room fixed-service classification; its normal interior route is not available to this conservative model.
- `D2:08f1c19ec3fae64971ce`: The upper-right room and its service approach lie outside the entrance component across the narrow source-geometry connection. Both the continuous diagnostic using the conservative classification and the raster reject this approach.
- `D3:c664e38ee8ad7512e30e`: The route around the toilet pod and kitchenette corners survives the continuous diagnostic but loses connectivity under whole-cell rasterization and conservative walking-disc erosion. This is a resolution/conservatism failure, not evidence of a continuously blocked shell.
- `D3:3039fa9dc0ece06809b4`: The toilet pod and kitchenette leave a narrow connection between the entrance pocket and the main space. The service approach fails both the continuous diagnostic and the raster under the configured walking width.
- `D3:bef90434d4b523903474`: The narrow passage between fixed blocks near the entrance remains connected in the continuous diagnostic but disconnects on the conservative raster. Resolution sensitivity is required before interpreting its zero score.

The diagnostic continuous check erodes the same conservative source-space classification. `conservative_raster_loss` means a continuous route exists but the whole-cell raster and conservative walking-disc criterion remove it; the required resolution sensitivity must examine this. Other failures also occur under the continuous classification, because fixed rooms, narrow connections or source geometry interrupt the approach. None establishes that the original dwelling is physically unusable. These cases remain in the denominator with invalid status and zero FCI.

Visual diagnosis also corrected kitchen-to-balcony doors mistakenly treated as mandatory indoor service approaches. A door touching an excluded exterior space but no usable interior outside door polygons is now excluded from that target list. Unknown non-exterior connections remain conservative targets. The frozen units, source geometry, dimensions and walking width were unchanged; provisional runs before this correction are not final results.

See [fixed_service_diagnostic.csv](../results/pilot/fixed_service_diagnostic.csv) and the empty-layout sheets for [D1](../results/pilot/empty_access_D1.png), [D2](../results/pilot/empty_access_D2.png), [D3](../results/pilot/empty_access_D3.png).

The [empty-space connectivity summary](../results/pilot/empty_space_summary.csv) also tests connectivity before walking-radius erosion and counts reachable furnishable cells. Passing fixed-service access does not imply that every habitable room is connected; source-space gaps can therefore produce valid but zero-service layouts. No unlabelled gap was filled to improve a score.

## Runtime and Exp. A projection

Measured solver time summed across cases is 1.845 h. Per-case median / p90 / p95 / maximum are 13.784 / 60.072 / 60.131 / 60.475 s. These times exclude plotting and shared preparation; the projection adds measured source-specific raster/candidate preparation.

| source | full_units | pilot_units | mean_unit_solver_s | mean_unit_preparation_s | projected_h |
| --- | --- | --- | --- | --- | --- |
| D1 | 1347 | 8 | 415.0082 | 0.2482 | 155.3751 |
| D2 | 884 | 6 | 290.3824 | 0.2875 | 71.3756 |
| D3 | 510 | 6 | 263.3919 | 0.0934 | 37.3271 |

The source-weighted projection is **264.08 h**, against 36 h, with one solve at a time. A descriptive unit-bootstrap interval is 193.49–340.41 h. It is not a completion guarantee: the pilot is small, D3 deliberately spans selected areas, and fast structural failures are included. Geometry revisions need a new projection. Aggregation, I/O and selected publication renders are additional costs.

Reducing D1 alone cannot satisfy the budget: D2+D3 already project to 108.70 h. The calculated D1 cap is zero, which is not a viable scientific design because D1 supplies the training corpus. At review, address solver efficiency and geometry issues first, then benchmark the prescribed shorter per-case budget and propose source-stratified caps if still necessary. Do not extrapolate a proportional speedup from halving the time limit: validated solution quality and actual stopping times must be measured. No frozen sample or solver limit has been changed by this report. A concrete fallback at the existing solver budget is source caps D1/D2/D3 = 153/100/57, giving a point projection of 29.89 h, or 35.87 h with the scheduling margin. This uniformly reduces source coverage after checking the D1-only option and requires reviewer approval because D2/D3 were originally all-inclusive. It is a scope proposal, not an executed experiment or a promise about unseen runtimes; preserve source-specific NIA stratification and the D1 site cap.

## Recorded visual review

All frozen empty layouts were also inspected on the three source contact sheets; observations and image hashes are recorded in [pilot_visual_review.json](pilot_visual_review.json).

- [`results/layouts/pilot/D1_26c3cf1fe59956b266da_H1_S0.png`](../results/layouts/pilot/D1_26c3cf1fe59956b266da_H1_S0.png): Static bodies remain fixed across all normal-day slots. Drawn routes enter through the circulation space and reach the relevant access strips; kitchen and sanitary areas remain unoccupied. Titles and legend are readable.
- [`results/layouts/pilot/D1_26c3cf1fe59956b266da_H2_S1.png`](../results/layouts/pilot/D1_26c3cf1fe59956b266da_H2_S1.png): The selected S1 solution uses static furniture. The work-slot route reaches the desk access strip; no within-day body/state changes appear. Shared clearance zones are translucent and distinguishable from bodies.
- [`results/layouts/pilot/D1_26c3cf1fe59956b266da_H3_S2.png`](../results/layouts/pilot/D1_26c3cf1fe59956b266da_H3_S2.png): Wall bed deploys at night and folds for the remaining slots; the drop-leaf table shows the converse normal-day pattern. Hatched stowed footprints preserve their anchors. Night routes reach both bed access zones, and the incomplete activity score is clearly shown rather than hidden.
- [`results/layouts/pilot/D1_f732e6230a6c7ba6ab35_H1_S0.png`](../results/layouts/pilot/D1_f732e6230a6c7ba6ab35_H1_S0.png): Furniture is visible in every slot, but no credited activity routes are drawn and the title reports zero FCI. The entrance circulation region is disconnected from furnishable cells under the source classification; this is a valid zero-service result, not evidence of a successfully furnished dwelling. Panel titles, axes and legend do not overlap.
- [`results/layouts/pilot/D1_49816767142d653310ef_H1_S0.png`](../results/layouts/pilot/D1_49816767142d653310ef_H1_S0.png): The retained empty layout is explicitly labelled INVALID in all-slot summary metadata, with zero FCI. The entrance vestibule is separated from the lower service approach by fixed-classified space. No furniture or invented activity paths conceal the structural-access failure.
- [`results/layouts/pilot/D2_016671f59dcf2ba8685b_H3_S2.png`](../results/layouts/pilot/D2_016671f59dcf2ba8685b_H3_S2.png): The S2 result uses only static furniture, unchanged across the six slots. Bed, desk, dining and two distinct armchair instances are visible; the drawn activity routes connect through the internal doorway to the left room. Fixed rooms remain unoccupied. Full reported FCI with zero burden therefore does not itself demonstrate a transformation benefit.
- [`results/layouts/pilot/D3_c664e38ee8ad7512e30e_H1_S0.png`](../results/layouts/pilot/D3_c664e38ee8ad7512e30e_H1_S0.png): The 8 m² shell remains empty and is labelled INVALID with zero FCI. Pod and kitchenette footprints are preserved; no fabricated furniture route bypasses the narrow passage. The matching empty-access sheet and continuous diagnostic explain the conservative raster loss.
- [`results/layouts/pilot/D3_384eb538ea7940b40792_H1_S2.png`](../results/layouts/pilot/D3_384eb538ea7940b40792_H1_S2.png): The 12 m² shell passes empty fixed-service access but the retained S2 layout is empty, with zero FCI and no activity routes across all slots. This clearly exposes a search fallback; it is not proof that furnishing this shell is impossible. Titles, axes and the empty-layout legend remain readable.
- [`results/layouts/pilot/D3_bdf0c78c4eba6436fb93_H1_S2.png`](../results/layouts/pilot/D3_bdf0c78c4eba6436fb93_H1_S2.png): The 32 m² shell contains six static items with unchanged footprints across the normal day. Routes from the bottom entrance reach the bed, dining/storage and lounge approach zones in the relevant slots; the fixed pod and kitchenette remain clear of furniture bodies. Full FCI and zero burden are shown without implying a need for transformation.

## Reproduction and boundary

From the repository root after reproducing the revised corpus and installing the declared environment:

```sh
python scripts/05_candidates.py
python scripts/06_pilot.py
python scripts/06_report.py --run-tests
python scripts/06_gate.py
```

The final command checks the hashes in the recorded visual reviews. Re-solving with multithreaded CP-SAT can produce different incumbents even with the same seed; new images must be visually reviewed before updating that review record. All numbers above are generated by this script from saved audited outputs. No Phase 7 experiment, FEA estimate, minimum-area result, R/K analysis or hypothesis verdict is claimed here.


## Review decisions requested

- Check the exact encoding, service-target scope, alternative-clearance approach rule for multi-person items, S1 variant-day interpretation and early-stop/retained-incumbent protocol before full experiments.
- Review conservative access failures and valid empty/time-limited fallbacks; decide any method or resolution changes before treating FCI as an optimized research outcome.
- Review the measured runtime projection and the proposed scope response. Furniture and household parameters were not adjusted to improve outcomes.
- Return the verdict in `reviews/G2_review.md`. Work stops at this gate as required.
