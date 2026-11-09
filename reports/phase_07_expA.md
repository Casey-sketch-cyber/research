# Phase 7 — Experiment A

## Phase-7 review implementation plan

The author instructs continuation under `reviews/phase07_review.md` (d81e411).
No A re-solve or geometry repair is authorized or needed for this response.
Preserve the original failed solve acceptance; create a separate, outcome-independent
evaluability list and an explicit analysis acceptance record.

- [x] E1: evaluate every frozen unit using the empty main raster at 0.60 m walking width;
  require all fixed-service targets reachable and at least half of raster-furnishable
  area covered or reachable within an additional 0.60 m clearance depth.
  Clearance expansion must stay in free cells and not jump through walls.
- [x] E2: select 20 excluded units with the fixed seed, draw empty raster, source geometry,
  entrance, walking coverage and failed targets; inspect and classify causes without repair.
- [x] E3: compare excluded/retained NIA, room count and source mix; publish tables and histogram.
- [x] E4: require complete valid 4-household × 3-strategy records for every evaluable unit,
  enforce whole-unit exclusions matching E1 and strict strategy ordering.
- [x] Generate A1 FEA, f0 curves, saving curves, adequate-area estimates and bootstrap
  intervals, paired tests, form/time decomposition and fixed-seed showcases.
- [x] S1: show real plans (D1+D2), designed shells (D3) and pooled evidence separately.
- [x] Run the approved A2 one-side double-bed sensitivity after A1.
- [ ] Continue B, D/R/ablations, C, reduced K, HK and literature screening in review order;
  prepare G3 without an intervening review stop.

K follows the current H1+H3 execution policy with the two-day budget. If its pilot
exceeds that budget, reduce training shells 30 → 24 → 18 before dropping H3.
The duplicate D-39 identifiers are disambiguated by date and phase in QUESTIONS.

Status: Original A solves are complete with failed raw solve acceptance preserved.
Following the phase-7 review, E1--E4 and A1 now pass their separate analysis-package acceptance (2619 evaluable units, 31428 valid cases). A2 completed all 348 evaluable small units / 2088 cases and passed solve acceptance. The paired form/time comparison and independent saved-layout audit also pass; see [A2 completion and limitations](phase_07_A2.md).
See [the review response](phase07_review_response.md) for evidence and the H4 catalogue-ceiling, censoring and fitted-crossing limits.
The earlier continuation stop is historical. See the generated
[completion audit](expA_completion_audit.md) for counts, measured runtime and
the exact match to previously recorded full-sample connectivity failures.
The fresh-pilot acceptance below remains launch evidence, not final A acceptance.
No population-level finding is claimed.

Execution-policy update D-38 supersedes D-37: restore K's two-day limit and
withdraw the full grid. Plan the reduced exploratory scope, freeze its candidate
grid and calibrate K with a pilot; retain its per-solve budgets. This does not
change A's quality checks or the currently applicable 36-hour A criterion.
See [COMPUTE_BUDGET.md](COMPUTE_BUDGET.md) for the estimated subtotal and unknowns.

## Round-3 implementation checklist

- [x] Finish the fresh 240-case reference and combine the large/small production
  arms; require per-source mean loss <=0.02 and NIA<=20 loss <=0.01.
- [x] The original large setting passes; the 2-worker/60-second fallback was not required.
- [x] Reproject A with a 15% margin and the M7 cap floors (D1 500, D2 200,
  all small D3 and at least 60 larger D3); reproject K without reducing solve budgets.
- [x] Freeze the verified configuration, sample and code before starting A.
- [x] A1 implementation: household-by-2-m²-bin form/time decomposition with paired
  unit-bootstrap intervals, S2>S1 shares and stacked figure F4b.
- [x] A2: after A, run the approved one-side double-bed sensitivity for all
  selected NIA<=20 units, H3/H4 and S0/S1/S2; keep main furniture defaults unchanged.
- [ ] B1: use only the footprint policy as the Exp. B greedy baseline; identify
  the portfolio only as CP-SAT initialization.
- [ ] A3: carry the separate time effect into K and the HK scenario reports.

The new configuration adds an inactive sensitivity declaration. Preserve the
pre-review benchmark configuration and explicitly verify that this declaration
is the only difference before transferring its pilot evidence to the main run.

## Checklist

- [x] Freeze the final production settings and any authorized sample cap using
  the round-2 mean-quality rules; retain every small D3 shell.
- [x] Run the final frozen sample × four households × S0/S1/S2, resuming only
  identical code, input and configuration fingerprints; respect the total CPU budget.
- [x] Revalidate every layout and strategy exchange; report zero-service,
  time-limit, invalid and ordering rates without hiding failures.
- [x] Fit household-specific pooled and source-specific isotonic S0 curves on
  NIA, the primary area axis specified by the G1 review.
- [x] Compute FEA, saving and relative saving with explicit right-censoring;
  never extrapolate unsupported equivalent areas.
- [x] Estimate 2 m²-bin saving curves and unit-bootstrap 95% intervals using
  1,000 resamples, with clear reporting of excluded censored values.
- [x] Estimate logistic minimum-adequate areas at tau=0.95 and sensitivity
  thresholds 0.90/1.00; flag unidentifiable or out-of-support crossings.
- [x] Report paired S2−S0 and S2−S1 tests and effect sizes by household.
- [x] Export fixed-seed example layouts and approximately 10/18/30 m² H3
  showcases; inspect the actual drawings.
- [ ] Complete the remaining literature screening and evidence limits before G3.
- [ ] Write an evidence-backed self-review and publish only audited, accurately labelled artifacts.

The guarded runner and round-3 continuation are implemented. Nineteen targeted
acceptance, continuation, paired-statistics and launch-guard tests pass; dry-run
also passes. A1 output generation is now gated on complete accepted evaluable A records under E1/E4. The
fresh reference and launch acceptance are complete. A finished its solves and
failed original final acceptance; all outputs and production settings are preserved. The reviewed evaluability and A1 package gates subsequently passed.
The numerical solver is unchanged from the 103-test regression baseline. The generated, dated
[round-3 status](G2_round3_status.md) distinguishes implementation from run completion.


<!-- ROUND3_ACCEPTANCE_BEGIN -->
## Measured round-3 acceptance

Status: PASS — authorized to start A without another review stop.

| group   |   cases |   mean_fci |   reference_mean |   mean_difference |   allowed_loss | passes   |
|:--------|--------:|-----------:|-----------------:|------------------:|---------------:|:---------|
| D1      |      96 |   0.952750 |         0.958638 |         -0.005889 |       0.020000 | True     |
| D2      |      72 |   0.971485 |         0.975529 |         -0.004045 |       0.020000 | True     |
| D3      |      72 |   0.811772 |         0.810703 |          0.001068 |       0.020000 | True     |
| NIA<=20 |      36 |   0.648676 |         0.645878 |          0.002798 |       0.010000 | True     |

All 516 saved pilot layouts revalidate independently. The numerical implementation and input hashes match the current frozen code and pilot. The preserved configuration differs from the production configuration only by the inactive A2 declaration; see `results/pilot/round3/config_transition.json`.

Exp. A: 2742 units, 32904 solves, 26.073873 projected hours including a 15% margin. Caps: []. Small sources absent from the pilot use the full 120 s cap plus observed overrun, rather than borrowing an easier source's mean. This is a measured-pilot projection, not a runtime guarantee.

Separate K workload projections (not observed K runtimes):

| scope                                                |   total_solves |   projected_hours_with_margin | within_48h   | selected_for_planning   |
|:-----------------------------------------------------|---------------:|------------------------------:|:-------------|:------------------------|
| also_drop_H3                                         |          22606 |                       394.226 | False        | False                   |
| drop_wardrobe_frontage                               |          33909 |                       591.339 | False        | False                   |
| exploratory_8_kits_30_train_15_holdout_15_real_H1_H2 |           2360 |                        41.156 | True         | True                    |
| full_grid                                            |          74049 |                      1291.340 | False        | False                   |

D-38 restores the two-day K limit and withdraws the full grid. Planned scope: `exploratory_8_kits_30_train_15_holdout_15_real_H1_H2`, projected at 41.156 hours including margin. It is exploratory, with H1/H2 only, eight candidate kits, 30 training shells, 15 held-out shells and 15 real plans. The candidate grid must be frozen and a K pilot must confirm runtime before execution. Per-solve budgets are unchanged; K has not started. Evaluation counts include S0/S1/S2 for the separate time effect.

Formal A outputs are not supplied by this acceptance report. A1 analysis requires a complete accepted A table. A2 remains a separate subsequent experiment with the main two-side defaults preserved.
<!-- ROUND3_ACCEPTANCE_END -->


<!-- EXPA_PROGRESS_BEGIN -->
## Dated formal-run progress

Observed 2026-11-08T16:42:47+00:00; run began 2026-11-07T08:43:57+00:00.

Status: complete. Completed solve cases: 32904/32904 (100.00%). Active group: large, 28608/28608 cases. Elapsed: 25.403 h. These are completion counts, not a final all-layouts-pass acceptance.

Final solve acceptance: False. Separate analysis package accepted: True. Repair/revalidation runtime pending: False. See the completion audit when present.

The accepted prior A projection is 26.074 h. The case prefix is not representative of the remaining workload; do not convert its overall completion percentage into a linear ETA. No partial score means or final research conclusions are reported.
<!-- EXPA_PROGRESS_END -->
