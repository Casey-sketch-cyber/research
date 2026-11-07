"""Refresh the frozen pilot after search corrections without starting formal runs."""
from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys

import pandas as pd

from fea.config import config_hash
from fea.io import prepare_cli, start_run, write_json


def main() -> None:
    """Run serial benchmark arms, preserving their resumable per-case checkpoints."""
    args = prepare_cli(__doc__).parse_args()
    config, _, _ = start_run(args, "06_round2_pilot_queue")
    root = Path("results/pilot/round2")
    selection = json.loads((root/"small_budget_assessment.json").read_text())
    small_workers, small_limit = selection["num_workers"], selection["time_limit_s"]
    plan = [dict(arm="refresh_large_w1_s20_t30", workers=1, limit=30, stride=.2, max_nia=None),
            dict(arm=f"refresh_small_w{small_workers}_s10_t{small_limit}", workers=small_workers,
                 limit=small_limit, stride=.1, max_nia=20),
            dict(arm="refresh_reference_w8_s10_t60", workers=8, limit=60, stride=.1, max_nia=None)]
    if args.dry_run:
        print(json.dumps({"plan": plan, "formal_experiments_started": False}))
        return
    spec = importlib.util.spec_from_file_location("pilot_driver", "scripts/06_revision.py")
    driver = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(driver)
    signature = driver.signature()
    completed = []
    state = dict(plan=plan, completed_arms=completed, numerical_hash=signature,
                 stage="starting", formal_experiments_started=False)
    for settings in plan:
        assert driver.signature() == signature, "Numerical implementation changed during queue"
        arm = settings["arm"]
        directory = Path("results/pilot/benchmarks")/arm
        expected_config = deepcopy(config)
        expected_config["solver"].update(num_workers=settings["workers"],
            time_limit_s=settings["limit"], reachability_round_s=5.)
        expected_config["raster"]["anchor_stride_m"] = settings["stride"]
        digest = config_hash(expected_config)
        command = [sys.executable, "scripts/06_revision.py", "--config", str(args.config),
            "--arm", arm, "--workers", str(settings["workers"]),
            "--limit", str(settings["limit"]), "--stride", str(settings["stride"])]
        if settings["max_nia"] is not None:
            command += ["--max-nia", str(settings["max_nia"])]
        state.update(stage="running", current_arm=arm)
        write_json(root/"pilot_refresh_status.json", state)
        summary_path = directory/"summary.json"
        if not summary_path.exists():
            with (Path("logs")/(arm+".log")).open("a", encoding="utf-8") as stream:
                result = subprocess.run(command, stdout=stream, stderr=subprocess.STDOUT)
            if result.returncode:
                state.update(stage="failed", exit_code=result.returncode)
                write_json(root/"pilot_refresh_status.json", state)
                raise SystemExit(result.returncode)
        summary = json.loads(summary_path.read_text())
        assert summary["code_hash"] == signature and summary["config_hash"] == digest
        assert summary["max_nia_m2"] == settings["max_nia"]
        frame = pd.read_csv(directory/"cases.csv")
        assert len(frame) == summary["expected_cases"] == summary["completed_cases"]
        assert frame.validator_pass.all() and not frame.duplicated(["unit_key", "household", "strategy"]).any()
        completed.append(arm)
    state.update(stage="benchmarks_complete_acceptance_pending", current_arm=None)
    write_json(root/"pilot_refresh_status.json", state)
    print(json.dumps(state))


if __name__ == "__main__":
    main()
