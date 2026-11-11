"""Lower-support and upper-support censoring cannot enter identified medians."""
from pathlib import Path
import sys
import numpy as np
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from phase07_p1_area import paired_gain,gain_summary

CURVE=dict(area=np.array([17.,19.,21.]),capacity=np.array([.8,.9,1.]))


def test_lower_support_gains_are_bounds_not_identified():
    result=paired_gain(CURVE,[.7,.95],[.9,1.])
    assert np.isnan(result['delta_ea_m2'][0])
    assert result['delta_ea_lower_bound_m2'][0]==pytest.approx(2.)
    assert result['delta_ea_m2'][1]==pytest.approx(1.)
    summary=gain_summary(result)
    assert summary['n_identified_positive_gains']==1 and summary['n_lower_bound_positive_gains']==1
    assert summary['median_delta_ea_identified_positive_m2']==pytest.approx(1.)
    assert summary['median_among_fci_improved_upper_unbounded']


def test_equal_scores_identify_zero_even_at_both_support_limits():
    curve=dict(area=np.array([17.,19.]),capacity=np.array([.8,.9]))
    result=paired_gain(curve,[.6,.95],[.6,.95])
    assert np.all(result['delta_gain_identified'])
    assert np.all(result['delta_ea_m2']==0)
    assert not np.any(result['delta_gain_lower_bound_only'])


def test_double_censoring_and_lower_edge_equality():
    curve=dict(area=np.array([17.,19.]),capacity=np.array([.8,.9]))
    result=paired_gain(curve,[.6,.95,.8],[.95,1.,.85])
    assert np.all(result['delta_gain_lower_bound_only'])
    assert np.allclose(result['delta_ea_lower_bound_m2'],[2.,0.,1.])
    assert np.all(np.isnan(result['delta_ea_m2']))
    with pytest.raises(ValueError):paired_gain(curve,[.9],[.8])
