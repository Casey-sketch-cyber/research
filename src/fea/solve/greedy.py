"""Descending-footprint, first-feasible wall-adjacent greedy baseline."""
from copy import deepcopy
import itertools
import time

import numpy as np
from scipy import ndimage

from fea.furniture.library import rectangles
from fea.households import demanded_hours
from fea.validate import validate_layout
from .reachability import state_masks, check_connectivity


def allocate(layout, items, household):
    """Choose distinct capable instances per simultaneous demand by enumeration."""
    service = {}
    for variant in household.variants:
        service[variant.name] = {}
        for slot in household.slots:
            tokens = {i["instance_id"]: next(s.serves for s in items[i["type"]].states
                      if s.name == i["states"][variant.name][slot.name]) for i in layout["items"]}
            options = []
            demands = variant.demand[slot.name]
            for d in demands:
                choices = [((), 0.)]
                if d.need == "storage":
                    keys = [i for i,t in tokens.items() if "storage" in t]
                    for n in range(1,len(keys)+1):
                        for group in itertools.combinations(keys,n):
                            capacity = sum(items[i.rsplit("#",1)[0]].storage_units for i in group)
                            choices.append((group, d.weight*min(1.,capacity/d.units)))
                else:
                    for rule in household.capability_rules[d.need].get("satisfied_by", [["storage"]]):
                        for group in itertools.product(*[[i for i,t in tokens.items() if token in t] for token in rule]):
                            if len(set(group)) == len(group): choices.append((group,d.weight))
                options.append(choices)
            best, score = [()]*len(demands), -1
            for combination in itertools.product(*options):
                used = [i for group,_ in combination for i in group]
                value = sum(v for _,v in combination)
                if len(used)==len(set(used)) and value > score:
                    best, score = [group for group,_ in combination], value
            service[variant.name][slot.name] = [dict(demand_id=d.id,need=d.need,by=list(g)) for d,g in zip(demands,best)]
    layout["service"] = service
    return layout


def _patterns(item, household, strategy):
    """Constant states and, for S2, one household-demand-driven state schedule."""
    patterns = [{v.name: {s.name: state.name for s in household.slots}
                 for v in household.variants} for state in item.states]
    if len(item.states) > 1 and strategy == "S2":
        patterns.append({v.name: {slot.name: max(item.states, key=lambda state: sum(
            d.weight for d in v.demand[slot.name] if any(all(t in state.serves for t in rule)
            for rule in household.capability_rules[d.need].get("satisfied_by", [["storage"]])))).name
            for slot in household.slots} for v in household.variants})
    return patterns


def _pattern_value(item, pattern, household, credits=None):
    """Rank one-item service potential; no room coordinates or outcomes are used."""
    states = {s.name: s for s in item.states}
    total = 0.
    for variant in household.variants:
        served = 0.
        for slot in household.slots:
            tokens = states[pattern[variant.name][slot.name]].serves
            values = []
            for demand in variant.demand[slot.name]:
                if demand.need == "storage":
                    value = min(1., item.storage_units/demand.units) if "storage" in tokens else 0.
                else:
                    # One instance cannot satisfy a two-distinct-instance rule.
                    value = float(any(len(rule) == 1 and rule[0] in tokens
                                      for rule in household.capability_rules[demand.need]["satisfied_by"]))
                values.append(max(0., value-(credits or {}).get(demand.id, 0.))*demand.weight)
            served += slot.hours*max(values, default=0.)
        total += variant.frequency*served/demanded_hours(household, variant.name)
    return total


def _footprint_hours(item, pattern, household):
    """Break equal-service initialization ties by space occupied over the day."""
    areas = {s.name: s.footprint[0]*s.footprint[1] for s in item.states}
    return sum(v.frequency*slot.hours*areas[pattern[v.name][slot.name]]
               for v in household.variants for slot in household.slots)


def greedy_layout(empty, grid, items, candidates, household, config, deadline, policy="footprint"):
    """Place each useful item at its first valid wall pose, largest footprints first.

    The footprint policy preserves the specified baseline. The service policy
    prioritizes one-item household service and tests its best schedule first.
    Every accepted addition improves independently validated FCI.
    """
    started = time.perf_counter()
    first_positive = None
    layout = deepcopy(empty)
    layout.update(validate_layout(layout,grid,config,household))
    width = household.overrides.get("walking_width",config["furniture"]["meta"]["walking_width"])
    adjacent = ndimage.binary_dilation(grid.wall)
    patterns_by_item = {item.name: _patterns(item, household, empty["strategy"]) for item in items.values()}
    if policy == "footprint":
        ordered = sorted(items.values(),key=lambda item:(-max(s.footprint[0]*s.footprint[1] for s in item.states),item.name))
    elif policy in ("service", "service_density"):
        for item in items.values():
            patterns_by_item[item.name].sort(key=lambda p: (-_pattern_value(item, p, household),
                                                           _footprint_hours(item, p, household)))
        ordered = sorted(items.values(), key=lambda item: (
            -_pattern_value(item, patterns_by_item[item.name][0], household), -len(item.states),
            max(s.footprint[0]*s.footprint[1] for s in item.states), item.name))
    else:
        raise ValueError("Unknown greedy policy")
    required_tokens = {t for v in household.variants for ds in v.demand.values() for d in ds
                       for rule in household.capability_rules[d.need].get("satisfied_by", [["storage"]]) for t in rule}
    attempts = 0
    def next_items():
        remaining_items = list(ordered)
        while remaining_items:
            if policy == "service_density":
                remaining_items.sort(key=lambda item: (
                    -max(_pattern_value(item, p, household, layout["credits"])
                         for p in patterns_by_item[item.name]) /
                    max(s.footprint[0]*s.footprint[1] for s in item.states), item.name))
            yield remaining_items.pop(0)
    for item in next_items():
        if not required_tokens.intersection(t for state in item.states for t in state.serves): continue
        if policy == "service_density" and not any(_pattern_value(item, p, household, layout["credits"]) > 1e-9
                                                    for p in patterns_by_item[item.name]): continue
        for number in range(item.max_instances):
            if time.perf_counter() >= deadline: break
            identity = item.name+"#"+str(number+1)
            patterns = patterns_by_item[item.name]
            if policy == "service":
                # Test the promised schedule across poses before falling back to
                # weaker furniture choices. The footprint arm retains partial
                # schedules, so this initializer does not restrict CP's domain.
                patterns = patterns[:1]
            accepted = False
            for x,y,angle in candidates[item.name]:
                body,_,_ = rectangles(item.states[-1],grid.resolution,int(angle))
                dx,dy,w,h=body
                if not adjacent[y+dy:y+dy+h,x+dx:x+dx+w].any(): continue
                for states in patterns:
                    if time.perf_counter() >= deadline: break
                    trial = deepcopy(layout)
                    trial["items"].append(dict(instance_id=identity,type=item.name,x=round(grid.origin[0]+int(x)*grid.resolution,9),
                        y=round(grid.origin[1]+int(y)*grid.resolution,9),orientation_deg=int(angle),states=states))
                    collision = False
                    seen = set()
                    for v in household.variants:
                        for slot in household.slots:
                            key=tuple(i["states"][v.name][slot.name] for i in trial["items"])
                            if key in seen: continue
                            seen.add(key)
                            masks=state_masks(trial,grid,items,v.name,slot.name)
                            newbody,newclear=masks.pop(identity)
                            if any(np.any(newbody & (b|c)) or np.any(newclear & b) for b,c in masks.values()): collision=True;break
                        if collision: break
                    if collision: continue
                    allocate(trial,items,household)
                    attempts += 1
                    checked=validate_layout(trial,grid,config,household)
                    preserves_service = policy == "footprint" or all(
                        checked["credits"].get(key, 0.) >= value-1e-9
                        for key, value in layout["credits"].items())
                    promised_gain = _pattern_value(item, states, household, layout["credits"])
                    achieves_schedule = policy != "service" or checked["fci"]-layout["fci"] >= promised_gain-1e-9
                    if checked["pass"] and checked["fci"]>layout["fci"]+1e-9 and preserves_service and achieves_schedule:
                        trial.update(checked)
                        if first_positive is None and checked["fci"]>0: first_positive=time.perf_counter()-started
                        layout=trial;accepted=True;break
                if accepted or time.perf_counter()>=deadline: break
            if not accepted: break
    layout["greedy"] = {"validated_trials":attempts,"first_positive_s":first_positive,"fci":layout["fci"],
                        "algorithm": policy+" / first improving feasible wall-adjacent pose"}
    return layout


def greedy_warm_start(empty, grid, items, candidates, household, config, deadline):
    """Try two service rankings and the unchanged footprint baseline in one budget.

    No known-answer pose, future strategy result, or held-out target is supplied.
    The independent validator selects the best service score, then burden.
    """
    started = time.perf_counter()
    remaining = max(0., deadline-started)
    results, first_positive = [], None
    for policy, stop in (("service_density", started+remaining/3),
                         ("service", started+remaining*2/3), ("footprint", deadline)):
        offset = time.perf_counter()-started
        layout = greedy_layout(empty, grid, items, candidates, household, config, stop, policy)
        info = layout["greedy"]
        if info["first_positive_s"] is not None and first_positive is None:
            first_positive = offset+info["first_positive_s"]
        results.append(layout)
        if layout["fci"] >= 1.-1e-9 and layout["tb"] == 0:
            break
    best = max(results, key=lambda v: (v["fci"], -v["tb"]))
    best["greedy"] = {"algorithm": "service-density/service/footprint portfolio", "fci": best["fci"],
        "first_positive_s": first_positive,
        "validated_trials": sum(v["greedy"]["validated_trials"] for v in results),
        "arms": [deepcopy(v["greedy"]) for v in results]}
    return best
