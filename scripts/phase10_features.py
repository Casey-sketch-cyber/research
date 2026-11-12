"""Geometry-only plan features, grouped splits and leakage-free target construction."""
from dataclasses import dataclass
import json

import numpy as np
import pandas as pd

from fea.geometry.unit import Unit, parts
from phase07_p1_area import fit_reference, paired_gain

KINDS = ("furnishable", "storage_only", "walkable_only", "fixed_service")
NODE_NAMES = ("area", "width", "depth", "aspect", "compactness", "window_count", "window_length", "door_count") + KINDS
GLOBAL_NAMES = ("nia", "habitable_rooms", "width", "depth", "aspect", "compactness",
                "door_count", "window_count", "door_length", "window_length")


@dataclass
class PlanFeatures:
    unit_key: str
    source: str
    group_id: str
    nia: float
    nodes: np.ndarray
    edges: np.ndarray
    global_features: np.ndarray
    tabular_features: np.ndarray


def shape_features(geometry):
    area = float(geometry.area)
    x0, y0, x1, y1 = geometry.bounds
    width, depth = sorted((float(x1-x0), float(y1-y0)))
    perimeter = float(geometry.length)
    return [area, width, depth, depth / max(width, 1e-8),
            4*np.pi*area / max(perimeter**2, 1e-8)]


def extract_geometry(serialized, tolerance):
    """Build component-level features from interior polygons and openings."""
    unit = Unit.from_dict(json.loads(serialized))
    interior = unit.interior
    components, kinds = [], []
    for index, kind in enumerate(KINDS):
        geometry = unit.classes.get(kind)
        if geometry is None:
            continue
        for part in parts(geometry.difference(unit.walls)):
            if part.area > 1e-8:
                components.append(part)
                kinds.append(index)
    if not components or interior.is_empty:
        raise ValueError("An evaluable plan has no graph components")
    door_links = []
    node_values = []
    for component, kind in zip(components, kinds):
        near_doors = [i for i, door in enumerate(unit.doors) if component.distance(door) <= tolerance]
        near_windows = [window for window in unit.windows if component.distance(window) <= tolerance]
        door_links.append(set(near_doors))
        base = shape_features(component)
        node_values.append([*base, len(near_windows), sum(w.length for w in near_windows),
                            len(near_doors), *(int(kind == j) for j in range(len(KINDS)))])
    edges = []
    for i, shape in enumerate(components):
        for j in range(i+1, len(components)):
            neighbor = components[j]
            adjacency = shape.distance(neighbor) <= tolerance and (
                shape.boundary.intersection(neighbor.buffer(tolerance)).length > 2*tolerance
            )
            if adjacency or door_links[i].intersection(door_links[j]):
                edges.extend(((i, j), (j, i)))
    nodes = np.asarray(node_values, dtype=np.float32)
    edge_array = np.asarray(edges, dtype=np.int64).reshape(-1, 2)
    area, width, depth, aspect, compact = shape_features(interior)
    global_features = np.asarray([area, unit.n_rooms, width, depth, aspect, compact, len(unit.doors),
                                  len(unit.windows), sum(d.length for d in unit.doors),
                                  sum(w.length for w in unit.windows)], dtype=np.float32)
    node_kinds = np.asarray(kinds)
    class_areas = [float(nodes[node_kinds == index, 0].sum()) for index in range(len(KINDS))]
    class_counts = [int((node_kinds == index).sum()) for index in range(len(KINDS))]
    tabular = np.concatenate([global_features, class_areas, class_counts, nodes[:, :8].mean(0),
                              nodes[:, :8].max(0), [len(edges)//2, len(components)]])
    if not np.isfinite(nodes).all() or not np.isfinite(tabular).all():
        raise ValueError("Nonfinite plan features")
    return PlanFeatures(unit.unit_key, unit.source, unit.group_id, area, nodes, edge_array,
                        global_features, tabular.astype(np.float32))


def split_groups(features, settings, seed):
    """Freeze D1 groups and retain D2/D3 as external sets."""
    table = pd.DataFrame([(v.unit_key, v.source, v.group_id, v.nia) for v in features],
                         columns=["unit_key", "source", "group_id", "nia_m2"]).sort_values("unit_key")
    if table.unit_key.duplicated().any() or table.group_id.isna().any():
        raise ValueError("Group split input differs")
    groups = sorted(table.loc[table.source == "D1", "group_id"].unique())
    shuffled = np.random.default_rng(seed).permutation(groups)
    train = int(round(settings["train"]*len(groups)))
    val = int(round(settings["val"]*len(groups)))
    mapping = {group: ("train" if i < train else "val" if i < train+val else "D1_test")
               for i, group in enumerate(shuffled)}
    table["split"] = table.source.map({"D2": "D2_external", "D3": "D3_external"})
    d1 = table.source.eq("D1")
    table.loc[d1, "split"] = table.loc[d1, "group_id"].map(mapping)
    if table.split.isna().any() or set(table.split) != {"train", "val", "D1_test", "D2_external", "D3_external"}:
        raise ValueError("A required split is empty")
    if table[d1].groupby("group_id").split.nunique().max() != 1:
        raise ValueError("D1 group split leaks")
    return table.reset_index(drop=True)


def targets(corrected, split):
    """Generate exact and bounded labels with a train-only static area reference."""
    keys = ["unit_key", "household"]
    capacity = corrected.pivot(index=keys, columns="strategy", values="fci_validator").reset_index()
    table = capacity.merge(split, on="unit_key", validate="many_to_one")
    if len(table) != len(capacity):
        raise ValueError("Missing geometry for a corrected target")
    parts = []
    knots = []
    for household, frame in table.groupby("household", sort=True):
        frame = frame.copy()
        train = frame[frame.split == "train"]
        reference = fit_reference(train.nia_m2, train.S0)
        gain = paired_gain(reference, frame.S0.to_numpy(), frame.S2.to_numpy())
        frame["saving_m2"] = gain["delta_ea_m2"]
        frame["saving_lower_bound_m2"] = gain["delta_ea_lower_bound_m2"]
        frame["saving_identified"] = gain["delta_gain_identified"]
        parts.append(frame)
        knots.extend(dict(household=household, nia_bin_midpoint_m2=area, fci_s0=score, n_train=count)
                     for area, score, count in zip(reference["area"], reference["capacity"], reference["counts"]))
    frame = pd.concat(parts, ignore_index=True).sort_values(keys).reset_index(drop=True)
    return frame.rename(columns={"S0": "fci_S0", "S2": "fci_S2"}), pd.DataFrame(knots)
