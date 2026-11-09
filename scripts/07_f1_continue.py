"""Run the full compatibility gate before the reviewed F1 re-solve."""
from pathlib import Path
import subprocess
import sys
from fea.io import prepare_cli,start_run


def main():
    args=prepare_cli(__doc__).parse_args();start_run(args,"07_f1_continue")
    if args.dry_run:
        print("Would execute compatibility then F1; any failure stops continuation.");return
    # Advisory lock is released automatically if the execution process exits.
    import fcntl
    with Path(".tmp/f1_execution.lock").open("a") as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        for path in ["scripts/07_f1_compatibility.py","scripts/07_run_f1.py"]:
            subprocess.run([sys.executable,"-u",path,"--config",args.config],check=True)


if __name__=="__main__":main()
