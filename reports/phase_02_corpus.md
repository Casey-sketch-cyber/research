# Phase 02: Corpus construction — G1 revision

**Status: COMPLETE, superseding the original furnishable-area corpus.**

## Checklist and acceptance
- [x] Convert all authorized D1/D2 and generated D3 units; preserve source group IDs as opaque keys.
- [x] Normalize, audit and filter by NIA and complete-dwelling requirements.
- [x] Separate storage-only areas, deduplicate geometry and freeze the site-capped sample.
- [x] Audit D2 scales and D3 entrance keepouts; publish exclusion-bias distributions.
- [x] Regenerate counts, F2 and 24 sample views.
- [x] Run observed-source loader regressions and corpus acceptance: 35 passed in 36.57s; 28 checks passed.

## Key numbers
| source   |   total |   eligible_before_dedup |   included |   expA_sample |   missing_gross |   duplicate_copies_removed |   excluded |
|:---------|--------:|------------------------:|-----------:|--------------:|----------------:|---------------------------:|-----------:|
| D1       |   46830 |                    3533 |       2326 |          1347 |           46830 |                       1207 |      44504 |
| D2       |   17000 |                     892 |        884 |           884 |               0 |                          8 |      16116 |
| D3       |     510 |                     510 |        510 |           510 |               0 |                          0 |          0 |

## Exclusions (nonexclusive reasons)
| source   | exclude_reason                     |     n |
|:---------|:-----------------------------------|------:|
| D1       | above_max_nia                      | 40279 |
| D2       | above_max_nia                      | 16061 |
| D1       | entrance_not_touching_known_spaces |  7263 |
| D1       | no_kitchen                         |  2816 |
| D1       | missing_entrance                   |  1730 |
| D1       | no_sanitary                        |  1371 |
| D1       | duplicate_geometry                 |  1207 |
| D2       | rooms_outside_source_outline       |   666 |
| D1       | missing_window                     |   508 |
| D2       | implausible_scale                  |   355 |
| D1       | no_habitable_room                  |   255 |
| D2       | entrance_not_touching_known_spaces |   233 |
| D1       | furnishable_wall_overlap           |   208 |
| D2       | no_kitchen                         |   125 |
| D2       | unsupported_detached_interior      |    96 |
| D1       | detached_entrance                  |    57 |
| D1       | below_min_nia                      |    56 |
| D2       | missing_window                     |    51 |
| D2       | duplicate_geometry                 |     8 |
| D2       | missing_entrance                   |     6 |
| D2       | below_min_nia                      |     6 |
| D1       | geometry_processing_error          |     3 |
| D1       | missing_nia                        |     3 |
| D2       | normalization_changed_area         |     1 |

## Decisions and deviations
Normalized geometry hashes include class layers, walls, sorted openings, entrance, room count and service flags. IDs/sites are excluded. Hashing uses a 1 micrometre grid; analysis coordinates remain unchanged. Mirrors and quarter-turn equivalence are not inferred. n_duplicates counts additional eligible copies, not total multiplicity. The representative is the lexically first source/unit key. Site grouping is retained.

D1 uses fixed-seed random order within 2 m² NIA × room-count strata, selected by proportional-quota deficit subject to at most five per site. Site caps can prevent exact proportional allocation; sample_strata.csv and F2 expose the difference. All eligible unique D2/D3 units are retained. The pilot must draw from this frozen file.

NIA includes fixed rooms and storage but excludes walls. Source gross-area claims are not substituted for NIA. There is no furnishable-area fallback. D2 geometric scale calibration and strict entrance contact remain approved assumptions. Missing D1 gross area remains missing. See GATE_G1_response.md for all M/S responses and selection-bias tables.

## Open questions
Review the revised views and scale/entrance distributions at G2. No unsupported novelty, FCI or FEA conclusion is inferred from corpus construction.

## Runtime and reproducibility
Successful aggregation invocation: 105.435 s (cached source conversion excluded). Per-source conversion attempts are recorded in corpus_audit.json; interrupted/restarted attempts are not presented as total end-to-end runtime. Config hash: a65331afaa04445f3a5510e794c1cea52d481be60b3f93a96f2e2e5224846b70. Commands: docs/REPRODUCING.md.
