"""Household-normalized FCI, cyclic burden and monotone equivalent-area inversion."""
from __future__ import annotations

import numpy as np

from .households import Household, demanded_hours


def fci(household: Household, credits: dict[str, float]) -> dict:
    """Weight each variant's own served/demanded ratio; preserve demand occurrences."""
    ratios, served = {}, {}
    for variant in household.variants:
        served[variant.name] = sum(slot.hours*d.weight*float(credits.get(d.id, 0.))
            for slot in household.slots for d in variant.demand[slot.name])
        ratios[variant.name] = served[variant.name]/demanded_hours(household, variant.name)
    return {"fci": sum(v.frequency*ratios[v.name] for v in household.variants),
            "fci_by_variant": ratios, "served_hours_by_variant": served,
            "served_hours": sum(v.frequency*served[v.name] for v in household.variants),
            "demanded_hours": demanded_hours(household)}


def transformation_burden(items: list[dict], household: Household, efforts: dict[str, float]) -> float:
    """Frequency-weighted daily effort, including the final-to-first slot transition."""
    total = 0.
    for variant in household.variants:
        for item in items:
            states = [item["states"][variant.name][slot.name] for slot in household.slots]
            total += variant.frequency*efforts[item["type"]]*sum(a != b for a, b in zip(states, states[-1:]+states[:-1]))
    return total


def invert_monotone(area: list[float], fitted_fci: list[float], target: float) -> dict:
    """Invert a continuous piecewise-linear monotone fit at its first crossing.

    Above support returns a censored lower bound, never an extrapolated saving.
    """
    x, y = np.asarray(area, float), np.asarray(fitted_fci, float)
    if len(x) < 2 or len(x) != len(y) or np.any(np.diff(x) <= 0) or np.any(np.diff(y) < 0):
        raise ValueError("Strict area ordering and nondecreasing capacity required")
    if target > y[-1]:
        return {"fea_m2": None, "right_censored": True, "lower_bound_m2": float(x[-1])}
    i = int(np.searchsorted(y, target, side="left"))
    value = x[0] if i == 0 else x[i-1]+(target-y[i-1])/(y[i]-y[i-1])*(x[i]-x[i-1])
    return {"fea_m2": float(value), "right_censored": False, "lower_bound_m2": None}
