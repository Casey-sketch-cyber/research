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


def greedy_layout(empty, grid, items, candidates, household, config, deadline):
    """Place each useful item at its first valid wall pose, largest footprints first.

    Constant states are attempted before a demand-priority per-slot state pattern
    (S2 only). Every accepted addition improves independently validated FCI.
    """
    started = time.perf_counter()
    first_positive = None
    layout = deepcopy(empty)
    layout.update(validate_layout(layout,grid,config,household))
    width = household.overrides.get("walking_width",config["furniture"]["meta"]["walking_width"])
    adjacent = ndimage.binary_dilation(grid.wall)
    ordered = sorted(items.values(),key=lambda item:(-max(s.footprint[0]*s.footprint[1] for s in item.states),item.name))
    required_tokens = {t for v in household.variants for ds in v.demand.values() for d in ds
                       for rule in household.capability_rules[d.need].get("satisfied_by", [["storage"]]) for t in rule}
    attempts = 0
    for item in ordered:
        if not required_tokens.intersection(t for state in item.states for t in state.serves): continue
        for number in range(item.max_instances):
            if time.perf_counter() >= deadline: break
            identity = item.name+"#"+str(number+1)
            patterns = [{v.name:{s.name:state.name for s in household.slots} for v in household.variants} for state in item.states]
            if len(item.states)>1 and empty["strategy"]=="S2":
                patterns.append({v.name:{slot.name:max(item.states,key=lambda state:sum(d.weight for d in v.demand[slot.name]
                    if any(all(t in state.serves for t in rule) for rule in household.capability_rules[d.need].get("satisfied_by", [["storage"]])))) .name
                    for slot in household.slots} for v in household.variants})
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
                    if checked["pass"] and checked["fci"]>layout["fci"]+1e-9:
                        trial.update({k:checked[k] for k in ("fci","fci_by_variant","tb","served_hours","demanded_hours")})
                        if first_positive is None and checked["fci"]>0: first_positive=time.perf_counter()-started
                        layout=trial;accepted=True;break
                if accepted or time.perf_counter()>=deadline: break
            if not accepted: break
    layout["greedy"] = {"validated_trials":attempts,"first_positive_s":first_positive,"fci":layout["fci"],"algorithm":"descending footprint / first feasible wall-adjacent pose"}
    return layout
