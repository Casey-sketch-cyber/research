# Phase 02: Corpus construction

**Status:** IN PROGRESS; Phase 01 acceptance passed.

## 1. Checklist (from PROCEDURES.md)
- [ ] Convert residential D1 records to unit geometry and identify entrances.
- [ ] Convert D2 geometry with an explicit, audited scale and class mapping.
- [ ] Generate every configured D3 shell family with fixed toilet and kitchenette.
- [ ] Normalize coordinates, validate geometry and apply the corpus filter.
- [ ] Write processed geometry, corpus CSV, inclusion/exclusion counts and area histogram.
- [ ] Render the fixed-seed sample: eight included units per source.
- [ ] Test at least one observed D1 dwelling and one observed D2 plan.

## 2. Acceptance checks
| Check | Result | Evidence |
|---|---|---|
| Corpus counts and histogram | PENDING | Not run |
| Exclusion reasons | PENDING | Not run |
| Sample renders | PENDING | Not run; human review is at G1 |
| Loader tests | PENDING | Not run |

## 3. Key numbers
Pending measured outputs.

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
Pending implementation and measured checks.

## 6. Open questions for the reviewer
See `reports/QUESTIONS.md` for scale and shell-geometry assumptions.

## 7. Runtime and resources
Not run.

## 8. Files added or changed
This checklist.
