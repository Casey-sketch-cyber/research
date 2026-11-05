"""Hand-computed metric cases and deliberately invalid layouts."""
from copy import deepcopy
from dataclasses import replace

import pytest
from shapely.geometry import LineString

from fea.config import load_config
from fea.geometry.raster import rasterize
from fea.households import parse_households
from fea.metrics import fci, invert_monotone
from fea.validate import validate_layout
from test_candidates import empty_room


def fixture():
    config = load_config("config/project.yaml")
    h = parse_households(config["households"], config["furniture"])["H1_single_commuter"]
    door = LineString([(0, 0), (1, 0)])
    room = empty_room()
    grid = rasterize(replace(room, doors=[door], entrance=door, walls=room.walls.difference(door)))
    item = dict(instance_id="single_bed#1", type="single_bed", x=2.1, y=1., orientation_deg=0,
                states={v.name: {s.name: "static" for s in h.slots} for v in h.variants})
    layout = dict(strategy="S0", items=[item], resolution_m=.1,
                  service={"normal": {"night": [dict(demand_id="normal:night:0", by=["single_bed#1"])]}})
    return config, h, grid, layout


def test_validator_recomputes_service_and_ignores_claimed_score():
    config, h, grid, layout = fixture()
    layout["fci"] = 1
    result = validate_layout(layout, grid, config, h)
    assert result["pass"], result["violations"]
    assert result["fci"] == pytest.approx(8/18.9)
    assert result["tb"] == 0


@pytest.mark.parametrize("problem,expected", [("body", "body_outside_allowed"),
    ("back", "wall_backing"), ("capability", "wrong_capability"), ("overlap", "body_overlap")])
def test_validator_catches_violations(problem, expected):
    config, h, grid, layout = fixture()
    if problem == "body": layout["items"][0]["x"] = 3.
    elif problem == "back":
        layout["items"].append({**deepcopy(layout["items"][0]), "instance_id": "desk#1", "type": "desk", "x": 1., "y": 2.})
    elif problem == "capability":
        layout["service"]["normal"]["leisure"] = [dict(demand_id="normal:leisure:1", by=["single_bed#1"])]
    elif problem == "overlap":
        layout["items"].append({**deepcopy(layout["items"][0]), "instance_id": "armchair#1", "type": "armchair"})
    result = validate_layout(layout, grid, config, h)
    assert not result["pass"]
    assert any(expected in v for v in result["violations"])
    assert result["fci"] == 0


def test_variant_ratios_are_weighted_after_separate_normalization():
    config = load_config("config/project.yaml")
    h = parse_households(config["households"], config["furniture"])["H3_couple_one_remote"]
    guest = h.variants[1]
    demand = deepcopy(guest.demand)
    demand["dinner"] = tuple(replace(d, weight=3.) for d in demand["dinner"])
    h = replace(h, variants=(h.variants[0], replace(guest, demand=demand)))
    credits = {d.id: 1. for demands in h.variants[0].demand.values() for d in demands}
    result = fci(h, credits)
    assert result["fci"] == pytest.approx(.857)
    assert result["fci"] != pytest.approx(result["served_hours"]/result["demanded_hours"])


def test_monotone_inverse_uses_first_plateau_point_and_marks_censoring():
    areas, values = [8, 12, 20, 30], [0, .5, .5, 1]
    assert invert_monotone(areas, values, .5)["fea_m2"] == 12
    assert invert_monotone(areas, values, .75)["fea_m2"] == 25
    assert invert_monotone(areas, values, 1.01) == {"fea_m2": None, "right_censored": True, "lower_bound_m2": 30.}


def test_slot_transformation_is_allowed_only_for_S2_and_burden_is_cyclic():
    config, h, grid, layout = fixture()
    item = layout["items"][0]
    item.update(instance_id="wall_bed_single#1", type="wall_bed_single", x=1.6, y=0.)
    item["states"]["normal"] = {s.name: "deployed" if s.name == "night" else "stowed" for s in h.slots}
    layout["service"]["normal"]["night"][0]["by"] = [item["instance_id"]]
    layout["strategy"] = "S2"
    good = validate_layout(layout, grid, config, h)
    assert good["pass"], good["violations"]
    assert good["tb"] == 2.  # night -> morning and leisure -> night
    layout["strategy"] = "S1"
    bad = validate_layout(layout, grid, config, h)
    assert any("day_wide_state_changed" in v for v in bad["violations"])


def test_one_item_cannot_cover_two_simultaneous_demands():
    config, h, grid, layout = fixture()
    h4 = parse_households(config["households"], config["furniture"])["H4_parent_child"]
    layout["service"]["normal"]["night"].append(dict(demand_id="normal:night:1", by=["single_bed#1"]))
    bad = validate_layout(layout, grid, config, h4)
    assert any("instance_used_twice" in v for v in bad["violations"])


def test_storage_capacity_is_partial_not_binary():
    config, h, grid, layout = fixture()
    h3 = parse_households(config["households"], config["furniture"])["H3_couple_one_remote"]
    layout["items"] = [dict(instance_id="shelving#1", type="shelving", x=1.5, y=0., orientation_deg=0,
        states={v.name: {s.name: "static" for s in h3.slots} for v in h3.variants})]
    layout["service"] = {v.name: {"morning": [dict(demand_id=v.name+":morning:0", by=["shelving#1"])]} for v in h3.variants}
    checked = validate_layout(layout, grid, config, h3)
    assert checked["pass"], checked["violations"]
    assert checked["fci"] == pytest.approx((2*.5/2)/26)


def test_entrance_threshold_between_grid_lines_has_no_false_seam():
    from shapely import affinity
    from fea.validate import _reachable
    import numpy as np
    door = LineString([(0, 0), (1, 0)])
    room = empty_room()
    move = lambda g: affinity.translate(g, .035, .027)
    shifted = replace(room, classes={k: move(g) for k, g in room.classes.items()},
        walls=move(room.walls.difference(door)), doors=[move(door)], entrance=move(door))
    grid = rasterize(shifted)
    assert _reachable(grid, np.zeros_like(grid.labels, bool), .6).sum() > 500


def test_narrow_passages_do_not_earn_service_credit_behind_a_barrier():
    config, h, grid, layout = fixture()
    bed = layout["items"][0]
    bed.update(x=2.5, y=1.7, orientation_deg=90)
    layout["items"].append({**deepcopy(bed), "instance_id": "desk#1", "type": "desk", "x": 2.5, "y": 4., "orientation_deg": 180})
    layout["service"]["normal"]["leisure"] = [dict(demand_id="normal:leisure:1", by=["desk#1"])]
    checked = validate_layout(layout, grid, config, h)
    assert checked["pass"], checked["violations"]
    assert checked["credits"]["normal:leisure:1"] == 0
    assert checked["fci"] == pytest.approx(8/18.9)
