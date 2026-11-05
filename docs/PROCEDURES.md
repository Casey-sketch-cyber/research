# Operating Procedures

Step-by-step procedures for carrying out `docs/RESEARCH_PLAN.md`. Each phase lists its **inputs**, **steps**, **outputs** and **acceptance checks**. A phase is done only when every acceptance check passes, or when the failure is documented in that phase's report together with the workaround used.

Values come from `config/*.yaml`. Code lives in `src/fea/`, runnable scripts in `scripts/`, and tests in `tests/`.

---

## Repository layout to create

```
src/fea/
  config.py              # load + merge YAML (project, furniture, households, overrides)
  io.py                  # read/write JSONL, parquet, CSV; result-path helpers; resume logic
  data/
    d1_swiss.py          # Swiss Dwellings loader → unified Unit objects
    d2_resplan.py        # ResPlan loader → unified Unit objects
    d3_shells.py         # parametric compact shells generator
    abo.py               # ABO listings parser (dimensions by product type)
    atus.py              # optional ATUS calibration
    hk_census.py         # HK 2021 subdivided-unit tables
  geometry/
    unit.py              # Unit dataclass: polygons per space class, doors, windows, entrance
    normalize.py         # rotate to dominant axis, translate to origin, clean geometry
    raster.py            # rasterize Unit → cell-class grid + wall/window masks
  furniture/
    library.py           # item specs with clearance scale applied
    candidates.py        # feasible poses per (item, orientation, state)
  households.py          # schedules, variants, capability rules
  solve/
    cpsat.py             # proposed method (S0/S1/S2)
    reachability.py      # BFS on eroded free space; no-good cut generation
    greedy.py
    anneal.py
    llm.py               # optional
  validate.py            # INDEPENDENT validator (shares no constraint code with solve/)
  metrics.py             # FCI, TB, f0 isotonic fit, FEA, A_min, bootstrap
  surrogate/
    features.py
    graphs.py
    models.py
    train.py
  scenario_hk.py
  viz/
    layouts.py           # per-slot layout renderings
    figures.py           # F1–F10
scripts/                 # thin CLI wrappers, numbered by phase (see below)
tests/
```

Every script takes `--config config/project.yaml` and `--dry-run`, and writes a log to `logs/<script>_<timestamp>.log` (git-ignored). Long runs must be **resumable**: skip instances whose result already exists in `data/interim/`.

### Unified data model

A `Unit` (one dwelling) holds:

- `unit_key`: a globally unique string, `"<source>:<site>:<building>:<apartment>"` for D1, `"<source>:<plan_id>"` for D2, `"D3:<params-hash>"` for D3
- `source`, `group_id` (used for grouped splits: `site_id` for D1, plan ID for D2, shell family for D3)
- Polygons by space class: `furnishable`, `walkable_only`, `fixed_service`, `excluded`
- `walls`, `doors` (each with width and hinge side if known), `windows`, `entrance` (one door)
- Scalar attributes: gross area, furnishable area, rooms, windows, doors
- `meta` (source-specific fields such as the D1 simulation summary)

### Layout JSON schema (one per solved instance)

```json
{
  "unit_key": "...", "household": "H2_single_remote_worker", "strategy": "S2", "algorithm": "cp_sat",
  "resolution_m": 0.10, "clearance_scale": 1.0, "walking_width": 0.60,
  "items": [
    {"instance_id": "wall_bed_single#1", "type": "wall_bed_single", "x": 1.20, "y": 0.00,
     "orientation_deg": 0, "states": {"normal": {"night": "deployed", "morning": "stowed", "...": "..."}}}
  ],
  "service": {"normal": {"night": [{"need": "sleep_1", "by": ["wall_bed_single#1"], "served": true}]}},
  "fci": 0.97, "fci_by_variant": {"normal": 0.97}, "tb": 2.0,
  "solver": {"status": "OPTIMAL", "time_s": 12.3, "objective": 0, "bound": 0, "reach_iterations": 2},
  "validator": {"pass": true, "violations": []},
  "config_hash": "..."
}
```

---

## Phase 0: Environment (day 1)

**Steps**
1. Create a Python 3.11 virtual environment. Core packages: `numpy pandas pyarrow shapely scipy networkx ortools scikit-learn lightgbm matplotlib pyyaml tqdm joblib pytest`. GPU packages, only for Exp. C or the optional LLM baseline: `torch` (an RTX 5090 needs a CUDA 12.8+ build, PyTorch ≥ 2.7) and `torch_geometric` (optional; fall back to a plain-PyTorch GNN if it fails to install).
2. Write `reports/ENVIRONMENT.md`:
   - OS, CPU model and core count, RAM, GPU (`nvidia-smi` output, or "no GPU")
   - Python version and `pip freeze` saved to `requirements.lock.txt`
   - Whether outbound internet works
3. Write `requirements.txt` with minimum versions.

**Acceptance**
- `pytest` runs (an empty suite is fine).
- `python -c "import ortools, shapely"` succeeds.
- ENVIRONMENT.md exists.

---

## Phase 1: Data acquisition and schema inspection (day 1)

**Steps**
1. `scripts/01_download.py` downloads into `data/raw/` (git-ignored) and writes `data/raw/MANIFEST.csv` (file, url, bytes, sha256, date):
   - D1: `https://zenodo.org/records/7788422/files/swiss-dwellings-v3.0.0.zip?download=1`
   - D2: clone or download ResPlan from GitHub (or Kaggle).
   - D4: `abo-listings.tar` **only**.
   - D6: the CSV/XLSX from data.gov.hk.
   - D5 (ATUS): only if Phase 4 calibration will be done.
2. **If the environment has no internet:** stop and write `reports/phase_01_data.md` listing the exact files and URLs the human must download, with target paths under `data/raw/`. Continue once the files are present.
3. `scripts/02_inspect_schemas.py` writes `reports/schemas/` (committed). For each file it records:
   - Columns and dtypes, row counts, and 5 example rows (geometry WKT truncated)
   - D1: every distinct `entity_type` and `entity_subtype` value with counts, plus the list of `simulations.csv` column-name prefixes
   - D2: the keys and geometry types in the pickle
   - D4: the share of listings with `item_dimensions` and `product_type`, and the product types that relate to furniture
   - D6: every field name and what it means (read the data dictionary)

**Acceptance**
- MANIFEST.csv has checksums.
- `reports/schemas/*.md` exists for D1, D2, D4 and D6.
- In `config/project.yaml`, every `corpus.d1_subtype_classes` `TODO_FILL_IN_PHASE_1` is replaced with the real subtype lists, and the reasoning for each class is written in the phase report.

---

## Phase 2: Corpus construction (days 2–3)

**Steps**
1. **D1 loader.**
   - Keep only `unit_usage == RESIDENTIAL`.
   - Group geometry by apartment and build a `Unit`.
   - Classify areas with `d1_subtype_classes`.
   - Find the entrance door: the door whose opening touches a non-unit area such as a corridor or staircase, or the unit boundary. Record the method and how many units it fails for.
   - Attach summary daylight and noise values from `simulations.csv` to `meta`.
2. **D2 loader.** Convert ResPlan polygons to `Unit` with the same classes. Document the mapping.
3. **D3 generator.** Create shells from `shells_D3` (areas × aspect ratios × entrance positions × window positions). The toilet pod and kitchenette are `fixed_service`.
4. **Normalize** (rotate to the dominant axis, translate) and **validate** geometry: valid polygons, rooms inside the unit outline, at least one window, an entrance present.
5. **Filter** with `corpus.*`. If fewer than 300 D1 units pass, use 55 m² and say so.
6. Write `data/processed/corpus_units.parquet` and `results/corpus/corpus_units.csv`. Columns: `unit_key, source, group_id, gross_area_m2, furnishable_area_m2, n_rooms, n_windows, n_doors, aspect_ratio, compactness, include, exclude_reason`.
7. Render a random sample of 24 included units (8 per source) to `results/corpus/samples/*.png`, showing space classes, doors, windows and the entrance in different colours.

**Acceptance**
- Corpus counts per source, with an area histogram (figure F2 draft), in the phase report.
- Exclusion reasons tabulated.
- The 24 sample renders look plausible: the human reviewer checks them at Gate G1.
- Unit tests for the loaders cover at least one known D1 apartment and one D2 plan.

---

## Phase 3: Furniture library check (day 3)

**Steps**
1. Parse ABO listings. For furniture product types (beds, sofas, sofa beds, desks, tables, wardrobes, shelves, and anything else relevant found in Phase 1), compute median and IQR of width, depth and height in metres. Convert units carefully and drop outliers above the 99th percentile.
2. Compare these with `config/furniture.yaml`. Write `results/furniture/abo_dimension_check.csv` with columns `item, config_w, config_d, abo_type, n, median_w, median_d, iqr_w, iqr_d, flag`. Set `flag` when a config dimension lies outside the ABO IQR.
3. Do **not** edit `furniture.yaml`. Put proposed changes in `config/furniture_overrides.yaml` (commented, not active) and list them in the report.

**Acceptance**
- The CSV exists.
- Each flagged item has a one-line justification: keep or change.

---

## Phase 4: Household schedules (day 3; ATUS calibration optional)

**Steps**
1. Implement `households.py`: parse slots, variants, demands, weights and capability rules. Implement `demanded_hours(h)`.
2. Unit tests: slot durations sum to 24 h for every variant, and every demand token exists in the furniture `serves` lists.
3. *(Optional)* ATUS: compute mean minutes at home in sleep, eating, work and leisure for comparable respondent groups (living alone and employed; working at home; couples; single parents; 65+). Compare these with the slot durations. Put proposals only in `reports/phase_04_households.md`.

**Acceptance**
- The tests pass.
- Table T3 (household schedules) is generated in `results/tables/T3_households.csv`.

### ⛔ GATE G1: data and corpus review
Push everything, then write `reports/GATE_G1.md` (template in `reports/TEMPLATE_phase_report.md`) summarizing Phases 0–4, with open questions. **Stop.** Continue only when `reviews/G1_review.md` exists with `Verdict: APPROVED`, or after making the changes it requests.

---

## Phase 5: Rasterization and candidate generation (days 4–5)

**Steps**
1. `raster.py`: produce a grid (resolution `raster.resolution_m`) whose cells are labelled FURNISHABLE, WALKABLE, BLOCKED or KEEPOUT. Also produce:
   - A wall mask of blocked cells next to free cells
   - A window mask of wall cells along window segments
   - The entrance cells
   - Door-swing keep-outs as configured
2. `candidates.py`: for each item, state and orientation, the body cells must be FURNISHABLE and the clearance cells must be FURNISHABLE or WALKABLE (not BLOCKED or KEEPOUT).
   - Wall-backed items need the full row of cells behind the body to be wall.
   - Tall items may not have window cells behind them.
   - Use 2D convolution or integral images; it must not be a Python loop over cells.
   - For transformable items, a **pose** is feasible only if every state the strategy can use fits at that pose (the anchor is shared).
3. Tests with hand-made rooms:
   - A 3.0 × 4.0 m empty room gives the expected count of `desk` poses (compute it analytically).
   - A wall-backed item is never placed in the middle of the room.
   - Nothing is placed on a door-swing keep-out.

**Acceptance**
- The tests pass.
- Median candidate generation time per unit is under 2 s.
- Candidate counts per item are logged.

---

## Phase 6: Solver, validator and pilot (days 5–7)

**Steps**
1. **CP-SAT model (`solve/cpsat.py`)**, as specified in RESEARCH_PLAN §5.2:
   - **Pose variables:** one Boolean `x[i,p]` per (item instance, feasible pose); Σ_p x[i,p] ≤ 1.
   - **Per-variant, per-slot state:**
     - S0: static only.
     - S1: one Boolean per transformable instance for the whole day (deployed or stowed).
     - S2: a Boolean per (instance, variant, slot).
   - **Occupancy, per (variant, slot, cell):** the body occupancy sum is ≤ 1. For each pose whose *active* clearance covers a cell, `x[i,p] ∧ active ⇒ cell not occupied by another body`. Linearize with auxiliary occupancy Booleans. To keep the model small, generate constraints only for cells covered by at least two candidates.
   - **Service assignment:** Booleans `y[need, slot, variant, instance]`. Each instance serves at most one need per slot. An instance can serve a need only if it is placed and in a state whose `serves` includes a token that satisfies the need. A need that requires two tokens (for example sleep_2 from two sleep_1) needs two distinct instances. Storage is served as `min(1, Σ units of placed storage items / required)`; model this with an integer scaled by 10.
   - **Objective:** weights from `solver.weights` (served weighted hours ≫ burden ≫ window proximity).
   - Set `solver.time_limit_s`, `num_workers` and `random_seed = seed`.
2. **Reachability loop (`solve/reachability.py`):**
   - For each (variant, slot), take the free cells (not covered by any active body) and erode them by `walking_width/2`.
   - BFS from the entrance cells.
   - Every served item's access cells (the clearance zone on its access side) must touch the reachable set. Doors to fixed-service spaces must also be reachable.
   - If this fails, add a no-good cut over the set of placed poses whose bodies border the disconnected region, and re-solve.
   - Stop after `reachability_max_iterations`. If the limit is hit, mark unreachable items as **unserved** in the final accounting rather than discarding the layout.
3. **Validator (`validate.py`):** write it independently. It reads only the layout JSON, the raster and the configs, recomputes everything from scratch, and recomputes FCI and TB. **Exp. A–D report FCI from the validator, not from the solver's objective.** If the solver and validator disagree on FCI by more than 1e-6, log it as a bug and investigate.
4. **Pilot:** choose 20 units: 8 D1 stratified by area, 6 D2 and 6 D3 including 8 m² and 12 m² shells. Run 4 main households × 3 strategies = 240 instances.
5. **Render** every pilot instance with `viz/layouts.py`: one panel per slot (for the `normal` variant) showing item bodies (colour by item, hatched when stowed), clearance zones (translucent), the walking path, and the FCI/TB in the title. Save to `results/layouts/pilot/<unit>_<household>_<strategy>.png`.
6. **Projection:** from the pilot runtimes, estimate the wall-clock time of the full Exp. A on this machine. **Exp. A must finish within 36 h.** If the projection exceeds that, propose in the gate report, in this order:
   1. Lower `time_limit_s` to 30.
   2. A stratified sample cap per source (by area bins).
   3. Run S1 only on a 30% subset.

**Acceptance**
- All solver outputs pass the validator, or every failure is explained.
- **S2 ≥ S1 ≥ S0 in FCI for every pilot instance** (S2 relaxes S1, which relaxes S0). Any violation is a bug or a timeout and must be explained.
- `results/pilot/pilot_solutions.csv` is written (schema in DELIVERABLES §3).
- At least 6 renders are reviewed and described in the report.
- Runtime statistics and the Exp. A projection are in the report.

### ⛔ GATE G2: method review
Push, write `reports/GATE_G2.md`, **stop**, and wait for `reviews/G2_review.md`.

---

## Phase 7: Experiment A, strategies (days 8–9)

**Steps**
1. Run every included unit × main households × {S0, S1, S2} with parallel workers. Use `n_jobs = max(1, cores // num_workers)` and keep the processes from oversubscribing the CPU. Write JSONL to `data/interim/expA/`, which can be resumed.
2. Aggregate into `results/expA/solutions.csv`.
3. Metrics (`metrics.py`):
   - Fit f₀,h with isotonic regression of FCI_S0 on furnishable area, separately for each household. Use D1+D2+D3 pooled, and also each source separately as a robustness check.
   - Compute FEA, saving and relative saving per (unit, household). Flag `right_censored`.
   - Build the area-saving curve: medians per 2 m² bin with bootstrap 95% CIs (resample units).
   - Compute A_min per (household, strategy) from a logistic fit of `1[FCI ≥ τ]` on area, with bootstrap CIs; ΔA_min = A_min(S0) − A_min(S2).
   - Wilcoxon signed-rank tests of S2 vs S0 and S2 vs S1 (paired by unit and household), with effect sizes.
4. Showcase renders: 3 units (about 10, 18 and 30 m²) × H3 × S0/S1/S2, the draft of figure F3.

**Acceptance**
- The solver status distribution is reported (OPTIMAL / FEASIBLE / TIMEOUT-without-solution / INFEASIBLE). TIMEOUT-without-solution must be under 5% of instances; if it isn't, report this and propose a fix.
- The FCI ordering check (S2 ≥ S1 ≥ S0) is reported across all instances.
- Files written: `fea.csv`, `area_saving_curve.csv`, `min_adequate_area.csv`, `tests.csv`.

## Phase 8: Experiment B, algorithms (day 9)

1. Draw a stratified sample of 200 (unit, household) S2 instances, stratified by source × area tercile × household. Fix the seed and save the list to `results/expB/instances.csv`.
2. Run greedy, simulated annealing and CP-SAT. Run the local LLM only if Phases 7–11 are on schedule. The LLM prompt must contain the raster as a list of free rectangles, the item specs and the slot schedule, and must ask for JSON matching the layout schema. Parse it robustly; up to 2 retries on invalid JSON.
3. **The validator scores every output.** Report the validity rate, the number and types of violations, FCI (with invalid layouts scored as their validator FCI), and runtime.

## Phase 9: Experiment D and ablations (day 10)

1. **Exp. D.** Compute each conventional indicator per (unit, household) and binary adequacy under each indicator. Report:
   - Spearman ρ(area, FCI_S0) and ρ(area, FCI_S2)
   - IQR of FCI within 2 m² bins
   - Confusion matrices against `FCI ≥ τ` and the misclassification rate per indicator

   Files: `results/expD/*.csv`.
2. **Ablations** from `config/project.yaml` → `ablations`. For the resolution and time-limit runs, use the fixed 50-unit subset saved in `results/ablations/subset.csv`. The other ablations run on the Exp. B 200-instance sample, or on everything if time allows; state which. Write `results/ablations/*.csv` and a tornado plot (F9) of the change in median saving and ΔA_min.

## Phase 10: Experiment C, surrogate (day 11)

1. Build the features and graphs from the `Unit` objects; no solver outputs may be used as inputs.
2. Group split by `group_id`, with the seed. D2 and D3 are additional test sets.
3. Train the four models. Tune hyperparameters on validation only, with small grids, and log every configuration tried. GPU is optional; the data is small.
4. Report MAE, RMSE, R² and Spearman per target, household and test set, plus inference ms per unit. Produce parity plots (F8).
5. Save the best GNN weights to `results/expC/models/` only if under 50 MB; otherwise save them locally and record the path.

## Phase 11: Hong Kong scenario (day 12)

1. For D3 shells at 8–20 m² × scenario households × {S0, S2}, use the **solver** (not the surrogate); there are few enough shells. Compute the adequate share and A_min.
2. Join with D6:
   - If D6 gives subdivided-unit counts and household-size distributions per district, weight by them.
   - If it gives a floor-area distribution, map units to the nearest shell area.
   - Otherwise report territory-level results only and state why.
3. Carbon: compute avoided floor area. Multiply by the embodied-carbon factor **only if** `hk_scenario.embodied_carbon_kgco2e_per_m2` has been filled in with a verified source; otherwise report the avoided m² only.
4. Outputs: `results/scenario_hk/*.csv` and figure F10.

### ⛔ GATE G3: results review
Push, write `reports/GATE_G3.md` with the headline numbers and how they bear on H1–H3, **stop**, and wait for `reviews/G3_review.md`.

---

## Phase 12: Figures, tables and drafts (days 13–14)

1. Generate F1–F10 and T1–T7 from scripts only (`scripts/12_make_figures.py`, `scripts/12_make_tables.py`). Save figures as PNG at 300 dpi plus PDF to `results/figures/`, and tables as CSV plus Markdown to `results/tables/`. Use a consistent style: one sans-serif font, colour-blind-safe palette, and labelled axes with units.
2. Write `manuscript/draft_methods.md` and `manuscript/draft_results.md`: factual descriptions of what was done and found, with every number traceable to a results file (cite the file path in an HTML comment next to each number). **No discussion or speculation, and no references that are not already in RESEARCH_PLAN §10.**
3. Write `reports/FINAL_SUMMARY.md` (see DELIVERABLES §5).

## Phase 12b: 3D renderings (days 13–14; presentation only)

The renders illustrate solved layouts for the paper and the graphical abstract. They never feed into any metric.

1. Export each solved layout to a scene description, `results/renders3d/scenes/<unit>_<household>_<strategy>.json`: unit polygons, walls, doors, windows, and every item's pose and per-slot state. Use the layout JSON plus the `Unit`.
2. `scripts/12b_render3d.py`, a Blender Python script run headless as `blender -b -P scripts/12b_render3d.py -- --config config/render.yaml`:
   - Extrude the walls to the ceiling height and apply the cutaway.
   - Build each item procedurally from boxes and bevels, using the 2D footprint (`config/furniture.yaml`, after any approved overrides) and the heights in `config/render.yaml`. Don't download any 3D model.
   - Use the colour-by-function palette so the renders match the 2D figures.
   - Render the stills listed in `config/render.yaml → outputs.stills` with one fixed camera, lighting and scale.
3. Compose figure **F3b**: rows = strategy (S0, S2), columns = slots (night, day, dinner), one figure per showcase unit, with the FCI and TB values (read from the results files) in the panel titles.
4. *(Optional)* The transformation animation in `outputs.animation`, saved as MP4 and GIF.
5. **If Blender can't run in your environment:** still commit the scene JSONs and `12b_render3d.py`, test the script on one scene with the CPU or the Python fallback, and write in the phase report a portable command for the author to run in a compatible environment, without personal equipment identifiers.

**Acceptance**
- The scene geometry in a render matches the 2D layout for the same instance. Check 3 instances by overlaying a top-view orthographic render on the 2D layout; overlap error should be under 2 cm.
- Every still listed in the config exists.
- The renders use the same camera and palette.

### ⛔ GATE G4: final package
Push, **stop**, and wait for `reviews/G4_review.md`.

---

**Visual target.** `docs/img/mockup_studio_S2.png` is a hand-made, illustrative mock-up (not a result) of the style expected for the per-slot layout renders (Phase 6) and the simple 3D massing. Final 3D renders (Phase 12b) should be higher quality.
