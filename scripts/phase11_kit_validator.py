"""Independent quality scoring of validated scheduled service assignments."""
from fea.metrics import fci
from fea.validate import validate_layout


def quality_metrics(layout, grid, config, household, qualities):
    """Apply minimum reachable item quality to each fulfilled non-storage demand."""
    raw = validate_layout(layout, grid, config, household)
    if not raw["pass"]:
        return {**raw, "fciq": 0., "quality_credits": {}}
    item_type = {item["instance_id"]: item["type"] for item in layout["items"]}
    inaccessible = set(raw["unreachable_items"])
    credits = {}
    for variant in household.variants:
        for slot in household.slots:
            by_id = {entry["demand_id"]: entry["by"] for entry in
                     layout.get("service", {}).get(variant.name, {}).get(slot.name, [])}
            for demand in variant.demand[slot.name]:
                credit = raw["credits"].get(demand.id, 0.)
                if credit > 0 and demand.need != "storage":
                    ids = [i for i in by_id.get(demand.id, [])
                           if f"{variant.name}:{slot.name}:{i}" not in inaccessible]
                    if not ids:
                        raise ValueError("Validated service has no reachable item")
                    credit *= min(qualities.get(item_type[i], 1.) for i in ids)
                credits[demand.id] = credit
    score = fci(household, credits)["fci"]
    if not 0 <= score <= raw["fci"]+1e-8:
        raise ValueError("FCIq exceeds its independently validated service score")
    return {**raw, "fciq": score, "quality_credits": credits}
