"""Review-approved inclusion, geometric deduplication and frozen experiment sampling."""
from __future__ import annotations

import hashlib
import json
from collections import Counter

import numpy as np
import pandas as pd
from shapely import normalize as canonical_geometry, set_precision

from fea.geometry.unit import Unit


def exclusion_reasons(row, config: dict) -> str:
    """Apply the unchanged NIA thresholds and minimum dwelling/scale requirements."""
    settings = config["corpus"]
    reasons = list(filter(None, row.geometry_failures.split(";")))
    if pd.isna(row.nia_m2):
        reasons.append("missing_nia")
    elif row.nia_m2 < settings["min_nia_m2"] - 1e-6:
        reasons.append("below_min_nia")
    elif row.nia_m2 > settings["max_nia_m2"] + 1e-6:
        reasons.append("above_max_nia")
    if settings["require_habitable_room"] and (row.n_rooms < 1 or not row.furnishable_area_m2 > 0):
        reasons.append("no_habitable_room")
    for name in ("sanitary", "kitchen"):
        if settings["require_" + name] and not row["has_" + name]:
            reasons.append("no_" + name)
    if row.source == "D2":
        if pd.isna(row.median_door_span_m) or pd.isna(row.median_wall_thickness_m):
            reasons.append("unmeasurable_scale")
        elif not (0.6 <= row.median_door_span_m <= 1.3 and 0.05 <= row.median_wall_thickness_m <= 0.50):
            reasons.append("implausible_scale")
    return ";".join(dict.fromkeys(reasons))


def geometry_hash(unit: Unit) -> str:
    """Hash source-independent normalized layers at one-micrometre precision.

    This identifies the normalized geometry as stored; it does not equate mirrored
    or quarter-turned plans. The analysis geometry itself is never quantized here.
    """
    def key(geometry):
        return canonical_geometry(set_precision(geometry.simplify(1e-7, preserve_topology=True), 1e-6)).wkb_hex
    payload = {"classes": {name: key(g) for name, g in sorted(unit.classes.items())},
               "walls": key(unit.walls), "doors": sorted(key(g) for g in unit.doors),
               "windows": sorted(key(g) for g in unit.windows),
               "entrance": key(unit.entrance) if unit.entrance is not None else None,
               "n_rooms": unit.n_rooms, "has_sanitary": unit.meta.get("has_sanitary"),
               "has_kitchen": unit.meta.get("has_kitchen")}
    return hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()


def deduplicate_frame(frame: pd.DataFrame, records: list[dict], config: dict) -> pd.DataFrame:
    """Keep a stable representative for every eligible normalized geometry."""
    frame = frame.copy()
    frame["eligible_before_dedup"] = frame.exclude_reason == ""
    frame["geometry_hash"] = ""
    frame["representative_key"] = frame.unit_key
    frame["n_duplicates"] = 0  # Additional copies; represented multiplicity is 1 + this value.
    frame["is_representative"] = True
    if config["corpus"]["deduplicate"]["enabled"]:
        for index in frame.index[frame.eligible_before_dedup]:
            frame.at[index, "geometry_hash"] = geometry_hash(Unit.from_dict(records[index]["unit"]))
        for _, group in frame[frame.eligible_before_dedup].groupby("geometry_hash", sort=True):
            indices = group.sort_values(["source", "unit_key"]).index
            representative = frame.at[indices[0], "unit_key"]
            frame.loc[indices, "representative_key"] = representative
            frame.loc[indices, "n_duplicates"] = len(indices) - 1
            frame.loc[indices[1:], "exclude_reason"] = "duplicate_geometry"
            frame.loc[indices[1:], "is_representative"] = False
    frame["include"] = frame.exclude_reason == ""
    return frame


def freeze_sample(frame: pd.DataFrame, config: dict) -> pd.DataFrame:
    """Choose proportionally stratified D1 units with a hard site cap and fixed seed."""
    frame = frame.copy()
    frame["nia_bin_2m2"] = np.floor((frame.nia_m2 + 1e-6) / 2) * 2
    frame["in_expA_sample"] = False
    eligible = frame[frame.include]
    frame.loc[eligible.index[eligible.source.isin(["D2", "D3"])], "in_expA_sample"] = True
    d1 = eligible[eligible.source == "D1"].sort_values("unit_key")
    settings = config["corpus"]["expA_sample"]["D1"]
    target = min(settings["n_max"], len(d1))
    rng = np.random.default_rng(config["seed"])
    groups = {key: list(rng.permutation(group.index)) for key, group in
              d1.groupby(["nia_bin_2m2", "n_rooms"], sort=True)}
    quotas = {key: len(indices) / max(1, len(d1)) * target for key, indices in groups.items()}
    chosen, sites, selected = Counter(), Counter(), []
    while len(selected) < target and groups:
        # Largest proportional deficit; exact ties resolve by the sorted stratum key.
        key = max(sorted(groups), key=lambda k: (quotas[k] - chosen[k]) / max(quotas[k], 1))
        while groups[key] and sites[frame.at[groups[key][-1], "group_id"]] >= settings["max_per_site"]:
            groups[key].pop()
        if not groups[key]:
            del groups[key]
            continue
        index = groups[key].pop()
        selected.append(index)
        chosen[key] += 1
        sites[frame.at[index, "group_id"]] += 1
    frame.loc[selected, "in_expA_sample"] = True
    return frame


def distribution_rows(frame: pd.DataFrame, value: str, category: str) -> list[dict]:
    """Produce counts and distribution endpoints without inventing empty-group values."""
    rows = []
    for source, group in frame.groupby("source"):
        values = pd.to_numeric(group[value], errors="coerce").dropna()
        rows.append({"source": source, "category": category, "measure": value, "n": len(values),
                     **{name: values.quantile(q) if len(values) else None
                        for name, q in (("min", 0), ("q25", .25), ("median", .5), ("q75", .75), ("max", 1))}})
    return rows
