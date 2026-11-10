"""Tiny end-to-end solves with independent scoring and nested strategy incumbents."""
from copy import deepcopy

import pytest

from fea.solve.cpsat import solve_layout
from fea.geometry.raster import rasterize
from fea.validate import validate_layout
from fea.households import parse_households
from test_metrics_validator import fixture
from test_candidates import empty_room
from dataclasses import replace
from shapely.geometry import LineString


def test_tiny_end_to_end_and_nested_strategies():
    config, household, _, _ = fixture()
    config = deepcopy(config)
    config["solver"]["time_limit_s"] = 10
    config["solver"]["num_workers"] = 1
    # Exact tiny case: one bed type, no untested modification of production defaults.
    config["furniture"]["static_items"] = {"single_bed": config["furniture"]["static_items"]["single_bed"]}
    config["furniture"]["transformable_items"] = {}
    room = empty_room()
    door = LineString([(0, 0), (1, 0)])
    room = replace(room, doors=[door], entrance=door, walls=room.walls.difference(door))
    incumbent = None
    for strategy in ("S0", "S1", "S2"):
        result = solve_layout(room, household, strategy, config, incumbent)
        checked = validate_layout(result, rasterize(room), config, household)
        assert checked["pass"], checked["violations"]
        assert checked["fci"] == pytest.approx(8/18.9)
        assert result["solver"]["fci_solver"] == pytest.approx(checked["fci"])
        incumbent = result


@pytest.mark.parametrize("name,kept,expected", [("H4_parent_child", "single_bed", 8/28),
    ("H3_couple_one_remote", "shelving", 1/26)])
def test_solver_respects_occurrence_and_capacity_limits(name, kept, expected):
    config, _, _, _ = fixture()
    household = parse_households(config["households"], config["furniture"])[name]
    config["solver"]["time_limit_s"] = 10
    config["solver"]["num_workers"] = 1
    if kept == "single_bed":
        config["furniture"]["max_instances"][kept] = 1  # Explicit one-instance limit fixture; main reviewed cap is two.
    config["furniture"]["static_items"] = {kept: config["furniture"]["static_items"][kept]}
    config["furniture"]["transformable_items"] = {}
    room = empty_room()
    door = LineString([(0, 0), (1, 0)])
    room = replace(room, doors=[door], entrance=door, walls=room.walls.difference(door))
    result = solve_layout(room, household, "S0", config)
    assert result["validator"]["pass"]
    assert result["fci"] == pytest.approx(expected)
