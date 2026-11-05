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

## 5. Decisions
Pending implementation and measured checks.

## 6. Open questions for the reviewer
See `reports/QUESTIONS.md` for scale and shell-geometry assumptions.

## 7. Runtime and resources
Not run.

## 8. Files added or changed
This checklist.
