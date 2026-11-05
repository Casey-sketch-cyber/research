"""Source-independent geometric dwelling representation."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from shapely import from_wkt, make_valid
from shapely.geometry import GeometryCollection
from shapely.geometry.base import BaseGeometry
from shapely.ops import unary_union


def parts(geometry: BaseGeometry) -> list[BaseGeometry]:
    """Return nonempty polygon components, dropping non-area repair remnants."""
    if geometry.is_empty:
        return []
    if geometry.geom_type == "Polygon":
        return [geometry]
    return [part for child in getattr(geometry, "geoms", []) for part in parts(child)]


def polygon_union(geometries: list[BaseGeometry]) -> BaseGeometry:
    """Make polygonal source geometries valid before unioning them."""
    return unary_union([p for g in geometries for p in parts(g if g.is_valid else make_valid(g))]) if geometries else GeometryCollection()


@dataclass
class Unit:
    """A dwelling in metres; source identifiers and world coordinates are not exported."""

    unit_key: str
    source: str
    group_id: str
    classes: dict[str, BaseGeometry]
    walls: BaseGeometry
    doors: list[BaseGeometry]
    windows: list[BaseGeometry]
    entrance: BaseGeometry | None
    gross_area_m2: float | None
    n_rooms: int
    meta: dict[str, Any] = field(default_factory=dict)

    @property
    def interior(self) -> BaseGeometry:
        """Known interior space; exterior excluded areas are not counted."""
        return polygon_union([self.classes.get(k, GeometryCollection()) for k in
                              ("furnishable", "storage_only", "walkable_only", "fixed_service")]).difference(self.walls)

    def to_dict(self) -> dict[str, Any]:
        """Serialize only normalized research geometry and nonidentifying metadata."""
        return {"unit_key": self.unit_key, "source": self.source, "group_id": self.group_id,
                "classes": {k: v.wkt for k, v in self.classes.items()}, "walls": self.walls.wkt,
                "doors": [g.wkt for g in self.doors], "windows": [g.wkt for g in self.windows],
                "entrance": self.entrance.wkt if self.entrance is not None else None,
                "gross_area_m2": self.gross_area_m2, "n_rooms": self.n_rooms, "meta": self.meta}

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> Unit:
        """Read the normalized unit interchange format."""
        record = dict(value)
        record["classes"] = {k: from_wkt(v) for k, v in record["classes"].items()}
        record["walls"] = from_wkt(record["walls"])
        for name in ("doors", "windows"):
            record[name] = [from_wkt(v) for v in record[name]]
        record["entrance"] = from_wkt(record["entrance"]) if record["entrance"] else None
        return cls(**record)
