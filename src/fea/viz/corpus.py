"""Draw source-normalized space classes and corpus distributions."""
from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import PathPatch, Patch
from matplotlib.path import Path as MplPath
from shapely.geometry.polygon import orient

from fea.geometry.unit import Unit, parts

COLORS = {"furnishable": "#d4e9d4", "walkable_only": "#d9eafa", "fixed_service": "#bcbcbc", "excluded": "#f4ead5"}


def draw_geometry(ax, geometry, color: str, filled: bool = True, width: float = 1.5):
    """Render polygon holes correctly and support opening line geometries."""
    if geometry.is_empty:
        return
    if geometry.geom_type == "Polygon":
        polygon = orient(geometry)
        vertices, codes = [], []
        for ring in [polygon.exterior, *polygon.interiors]:
            points = list(ring.coords)
            vertices.extend(points)
            codes.extend([MplPath.MOVETO] + [MplPath.LINETO] * (len(points) - 2) + [MplPath.CLOSEPOLY])
        ax.add_patch(PathPatch(MplPath(vertices, codes), facecolor=color if filled else "none", edgecolor=color, linewidth=width))
    elif geometry.geom_type in ("LineString", "LinearRing"):
        ax.plot(*geometry.xy, color=color, linewidth=width)
    else:
        for child in getattr(geometry, "geoms", []):
            draw_geometry(ax, child, color, filled, width)


def draw_unit(ax, unit: Unit, short: bool = False):
    """Show all class layers and distinguish the selected entrance from other doors."""
    for name, color in COLORS.items():
        draw_geometry(ax, unit.classes[name], color, width=0.6)
    draw_geometry(ax, unit.walls, "#333333", width=0.7)
    for opening in unit.windows:
        draw_geometry(ax, opening, "#167dcc", width=2.2)
    for opening in unit.doors:
        draw_geometry(ax, opening, "#dc8c18", width=2)
    if unit.entrance is not None:
        draw_geometry(ax, unit.entrance, "#bf2441", width=3)
    if "toilet_geometry" in unit.meta:
        from shapely import from_wkt
        draw_geometry(ax, from_wkt(unit.meta["toilet_geometry"]), "#555555", filled=False, width=1)
    ax.autoscale_view()
    ax.set_aspect("equal")
    ax.set_xlabel("Local x (m)")
    ax.set_ylabel("Local y (m)")
    ax.set_title(f"{unit.source} | furnishable {unit.classes['furnishable'].area:.2f} m²" + ("" if short else f"\n{unit.unit_key}"), fontsize=10)
    ax.spines[["top", "right"]].set_visible(False)


def render_samples(units: list[Unit], output: Path):
    """Write individual 300-dpi samples and a review contact sheet."""
    output.mkdir(parents=True, exist_ok=True)
    legend = [Patch(color=value, label=key.replace("_", " ")) for key, value in COLORS.items()]
    legend += [Patch(color=value, label=key) for key, value in [("walls", "#333333"), ("door", "#dc8c18"), ("window", "#167dcc"), ("entrance", "#bf2441")]]
    for i, unit in enumerate(units):
        fig, ax = plt.subplots(figsize=(7, 7), layout="constrained")
        draw_unit(ax, unit)
        fig.legend(handles=legend, loc="outside lower center", ncol=4, fontsize=8)
        fig.savefig(output / f"{unit.source}_{i % 8 + 1:02d}.png", dpi=300)
        plt.close(fig)
    fig, axes = plt.subplots(6, 4, figsize=(16, 23), layout="constrained")
    for ax, unit in zip(axes.flat, units):
        draw_unit(ax, unit, short=True)
    fig.legend(handles=legend, loc="outside lower center", ncol=4, fontsize=11)
    fig.savefig(output.parent / "sample_contact_sheet.png", dpi=180)
    plt.close(fig)


def render_histogram(frame, output: Path, digest: str):
    """Plot the actual included-unit furnishable-area distribution by source."""
    output.parent.mkdir(parents=True, exist_ok=True)
    fig, axes = plt.subplots(1, 3, figsize=(12, 3.8), sharex=True, layout="constrained")
    for ax, source in zip(axes, ("D1", "D2", "D3")):
        values = frame[(frame.source == source) & frame.include].furnishable_area_m2
        ax.hist(values, bins=15, color="#447c9d", edgecolor="white")
        ax.set_title(f"{source} (n={len(values):,})")
        ax.set_xlabel("Furnishable area (m²)")
        ax.set_ylabel("Included units")
    fig.savefig(output.with_suffix(".png"), dpi=300, metadata={"Description": "config_hash=" + digest})
    fig.savefig(output.with_suffix(".pdf"), metadata={"Subject": "config_hash=" + digest, "Creator": "Research Automation"})
    plt.close(fig)
