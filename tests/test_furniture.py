"""Unit conversion and statistical boundaries that affect furniture comparisons."""
import pandas as pd
import pytest

from fea.data.abo import dimensions_m
from fea.furniture.checks import outside_interval, summary, trim_type


def test_dimension_units_and_missing_units():
    item = {"item_dimensions": {"width": {"value": 100, "unit": "centimeters"}, "length": {"value": 2, "unit": "feet"}, "height": {"value": 10, "unit": "inches"}}}
    assert dimensions_m(item) == pytest.approx({"width": 1, "depth": 0.6096, "height": 0.254})
    item["item_dimensions"]["width"]["unit"] = "unspecified"
    assert dimensions_m(item) is None


def test_typewise_upper_tail_and_quartile_endpoints():
    frame = pd.DataFrame({"width": [1.] * 100 + [1000.], "depth": [2.] * 101, "height": [3.] * 101})
    clean, upper = trim_type(frame)
    assert len(clean) == 100
    values = summary(clean)
    assert values["median_w"] == 1 and values["median_d"] == 2
    assert not outside_interval(1, 2, values)
    assert outside_interval(2, 1, values)
