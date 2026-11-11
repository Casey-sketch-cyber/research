"""Run the fixed B timing pilot, then the full benchmark after its acceptance."""
import os
import subprocess
from datetime import datetime,timezone
from pathlib import Path
from fea.io import prepare_cli,start_run,write_json


def main():
    args=prepare_cli(__doc__).parse_args();start_run(args,'08_continue_expB')
    if args.dry_run:print('Would run the tested 12-pair pilot and continue the identical 200-pair B benchmark after its hash-bound gate passes.');return
    import fcntl
    with Path('.tmp/expB_pipeline.lock').open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        for stage,extra in [('pilot',['--pilot']),('full',[])]:
            write_json('results/expB/continuation.json',dict(stage=stage,status='running',observed_at_utc=datetime.now(timezone.utc).isoformat(timespec='seconds')))
            result=subprocess.run([os.sys.executable,'scripts/08_run_expB.py','--config',args.config,*extra])
            if result.returncode:
                write_json('results/expB/continuation.json',dict(stage=stage,status='failed',exit_code=result.returncode,observed_at_utc=datetime.now(timezone.utc).isoformat(timespec='seconds')))
                raise SystemExit(result.returncode)
        write_json('results/expB/continuation.json',dict(status='complete',stage='full',analysis_pending=True,observed_at_utc=datetime.now(timezone.utc).isoformat(timespec='seconds')))


if __name__=='__main__':main()
