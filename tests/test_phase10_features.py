"""Regressions for split membership and the train-only P1 target reference."""
import json
from pathlib import Path
import sys

import pandas as pd
from shapely.geometry import LineString, box, GeometryCollection
from fea.geometry.unit import Unit

sys.path.insert(0, str(Path("scripts")))
from phase10_features import extract_geometry, split_groups, targets


def two_rooms(key, source, group):
    unit = Unit(key, source, group, {"furnishable": box(0, 0, 2, 2).union(box(2.06, 0, 4, 2))},
                GeometryCollection(), [LineString([(2, .5), (2.06, .5)])], [],
                None, None, 2)
    return extract_geometry(json.dumps(unit.to_dict()), .05)


def test_shared_door_links_distinct_rooms():
    plan = two_rooms("a", "D1", "g")
    assert plan.nodes.shape == (2, 12)
    assert set(map(tuple, plan.edges)) == {(0, 1), (1, 0)}
    assert (plan.nodes[:, 7] == 1).all()


def test_group_split_is_independent_of_input_order():
    plans = [two_rooms(f"u{i}_{j}", "D1", f"g{i}") for i in range(10) for j in range(2)]
    plans += [two_rooms("external"+s, s, "external"+s) for s in ("D2", "D3")]
    settings = {"train": .7, "val": .15, "test": .15}
    left, right = split_groups(plans, settings, 20261105), split_groups(plans[::-1], settings, 20261105)
    pd.testing.assert_frame_equal(left, right)
    assert left[left.source == "D1"].groupby("group_id").split.nunique().max() == 1


def test_reference_ignores_external_scores_and_retains_bounds():
    split = pd.DataFrame([
        ["a", "D1", "a", 18., "train"], ["b", "D1", "b", 20., "train"],
        ["c", "D2", "c", 19., "D2_external"], ["d", "D2", "d", 19., "D2_external"],
    ], columns=["unit_key", "source", "group_id", "nia_m2", "split"])
    rows = []
    for key, s0, s2 in [("a", .6, .7), ("b", .9, .9), ("c", .2, .8), ("d", .2, .2)]:
        for name, score in [("S0", s0), ("S1", s0), ("S2", s2)]:
            rows.append(dict(unit_key=key, household="H", strategy=name, fci_validator=score))
    capacity = pd.DataFrame(rows)
    first, ref = targets(capacity, split)
    external = capacity.unit_key.eq("c") & capacity.strategy.eq("S2")
    capacity.loc[external, "fci_validator"] = .85
    _, next_ref = targets(capacity, split)
    pd.testing.assert_frame_equal(ref, next_ref)
    f = first.set_index("unit_key")
    assert not f.loc["c", "saving_identified"] and f.loc["c", "saving_lower_bound_m2"] > 0
    assert f.loc["d", "saving_identified"] and f.loc["d", "saving_m2"] == 0
