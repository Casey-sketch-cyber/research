"""Record phase-7 analysis acceptance and A2 progress without partial outcome claims."""
from datetime import datetime, timezone
import json
from pathlib import Path
from fea.io import prepare_cli, start_run, write_json


def main():
    args=prepare_cli(__doc__).parse_args()
    start_run(args,"07_review_status")
    if args.dry_run:
        print("Would snapshot reviewed A1 acceptance and completed A2 checkpoints.")
        return
    root=Path("results/expA2")
    read=lambda p: json.loads(p.read_text()) if p.exists() else {}
    run=read(root/"run.json")
    progress=read(root/"progress.json")
    accepted=read(root/"acceptance.json")
    cache=Path(run["cache"]) if run else None
    checkpoints=list(cache.glob("D*.json")) if cache else []
    started=datetime.fromtimestamp((cache/"run.json").stat().st_mtime,timezone.utc) if cache else None
    record=dict(observed_at_utc=datetime.now(timezone.utc).isoformat(timespec="seconds"),
        A1_package_passed=read(Path("results/expA/analysis_package_acceptance.json")).get("passed",False),
        A2_status=run.get("status","not_started"),A2_started_at_utc=started.isoformat(timespec="seconds") if started else None,
        start_timestamp_basis="initial variant-cache manifest timestamp",A2_units=run.get("units"),
        A2_expected_cases=run.get("expected_cases"),A2_completed_triplet_cases=progress.get("completed_cases",0),
        A2_strategy_checkpoints=len(checkpoints),A2_final_acceptance_passed=accepted.get("passed"),
        checkpoint_limit="Individual strategy checkpoints precede complete triplet revalidation/sharing; they are not final accepted case counts.",
        partial_outcome_claims=False,
        next="Complete A2 and its comparison, then B, D/R/ablations, C, reduced H1+H3 K, HK, literature, G3.")
    write_json(root/"status_snapshot.json",record)
    print(json.dumps(record))


if __name__=="__main__":
    main()
