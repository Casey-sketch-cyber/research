"""Validated daily schedules; no furniture assignment or solver logic."""
from __future__ import annotations

import math
from dataclasses import dataclass


@dataclass(frozen=True)
class Slot:
    name: str
    start: float
    end: float

    @property
    def hours(self) -> float:
        """Duration including midnight wrap; equal endpoints are rejected."""
        return (self.end - self.start) % 24


@dataclass(frozen=True)
class Demand:
    id: str
    need: str
    weight: float
    units: float | None = None


@dataclass(frozen=True)
class Variant:
    name: str
    frequency: float
    demand: dict[str, tuple[Demand, ...]]


@dataclass(frozen=True)
class Household:
    name: str
    persons: int
    slots: tuple[Slot, ...]
    variants: tuple[Variant, ...]
    capability_rules: dict
    overrides: dict[str, float]


def positive(value: float, label: str) -> float:
    """Return a finite positive number or reject invalid configuration."""
    if isinstance(value, bool):
        raise ValueError(f"{label} must be a finite positive number")
    number = float(value)
    if not math.isfinite(number) or number <= 0:
        raise ValueError(f"{label} must be a finite positive number")
    return number


def furniture_tokens(furniture: dict) -> set[str]:
    """Collect capabilities from static, transformable and optional serves lists."""
    tokens = set()
    for section in ("static_items", "transformable_items", "optional_items"):
        for item in furniture.get(section, {}).values():
            serves = item["serves"]
            groups = serves.values() if isinstance(serves, dict) else [serves]
            for group in groups:
                tokens.update(group)
    return tokens


def parse_slots(raw: dict) -> tuple[Slot, ...]:
    """Check both 24-hour total and gap-free, non-overlapping clock coverage."""
    slots, pieces = [], []
    for name, interval in raw.items():
        if len(interval) != 2:
            raise ValueError("Each slot must contain two endpoints")
        start, end = map(float, interval)
        if not (0 <= start < 24 and 0 <= end <= 24) or start == end or (start == 0 and end == 24):
            raise ValueError("Slot endpoints must define a positive duration below 24 hours")
        slot = Slot(name, start, end)
        slots.append(slot)
        pieces.extend([(start, 24.), (0., end)] if end < start else [(start, end)])
    cursor = 0.
    for start, end in sorted(p for p in pieces if p[1] > p[0]):
        if not math.isclose(start, cursor, abs_tol=1e-9, rel_tol=0):
            raise ValueError("Schedule has a gap or overlap")
        cursor = end
    if not math.isclose(cursor, 24., abs_tol=1e-9, rel_tol=0) or not math.isclose(sum(s.hours for s in slots), 24.):
        raise ValueError("Schedule must cover exactly 24 hours")
    return tuple(slots)


def parse_households(config: dict, furniture: dict) -> dict[str, Household]:
    """Validate schedules and retain distinct demand occurrences and exact frequencies."""
    slots = parse_slots(config["slots"])
    slot_names = {slot.name for slot in slots}
    tokens = furniture_tokens(furniture)
    rules = config["capability_rules"]
    for need, rule in rules.items():
        if need not in tokens:
            raise ValueError(f"Unknown capability: {need}")
        if rule.get("type") == "capacity":
            if rule.get("attribute") != "storage_units" or rule.get("partial_credit") is not True:
                raise ValueError("Unsupported capacity rule")
        else:
            options = rule.get("satisfied_by", [])
            if not options or any(not option or not set(option) <= tokens for option in options):
                raise ValueError(f"Invalid capability alternatives: {need}")
    result = {}
    for name, spec in config["households"].items():
        persons = spec["persons"]
        if isinstance(persons, bool) or not isinstance(persons, int) or persons < 1:
            raise ValueError("persons must be a positive integer")
        variants = []
        for variant_name, variant in spec["variants"].items():
            frequency = positive(variant["frequency"], "frequency")
            if set(variant["demand"]) != slot_names:
                raise ValueError("Every variant must explicitly list every slot")
            demands = {}
            for slot in slots:
                occurrences = []
                for index, item in enumerate(variant["demand"][slot.name]):
                    need = item["need"]
                    if need not in tokens or need not in rules:
                        raise ValueError(f"Unknown demand: {need}")
                    weight = positive(item.get("weight", 1.), "weight")
                    units = None
                    if rules[need].get("type") == "capacity":
                        units = positive(item["units"], "units")
                    elif "units" in item:
                        raise ValueError("units is only valid for capacity demands")
                    occurrences.append(Demand(f"{variant_name}:{slot.name}:{index}", need, weight, units))
                demands[slot.name] = tuple(occurrences)
            variants.append(Variant(variant_name, frequency, demands))
        if not variants or not math.isclose(sum(v.frequency for v in variants), 1., abs_tol=1e-9, rel_tol=0):
            raise ValueError("Variant frequencies must sum to one")
        overrides = {key: positive(value, key) for key, value in spec.get("overrides", {}).items()}
        household = Household(name, persons, slots, tuple(variants), rules, overrides)
        if any(demanded_hours(household, v.name) <= 0 for v in variants):
            raise ValueError("A variant must have positive demanded hours")
        result[name] = household
    for scope in ("main_households", "ablation_households"):
        if not set(config[scope]) <= result.keys():
            raise ValueError(f"Unknown household in {scope}")
    return result


def demanded_hours(household: Household, variant: str | None = None) -> float:
    """Sum duration × demand weight, preserving duplicates and excluding capacity units.

    With a variant name, return its FCI denominator. Otherwise return the
    frequency-weighted descriptive mean. FCI must later be the weighted mean of
    variant FCI ratios, not the ratio of aggregated served/demanded hours.
    """
    totals = {day.name: sum(slot.hours * sum(d.weight for d in day.demand[slot.name])
                           for slot in household.slots) for day in household.variants}
    if variant is not None:
        return totals[variant]
    return sum(day.frequency * totals[day.name] for day in household.variants)


def schedule_rows(households: dict[str, Household], config: dict, digest: str) -> list[dict]:
    """Build long-form table rows with explicit scope, weights and capacity requirements."""
    import json
    from dataclasses import asdict

    rows = []
    for household in households.values():
        for day in household.variants:
            for slot in household.slots:
                needs = day.demand[slot.name]
                text = "; ".join(f"{d.need} (weight={d.weight:g}" + (f", units={d.units:g}" if d.units is not None else "") + ")" for d in needs) or "none"
                rows.append({"household": household.name, "persons": household.persons,
                             "scope": "main" if household.name in config["main_households"] else "ablation",
                             "variant": day.name, "frequency": day.frequency, "slot": slot.name,
                             "start_hour": slot.start, "end_hour": slot.end, "duration_h": slot.hours,
                             "demands": text, "demands_json": json.dumps([asdict(d) for d in needs], sort_keys=True),
                             "slot_demanded_hours": slot.hours * sum(d.weight for d in needs),
                             "variant_demanded_hours": demanded_hours(household, day.name),
                             "mean_demanded_hours": demanded_hours(household),
                             "overrides_json": json.dumps(household.overrides, sort_keys=True), "config_hash": digest})
    return rows
