"""Configuration transition and exact-case acceptance for reviewed F1 reruns."""
from copy import deepcopy
import numpy as np
import pandas as pd
from fea.config import config_hash

CHANGED_HOUSEHOLDS=["H3_couple_one_remote","H4_parent_child"]
UNCHANGED_HOUSEHOLDS=["H1_single_commuter","H2_single_remote_worker"]


def original_configuration(corrected,original_hash):
    """Permit exactly the two reviewed instance-cap additions, no numerical drift."""
    previous=deepcopy(corrected)
    for key in ("single_bed","wall_bed_single"):
        if previous["furniture"]["max_instances"].get(key)!=2:
            raise ValueError("F1 requires both reviewed bed instance limits at two")
        previous["furniture"]["max_instances"].pop(key)
    if config_hash(previous)!=original_hash:
        raise ValueError("F1 transition includes unreviewed configuration changes")
    return previous


def check_cases(frame,unit_keys,households=CHANGED_HOUSEHOLDS):
    """Require complete finite, valid triplets without discarding genuine zeros."""
    keys=["unit_key","household","strategy"]
    expected=pd.MultiIndex.from_product([sorted(unit_keys),households,["S0","S1","S2"]],names=keys)
    actual=pd.MultiIndex.from_frame(frame[keys])
    if actual.has_duplicates or len(actual)!=len(expected) or len(expected.difference(actual)):
        raise ValueError("F1 missing, duplicate or unexpected cases")
    values=frame.fci_validator.to_numpy(float)
    if not frame.validator_pass.eq(True).all() or not np.isfinite(values).all() or np.any(values < -1e-9) or np.any(values > 1+1e-9):
        raise ValueError("F1 invalid layout or score")
    wide=frame.pivot(index=["unit_key","household"],columns="strategy",values="fci_validator")
    if ((wide.S1 < wide.S0-1e-8)|(wide.S2 < wide.S1-1e-8)).any():raise ValueError("F1 strategy ordering failed")
    return dict(passed=True,units=len(unit_keys),completed_cases=len(frame),expected_cases=len(expected),
        invalid_cases=0,ordering_failures=0,zero_cases=int((values<=1e-9).sum()))
