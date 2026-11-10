"""Mirrored access must add a side choice without doubling family inventory."""
from copy import deepcopy
from pathlib import Path
import sys
import numpy as np
import pytest
from ortools.sat.python import cp_model
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from phase07_f3 import variant_config,mapped_layouts
from fea.config import load_config
from fea.furniture.library import library
from fea.furniture.candidates import generate_candidates
from fea.geometry.raster import rasterize
from fea.solve.cpsat import Model
from fea.validate import validate_layout
from test_candidates import empty_room
from test_metrics_validator import fixture


def test_mirrors_preserve_main_defaults_and_share_inventory():
    main=load_config("config/project.yaml");before=deepcopy(main);variant=variant_config(main)
    assert main==before
    assert variant["furniture"]["max_instances"]["single_bed"]==2
    for family,group in variant["furniture"]["instance_groups"].items():
        section="static_items" if family=="double_bed" else "transformable_items"
        assert family not in variant["furniture"][section]
        assert group["max_instances"]==main["furniture"]["max_instances"].get(family,1)
        for side in ["left","right"]:
            actual=deepcopy(variant["furniture"][section][family+"__"+side]);original=main["furniture"][section][family]
            active=actual if section=="static_items" else actual["states"]["deployed"]
            assert active["clearance"]=={side:.6}
            active["clearance"]=original["clearance"] if section=="static_items" else original["states"]["deployed"]["clearance"]
            assert actual==original


def test_both_mirrors_have_necessary_corner_candidates():
    variant=variant_config(load_config("config/project.yaml"));grid=rasterize(empty_room());items=library(variant["furniture"],"S0")
    names=["double_bed__left","double_bed__right"]
    poses=generate_candidates(grid,{name:items[name] for name in names})
    x0,y0=[int(round(-v/grid.resolution)) for v in grid.origin]
    left_corner=np.array([x0,y0,0]);right_corner=np.array([x0+16,y0,0])
    assert np.any(np.all(poses[names[1]]==left_corner,axis=1))
    assert not np.any(np.all(poses[names[0]]==left_corner,axis=1))
    assert np.any(np.all(poses[names[0]]==right_corner,axis=1))
    assert not np.any(np.all(poses[names[1]]==right_corner,axis=1))


def test_solver_and_independent_validator_enforce_shared_limit():
    config,h,grid,layout=fixture();config=deepcopy(config)
    config["furniture"]["static_items"]={name:config["furniture"]["static_items"][name] for name in ["single_bed","armchair"]}
    config["furniture"]["transformable_items"]={}
    chair={**deepcopy(layout["items"][0]),"type":"armchair","instance_id":"armchair#1","x":.5,"y":1.}
    layout["items"].append(chair)
    assert validate_layout(layout,grid,config,h)["pass"]
    items=library(config["furniture"],"S0");candidates=generate_candidates(grid,items)
    for grouped,expected in [(False,cp_model.OPTIMAL),(True,cp_model.INFEASIBLE)]:
        if grouped:config["furniture"]["instance_groups"]={"test_family":{"members":["single_bed","armchair"],"max_instances":1}}
        model=Model(grid,h,items,candidates,"S0",config)
        for identity in ["single_bed#1","armchair#1"]:model.model.Add(model.instances[identity].present==1)
        model.model.ClearObjective();solver=cp_model.CpSolver();solver.parameters.max_time_in_seconds=5;solver.parameters.num_search_workers=1
        assert solver.Solve(model.model)==expected
    checked=validate_layout(layout,grid,config,h)
    assert not checked["pass"] and "family_instance_limit:test_family" in checked["violations"]


def test_warm_start_remaps_ids_and_keeps_side_fixed_across_slots():
    config=variant_config(load_config("config/project.yaml"))
    original=dict(items=[dict(type="double_bed",instance_id="double_bed#1",states={"normal":{"night":"static","morning":"static"}})],
        service={"normal":{"night":[dict(by=["double_bed#1"])],"morning":[dict(by=[])]}})
    before=deepcopy(original);mapped=list(mapped_layouts(original,config))
    assert original==before and len(mapped)==2
    for value in mapped:
        identity=value["items"][0]["instance_id"]
        assert value["service"]["normal"]["night"][0]["by"]==[identity]
        assert value["items"][0]["states"]==original["items"][0]["states"]
