# Research execution budget

Historical A completed 32,904 solves in 25.403 hours. Historical fixed-left A2 completed 2,088 solves in 15.082 hours. The November 9 review supersedes H3/H4 main outcomes and the fixed-left A2 interpretation. These are historical execution times.

F1 completed 15,714 corrected H3/H4 solves in 18.498 hours; the combined 31,428-case dataset passed validation. F3 completed 1,044 new solves in 8.398 hours. The respective nominal solve-cap allocations were 31.311 and 11.600 hours, excluding preparation and validation. The F2 and P1 analysis packages both passed.

| Accepted phase | Measured elapsed | Work included |
| --- | --- | --- |
| [B](phase_08_B_results.md) | 0.178 h pilot; 0.999 h full stage | The full stage reused pilot checkpoints; 600 outputs on 200 matched cases |
| [D](phase_09_D_results.md) | 3.296 s | Reused corrected evidence for 10,476 unit–household pairs |
| [R](phase_09_R_results.md) | 640.830 s | 16 approximate room reproductions and 10,476 main layout checks |
| [Ablations](phase_09_ablation_results.md) | 6.156 h initial; 0.708 h resumed | 14,835 layouts; initial attempt stopped at the coarse grid/anchor mismatch; 4,725 unchanged triplets were verified and reused |
| [C](phase_10_C_results.md) | 25.993 s | Grouped surrogate evaluation and evidence exports |
| [Reduced K](phase_11b_K_results.md) | 11.360 h including pilot | 1,803 layouts; retained 30 training shells, 15 held-out shells and 15 real plans per household |
| [Hong Kong](phase_11_HK_results.md) | 8.793 h | 4,290 validated layout records across 390 shell templates; reused eligible corrected catalogue and kit evidence |

The 16-layout K pilot took 0.147 h and projected 30.39 h at the retained scope. The measured K run remained within the 48-hour cap. The full K grid stays disabled. The measured times cover the stated phases and exclude reviewer turnaround. The former 10–14-day calendar estimate was retired.

F1, F2, F3, B, D, R, ablations, C, reduced K, the Hong Kong scenario and the retrieved literature screening are complete. The consolidated [G3 package](GATE_G3.md) is ready for results review.

## G3 review follow-up

Catalogue rescoring and 120 quality-aware K S2 optimizations took 0.810 h. The nine-vector selection and confirmations took 0.01 min, including 0 new kit confirmation solves. The revised Hong Kong scenario took 4.524 h with 517 fresh S2 solves on the fixed shell grid. The B reference and C AUC use existing evidence. [Review response](GATE_G3_response.md)
