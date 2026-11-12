"""Quality objective regression and preservation of reviewed dimensions."""
from pathlib import Path
from types import SimpleNamespace as Box
import sys

from ortools.sat.python import cp_model
from fea.config import load_config

sys.path.insert(0, str(Path("scripts")))
from phase11_kit_design import candidate_grid, kit_configuration
from phase11_kit_solver import quality_objective


def test_quality_uses_minimum_selected_item_weight():
    m = cp_model.CpModel()
    q1, q2, absent, served = [m.NewBoolVar(name) for name in ("q1", "q2", "absent", "served")]
    m.Add(q1 == 1)
    m.Add(q2 == 1)
    m.Add(absent == 0)
    m.Add(served == 1)
    key = ("regular", "day", "demand", 0, 0)
    model = Box(model=m, assignment={key+("one",): q1, key+("two",): q2, key+("abs",): absent},
                instances={name: Box(item=Box(name=name)) for name in ("one", "two", "abs")},
                credit={"demand": (served, 1)}, burden_terms=[], burden=0, window_terms=[],
                primary_upper=1, primary_scale=1)
    demand = Box(id="demand", need="lounge_2", weight=1.)
    household = Box(slots=[Box(name="day", hours=1.)],
                    variants=[Box(name="regular", frequency=1., demand={"day": [demand]})])
    value, scale, _ = quality_objective(model, household, {"one": .85, "two": .7, "abs": .6})
    solver = cp_model.CpSolver()
    assert solver.Solve(m) == cp_model.OPTIMAL
    assert abs(solver.Value(value)/float(scale)-.7) < 1e-9


def test_kit_changes_widths_but_preserves_clearance_and_stowed_depth():
    base = load_config(Path("config/project.yaml"))
    households = ["H1_single_commuter", "H3_couple_one_remote"]
    kits = candidate_grid(base, households, 8)
    assert all(len({tuple(k["dimensions"].values()) for k in values}) == 8 for values in kits.values())
    h = households[0]
    cfg, qualities = kit_configuration(base, h, kits[h][0])
    new = cfg["furniture"]["transformable_items"]["fold_down_desk"]["states"]
    old = base["furniture"]["transformable_items"]["fold_down_desk"]["states"]
    assert new["stowed"]["footprint"][1] == old["stowed"]["footprint"][1]
    assert new["deployed"]["clearance"] == old["deployed"]["clearance"]
    assert new["stowed"]["footprint"][0] == .8 and new["deployed"]["footprint"][1] == .45
    assert qualities["fold_down_desk"] == .7
