"""Continue accepted F1 into numerical F2 analysis, without altering the active solver."""
import json
from pathlib import Path
import subprocess
import sys
import time
from datetime import datetime,timezone
from fea.io import prepare_cli,start_run,write_json


def main():
    args=prepare_cli(__doc__).parse_args();start_run(args,"07_f2_continue")
    if args.dry_run:print("Would wait for this F1 run to complete and pass its gate, then run F2 analysis. A failed or replaced F1 stops continuation.");return
    import fcntl
    root=Path("results/expA_f1");run_path=root/"run.json";expected=json.loads(run_path.read_text())["inputs"]
    def record(status):write_json(root/"F2_continuation.json",dict(status=status,F1_inputs=expected,observed_at_utc=datetime.now(timezone.utc).isoformat(timespec="seconds")))
    with Path(".tmp/f2_execution.lock").open("a") as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        record("waiting_for_F1")
        while True:
            run=json.loads(run_path.read_text())
            if run["inputs"]!=expected or run["status"] not in ["running","complete"]:
                record("stopped_F1_failed_or_replaced");raise ValueError("F1 failed or changed while F2 waited")
            if run["status"]=="complete":break
            time.sleep(45)
        record("running_numerical_F2")
        try:subprocess.run([sys.executable,"-u","scripts/07_f2_analysis.py","--config",args.config],check=True)
        except Exception:
            record("failed_numerical_F2");raise
        record("numerical_F2_complete_visual_and_layout_review_pending")


if __name__=="__main__":main()
