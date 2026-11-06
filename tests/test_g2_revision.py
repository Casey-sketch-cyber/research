"""Regression cases for the G2 access and source-geometry review."""
from dataclasses import replace

import numpy as np
import pytest
from shapely.geometry import GeometryCollection, box

from fea.geometry.raster import Raster, gap_fill, rasterize
from fea.solve.reachability import walking_masks
from fea.validate import _reachable, validate_layout
from test_candidates import empty_room
from test_metrics_validator import fixture


def corridor(cells):
    labels = np.zeros((45, 60), np.uint8)
    labels[15:15+cells, 15:55] = 1
    portal = np.zeros_like(labels, bool)
    portal[15:15+cells, 2:15] = True
    empty = np.zeros_like(portal)
    return Raster(labels, .1, (0., 0.), empty, empty, empty, portal, [], GeometryCollection())


@pytest.mark.parametrize("width,cells,expected", [(.6,6,True),(.6,5,False),(.9,9,True),(.9,8,False)])
@pytest.mark.parametrize("transpose", [False,True])
def test_exact_corridor_width(width, cells, expected, transpose):
    grid = corridor(cells)
    if transpose:
        grid = replace(grid, labels=grid.labels.T, entrance_extension=grid.entrance_extension.T)
    occupied = np.zeros_like(grid.labels, bool)
    solver = walking_masks(grid, occupied, width)[0]
    validator = _reachable(grid, occupied, width)
    assert np.array_equal(solver, validator)
    goal = (50, 15) if transpose else (15, 50)
    assert bool(validator[goal]) == expected


@pytest.mark.parametrize("width,cells", [(.6,6),(.9,9)])
def test_exact_bed_side_strip_is_reached(width, cells):
    # Bed long side lies along a corridor, with a wall on the other side.
    grid = corridor(cells)
    labels = grid.labels.copy()
    labels[15+cells:15+cells+9, 25:45] = 1
    grid = replace(grid, labels=labels)
    occupied = np.zeros_like(labels, bool)
    occupied[15+cells:15+cells+9,25:45] = True
    strip = np.zeros_like(labels, bool)
    strip[15:15+cells,25:45] = True
    assert np.any(_reachable(grid, occupied, width) & strip)
    assert np.any(walking_masks(grid, occupied, width)[0] & strip)


def test_independent_access_agrees_on_irregular_obstacles():
    rng = np.random.default_rng(18)
    grid = corridor(20)
    for width in (.6, .9):
        for _ in range(10):
            occupied = np.zeros_like(grid.labels, bool)
            for x, y in rng.integers([20,15], [50,30], size=(3,2)):
                occupied[y:y+4,x:x+4] = True
            assert np.array_equal(walking_masks(grid, occupied, width)[0], _reachable(grid, occupied, width))


def test_gap_repair_never_crosses_wall_and_does_not_change_nia():
    unit = empty_room(4,4)
    spaces = box(0,0,1.95,4).union(box(2.05,0,4,4))
    unit = replace(unit, classes={**unit.classes, "furnishable": spaces})
    area = unit.interior.area
    assert gap_fill(unit).area == pytest.approx(.4)
    assert unit.interior.area == area
    wall = box(1.95,0,2.05,4)
    unit = replace(unit, walls=unit.walls.union(wall))
    assert gap_fill(unit).area < 1e-8
    assert gap_fill(replace(unit, walls=unit.walls), .05).area < 1e-8


def test_kitchen_target_walkable_but_fixture_blocked():
    unit = empty_room(4,4)
    kitchen = box(2,0,4,4)
    fixture_body = box(3.4,0,4,1)
    unit = replace(unit, classes={**unit.classes,"furnishable":box(0,0,2,4),
        "walkable_only":kitchen.difference(fixture_body),"fixed_service":fixture_body},
        meta={"kitchen_region_geometry":kitchen.difference(fixture_body).wkt})
    grid = rasterize(unit)
    assert grid.kitchen.any()
    assert np.all(grid.labels[grid.kitchen] != 1)
    assert len(grid.service_targets) == 1


def test_anchor_lattice_uses_local_metres_not_padding():
    from fea.furniture.library import library
    from fea.furniture.candidates import generate_candidates
    from fea.config import load_config
    from shapely.geometry import LineString
    unit=empty_room();door=LineString([(0,0),(1,0)])
    unit=replace(unit,doors=[door],entrance=door,walls=unit.walls.difference(door))
    grid=rasterize(unit)
    item=library(load_config('config/project.yaml')['furniture'])['shelving']
    poses=generate_candidates(grid,{'shelving':item},anchor_stride_m=.2)['shelving']
    assert len(poses)>0
    for x,y,_ in poses:
        assert (grid.origin[0]+x*.1)/.2 == pytest.approx(round((grid.origin[0]+x*.1)/.2))
        assert (grid.origin[1]+y*.1)/.2 == pytest.approx(round((grid.origin[1]+y*.1)/.2))


@pytest.mark.parametrize('blocker_x,target_x,expected',[(3,8,False),(4,8,False),(0,8,True),(3,7,True)])
def test_geometric_cut_rules_out_a_region_but_retains_alternate_route_or_target(blocker_x,target_x,expected):
    from types import SimpleNamespace
    from ortools.sat.python import cp_model
    from fea.solve.cpsat import Model
    model=Model.__new__(Model);m=model.model=cp_model.CpModel()
    def instance(name):
        return SimpleNamespace(present=m.NewBoolVar(name+'p'),x=m.NewIntVar(0,10,name+'x'),
            y=m.NewIntVar(5,5,name+'y'),orientation=m.NewIntVar(0,0,name+'o'),states={('v','s'):0})
    blocker,target=instance('b'),instance('t')
    model.instances={'b':blocker,'t':target}
    assignment=m.NewBoolVar('assigned')
    model.assignment={('v','s','d',0,0,'t'):assignment}
    model.rectangle=lambda inst,key,kind:(m.NewOptionalFixedSizeIntervalVar(inst.x,2,inst.present,'ix'),
                                        m.NewOptionalFixedSizeIntervalVar(inst.y,2,inst.present,'iy'))
    values={blocker.x.Index():4,target.x.Index():8,target.y.Index():5,assignment.Index():1}
    before=SimpleNamespace(Value=lambda variable:values.get(variable.Index(),0))
    model.cut([dict(variant='v',slot='s',demand_id='d',instance_id='t',
        blockers=['b'],barrier_rectangles={'b':[4,5,5,6]})],before)
    for inst in (blocker,target):m.Add(inst.present==1)
    m.Add(assignment==1);m.Add(blocker.x==blocker_x);m.Add(target.x==target_x)
    solver=cp_model.CpSolver();solver.parameters.num_search_workers=1
    status=solver.Solve(m)
    assert (status in (cp_model.FEASIBLE,cp_model.OPTIMAL)) == expected


def test_zero_thickness_internal_separator_stays_blocked():
    from shapely.geometry import LineString
    unit=empty_room(4,4)
    unit=replace(unit,walls=unit.walls.union(LineString([(2,0),(2,4)])))
    grid=rasterize(unit)
    x=round((2-grid.origin[0])/.1)
    ys=slice(round((0-grid.origin[1])/.1),round((4-grid.origin[1])/.1))
    assert not grid.walkable[ys,x-1:x+1].any()


def test_kitchen_reclassification_preserves_extent_outside_generic_inner_polygon():
    from fea.data.d2_resplan import from_plan
    kitchen=box(3.8,1,4.1,2)
    unit=from_plan(dict(id=1,area=16,inner=box(0,0,4,4),kitchen=kitchen,
        bathroom=box(0,3,1,4),living=box(0,0,3,3)))
    assert unit.classes['walkable_only'].intersection(kitchen).area == pytest.approx(.3)
    assert unit.interior.area == pytest.approx(16.1)
    assert unit.meta['rooms_outside_source_outline_m2'] == pytest.approx(.1)


def test_kitchen_fixture_near_door_does_not_create_a_second_kitchen_target():
    from shapely.geometry import LineString
    from fea.geometry.raster import fixed_service_doors
    unit=empty_room(4,4);bath=box(2,3,4,4);fixture=box(3.4,0,4,1)
    kitchen_door=LineString([(3.4,0),(3.4,1)])
    bath_door=LineString([(2.1,3),(3,3)])
    unit=replace(unit,doors=[kitchen_door,bath_door],classes={**unit.classes,
        'fixed_service':bath.union(fixture),'furnishable':box(0,0,2,4),
        'walkable_only':box(2,0,4,3).difference(fixture)},
        meta={'service_room_geometry':bath.wkt,'kitchen_region_geometry':box(2,0,3.4,3).wkt})
    doors=fixed_service_doors(unit)
    assert len(doors)==1 and doors[0].equals(bath_door)
    assert len(rasterize(unit).service_targets)==2
