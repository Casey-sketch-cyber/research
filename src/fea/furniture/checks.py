"""Transparent, deliberately broad ABO reference comparisons."""
from __future__ import annotations

import pandas as pd

DIMENSIONS = ["width", "depth", "height"]
REFERENCE_TYPES = ["BED", "BED_FRAME", "CABINET", "CHAIR", "DESK", "SHELF", "SOFA", "TABLE", "AV_FURNITURE", "BEAN_BAG_CHAIR", "FURNITURE"]
STATIC_TYPES = {"single_bed": ["BED", "BED_FRAME"], "double_bed": ["BED", "BED_FRAME"],
                "wardrobe": ["CABINET"], "shelving": ["SHELF"], "desk": ["DESK"],
                "dining_table_2": ["TABLE"], "dining_table_4": ["TABLE"], "sofa_2": ["SOFA"], "armchair": ["CHAIR"]}


def trim_type(frame: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """Drop a listing if any dimension exceeds its type's untrimmed 99th percentile."""
    upper = frame[DIMENSIONS].quantile(0.99)
    return frame.loc[frame[DIMENSIONS].le(upper).all(axis=1)], upper.to_dict()


def summary(frame: pd.DataFrame) -> dict:
    """Return medians and explicit quartile endpoints in metres."""
    result = {"n": len(frame)}
    for dimension, suffix in zip(DIMENSIONS, ("w", "d", "h")):
        values = frame[dimension]
        q25, q75 = values.quantile([0.25, 0.75]).tolist()
        result.update({f"median_{suffix}": values.median(), f"q25_{suffix}": q25,
                       f"q75_{suffix}": q75, f"iqr_{suffix}": q75 - q25})
    return result


def outside_interval(width: float, depth: float, statistics: dict) -> bool:
    """Compare orientation-labelled dimensions, without swapping axes to improve agreement."""
    return not (statistics["q25_w"] <= width <= statistics["q75_w"] and statistics["q25_d"] <= depth <= statistics["q75_d"])


def configured_rows(furniture: dict):
    """Yield every configured footprint with a declared comparison limitation."""
    for name, value in furniture["static_items"].items():
        yield name, "static", value["footprint"], STATIC_TYPES[name], False, "Keep: author design default; mixed product sizes/types do not establish an appropriate compact-dwelling replacement."
    for name, value in furniture["transformable_items"].items():
        for state, spec in value["states"].items():
            types = []
            if state == "deployed":
                types = ["BED", "BED_FRAME"] if "bed" in name else (["DESK"] if "desk" in name else ["TABLE"])
            elif name in ("sofa_bed", "wall_bed_over_sofa"):
                types = ["SOFA"]
            elif name == "extendable_table":
                types = ["TABLE"]
            yield name, state, spec["footprint"], types, True, "Keep pending separate evidence: ABO broad product types do not identify this transformation mechanism or state; any ordinary-furniture analogue is contextual only."
    for name, value in furniture.get("optional_items", {}).items():
        yield name, "optional", value["footprint"], ["BED", "BED_FRAME"], True, "Keep outside main experiments: the listing dimensions do not validate the stacked arrangement or ceiling-height requirement."
