# Reproducing the data and corpus package

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
is missing, D2 metric calibration is an explicit assumption for review, and D3
gross internal area includes its fixed toilet and kitchenette. The smallest D3
shells remain available even when excluded from the main furnishable-area
corpus. No FCI or FEA outcomes are produced in these preparation phases.

Before publication, stage only intended public files and run:

```sh
python scripts/check_publication.py --staged
```

The publication process additionally checks session-private terms supplied in
memory through an environment variable; do not save such terms in a config,
report, command file or commit. Use a neutral, nonpersonal Git author and
committer identity. Existing upstream history is not rewritten.
