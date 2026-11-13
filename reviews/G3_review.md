# Gate G3 review: results

**Reviewer:** Claude, 2026-11-13. **Package:** PR #2 (`codex/phase-11-g3-results`, commit 2c485be), plus the Phase 8–9 code already on `main` (B, D, R, ablation, C, K and HK runners).

**Verdict: APPROVED WITH REQUIRED CHANGES.** The evidence is accepted and PR #2 is merged as the record. Before G4, address the three **[must]** items in a follow-up PR (`codex/phase-11c-g3-fixes`). K1 changes what the K and HK-kit rows say. B1 changes how the solver benchmark is framed. None of the three needs new production solves of A, D, R, C or the ablations. After that PR is reviewed, continue to Phase 12.

## What I checked independently

| Item | Method | Result |
|---|---|---|
| D misclassification | Recomputed from `results/expA_f1/solutions.csv` (D1 + D2, n = 2,109) | All eight 30/45 m² rows and every 8 m² FP count match GATE_G3 exactly |
| C rank metrics | Recomputed Spearman from `results/expC/predictions.csv` | GraphSAGE D1 S0 0.087 / 0.142 / 0.588 / 0.661 and S2 0.088 / 0.223 / 0.479 / 0.588 match |
| C split | `results/expC/splits.csv` | 323 / 69 / 70 D1 groups; no group in two splits; D2 and D3 external. Labels use a train-only static curve, so no leakage |
| B against production | Joined `expB/cases.csv` to `expB/corrected_main_reference.csv` | See B1 below |
| K kit vs catalogue | Recomputed from `expK/confirmations.csv`, plain FCI and FCIq | Matches the report; see K1 below |
| Ablation recovery | Read the diff of `09_run_ablations.py` and `phase09_ablation_jobs.py` | Inheritance needs an identical config, a prior failed run of the recorded type and only the two documented script changes; anchor-adjusted triplets are always re-solved. Sound |
| Validator independence | `phase08_algorithms.Evaluator.checked`, `phase11_kit_validator.quality_metrics`, `phase11_hk_cases` | Annealing raises on any validator disagreement. FCIq is computed on top of `validate_layout`, with a check that FCIq ≤ validated FCI. HK reuse re-validates saved layouts and checksums |
| Figures | Viewed F10 and F12 | Readable and consistent with the tables |
| Tests | Could not re-run here (no network to install shapely, ortools or tqdm in this session) | Relied on `results/g3/test_receipt.json` (183 passed) |

The A primary results, P1 area labels, A_min, D, R, the ablations, C and the literature screening are accepted as reported.

## [must] items

### B1. Report the production pipeline in the solver benchmark

As reported, B makes the project's main solver look weakest: standalone CP-SAT has mean FCI 0.868, below annealing at 0.934. But B's CP-SAT arm is not the configuration that produced A. Production uses the greedy portfolio as a warm start and shares incumbents S0 → S1 → S2.

On the same 200 S2 pairs, the accepted production layouts score:

- mean FCI **0.943**, at or above annealing in 189 of 200 pairs;
- equal to the best value any method found in 189 of 200 pairs;
- a mean shortfall of **0.0034** FCI to the best-known value (11 pairs fall short; the largest gap is 0.23, on a D3 H2 shell).

Required changes:

- Add "production pipeline (portfolio warm start + shared incumbents)" as a fourth reference row in the B table and in GATE_G3, with its own runtime: the summed S0 + S1 + S2 solve time.
- Add paired differences of production minus each arm.
- State the finding plainly: CP-SAT alone, with a cold start, is weaker than annealing under these budgets. The hybrid is the strongest and is what A used.
- List the 11 pairs where production falls short. Say that A's FCI values are achievable lower bounds for those budgets, with a measured mean gap of 0.003.

This is also the honest answer to the reviewer question "why CP-SAT?" that the paper will face.

### K1. Score the catalogue with the same quality curve as the kit

The plan (RESEARCH_PLAN §5.9) defines q as rising from an item's minimum usable size to its recommended size. That curve should apply to every item of a given type, including catalogue items. The run instead fixes catalogue q = 1 ("Catalogue service quality is one").

Under the configured curves, the catalogue's own dimensions score:

| Item | Catalogue size | q under the configured curve |
|---|---|---|
| Fold-down desk | 1.0 × 0.55 m | 0.9 |
| Drop-leaf table | 0.8 × 0.75 m | 0.9 |
| Wall beds | 1.0 m single, 1.5 m double | 1.0 |
| Wardrobe | 1.0 m frontage | 1.0 storage unit, unchanged |

So the comparison is asymmetric, and the bias runs against the kit. The kit search could not reach the catalogue's score even by choosing the catalogue's own dimensions, because the kit is penalised at 0.9 for those sizes while the catalogue is not. This plausibly explains why the H3 kit picked a larger desk, table and wardrobe and still lost.

The HK S2-kit rows inherit the same asymmetry.

Required changes:

1. Rescore every saved catalogue K layout (S0, S1 and S2; train, held-out and real) and every HK catalogue layout with `quality_metrics`, using the catalogue dimensions' q values.
2. Also re-solve catalogue S2 with `solve_quality` on the K cohorts, warm-started from the existing catalogue layouts with the same chain and budget as the kit. The catalogue then gets the same FCIq optimisation as the kit. Report both the rescored and the re-optimised values. The rescored value is a lower bound for the catalogue.
3. The catalogue vector (1.0 or 1.5, 1.0, 0.55, 0.8, 0.75, 1.0) lies in the configured design grid but was not one of the eight maximin vectors. Add it as a ninth candidate in the selection ranking at the 30-shell stage, using the step 2 results. If it ranks first, the selected kit is the catalogue: say so, because that is a finding. Do the same for the bespoke comparator, so bespoke is never below the catalogue on a shell by construction.
4. Regenerate the K table, F12 if the selection changes, the HK S2-kit rows, F10, the H4-hypothesis row in GATE_G3 and the bespoke-share column.

Keep the current q = 1 numbers as a labelled sensitivity ("catalogue credited at full quality").

### K2. Keep the K conclusion open until K1 is done

Do not carry the sentence "the H4 hypothesis is unsupported" forward to G4 until K1 is rerun. Whatever the outcome, report the size–quality trade-off that the data already show, from the confirmations:

| Household | Cohort | Plain FCI: catalogue | Plain FCI: flat-quality kit |
|---|---|---|---|
| H1 | Train | 0.727 | 0.749 |
| H1 | Held out | 0.724 | 0.769 |
| H3 | Train | 0.657 | 0.668 |
| H3 | Held out | 0.724 | 0.746 |

Smaller furniture buys coverage and pays for it in quality. Tabulate plain FCI against mean q for all eight vectors (and the catalogue vector) at the 30-shell stage, as a frontier. That gives a design result whichever way K1 lands.

## [should] items

- **HK time effect for couples.** The H3 S0 crossing lies outside 8–20 m², but S1 (16.91 m²) and S2 (14.43 m²) are both identified. Report ΔA_min(S1 → S2) for H3 with a paired bootstrap interval. This is the cleanest equivalent-area estimate of switching itself, and it falls in the HK size range.
- **C as a screen.** Labels are saturated: 46–98% of D1 test FCI labels equal 1. Add a clearly labelled post-hoc secondary metric: AUC for adequacy (FCI ≥ 0.95). My recomputation gives GraphSAGE versus area-only AUCs on D1 S0 of 0.80 vs 0.73 (H3) and 0.89 vs 0.82 (H4). The prespecified ρ ≥ 0.80 verdict stays "not supported"; do not replace it.
- **Pooled H2 ΔA_min (6.32 m²).** The S2 crossing at 8.27 m² sits at the lower support edge, and too few bootstrap fits succeed to give an interval. Mark it as boundary-limited and don't headline it. D3's 3.63 m² [2.78, 4.77] is the usable H2 estimate.
- **8 m² rule.** Say in one sentence that no real plan falls below 8 m² NIA, so this comparison is informative only for the D3 and HK shells.

## Notes for the paper (no action now)

- The headline story holds:
  - most real plans are already fully functional with static furniture;
  - the gains concentrate in two-person households in about 12–30 m²;
  - for parent and child, form dominates; for couples, form and switching matter about equally;
  - fixed area thresholds misclassify about half of two-person cases, mostly by rejecting plans that function.
- The literature positioning is adequate. Zeng et al. (SBF) and Bu & Che Mat are the closest antecedents; cite both, as Codex proposes. Q34 is answered by this review: adopt the proposed citations and the "what this study adds" wording.

## Merge record

PR #2 merged into `main` on 2026-11-13 (254f456). The follow-up PR for B1, K1 and K2 will be reviewed separately.
