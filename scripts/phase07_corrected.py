"""Fail-closed loader for the reviewed F1 corrected and reused evidence."""
from copy import deepcopy
import json
from pathlib import Path
import numpy as np
import pandas as pd
from fea.config import config_hash
from fea.io import sha256_file
from phase07_f1 import check_cases, CHANGED_HOUSEHOLDS, UNCHANGED_HOUSEHOLDS


def verify_reused(original, combined):
    """Reused H1/H2 outcomes retain their exact old provenance and measurements."""
    keys=["unit_key","household","strategy"]
    a=original[original.household.isin(UNCHANGED_HOUSEHOLDS)].set_index(keys).sort_index()
    b=combined[combined.household.isin(UNCHANGED_HOUSEHOLDS)].set_index(keys).sort_index()
    if not a.index.equals(b.index):raise ValueError("H1/H2 reuse membership changed")
    for name in ["source","config_hash","code_hash"]:
        if not a[name].equals(b[name]):raise ValueError("H1/H2 provenance changed: "+name)
    for name in ["nia_m2","fci_validator","tb"]:
        if not np.allclose(a[name],b[name],atol=1e-12,rtol=0,equal_nan=False):raise ValueError("H1/H2 outcome changed: "+name)
    if not b.result_origin.eq("original_A_H1H2_verified_unaffected").all():raise ValueError("Reused rows lack origin labels")


def load_corrected(config, root=Path("results/expA_f1")):
    """Require a completed F1, immutable inputs and original provenance for reuse."""
    run=json.loads((root/"run.json").read_text());gate=json.loads((root/"acceptance.json").read_text());inputs=run["inputs"]
    if run["status"]!="complete" or not gate["passed"] or not gate["main_original_untouched"]:raise ValueError("F1 is incomplete or failed")
    if gate["input_provenance"]!=inputs or inputs["corrected_config_hash"]!=config_hash(config):raise ValueError("F1 configuration or provenance differs")
    for path,digest in [(root/"solutions.csv",gate["combined_sha256"]),(root/"H3H4_solutions.csv",gate["H3H4_sha256"]),
        (root/"sample.csv",inputs["sample_sha256"]),(root/"compatibility_acceptance.json",inputs["compatibility_sha256"]),
        (Path("results/expA/solutions.csv"),inputs["original_solutions_sha256"]),
        (Path("results/expA/evaluability.csv"),inputs["evaluability_sha256"])]:
        if sha256_file(path)!=digest:raise ValueError("F1 evidence file changed: "+path.as_posix())
    compat=json.loads((root/"compatibility_acceptance.json").read_text())
    if not compat["passed"] or compat["audit_sha256"]!=sha256_file(root/"H1H2_compatibility.csv"):raise ValueError("F1 reuse gate changed")
    frame=pd.read_csv(root/"solutions.csv",low_memory=False);sample=pd.read_csv(root/"sample.csv")
    check_cases(frame,sample.unit_key,config["households"]["main_households"])
    meta=sample.set_index("unit_key")
    if not frame.source.eq(frame.unit_key.map(meta.source)).all() or not np.allclose(frame.nia_m2,frame.unit_key.map(meta.nia_m2),rtol=0,atol=1e-7):raise ValueError("F1 source or area metadata changed")
    e1=pd.read_csv("results/expA/evaluability.csv")
    if set(sample.unit_key)!=set(e1.loc[e1.evaluable,"unit_key"]):raise ValueError("F1 changed E1 membership")
    original=pd.read_csv("results/expA/solutions.csv",low_memory=False)
    verify_reused(original[original.unit_key.isin(sample.unit_key)],frame)
    changed=frame[frame.household.isin(CHANGED_HOUSEHOLDS)]
    if set(changed.budget_group)!={"small","large"} or not changed.budget_group.eq(np.where(changed.nia_m2<=20+1e-8,"small","large")).all():raise ValueError("F1 budget-group membership changed")
    if not changed.result_origin.eq("F1_corrected_rerun").all():raise ValueError("Corrected rows lack re-solve origin")
    for group,settings in run["production_settings"].items():
        local=deepcopy(config);local["solver"].update({k:settings[k] for k in ["time_limit_s","num_workers"]})
        local["raster"]["anchor_stride_m"]=settings["anchor_stride_m"]
        if not changed.loc[changed.budget_group==group,"config_hash"].eq(config_hash(local)).all():raise ValueError("F1 production budget hash changed")
    return frame,gate
