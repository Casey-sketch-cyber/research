"""Optimize quality-weighted service using the existing geometry and CP-SAT model."""
from copy import deepcopy
from fractions import Fraction
import math
import time

from ortools.sat.python import cp_model

from fea.config import config_hash
from fea.furniture.library import library
from fea.households import demanded_hours
from fea.solve.cpsat import Model, _integer_coefficients, solve_layout
from fea.solve.greedy import greedy_layout
from fea.solve.reachability import check_connectivity
from phase11_kit_validator import quality_metrics

QUALITY_SCALE = 100


def quality_objective(model, household, qualities):
    """Add exact integer minimum quality over selected service assignments."""
    m = model.model
    assignments = {}
    for (variant, slot, demand, _, _, item), flag in model.assignment.items():
        quality = qualities.get(model.instances[item].item.name, 1.)
        scaled = round(quality*QUALITY_SCALE)
        if not 0 <= scaled <= QUALITY_SCALE or abs(scaled/QUALITY_SCALE-quality) > 1e-8:
            raise ValueError("Item quality is outside the supported exact scale")
        if scaled < QUALITY_SCALE:
            assignments.setdefault((variant, slot, demand), []).append(QUALITY_SCALE-(QUALITY_SCALE-scaled)*flag)
    terms = []
    for variant in household.variants:
        for slot in household.slots:
            for demand in variant.demand[slot.name]:
                coefficient = (Fraction(str(variant.frequency))*Fraction(str(slot.hours))*
                               Fraction(str(demand.weight))/Fraction(str(demanded_hours(household, variant.name))))
                served, denom = model.credit[demand.id]
                relevant = assignments.get((variant.name, slot.name, demand.id), [])
                if demand.need == "storage" or not relevant:
                    terms.append((served, coefficient/denom))
                else:
                    capped = m.NewIntVar(0, QUALITY_SCALE, demand.id+":quality_credit")
                    m.AddMinEquality(capped, [QUALITY_SCALE*served, *relevant])
                    terms.append((capped, coefficient/QUALITY_SCALE))
    coeff, scale = _integer_coefficients([c for _, c in terms])
    quality = sum(c*v for c, (v, _) in zip(coeff, terms))
    burden_coeff, _ = _integer_coefficients([c for _, c in model.burden_terms])
    window = sum(v for v, _ in model.window_terms)
    window_bound = sum(bound for _, bound in model.window_terms)
    secondary = window_bound+1
    weight = sum(burden_coeff)*secondary+window_bound+1
    m.Maximize(quality*weight-model.burden*secondary-window)
    upper = min(math.ceil(scale), math.ceil(model.primary_upper*scale/model.primary_scale))
    return quality, scale, upper


class QualityBoundStop(cp_model.CpSolverSolutionCallback):
    def __init__(self, expression, upper, burden):
        super().__init__()
        self.expression, self.upper, self.burden = expression, upper, burden

    def on_solution_callback(self):
        if self.Value(self.expression) >= self.upper and self.Value(self.burden) == 0:
            self.StopSearch()


def remove_unreachable(layout, problems):
    """Keep only accessible assigned service before independent rescoring."""
    for problem in problems:
        demand = problem["demand_id"]
        if not demand:
            continue
        entries = layout["service"][problem["variant"]][problem["slot"]]
        for entry in entries:
            if entry["demand_id"] == demand and problem["instance_id"] in entry["by"]:
                if entry["need"] == "storage":
                    entry["by"].remove(problem["instance_id"])
                else:
                    entry["by"] = []


def objective_score(check):
    return check["fciq"], -check["tb"]


def solve_quality(unit, household, strategy, config, qualities, prepared, incumbent=None):
    """Retain the best independently valid FCIq and use the reviewed time cap."""
    grid, candidates = prepared
    furniture = config["furniture"]
    scale = household.overrides.get("global_clearance_scale", furniture["meta"]["global_clearance_scale"])
    items = library(furniture, strategy, scale)
    if all(qualities.get(name, 1.) == 1. for name in items):
        return solve_layout(unit, household, strategy, config, incumbent, prepared)

    started = time.perf_counter()
    settings = config["solver"]
    digest = config_hash(config)
    width = household.overrides.get("walking_width", furniture["meta"]["walking_width"])
    empty = dict(unit_key=unit.unit_key, source=unit.source, nia_m2=unit.interior.area,
                 furnishable_area_m2=unit.classes["furnishable"].area, household=household.name,
                 strategy=strategy, algorithm="cp_sat_quality", resolution_m=grid.resolution, items=[], service={},
                 config_hash=digest)
    best = deepcopy(empty)
    best_check = quality_metrics(best, grid, config, household, qualities)
    if not best_check["pass"]:
        raise ValueError("Ineligible empty shell in furniture-kit sample")
    if incumbent:
        proposal = deepcopy(incumbent)
        proposal["strategy"] = strategy
        trial = quality_metrics(proposal, grid, config, household, qualities)
        if trial["pass"] and objective_score(trial) >= objective_score(best_check):
            best, best_check = proposal, trial
    greedy = greedy_layout(empty, grid, items, candidates, household, config,
                           min(started+settings["time_limit_s"]*.15, time.perf_counter()+6.))
    trial = quality_metrics(greedy, grid, config, household, qualities)
    if trial["pass"] and objective_score(trial) >= objective_score(best_check):
        best, best_check = greedy, trial

    model = Model(grid, household, items, candidates, strategy, config)
    quality, multiplier, upper = quality_objective(model, household, qualities)
    error = model.model.Validate()
    if error:
        raise ValueError("Invalid quality CP-SAT model: "+error)
    model.warm_start(best, enforce_bound=False)
    model.model.Add(quality >= round(best_check["fciq"]*float(multiplier)))
    deadline = started + settings["time_limit_s"]
    slice_s = float(settings.get("reachability_round_s", 5.))
    status = "TIMEOUT_WITH_INCUMBENT"
    iterations = 0
    for _ in range(settings["reachability_max_iterations"]):
        if round(best_check["fciq"]*float(multiplier)) >= upper and best_check["tb"] <= 1e-9:
            status = "SATURATED_QUALITY_INCUMBENT"
            break
        left = deadline-time.perf_counter()
        if left <= .01:
            break
        solver = cp_model.CpSolver()
        solver.parameters.max_time_in_seconds = min(left, slice_s)
        solver.parameters.num_search_workers = settings["num_workers"]
        solver.parameters.random_seed = config["seed"]
        result = solver.Solve(model.model, QualityBoundStop(quality, upper, model.burden))
        iterations += 1
        if result == cp_model.UNKNOWN:
            slice_s *= 2
            continue
        if result not in (cp_model.FEASIBLE, cp_model.OPTIMAL):
            break
        slice_s = float(settings.get("reachability_round_s", 5.))
        proposed = model.extract(solver, unit, strategy, digest)
        problems = check_connectivity(proposed, grid, items, household, width)
        remove_unreachable(proposed, problems)
        check = quality_metrics(proposed, grid, config, household, qualities)
        if not problems and check["pass"]:
            if abs(check["fciq"]-solver.Value(quality)/float(multiplier)) > 1e-7:
                raise ValueError("Independent validator disagrees with the FCIq objective")
            if abs(check["fci"]-solver.Value(model.primary)/float(model.primary_scale)) > 1e-7:
                raise ValueError("Independent validator disagrees with ordinary FCI")
        if check["pass"] and objective_score(check) >= objective_score(best_check):
            best, best_check = proposed, check
            status = "FEASIBLE_ACCESS_ADJUSTED" if problems else solver.StatusName(result)
        if not problems and result == cp_model.OPTIMAL:
            break
        model.cut(problems, solver)
        model.warm_start(best, enforce_bound=False)
        model.model.Add(quality >= round(best_check["fciq"]*float(multiplier)))
    best.update({name: best_check[name] for name in ("fci", "fci_by_variant", "served_hours", "demanded_hours", "tb", "fciq")})
    best["algorithm"], best["config_hash"] = "cp_sat_quality", digest
    best["validator"] = best_check
    best["solver"] = dict(status=status, time_s=time.perf_counter()-started, fci_solver=best_check["fci"],
                          quality_objective=best_check["fciq"], reach_iterations=iterations,
                          quality_upper_bound=float(upper/multiplier))
    return best
