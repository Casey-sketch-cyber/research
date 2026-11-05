# Phase 03: Furniture library check — G1 revision

**Status: COMPLETE; defaults approved as design assumptions.**

## Checklist and acceptance
- [x] Parse authorized listings and convert units.
- [x] Trim above the per-type 99th percentile.
- [x] Sort each footprint into long/short sides before quartile comparisons (S2).
- [x] Explain every flag and retain unchanged furniture defaults.
All 5 checks passed; 2 passed in 0.46s.

## Key numbers
Reference listings before/after trimming: 4625/4526. Comparisons: 24; outside IQR: 11; unvalidated states/items: 15; no cohort: 4. Flags overlap. Values are in results/furniture/abo_dimension_check.csv and abo_type_statistics.csv.

## Decisions, limitations and open questions
The review approved unchanged design defaults. Broad ordinary-product cohorts do not validate transformation mechanism/state, clearance, storage capacity or occupant capacity. No replacement size is inferred. The planned clearance sensitivity analysis remains necessary; state-specific product evidence is still limited.

## Runtime
Successful invocation: 10.317 s. Config hash: 82d8d08d5c86d0a16688aa23f5568be927e5b7239aec81d2bdfa8935128f33de.
