"""Publish bounded formal-A progress without extrapolating a nonuniform case prefix."""
from datetime import datetime, timezone
import json
from pathlib import Path

import pandas as pd

from fea.io import prepare_cli, start_run, write_json


def main():
    args = prepare_cli(__doc__).parse_args()
    start_run(args, "07_status")
    if args.dry_run:
        print("Would record completed A case counts and the prior budget; no partial scores.")
        return
    root = Path("results/expA")
    manifest = json.loads((root/"run.json").read_text())
    progress = json.loads((root/"progress.json").read_text())
    observed = datetime.now(timezone.utc)
    marker = root/"monitor_metadata.json"
    run_mtime = (Path(manifest["cache"])/"run.json").stat().st_mtime
    if not marker.exists():
        started = datetime.fromtimestamp(run_mtime, timezone.utc)
        write_json(marker, dict(run_started_at_utc=started.isoformat(timespec="seconds"),
            timestamp_basis="initial observed run-manifest timestamp; a future resume must be identified separately",
            initial_manifest_mtime=run_mtime,
            code_hash=manifest["code_hash"]))
    metadata = json.loads(marker.read_text())
    assert metadata["code_hash"] == manifest["code_hash"]
    complete = manifest.get("status") == "complete"
    ended = datetime.fromtimestamp((root/"run.json").stat().st_mtime, timezone.utc) if complete else observed
    elapsed = (ended-datetime.fromisoformat(metadata["run_started_at_utc"])).total_seconds()/3600
    expected = manifest["expected_cases"]
    completed = progress["completed_cases"]
    assert 0 <= completed <= expected
    selection = manifest["production_settings"]
    sample = pd.read_csv(selection["sample_path"])
    group = progress["group"]
    small_cases = int((sample.nia_m2 <= 20+1e-8).sum())*12
    group_expected = small_cases if group == "small" else expected-small_cases
    group_completed = completed if group == "small" else completed-small_cases
    prior = selection["projected_expA_hours"]
    acceptance_path = root/"solve_acceptance.json"
    acceptance = json.loads(acceptance_path.read_text()) if acceptance_path.exists() else None
    package_path = root/"analysis_package_acceptance.json"
    package = json.loads(package_path.read_text()) if package_path.exists() else {}
    analysis_passed = package.get("passed", False)
    resumed = abs(run_mtime-metadata["initial_manifest_mtime"]) > 1.5
    remaining = (0. if analysis_passed or (acceptance and acceptance["passed"]) else None) if complete else prior-elapsed if prior > elapsed and not resumed else None
    record = dict(observed_at_utc=observed.isoformat(timespec="seconds"),
        run_started_at_utc=metadata["run_started_at_utc"], status=manifest.get("status"),
        completed_cases=completed, expected_cases=expected, completion_fraction=completed/expected,
        active_group=group, group_completed_cases=group_completed, group_expected_cases=group_expected,
        elapsed_wall_hours=elapsed, prior_projected_total_hours=prior,
        resumed_since_initial_observation=resumed, final_validation_acceptance_pending=acceptance is None,
        final_validation_acceptance_passed=acceptance["passed"] if acceptance else None,
        completed_at_utc=ended.isoformat(timespec="seconds") if complete else None,
        completion_timestamp_basis="final execution run-manifest write time" if complete else None,
        repair_runtime_pending=bool(complete and acceptance and not acceptance["passed"] and not analysis_passed),
        analysis_package_passed=analysis_passed,
        remaining_hours_relative_to_prior_projection=remaining,
        numerical_code_hash=manifest["numerical_hash"], source_quality_pass=selection["source_quality_pass"],
        small_quality_pass=selection["small_quality_pass"], partial_score_means_published=False,
        estimate_limit="Subtracts elapsed time from the accepted pilot budget; it is not a live throughput ETA. Cases are ordered by size/source and early fractions cannot be linearly extrapolated.")
    write_json(root/"progress_snapshot.json", record)
    section = ["<!-- EXPA_PROGRESS_BEGIN -->", "## Dated formal-run progress", "",
        f"Observed {record['observed_at_utc']}; run began {record['run_started_at_utc']}.", "",
        f"Status: {record['status']}. Completed solve cases: {completed}/{expected} ({completed/expected:.2%}). Active group: {group}, {group_completed}/{group_expected} cases. Elapsed: {elapsed:.3f} h. These are completion counts, not a final all-layouts-pass acceptance.", "",
        f"Final solve acceptance: {record['final_validation_acceptance_passed']}. Separate analysis package accepted: {analysis_passed}. Repair/revalidation runtime pending: {record['repair_runtime_pending']}. See the completion audit when present.", "",
        f"The accepted prior A projection is {prior:.3f} h. The case prefix is not representative of the remaining workload; do not convert its overall completion percentage into a linear ETA. No partial score means or final research conclusions are reported.",
        "<!-- EXPA_PROGRESS_END -->"]
    phase = Path("reports/phase_07_expA.md")
    text = phase.read_text(encoding="utf-8")
    begin, end = "<!-- EXPA_PROGRESS_BEGIN -->", "<!-- EXPA_PROGRESS_END -->"
    if begin in text:
        left, tail = text.split(begin, 1)
        _, right = tail.split(end, 1)
        text = left+"\n".join(section)+right
    else:
        text += "\n\n"+"\n".join(section)+"\n"
    phase.write_text(text, encoding="utf-8")
    print(json.dumps(record))


if __name__ == "__main__":
    main()
