"""Regression tests for reviewed paired analysis and reuse provenance."""
import importlib.util
import json
from pathlib import Path
import numpy as np
import pandas as pd
import pytest
from phase07_corrected import verify_reused


def module():
    spec=importlib.util.spec_from_file_location("f2_under_test","scripts/07_f2_analysis.py")
    value=importlib.util.module_from_spec(spec);spec.loader.exec_module(value);return value


def test_equal_scores_remain_zero_and_primary_statistics_are_paired(tmp_path):
    analysis=module()
    frame=pd.DataFrame(dict(unit_key=["a","b","c","d"],source=["D3"]*4,nia_m2=[8.,10.,12.,14.],
        S0=[.2,.4,.6,1.],S1=[.3,.5,.6,1.],S2=[.4,.7,.6,1.]))
    destination=tmp_path/"group"
    job=("D3","H3_couple_one_remote",frame,dict(n=20,ci=.95),[.8,.9,1.],42,str(destination))
    analysis.group_job(job)
    cases=pd.read_csv(destination/"paired_equivalent_area.csv")
    assert cases.loc[cases.unit_key.isin(["c","d"]),"delta_ea_m2"].eq(0).all()
    primary=pd.read_csv(destination/"primary_effects.csv");total=primary[(primary.stratum=="overall")&(primary.comparison=="S2-S0")].iloc[0]
    assert total.mean_difference==pytest.approx(.125)
    assert total.share_improved==pytest.approx(.5)
    assert np.isfinite(total.mean_difference_ci_lo)
    # Paired metric output uses two references and never subtracts the unit's own area.
    assert set(cases.method)=={"median_bin_cummax","mean_isotonic"}
    assert "saving_m2" not in cases
    assert analysis.group_job(job)==str(destination)
    (destination/"primary_effects.csv").write_text("changed")
    with pytest.raises(ValueError,match="checkpoint changed"):analysis.group_job(job)


def test_reuse_cannot_relabel_old_scores_with_corrected_hash():
    old=pd.DataFrame([dict(unit_key="a",household="H1_single_commuter",strategy="S0",source="D3",nia_m2=10.,
        fci_validator=.5,tb=0.,config_hash="old",code_hash="old_code")])
    reused=old.copy();reused["result_origin"]="original_A_H1H2_verified_unaffected"
    verify_reused(old,reused)
    reused.loc[0,"config_hash"]="new"
    with pytest.raises(ValueError,match="provenance changed"):verify_reused(old,reused)
    reused=old.copy();reused["result_origin"]="original_A_H1H2_verified_unaffected";reused.loc[0,"fci_validator"]+=.1
    with pytest.raises(ValueError,match="outcome changed"):verify_reused(old,reused)
