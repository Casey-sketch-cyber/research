# Phase 02: Corpus construction

**Status:** COMPLETE for G1 review. Computational acceptance passed; the human visual and modelling review remains at G1. Upload awaits repository write access.

## 1. Checklist (from PROCEDURES.md)
- [x] Convert residential D1 records to unit geometry and identify entrances.
- [x] Convert D2 geometry with an explicit, audited scale and class mapping.
- [x] Generate every configured D3 shell family with fixed toilet and kitchenette.
- [x] Normalize coordinates, validate geometry and apply the corpus filter.
- [x] Write processed geometry, corpus CSV, inclusion/exclusion counts and area histogram.
- [x] Render the fixed-seed sample: eight included units per source.
- [x] Test at least one observed D1 dwelling and one observed D2 plan.

## 2. Acceptance checks
| Check | Result | Evidence |
|---|---|---|
| Corpus counts and histogram | PASS | `results/corpus/counts.csv`; `results/figures/F2_corpus_area.png` and `.pdf` |
| Exclusion reasons | PASS | `results/corpus/exclusion_reasons.csv`; reasons may overlap |
| Sample renders | PASS, human review pending | 24 PNGs in `results/corpus/samples/`; source metadata in `sample_units.json` |
| Loader tests | PASS | `reports/phase02_acceptance.json`: 12 tests pass without skips |
| Full package checks | PASS | All 16 checks true, including CSV/parquet agreement and public sample local coordinates |

## 3. Key numbers
| Source | Converted | Included | Excluded | Missing entrance |
|---|---:|---:|---:|---:|
| D1 | 46,830 | 11,598 | 35,232 | 1,730 |
| D2 | 17,000 | 1,978 | 15,022 | 6 |
| D3 | 510 | 420 | 90 | 0 |

Evidence: `reports/corpus_audit.json` and generated corpus tables. The area
ceiling remains 45 m²: D1 already exceeds the minimum sample requirement. D1
simulation summaries are available for 46,815 records. The maximum included-unit
normalization area change is 1.6503e-8 m². Three D1 topology failures and one D2
area-preservation failure are explicitly excluded. The complete exclusion
table is in `results/corpus/exclusion_reasons.csv`; counts are not mutually
exclusive. No sample cap is applied.

The 24-panel contact sheet was visually inspected. Source classes, openings and
entrances are distinguishable. D1 sample 01 has no labelled fixed-service room;
no bathroom or kitchen was invented. D1 samples 06 and 07 have similar source
layouts, consistent with repeated plans in a site; grouped evaluation remains
necessary. D2 samples show no unexplained detached inner region. D3 samples
show the nearest feasible service arrangement, which can place the toilet at
the far end of a narrow shell. These modelling cases are highlighted for G1.

## 4. Deviations from the plan
- D1 lacks an authoritative apartment gross-area field; gross area stays missing. Known interior-space area is recorded separately, never relabelled as gross.
- D2 metric scale is sqrt(source `area` / union(inner, wall, door, window, front_door).area). The released `net_area` is not used. This explicit assumption needs G1 review.
- D3 uses observed D1 opening-record median spans, not verified clear widths. Services use the nearest feasible corner/wall arrangement without body or entrance keep-out overlap. All shells remain available even when below the main furnishable-area filter.
- D1 has no separate verified whole-unit outline. Its known interior is the union of classified interior spaces and assigned openings. Containment is consequently constructive for D1, rather than an independent test against a supplied footprint. D2 additionally checks classified rooms against its source inner/structure footprint.
- Normalization can expose floating-point topology defects; invalid transformed layers are repaired and every unit is checked for area preservation. Units with no classified interior keep missing contact distances instead of invalid JSON NaN values.
- A numerical coordinate grid of 1e-9 m removes near-coincident vertices before rotation; post-transform snapping and validity repair preserve polygon area within 1e-6 m² for included units. Zero-area remnants of polygonal layers are dropped. A measured D2 regression where naive repair changed area is covered by an observed-source test.
- If a source unit still raises a GEOS topology error, it receives an explicit `geometry_processing_error` exclusion and missing normalized area, with an empty geometry placeholder. No source-frame geometry or fabricated area is substituted. An excessive area change is separately excluded as `normalization_changed_area`.

### Conversion rules

| Source | Furnishable | Walkable only | Fixed service / excluded |
|---|---|---|---|
| D1 | Explicit Phase 1 subtype mapping, minus built-in features and walls | Mapped circulation plus door openings, minus fixed services | Mapped service rooms, built-in features and columns; other subtypes remain excluded |
| D2 | Bedroom, living, storage, dining and office, clipped to `inner` and excluding fixed services/walls | Remaining inner area and door openings, excluding fixed services/outdoor labels/walls | Bathroom and kitchen fixed; balcony (including release spelling `balacony`), garden, parking, pool and stair excluded; parcel `land` is not a room |
| D3 | Rectangular shell minus the two configured fixed services | None as a separate class; walking may use furnishable space later | Configured toilet pod and kitchenette, with no added guessed furniture or dimensions |

D1 entrance selection uses source `ENTRANCE_DOOR` labels first, choosing the
candidate closest to known interior spaces when several exist. Only if those
labels are absent does it try contact with public circulation. Door contact
uses a strict numerical tolerance; millimetre-scale source gaps remain explicit
exclusions pending G1 review. No physical padding is introduced to improve the
inclusion count. D2 unexplained detached inner components also cause exclusion.

Daylight and noise metadata are unweighted means over the available D1
simulation area records, not dwelling area-weighted exposures. Room counts use
components of the mapped habitable-room labels; D3 has one main room. These
source-dependent conventions require care in later room-based comparisons.

All layers receive one shared rigid transform. The origin is the minimum of the
known interior, so an excluded balcony may legitimately extend to negative
local coordinates. The source-to-local transform is not exported.

## 5. Decisions
See D-07 through D-10 in `reports/DECISIONS.md`. The numerical grid and failure
exclusions are engineering safeguards; they do not change furniture dimensions
or household schedules.

## 6. Open questions for the reviewer
See `reports/QUESTIONS.md` for scale and shell-geometry assumptions.

## 7. Runtime and resources
The successful main invocation took 927.19 s. Source conversion took 906.64 s
for D1, 267.01 s for D2 and 5.08 s for D3; independent source conversion was
overlapped. These times exclude earlier failed/debugging runs. CPU only; peak
RAM was not sampled and is not estimated. See `reports/corpus_audit.json`.

## 8. Files added or changed
Source loaders, geometry representation/normalization/audits, corpus builder
and acceptance script, rendering code, observed-source tests, scalar corpus
tables, sample geometries/images, area figure and reproducibility instructions.
