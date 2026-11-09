"""Freeze the reviewed S2 algorithm-comparison sample after completed A2."""
import json
from pathlib import Path
import pandas as pd
from fea.io import prepare_cli,start_run,write_json,sha256_file
from phase08_sampling import select_instances


def main():
    args=prepare_cli(__doc__).parse_args();config,_,_=start_run(args,"08_prepare_expB")
    if args.dry_run:print("Would freeze 200 E1-evaluable pairs using geometry and household labels only.");return
    accepted=json.loads(Path("results/expA2/report_acceptance.json").read_text())
    visual=json.loads(Path("config/a2_visual_review.json").read_text())
    if not accepted["passed"] or accepted.get("visual_review_pending",True) or not visual["passed"]:raise ValueError("A2 analysis or visual review incomplete")
    for name,digest in visual["hashes"].items():
        if sha256_file(Path(name))!=digest:raise ValueError("A2 reviewed artifact changed")
    e1=Path("results/expA/evaluability.csv")
    if sha256_file(e1)!=accepted["evaluability_sha256"]:raise ValueError("E1 changed")
    sample,allocation,bounds=select_instances(pd.read_csv(e1),config["households"]["main_households"],config["seed"])
    root=Path("results/expB");root.mkdir(exist_ok=True,parents=True)
    path=root/"instances.csv"
    if path.exists() and path.read_text()!=sample.to_csv(index=False):raise ValueError("Existing B sample differs; preserve it")
    sample.to_csv(path,index=False);allocation.to_csv(root/"sampling_allocation.csv",index=False);bounds.to_csv(root/"area_terciles.csv",index=False)
    write_json(root/"sample_manifest.json",dict(seed=config["seed"],instances=len(sample),strata=len(allocation),strategy="S2",
        source_counts=sample.source.value_counts().to_dict(),household_counts=sample.household.value_counts().to_dict(),
        evaluability_sha256=sha256_file(e1),instances_sha256=sha256_file(path),
        implementation={p:sha256_file(Path(p)) for p in ["scripts/08_prepare_expB.py","scripts/phase08_sampling.py"]},
        selection="Balanced quotas across source x within-source NIA tercile x household; fixed seed for quotas and units; area ties kept together after rounding NIA to eight decimals.",
        outcome_files_read=[],algorithm_results_started=False))
    print(json.dumps(dict(instances=len(sample),strata=len(allocation),source_counts=sample.source.value_counts().to_dict(),algorithm_results_started=False)))


if __name__=="__main__":main()
