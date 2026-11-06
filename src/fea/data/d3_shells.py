"""Generate the configured shells with deterministic collision-free fixed services."""
from __future__ import annotations

import itertools
import json
import math
from collections.abc import Iterator
from pathlib import Path

from shapely.geometry import GeometryCollection, LineString, box
from shapely.geometry.base import BaseGeometry

from fea.geometry.unit import Unit, polygon_union, parts
from fea.geometry.raster import door_keepout, rasterize
from fea.validate import _reachable
import numpy as np
from .d1_swiss import opaque_id


def fixed_services(width: float, depth: float, entry: BaseGeometry, keepout: BaseGeometry,
                   toilet_size: list[float], kitchen_size: list[float], all_candidates: bool = False):
    """Choose the nearest feasible corner pod, then the nearest feasible wall kitchen.

    Candidate coordinates come from wall ends, doorway ends and pod boundaries;
    no extra positioning grid or unverified room-size parameter is introduced.
    """
    shell = box(0, 0, width, depth)
    candidates = []
    for tw, td in (toilet_size, toilet_size[::-1]):
        for tx, ty in itertools.product((0, width - tw), (0, depth - td)):
            toilet = box(tx, ty, tx + tw, ty + td)
            if not shell.covers(toilet) or toilet.distance(keepout) <= 1e-8:
                continue
            for kw, kd in (kitchen_size, kitchen_size[::-1]):
                xs = {0.0, width - kw, tx - kw, tx + tw, keepout.bounds[2]+.1}
                ys = {0.0, depth - kd, ty - kd, ty + td, keepout.bounds[3]+.1}
                for kx, ky in itertools.product(sorted(xs), sorted(ys)):
                    if not (abs(kx) < 1e-9 or abs(ky) < 1e-9 or abs(kx + kw - width) < 1e-9 or abs(ky + kd - depth) < 1e-9):
                        continue
                    kitchen = box(kx, ky, kx + kw, ky + kd)
                    if shell.covers(kitchen) and kitchen.intersection(toilet).area <= 1e-9 and kitchen.distance(keepout) > 1e-8:
                        score = (toilet.centroid.distance(entry), kitchen.centroid.distance(entry), tx, ty, kx, ky, tw)
                        candidates.append((score, toilet, kitchen))
    if not candidates:
        raise ValueError("No feasible fixed-service arrangement for configured shell")
    ordered = [(t, k) for _, t, k in sorted(candidates, key=lambda value: value[0])]
    return ordered if all_candidates else ordered[0]


def toilet_door(toilet: BaseGeometry, free: BaseGeometry, span: float, walking_width: float) -> BaseGeometry:
    """Choose the centred pod-face opening with most adjacent free space."""
    x0, y0, x1, y1 = toilet.bounds
    faces = [((x0, y0), (x1, y0)), ((x1, y0), (x1, y1)), ((x1, y1), (x0, y1)), ((x0, y1), (x0, y0))]
    candidates = []
    for p0, p1 in faces:
        line = LineString([p0, p1])
        length = min(span, line.length)
        door = LineString([line.interpolate((line.length - length) / 2), line.interpolate((line.length + length) / 2)])
        available = door.buffer(walking_width / 2, cap_style=2).intersection(free).area
        candidates.append((available, door))
    return max(candidates, key=lambda value: value[0])[1]


def load_d3(config: dict) -> Iterator[Unit]:
    """Generate every configured parameter tuple, including below-filter shells."""
    settings = config["shells_D3"]
    openings = json.loads(Path("reports/schemas/D1_opening_dimensions.json").read_text())["openings"]
    door_width = openings["ENTRANCE_DOOR"]["median_width_m"]
    window_width = openings["WINDOW"]["median_width_m"]
    internal_width = openings["DOOR"]["median_width_m"]
    for area, ratio, entry_position, window_position in itertools.product(settings["areas_m2"], settings["aspect_ratios"],
                                                                        settings["entrance_positions"], settings["window_positions"]):
        width, depth = math.sqrt(area / ratio), math.sqrt(area * ratio)
        shell = box(0, 0, width, depth)
        if entry_position.startswith("short_wall"):
            span = min(door_width, width)
            x = (width - span) / 2 if entry_position.endswith("center") else 0.0
            entrance = LineString([(x, 0), (x + span, 0)])
            keepout = box(x, 0, x + span, span)
        else:
            span = min(door_width, depth)
            entrance = LineString([(0, 0), (0, span)])
            keepout = box(0, 0, span, span)
        if window_position == "opposite_short_wall":
            win_span = min(window_width, width)
            window = LineString([((width - win_span) / 2, depth), ((width + win_span) / 2, depth)])
        else:
            win_span = min(window_width, depth)
            window = LineString([(width, (depth - win_span) / 2), (width, (depth + win_span) / 2)])
        parameters = {"gross_area_m2": area, "aspect_ratio": ratio, "entrance_position": entry_position,
                      "window_position": window_position}
        key = "D3:" + opaque_id(json.dumps(parameters, sort_keys=True))
        accepted = None
        attempted = 0
        try:
            arrangements = fixed_services(width, depth, entrance, keepout, settings["toilet_pod"]["footprint"],
                                          settings["kitchenette"]["footprint"], all_candidates=True)
        except ValueError:
            arrangements = []
        for toilet, kitchen in arrangements:
            attempted += 1
            fixed = polygon_union([toilet, kitchen])
            free = shell.difference(fixed)
            service_door = toilet_door(toilet, free, internal_width, .9)
            # Continuous configuration space: every surviving main-floor centre
            # component must connect to the external portal with a 0.90 m disc.
            portal = door_keepout(entrance, shell, both_sides=True).difference(shell)
            centres = polygon_union([free, portal]).buffer(-.45/math.cos(math.pi/128), quad_segs=32)
            components = parts(centres)
            connected = [g for g in components if g.intersection(portal).area > 1e-9]
            if len(connected) != 1: continue
            reached = connected[0]
            if any(g.intersection(shell).area > 1e-8 and not g.equals(reached) for g in components): continue
            coverage = reached.buffer(.45, quad_segs=32).intersection(free)
            if coverage.intersection(service_door.buffer(.01)).area <= 1e-9: continue
            near = all((g.centroid.y <= depth / 2 if entry_position.startswith("short_wall")
                        else g.centroid.x <= width / 2) for g in (toilet, kitchen))
            unit = Unit(key, "D3", "D3:" + opaque_id((ratio, entry_position, window_position)),
                {"furnishable": free, "storage_only": GeometryCollection(), "walkable_only": GeometryCollection(),
                 "fixed_service": fixed, "excluded": GeometryCollection()},
                shell.boundary.difference(entrance), [entrance, service_door], [window], entrance, float(area), 1,
                {"parameters": parameters, "entrance_method": "generated",
                 "fixed_placement": "ordered nearest-corner/wall candidates; continuous 0.90 m access and empty-raster check",
                 "has_sanitary": True, "has_kitchen": True, "has_kitchen_dining": False,
                 "service_placement": "near_entrance" if near else "far_end",
                 "service_placement_rule": "near only when both service centroids are in the entrance-wall half",
                 "toilet_geometry": toilet.wkt, "kitchen_geometry": kitchen.wkt,
                 "opening_width_source": "D1 residential opening-record medians", "entrance_width_m": span,
                 "window_width_m": win_span, "internal_door_width_m": service_door.length,
                 "fixed_service_area_m2": fixed.area, "entrance_keepout_overlap_m2": fixed.intersection(keepout).area,
                 "continuous_access_width_m": .9, "candidate_attempts": attempted})
            grid = rasterize(unit, config["raster"]["resolution_m"])
            reached_cells = _reachable(grid, np.zeros_like(grid.labels, bool), config["furniture"]["meta"]["walking_width"])
            if not all(np.any(t & reached_cells) for t in grid.service_targets): continue
            accepted = unit
            break
        if accepted is not None:
            yield accepted
        else:
            # Explicit rejected record retains the parameter key for old-to-new
            # mapping; the corpus filter excludes it before sampling.
            yield Unit(key, "D3", "D3:"+opaque_id((ratio, entry_position, window_position)),
                {"furnishable": shell, "storage_only": GeometryCollection(), "walkable_only": GeometryCollection(),
                 "fixed_service": GeometryCollection(), "excluded": GeometryCollection()},
                shell.boundary.difference(entrance), [entrance], [window], entrance, float(area), 1,
                {"parameters": parameters, "generator_failure": "generator_infeasible", "candidate_attempts": attempted,
                 "has_sanitary": False, "has_kitchen": False, "entrance_method": "generated"})
