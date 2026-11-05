"""Apply one rigid coordinate transform to every layer of a unit."""
from __future__ import annotations

import math
from dataclasses import replace

import numpy as np
from shapely import affinity, from_wkt, make_valid, set_precision
from shapely.geometry.base import BaseGeometry

from .unit import Unit, parts, polygon_union


def normalize(unit: Unit) -> Unit:
    """Align the weighted orthogonal edge direction, then translate to a local origin."""
    vector = 0j
    for polygon in parts(unit.interior):
        edges = np.diff(np.asarray(polygon.exterior.coords), axis=0)
        for x, y in edges:
            vector += math.hypot(x, y) * np.exp(4j * math.atan2(y, x))
    angle = math.degrees(np.angle(vector) / 4) if abs(vector) > 1e-12 else 0.0
    rotated = affinity.rotate(unit.interior, -angle, origin=(0, 0))
    origin = rotated.bounds[:2] if not rotated.is_empty else (0.0, 0.0)

    repairs = []
    def transform(g: BaseGeometry) -> BaseGeometry:
        if g.geom_type == "GeometryCollection" and parts(g):
            g = polygon_union([g])
        # A nanometre numerical grid removes near-coincident vertices before
        # rotation; it is many orders below both input resolution and raster size.
        # Pointwise snapping afterward prevents roundoff from changing hole parity.
        cleaned = set_precision(g if g.is_valid else make_valid(g), 1e-9)
        result = affinity.translate(affinity.rotate(cleaned, -angle, origin=(0, 0)), xoff=-origin[0], yoff=-origin[1])
        result = set_precision(result, 1e-9, mode="pointwise")
        if not result.is_valid:
            repairs.append(True)
            result = make_valid(result)
        if result.geom_type == "GeometryCollection" and parts(g):
            result = polygon_union([result])
        return result

    # The inverse/source-frame transform is deliberately not published.
    return replace(unit, classes={k: transform(g) for k, g in unit.classes.items()}, walls=transform(unit.walls),
                   doors=[transform(g) for g in unit.doors], windows=[transform(g) for g in unit.windows],
                   entrance=transform(unit.entrance) if unit.entrance is not None else None,
                   meta={**unit.meta, **{k: transform(from_wkt(unit.meta[k])).wkt
                                         for k in ("toilet_geometry", "kitchen_geometry") if k in unit.meta},
                         "normalization_repaired_layers": len(repairs),
                         "numerical_coordinate_grid_m": 1e-9,
                         "coordinates": "dominant-axis-aligned local metres"})
