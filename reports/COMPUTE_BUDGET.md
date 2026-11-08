# Research execution budget

D-38 supersedes D-37: the author restores K's two-day budget and withdraws the full grid. Plan the previously reported reduced exploratory scope: H1/H2, eight kits, 30 training shells, 15 held-out shells and 15 real plans. Freeze the candidate grid and confirm runtime before execution; per-solve budgets are unchanged. The rejected full-grid budget is excluded from the active subtotal.

| experiment            |   solves |   hours | basis                                                                                          |   days |
|:----------------------|---------:|--------:|:-----------------------------------------------------------------------------------------------|-------:|
| A                     |    32904 |  26.074 | measured pilot mean costs; conditional on quality acceptance                                   |  1.086 |
| A2                    |     2148 |  37.459 | all selected small units, H3/H4, S0/S1/S2; full 120 s cap plus pilot overhead, not measured A2 |  1.561 |
| K_reduced_exploratory |     2360 |  41.156 | active planned scope at 120 s cap plus pilot overhead, not measured K                          |  1.715 |

Quantified subtotal: **104.689 hours / 4.362 days** of continuous serial use at the current concurrency. These budgets already include a 15% margin. A is pilot-calibrated; A2 and K use the full per-solve cap and are not measured run durations. The subtotal is neither a minimum nor a complete project ETA.

Still uncalibrated:

| experiment            | scope                                                                                        |
|:----------------------|:---------------------------------------------------------------------------------------------|
| B                     | 200 pairs: footprint greedy, simulated annealing and CP-SAT; optional LLM separate           |
| other_sensitivities   | drop-one items, clearance, walking width, raster resolution, solve budget and strict access  |
| C                     | four surrogate models and validation-only tuning; grids/runtime not yet calibrated           |
| D_R_HK                | reuse A layouts where applicable; R reproduction and kit-HK extensions need their own checks |
| analysis_and_delivery | FEA/adequacy/bootstrap analysis, literature, figures, rendering and review revisions         |

## Remaining experimental compute time

A has no usable remaining runtime estimate. A failed final acceptance requires a repair/revalidation budget; an overrun or resumed run also requires recalibration. No complete remaining subtotal is claimed.

| experiment            |   remaining_hours | basis                                                                                          |
|:----------------------|------------------:|:-----------------------------------------------------------------------------------------------|
| A                     |           nan     | measured pilot mean costs; conditional on quality acceptance                                   |
| A2                    |            37.459 | all selected small units, H3/H4, S0/S1/S2; full 120 s cap plus pilot overhead, not measured A2 |
| K_reduced_exploratory |            41.156 | active planned scope at 120 s cap plus pilot overhead, not measured K                          |

D-40 withdraws the earlier 10–14-day calendar ETA as an active forecast: it included an unmeasured 5–9-day development/analysis reserve and was not experimental compute time. No fixed analysis-day surcharge is added here. Prepare analysis and figures alongside runs when resources and completed evidence permit, while retaining validation.

The subtotal covers A, A2 and reduced K only. Algorithm comparisons, surrogate training and other sensitivities still need runtime calibration; the complete experimental total remains unknown. Statistical D/R/HK work reuses A results where valid. Do not present the subtotal as a promise that every experiment will finish within that time.

Do not interpret this partial subtotal as the whole project's delivery date. Actual early stopping can shorten solves, while changed parametric domains, implementation, failures and review can extend the calendar. K's reduced scope is exploratory, with limited household and design-grid coverage; report those limits.

## Review sequence

G2 round 3 §3 explicitly permits starting A without another stop if fresh hybrid quality and A runtime checks pass. If the prescribed fallback still fails, stop and report. This does not abolish later G3/G4 reviews. The active K budget follows config/execution_policy.yaml; method validation and the K pilot remain required.
