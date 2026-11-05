"""Hand-computed demand totals and malformed schedule rejection."""
import copy

import pytest

from fea.config import load_config
from fea.households import demanded_hours, parse_households, parse_slots


@pytest.fixture
def config():
    return load_config("config/project.yaml")


def test_demanded_hours_by_hand_and_full_day(config):
    households = parse_households(config["households"], config["furniture"])
    # H1: 8 + 2*(1+1) + 2 + 1 + 3*(1+0.3) = 18.9.
    # H4: 8*2 + 2*(1+1) + 2*(1+1) + 1 + 3 = 28.
    expected = [18.9, 26., 26., 28., 26.]
    for household, total in zip(households.values(), expected):
        assert demanded_hours(household) == pytest.approx(total)
        for variant in household.variants:
            assert demanded_hours(household, variant.name) == pytest.approx(total)
            assert sum(s.hours for s in household.slots) == 24
    parent = households["H4_parent_child"]
    night = parent.variants[0].demand["night"]
    assert len(night) == 2 and night[0].id != night[1].id
    assert parent.slots[0].hours == 8
    couple = households["H3_couple_one_remote"]
    assert [v.frequency for v in couple.variants] == [0.857, 0.143]
    assert couple.variants[1].demand["dinner"][0].need == "dine_4"
    assert households["H5_older_adult"].overrides == {"walking_width": 0.9, "global_clearance_scale": 1.2}


def test_capacity_units_are_not_demand_weights(config):
    raw = copy.deepcopy(config["households"])
    raw["households"]["H1_single_commuter"]["variants"]["normal"]["demand"]["morning"][0]["units"] = 7.
    households = parse_households(raw, config["furniture"])
    assert demanded_hours(households["H1_single_commuter"]) == pytest.approx(18.9)


def test_variant_totals_remain_separate(config):
    raw = copy.deepcopy(config["households"])
    raw["households"]["H3_couple_one_remote"]["variants"]["guests"]["demand"]["day"] = []
    couple = parse_households(raw, config["furniture"])["H3_couple_one_remote"]
    assert demanded_hours(couple, "normal") == 26
    assert demanded_hours(couple, "guests") == 18
    assert demanded_hours(couple) == pytest.approx(0.857 * 26 + 0.143 * 18)


def test_overlap_even_with_24_hour_sum_is_rejected():
    with pytest.raises(ValueError, match="gap or overlap"):
        parse_slots({"a": [0, 12], "b": [11, 23]})


@pytest.mark.parametrize("bad", ["token", "frequency", "weight", "units", "slot"])
def test_malformed_schedule_is_rejected(config, bad):
    raw = copy.deepcopy(config["households"])
    variant = raw["households"]["H1_single_commuter"]["variants"]["normal"]
    if bad == "token":
        variant["demand"]["night"][0]["need"] = "unknown"
    elif bad == "frequency":
        variant["frequency"] = 0.9
    elif bad == "weight":
        variant["demand"]["night"][0]["weight"] = float("nan")
    elif bad == "units":
        variant["demand"]["morning"][0]["units"] = 0
    else:
        variant["demand"].pop("day")
    with pytest.raises(ValueError):
        parse_households(raw, config["furniture"])
