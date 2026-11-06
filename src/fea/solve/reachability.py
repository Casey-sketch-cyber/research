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


def walking_masks(grid, occupied, width):
    """Disc erosion permits exact-width corridors; dilation restores covered cells."""
    diameter = width/grid.resolution
    n = int(np.ceil(diameter-1e-9))
    yy, xx = np.indices((n, n))
    disc = (xx-(n-1)/2)**2+(yy-(n-1)/2)**2 <= (diameter/2)**2+1e-9
    free = (grid.walkable & ~occupied) | grid.entrance_extension
    centres = ndimage.binary_erosion(free, structure=disc)
    labels, _ = ndimage.label(centres)
    seeds = np.unique(labels[grid.entrance_extension & centres])
    reached = np.isin(labels, seeds[seeds != 0])
    covered = ndimage.binary_dilation(reached, structure=disc) & grid.walkable & ~occupied
    return covered, reached, centres, disc


def check_connectivity(layout, grid, items, household, width):
    """Find failed service and a certificate of the occupied reference frontier."""
    problems = []
    for variant in household.variants:
        for slot in household.slots:
            masks = state_masks(layout, grid, items, variant.name, slot.name)
            occupied = np.zeros_like(grid.labels, bool)
            for body, _ in masks.values(): occupied |= body
            reached, refs, _, disc = walking_masks(grid, occupied, width)
            _, _, empty_refs, _ = walking_masks(grid, np.zeros_like(occupied), width)
            frontier = empty_refs & ~refs & (ndimage.binary_dilation(refs) | grid.entrance_extension)
            # One occupied witness cell per blocked frontier reference is enough
            # to certify the barrier. If all witnesses remain covered, no new
            # route can leave the reached component (including entrance seeds).
            witnesses = {}
            offsets = np.argwhere(disc)-np.array(disc.shape)//2
            for y, x in np.argwhere(frontier):
                choices = [(int(y+dy), int(x+dx)) for dy, dx in offsets
                           if 0 <= y+dy < occupied.shape[0] and 0 <= x+dx < occupied.shape[1]
                           and occupied[y+dy, x+dx]]
                if not choices: continue
                cy, cx = choices[0]
                owner = next(i for i, (body, _) in masks.items() if body[cy, cx])
                witnesses.setdefault(owner, []).append((cx, cy))
            barriers = {}
            for identity, cells in witnesses.items():
                xs, ys = zip(*cells)
                barriers[identity] = [min(xs), min(ys), max(xs)+1, max(ys)+1]
            common = dict(variant=variant.name, slot=slot.name, blockers=sorted(barriers),
                          barrier_rectangles=barriers)
            for index, target in enumerate(grid.service_targets):
                if not np.any(reached & target):
                    problems.append(dict(**common, demand_id=None, instance_id=None, fixed_service=index))
            for assignment in layout.get("service", {}).get(variant.name, {}).get(slot.name, []):
                for identity in assignment["by"]:
                    if not np.any(masks[identity][1] & reached):
                        problems.append(dict(**common, demand_id=assignment["demand_id"], instance_id=identity))
    return problems
