# Phase 7 — Experiment A

Status: preparation only. No formal Experiment A result is available. The author
has delegated self-review and continuation and paused uploads. The runner must
refuse to start until round-2 mechanism, mean-quality and runtime checks pass.

## Checklist

- [ ] Freeze the final production settings and any authorized sample cap using
  the round-2 mean-quality rules; retain every small D3 shell.
- [ ] Run the final frozen sample × four households × S0/S1/S2, resuming only
  identical code, input and configuration fingerprints; respect the total CPU budget.
- [ ] Revalidate every layout and strategy exchange; report zero-service,
  time-limit, invalid and ordering rates without hiding failures.
- [ ] Fit household-specific pooled and source-specific isotonic S0 curves on
  NIA, the primary area axis specified by the G1 review.
- [ ] Compute FEA, saving and relative saving with explicit right-censoring;
  never extrapolate unsupported equivalent areas.
- [ ] Estimate 2 m²-bin saving curves and unit-bootstrap 95% intervals using
  1,000 resamples, with clear reporting of excluded censored values.
- [ ] Estimate logistic minimum-adequate areas at tau=0.95 and sensitivity
  thresholds 0.90/1.00; flag unidentifiable or out-of-support crossings.
- [ ] Report paired S2−S0 and S2−S1 tests and effect sizes by household.
- [ ] Export fixed-seed example layouts and approximately 10/18/30 m² H3
  showcases; inspect the actual drawings.
- [ ] Complete the remaining literature screening and evidence limits before G3.
- [ ] Write an evidence-backed self-review; do not upload until requested again.

The guarded runner is implemented and its five acceptance-guard tests plus dry-run pass. It has not run Experiment A: the accepted production_selection.json intentionally does not yet exist. Source code and benchmarks remain local; the expanded numerical regression suite passes 103 tests.
