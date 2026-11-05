# Phase 04: Household schedules

**Status:** COMPLETE for G1 review. Schedules retain uncalibrated author defaults.

## 1. Checklist
- [x] Parse slots, variants, demands, weights and capability rules.
- [x] Implement demanded_hours with separate alternative-day denominators.
- [x] Test 24-hour coverage, known capabilities, duplicate demands and hand-computed totals.
- [x] Generate Table T3 from unchanged household defaults.
- [x] Defer optional ATUS calibration; no empirical calibration claim is made.

## 2. Acceptance checks
All four checks in `reports/households_audit.json` passed. Nine household tests
passed, including hand-computed totals, midnight wrap, duplicate demand IDs,
capacity/weight separation, different variant denominators, and rejection of
overlaps, unknown tokens, invalid weights/units and incomplete schedules.
`results/tables/T3_households.csv` and its Markdown version were generated.

## 3. Key numbers
Table T3 contains 36 slot rows for five households and six day variants. Weighted
demanded hours are H1: 18.9, H2: 26, H3: 26, H4: 28 and H5: 26. These are sums
over simultaneous activity requirements and can exceed 24 clock hours. H1 is
8 + 2*(1+1) + 2 + 1 + 3*(1+0.3); H4 is 8*2 + 2*(1+1) + 2*(1+1) + 1 + 3.
H3 keeps the exact configured frequencies 0.857 and 0.143. H5 remains ablation
only, with walking width 0.90 m and clearance multiplier 1.2.

## 4. Deviations from the plan
Optional ATUS calibration is deferred. Household defaults remain author assumptions.

## 5. Decisions
Preserve the configured variant frequencies exactly. Storage capacity requirements
are attributes of one demand, not extra demand weights. Duplicate sleep demands
remain separate. Variant FCI values must later be averaged by frequency; averaging
their denominators is only a descriptive summary and is not the FCI formula.

## 6. Open questions
No schedule changes proposed before G1 review.

## 7. Runtime and resources
Successful invocation: 0.632 seconds, including nine tests (0.38 seconds).
CPU only; peak memory was not measured.

## 8. Files added or changed
`src/fea/households.py`, `scripts/05_schedules.py`, `tests/test_households.py`,
the three T3 files and `reports/households_audit.json`. The household config is
byte-identical to the author version; its hash is in the audit.
