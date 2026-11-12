# Research execution budget

Historical A completed 32904 solves in 25.403 hours. Historical fixed-left A2 completed 2088 solves in 15.082 hours. The 2026-11-09 review supersedes H3/H4 main outcomes and the fixed-left A2 interpretation; these are not the runtime of the corrected experiments.

F1 corrected H3/H4 cases: 15714. Status: complete; recorded completed cases: 15714; measured hours when complete: 18.498068391575167. F2 full package passed: True. Small-home settings remain 120 seconds / four workers / three concurrent jobs; large-home settings remain 30 seconds / one worker / fourteen concurrent jobs. Nominal full solve-cap allocation: 31.311 hours, excluding geometry and validation overhead. This is neither measured remaining time nor a completion deadline.

F3 follows F1 and F2: the same 348 small units × H3 × three strategies = 1044 solves. Nominal full solve-cap allocation: 11.600 hours, excluding overhead. Current status: complete; recorded completed cases: 1044; measured hours when complete: 8.397508191707958; full package passed: True. The old fixed-left duration does not calibrate this mirrored run.

K follows D-39 and D-38: H1+H3, eight kits, 30 training shells, 15 held-out shells and 15 real plans; 2360 solves and historical count-based allowance 41.156 hours. H3 costs remain unmeasured. Freeze the grid and run its pilot; if it exceeds 48 hours, reduce training shells 30 → 24 → 18 before dropping H3. The full grid stays disabled.

B pilot status: complete; measured pilot hours: 0.1778124201002841. Full benchmark status: complete; 600/600 outputs in the dated snapshot 2026-11-12T02:58:24+00:00. Pilot-based full workload projection: 1.0423386198362439 parallel hours. 12 geometry-selected source/household pilot pairs, matched-stratum timing scaled by full-run concurrency; planning estimate, not a deadline or upper bound. Full stage reuses pilot checkpoints. Full-stage measured hours are available only after completion: 0.999104761001654. P1 analysis package passed: True.

Remaining ablations, C and reduced K still need runtime calibration. D/R/HK reuse validated corrected evidence where applicable. Full remaining experimental time is unknown. The former 10–14-day calendar estimate is retired; no arbitrary analysis-day reserve is added.

Execution order: F1 → F2 → F3 → B → D/R/ablations → C → K → HK → literature → G3. The review requires no additional intermediate reviewer stop. G3/G4 remain.
