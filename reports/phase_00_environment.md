# Phase 00: Environment

**Status:** COMPLETE. No research experiment results have been produced. Config hash and measurements are recorded in `reports/environment.json`.

## 1. Checklist (from PROCEDURES.md)
- [x] Create an isolated Python 3.11 environment and install core dependencies.
- [x] Record sanitized OS, CPU, effective cores, memory, GPU and internet checks.
- [x] Save dependency versions and minimum requirements.

## 2. Acceptance checks
| Check | Result | Evidence |
|---|---|---|
| pytest runs | PASS | `reports/environment.json`: exit code 0; 3 passed |
| ortools and shapely import | PASS | `reports/environment.json`: imports PASS |
| ENVIRONMENT.md exists | PASS | `reports/ENVIRONMENT.md` |

## 3. Key numbers
| Quantity | Value | Source |
|---|---|---|
| Python | 3.11.18 | `reports/environment.json` |
| Effective CPU cores | 14 | `reports/environment.json` |
| Memory limit | 90 GiB | `reports/environment.json` |
| Environment-check runtime | 25.306 s | `reports/environment.json` |

## 4. Deviations from the plan
Public artifacts exclude connection details, usernames, hostnames, absolute filesystem paths, source addresses and geolocation. Raw data and operational transport files remain outside version control. Public plan identifiers will be opaque, while local provenance mappings remain private. Dataset-level attribution and published research geography are retained where needed for scientific provenance.

The observed hardware differs from the planning example; only effective resource limits will drive parallelism. The D2 repository landing-page probe timed out, while other source probes returned HTTP 200. Phase 1 uses the official raw-download endpoint, with bounded retries and checksum validation; any download failure will be reported, not replaced by synthetic data. The package lock omits the editable checkout path and includes build/runtime package versions.

## 5. Decisions
- The initial execution scope is Phases 0–4, ending at the required G1 review.
- GPU dependencies are deferred until their experimental phase.

## 6. Open questions for the reviewer
- The author-led novelty check is not yet present; it is not represented as complete.

## 7. Runtime and resources
The environment-check runtime above excludes installation. Installation wall time was not instrumented. GPU training packages were not installed; the GPU remains unused by this project.

## 8. Files added or changed
- Environment report, dependency manifests, package configuration and common CLI helpers.
- Publication policy/audit, configuration and publication-boundary tests.
