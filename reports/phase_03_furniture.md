# Phase 03: Furniture library check

**Status:** COMPLETE for G1 review. Reference comparisons do not validate the design defaults.

## 1. Checklist
- [x] Parse authorized ABO listing dimensions and units.
- [x] Remove values above the per-product-type 99th percentile and compute width/depth/height medians and IQRs.
- [x] Compare each configured item/state and record the strength of the category match.
- [x] Give every flagged item a keep/change justification; preserve furniture.yaml and provide commented proposals only.

## 2. Acceptance checks
All five automated checks passed in `furniture_audit.json`, including two tests.
Every footprint has a keep-pending-review decision and a reason in the CSV and
`results/furniture/interpretation.md`. No proposed size replacement was sufficiently
supported; `config/furniture_overrides.yaml` contains comments only.

## 3. Key numbers
The source contains 4,625 unique dimension-bearing reference listings in the
selected furniture types; 4,526 remain after type-specific trimming. The 24
configured footprints comprise nine static items, fourteen transformation states
and one optional item. Fourteen comparisons are outside the reference IQR;
fifteen states/items are explicitly unvalidated; four have no matching reference
cohort. These flag counts overlap. See `furniture_audit.json` for the source and
configuration hashes and `results/furniture/abo_type_statistics.csv` for sample
sizes, quartiles and trimming thresholds.

## 4. Deviations from the plan
Broad ABO categories cannot verify transformation-state dimensions, clearance,
storage capacity or the number of people served. Such comparisons remain
explicitly unvalidated; no product state is inferred from a generic category.

## 5. Decisions
Preserve author design defaults pending review. No size-based cohort filtering
will be used to make the configured footprints agree with the reference data.

## 6. Open questions
Reviewer to assess whether broad-category comparisons are sufficient and which
transformable states require separate evidence.

## 7. Runtime and resources
The successful script invocation took 10.623 seconds, including its two tests
(0.39 seconds). No GPU was used and peak memory was not measured.

## 8. Files added or changed
`src/fea/furniture/checks.py`, `scripts/04_check_furniture.py`,
`tests/test_furniture.py`, the commented overrides file, the three furniture
result files, and `reports/furniture_audit.json`.
