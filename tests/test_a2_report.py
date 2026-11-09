"""Paired sensitivity bootstraps must preserve cross-configuration covariance."""
import importlib.util
from pathlib import Path
import sys
import numpy as np
import pandas as pd
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
spec=importlib.util.spec_from_file_location("a2_report_test","scripts/07_a2_report.py")
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)


def test_paired_bootstrap_keeps_constant_change():
    frame=pd.DataFrame(dict(source=["D3"]*3,household=["H3"]*3,nia_m2=[10.,10.2,10.8],
        form_main=[.1,.3,.5],time_main=[.4,.2,0.],form_A2=[.2,.4,.6],time_A2=[.3,.1,-.1],
        delta_form=[.1]*3,delta_time=[-.1]*3))
    config={"seed":42,"experiments":{"bootstrap":{"n":1000,"ci":.95}}}
    result=module.summarise(frame,config)
    pooled=result[(result.pooling=="pooled")&(result.scope=="overall")].iloc[0]
    assert np.allclose([pooled.delta_form,pooled.delta_form_ci_lo,pooled.delta_form_ci_hi],.1)
    assert np.allclose([pooled.delta_time,pooled.delta_time_ci_lo,pooled.delta_time_ci_hi],-.1)
    assert pooled.form_main_ci_hi > pooled.form_main_ci_lo
    single=module.summarise(frame.iloc[:1],config)
    assert single.delta_form_ci_lo.isna().all()
