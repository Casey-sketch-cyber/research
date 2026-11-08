# Experiment A: completed solves, acceptance failed

Observed 2026-11-08T15:52:21+00:00. Final output written 2026-11-08T10:08:07+00:00 (UTC).

Completed 32904/32904 cases across 2742 units. Measured solve-group wall time: 25.403 hours. Computation completion is not scientific acceptance.

## Acceptance and diagnosis

- Acceptance passed: False; invalid cases: 1392 across 116 units.
- Strategy-ordering failures: 0; zero-service cases: 1546 (4.699%), including 154 validator-valid zero-service cases.
- Failed units by source: {"D1": 105, "D2": 11}.
- All failed layouts are empty, structurally unreachable, and have only fixed-service-access violations: True.
- Exact match to the prior full-sample connectivity audit's failed-unit set: True (116 units).

The full-sample connectivity record already exposed these units. The launch gate checked pilot quality and runtime but did not resolve these recorded full-sample failures before launch. This is a preflight integration omission; the final acceptance stop correctly prevents downstream inference.

The diagnostic label means fixed services are unreachable in the current empty-shell model. It does not establish whether the original dwelling is inaccessible or whether conversion, rasterization or the approach rule is responsible. No sample exclusions, geometry changes, validator relaxation or acceptance override have been applied.

A1, A2 and K have not started. Next, inspect the affected original geometries and access masks, document the cause per unit, and validate any proposed correction before resuming. Existing solved layouts and failed outputs remain preserved. Repair/revalidation runtime is uncalibrated.

## Reproduce

`python scripts/07_completion_audit.py` reads the completed A table and prior connectivity audit. Input digests and timing are in `results/expA/completion_audit.json`.
