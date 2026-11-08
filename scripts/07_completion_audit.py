"""Report completed A solves and failed acceptance without changing research inputs."""
from datetime import datetime, timezone
import json
from pathlib import Path

import pandas as pd

from fea.io import prepare_cli, sha256_file, start_run, write_json


def main():
    args = prepare_cli(__doc__).parse_args()
    start_run(args, "07_completion_audit")
    if args.dry_run:
        print("Would audit completed A counts against prior connectivity evidence; no solves or acceptance changes.")
        return
    root = Path("results/expA")
    manifest = json.loads((root / "run.json").read_text())
    acceptance = json.loads((root / "solve_acceptance.json").read_text())
    assert manifest["status"] == "complete"
    execution = json.loads(Path("results/pilot/round3/execution_status.json").read_text())
    assert not acceptance["passed"] and execution["stage"] == "stopped_A_solve_acceptance_failed"
    frame = pd.read_csv(root / "solutions.csv", low_memory=False)
    assert len(frame) == manifest["expected_cases"] == acceptance["completed_cases"]
    assert not frame.duplicated(["unit_key", "household", "strategy"]).any()
    failed = frame.loc[~frame.validator_pass]
    assert len(failed) == acceptance["invalid_cases"]
    assert frame.status.value_counts().to_dict() == acceptance["status_distribution"]
    zero = frame.fci_validator <= 1e-9
    assert int(zero.sum()) == acceptance["zero_service_cases"]
    pivot = frame.pivot(index=["unit_key", "household"], columns="strategy", values="fci_validator")
    ordering = int(((pivot.S2 < pivot.S1 - 1e-8) | (pivot.S1 < pivot.S0 - 1e-8)).sum())
    assert ordering == acceptance["ordering_failures"]
    prior_path = Path("results/pilot/gap_connectivity_audit.csv")
    prior = pd.read_csv(prior_path)
    prior_failed = set(prior.loc[~prior.after_empty_access, "unit_key"])
    failed_units = set(failed.unit_key)
    timing = manifest["timing"]
    completed = datetime.fromtimestamp((root / "run.json").stat().st_mtime, timezone.utc)
    audit = dict(
        observed_at_utc=datetime.now(timezone.utc).isoformat(timespec="seconds"),
        completed_at_utc=completed.isoformat(timespec="seconds"),
        completion_timestamp_basis="final run-manifest write time on the execution filesystem",
        completed_cases=len(frame), expected_cases=manifest["expected_cases"],
        selected_units=manifest["selected_units"], acceptance=acceptance,
        solve_group_wall_hours=sum(row["wall_time_s"] for row in timing) / 3600,
        timing=timing, failed_units=len(failed_units),
        failed_units_by_source=failed.groupby("source").unit_key.nunique().to_dict(),
        failures_per_unit_distribution=failed.groupby("unit_key").size().value_counts().to_dict(),
        all_failed_layouts_empty=bool((failed.n_items == 0).all()),
        all_failures_structural=bool((failed.status == "STRUCTURAL_UNREACHABLE").all()),
        all_violations_fixed_service_access=bool(failed.violations.fillna("").map(
            lambda value: bool(value) and all(v.startswith("fixed_service_unreachable:") for v in value.split(";"))).all()),
        prior_connectivity_failed_units=len(prior_failed),
        failed_unit_set_equals_prior_connectivity_failures=failed_units == prior_failed,
        valid_zero_service_cases=int((zero & frame.validator_pass).sum()),
        provenance={name: sha256_file(Path(name)) for name in [
            "results/expA/solutions.csv", "results/expA/run.json",
            "results/expA/solve_acceptance.json", str(prior_path)]},
        disposition="Retain failed acceptance and all cases; diagnose original geometry versus raster/access rules before correction or inference.",
        downstream_started=False,
    )
    write_json(root / "completion_audit.json", audit)
    failed.groupby(["unit_key", "source", "nia_m2"]).size().rename("failed_cases").reset_index().to_csv(
        root / "structural_failure_units.csv", index=False)
    text = ["# Experiment A: completed solves, acceptance failed", "",
        f"Observed {audit['observed_at_utc']}. Final output written {audit['completed_at_utc']} (UTC).", "",
        f"Completed {len(frame)}/{manifest['expected_cases']} cases across {manifest['selected_units']} units. "
        f"Measured solve-group wall time: {audit['solve_group_wall_hours']:.3f} hours. "
        "Computation completion is not scientific acceptance.", "",
        "## Acceptance and diagnosis", "",
        f"- Acceptance passed: {acceptance['passed']}; invalid cases: {len(failed)} across {len(failed_units)} units.",
        f"- Strategy-ordering failures: {ordering}; zero-service cases: {int(zero.sum())} "
        f"({zero.mean():.3%}), including {audit['valid_zero_service_cases']} validator-valid zero-service cases.",
        f"- Failed units by source: {json.dumps(audit['failed_units_by_source'], sort_keys=True)}.",
        f"- All failed layouts are empty, structurally unreachable, and have only fixed-service-access violations: "
        f"{audit['all_failed_layouts_empty'] and audit['all_failures_structural'] and audit['all_violations_fixed_service_access']}.",
        f"- Exact match to the prior full-sample connectivity audit's failed-unit set: "
        f"{audit['failed_unit_set_equals_prior_connectivity_failures']} ({len(prior_failed)} units).", "",
        "The full-sample connectivity record already exposed these units. The launch gate checked pilot "
        "quality and runtime but did not resolve these recorded full-sample failures before launch. "
        "This is a preflight integration omission; the final acceptance stop correctly prevents downstream inference.", "",
        "The diagnostic label means fixed services are unreachable in the current empty-shell model. "
        "It does not establish whether the original dwelling is inaccessible or whether conversion, "
        "rasterization or the approach rule is responsible. No sample exclusions, geometry changes, "
        "validator relaxation or acceptance override have been applied.", "",
        "A1, A2 and K have not started. Next, inspect the affected original geometries and access masks, "
        "document the cause per unit, and validate any proposed correction before resuming. "
        "Existing solved layouts and failed outputs remain preserved. Repair/revalidation runtime is uncalibrated.", "",
        "## Reproduce", "", "`python scripts/07_completion_audit.py` reads the completed A table and "
        "prior connectivity audit. Input digests and timing are in `results/expA/completion_audit.json`.", ""]
    Path("reports/expA_completion_audit.md").write_text("\n".join(text), encoding="utf-8")
    print(json.dumps({k: audit[k] for k in ("completed_cases", "solve_group_wall_hours", "failed_units",
        "failed_unit_set_equals_prior_connectivity_failures")}))


if __name__ == "__main__":
    main()
