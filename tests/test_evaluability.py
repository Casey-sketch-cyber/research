"""Barriers and analysis completeness are independent of observed score patterns."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/"scripts"))

import numpy as np
import pandas as pd
import pytest

from phase07_evaluability import clearance_coverage
from phase07_analysis import select_evaluable


def test_clearance_cannot_jump_wall_to_nearby_room():
    free = np.ones((9, 15), bool)
    free[:, 7] = False
    covered = np.zeros_like(free)
    covered[:, :7] = True
    expanded = clearance_coverage(covered, free, .1, .6)
    assert expanded[:, :7].all()
    assert not expanded[:, 8:].any()


def test_clearance_respects_distance_and_does_not_cut_corners():
    free = np.ones((15, 15), bool)
    covered = np.zeros_like(free)
    covered[7, 7] = True
    expanded = clearance_coverage(covered, free, .1, .6)
    assert expanded[7, 13] and not expanded[7, 14]
    free[7, 8] = free[8, 7] = False
    short = clearance_coverage(covered, free, .1, .15)
    assert not short[8, 8]


def data():
    households = ["H1", "H2", "H3", "H4"]
    sample = pd.DataFrame({"unit_key":["keep_zero", "exclude"]})
    evaluation = pd.DataFrame(dict(unit_key=["keep_zero", "exclude"], source=["D3", "D1"],
        nia_m2=[8., 20.], evaluable=[True, False]))
    rows = [dict(unit_key=u, source="D3" if u == "keep_zero" else "D1", nia_m2=8. if u == "keep_zero" else 20.,
        household=h, strategy=s, validator_pass=u == "keep_zero", fci_validator=0.)
        for u in sample.unit_key for h in households for s in ["S0", "S1", "S2"]]
    return pd.DataFrame(rows), evaluation, sample, households


def test_whole_unit_exclusion_preserves_genuine_zeros():
    selected, report = select_evaluable(*data())
    assert len(selected) == report["retained_zero_cases"] == 12
    assert report["excluded_cases"] == 12 and report["excluded_units"] == 1


@pytest.mark.parametrize("problem", ["missing", "duplicate", "invalid", "ordering", "flag", "wrong_source", "extra_unit"])
def test_analysis_gate_rejects_inconsistent_cases(problem):
    rows, evaluation, sample, households = data()
    if problem == "missing": rows = rows.iloc[1:]
    elif problem == "duplicate": rows = pd.concat([rows, rows.iloc[[0]]])
    elif problem == "invalid": rows.loc[0, "validator_pass"] = False
    elif problem == "ordering": rows.loc[0, "fci_validator"] = .5
    elif problem == "flag": evaluation["evaluable"] = ["False", "True"]
    elif problem == "wrong_source": rows.loc[0, "source"] = "D1"
    elif problem == "extra_unit": evaluation.loc[1, "unit_key"] = "different"
    with pytest.raises(ValueError): select_evaluable(rows, evaluation, sample, households)
