"""Paired bootstraps preserve form/time covariance and expose missing data."""
import importlib.util
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/"scripts"))

import numpy as np
import pandas as pd
import pytest


def module():
    spec = importlib.util.spec_from_file_location("decomposition", "scripts/07_decomposition.py")
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def fixture():
    return pd.DataFrame([dict(unit_key=str(i), household="H3", source="D3", nia_m2=12.,
        strategy=s, fci_validator=value, validator_pass=True)
        for i, values in enumerate(((.2, .3, .8), (.2, .7, .8)))
        for s, value in zip(("S0", "S1", "S2"), values)])


def test_effects_sum_exactly_and_bootstrap_keeps_constant_total():
    m = module()
    effects = m.paired_effects(fixture())
    assert np.allclose(effects.form_effect+effects.time_effect, effects.total_effect)
    summary = m.summarize(effects, 500, .95, 7)
    assert np.allclose(summary.mean_total_effect_ci_lo, .6)
    assert np.allclose(summary.mean_total_effect_ci_hi, .6)
    assert (summary.mean_form_effect_ci_hi > summary.mean_form_effect_ci_lo).all()
    pd.testing.assert_frame_equal(summary, m.summarize(effects.iloc[::-1], 500, .95, 7))


def test_single_unit_has_mean_but_no_invented_precision():
    m = module()
    result = m.summarize(m.paired_effects(fixture().iloc[:3]), 50, .95, 7)
    assert result.mean_form_effect_ci_lo.isna().all()
    assert result.bootstrap_resamples.eq(0).all()


def test_missing_or_reversed_strategy_is_rejected():
    m = module()
    with pytest.raises(ValueError):
        m.paired_effects(fixture().iloc[1:])
    changed = fixture()
    changed.loc[changed.strategy == "S2", "fci_validator"] = .1
    with pytest.raises(ValueError, match="ordering"):
        m.paired_effects(changed)
