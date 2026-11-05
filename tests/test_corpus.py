"""Geometric invariants and integration checks on authorized observed source data."""
import math
from pathlib import Path
from dataclasses import replace

import pytest
from shapely import affinity, from_wkt
from shapely.geometry import GeometryCollection, LineString, box

from fea.config import load_config
from fea.data.d1_swiss import load_d1
from fea.data.d1_swiss import opaque_id
from fea.data.d2_resplan import load_d2
from fea.data.d2_resplan import from_plan
from fea.data.archives import read_geometry_pickle
from fea.data.d3_shells import load_d3
from fea.geometry.normalize import normalize
from fea.geometry.unit import Unit


def test_all_generated_shells_preserve_area_and_fixed_services():
    config = load_config("config/project.yaml")
    units = list(load_d3(config))
    settings = config["shells_D3"]
    expected = math.prod(len(settings[k]) for k in ("areas_m2", "aspect_ratios", "entrance_positions", "window_positions"))
    assert len(units) == expected == len({u.unit_key for u in units})
    fixed_area = math.prod(settings["toilet_pod"]["footprint"]) + math.prod(settings["kitchenette"]["footprint"])
    for unit in units:
        assert unit.interior.area == pytest.approx(unit.gross_area_m2)
        assert unit.classes["fixed_service"].area == pytest.approx(fixed_area)
        assert unit.classes["furnishable"].area == pytest.approx(unit.gross_area_m2 - fixed_area)
        assert unit.meta["entrance_keepout_overlap_m2"] < 1e-8
        assert unit.entrance.distance(unit.classes["furnishable"]) < 1e-8
        assert unit.doors[1].buffer(0.01).intersection(unit.classes["furnishable"]).area > 0
        normalized = normalize(unit)
        assert from_wkt(normalized.meta["toilet_geometry"]).difference(normalized.classes["fixed_service"]).area < 1e-8


@pytest.mark.parametrize("source,loader,archive", [("D1", load_d1, "swiss_dwellings/swiss-dwellings-v3.0.0.zip"), ("D2", load_d2, "resplan/ResPlan.zip")])
def test_observed_source_unit_loader(source, loader, archive):
    config = load_config("config/project.yaml")
    if not (Path(config["paths"]["raw"]) / archive).exists():
        pytest.skip("Authorized raw dataset required for observed-unit integration test")
    generator = loader(config)
    try:
        unit = next(generator)
    finally:
        generator.close()
    assert unit.source == source
    assert unit.interior.area > 0
    assert unit.classes["furnishable"].area > 0
    assert unit.entrance is not None and unit.windows
    normalized = normalize(unit)
    assert normalized.interior.area == pytest.approx(unit.interior.area)
    assert normalized.interior.bounds[0] == pytest.approx(0, abs=1e-8)
    assert normalized.interior.bounds[1] == pytest.approx(0, abs=1e-8)
    assert normalized.entrance.distance(normalized.interior) == pytest.approx(unit.entrance.distance(unit.interior), abs=1e-8)
    restored = Unit.from_dict(normalized.to_dict())
    assert restored.interior.symmetric_difference(normalized.interior).area < 1e-8
    if source == "D1":
        assert unit.gross_area_m2 is None
        assert unit.meta["simulation_area_means"]
    else:
        assert unit.meta["raw_geometry_area_after_scaling_m2"] == pytest.approx(unit.gross_area_m2)
        assert unit.meta["released_net_area_unused"]


def test_observed_near_coincident_D2_vertices_preserve_fixed_area():
    path = Path("data/raw/resplan/extracted/ResPlan.pkl")
    if not path.exists():
        pytest.skip("Authorized D2 raw data required for numerical regression")
    with path.open("rb") as stream:
        plans = read_geometry_pickle(stream)
    plan = next(p for p in plans if opaque_id(p["id"]) == "a33686b000cb614d879a")
    unit = from_plan(plan)
    normalized = normalize(unit)
    for name, geometry in unit.classes.items():
        assert normalized.classes[name].is_valid
        assert abs(normalized.classes[name].area - geometry.area) < 1e-6


def test_polygon_wall_with_zero_area_remnants_normalizes():
    unit = next(load_d3(load_config("config/project.yaml")))
    wall = GeometryCollection([box(0, 0, 0.1, 2), LineString([(0.1, 2), (0.1, 2.1)])])
    normalized = normalize(replace(unit, walls=wall))
    assert normalized.walls.is_valid
    assert normalized.walls.geom_type in ("Polygon", "MultiPolygon")
    assert normalized.walls.area == pytest.approx(0.2)
