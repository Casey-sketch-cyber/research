"""Solver-side walking connectivity and boundary-blocker identification."""
from __future__ import annotations

import numpy as np
from scipy import ndimage

from fea.furniture.library import rectangles


def state_masks(layout, grid, items, variant, slot):
    """Materialize active solver rectangles; the validator has its own implementation."""
    masks = {}
    for placed in layout["items"]:
        item = items[placed["type"]]
        state = next(s for s in item.states if s.name == placed["states"][variant][slot])
        body, strips, _ = rectangles(state, grid.resolution, placed["orientation_deg"])
        x, y = [round((placed[k]-grid.origin[i])/grid.resolution) for i, k in enumerate(("x", "y"))]
        body_mask, clearance = np.zeros_like(grid.labels, bool), np.zeros_like(grid.labels, bool)
        for mask, rects in ((body_mask, [body]), (clearance, strips)):
            for dx, dy, w, h in rects: mask[y+dy:y+dy+h, x+dx:x+dx+w] = True
        masks[placed["instance_id"]] = (body_mask, clearance)
    return masks


def check_connectivity(layout, grid, items, household, width):
    """Label eroded-free components and identify the poses bordering failed access."""
    problems = []
    for variant in household.variants:
        for slot in household.slots:
            masks = state_masks(layout, grid, items, variant.name, slot.name)
            occupied = np.zeros_like(grid.labels, bool)
            for body, _ in masks.values(): occupied |= body
            free = (grid.walkable & ~occupied) | grid.entrance_extension
            distance = ndimage.distance_transform_edt(np.pad(free, 1))[1:-1, 1:-1]*grid.resolution-grid.resolution/np.sqrt(2)
            eroded = free & (distance >= width/2-1e-9)
            labels, _ = ndimage.label(eroded)
            seeds = np.unique(labels[grid.entrance_extension & eroded])
            reached = np.isin(labels, seeds[seeds != 0]) & grid.walkable
            disconnected = free & grid.walkable & ~reached
            border = ndimage.binary_dilation(disconnected)
            blockers = [identity for identity, (body, _) in masks.items() if np.any(body & border)]
            for index, target in enumerate(grid.service_targets):
                if not np.any(reached & target):
                    problems.append(dict(variant=variant.name, slot=slot.name, demand_id=None,
                        instance_id=None, blockers=blockers, fixed_service=index))
            for assignment in layout.get("service", {}).get(variant.name, {}).get(slot.name, []):
                for identity in assignment["by"]:
                    if not np.any(masks[identity][1] & reached):
                        problems.append(dict(variant=variant.name, slot=slot.name, demand_id=assignment["demand_id"],
                            instance_id=identity, blockers=sorted(set(blockers+[identity]))))
    return problems
