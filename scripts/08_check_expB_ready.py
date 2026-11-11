"""Verify the frozen B sample and corrected main evidence after F3 acceptance."""
from copy import deepcopy
from datetime import datetime, timezone
import json
from pathlib import Path
import numpy as np
import pandas as pd
from tqdm import tqdm
from fea.config import config_hash
from fea.geometry.unit import Unit
from fea.geometry.raster import rasterize
from fea.households import parse_households
from fea.validate import validate_layout
from fea.io import prepare_cli,start_run,write_json,sha256_file
from phase07_corrected import load_corrected
from phase08_sampling import select_instances


def main():
    args=prepare_cli(__doc__).parse_args();config,_,_=start_run(args,"08_check_expB_ready")
    if args.dry_run: print("Would verify accepted F3, preserve the exact frozen 200 B pairs, and independently revalidate their corrected main references.");return
    f3root=Path("results/expA_f3");f3=json.loads((f3root/"package_acceptance.json").read_text())
    if not f3["passed"] or not f3["full_F3_package_complete"]:raise ValueError("F3 package is incomplete")
    for path,key in [(f3root/"report_acceptance.json","numerical_acceptance_sha256"),(Path("config/f3_visual_review.json"),"visual_review_sha256"),(f3root/"solutions.csv","F3_solutions_sha256")]:
        if sha256_file(path)!=f3[key]:raise ValueError("F3 package evidence changed")
    numerical=json.loads((f3root/"report_acceptance.json").read_text())
    if not numerical["passed"]:raise ValueError("F3 numerical gate failed")
    for path,digest in {**numerical["inputs"],**numerical["outputs"]}.items():
        if sha256_file(Path(path))!=digest:raise ValueError("F3 analysis input/output changed")
    root=Path("results/expB");manifest=json.loads((root/"sample_manifest.json").read_text());sample=pd.read_csv(root/"instances.csv")
    e1=Path("results/expA/evaluability.csv")
    if sha256_file(root/"instances.csv")!=manifest["instances_sha256"] or sha256_file(e1)!=manifest["evaluability_sha256"]:raise ValueError("Frozen B sample/E1 changed")
    for path,digest in manifest["implementation"].items():
        if sha256_file(Path(path))!=digest:raise ValueError("Original sample implementation changed")
    regenerated,_,_=select_instances(pd.read_csv(e1),config["households"]["main_households"],config["seed"])
    pd.testing.assert_frame_equal(sample,regenerated,check_exact=False,rtol=0,atol=1e-8)
    solutions,gate=load_corrected(config);keys=["unit_key","household","strategy"]
    reference=sample[keys+["area_tercile"]].merge(solutions,on=keys,how="left",validate="one_to_one")
    if len(reference)!=200 or reference.fci_validator.isna().any():raise ValueError("Missing corrected B reference")
    run=json.loads(Path("results/expA_f1/run.json").read_text());old_run=json.loads(Path("results/expA/run.json").read_text())
    old_config=json.loads(Path("results/expA_f1/original_config_snapshot.json").read_text())
    corpus=pd.read_parquet(Path(config["paths"]["processed"])/"corpus_units.parquet",columns=["unit_key","unit_json"]).set_index("unit_key")
    households=parse_households(config["households"],config["furniture"]);audits=[]
    for row in tqdm(reference.itertuples(index=False),total=len(reference),desc="B corrected-reference audit"):
        reused=row.result_origin=="original_A_H1H2_verified_unaffected"
        selected_run=old_run if reused else run;local=deepcopy(old_config if reused else config)
        settings=run["production_settings"][row.budget_group]
        local["solver"].update({k:settings[k] for k in ["time_limit_s","num_workers"]});local["raster"]["anchor_stride_m"]=settings["anchor_stride_m"]
        path=Path(selected_run["cache"])/row.budget_group/"shared"/row.layout_file;layout=json.loads(path.read_text())
        if config_hash(local)!=row.config_hash or layout["config_hash"]!=row.config_hash or any(layout[k]!=getattr(row,k) for k in keys):raise ValueError("B reference layout identity/provenance differs")
        unit=Unit.from_dict(json.loads(corpus.loc[row.unit_key,"unit_json"]))
        grid=rasterize(unit,config["raster"]["resolution_m"],config["furniture"]["meta"]["walking_width"],config["raster"]["source_gap_close_m"])
        checked=validate_layout(layout,grid,local,households[row.household])
        corrected=validate_layout(layout,grid,config,households[row.household])
        if not checked["pass"] or not corrected["pass"] or not np.allclose([checked["fci"],corrected["fci"],layout["fci"]],row.fci_validator,atol=1e-8,rtol=0):raise ValueError("B corrected reference revalidation failed")
        audits.append(dict(unit_key=row.unit_key,household=row.household,strategy=row.strategy,validator_pass=True,
            fci_validator=corrected["fci"],result_origin=row.result_origin,actual_original_config_hash=row.config_hash,
            checked_main_config_hash=config_hash(config),layout_sha256=sha256_file(path)))
    reference.to_csv(root/"corrected_main_reference.csv",index=False);pd.DataFrame(audits).to_csv(root/"reference_revalidation.csv",index=False)
    result=dict(passed=True,instances=len(reference),independently_revalidated=len(audits),
        corrected_H3H4_instances=int(reference.result_origin.eq("F1_corrected_rerun").sum()),
        reused_verified_H1H2_instances=int(reference.result_origin.eq("original_A_H1H2_verified_unaffected").sum()),
        sample_sha256=manifest["instances_sha256"],F1_solutions_sha256=gate["combined_sha256"],
        F3_package_sha256=sha256_file(f3root/"package_acceptance.json"),main_config_hash=config_hash(config),
        outputs={p:sha256_file(root/p) for p in ["corrected_main_reference.csv","reference_revalidation.csv"]},
        implementation_sha256=sha256_file(Path(__file__)),checked_at_utc=datetime.now(timezone.utc).isoformat(timespec="seconds"),
        algorithm_comparison_started=False,limitations="This is input preparation, not an algorithm comparison or new CP-SAT runtime measurement.")
    write_json(root/"readiness.json",result);print(json.dumps(result))


if __name__=="__main__":main()
