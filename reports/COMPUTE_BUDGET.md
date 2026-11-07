# Research execution budget

The author permits K to exceed two days (D-37). Preserve the planned full scope; no per-solve budget is reduced. The original short project timetable does not describe this full-grid budget.

| experiment   |   solves |    hours | basis                                                                                          |   days |
|:-------------|---------:|---------:|:-----------------------------------------------------------------------------------------------|-------:|
| A            |    32904 |   26.074 | measured pilot mean costs; conditional on quality acceptance                                   |  1.086 |
| A2           |     2148 |   37.459 | all selected small units, H3/H4, S0/S1/S2; full 120 s cap plus pilot overhead, not measured A2 |  1.561 |
| K_full       |    74049 | 1291.340 | planned full grid at 120 s cap plus pilot overhead, not measured K                             | 53.806 |

Quantified subtotal: **1354.873 hours / 56.453 days** of continuous serial use at the current concurrency. These budgets already include a 15% margin. A is pilot-calibrated; A2 and K use the full per-solve cap and are not measured run durations. The subtotal is neither a minimum nor a complete project ETA.

Still uncalibrated:

| experiment            | scope                                                                                        |
|:----------------------|:---------------------------------------------------------------------------------------------|
| B                     | 200 pairs: footprint greedy, simulated annealing and CP-SAT; optional LLM separate           |
| other_sensitivities   | drop-one items, clearance, walking width, raster resolution, solve budget and strict access  |
| C                     | four surrogate models and validation-only tuning; grids/runtime not yet calibrated           |
| D_R_HK                | reuse A layouts where applicable; R reproduction and kit-HK extensions need their own checks |
| analysis_and_delivery | FEA/adequacy/bootstrap analysis, literature, figures, rendering and review revisions         |

Plan at roughly a two-month scale if retaining full K, pending a K runtime pilot; do not promise a precise completion date from this table. Actual early stopping can shorten solves, while changed parametric domains, implementation, failures and review can extend the calendar.

## Review sequence

G2 round 3 §3 explicitly permits starting A without another stop if fresh hybrid quality and A runtime checks pass. If the prescribed fallback still fails, stop and report. This does not abolish later G3/G4 reviews. K's former two-day cap is superseded by D-37; method validation and the K pilot remain required.
