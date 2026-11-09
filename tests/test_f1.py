from copy import deepcopy
from pathlib import Path
import sys
import numpy as np
import pandas as pd
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from fea.config import config_hash
from phase07_f1 import original_configuration,check_cases,CHANGED_HOUSEHOLDS


def test_only_reviewed_caps_may_change():
    original={"furniture":{"max_instances":{"default":1}},"seed":42}
    corrected=deepcopy(original);corrected["furniture"]["max_instances"].update(single_bed=2,wall_bed_single=2)
    assert original_configuration(corrected,config_hash(original))==original
    assert corrected["furniture"]["max_instances"]["single_bed"]==2
    corrected["seed"]=43
    with pytest.raises(ValueError):original_configuration(corrected,config_hash(original))


def test_f1_rejects_invalid_incomplete_or_unordered_cases():
    rows=[dict(unit_key='u',household=h,strategy=s,fci_validator=i/4,validator_pass=True) for h in CHANGED_HOUSEHOLDS for i,s in enumerate(['S0','S1','S2'])]
    frame=pd.DataFrame(rows);assert check_cases(frame,['u'])["zero_cases"]==2
    with pytest.raises(ValueError):check_cases(frame.iloc[:-1],['u'])
    bad=frame.copy();bad.loc[0,'fci_validator']=.9
    with pytest.raises(ValueError):check_cases(bad,['u'])
    bad=frame.copy();bad.loc[0,'fci_validator']=np.nan
    with pytest.raises(ValueError):check_cases(bad,['u'])
