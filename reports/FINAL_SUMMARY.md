# Final summary

## Findings

On 2,109 observed floor plans, allowing form and time raised modeled capacity for 7.5% of commuters, 8.7% of remote workers, 23.5% of couples and 35.9% of parents with a child. The all-pair median equivalent-area gain was zero for each household. Identified positive gains for a couple had a median of 6.21 m². The largest two-person gains in the generated shells occurred at intermediate sizes. In the Hong Kong scenario, a larger couple kit made 21 more of the 120 shells adequate at 13–16 m² and reduced mean FCIq below 13 m². The commuter comparisons support keeping the catalogue. GraphSAGE fell below the planned rank criterion on observed held-out sites. [Coverage and area](../results/tables/g4/T4.md) · [Hong Kong figure](../results/figures/g4/F10.pdf) · [Prediction metrics](../results/expC/metrics.csv)

## Research questions

| Question | Answer and evidence |
| --- | --- |
| **RQ1. How much coverage does transformable furniture add?** | Among observed plans the largest mean form increment was 0.0271 FCI for parent and child. The couple had the largest mean switching increment, 0.0112. The combined gain occurred in a minority of matched plans for every household. [Primary effects](../results/expA_f1/analysis/primary_effects.csv) |
| **RQ2. How large is the gain on a common static area scale?** | Over all observed pairs the zero median reflects many unchanged scores. Conditional gains range by household, with support-limited commuter results. At τ = 0.95 the parent-and-child observed-plan ΔAₘᵢₙ was 10.78 m². The same contrast in D3 was 6.45 m². [Paired area summary](../results/g3/area_summary.csv) · [Area crossings](../results/expA_f1/analysis/min_adequate_area.csv) |
| **RQ3. What does the Hong Kong scenario show?** | Adequacy depends on household, area and strategy. The couple switching contrast was 2.24 m². The census lacks a joint household-size and floor-area distribution for territory weights or totals. The 8 m² comparator is covered by the generated shells. The observed plans start at 16.75 m². [Scenario summary](../results/g3_review_k3/hk_scenario_summary.csv) · [Switching comparison](../results/g3_review/hong_kong/couple_switching.csv) · [D6 coverage](schemas/D6.md) |
| **RQ4. Which kit dimensions improve the fit?** | No tested kit established an improvement for the commuter. H3_kit_02 gained adequacy at 13–16 m² and lost mean FCIq below 13 m². Its training mean interval includes zero. [Paired kit results](../results/g3_review_k3/paired_effects.csv) · [H3 size bands](../results/g3_review_k3/hk_h3_size_bands.csv) |

| Hypothesis | Verdict and evidence |
| --- | --- |
| **H1. Gains peak at the smallest areas.** | **Partly supported.** Gains are positive for some units, with intermediate-size peaks for the two-person D3 households. The pattern is nonmonotonic. [Absolute and relative bin results](../results/g3/area_summary.csv) |
| **H2. Area alone misses relevant differences in capacity.** | **Supported within the model.** In observed plans the 45 m² comparator disagreed with S2 adequacy on 55.7% of couple and 52.7% of parent-and-child cases. Within-bin dispersion shows capacity differences under the same household and strategy. [Dispersion](../results/expD/dispersion.csv) · [Confusion tables](../results/expD/confusion.csv) |
| **H3. Graph prediction reaches Spearman ρ ≥ 0.80 on held-out sites.** | **Not supported.** D1 GraphSAGE correlations ranged from 0.087 to 0.661 for S0 and 0.088 to 0.588 for S2. [Held-out metrics](../results/expC/metrics.csv) |
| **H4. A standard kit improves adequacy and captures most of the bespoke gain.** | **Not supported for the commuter. Mixed for the couple.** H3_kit_02 was adequate on 5/30 training shells versus 2/30 for the catalogue. Its paired mean interval includes zero and it captured 7.4% of the observed bespoke gain. [Kit selection](../results/g3_review_k3/kit.yaml) · [Paired effects](../results/g3_review_k3/paired_effects.csv) |

## Headline estimates

Intervals are 95% bootstrap intervals where supported. A “≥” result is a reference-support lower bound.

| Quantity | Estimate | Evidence |
| --- | --- | --- |
| Couple, observed, mean form and time effects | 0.0130 [0.0112, 0.0148] and 0.0112 [0.0094, 0.0130] FCI | [Primary effects](../results/expA_f1/analysis/primary_effects.csv) |
| Identified positive ΔEA, observed | Remote worker 1.33 [0.75, 3.11], couple 6.21 [4.20, 10.00], parent and child 5.00 [4.20, 8.00] m² | [Area summary](../results/g3/area_summary.csv) |
| Observed commuter median among improved pairs | ≥2.00 m². The identified-positive median is unavailable. | [P1 results](phase_07_P1_results.md) |
| ΔAₘᵢₙ, observed parent and child | 10.78 [9.15, 12.70] m² | [Area crossings](../results/expA_f1/analysis/min_adequate_area.csv) |
| ΔAₘᵢₙ, D3 | Commuter 1.68 [1.12, 2.38], remote worker 3.63 [2.78, 4.77], couple 5.53 [4.90, 6.12], parent and child 6.45 [5.19, 7.75] m² | [Area crossings](../results/expA_f1/analysis/min_adequate_area.csv) |
| Production versus standalone annealing | +0.0087 [0.0016, 0.0160] mean FCI on 200 pairs | [Benchmark effects](../results/g3_review/benchmark/production_paired_effects.csv) |
| Couple mirrored-access sensitivity | −0.0122 [−0.0203, −0.0040] FCI change in time effect | [F3 sensitivity](../results/expA_f3/effect_summary.csv) |
| HK couple, form only to form plus time | 2.24 [1.66, 2.82] m² under the common quality rule | [Switching comparison](../results/g3_review/hong_kong/couple_switching.csv) |
| HK couple, larger kit versus optimized catalogue | Aₘᵢₙ 15.39 [14.67, 16.19] versus 16.12 [15.70, 16.57] m². The point estimates differ by 0.73 m². | [Scenario crossings](../results/g3_review_k3/hk_scenario_summary.csv) |
| HK couple, 13–16 m² and below 13 m² | 51/120 versus 30/120 adequate at 13–16 m². Mean FCIq 0.448 versus 0.500 below 13 m². These are enumerations of the fixed grid. | [Size bands](../results/g3_review_k3/hk_h3_size_bands.csv) |
| Training mean FCIq contrast for the highest ranked kit | Commuter +0.0013 [−0.0153, +0.0200] using the best saved layouts. Couple +0.0021 [−0.0336, +0.0279] after matched extra search. | [Paired kit results](../results/g3_review_k3/paired_effects.csv) |

## Limitations encountered

- The predeclared empty-geometry screen excludes 123 units. The audit found that oblique kitchen openings can be lost at 0.10 m resolution. Valid zero-score layouts remain in the results. [Evaluability audit](expA_evaluability.md) · [Exclusion causes](expA_exclusion_causes.md)
- Some observed-plan area inverses and adequacy crossings lie outside model support. The pooled reference adds generated support and changes implied area. For D2, metric scale remains a data preparation assumption. [P1 results](phase_07_P1_results.md) · [D2 audit](schemas/D2.md)
- The benchmark found 11 cases in which another method achieved a higher FCI than production. Kit results cover nine vectors and the approved reduced scope. H1_kit_01's best saved training result includes confirmation effort. Mirrored one-side access changes both clearance and access targets. [Shortfalls](../results/g3_review/benchmark/production_shortfalls.csv) · [K3 review](../reviews/G3_review_round3.md) · [F3 sensitivity](phase_07_F3_results.md)
- The room study deducts clearances and gives conflicting furniture dimensions. The approximate comparison uses body-free daytime area, including service space where present. The literature screen covered 3,006 retrieved titles and 407 available abstracts. It retained 540 records with unavailable abstracts. Two overlap records remained at abstract or project-summary access. [Room comparison](phase_09_R_results.md) · [Literature screening](novelty_check.md#systematic-confirmation-task-l--g3)
- The scenario uses a fixed template grid and no district weighting. A territory-wide area total or embodied-carbon estimate would require additional data. [D6 coverage](schemas/D6.md)

## Reproduction from a clean checkout

Use Python 3.11 and the committed dependency lock. Run from the repository root. The historical numerical runners use Linux file locks. Place the raw archives in the matching subdirectories of `data/raw`. The accepted output snapshots are in the checkout. [Pinned datasets](../config/downloads.yaml)

~~~sh
python -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements.lock.txt
python -m pip install --no-deps -e .
python scripts/01_download.py --verify-only
python scripts/11d_report_k3.py --verify
python scripts/11_complete_literature.py --verify
python scripts/12_verify_g4.py --verify
~~~

Rebuild the G4 visuals and tables in a separate checkout to preserve the release hashes. The four small-shell layout inputs and the three original showcase plans are in the repository.

~~~sh
python scripts/12b_export_scenes.py
blender -b -P scripts/12b_render3d.py -- --config config/render.yaml
blender -b -P scripts/12c_render_polish.py -- --config config/render.yaml
python scripts/12_make_figures.py --only 2d
python scripts/12_make_figures.py --only 3d
python scripts/12_make_tables.py
~~~

Blender 4.5 LTS was used. A CUDA installation can pass `--device cuda` after the script options. The equivalent invocation with that Blender version's Python module is `python scripts/12b_render3d.py --config config/render.yaml`. Use the same invocation with `scripts/12c_render_polish.py` for the presentation views. Fresh outputs record fresh runtimes and PDF creation dates. Scene and score digests can be compared independently of those records.

### Numerical stage commands

Install the version used for Experiment C before training the surrogate. [Accepted software record](../results/expC/acceptance.json)

~~~sh
python -m pip install torch==2.7.1 --index-url https://download.pytorch.org/whl/cpu
~~~

Use the reviewed commits and matching configuration snapshots. The original A and A2 launches predate the two-single-bed correction. F1 used the numerical implementation in `022a790`. Later accepted F3, P1, B–K and HK use the corresponding reviewed commits. For F2, refresh the figure signatures after inspection and run `python scripts/07_f2_acceptance.py`. Finalize F3, P1 and R by rerunning their analysis drivers with `--finalize` after inspecting the figures. Historical gates bind exact result and layout hashes. A fresh run under fixed wall-clock limits can return different valid incumbents. For the published numbers, verify the committed evidence. For new runs, revalidate the generated checkpoints and inspect the figures before writing new visual-review receipts.

| Phase | Commands in dependency order | Frozen records |
| --- | --- | --- |
| 0–5 | `python scripts/00_env_report.py` → `python scripts/01_download.py --verify-only` → `python scripts/02_inspect_schemas.py` → `python scripts/02_accept_data.py` → `python scripts/03_build_corpus.py` → `python scripts/03_accept_corpus.py` → `python scripts/04_check_furniture.py` → `python scripts/05_schedules.py` → `python scripts/05_candidates.py` | [Preparation](../docs/PROCEDURES.md) · [Corpus](phase_02_corpus.md) |
| 6 | `python scripts/06_revision.py --prepare` → `python scripts/06_revision_pipeline.py` → `python scripts/06_cut_comparison.py` → `python scripts/06_revision_report.py --export --render --run-tests` → `python scripts/06_round2_pilot_queue.py` → `python scripts/06_round3_continue.py` | [Pilot](phase_06_pilot.md) · [G2 response](GATE_G2_response.md) |
| 7, original A and A2 | `python scripts/07_run_expA.py --selection results/pilot/round2/production_selection.json` → `python scripts/07_evaluability.py` → `python scripts/07_metrics.py` → `python scripts/07_run_a2.py` → `python scripts/07_a2_report.py` | [Historical A](phase_07_expA.md) · [A2](phase_07_A2.md) |
| 7, F1–F3 and P1 | `python scripts/07_f1_compatibility.py` → `python scripts/07_run_f1.py` → `python scripts/07_f2_analysis.py` → `python scripts/07_f2_showcases.py` → `python scripts/07_run_f3.py` → `python scripts/07_f3_report.py` → `python scripts/07_p1_analysis.py` | [F1–F3](phase_07_F1_F2_F3.md) · [P1 inspection and finalization](phase_07_P1_results.md) |
| 8–9b | `python scripts/08_prepare_expB.py` → `python scripts/08_run_expB.py` → `python scripts/08_report_expB.py` → `python scripts/09_run_expD.py` → `python scripts/09_run_expR.py` → `python scripts/09_run_ablations.py` → `python scripts/09_report_ablations.py` | [B](phase_08_B_results.md) · [D](phase_09_D_results.md) · [R](phase_09_R_results.md) · [Ablations](phase_09_ablation_results.md) |
| 10–11b | `python scripts/10_run_expC.py` → `python scripts/11b_run_expK.py` → `python scripts/11_scenario_hk.py` → `python scripts/11_complete_literature.py --verify` → `python scripts/11_make_G3.py --verify` | [C](phase_10_C_results.md) · [Reduced K](phase_11b_K_results.md) · [HK](phase_11_HK_results.md) · [Literature snapshot](task_L_literature.md) |
| 11c–11d | `python scripts/11c_recheck_B_C.py` → `python scripts/11c_rescore_catalogue.py` → `python scripts/11c_recheck_kit.py` → `python scripts/11c_recheck_hk.py` → `python scripts/11d_run_k3.py` → `python scripts/11d_report_k3.py` | [G3 response](GATE_G3_response.md) · [K3 run](phase_11d_K3.md) |
| 12–12b | Run the G4 commands above. To refresh H1 examples from the full numerical run, first run `python scripts/12b_export_scenes.py --capture-shell-evidence`. | [G4 evidence](../results/g4/release_manifest.json) |

## Measured compute time

The table gives phase elapsed time where recorded. Independent phases sometimes overlapped.

| Phase | Recorded time | Work covered |
| --- | --- | --- |
| 0 | 25.306 s | [Environment check](phase_00_environment.md) |
| 1 | 2.844 s verification and 73.724 s schema inspection | Initial transfer timing is incomplete. [Acquisition](acquisition.json) · [Schema timing](schema_run.json) |
| 2 | 49.329 s | [Recorded corpus conversion invocation](corpus_audit.json) |
| 3–4 | 10.317 s and 0.672 s | [Furniture check](phase_03_furniture.md) · [Household audit](households_audit.json) |
| 5–6 | 0.123 s median candidate generation per unit. The paired 20-case cut comparison took 32.15 s and 31.83 s per arm. | Pilot history includes other benchmarks and development runs without a consolidated elapsed total for all attempts. [Candidates](phase_05_candidates.md) · [Pilot](phase_06_pilot.md) |
| 7 | Original A 25.403 h, historical A2 15.082 h, F1 18.498 h, F3 8.398 h | F2 and P1 analyzed saved scores. [Execution budget](COMPUTE_BUDGET.md) |
| 8 | 0.178 h pilot and 0.999 h full stage | The full stage reused pilot checkpoints. [B](phase_08_B_results.md) |
| 9–9b | D 3.296 s, R 640.830 s, ablations 6.156 h initial and 0.708 h resumed | [D](phase_09_D_results.md) · [R](phase_09_R_results.md) · [Ablations](phase_09_ablation_results.md) |
| 10 | 25.993 s | [C](phase_10_C_results.md) |
| 11–11b | HK 8.793 h and reduced K 11.360 h including pilot | [HK](phase_11_HK_results.md) · [Reduced K](phase_11b_K_results.md) |
| 11c–11d | 0.810 h catalogue update, 4.524 h HK revision and 20.82 min K3 extra search | [Recorded review runs](COMPUTE_BUDGET.md) |
| 12–12b | 18.06 s for figures and tables, 4.58 s for scene export and 370.36 s for the 30 stills and 3 top views | [Phase report](phase_12_G4.md) |
