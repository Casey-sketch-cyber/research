"""Build D1 units from actually assigned apartment geometries and simulation rows."""
from __future__ import annotations

import hashlib
from collections.abc import Iterator
from pathlib import Path

import numpy as np
import pandas as pd
from shapely import from_wkt
from shapely.geometry import GeometryCollection
from tqdm import tqdm

from fea.geometry.unit import Unit, parts, polygon_union
from .archives import extract_named

KEYS = ["site_id", "building_id", "floor_id", "apartment_id"]


def opaque_id(value: object) -> str:
    """Create reproducible opaque keys while retaining grouping semantics."""
    return hashlib.sha256(str(value).encode()).hexdigest()[:20]


def load_d1(config: dict, completed_keys: set[str] | None = None) -> Iterator[Unit]:
    """Yield all identifiable residential units; the common filter runs afterward."""
    root = Path(config["paths"]["raw"]) / "swiss_dwellings"
    archive = root / "swiss-dwellings-v3.0.0.zip"
    geometry_path = extract_named(archive, "geometries.csv", root / "extracted/geometries.csv")
    wanted = KEYS + ["unit_usage", "entity_type", "entity_subtype", "geometry"]
    chunks = []
    public = {}
    for frame in tqdm(pd.read_csv(geometry_path, usecols=wanted, dtype={"apartment_id": "string"}, chunksize=100000), desc="D1 read"):
        circulation = frame[(frame.unit_usage == "PUBLIC") & (frame.entity_type == "area") &
                            frame.entity_subtype.isin(["CORRIDOR", "CORRIDORS_AND_HALLS", "STAIRCASE", "LOBBY", "FOYER"])]
        for key, group in circulation.groupby(KEYS[:3]):
            public.setdefault(key, []).extend(from_wkt(group.geometry.to_numpy()))
        frame = frame[(frame.unit_usage == config["corpus"]["d1_unit_usage"]) & frame.apartment_id.notna()].copy()
        frame["geom"] = from_wkt(frame.pop("geometry").to_numpy())
        chunks.append(frame)
    geometry = pd.concat(chunks, ignore_index=True)
    del chunks
    public = {key: polygon_union(value) for key, value in public.items()}
    simulation_path = extract_named(archive, "simulations.csv", root / "extracted/simulations.csv")
    columns = pd.read_csv(simulation_path, nrows=0).columns
    fields = [c for c in columns if (c.startswith("sun_") and c.endswith("_mean")) or c.startswith("noise_")]
    sim = pd.read_csv(simulation_path, usecols=KEYS + fields, dtype={"apartment_id": "string"})
    simulations = sim.groupby(KEYS, dropna=False)[fields].mean().to_dict("index")
    del sim
    mapping = config["corpus"]["d1_subtype_classes"]
    room_types = set(mapping["furnishable"]) - {"STOREROOM", "CLOAKROOM"}
    for key, frame in tqdm(geometry.groupby(KEYS, sort=True), desc="D1 units"):
        unit_key = "D1:" + opaque_id(tuple(str(v) for v in key))
        if completed_keys and unit_key in completed_keys:
            continue
        areas = frame[frame.entity_type == "area"]
        if areas.empty:
            continue
        classes = {name: polygon_union(areas.loc[areas.entity_subtype.isin(subtypes), "geom"].tolist())
                   for name, subtypes in mapping.items()}
        fixed_objects = frame[(frame.entity_type == "feature") | (frame.entity_subtype == "COLUMN")].geom.tolist()
        fixed = polygon_union(fixed_objects)
        classes["fixed_service"] = polygon_union([classes["fixed_service"], fixed])
        classes["furnishable"] = classes["furnishable"].difference(fixed)
        classes["walkable_only"] = classes["walkable_only"].difference(fixed)
        classes["storage_only"] = classes["storage_only"].difference(fixed)
        windows = parts(polygon_union(frame.loc[frame.entity_subtype == "WINDOW", "geom"].tolist()))
        doors = parts(polygon_union(frame.loc[frame.entity_subtype.isin(["DOOR", "ENTRANCE_DOOR"]), "geom"].tolist()))
        semantic = frame.loc[frame.entity_subtype == "ENTRANCE_DOOR", "geom"].tolist()
        entrances = [door for door in doors if any(door.intersection(candidate).area > 1e-9 for candidate in semantic)]
        method = "source_entrance_door"
        if not entrances:
            shared = public.get(key[:3], GeometryCollection())
            inside = polygon_union([classes["furnishable"], classes["storage_only"], classes["walkable_only"]])
            entrances = [door for door in doors if door.distance(shared) <= 1e-7 and door.distance(inside) <= 1e-7]
            method = "public_circulation_contact"
        known_spaces = polygon_union([classes[k] for k in ("furnishable", "storage_only", "walkable_only", "fixed_service")])
        entrance = min(entrances, key=lambda g: (g.distance(known_spaces) if not known_spaces.is_empty else 0, g.wkb_hex)) if entrances else None
        entrance_contact = entrance.distance(known_spaces) if entrance is not None and not known_spaces.is_empty else None
        walls = polygon_union(frame.loc[frame.entity_subtype.isin(["WALL", "COLUMN", "WINDOW"]), "geom"].tolist())
        walls = walls.difference(polygon_union(doors))
        classes["furnishable"] = classes["furnishable"].difference(walls)
        if not classes["storage_only"].is_empty:
            classes["storage_only"] = classes["storage_only"].difference(walls)
        classes["walkable_only"] = polygon_union([classes["walkable_only"], *doors]).difference(classes["fixed_service"])
        summary = simulations.get(key, {})
        summary = {name: float(value) for name, value in summary.items() if np.isfinite(value)}
        meta = {"entrance_method": method if entrance is not None else "unidentified", "entrance_candidates": len(entrances),
                "gross_area_method": "unavailable: source does not define unit gross area; no proxy is relabelled gross",
                "has_sanitary": bool(any(not g.is_empty and g.area > 0 for g in frame.loc[
                    ((frame.entity_type == "area") & frame.entity_subtype.isin(["BATHROOM", "SANITARY_ROOMS"])) |
                    ((frame.entity_type == "feature") & (frame.entity_subtype == "TOILET")), "geom"])),
                "has_kitchen": bool(any(not g.is_empty and g.area > 0 for g in frame.loc[
                    ((frame.entity_type == "area") & frame.entity_subtype.isin(["KITCHEN", "KITCHEN_DINING"])) |
                    ((frame.entity_type == "feature") & (frame.entity_subtype == "KITCHEN")), "geom"])),
                "has_kitchen_dining": bool((areas.entity_subtype == "KITCHEN_DINING").any()),
                "simulation_area_means": summary,
                "source_invalid_geometries": int(sum(not g.is_valid for g in frame.geom)),
                "entrance_distance_to_known_spaces_m": entrance_contact}
        yield Unit(unit_key, "D1", "D1:" + opaque_id(int(key[0])),
                   classes, walls, doors, windows, entrance, None,
                   sum(len(parts(g)) for g in areas.loc[areas.entity_subtype.isin(room_types), "geom"]), meta)
