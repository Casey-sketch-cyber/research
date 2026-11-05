"""Conservative, vectorized floor-grid representation with separate opening masks."""
from __future__ import annotations

from dataclasses import dataclass
import math

import numpy as np
import shapely
from scipy import ndimage
from shapely.geometry import GeometryCollection, Polygon
from shapely.ops import unary_union

from .unit import Unit, polygon_union

BLOCKED, FURNISHABLE, STORAGE_ONLY, WALKABLE, KEEPOUT = range(5)


@dataclass
class Raster:
    """Cell labels and geometry-derived masks in local metres (array rows increase y)."""
    labels: np.ndarray
    resolution: float
    origin: tuple[float, float]
    wall: np.ndarray
    window: np.ndarray
    entrance: np.ndarray
    entrance_extension: np.ndarray
    service_targets: list[np.ndarray]
    keepout_geometry: object

    @property
    def walkable(self) -> np.ndarray:
        """Door keepouts are traversable but unavailable to furniture/clearance."""
        return self.labels != BLOCKED


def door_keepout(door, interior, both_sides: bool = False):
    """Return a width-square on each possible room side of the door centreline."""
    rectangle = door.minimum_rotated_rectangle
    points = np.asarray(rectangle.exterior.coords if rectangle.geom_type == "Polygon" else rectangle.coords)
    deltas = np.diff(points, axis=0)
    lengths = np.linalg.norm(deltas, axis=1)
    if not len(lengths) or max(lengths) <= 0:
        return GeometryCollection()
    i = int(np.argmax(lengths))
    width = float(lengths[i])
    tangent = deltas[i] / width
    normal = np.array([-tangent[1], tangent[0]])
    centre = np.array([door.centroid.x, door.centroid.y])
    probes = [shapely.Point(*(centre + sign * normal * width / 2)) for sign in (-1, 1)]
    sides = [sign for sign, probe in zip((-1, 1), probes) if interior.covers(probe)]
    if both_sides or not sides:
        sides = [-1, 1]
    return polygon_union([Polygon([centre-tangent*width/2, centre+tangent*width/2,
        centre+tangent*width/2+sign*normal*width, centre-tangent*width/2+sign*normal*width]) for sign in sides])


def rasterize(unit: Unit, resolution: float = .1) -> Raster:
    """Cover whole cells only; fixed services and physical walls remain blocked."""
    if resolution <= 0 or unit.interior.is_empty:
        raise ValueError("Positive grid resolution and nonempty interior required")
    r = resolution
    x0, y0, x1, y1 = unit.interior.bounds
    # Exterior entrance portal lets radius erosion start outside the dwelling;
    # it avoids seeding an arbitrary interior component past a blocked doorway.
    entry_span = max(np.linalg.norm(np.diff(np.asarray(unit.entrance.minimum_rotated_rectangle.exterior.coords), axis=0), axis=1)) if unit.entrance is not None and unit.entrance.minimum_rotated_rectangle.geom_type == "Polygon" else (unit.entrance.length if unit.entrance is not None else 0.)
    padding = math.ceil(max(1., entry_span+r)/r)
    origin = (math.floor(x0/r)*r-padding*r, math.floor(y0/r)*r-padding*r)
    nx, ny = math.ceil((x1-origin[0])/r)+padding, math.ceil((y1-origin[1])/r)+padding
    yy, xx = np.indices((ny, nx))
    cells = shapely.box(origin[0]+xx*r, origin[1]+yy*r, origin[0]+(xx+1)*r, origin[1]+(yy+1)*r)
    free = polygon_union([unit.classes.get(k, GeometryCollection()) for k in
                          ("furnishable", "storage_only", "walkable_only")]).difference(unit.walls)
    # Mixed class cells can be circulation but never receive a non-storage body.
    labels = np.zeros((ny, nx), np.uint8)
    def covered(g):
        padded = g.buffer(1e-9)
        shapely.prepare(padded)
        return shapely.covers(padded, cells)
    labels[covered(free)] = WALKABLE
    for name, value in (("storage_only", STORAGE_ONLY), ("furnishable", FURNISHABLE)):
        labels[covered(unit.classes.get(name, GeometryCollection()).difference(unit.walls))] = value
    keepout = polygon_union([door_keepout(d, unit.interior) for d in unit.doors])
    # A positive-area overlap, not a shared edge, excludes a cell.
    reserved = shapely.area(shapely.intersection(cells, keepout)) > 1e-10
    labels[reserved & (labels != BLOCKED)] = KEEPOUT
    adjacent = ndimage.binary_dilation(labels != BLOCKED)
    wall = (labels == BLOCKED) & adjacent & shapely.intersects(cells, unit.walls.buffer(1e-8))
    windows = unary_union(unit.windows)  # Retain line windows in generated shells.
    window = wall & shapely.intersects(cells, windows.buffer(r*.01))
    entrance = np.zeros_like(wall)
    extension = np.zeros_like(wall)
    if unit.entrance is not None:
        entrance = (labels != BLOCKED) & shapely.intersects(cells, unit.entrance.buffer(r*.51))
        exterior = door_keepout(unit.entrance, unit.interior, both_sides=True).difference(unit.interior).difference(unit.walls)
        extension = covered(exterior)
    fixed = unit.classes.get("fixed_service", GeometryCollection())
    targets = []
    for door in unit.doors:
        if unit.entrance is not None and door.equals(unit.entrance):
            continue
        if door.distance(fixed) <= r:
            targets.append((labels != BLOCKED) & shapely.intersects(cells, door.buffer(.3+r)))
    return Raster(labels, r, origin, wall, window, entrance, extension, targets, keepout)
