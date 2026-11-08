"""Outcome-independent empty-raster evaluability required by the Phase 7 review."""
import heapq
import math

import numpy as np
from scipy import ndimage

from fea.geometry.raster import FURNISHABLE, rasterize
from fea.validate import _reachable


RULE = dict(walking_width_m=0.60, clearance_depth_m=0.60, minimum_furnishable_share=0.50,
    furnishable_denominator="raster FURNISHABLE cells, excluding door keepouts and blocked partial cells",
    clearance_metric="8-neighbour free-cell shortest path; no diagonal corner cutting or wall crossing",
    fixed_target_rule="each target mask intersects entrance-connected walking-disc coverage",
    outcome_inputs_used=False, version="phase07_E1_v1")


def clearance_coverage(covered, free, resolution, depth):
    """Expand body coverage by a bounded free-space distance, respecting barriers."""
    covered = np.asarray(covered, bool) & free
    distance = np.full(free.shape, np.inf)
    distance[covered] = 0.
    boundary = covered & ~ndimage.binary_erosion(covered)
    queue = [(0., int(y), int(x)) for y, x in np.argwhere(boundary)]
    heapq.heapify(queue)
    moves = [(dy, dx, resolution*math.hypot(dy, dx))
             for dy in (-1, 0, 1) for dx in (-1, 0, 1) if dy or dx]
    height, width = free.shape
    while queue:
        cost, y, x = heapq.heappop(queue)
        if cost > distance[y, x]+1e-12:
            continue
        for dy, dx, step in moves:
            a, b = y+dy, x+dx
            if not (0 <= a < height and 0 <= b < width and free[a, b]):
                continue
            if dy and dx and (not free[y, b] or not free[a, x]):
                continue
            candidate = cost+step
            if candidate <= depth+1e-9 and candidate < distance[a, b]-1e-12:
                distance[a, b] = candidate
                heapq.heappush(queue, (candidate, a, b))
    return distance <= depth+1e-9


def evaluate_empty(unit, resolution=.1, max_gap=.15, masks=False):
    """Use geometry only: furniture, scores and solver records are never inputs."""
    width = RULE["walking_width_m"]
    grid = rasterize(unit, resolution, width, max_gap)
    covered = _reachable(grid, np.zeros_like(grid.labels, bool), width)
    expanded = clearance_coverage(covered, grid.walkable, resolution, RULE["clearance_depth_m"])
    furnishable = grid.labels == FURNISHABLE
    count = int(furnishable.sum())
    failed_targets = [i for i, target in enumerate(grid.service_targets) if not np.any(target & covered)]
    share = float((expanded & furnishable).sum()/count) if count else 0.
    a_pass = not failed_targets
    b_pass = count > 0 and share+1e-12 >= RULE["minimum_furnishable_share"]
    reasons = ([] if a_pass else ["fixed_service_unreachable"])+([] if b_pass else ["furnishable_reachable_share_below_half"])
    record = dict(unit_key=unit.unit_key, source=unit.source, nia_m2=unit.interior.area,
        a_pass=a_pass, b_reachable_share=share, evaluable=bool(a_pass and b_pass),
        reason=";".join(reasons) if reasons else "evaluable", n_rooms=unit.n_rooms,
        furnishable_area_m2=unit.classes["furnishable"].area,
        raster_furnishable_area_m2=count*resolution**2,
        directly_covered_furnishable_share=float((covered & furnishable).sum()/count) if count else 0.,
        fixed_target_count=len(grid.service_targets), failed_targets=failed_targets)
    return (record, grid, covered, expanded) if masks else record
