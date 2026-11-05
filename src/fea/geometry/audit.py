"""Geometry audits independent of the source loaders."""
from __future__ import annotations

import math

import numpy as np

from .unit import Unit, polygon_union


def describe(unit: Unit) -> dict:
    """Return common scalars and explicit geometry failures for one normalized unit."""
    interior = unit.interior
    rectangle = interior.minimum_rotated_rectangle
    edges = np.linalg.norm(np.diff(np.asarray(rectangle.exterior.coords), axis=0), axis=1) if rectangle.geom_type == "Polygon" else []
    failures = []
    layers = [*unit.classes.values(), unit.walls, *unit.doors, *unit.windows]
    if any(not g.is_valid for g in layers):
        failures.append("invalid_geometry")
    if interior.is_empty or interior.area <= 0:
        failures.append("empty_interior")
    if unit.meta.get("rooms_outside_source_outline_m2", 0) > 1e-6:
        failures.append("rooms_outside_source_outline")
    if unit.meta.get("unsupported_detached_inner_area_m2", 0) > 1e-6:
        failures.append("unsupported_detached_interior")
    contact = unit.meta.get("entrance_distance_to_known_spaces_m")
    if contact is not None and contact > 1e-6:
        failures.append("entrance_not_touching_known_spaces")
    if not unit.windows:
        failures.append("missing_window")
    if unit.entrance is None or unit.entrance.is_empty:
        failures.append("missing_entrance")
    elif unit.entrance.distance(interior) > 1e-6:
        failures.append("detached_entrance")
    if unit.classes["furnishable"].intersection(unit.classes["fixed_service"]).area > 1e-6:
        failures.append("furnishable_fixed_overlap")
    if unit.classes["furnishable"].intersection(unit.walls).area > 1e-6:
        failures.append("furnishable_wall_overlap")
    return {"unit_key": unit.unit_key, "source": unit.source, "group_id": unit.group_id,
            "gross_area_m2": unit.gross_area_m2, "furnishable_area_m2": unit.classes["furnishable"].area,
            "known_interior_area_m2": interior.area, "n_rooms": unit.n_rooms,
            "n_windows": len(unit.windows), "n_doors": len(unit.doors),
            "aspect_ratio": float(max(edges) / min(edges)) if len(edges) and min(edges) > 0 else None,
            "compactness": 4 * math.pi * interior.area / interior.length ** 2 if interior.length else None,
            "geometry_failures": ";".join(failures), "entrance_method": unit.meta.get("entrance_method"),
            "source_invalid_geometries": unit.meta.get("source_invalid_geometries", 0),
            "normalization_repaired_layers": unit.meta.get("normalization_repaired_layers", 0),
            "simulation_fields": len(unit.meta.get("simulation_area_means", {}))}
