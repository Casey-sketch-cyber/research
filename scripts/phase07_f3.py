"""F3 either-side variants with shared inventory and explicit warm-start remapping."""
from collections import Counter
from copy import deepcopy
import itertools
from pathlib import Path
import yaml
from fea.config import config_hash
from fea.validate import validate_layout

HOUSEHOLDS=["H3_couple_one_remote"]


def variant_config(base: dict) -> dict:
    """Create disjoint left/right aliases while preserving total family inventory."""
    spec=yaml.safe_load(Path("config/f3_overrides.yaml").read_text())
    if spec["sides"]!=["left","right"] or spec["access_width_m"]!=.6:raise ValueError("F3 must use the reviewed two 0.60 m side alternatives")
    result=deepcopy(base);furniture=result["furniture"]
    if furniture.get("instance_groups"):raise ValueError("F3 expects the unmodified main inventory")
    furniture["instance_groups"]={}
    for family,state in spec["families"].items():
        section="static_items" if state=="static" else "transformable_items"
        original=furniture[section].pop(family);limit=furniture["max_instances"].get(family,furniture["max_instances"]["default"])
        aliases=[]
        for side in spec["sides"]:
            name=family+"__"+side;aliases.append(name);value=deepcopy(original)
            target=value if state=="static" else value["states"][state]
            target["clearance"]={side:spec["access_width_m"]}
            furniture[section][name]=value;furniture["max_instances"][name]=limit
        furniture["instance_groups"][family]=dict(members=aliases,max_instances=limit)
    result["solver"].update(spec["solver"]);result["raster"]["anchor_stride_m"]=spec["anchor_stride_m"]
    return result


def mapped_layouts(layout: dict, variant: dict):
    """Enumerate physical mirror choices, updating every assignment reference."""
    groups=variant["furniture"]["instance_groups"]
    affected=[item for item in layout["items"] if item["type"] in groups]
    choices=[groups[item["type"]]["members"] for item in affected]
    for combination in itertools.product(*choices):
        mapped=deepcopy(layout);chosen={item["instance_id"]:alias for item,alias in zip(affected,combination)}
        ids={};counts=Counter()
        for item in mapped["items"]:
            old=item["instance_id"]
            if old in chosen:
                alias=chosen[old];counts[alias]+=1;item["type"]=alias;item["instance_id"]=alias+"#"+str(counts[alias]);ids[old]=item["instance_id"]
        for slots in mapped.get("service",{}).values():
            for entries in slots.values():
                for entry in entries:entry["by"]=[ids.get(identity,identity) for identity in entry["by"]]
        mapped["config_hash"]=config_hash(variant)
        yield mapped


def mapped_incumbent(layout: dict, grid, variant: dict, household) -> tuple:
    """Choose the best independently valid mapping; retain losses explicitly."""
    best=None;valid=0;attempted=0
    for mapped in mapped_layouts(layout,variant):
        attempted+=1;checked=validate_layout(mapped,grid,variant,household)
        if not checked["pass"]:continue
        valid+=1;mapped.update({key:checked[key] for key in ["fci","fci_by_variant","tb","served_hours","demanded_hours"]})
        mapped["validator"]=checked
        if best is None or (mapped["fci"],-mapped["tb"])>(best["fci"],-best["tb"]):best=mapped
    return best,dict(mirror_combinations=attempted,valid_mappings=valid,best_mapped_fci=None if best is None else best["fci"])
