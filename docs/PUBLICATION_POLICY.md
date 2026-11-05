# Publication boundary

The author's current instruction permits all research-related content, including public study regions, dataset names and scholarly references. It excludes unrelated equipment identifiers, physical server location, connection details, personal information and machine-specific filesystem paths.

Only code, configurations, small derived outputs and sanitized reports are published. Raw downloads, credentials, SSH transport, caches, unfiltered logs and local provenance mappings remain outside Git. Source-frame coordinates and address tables are unnecessary for the analysis and are excluded from public outputs. Plan geometry is normalized before publication. Environment reports contain only software versions and non-identifying compute specifications needed to interpret reproducibility and runtime.

Before each push, stage an explicit file list and run:

```sh
python scripts/check_publication.py --config config/project.yaml --staged
git diff --cached --check
```

The audit scans the staged bytes, rejects private directories and oversized files, and can accept session-only private terms via the environment variable `FEA_PRIVATE_TERMS_JSON`. Never save those values in a configuration or log. Automated scanning supplements an inspection of changed files, images, document metadata and Git commit metadata.

Original open-source copyright notices and research citations are retained. New automated commits use a nonpersonal author and committer identity. No project code needs SSH credentials or a particular host to reproduce the work.
