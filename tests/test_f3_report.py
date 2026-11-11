"""Paired F3 reporting must preserve negative changes and unit covariance."""
import importlib.util
from pathlib import Path
import numpy as np
import pandas as pd
import pytest

spec=importlib.util.spec_from_file_location("f3_report",Path(__file__).parents[1]/"scripts/07_f3_report.py")
report=importlib.util.module_from_spec(spec);spec.loader.exec_module(report)


def fixture():
    rows=[]
    for key,main,variant in [("u1",[.4,.6,.9],[.3,.6,.8]),("u2",[.3,.5,.6],[.4,.5,.7])]:
        for strategy,a,b in zip(["S0","S1","S2"],main,variant):
            rows.append(dict(unit_key=key,household="H3",source="D3",nia_m2=12, strategy=strategy,main_fci=a,fci_validator=b,delta_fci=b-a))
    return pd.DataFrame(rows)


def test_signed_effects_and_complete_pairing():
    frame=fixture();pairs=report.paired_effects(frame)
    assert len(pairs)==2
    assert pairs.loc[0,"delta_time"]==pytest.approx(-.1)
    assert pairs.loc[1,"delta_time"]==pytest.approx(.1)
    assert (frame.delta_fci<0).sum()==2
    assert np.allclose(pairs.delta_form+pairs.delta_time,(pairs.F3_S2-pairs.F3_S0)-(pairs.main_S2-pairs.main_S0))
    with pytest.raises(ValueError,match="Incomplete"):
        report.paired_effects(frame.iloc[:-1])


def test_rejects_unpaired_difference():
    frame=fixture();frame.loc[0,"delta_fci"]=0
    with pytest.raises(ValueError,match="paired scores"):
        report.paired_effects(frame)


def test_summary_singleton_and_paired_mean():
    config={"seed":17,"experiments":{"bootstrap":{"n":1000,"ci":.95}}}
    pairs=report.paired_effects(fixture())
    summary=report.summarise(pairs,config)
    overall=summary[(summary.pooling=="pooled")&(summary.scope=="overall")].iloc[0]
    assert overall.delta_time==pytest.approx(0,abs=1e-12)
    assert overall.delta_time_ci_lo<=0<=overall.delta_time_ci_hi
    singleton=report.summarise(pairs.iloc[:1],config)
    assert singleton.delta_time_ci_lo.isna().all()
    assert singleton.delta_time_ci_hi.isna().all()
