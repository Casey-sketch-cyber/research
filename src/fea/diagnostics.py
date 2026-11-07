"""Hand-specified mechanism fixtures, separate from the population of dwellings.

The deliberately small fixed-service blocks are algorithmic test obstacles, not
claims about habitable bathroom dimensions. They never enter Exp. A or Exp. K.
Furniture, household capabilities and clearance defaults remain unchanged.
"""
from shapely.geometry import LineString, box

from fea.geometry.unit import Unit


def mechanism_shell(area: int) -> Unit:
    """Create one of three pre-specified 9/11/13 m² diagnostic rectangles."""
    if area not in (9, 11, 13):
        raise ValueError("Diagnostic areas are fixed before solver comparisons")
    width, depth = area / 2.5, 2.5
    room = box(0, 0, width, depth)
    pod = box(width-.8, 1.7, width, depth)
    kitchen = box(width-.4, 0, width, .6)
    entrance = LineString([(width, .7), (width, 1.6)])
    pod_door = LineString([(width-.7, 1.7), (width-.1, 1.7)])
    fixed = pod.union(kitchen)
    walls = room.boundary.union(pod.boundary).difference(entrance).difference(pod_door)
    return Unit(f"mechanism:{area}", "diagnostic", "mechanism",
                {"furnishable": room.difference(fixed), "fixed_service": fixed},
                walls, [entrance, pod_door], [], entrance, float(area), 1,
                {"toilet_geometry": pod.wkt, "kitchen_geometry": kitchen.wkt,
                 "diagnostic_only": True, "population_eligible": False,
                 "service_blocks_note": "Synthetic obstacles; not habitable minimum dimensions"})


def mechanism_witness(area: int, household) -> dict:
    """Hand-write poses, states and service claims, without invoking a solver.

    The table body occupies y=1.7..2.5 by day, overlapping the bed's night
    footprint y=0..2.2. At night the table occupies only y=2.3..2.5. H1 cannot
    claim sleep_1 from a sleep_2 item under the unchanged capability rules.
    Unserved storage and guest dining remain explicit in the lower bound.
    """
    layout = {"strategy": "S2", "unit_key": f"mechanism:{area}",
              "resolution_m": .1, "items": [], "service": {}}
    poses = [("wall_bed_over_sofa", .6, 0., 0), ("drop_leaf_table", 1.7, 2.5, 180)]
    if area >= 11:
        poses.append(("wardrobe" if area == 13 else "shelving", 2.7, 0., 0))
    for name, x, y, angle in poses:
        states = {}
        for variant in household.variants:
            states[variant.name] = {}
            for slot in household.slots:
                if name in ("wardrobe", "shelving"):
                    state = "static"
                else:
                    state = "deployed" if (slot.name == "night") == (name == "wall_bed_over_sofa") else "stowed"
                states[variant.name][slot.name] = state
        layout["items"].append(dict(instance_id=name+"#1", type=name, x=x, y=y,
                                    orientation_deg=angle, states=states))
    for variant in household.variants:
        layout["service"][variant.name] = {}
        for slot in household.slots:
            entries = []
            for demand in variant.demand[slot.name]:
                by = []
                if demand.need == "sleep_2" and slot.name == "night":
                    by = ["wall_bed_over_sofa#1"]
                elif demand.need in ("lounge_1", "lounge_2") and slot.name != "night":
                    by = ["wall_bed_over_sofa#1"]
                elif demand.need in ("dine_2", "work_1") and slot.name != "night":
                    by = ["drop_leaf_table#1"]
                elif demand.need == "storage" and area >= 11:
                    by = [("wardrobe" if area == 13 else "shelving")+"#1"]
                entries.append(dict(demand_id=demand.id, need=demand.need, by=by))
            layout["service"][variant.name][slot.name] = entries
    return layout
