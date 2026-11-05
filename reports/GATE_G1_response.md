# Response to G1 review

**Status: M1–M6 and S1–S4 corpus changes complete; continued engineering authorized through G2.**

Q-12 continuation is authorized in reviews/G1_review_addendum_Q12.md. Related work is evidence to build on; no first/novelty claim or literature-based engineering stop remains. Later Experiments R and K are added by the author and remain beyond G2. Remaining Task L screening is due during Phase 7/G3; the historical stop report is not the current instruction.

## M1: NIA — done
NIA is the union of furnishable, storage-only, walkable-only and fixed-service regions minus walls. Excluded outdoor/service classes are not added. The primary filter is 8–50 m² with only a 1e-6 m² numerical tolerance; the obsolete furnishable-area fallback is not applied. D1 gross area remains missing. F2 reports NIA first and furnishable area second.

## M2: Complete dwellings — done
Require a habitable room with positive furnishable area, sanitary room/fixture and kitchen room/fixture. Explicit reasons are in exclusion_reasons.csv (reasons overlap, so their counts must not be summed as unique exclusions).

## M3: Storage-only rooms — done in corpus and Phase 5
STOREROOM/CLOAKROOM and D2 storage are a separate storage_only layer. Their area counts towards NIA and circulation; only storage furniture bodies may occupy them in candidate generation and validation. No beds/tables/seating are recategorized as storage furniture.

## M4: Deduplication — done
Normalized geometry hashes include class layers, walls, sorted openings, entrance, room count and service flags. IDs/sites are excluded. Hashing uses a 1 micrometre grid; analysis coordinates remain unchanged. Mirrors and quarter-turn equivalence are not inferred. n_duplicates counts additional eligible copies, not total multiplicity. The representative is the lexically first source/unit key. Site grouping is retained.

## M5: Frozen experiment sample — done
D1 uses fixed-seed random order within 2 m² NIA × room-count strata, selected by proportional-quota deficit subject to at most five per site. Site caps can prevent exact proportional allocation; sample_strata.csv and F2 expose the difference. All eligible unique D2/D3 units are retained. The pilot must draw from this frozen file.

D1 sample sites: 486; largest site contribution: 5. Sample units containing KITCHEN_DINING: 0; that class remains conservatively fixed service, as approved.

## M6: Regenerated artifacts — done
corpus_units.csv, counts.csv, exclusion_reasons.csv, expA_sample.csv, sample_strata.csv, F2 PNG/PDF, sample_units.json, 24 individual views and the contact sheet are regenerated from the revised definitions. Views show both areas and are drawn from the frozen sample.

| source   |   total |   eligible_before_dedup |   included |   expA_sample |   missing_gross |   duplicate_copies_removed |   excluded |
|:---------|--------:|------------------------:|-----------:|--------------:|----------------:|---------------------------:|-----------:|
| D1       |   46830 |                    3533 |       2326 |          1347 |           46830 |                       1207 |      44504 |
| D2       |   17000 |                     892 |        884 |           884 |               0 |                          8 |      16116 |
| D3       |     510 |                     510 |        510 |           510 |               0 |                          0 |          0 |

## S1: D2 scale — done
Door span is the long side of each calibrated opening's minimum rectangle. Wall thickness uses normal cross-sections at wall-boundary edge midpoints, weighted by edge length, not a bounding-box width. Unmeasurable values and median door/wall spans outside 0.6–1.3 / 0.05–0.50 m are excluded. Released wall_depth is scaled independently for comparison. No measured value is clipped to the admissible ranges.

| source   | category   | measure                 |     n |        min |      q25 |   median |      q75 |      max |
|:---------|:-----------|:------------------------|------:|-----------:|---------:|---------:|---------:|---------:|
| D2       | D2_all     | median_door_span_m      | 17000 | 0.0252453  | 0.921201 | 0.970449 | 1.02726  | 2.47096  |
| D2       | D2_all     | median_wall_thickness_m | 17000 | 0.00522317 | 0.200479 | 0.215758 | 0.237281 | 0.619242 |
| D2       | D2_all     | released_wall_depth_m   | 17000 | 0.00522317 | 0.200479 | 0.215758 | 0.237272 | 0.619242 |

Per-plan values and flags: d2_scale_audit.csv. Scale plausibility supports the approved calibration assumption; it is not independent ground-truth surveying.

## S2: ABO orientation — done
Each listing footprint is sorted to long/short sides before computing quartiles. Configuration dimensions are similarly sorted. 11 of 24 comparisons are outside the IQR; 15 remain state-specific unvalidated comparisons and 4 have no cohort. Furniture defaults are unchanged and review-approved design assumptions.

## S3: Entrance selection bias — done
The comparison below includes only units whose complete reason set is a nonempty subset of missing_entrance / entrance_not_touching_known_spaces; no other failure is included. Included units are deduplicated. The table reports observed selection differences, not an assumption that exclusion is size-neutral. The pre-dedup eligible distribution is also available in review_distributions.csv.

| source   | category                | measure   |    n |     min |     q25 |   median |     q75 |     max |
|:---------|:------------------------|:----------|-----:|--------:|--------:|---------:|--------:|--------:|
| D1       | included_unique         | nia_m2    | 2326 | 12.3195 | 31.4054 |  38.9791 | 45.6353 | 49.997  |
| D2       | included_unique         | nia_m2    |  884 | 17.9174 | 42.2586 |  45.464  | 48.0448 | 49.958  |
| D3       | included_unique         | nia_m2    |  510 |  8      | 12      |  16      | 25      | 40      |
| D1       | included_unique         | n_rooms   | 2326 |  1      |  1      |   1      |  2      |  3      |
| D2       | included_unique         | n_rooms   |  884 |  2      |  2      |   2      |  2      |  5      |
| D3       | included_unique         | n_rooms   |  510 |  1      |  1      |   1      |  1      |  1      |
| D1       | entrance_only_exclusion | nia_m2    |  830 | 16.4408 | 33.5987 |  42.539  | 47.5322 | 49.9933 |
| D2       | entrance_only_exclusion | nia_m2    |    4 | 42.8781 | 44.3414 |  45.5285 | 46.7947 | 48.4954 |
| D1       | entrance_only_exclusion | n_rooms   |  830 |  1      |  1      |   1      |  2      |  3      |
| D2       | entrance_only_exclusion | n_rooms   |    4 |  2      |  2      |   2      |  2      |  2      |

## S4: D3 services — done
Maximum fixed-service/entrance-keepout overlap: 0 m². Placement counts: {"far_end": 244, "near_entrance": 266}. near_entrance requires both service centroids in the entrance-wall half of the shell; otherwise far_end. All generated shells remain recorded, even if a later check excludes one.

## Acceptance and scope
28/28 automated acceptance checks passed. Full suite: 40 passed in 38.52s. Config hash: 82d8d08d5c86d0a16688aa23f5568be927e5b7239aec81d2bdfa8935128f33de. The corpus package contains no FCI/FEA results. Continue Phases 5–6 and stop at G2 under the review authorization.

## Engineering corrections
D1 and D2 records exposed a GEOS assertion when subtracting mixed-dimensional geometry from empty storage. Empty storage now bypasses that identity operation; the observed D2 record has a regression test and both full sources are checked. Completed cached records were reused only where the correction was semantically identical; new clean runs regenerate all source data. D1/D2 resume skips already completed keys before geometric conversion.

## Visual inspection of regenerated artifacts
The 24-unit contact sheet and F2 were inspected: both area labels are legible, the D1-05 storage room is distinct, service areas are separated from furnishing space, and D3 entrance spans remain unobstructed by service bodies. F2 shows that the site cap reduces the share of smaller D1 units in the frozen sample; exact proportionality is not claimed. These are checks of rendered geometry, not furniture feasibility results.
