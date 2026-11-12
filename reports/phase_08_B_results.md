# Phase 8 — Algorithm comparison results

## Completed benchmark

The frozen 200 S2 pairs produced 600 algorithm outputs. All outputs were independently rescored from saved layouts; invalid outputs remain included with their validator score (zero). Three algorithms share candidate generation and the corrected main configuration. Measured wall time is 0.177812 hours for the pilot and 0.999105 additional hours for the full stage (sum 1.176917 hours). The full stage reuses identical pilot checkpoints; individual runtime statistics retain each actual execution once.

| algorithm           |   n_cases |   validity_rate |   mean_fci |   median_fci |   mean_preparation_s |   mean_algorithm_s |   mean_elapsed_s |   median_elapsed_s |
|:--------------------|----------:|----------------:|-----------:|-------------:|---------------------:|-------------------:|-----------------:|-------------------:|
| cp_sat              |       200 |        1.000000 |   0.867511 |     0.961538 |             0.315175 |          38.119107 |        38.450935 |          30.440822 |
| greedy_footprint    |       200 |        1.000000 |   0.861199 |     1.000000 |             0.309126 |           3.146633 |         3.465412 |           1.944071 |
| simulated_annealing |       200 |        1.000000 |   0.934115 |     1.000000 |             0.291123 |         103.815537 |       104.118149 |         108.328061 |

## Paired FCI comparisons

| comparison                                 |   n_pairs |   mean_difference |     ci_lo |     ci_hi |   share_better |   share_worse |   bootstrap_resamples | resampling                                                            |
|:-------------------------------------------|----------:|------------------:|----------:|----------:|---------------:|--------------:|----------------------:|:----------------------------------------------------------------------|
| cp_sat minus greedy_footprint              |       200 |          0.006312 | -0.026349 |  0.035622 |       0.330000 |      0.415000 |                  1000 | Physical-unit clusters within source; all sampled households retained |
| cp_sat minus simulated_annealing           |       200 |         -0.066604 | -0.088359 | -0.048521 |       0.070000 |      0.575000 |                  1000 | Physical-unit clusters within source; all sampled households retained |
| simulated_annealing minus greedy_footprint |       200 |          0.072916 |  0.054138 |  0.093134 |       0.415000 |      0.000000 |                  1000 | Physical-unit clusters within source; all sampled households retained |

## Settings, timing and scope

The greedy arm runs only descending-footprint, first-improving feasible wall-adjacent placement and exhausts its scan. Annealing runs all 20000 proposals × 3 restarts, initialized only by standalone greedy; its initialization is included in its own runtime. The penalty and geometric temperature schedule were frozen before B outcomes. Every new best found by fast scoring and every final output is independently validated. CP-SAT uses its normal internal initializer and the unchanged per-unit small/large budgets; no saved A/F1/F3 layout is supplied.

Each algorithm receives separately rebuilt raster/candidate inputs. Preparation, algorithm and final validation time are reported separately; runtime_s includes all three plus saving overhead. Times are observed under the recorded concurrent benchmark, not isolated latency measurements. Source, household and budget-group summaries are in algorithm_summary.csv. The original 200 pairs balance 36 strata, so the pooled mean describes this benchmark rather than a population-weighted housing stock.

Fresh standalone CP-SAT differs from historical shared-strategy main evidence in 112 pairs; 112 are lower. Preserve these differences: historical A used preceding/shared-strategy incumbents, whereas B measures fresh standalone S2. Corrected main references are retained for traceability, not substituted into B scores or used as baseline starting answers.

This completes B numerical and saved-output checks; the remaining D/R/ablations, C, K, HK and literature work still precedes G3. Reproduce with scripts/08_continue_expB.py followed by scripts/08_report_expB.py.
