# Phase 7 — Experiment A

Status: round-3 conditional approval; acceptance checks in progress. The reviewer
authorizes starting Experiment A without another stop once the fresh hybrid
quality comparison and <=36-hour projection pass. See `reviews/G2_review_round3.md`.
No formal Experiment A result is available yet. Publication remains authorized.

Execution-policy update D-38 supersedes D-37: restore K's two-day limit and
withdraw the full grid. Plan the reduced exploratory scope, freeze its candidate
grid and calibrate K with a pilot; retain its per-solve budgets. This does not
change A's quality checks or the currently applicable 36-hour A criterion.
See [COMPUTE_BUDGET.md](COMPUTE_BUDGET.md) for the estimated subtotal and unknowns.

## Round-3 implementation checklist

- [ ] Finish the fresh 240-case reference and combine the large/small production
  arms; require per-source mean loss <=0.02 and NIA<=20 loss <=0.01.
- [ ] If the large setting fails, test 2 workers / 60 s; stop if the fallback fails.
- [ ] Reproject A with a 15% margin and the M7 cap floors (D1 500, D2 200,
  all small D3 and at least 60 larger D3); reproject K without reducing solve budgets.
- [ ] Freeze the verified configuration, sample and code before starting A.
- [x] A1 implementation: household-by-2-m²-bin form/time decomposition with paired
  unit-bootstrap intervals, S2>S1 shares and stacked figure F4b.
- [ ] A2: after A, run the approved one-side double-bed sensitivity for all
  selected NIA<=20 units, H3/H4 and S0/S1/S2; keep main furniture defaults unchanged.
- [ ] B1: use only the footprint policy as the Exp. B greedy baseline; identify
  the portfolio only as CP-SAT initialization.
- [ ] A3: carry the separate time effect into K and the HK scenario reports.

The new configuration adds an inactive sensitivity declaration. Preserve the
pre-review benchmark configuration and explicitly verify that this declaration
is the only difference before transferring its pilot evidence to the main run.

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
- [ ] Write an evidence-backed self-review and publish only audited, accurately labelled artifacts.

The guarded runner and round-3 continuation are implemented. Nineteen targeted
acceptance, continuation, paired-statistics and launch-guard tests pass; dry-run
also passes. A1 output generation is gated on complete accepted A results. The
fresh reference is still running at this preparation snapshot; no accepted
production selection or formal A result is claimed here. The numerical solver
is unchanged from the 103-test regression baseline. The generated, dated
[round-3 status](G2_round3_status.md) distinguishes implementation from run completion.
