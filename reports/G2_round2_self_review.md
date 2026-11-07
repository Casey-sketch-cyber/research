# G2 round-2 self-review (in progress)

The author delegates continuation and self-review and has paused uploads. This file is an engineering self-review, not a replacement for the immutable reviewer records.

## Wall-flush lattice correction

Stride is applied along the wall only for wall-backed furniture. Perpendicular flush coordinates remain eligible. Free-standing items still use both axes. Translated-wall tests exercise all four orientations.

Arm `r2_wallflush_w1_s20_t30` completed 240 cases in 165.201 s; all 240 layouts pass independent validation. Mean FCI is 0.908132618.

| group   |   cases |   mean_fci |   reference_mean |   difference |   allowed_loss | passes   |
|:--------|--------:|-----------:|-----------------:|-------------:|---------------:|:---------|
| D1      |      96 |   0.944365 |         0.956454 |    -0.012089 |       0.020000 | True     |
| D2      |      72 |   0.970899 |         0.959809 |     0.011091 |       0.020000 | True     |
| D3      |      72 |   0.797056 |         0.797202 |    -0.000146 |       0.020000 | True     |
| NIA<=20 |      36 |   0.621890 |         0.636884 |    -0.014994 |       0.010000 | False    |

The full-anchor reference is the frozen earlier benchmark. At stride 0.10 m the wall correction is an identity; no full-anchor candidate changes. Numerical comparisons are provisional until R1 search checks finish. Positive differences are finite-budget outcomes, not dominance of a coarse domain.

## Known-answer diagnostic fixtures

Three hand-built rectangles have 9, 11 and 13 m² NIA. Each has a synthetic 0.8×0.8 m fixed pod and 0.4×0.6 m kitchen obstacle, deliberately separate from the D3 dwelling generator. These are algorithmic diagnostics, not habitable minimum dimensions or study-population observations. They must not enter A, K, minimum-area estimates or policy claims.

The hand-written table's deployed body intersects the bed's night footprint. The six schedules pass the independent validator, and fixing their poses/states yields feasible CP models. Simultaneous deployment and S1 relabelling are rejected. H1 cannot claim sleep_1 from the requested sleep_2 bed under the unchanged capability rules; its lower bound explicitly omits sleep. H3 exercises the sleep/lounge transformation mechanism.

| unit_key     |   nia_m2 | household            |   lower_bound |       tb | validator_pass   | h1_sleep2_does_not_satisfy_sleep1   | population_eligible   |
|:-------------|---------:|:---------------------|--------------:|---------:|:-----------------|:------------------------------------|:----------------------|
| mechanism:9  |        9 | H1_single_commuter   |      0.470899 | 2.800000 | True             | True                                | False                 |
| mechanism:9  |        9 | H3_couple_one_remote |      0.917577 | 2.800000 | True             | False                               | False                 |
| mechanism:11 |       11 | H1_single_commuter   |      0.523810 | 2.800000 | True             | True                                | False                 |
| mechanism:11 |       11 | H3_couple_one_remote |      0.936808 | 2.800000 | True             | False                               | False                 |
| mechanism:13 |       13 | H1_single_commuter   |      0.576720 | 2.800000 | True             | True                                | False                 |
| mechanism:13 |       13 | H3_couple_one_remote |      0.956038 | 2.800000 | True             | False                               | False                 |

Unconstrained searches never receive these witnesses as incumbents. Fixed-pose model tests establish expressiveness only, not search success.

## Completed search diagnostics

| arm                     | mode      |   completed_cases |   mean_s1 |   mean_s2 |   s2_improved_pairs |   s2_below_witness |   wall_time_s |
|:------------------------|:----------|------------------:|----------:|----------:|--------------------:|-------------------:|--------------:|
| mechanism_probe_w4_t120 | mechanism |                 2 |  0.725269 |  0.725269 |                   0 |                  1 |    226.225759 |

## Remaining acceptance checks

- All six S2 diagnostic searches must reach their hand-written lower bounds; at least one diagnostic shell must have S2>S1.
- Freeze and solve every pilot NIA<=22 plus 12 seed-selected D3 shells of 9–15 m²; use full anchors / 8 workers / 300 s for S1/S2 and all four households.
- Select the size-dependent setting by the predeclared mean criteria; rerun any benchmarks affected by a search correction.
- Reproject A and K; do not start formal A based on the superseded median rule.

Reproduce: `python scripts/06_round2.py --mode prepare`; use the explicit mode/arm/worker/limit arguments in each run.json; `python scripts/06_round2_report.py --render`.
