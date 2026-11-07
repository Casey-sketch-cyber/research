"""Known feasible time-sharing layouts and deliberate concurrent-state failures."""
from copy import deepcopy

import pytest

from fea.config import load_config
from fea.diagnostics import mechanism_shell, mechanism_witness
from fea.geometry.raster import rasterize
from fea.households import parse_households
from fea.validate import validate_layout


@pytest.mark.parametrize("area", [9, 11, 13])
@pytest.mark.parametrize("prefix", ["H1", "H3"])
def test_hand_written_time_sharing_witness(area, prefix):
    config = load_config("config/project.yaml")
    household = next(h for name, h in parse_households(config["households"], config["furniture"]).items()
                     if name.startswith(prefix))
    unit = mechanism_shell(area)
    grid = rasterize(unit)
    layout = mechanism_witness(area, household)
    checked = validate_layout(layout, grid, config, household)
    assert checked["pass"], checked["violations"]
    assert checked["fci"] > 0 and checked["tb"] > 0
    assert abs(unit.interior.area-area) < 1e-8
    assert unit.meta["population_eligible"] is False
    # These are independently hand-counted hours, not solver output.
    if prefix == "H3":
        expected = (24 + {9: 0, 11: .5, 13: 1}[area] - .143)/26
        assert checked["fci"] == pytest.approx(expected)
    else:
        expected = (8.9 + {9: 0, 11: 1, 13: 2}[area])/18.9
        assert checked["fci"] == pytest.approx(expected)
    constant = deepcopy(layout)
    constant["strategy"] = "S1"
    assert not validate_layout(constant, grid, config, household)["pass"]
    simultaneous = deepcopy(layout)
    for variant in household.variants:
        simultaneous["items"][1]["states"][variant.name]["night"] = "deployed"
    bad = validate_layout(simultaneous, grid, config, household)
    assert not bad["pass"] and any("overlap" in v for v in bad["violations"])


@pytest.mark.parametrize("area", [9, 11, 13])
@pytest.mark.parametrize("prefix", ["H1", "H3"])
def test_constraint_model_can_represent_known_witness(area, prefix):
    """Separate model expressiveness from the unconstrained search diagnostic."""
    from ortools.sat.python import cp_model
    from fea.furniture.candidates import generate_candidates
    from fea.furniture.library import library
    from fea.solve.cpsat import Model

    config = load_config("config/project.yaml")
    household = next(h for name, h in parse_households(config["households"], config["furniture"]).items()
                     if name.startswith(prefix))
    unit = mechanism_shell(area)
    grid = rasterize(unit)
    witness = mechanism_witness(area, household)
    lower = validate_layout(witness, grid, config, household)["fci"]
    items = library(config["furniture"])
    candidates = generate_candidates(grid, items)
    model = Model(grid, household, items, candidates, "S2", config)
    placed = {i["instance_id"]: i for i in witness["items"]}
    for key, instance in model.instances.items():
        item = placed.get(key)
        model.model.Add(instance.present == int(item is not None))
        if item is None:
            continue
        model.model.Add(instance.x == round((item["x"]-grid.origin[0])/grid.resolution))
        model.model.Add(instance.y == round((item["y"]-grid.origin[1])/grid.resolution))
        model.model.Add(instance.orientation == item["orientation_deg"]//90)
        for (variant, slot), variable in instance.states.items():
            state = [s.name for s in instance.item.states].index(item["states"][variant][slot])
            model.model.Add(variable == state)
    model.model.Add(model.primary >= round(lower*float(model.primary_scale)))
    solver = cp_model.CpSolver()
    solver.parameters.num_search_workers = 1
    solver.parameters.max_time_in_seconds = 10
    status = solver.Solve(model.model)
    assert status in (cp_model.OPTIMAL, cp_model.FEASIBLE)
    layout = model.extract(solver, unit, "S2", "diagnostic")
    checked = validate_layout(layout, grid, config, household)
    assert checked["pass"] and checked["fci"] >= lower-1e-9


def test_service_schedule_tie_prefers_smaller_idle_footprint():
    """Equal service must not automatically select a permanently deployed table."""
    from fea.furniture.library import library
    from fea.solve.greedy import _patterns, _pattern_value, _footprint_hours
    config = load_config("config/project.yaml")
    h = parse_households(config["households"], config["furniture"])["H3_couple_one_remote"]
    item = library(config["furniture"])["drop_leaf_table"]
    patterns = _patterns(item, h, "S2")
    best = min(patterns, key=lambda p: (-_pattern_value(item, p, h), _footprint_hours(item, p, h)))
    assert best["normal"]["night"] == "stowed"
    assert best["normal"]["day"] == "deployed"


def test_full_witness_hint_is_feasible_without_changing_the_search_domain():
    from ortools.sat.python import cp_model
    from fea.furniture.candidates import generate_candidates
    from fea.furniture.library import library
    from fea.solve.cpsat import Model
    config = load_config("config/project.yaml")
    h = parse_households(config["households"], config["furniture"])["H3_couple_one_remote"]
    unit = mechanism_shell(13)
    grid = rasterize(unit)
    items = library(config["furniture"])
    model = Model(grid, h, items, generate_candidates(grid, items), "S2", config)
    witness = mechanism_witness(13, h)
    witness.update(validate_layout(witness, grid, config, h))
    variables_before = len(model.model.Proto().variables)
    model.warm_start(witness)
    assert len(model.model.Proto().variables) == variables_before
    assert not model.model.Validate()
    solver = cp_model.CpSolver()
    solver.parameters.num_search_workers = 1
    solver.parameters.max_time_in_seconds = 10
    # Diagnostic only: test every supplied hint together for consistency.
    solver.parameters.fix_variables_to_their_hinted_value = True
    assert solver.Solve(model.model) in (cp_model.FEASIBLE, cp_model.OPTIMAL)
    checked = validate_layout(model.extract(solver, unit, "S2", "diagnostic"), grid, config, h)
    assert checked["pass"] and checked["fci"] >= witness["fci"]-1e-9


@pytest.mark.parametrize("area", [9, 11, 13])
def test_generic_warm_start_finds_sharing_without_witness_input(area):
    import time
    from fea.furniture.candidates import generate_candidates
    from fea.furniture.library import library
    from fea.solve.greedy import greedy_warm_start
    config = load_config("config/project.yaml")
    h = parse_households(config["households"], config["furniture"])["H3_couple_one_remote"]
    grid = rasterize(mechanism_shell(area))
    items = library(config["furniture"])
    candidates = generate_candidates(grid, items)
    result = greedy_warm_start({"strategy": "S2", "items": [], "service": {}}, grid, items,
                               candidates, h, config, time.perf_counter()+12)
    checked = validate_layout(result, grid, config, h)
    lower = validate_layout(mechanism_witness(area, h), grid, config, h)["fci"]
    assert checked["pass"] and checked["fci"] >= lower-1e-9
    assert checked["credits"] == result["credits"]
