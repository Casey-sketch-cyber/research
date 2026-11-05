# Deliverables and Review Protocol

What Codex must push to this repository, in what form, and how review works. The reviewer (Claude, working with the human author) reads **only what is in the repository**. If something isn't pushed, it can't be reviewed.

## 1. General rules

- **Never commit raw or interim data.** `data/raw/` and `data/interim/` are git-ignored. Commit small derived tables only (each file < 50 MB; prefer CSV for anything a reviewer reads).
- **Every number must be reproducible** by a committed script from committed configs. No hand-edited result files.
- **Commit messages:** `phase-NN: <what>`, for example `phase-06: CP-SAT solver + validator, pilot results`.
- **Push at the end of every phase**, and at least once per working day during long runs (partial aggregates are fine if clearly marked `PARTIAL` in the file name or report).
- **Figures:** PNG at 300 dpi plus PDF, produced by scripts, with axis labels and units.
- **Failures are deliverables too.** If something didn't work, the report says what, why, and what was done instead.

## 2. Per-phase reports

After each phase, add `reports/phase_NN_<name>.md` using `reports/TEMPLATE_phase_report.md`. Mandatory sections:

1. What was done, as a checklist mirroring PROCEDURES.md
2. Acceptance checks, each PASS or FAIL with evidence (a file path or number)
3. Key numbers
4. Deviations from the plan, and why
5. Decisions made, which are also appended to `reports/DECISIONS.md`
6. Open questions for the reviewer
7. Runtime and resources used

## 3. Required result files (CSV schemas)

| File | Columns |
|---|---|
| `results/corpus/corpus_units.csv` | unit_key, source, group_id, gross_area_m2, furnishable_area_m2, n_rooms, n_windows, n_doors, aspect_ratio, compactness, include, exclude_reason |
| `results/furniture/abo_dimension_check.csv` | item, config_w, config_d, abo_type, n, median_w, median_d, iqr_w, iqr_d, flag |
| `results/pilot/pilot_solutions.csv` and `results/expA/solutions.csv` | unit_key, source, furnishable_area_m2, household, strategy, algorithm, status, fci_validator, fci_solver, tb, n_items, served_hours, demanded_hours, solve_time_s, reach_iterations, objective, bound, validator_pass, n_violations |
| `results/expA/fea.csv` | unit_key, source, household, area_m2, fci_S0, fci_S1, fci_S2, fea_m2, saving_m2, saving_rel, right_censored |
| `results/expA/area_saving_curve.csv` | household, pooling (pooled/D1/D2/D3), area_bin_lo, area_bin_hi, n, median_saving_m2, ci_lo, ci_hi, median_saving_rel, rel_ci_lo, rel_ci_hi |
| `results/expA/min_adequate_area.csv` | household, strategy, tau, a_min_m2, ci_lo, ci_hi, delta_vs_S0_m2 |
| `results/expA/tests.csv` | comparison, household, n, median_diff, statistic, p_value, effect_size |
| `results/expB/instances.csv`, `results/expB/algorithms.csv` | unit_key, household, algorithm, valid, n_violations, violation_types, fci_validator, runtime_s |
| `results/expC/metrics.csv` | model, target, household, test_set, mae, rmse, r2, spearman, infer_ms_per_unit |
| `results/expC/predictions.csv` | unit_key, household, test_set, target, y_true, y_pred_<model>… |
| `results/expD/correlations.csv`, `results/expD/dispersion.csv`, `results/expD/confusion.csv` | as described in PROCEDURES Phase 9 |
| `results/expR/source_values.csv` | quantity, value, unit, page, section, note |
| `results/expR/reproduction.csv` | shell_id, aspect_ratio, household, strategy, free_activity_area_day_m2, gain_m2, gain_rel, reported_value_m2, reported_gain_rel |
| `results/expR/generalization.csv`, `results/expR/bridge.csv` | unit_key, source, nia_m2, aspect_ratio, compactness, household, free_area_day_S0_m2, free_area_day_S2_m2, gain_rel, saving_rel_fea |
| `results/ablations/*.csv` | ablation, value, n, median_fci_S2, median_saving_m2, delta_a_min_m2 |
| `results/scenario_hk/*.csv` | area_m2, household, strategy, adequate_share, a_min, plus district weights if available |
| `results/tables/T1..T7.(csv,md)` | — |
| `results/literature/raw_hits.csv` (task L) | rec_id, doi, title, year, venue, type, authors_first3, sources, query_ids, cited_by, abstract_available, url |
| `results/literature/screened.csv` (task L) | rec_id, doi, title, year, venue, stage1, stage2, claim_affected, note, fulltext_checked |
| `results/figures/F1..F10.(png,pdf)` | — |
| `results/figures/F3b_<unit>.(png,pdf)` | 3D render grid: S0/S2 × night/day/dinner (Phase 12b) |
| `results/renders3d/stills/*.png`, `results/renders3d/scenes/*.json`, `results/renders3d/animation.(mp4,gif)` (optional) | 3D stills, their scene descriptions, and the optional transformation animation; each file < 50 MB |

Layout renderings to commit:

- **All pilot renders** (Phase 6)
- **F3 showcase renders**
- **24 randomly sampled Exp. A renders** (fixed seed), in `results/layouts/sample/`

Don't commit every layout JSON. Commit only the pilot and sample JSONs (`results/layouts/**/*.json`).

## 4. Gate packages

At each gate, write `reports/GATE_Gx.md` and push, then **stop**.

| Gate | Must include |
|---|---|
| **G1** (after Phase 4) | ENVIRONMENT.md, data MANIFEST summary, schema reports, final `d1_subtype_classes` mapping, corpus counts and area histogram, 24 sample renders, ABO check, household table, open questions |
| **G2** (after Phase 6) | Solver and validator description (how the code actually implements §5.2, including any simplifications), test results, pilot CSV, at least 20 pilot renders (all are committed), status and runtime statistics, FCI ordering check, Exp. A runtime projection and proposed adjustments |
| **G3** (after Phase 11) | Headline numbers for H1–H4 (including Exp. R reproduction and generalization): median saving per household and area bin, ΔA_min with CIs, Exp. B table, Exp. C metrics, Exp. D misclassification rates, top ablation sensitivities, HK scenario results; anomalies and a list of known issues |
| **G4** (after Phase 12 and 12b) | All figures and tables (including the F3b 3D renders), the manuscript drafts, FINAL_SUMMARY.md, and a reproduction command list |

## 5. `reports/FINAL_SUMMARY.md` (G4)

1. One-paragraph summary of the findings
2. Answers to RQ1–RQ3 and a verdict on H1–H3 (supported / partly / not supported), each with the result file it rests on
3. Headline numbers table (each with its CI and source file)
4. Limitations actually encountered, beyond those listed in the plan
5. Exact commands to reproduce everything from a clean clone plus `data/raw/`
6. Total compute time per phase

## 6. Review protocol

- The reviewer writes `reviews/Gx_review.md` with:
  - `Verdict: APPROVED` or `Verdict: CHANGES_REQUESTED`
  - Numbered change requests, each marked **[must]** or **[should]**
- Codex addresses every **[must]**, replies to each request in `reports/GATE_Gx_response.md` (done / not done + reason), pushes, and continues only once the verdict is APPROVED or the human author tells it to proceed.
- Small questions between gates go in `reports/QUESTIONS.md`. Codex may continue with a stated default assumption while waiting, and must log that assumption in `reports/DECISIONS.md`.
