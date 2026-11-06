# Reproducing the corpus and method pilot

Use Python 3.11 and a project-local virtual environment. Keep temporary files,
caches and outputs inside the project or another explicitly selected workspace.
Install `requirements.txt`, then install this package with `pip install -e .`.
`requirements.lock.txt` records the versions used for the recorded run.

From the repository root:

```sh
python scripts/00_env_report.py --config config/project.yaml
python scripts/01_download.py --config config/project.yaml
python scripts/02_inspect_schemas.py --config config/project.yaml
python scripts/02_accept_data.py --config config/project.yaml
python scripts/03_build_corpus.py --config config/project.yaml
python scripts/03_accept_corpus.py --config config/project.yaml
python scripts/04_check_furniture.py --config config/project.yaml
python scripts/05_schedules.py --config config/project.yaml
python scripts/03_review_report.py --config config/project.yaml
python -m pytest -q
```

Each phase command supports `--dry-run`. Downloads use partial-file resume and
publisher checksums where available. The corpus keeps per-unit checkpoints in
`data/interim/corpus/`, keyed by configuration and conversion-code hashes, and
bypasses fully completed sources. If conversion code changes, a new cache is
used; old outputs are never silently reused under changed geometry logic.

Only the sources listed in `config/project.yaml` are permitted. Their exact
download URLs and the pinned D2 revision are in `config/downloads.yaml`.
Raw archives, extracted data and all interim checkpoints remain untracked.
The complete normalized geometry is in the untracked
`data/processed/corpus_units.parquet`; the public corpus CSV contains scalar
attributes for every unit and an explicit inclusion/exclusion flag.

D1 is attributed to Swiss Dwellings (DOI 10.5281/zenodo.7788422); D2 to ResPlan;
D4 to Amazon Berkeley Objects; and D6 to the Hong Kong Census and Statistics
Department. Dataset licensing and links are recorded in the project config and
schema reports. No source-frame coordinates, property addresses or personal
contact details are exported. Opaque identifiers preserve within-source groups.

Read `reports/phase_02_corpus.md` before interpreting area values: D1 gross area
is missing, D2 metric calibration is an explicit review-approved assumption, and D3
gross internal area includes its fixed toilet and kitchenette. NIA (8–50 m²) is the primary area measure. Complete-dwelling and scale filters
precede deduplication and the frozen experiment sample. All D3 shells remain
recorded; experiment flags are explicit. No FCI or FEA outcomes are produced in these preparation phases.

Furniture checks compare broad product cohorts only and do not validate moving
states or clearances. Table T3 preserves author schedules without optional ATUS
calibration. Raw data must be present for observed-source loader tests; the G1
recorded suite ran with all required data and no skips. The G1 review and Q-12 addendum authorize the corrections followed by
Phases 5–6, stopping at G2. Later gates still require their stated review.

## Corrected G2 method and frozen pilot

The G2 rerun preserves the 20 reviewed pilot keys and regenerates D3 with the same parameters. Kitchens are walkable with blocked fixtures; sanitary doors and kitchen areas have separate targets. Source gap repair changes circulation, not NIA. Rebuild the corrected full corpus before preparing the pilot.

```sh
python scripts/03_blocker_audit.py --config config/project.yaml
python scripts/05_candidates.py --config config/project.yaml
python scripts/06_revision.py --config config/project.yaml --prepare
python scripts/06_revision_pipeline.py --config config/project.yaml --rerun
python scripts/06_cut_comparison.py --config config/project.yaml
python scripts/06_revision_report.py --config config/project.yaml --export --render --run-tests
```

The six full 240-case arms compare 8-worker 0.10/0.20 m anchors, then 1/2/4 workers at 0.20 m, then a 30 s limit at the selected worker count. The 60 s arms are the time-limit reference. The selection rule is fixed in the pipeline; cases are independently revalidated and feasible incumbents are shared in both directions before comparisons. Invalid cases remain in FCI distributions at zero. Numeric libraries use one thread per process. CP-SAT concurrency is 1, 3, 7 or 14 for 8, 4, 2 or 1 search workers respectively.

The cut/restart comparison uses the same 20 units with H1/S2, holding geometry, greedy, anchors and limits fixed. It records both first positive incumbent time and first positive independently valid CP-search result.

Long case runs have project-local checkpoints. A resumed result is explicitly ineligible for throughput measurement. The pipeline preserves published/interrupted arms and gives a fresh rerun a numbered suffix; a clean clone does not treat a committed summary as a locally completed experiment. Multithreaded CP-SAT may return different incumbents despite a fixed seed.

After inspecting at least six current complete renders, including H1 S0/S2 at 8 and 12 m², update the paths, hashes and factual observations in `reports/pilot_visual_review.json`. Diagnose any structural failure in `reports/pilot_access_notes.json`. Then run:

```sh
python scripts/06_revision_report.py --config config/project.yaml --write-report
```

That command verifies the inspected image hashes. Every final layout and normal-day render is published with its hash. Historical pre-review results remain under `results/pilot/baseline_g2/` and at commit 67af2ee; the old `06_pilot.py`, `06_report.py` and `06_gate.py` describe that historical workflow. Use the revision commands for the corrected method.

The export records selected solver parameters, calibrates source-specific runtime to measured parallel throughput, adds 15%, and applies only the review-approved caps if Exp. A still exceeds 36 h. It preserves the uncapped sample and all valid D3 shells at NIA ≤20 m². Geometry-conversion config hashes remain provenance; the analysis config hash identifies the selected solve. Exp. K's separate workload projection is not a measured K result. Formal experiments remain unstarted until the author-requested review.

Before publication, stage only intended public files and run:

```sh
python scripts/check_publication.py --staged
```

The publication process additionally checks session-private terms supplied in
memory through an environment variable; do not save such terms in a config,
report, command file or commit. Use a neutral, nonpersonal Git author and
committer identity with an address such as `research-automation@example.invalid`.
Do not guess a GitHub noreply address: it can associate the commit with an
unrelated account. Existing upstream history is not rewritten.
