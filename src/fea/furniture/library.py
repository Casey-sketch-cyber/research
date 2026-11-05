"""Unchanged furniture defaults expanded into typed states and grid rectangles."""
from __future__ import annotations

from dataclasses import dataclass
import math


@dataclass(frozen=True)
class State:
    """A footprint and active clearance strips, with capabilities."""
    name: str
    footprint: tuple[float, float]
    clearance: dict[str, float]
    serves: tuple[str, ...]


@dataclass(frozen=True)
class Item:
    """One library type; count limits are distinct from state-dependent capacity."""
    name: str
    states: tuple[State, ...]
    wall_backed: bool
    tall: bool
    effort: float
    storage_units: float
    max_instances: int


def library(config: dict, strategy: str = "S2", clearance_scale: float | None = None) -> dict[str, Item]:
    """Expand configured main items without optional loft beds or silent overrides."""
    if strategy not in config["strategies"]:
        raise ValueError("Unknown furniture strategy")
    scale = clearance_scale if clearance_scale is not None else config["meta"]["global_clearance_scale"]
    result = {}
    for section in (["static_items"] if strategy == "S0" else ["static_items", "transformable_items"]):
        for name, spec in config[section].items():
            states = spec.get("states", {"static": spec})
            result[name] = Item(name, tuple(State(state, tuple(value["footprint"]),
                {k: float(v)*scale for k, v in value.get("clearance", {}).items()},
                tuple(spec["serves"][state] if isinstance(spec["serves"], dict) else spec["serves"]))
                for state, value in states.items()), spec["wall_backed"], spec["tall"],
                spec.get("effort", 0.), spec.get("storage_units", 0.),
                config["max_instances"].get(name, config["max_instances"]["default"]))
    return result


def rotate_rect(rect: tuple[int, int, int, int], orientation: int) -> tuple[int, int, int, int]:
    """Rotate a grid rectangle about a shared back-left anchor by quarter turns."""
    x, y, w, h = rect
    return [(x, y, w, h), (-y-h, x, h, w), (-x-w, -y-h, w, h), (y, -x-w, h, w)][orientation//90]


def rectangles(state: State, resolution: float, orientation: int = 0) -> tuple[tuple, list[tuple], tuple]:
    """Return outward-rounded body, individual clearance strips and backing row."""
    ceil = lambda v: int(math.ceil(v/resolution-1e-9))
    w, d = map(ceil, state.footprint)
    c = {k: ceil(v) for k, v in state.clearance.items() if v > 0}
    strips = {"front": (0, d, w, c.get("front", 0)), "back": (0, -c.get("back", 0), w, c.get("back", 0)),
              "left": (-c.get("left", 0), 0, c.get("left", 0), d), "right": (w, 0, c.get("right", 0), d)}
    return (rotate_rect((0, 0, w, d), orientation),
            [rotate_rect(strips[k], orientation) for k in ("front", "back", "left", "right") if k in c],
            rotate_rect((0, -1, w, 1), orientation))
