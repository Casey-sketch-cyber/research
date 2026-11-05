"""Enumerate feasible fixed anchors with vectorized summed-area rectangle queries."""
from __future__ import annotations

import numpy as np

from fea.geometry.raster import Raster, FURNISHABLE, STORAGE_ONLY, WALKABLE
from .library import Item, rectangles


def rectangle_fits(mask: np.ndarray, rect: tuple[int, int, int, int]) -> np.ndarray:
    """Check every grid vertex at once; no Python loop over grid cells or anchors."""
    ny, nx = mask.shape
    yy, xx = np.indices((ny+1, nx+1))
    dx, dy, w, h = rect
    x0, y0, x1, y1 = xx+dx, yy+dy, xx+dx+w, yy+dy+h
    valid = (x0 >= 0) & (y0 >= 0) & (x1 <= nx) & (y1 <= ny)
    integral = np.pad(mask.astype(np.int32), ((1, 0), (1, 0))).cumsum(0).cumsum(1)
    x0, x1 = np.clip(x0, 0, nx), np.clip(x1, 0, nx)
    y0, y1 = np.clip(y0, 0, ny), np.clip(y1, 0, ny)
    count = integral[y1, x1]-integral[y0, x1]-integral[y1, x0]+integral[y0, x0]
    return valid & (count == w*h)


def generate_candidates(raster: Raster, items: dict[str, Item], orientations=(0, 90, 180, 270)) -> dict[str, np.ndarray]:
    """Return integer (column, row, degrees) anchors fitting every allowed state."""
    result = {}
    clearance = np.isin(raster.labels, [FURNISHABLE, STORAGE_ONLY, WALKABLE])
    for name, item in items.items():
        storage_only = set(t for state in item.states for t in state.serves) == {"storage"}
        body_mask = np.isin(raster.labels, [FURNISHABLE, STORAGE_ONLY] if storage_only else [FURNISHABLE])
        poses = []
        for orientation in orientations:
            valid = np.ones(tuple(n+1 for n in raster.labels.shape), dtype=bool)
            for state in item.states:
                body, strips, back = rectangles(state, raster.resolution, orientation)
                valid &= rectangle_fits(body_mask, body)
                for strip in strips:
                    valid &= rectangle_fits(clearance, strip)
                if item.wall_backed:
                    valid &= rectangle_fits(raster.wall & (~raster.window if item.tall else True), back)
            rows, columns = np.nonzero(valid)
            poses.extend(np.column_stack((columns, rows, np.full(len(rows), orientation))))
        result[name] = np.asarray(poses, dtype=np.int32).reshape(-1, 3)
    return result
