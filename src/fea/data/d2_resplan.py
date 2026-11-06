"""Convert normalized D2 polygons using an explicit source-gross-area calibration."""
from __future__ import annotations

import math
from collections.abc import Iterator
from pathlib import Path

from shapely import affinity
from shapely.geometry import GeometryCollection
from shapely.geometry.base import BaseGeometry
from tqdm import tqdm

from fea.geometry.unit import Unit, parts, polygon_union
from fea.geometry.scale import scale_measurements
from .archives import extract_named, read_geometry_pickle
from .d1_swiss import opaque_id


def from_plan(plan: dict) -> Unit:
    """Convert one source plan; the calibration assumption is recorded in metadata."""
    def union(names: list[str]) -> BaseGeometry:
        return polygon_union([plan[n] for n in names if isinstance(plan.get(n), BaseGeometry)])

    inner = union(["inner"])
    footprint = union(["inner", "wall", "door", "window", "front_door"])
    gross = float(plan["area"])
    scale = math.sqrt(gross / footprint.area) if gross > 0 and footprint.area > 0 else None
    if scale is None:
        raise ValueError("D2 source area cannot be calibrated")

    def metric(g: BaseGeometry) -> BaseGeometry:
        return affinity.scale(g, xfact=scale, yfact=scale, origin=(0, 0))

    fixed = union(["bathroom"])
    kitchen = union(["kitchen"])
    excluded = union(["balcony", "balacony", "garden", "parking", "pool", "stair"])
    furnishable = union(["bedroom", "living", "dining", "office"]).intersection(inner).difference(polygon_union([fixed, kitchen]))
    storage = union(["storage"]).intersection(inner).difference(fixed)
    walls = union(["wall", "window"])
    furnishable = furnishable.difference(walls)
    # GEOS can assert on empty GeometryCollection minus a mixed-dimensional
    # collection. Empty storage is already disjoint; no overlay is necessary.
    if not storage.is_empty:
        storage = storage.difference(walls).difference(furnishable)
    walkable = inner.difference(polygon_union([furnishable, storage, fixed, excluded, walls]))
    # Preserve the original kitchen-room extent/NIA when changing its access class.
    # Some released kitchen edges extend beyond the generic inner polygon.
    walkable = polygon_union([walkable, kitchen.difference(fixed).difference(walls)])
    doors = parts(union(["door", "front_door"]))
    walls = walls.difference(polygon_union(doors))
    front = union(["front_door"])
    support = union(["wall", "door", "window", "front_door", "bedroom", "living", "storage", "dining", "office", "bathroom", "kitchen"])
    detached_inner = sum(g.area for g in parts(inner) if g.distance(support) > 1e-6)
    entrance = next((door for door in doors if door.intersection(front).area > 1e-9), None)
    windows = parts(union(["window"]))
    classes = {"furnishable": furnishable, "storage_only": storage,
               "walkable_only": polygon_union([walkable, *doors]).difference(fixed),
               "fixed_service": fixed, "excluded": excluded}
    key = "D2:" + opaque_id(plan["id"])
    return Unit(key, "D2", key, {name: metric(g) for name, g in classes.items()}, metric(walls),
                [metric(g) for g in doors], [metric(g) for g in windows], metric(entrance) if entrance is not None else None,
                gross, sum(len(parts(plan[k])) for k in ("bedroom", "living", "dining", "office") if isinstance(plan.get(k), BaseGeometry)),
                {"entrance_method": "source_front_door" if entrance is not None else "unidentified",
                 "metric_calibration": "source area / union(inner, wall, door, window, front_door)",
                 "scale_m_per_source_unit": scale, "released_net_area_unused": True,
                 "has_sanitary": union(["bathroom"]).area > 0,
                 "has_kitchen": union(["kitchen"]).area > 0,
                 "has_kitchen_dining": False,
                 "service_room_geometry": metric(fixed).wkt,
                 "kitchen_region_geometry": metric(kitchen.difference(walls).difference(fixed)).wkt,
                 **scale_measurements(metric(walls), [metric(g) for g in doors],
                                      float(plan["wall_depth"]) * scale if plan.get("wall_depth") is not None else None),
                 "raw_geometry_area_after_scaling_m2": footprint.area * scale ** 2,
                 "source_invalid_geometries": sum(not g.is_valid for g in plan.values() if isinstance(g, BaseGeometry)),
                 "entrance_distance_to_known_spaces_m": entrance.distance(inner) * scale if entrance is not None and not inner.is_empty else None,
                 "unsupported_detached_inner_area_m2": detached_inner * scale ** 2,
                 "rooms_outside_source_outline_m2": polygon_union([furnishable, fixed, walkable]).difference(footprint).area * scale ** 2})


def load_d2(config: dict, completed_keys: set[str] | None = None) -> Iterator[Unit]:
    """Yield the pinned D2 release in stable source-ID order."""
    root = Path(config["paths"]["raw"]) / "resplan"
    path = extract_named(root / "ResPlan.zip", "ResPlan.pkl", root / "extracted/ResPlan.pkl")
    with path.open("rb") as stream:
        plans = read_geometry_pickle(stream)
    for plan in tqdm(sorted(plans, key=lambda p: p["id"]), desc="D2 units"):
        if completed_keys and "D2:" + opaque_id(plan["id"]) in completed_keys:
            continue
        yield from_plan(plan)
