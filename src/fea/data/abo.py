"""Read ABO listing metadata, with explicit units and no product-media downloads."""
from __future__ import annotations

import gzip
import json
import tarfile
from collections.abc import Iterator
from pathlib import Path
from typing import Any


def listings(path: Path) -> Iterator[dict[str, Any]]:
    """Iterate JSON lines inside the listings archive without extracting paths."""
    with tarfile.open(path) as archive:
        for member in sorted(archive.getmembers(), key=lambda item: item.name):
            if member.isfile() and member.name.endswith(".json.gz"):
                with gzip.open(archive.extractfile(member), "rt", encoding="utf-8") as stream:
                    for line in stream:
                        if line.strip():
                            yield json.loads(line)


def dimensions_m(item: dict[str, Any]) -> dict[str, float] | None:
    """Return width, depth (= listing length), height in metres, or no usable triple."""
    dimensions = item.get("item_dimensions")
    if not isinstance(dimensions, dict):
        return None
    factors = {"inches": 0.0254, "inch": 0.0254, "centimeters": 0.01, "centimetres": 0.01,
               "millimeters": 0.001, "millimetres": 0.001, "meters": 1.0, "metres": 1.0,
               "feet": 0.3048, "foot": 0.3048}
    result = {}
    for source, target in (("width", "width"), ("length", "depth"), ("height", "height")):
        record = dimensions.get(source, {})
        record = record.get("normalized_value", record)
        try:
            value = float(record["value"]) * factors[record["unit"].lower()]
        except (KeyError, TypeError, ValueError):
            return None
        if not 0 < value < float("inf"):
            return None
        result[target] = value
    return result


def product_types(item: dict[str, Any]) -> list[str]:
    """Extract all provided product type labels without guessing from titles."""
    return sorted({entry["value"] for entry in item.get("product_type", []) if entry.get("value")})
