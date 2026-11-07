"""Continue only through reviewer-approved gates; retain every failed check."""
from datetime import datetime, timezone
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import time
from types import SimpleNamespace

from fea.io import prepare_cli, start_run, write_json, sha256_file


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def next_action(selection: dict) -> str:
    """An inadequate small arm, stale mechanism or excessive runtime is a stop."""
    if (all(selection.get(k) is True for k in ("accepted", "mechanism_pass", "source_quality_pass", "small_quality_pass"))
            and 0 < selection.get("projected_expA_hours", float("inf")) <= 36):
        return "run_A"
    if (selection.get("needs_large_fallback") and selection.get("small_quality_pass")
            and selection.get("mechanism_pass")):
        return "fallback"
    return "stop"


def main():
    parser = prepare_cli(__doc__)
    parser.add_argument("--launch-expA", action="store_true")
    parser.add_argument("--max-wait-seconds", type=int, default=14400)
    args = parser.parse_args()
    start_run(args, "06_round3_continue")
    if args.dry_run:
        print("Would wait for the fresh reference, check round-3 conditions, try the reviewed fallback if eligible, and launch A only with --launch-expA and accepted evidence. K is never launched.")
        return
    root = Path("results/pilot/round3")
    status_path = root/"execution_status.json"
    approved = root/"approved_project.yaml"
    approved_hash = sha256_file(approved)
    revision = load("scripts/06_revision.py", "revision_round3")
    code_hash = revision.signature()

    def status(stage, **extra):
        write_json(status_path, dict(stage=stage, observed_at_utc=datetime.now(timezone.utc).isoformat(timespec="seconds"),
            launch_expA_requested=args.launch_expA, K_started=False, **extra))

    def run(script, *options):
        result = subprocess.run([sys.executable, "scripts/"+script, *options])
        if result.returncode:
            status("command_failed", script=script, exit_code=result.returncode)
            raise SystemExit(result.returncode)

    status("waiting_for_reference")
    start = time.monotonic()
    while True:
        queue = json.loads(Path("results/pilot/round2/pilot_refresh_status.json").read_text())
        if queue["stage"] == "benchmarks_complete_acceptance_pending":
            break
        if queue["stage"] == "failed" or time.monotonic()-start > args.max_wait_seconds:
            status("stopped_before_acceptance", reason="benchmark failure or wait limit")
            return
        time.sleep(30)
    assert revision.signature() == code_hash, "Numerical code changed while waiting"
    assert sha256_file(approved) == approved_hash, "Approved configuration snapshot changed"
    # The preceding queue loaded the pre-review configuration; replace it only
    # after every queued arm finishes. The acceptance script checks equivalence.
    shutil.copyfile(approved, args.config)
    status("checking_acceptance")
    run("06_round3_acceptance.py")
    selection_path = Path("results/pilot/round2/production_selection.json")
    selection = json.loads(selection_path.read_text())
    if next_action(selection) == "fallback":
        status("running_reviewed_large_fallback")
        arm = "refresh_large_w2_s20_t60"
        if not (Path("results/pilot/benchmarks")/arm/"summary.json").exists():
            baseline = json.loads((root/"benchmark_base_config.json").read_text())
            revision.benchmark(baseline, SimpleNamespace(arm=arm, workers=2, limit=60,
                stride=.2, max_nia=None, max_jobs=None))
        run("06_round3_acceptance.py", "--large-arm", arm)
        selection = json.loads(selection_path.read_text())
    if next_action(selection) != "run_A":
        status("stopped_acceptance_failed", accepted=False)
        return
    if not args.launch_expA:
        status("accepted_A_not_launched", accepted=True)
        return
    status("running_expA", accepted=True)
    run("07_run_expA.py")
    acceptance = json.loads(Path("results/expA/solve_acceptance.json").read_text())
    if not acceptance["passed"]:
        status("stopped_A_solve_acceptance_failed", acceptance=acceptance)
        return
    status("running_A1_decomposition")
    run("07_decomposition.py")
    status("A_solves_and_A1_complete_other_phase7_analysis_and_A2_pending")


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        write_json("results/pilot/round3/execution_status.json", dict(stage="stopped_error",
            exception_type=type(error).__name__, K_started=False,
            observed_at_utc=datetime.now(timezone.utc).isoformat(timespec="seconds")))
        raise
