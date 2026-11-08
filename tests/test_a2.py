"""The sensitivity is explicit, isolated and complete; main defaults stay frozen."""
from copy import deepcopy
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/"scripts"))

import pandas as pd
import pytest

from fea.config import load_config
from phase07_a2 import HOUSEHOLDS, acceptance, variant_config


def test_a2_changes_only_approved_clearances_and_runtime_settings():
    base = load_config("config/project.yaml")
    before = deepcopy(base)
    variant = variant_config(base)
    assert base == before
    assert variant["furniture"]["static_items"]["double_bed"]["clearance"]["left"] == .6
    assert variant["furniture"]["static_items"]["double_bed"]["clearance"]["right"] == 0
    assert base["furniture"]["static_items"]["double_bed"]["clearance"]["right"] == .5
    for name in ("wall_bed_double", "wall_bed_over_sofa", "sofa_bed"):
        original = base["furniture"]["transformable_items"][name]
        changed = variant["furniture"]["transformable_items"][name]
        assert changed["states"]["stowed"] == original["states"]["stowed"]
        assert changed["states"]["deployed"]["footprint"] == original["states"]["deployed"]["footprint"]
        assert changed["states"]["deployed"]["clearance"] == dict(left=.6, right=0., front=0., back=0.)
    assert variant["households"] == base["households"]
    assert variant["solver"]["num_workers"] == 4 and variant["solver"]["time_limit_s"] == 120


def fixture():
    return pd.DataFrame([dict(unit_key="test", household=h, strategy=s, validator_pass=True,
        fci_validator=0., status="FEASIBLE") for h in HOUSEHOLDS for s in ["S0", "S1", "S2"]])


def test_a2_keeps_valid_zero_cases_and_requires_full_pairs():
    assert acceptance(fixture(), ["test"])["zero_cases"] == 6
    with pytest.raises(ValueError): acceptance(fixture().iloc[1:], ["test"])


def test_a2_does_not_hide_invalid_or_reversed_results():
    frame = fixture()
    frame.loc[0, "validator_pass"] = False
    with pytest.raises(ValueError): acceptance(frame, ["test"])
    frame = fixture()
    frame.loc[0, "fci_validator"] = .7
    with pytest.raises(ValueError): acceptance(frame, ["test"])
