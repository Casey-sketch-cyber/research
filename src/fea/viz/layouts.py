"""Per-slot pilot views of actual validated layouts, including access routes."""
from __future__ import annotations

from collections import deque
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Patch
import numpy as np
from scipy import ndimage

from fea.furniture.library import library, rectangles
from fea.geometry.raster import rasterize
from fea.validate import validate_layout
from .corpus import draw_unit


def _paths(reached, entrance, targets):
    """Draw shortest four-neighbour routes within the checked covered area (illustrative guides, not disc-centre trajectories)."""
    if not reached.any() or not entrance.any(): return []
    distance = ndimage.distance_transform_edt(~entrance)
    candidates = np.argwhere(reached)
    start = tuple(candidates[np.argmin(distance[reached])])
    predecessor = {start: None}; queue = deque([start])
    while queue:
        y, x = queue.popleft()
        for dy, dx in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            v = y+dy, x+dx
            if 0 <= v[0] < reached.shape[0] and 0 <= v[1] < reached.shape[1] and reached[v] and v not in predecessor:
                predecessor[v] = (y, x); queue.append(v)
    paths = []
    for target in targets:
        points = [tuple(v) for v in np.argwhere(target & reached) if tuple(v) in predecessor]
        if not points: continue
        point = min(points, key=lambda p: (p[0]-start[0])**2+(p[1]-start[1])**2)
        route = []
        while point is not None: route.append(point); point = predecessor[point]
        paths.append(np.asarray(route))
    return paths


def render_layout(unit, layout: dict, config: dict, household, output: Path, grid=None):
    """Render all six normal-day slots from the saved positions/states/assignments."""
    grid = grid or rasterize(unit, layout["resolution_m"])
    checked = validate_layout(layout, grid, config, household, diagnostics=True)
    items = library(config["furniture"], layout["strategy"], household.overrides.get("global_clearance_scale"))
    color_names = sorted(library(config["furniture"]))
    colors = {name: plt.get_cmap("tab20")(i%20) for i, name in enumerate(color_names)}
    fig, axes = plt.subplots(2, 3, figsize=(15, 10), layout="constrained")
    for ax, slot in zip(axes.flat, household.slots):
        draw_unit(ax, unit, short=True)
        reached = checked["paths"]["normal"][slot.name]
        ny, nx = reached.shape; ox, oy = grid.origin; r = grid.resolution
        ax.imshow(np.ma.masked_where(~reached, reached), origin="lower", extent=(ox, ox+nx*r, oy, oy+ny*r),
                  cmap="Blues", vmin=0, vmax=1, alpha=.12, interpolation="nearest")
        assigned = {i for a in layout.get("service", {}).get("normal", {}).get(slot.name, []) for i in a["by"]}
        targets = []
        for placed in layout["items"]:
            state_name = placed["states"]["normal"][slot.name]
            state = next(s for s in items[placed["type"]].states if s.name == state_name)
            body, clearances, _ = rectangles(state, r, placed["orientation_deg"])
            target = np.zeros_like(reached)
            cx, cy = [round((placed[k]-grid.origin[i])/r) for i, k in enumerate(("x", "y"))]
            for dx, dy, w, h in clearances:
                ax.add_patch(Rectangle((placed["x"]+dx*r, placed["y"]+dy*r), w*r, h*r,
                    facecolor=colors[placed["type"]], alpha=.14, edgecolor="none"))
                target[cy+dy:cy+dy+h, cx+dx:cx+dx+w] = True
            if placed["instance_id"] in assigned: targets.append(target)
            dx, dy, w, h = body
            x, y = placed["x"]+dx*r, placed["y"]+dy*r
            ax.add_patch(Rectangle((x, y), w*r, h*r, facecolor=colors[placed["type"]],
                edgecolor="#333333", lw=.65, alpha=.8, hatch="///" if state_name == "stowed" else None))
            label = "".join(p[0].upper() for p in placed["type"].split("_"))+placed["instance_id"].rsplit("#", 1)[-1]
            ax.text(x+w*r/2, y+h*r/2, label, ha="center", va="center", fontsize=6)
        for path in _paths(reached, grid.entrance, targets):
            ax.plot(ox+(path[:, 1]+.5)*r, oy+(path[:, 0]+.5)*r, color="#156d9c", lw=.8, alpha=.8)
        x0, y0, x1, y1 = unit.interior.bounds
        ax.set_xlim(x0-.3, x1+.3); ax.set_ylim(y0-.3, y1+.3)
        ax.set_title(f"{slot.name} ({slot.hours:g} h)", fontsize=10)
    names = sorted({i["type"] for i in layout["items"]})
    handles = [Patch(facecolor=colors[n], label=n.replace("_", " ")) for n in names]
    handles += [Patch(facecolor="none", edgecolor="gray", hatch="///", label="stowed"), Patch(facecolor="#156d9c", alpha=.2, label="reachable area / guide")]
    if grid.kitchen is not None and grid.kitchen.any(): handles.append(Patch(facecolor="#d3d3d3",hatch="...",label="walkable kitchen"))
    fig.legend(handles=handles, loc="outside lower center", ncol=5, fontsize=8)
    fig.suptitle(f"{unit.unit_key} | {household.name} | {layout['strategy']}\n"
        f"NIA {unit.interior.area:.2f} m² | Furnishable {unit.classes['furnishable'].area:.2f} m² | "
        f"Validated FCI {checked['fci']:.4f} | TB {checked['tb']:.3f} | "
        f"{'VALID' if checked['pass'] else 'INVALID: '+str(len(checked['violations']))+' violations'}", fontsize=12)
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output, dpi=300); plt.close(fig)
