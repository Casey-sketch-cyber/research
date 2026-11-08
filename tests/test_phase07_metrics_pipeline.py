"""A shared linear capacity curve must produce zero saving and no spurious test effect."""
import importlib.util
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/"scripts"))

import numpy as np
import pandas as pd


def test_equal_linear_strategies_have_zero_saving_and_null_paired_test(tmp_path):
    spec = importlib.util.spec_from_file_location("metrics_driver", "scripts/07_metrics.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    area = np.repeat(np.linspace(8, 30, 10), 3)
    scores = .05+.9*(area-8)/22
    frame = pd.DataFrame(dict(unit_key=[f"synthetic_{i:02d}" for i in range(len(area))],
        source="synthetic", household="H1", nia_m2=area, S0=scores, S1=scores, S2=scores))
    module.group_job(("synthetic", "H1", frame, {"n":20, "ci":.95}, [.90, .95, 1.], 17, str(tmp_path)))
    cases = pd.read_csv(tmp_path/"fea.csv")
    curves = pd.read_csv(tmp_path/"area_saving_curve.csv")
    paired = pd.read_csv(tmp_path/"tests.csv")
    assert np.allclose(cases.saving_m2, 0., atol=1e-10)
    assert np.allclose(curves.median_saving_m2, 0., atol=1e-10)
    assert np.allclose(curves.ci_lo.dropna(), 0., atol=1e-10)
    assert np.allclose(curves.ci_hi.dropna(), 0., atol=1e-10)
    assert paired.p_value.eq(1).all() and paired.effect_size.eq(0).all()
    assert not cases.right_censored.any()
