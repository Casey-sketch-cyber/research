"""Constrained archive extraction and geometry-only pickle loading."""
from __future__ import annotations

import pickle
import shutil
import zipfile
import zlib
from pathlib import Path
from typing import Any, BinaryIO


def extract_named(zip_path: Path, basename: str, destination: Path) -> Path:
    """Extract one uniquely named regular member to an explicit local destination."""
    with zipfile.ZipFile(zip_path) as archive:
        members = [m for m in archive.infolist() if not m.is_dir() and Path(m.filename).name == basename]
        if len(members) != 1:
            raise ValueError(f"Expected exactly one archive member named {basename}")
        member = members[0]
        destination.parent.mkdir(parents=True, exist_ok=True)
        if destination.exists() and destination.stat().st_size == member.file_size:
            crc = 0
            with destination.open("rb") as cached:
                for block in iter(lambda: cached.read(1024 * 1024), b""):
                    crc = zlib.crc32(block, crc)
            if crc == member.CRC:
                return destination
        temporary = destination.with_suffix(destination.suffix + ".part")
        with archive.open(member) as source, temporary.open("wb") as target:
            shutil.copyfileobj(source, target, length=1024 * 1024)
        if temporary.stat().st_size != member.file_size:
            raise ValueError("Incomplete extraction")
        temporary.replace(destination)
    return destination


class GeometryUnpickler(pickle.Unpickler):
    """Allow only known geometry/numeric constructors, never arbitrary code globals."""

    allowed = {
        ("shapely.io", "from_wkb"), ("shapely", "from_wkb"),
        ("shapely.geometry.polygon", "Polygon"), ("shapely.geometry.multipolygon", "MultiPolygon"),
        ("shapely.geometry.linestring", "LineString"), ("shapely.geometry.multilinestring", "MultiLineString"),
        ("shapely.geometry.point", "Point"), ("shapely.geometry.collection", "GeometryCollection"),
        ("numpy.core.multiarray", "_reconstruct"), ("numpy.core.multiarray", "scalar"),
        ("numpy._core.multiarray", "_reconstruct"), ("numpy._core.multiarray", "scalar"),
        ("numpy", "ndarray"), ("numpy", "dtype"),
        ("builtins", "set"), ("builtins", "frozenset"),
        ("networkx.classes.graph", "Graph"),
    }

    def find_class(self, module: str, name: str) -> Any:
        """Fail closed on any undeclared global referenced by a pickle."""
        if (module, name) not in self.allowed:
            raise pickle.UnpicklingError(f"Disallowed pickle global: {module}.{name}")
        return super().find_class(module, name)


def read_geometry_pickle(stream: BinaryIO) -> Any:
    """Load only the constrained geometry/numeric pickle representation."""
    return GeometryUnpickler(stream).load()
