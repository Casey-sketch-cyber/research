"""Freeze geometry-only reduced kit designs and disjoint transfer cohorts."""
from copy import deepcopy
from itertools import product
import json

import numpy as np
import pandas as pd

from fea.geometry.unit import Unit

BED = {"H1_single_commuter": ("wall_bed_single", "wall_bed_width_single"),
       "H3_couple_one_remote": ("wall_bed_double", "wall_bed_width_double")}


def candidate_grid(config, households, size):
    """Choose fixed maximin vectors from the configured design grid."""
    design = config["experiments"]["K_kit_design"]["variables"]
    rng = np.random.default_rng(config["seed"])
    result = {}
    for household in households:
        names = [name for name, spec in design.items()
                 if "applies_to" not in spec or household in spec["applies_to"]]
        all_vectors = np.asarray(list(product(*(design[name]["values"] for name in names))), dtype=float)
        if len(all_vectors) < size:
            raise ValueError("Too few configured kit combinations")
        scaled = (all_vectors-all_vectors.min(0))/np.ptp(all_vectors, axis=0)
        selected = [0, len(all_vectors)-1]
        priority = rng.permutation(len(all_vectors))
        while len(selected) < size:
            distances = ((scaled[:, None, :]-scaled[selected][None, :, :])**2).sum(axis=2).min(axis=1)
            distances[selected] = -1.
            chosen = priority[np.argmax(distances[priority])]
            selected.append(int(chosen))
        result[household] = [
            {"kit_id": f"{household.split('_')[0]}_kit_{i:02}",
             "dimensions": dict(zip(names, map(float, all_vectors[index])))}
            for i, index in enumerate(selected, 1)
        ]
    return result


def kit_configuration(base, household, candidate):
    """Apply only configured dimensions, retaining clearances and stowed depths."""
    config = deepcopy(base)
    if candidate is None:
        return config, {}
    variables = base["experiments"]["K_kit_design"]["variables"]
    dimensions = candidate["dimensions"]
    transform = config["furniture"]["transformable_items"]
    bed, bed_width = BED[household]
    for item, width_key, depth_key in [
        (bed, bed_width, None), ("fold_down_desk", "desk_width", "desk_depth_deployed"),
        ("drop_leaf_table", "table_width", "table_depth_deployed"),
    ]:
        states = transform[item]["states"]
        for state in states.values():
            state["footprint"][0] = dimensions[width_key]
        if depth_key:
            states["deployed"]["footprint"][1] = dimensions[depth_key]
    frontage = dimensions["wardrobe_frontage"]
    wardrobe = config["furniture"]["static_items"]["wardrobe"]
    wardrobe["footprint"][0] = frontage
    spec = variables["wardrobe_frontage"]
    wardrobe["storage_units"] = float(np.interp(frontage, spec["values"], spec["storage_units"]))
    def quality(name):
        values = variables[name]
        return float(np.interp(dimensions[name], values["values"], values["q"]))
    qualities = {bed: quality(bed_width), "fold_down_desk": min(quality("desk_width"), quality("desk_depth_deployed")),
                 "drop_leaf_table": min(quality("table_width"), quality("table_depth_deployed"))}
    return config, qualities


def balanced_order(frame, strata, seed):
    """Cycle over shuffled strata, drawing without replacement within each."""
    rng = np.random.default_rng(seed)
    groups = []
    for _, part in frame.sort_values("unit_key").groupby(strata, sort=True):
        indexes = part.index.to_numpy()
        groups.append(list(rng.permutation(indexes)))
    result = []
    ordering = rng.permutation(len(groups))
    while len(result) < len(frame):
        for i in ordering:
            if groups[i]:
                result.append(groups[i].pop())
    return frame.loc[result].reset_index(drop=True)


def select_shells(config, policy, sample, corpus):
    """Select training, novel-geometry holdout and real transfer sets."""
    limits = config["experiments"]["K_kit_design"]
    a, b = limits["target"]["nia_m2"]
    generated = sample[(sample.source == limits["target"]["source"]) & sample.nia_m2.between(a-1e-8, b+1e-8)]
    rows = []
    for row in generated.itertuples(index=False):
        unit = Unit.from_dict(json.loads(corpus.loc[row.unit_key, "unit_json"]))
        parameters = unit.meta["parameters"]
        rows.append(dict(unit_key=row.unit_key, source=row.source, nia_m2=row.nia_m2,
                         nominal_area_m2=parameters["gross_area_m2"], aspect_ratio=parameters["aspect_ratio"],
                         entrance_position=parameters["entrance_position"], window_position=parameters["window_position"]))
    shells = pd.DataFrame(rows)
    levels = limits["holdout"]
    novel = np.isclose(shells.aspect_ratio, levels["aspect_ratio"]) | shells.entrance_position.eq(levels["entrance_position"])
    strata = ["nominal_area_m2", "aspect_ratio", "entrance_position"]
    # Alternate area levels first, then advance within each area's shape/entry strata.
    def select_pool(frame, count, seed):
        rng = np.random.default_rng(seed)
        areas = list(frame.groupby("nominal_area_m2", sort=True))
        ranked = [balanced_order(part, strata[1:], seed+i) for i, (_, part) in enumerate(areas)]
        ids = []
        order = rng.permutation(len(ranked))
        for depth in range(max(map(len, ranked))):
            ids.extend(ranked[i].iloc[depth].to_dict() for i in order if len(ranked[i]) > depth)
            if len(ids) >= count:
                break
        return pd.DataFrame(ids[:count])

    train = select_pool(shells[~novel], policy["training_shells"], config["seed"])
    held = select_pool(shells[novel], policy["heldout_shells"], config["seed"]+1)
    real_rule = limits["real_plan_check"]
    real = sample[sample.source.isin(real_rule["sources"]) & (sample.nia_m2 <= real_rule["max_nia_m2"]+1e-8)].copy()
    real["area_band"] = np.floor(real.nia_m2/2).astype(int)
    real = balanced_order(real, ["source", "area_band"], config["seed"]+2).iloc[:policy["real_plans"]]
    real = real[["unit_key", "source", "nia_m2"]]
    result = []
    for label, frame, n in [("train", train, policy["training_shells"]), ("heldout", held, policy["heldout_shells"]),
                            ("real", real, policy["real_plans"])]:
        if len(frame) != n:
            raise ValueError("Insufficient eligible shell or real-plan support")
        table = frame.copy()
        table["set"], table["rank"] = label, np.arange(1, n+1)
        result.append(table)
    selected = pd.concat(result, ignore_index=True)
    if selected.unit_key.duplicated().any():
        raise ValueError("Kit cohorts overlap")
    return selected
