# Instructions for Codex

You are the research engineer for this project. Your job is to carry out the computational work in `docs/RESEARCH_PLAN.md` by following `docs/PROCEDURES.md` phase by phase, and to push the outputs specified in `docs/DELIVERABLES.md` so that a reviewer can check them.

## Read first, in this order

1. `docs/RESEARCH_PLAN.md`: what we are trying to show, and the exact definitions (FCI, FEA, TB, strategies S0/S1/S2)
2. `docs/PROCEDURES.md`: what to do in each phase, and the acceptance checks
3. `docs/DELIVERABLES.md`: what to push, file schemas, gates and review protocol
4. `config/project.yaml`, `config/furniture.yaml`, `config/households.yaml`: all parameters; `config/render.yaml`: 3D render settings (Phase 12b, presentation only)

If these documents conflict, the order of precedence is: a review file in `reviews/` > PROCEDURES > RESEARCH_PLAN > DELIVERABLES. Log any conflict you find in `reports/QUESTIONS.md`.

## How to work

- **Go phase by phase (0 → 12).** Don't start a phase before the previous phase's acceptance checks pass, or before the failure is documented with a workaround.
- **Stop at every gate (G1, G2, G3, G4).** Push, write `reports/GATE_Gx.md`, and end your session with a short message to the human saying that the gate is ready for review. Resume only when `reviews/Gx_review.md` says `Verdict: APPROVED`, or when you have addressed its **[must]** items and the human tells you to continue.
- **At the start of every session:**
  1. `git pull`
  2. Read `reviews/` for new files.
  3. Read `reports/DECISIONS.md` and the latest phase report, so you know where you are.
- **Plan before coding** in each phase: write the checklist from PROCEDURES into the phase report, then tick items off as you go.
- **Commit small and often.** Push at the end of every phase and at least daily during long runs. Use messages of the form `phase-NN: <what>`.

## Non-negotiable research-integrity rules

1. **Never fabricate or estimate a result.** Every number in reports, tables, figures and drafts must come from a committed script's output. If a run fails, report the failure.
2. **Never invent references, dataset facts or parameter values.** Use only the references listed in RESEARCH_PLAN §10. Values marked `TODO_VERIFY` stay unused until the human supplies them. Values marked `TODO_FILL_IN_PHASE_1` are filled from data inspection, and the evidence goes in the report.
3. **Don't silently change the configs** in `config/furniture.yaml` or `config/households.yaml`. Propose changes in an `*_overrides.yaml` file and in the phase report; apply them only after a reviewer approves.
4. **The validator is the source of truth.** It must not import constraint logic from `src/fea/solve/`. Report FCI from the validator.
5. **No test-set peeking.** Grouped splits by `group_id`; tune hyperparameters on validation only; log every configuration tried.
6. **Fixed seeds everywhere** (`config/project.yaml: seed`). Record the config hash in every result.
7. **Don't download data that isn't listed** in `config/project.yaml: datasets`. Download only `abo-listings.tar` from ABO, never its images or 3D models. Never commit raw data.
8. **If an expected pattern doesn't appear** (for example S2 < S0 somewhere, or a hypothesis isn't supported), **don't tune things until it does.** Report it, investigate whether it's a bug, and let the reviewer decide.

## Engineering conventions

- Python 3.11. Package `src/fea/` (install with `pip install -e .`, so create `pyproject.toml`). Scripts in `scripts/` are numbered by phase: `00_env_report.py`, `01_download.py`, `02_inspect_schemas.py`, `03_build_corpus.py`, `04_check_furniture.py`, `05_schedules.py`, `06_pilot.py`, `07_run_expA.py`, `08_run_expB.py`, `09_run_expD_ablations.py`, `10_run_expC.py`, `11_scenario_hk.py`, `12_make_figures.py`, `12_make_tables.py`, `12b_render3d.py` (Blender, headless).
- Every script: `--config`, `--dry-run`, a log file in `logs/`, resumable long runs, and a progress bar.
- Tests in `tests/` with `pytest`. At minimum, test the raster, candidates, validator (hand-made violating layouts must be caught), metrics (FCI on a toy case computed by hand; FEA inversion on a synthetic monotone curve), and a tiny end-to-end solve.
- Type hints and docstrings on public functions. No notebook-only logic: notebooks, if any, go in `notebooks/` and only import from `src/fea/`.
- **Parallelism:** CP-SAT uses `num_workers` threads per solve. Run `max(1, cores // num_workers)` solves in parallel and never oversubscribe.
- **Hardware notes:** Only Exp. C (GNN) and the optional LLM baseline use the GPU. Select a compatible PyTorch/CUDA build for the execution environment. If you run without a GPU, Exp. C still works on the CPU (the data is small). Skip the LLM baseline and say so. Do not publish personal equipment or operational identifiers.
- **No internet in the sandbox?** Follow PROCEDURES Phase 1 step 2: list the exact files for the human to download, then stop.

## Time budget

Computation must be finished by about day 14 (see RESEARCH_PLAN §9). If a phase overruns by more than one day, write the problem and options in `reports/QUESTIONS.md` and apply the cheapest scope reduction listed in PROCEDURES (Phase 6 step 6), in that order. Optional items are the first to drop: the LLM baseline, ATUS calibration and the loft bed.

## What "done" looks like

Gate G4 is approved. All files in DELIVERABLES §3 exist and are generated by scripts. `reports/FINAL_SUMMARY.md` answers RQ1–RQ3 with traceable numbers. A clean clone plus `data/raw/` reproduces everything with the commands listed there.
