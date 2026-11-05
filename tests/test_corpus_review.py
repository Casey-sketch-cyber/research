"""Meaningful regressions for the G1 area, completeness, dedup and sampling changes."""
from dataclasses import replace

import numpy as np
import pandas as pd
import pytest
from shapely.geometry import GeometryCollection, LineString, box

from fea.config import load_config
from fea.corpus import exclusion_reasons, geometry_hash, freeze_sample, deduplicate_frame
from fea.geometry.scale import scale_measurements
from fea.geometry.unit import Unit


def test_storage_counts_in_nia_but_walls_do_not():
    unit = Unit("toy", "D1", "site", {"furnishable": box(0, 0, 4, 4),
        "storage_only": box(4, 0, 5, 4), "fixed_service": box(0, 4, 5, 5),
        "walkable_only": GeometryCollection()}, box(0, 0, .2, 5), [], [], None, None, 1)
    assert unit.interior.area == pytest.approx(24)
    assert geometry_hash(unit) == geometry_hash(replace(unit, unit_key="another", group_id="another_site"))
    assert geometry_hash(unit) != geometry_hash(replace(unit, n_rooms=2))


def test_small_furnishable_area_cannot_hide_a_large_incomplete_dwelling():
    row = pd.Series(dict(source="D1", geometry_failures="", nia_m2=60,
                         furnishable_area_m2=15, n_rooms=0, has_sanitary=False, has_kitchen=False))
    reasons = exclusion_reasons(row, load_config("config/project.yaml")).split(";")
    assert set(reasons) == {"above_max_nia", "no_habitable_room", "no_sanitary", "no_kitchen"}


def test_duplicate_copies_cannot_receive_extra_experiment_weight():
    original = Unit("b", "D1", "site1", {"furnishable": box(0, 0, 4, 4)},
                    GeometryCollection(), [], [], None, None, 1)
    copies = [original, replace(original, unit_key="a", group_id="site2"),
              replace(original, unit_key="c", n_rooms=2)]
    frame = pd.DataFrame([dict(unit_key=u.unit_key, source=u.source, exclude_reason="") for u in copies])
    result = deduplicate_frame(frame, [{"unit": u.to_dict()} for u in copies], load_config("config/project.yaml"))
    assert set(result.loc[result.include, "unit_key"]) == {"a", "c"}
    assert result.loc[0, "representative_key"] == "a"
    assert result.loc[0, "exclude_reason"] == "duplicate_geometry"
    assert result.loc[result.include, "n_duplicates"].sum() == 1


def test_wall_cross_section_measurement_is_not_bounding_box_width():
    walls = box(0, 0, 5, 5).difference(box(.2, .2, 4.8, 4.8))
    values = scale_measurements(walls, [box(0, 1, .2, 1.9)], .2)
    assert values["median_wall_thickness_m"] == pytest.approx(.2)
    assert values["median_door_span_m"] == pytest.approx(.9)


def test_frozen_sample_respects_sites_and_seed():
    config = load_config("config/project.yaml")
    config["corpus"]["expA_sample"]["D1"] = dict(n_max=20, max_per_site=2)
    frame = pd.DataFrame([dict(unit_key=str(i), group_id=str(i//6), source="D1", include=True,
                              nia_m2=8+2*(i%10), n_rooms=1+i%2) for i in range(60)])
    a, b = freeze_sample(frame, config), freeze_sample(frame, config)
    assert a.in_expA_sample.tolist() == b.in_expA_sample.tolist()
    chosen = a[a.in_expA_sample]
    assert len(chosen) == 20
    assert chosen.groupby("group_id").size().max() <= 2
    assert chosen.nia_bin_2m2.nunique() > 1
