# G2 round-3 implementation and status

Observed: 2026-11-08T15:52:23+00:00

The reviewer conditionally approves Phase 7. The author requests implementing this review. Main runs keep the two-side double-bed clearances; the approved one-side variant is A2 only. Review files are unchanged.

## Fresh pilot and continuation

| arm                          |   expected_cases |   saved_checkpoints |   completed_validated_cases | status   |
|:-----------------------------|-----------------:|--------------------:|----------------------------:|:---------|
| refresh_large_w1_s20_t30     |              240 |                 240 |                         240 | complete |
| refresh_small_w4_s10_t120    |               36 |                  36 |                          36 | complete |
| refresh_reference_w8_s10_t60 |              240 |                 240 |                         240 | complete |

Execution stage: `stopped_A_solve_acceptance_failed`. Formal A has started; see its run/progress records. Checkpoints are not completed-arm acceptance. No partial score means are reported.

The continuation checks the source means, small-home mean, current code/configuration and measured runtime. It tries 2 workers / 60 s only for the reviewed larger-home quality fallback. Failed conditions stop A. Passing conditions launch the guarded A runner without another review stop, then generate A1 only after the complete A table passes solve acceptance.

## Runtime evidence

A under the measured candidate setting: 26.073873 projected hours including 15% margin; caps: []. This remains conditional on the hybrid quality comparison. Source/size cost calibration is in `expA_cost_calibration.csv`; absent small-source pilot cells use the full solve cap plus observed overrun.

K uses the approved 120 s small-home budget, including full S0/S1/S2 evaluations for the time effect. The table is a conservative workload projection, not observed K runtime:

| scope                                                |   total_solves |   projected_hours_with_margin | within_48h   | selected_for_planning   |
|:-----------------------------------------------------|---------------:|------------------------------:|:-------------|:------------------------|
| also_drop_H3                                         |          22606 |                       394.226 | False        | False                   |
| drop_wardrobe_frontage                               |          33909 |                       591.339 | False        | False                   |
| exploratory_8_kits_30_train_15_holdout_15_real_H1_H2 |           2360 |                        41.156 | True         | True                    |
| full_grid                                            |          74049 |                      1291.340 | False        | False                   |

K has not started. D-38 restores the two-day limit and withdraws the full grid. Plan the previously reported eight-kit exploratory scope: H1/H2, 30 training shells, 15 held-out shells and 15 real plans. Freeze the candidate grid and confirm cost in a K pilot. Per-solve budgets remain unchanged; the full-grid row is a rejected historical alternative.

## Implementation and remaining work

- 19 targeted acceptance, continuation, launch-guard and paired-statistics tests pass. Numerical solver logic is unchanged.
- A1 is implemented: paired form/time/total effects, S2>S1 shares, household × 2 m²-bin means, 1,000 unit-bootstrap resamples and 95% intervals. Source-specific tables accompany pooled tables. Single-unit bins have no CI. F4b uses stacked effects and separate form/total intervals; time intervals are in the table.
- The F4b renderer was checked visually on completed pilot pairs in private scratch output; this is not a formal A figure or result.
- A2 runs after A on every selected NIA<=20 unit, H3/H4, S0/S1/S2, retaining the small-home budget. It has not run. Main furniture defaults remain unchanged.
- B1 is retained as a requirement for the future Exp. B runner: call the footprint policy alone; do not label the CP-SAT initialization portfolio as that baseline.
- A3 requires the separate time effect in K and HK. Remaining Phase 7 FEA/adequacy analysis, layout review and literature screening are still due.

## Reproduce

`python scripts/06_round3_continue.py --launch-expA` waits for the already-launched fresh pilot queue, verifies acceptance and stops on unsupported conditions. `python scripts/06_round3_status.py` refreshes this snapshot. `python scripts/07_decomposition.py` requires complete accepted A results.

The preserved benchmark configuration and the new approved project configuration are included. Their only difference is the inactive A2 declaration; no completed benchmark was silently relabelled with a new hash.
