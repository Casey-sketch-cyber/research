"""Independent layout checker: no solver or candidate-generation imports."""
from __future__ import annotations

from collections import Counter, deque
import itertools
import math

import numpy as np
from scipy.ndimage import distance_transform_edt

from .geometry.raster import Raster, FURNISHABLE, STORAGE_ONLY, WALKABLE
from .households import Household
from .metrics import fci


def _rectangles(spec: dict, state: str, resolution: float, angle: int, scale: float):
    """Independently reconstruct outward-rounded rectangles from original config."""
    value = spec.get("states", {}).get(state, spec)
    w, d = [math.ceil(float(v)/resolution-1e-9) for v in value["footprint"]]
    offsets = [(0, 0, w, d)]
    for side, clearance in value.get("clearance", {}).items():
        c = math.ceil(float(clearance)*scale/resolution-1e-9)
        if c <= 0: continue
        offsets.append({"front": (0, d, w, c), "back": (0, -c, w, c),
                        "left": (-c, 0, c, d), "right": (w, 0, c, d)}[side])
    offsets.append((0, -1, w, 1))
    rotated = []
    for x, y, width, height in offsets:
        corners = [(x, y), (x+width, y), (x, y+height), (x+width, y+height)]
        for _ in range(angle//90): corners = [(-b, a) for a, b in corners]
        xs, ys = zip(*corners)
        rotated.append((min(xs), min(ys), max(xs)-min(xs), max(ys)-min(ys)))
    return rotated[0], rotated[1:-1], rotated[-1]


def _mask(shape, anchor, rectangle):
    x, y = anchor
    dx, dy, w, h = rectangle
    x, y = x+dx, y+dy
    mask = np.zeros(shape, bool)
    valid = x >= 0 and y >= 0 and x+w <= shape[1] and y+h <= shape[0]
    if valid: mask[y:y+h, x:x+w] = True
    return mask, valid


def _reachable(grid: Raster, occupied: np.ndarray, walking_width: float) -> np.ndarray:
    """Explicit four-neighbour BFS after conservative Euclidean-radius erosion."""
    free = (grid.walkable & ~occupied) | grid.entrance_extension
    radius = walking_width/2
    # Subtract the blocked cell's half diagonal, so diagonal corners cannot
    # falsely admit a walking disc that the centre-to-centre distance misses.
    distances = distance_transform_edt(np.pad(free, 1))[1:-1, 1:-1]*grid.resolution-grid.resolution/math.sqrt(2)
    centres = free & (distances >= radius-1e-9)
    seen = np.zeros_like(free)
    queue = deque(map(tuple, np.argwhere(centres & grid.entrance_extension)))
    for y, x in queue: seen[y, x] = True
    while queue:
        y, x = queue.popleft()
        for dy, dx in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            a, b = y+dy, x+dx
            if 0 <= a < free.shape[0] and 0 <= b < free.shape[1] and centres[a, b] and not seen[a, b]:
                seen[a, b] = True
                queue.append((a, b))
    return seen & grid.walkable


def validate_layout(layout: dict, grid: Raster, config: dict, household: Household, diagnostics: bool = False) -> dict:
    """Recompute geometry, assigned service, reachability, FCI and cyclic TB.

    Served flags/credits in input are ignored. Unreachable assigned items receive
    zero service, while structural violations invalidate the layout. The checker
    evaluates the supplied assignment, not an unreported second optimization.
    """
    furniture = config["furniture"]
    strategy = layout["strategy"]
    raw = dict(furniture["static_items"])
    if strategy in ("S1", "S2"): raw.update(furniture["transformable_items"])
    violations, unreachable, credits = [], [], {}
    if strategy not in ("S0", "S1", "S2"): violations.append("unknown_strategy")
    items = layout.get("items", [])
    identifiers = [v["instance_id"] for v in items]
    if len(set(identifiers)) != len(items): violations.append("duplicate_instance_id")
    counts = Counter(v["type"] for v in items)
    for name, count in counts.items():
        if count > furniture["max_instances"].get(name, furniture["max_instances"]["default"]): violations.append("instance_limit:"+name)
    scale = household.overrides.get("global_clearance_scale", furniture["meta"]["global_clearance_scale"])
    width = household.overrides.get("walking_width", furniture["meta"]["walking_width"])
    if abs(layout.get("resolution_m", grid.resolution)-grid.resolution) > 1e-9: violations.append("resolution_mismatch")
    shapes, specs = {}, {}
    for item in items:
        identity, name = item["instance_id"], item["type"]
        if name not in raw:
            violations.append("disallowed_item:"+identity); continue
        spec = specs[identity] = raw[name]
        states = list(spec.get("states", {"static": spec}))
        coords = [(float(item[k])-grid.origin[i])/grid.resolution for i, k in enumerate(("x", "y"))]
        if not all(math.isfinite(v) and abs(v-round(v)) < 1e-6 for v in coords):
            violations.append("off_grid_anchor:"+identity); continue
        anchor = tuple(round(v) for v in coords)
        angle = item["orientation_deg"]
        if angle not in config["raster"]["orientations_deg"]:
            violations.append("orientation:"+identity); continue
        all_tokens = spec["serves"] if isinstance(spec["serves"], list) else sum(spec["serves"].values(), [])
        body_allowed = np.isin(grid.labels, [FURNISHABLE, STORAGE_ONLY] if set(all_tokens) == {"storage"} else [FURNISHABLE])
        clear_allowed = np.isin(grid.labels, [FURNISHABLE, STORAGE_ONLY, WALKABLE])
        for state in states:
            body_rect, clear_rects, back_rect = _rectangles(spec, state, grid.resolution, angle, scale)
            body, inside = _mask(grid.labels.shape, anchor, body_rect)
            clear = np.zeros_like(body)
            for rectangle in clear_rects:
                strip, valid = _mask(grid.labels.shape, anchor, rectangle)
                inside &= valid; clear |= strip
            back, back_inside = _mask(grid.labels.shape, anchor, back_rect)
            if not inside or np.any(body & ~body_allowed): violations.append("body_outside_allowed:"+identity+":"+state)
            if np.any(clear & ~clear_allowed): violations.append("clearance_outside_allowed:"+identity+":"+state)
            if spec["wall_backed"] and (not back_inside or np.any(back & ~grid.wall)): violations.append("wall_backing:"+identity)
            if spec["wall_backed"] and spec["tall"] and np.any(back & grid.window): violations.append("tall_window_backing:"+identity)
            shapes[identity, state] = body, clear
        for variant in household.variants:
            selected_states = []
            for slot in household.slots:
                state = item.get("states", {}).get(variant.name, {}).get(slot.name)
                selected_states.append(state)
                if state not in states: violations.append("invalid_state:"+identity)
            if strategy in ("S0", "S1") and len(set(selected_states)) > 1: violations.append("day_wide_state_changed:"+identity)
    paths, access = {}, {}
    for variant in household.variants:
        paths[variant.name] = {}
        for slot in household.slots:
            active = {}
            for item in items:
                state = item.get("states", {}).get(variant.name, {}).get(slot.name)
                if (item["instance_id"], state) in shapes: active[item["instance_id"]] = (state, *shapes[item["instance_id"], state])
            occupancy = np.zeros_like(grid.labels, dtype=np.int16)
            for _, body, _ in active.values(): occupancy += body
            if np.any(occupancy > 1): violations.append(f"body_overlap:{variant.name}:{slot.name}")
            for identity, (_, body, clear) in active.items():
                if np.any(clear & ((occupancy-body.astype(int)) > 0)): violations.append(f"clearance_collision:{variant.name}:{slot.name}:{identity}")
            reachable = _reachable(grid, occupancy > 0, width)
            paths[variant.name][slot.name] = reachable
            for index, target in enumerate(grid.service_targets):
                if not np.any(target & reachable): violations.append(f"fixed_service_unreachable:{variant.name}:{slot.name}:{index}")
            for identity, (_, _, clear) in active.items():
                access[identity] = bool(np.any(clear & reachable))
                if not access[identity]: unreachable.append(f"{variant.name}:{slot.name}:{identity}")
            assignments = layout.get("service", {}).get(variant.name, {}).get(slot.name, [])
            entries = {a.get("demand_id"): a for a in assignments}
            if len(entries) != len(assignments): violations.append("duplicate_demand_assignment")
            used = set()
            expected_ids = {d.id for d in variant.demand[slot.name]}
            if not set(entries) <= expected_ids: violations.append("unknown_demand_assignment")
            for demand in variant.demand[slot.name]:
                by = entries.get(demand.id, {}).get("by", [])
                if len(by) != len(set(by)) or not set(by) <= active.keys():
                    violations.append("invalid_assigned_instances:"+demand.id); by = []
                if set(by) & used: violations.append("instance_used_twice:"+demand.id)
                used.update(by)
                valid_by = [i for i in by if access.get(i, False)]
                tokens = {i: specs[i]["serves"] if isinstance(specs[i]["serves"], list) else specs[i]["serves"][active[i][0]] for i in valid_by}
                if demand.need == "storage":
                    if any("storage" not in tokens[i] for i in valid_by): violations.append("storage_capability:"+demand.id)
                    credits[demand.id] = min(1., sum(specs[i].get("storage_units", 0.) for i in valid_by if "storage" in tokens[i])/demand.units)
                else:
                    fulfilled = False
                    for option in household.capability_rules[demand.need]["satisfied_by"]:
                        if len(option) != len(valid_by): continue
                        fulfilled |= any(all(t in tokens[i] for t, i in zip(option, permutation)) for permutation in itertools.permutations(valid_by))
                    credits[demand.id] = float(fulfilled)
                    if by and len(valid_by) == len(by) and not fulfilled: violations.append("wrong_capability:"+demand.id)
    burden = 0.
    for variant in household.variants:
        for item in items:
            states = [item.get("states", {}).get(variant.name, {}).get(s.name) for s in household.slots]
            burden += variant.frequency*raw.get(item["type"], {}).get("effort", 0.)*sum(states[i] != states[i-1] for i in range(len(states)))
    violations = sorted(set(violations))
    metrics = fci(household, {} if violations else credits)
    result = {**metrics, "tb": burden, "pass": not violations, "violations": violations,
              "credits": credits, "unreachable_items": unreachable}
    if diagnostics: result["paths"] = paths
    return result
