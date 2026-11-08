"""Analytic crossing checks and nonidentifiability must survive result processing."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/"scripts"))

import numpy as np
import pytest
from scipy.special import expit

from phase07_statistics import adequate_crossing, interval, invert_curve


def test_inverse_plateau_first_crossing_and_support_flags():
    values, right, left = invert_curve([8, 12, 20, 30], [0, .5, .5, 1], [0, .5, .75, 1.1])
    assert values[:3] == pytest.approx([8, 12, 25])
    assert np.isnan(values[3]) and right.tolist() == [False, False, False, True]
    assert left.tolist() == [True, False, False, False]


def test_logistic_recovers_known_fractional_binomial_crossing():
    x = np.linspace(8, 50, 120)
    y = expit((x-18.5)/4)
    fit = adequate_crossing(x, y)
    assert fit["status"] == "identified"
    assert fit["a_min_m2"] == pytest.approx(18.5, abs=1e-6)
    assert fit["slope"] == pytest.approx(.25, abs=1e-6)


@pytest.mark.parametrize("values,expected", [([0, 0, 0, 0], "one_outcome_class"),
    ([1, 1, 1, 1], "one_outcome_class"), ([0, 0, 1, 1], "complete_or_quasi_separation")])
def test_absent_or_separated_classes_do_not_invent_minimum_area(values, expected):
    fit = adequate_crossing([8, 10, 20, 30], values)
    assert fit["status"] == expected and fit["a_min_m2"] is None


def test_crossing_outside_support_is_not_reported_as_area():
    x = np.linspace(8, 50, 100)
    fit = adequate_crossing(x, expit((x-70)/10))
    assert fit["status"] == "crossing_outside_observed_support" and fit["a_min_m2"] is None


def test_missing_bootstraps_are_counted_not_silently_conditioned_away():
    lo, hi, count, status = interval([1., 2., np.nan, np.nan])
    assert lo is None and hi is None and count == 2
    assert status == "insufficient_supported_bootstraps"
