from pathlib import Path
import sys
import numpy as np
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from phase07_paired_area import fit_reference,paired_gain,gain_summary


def test_reference_uses_bin_median_and_cumulative_max():
    curve=fit_reference([8.,8.5,9.,10.,10.5,12.],[.1,.3,.9,.1,.2,1.])
    assert np.allclose(curve['area'],[9.,11.,13.])
    assert np.allclose(curve['raw_capacity'],[.3,.15,1.])
    assert np.allclose(curve['capacity'],[.3,.3,1.])


def test_paired_inverse_gain_has_no_own_area_term():
    curve=dict(area=np.array([9.,11.,13.]),capacity=np.array([.2,.6,1.]))
    result=paired_gain(curve,[.2,.6,1.],[.6,1.,1.])
    assert np.allclose(result['delta_ea_m2'],[2.,2.,0.])
    summary=gain_summary(result)
    assert summary['median_delta_ea_positive_uncensored_m2']==2.
    assert summary['share_fully_functional_S0']==pytest.approx(1/3)


def test_censoring_bounds_and_equal_censored_scores():
    curve=dict(area=np.array([10.,20.]),capacity=np.array([.2,.8]))
    result=paired_gain(curve,[.5,.9,1.],[1.,1.,1.])
    assert np.allclose(result['delta_ea_lower_bound_m2'],[5.,0.,0.])
    assert np.array_equal(result['delta_right_censored'],[True,True,False])
    assert np.isnan(result['delta_ea_m2'][:2]).all() and result['delta_ea_m2'][2]==0.
    assert result['ea_S0_right_censored'][2] and result['ea_S2_right_censored'][2]
    summary=gain_summary(result)
    assert summary['median_among_fci_improved_upper_unbounded']


def test_lower_support_flags_and_nonnegative_order_guard():
    curve=dict(area=np.array([10.,20.]),capacity=np.array([.2,1.]))
    result=paired_gain(curve,[.1,.1],[.15,.6])
    assert np.allclose(result['delta_ea_m2'],[0.,5.])
    assert result['ea_S0_lower_support_boundary'].all()
    with pytest.raises(ValueError):paired_gain(curve,[.9],[.8])
