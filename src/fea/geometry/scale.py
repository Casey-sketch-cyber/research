"""Geometry-derived calibrated door spans and wall-thickness cross-sections."""
from __future__ import annotations

import numpy as np
from shapely.geometry import LineString, Point

from .unit import parts


def linear_parts(geometry):
    """Yield only line components of an intersection."""
    if geometry.geom_type in ("LineString", "LinearRing"):
        yield geometry
    else:
        for child in getattr(geometry, "geoms", []):
            yield from linear_parts(child)


def scale_measurements(walls, doors, released_depth: float | None) -> dict:
    """Measure wall cross-sections normal to boundary midpoints, weighted by edge length.

    Weighting prevents tiny wall end caps from dominating the thickness statistic.
    The ray spans the whole bounding box; values are not clipped to plausible ranges.
    """
    spans = []
    for door in doors:
        rectangle = door.minimum_rotated_rectangle
        if rectangle.geom_type == "Polygon":
            edges = np.linalg.norm(np.diff(np.asarray(rectangle.exterior.coords), axis=0), axis=1)
            spans.append(float(max(edges)))
        elif door.length:
            spans.append(door.length)
    widths, weights = [], []
    if not walls.is_empty:
        extent = np.hypot(walls.bounds[2] - walls.bounds[0], walls.bounds[3] - walls.bounds[1]) + 1
        for polygon in parts(walls):
            for ring in (polygon.exterior, *polygon.interiors):
                xy = np.asarray(ring.coords)
                for a, b in zip(xy[:-1], xy[1:]):
                    delta = b - a
                    length = float(np.linalg.norm(delta))
                    if length < 1e-7:
                        continue
                    midpoint = (a + b) / 2
                    normal = np.array([-delta[1], delta[0]]) / length
                    ray = LineString([midpoint - extent * normal, midpoint + extent * normal])
                    intersections = [g.length for g in linear_parts(ray.intersection(walls))
                                     if g.length > 1e-7 and g.distance(Point(midpoint)) < 1e-7]
                    if intersections:
                        widths.append(min(intersections))
                        weights.append(length)
    median = None
    if widths:
        order = np.argsort(widths)
        index = np.searchsorted(np.cumsum(np.asarray(weights)[order]), sum(weights) / 2)
        median = float(np.asarray(widths)[order][index])
    return {"median_door_span_m": float(np.median(spans)) if spans else None,
            "median_wall_thickness_m": median, "wall_thickness_sections": len(widths),
            "released_wall_depth_m": released_depth}
