"""Shared-anchor CP-SAT layouts with exact grid rectangles and lazy access cuts."""
from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from fractions import Fraction
import math
import itertools
import time

import numpy as np
from ortools.sat.python import cp_model
from scipy import ndimage

from fea.config import config_hash
from fea.furniture.library import library, rectangles
from fea.furniture.candidates import generate_candidates
from fea.geometry.raster import rasterize
from fea.households import demanded_hours
from fea.validate import validate_layout
from .reachability import check_connectivity
from .greedy import greedy_warm_start as greedy_layout


@dataclass
class Instance:
    """A presence bit and a candidate-table anchor shared across every slot."""
    identity: str
    item: object
    present: object
    x: object
    y: object
    orientation: object
    states: dict
    pose: object


def _integer_coefficients(values):
    denominator = math.lcm(*(v.denominator for v in values)) if values else 1
    coefficients = [int(v*denominator) for v in values]
    divisor = math.gcd(*coefficients) if coefficients else 1
    divisor = max(1, divisor)
    return [v//divisor for v in coefficients], Fraction(denominator, divisor)


def relaxed_capacity_bound(instances, household):
    """Upper-bound FCI by removing geometry and day-wide state consistency."""
    tokens = {key: set(t for state in instance.item.states for t in state.serves) for key, instance in instances.items()}
    total = Fraction(0)
    for variant in household.variants:
        served = Fraction(0)
        for slot in household.slots:
            options = []
            for demand in variant.demand[slot.name]:
                weight = Fraction(str(demand.weight))
                possibilities = [(frozenset(), Fraction(0))]
                if demand.need == "storage":
                    keys = frozenset(i for i, ts in tokens.items() if "storage" in ts)
                    amount = sum(Fraction(str(instances[i].item.storage_units)) for i in keys)
                    possibilities.append((keys, weight*min(Fraction(1), amount/Fraction(str(demand.units)))))
                else:
                    for rule in household.capability_rules[demand.need]["satisfied_by"]:
                        for selected in itertools.product(*[[i for i, ts in tokens.items() if token in ts] for token in rule]):
                            if len(set(selected)) == len(selected): possibilities.append((frozenset(selected), weight))
                options.append(possibilities)
            best = Fraction(0)
            for allocation in itertools.product(*options):
                ids = [i for members, _ in allocation for i in members]
                if len(ids) == len(set(ids)): best = max(best, sum((v for _, v in allocation), Fraction(0)))
            served += Fraction(str(slot.hours))*best
        total += Fraction(str(variant.frequency))*served/Fraction(str(demanded_hours(household, variant.name)))
    return total


class PrimaryBoundStop(cp_model.CpSolverSolutionCallback):
    """Stop only after proving the FCI bound and zero burden; window tie-break stays open."""
    def __init__(self, model):
        super().__init__()
        self.layout_model = model
        self.reached = False

    def on_solution_callback(self):
        if self.Value(self.layout_model.primary) >= self.layout_model.primary_upper and self.Value(self.layout_model.burden) == 0:
            self.reached = True
            self.StopSearch()


class Model:
    """Table-domain anchors and optional rectangle intervals, not cell-wise occupancies.

    Each body/clearance strip is a rectangle at the common raster anchor. Global
    NoOverlap2D constraints impose the same body/body and body/clearance exclusions
    while allowing clearance/clearance overlap. The configured anchor lattice is explicit; geometry stays at raster resolution.
    """
    def __init__(self, grid, household, items, candidates, strategy, config):
        self.grid, self.household, self.items, self.config = grid, household, items, config
        self.pose_indices = {name: {tuple(int(v) for v in p): n+1 for n, p in enumerate(poses)}
                             for name, poses in candidates.items()}
        self.model = m = cp_model.CpModel()
        self.instances, self.assignment, self.credit = {}, {}, {}
        self.primary_terms, self.burden_terms, self.window_terms = [], [], []
        self.rect_cache = {}
        ny, nx = grid.labels.shape
        window_distance = ndimage.distance_transform_edt(~grid.window) if grid.window.any() else np.zeros_like(grid.labels, float)
        for name, item in items.items():
            poses = candidates[name]
            if not len(poses): continue
            previous = None
            for number in range(item.max_instances):
                identity = f"{name}#{number+1}"
                present = m.NewBoolVar(identity+":placed")
                x, y = m.NewIntVar(0, nx, identity+":x"), m.NewIntVar(0, ny, identity+":y")
                orient = m.NewIntVar(0, 3, identity+":orientation")
                # Index 0 is the absent sentinel; actual candidates use distinct indices.
                pose = m.NewIntVar(0, len(poses), identity+":pose")
                m.AddAllowedAssignments([pose, x, y, orient], [[0, 0, 0, 0]]+
                    [[i+1, int(a), int(b), int(o)//90] for i, (a, b, o) in enumerate(poses)])
                m.Add(pose > 0).OnlyEnforceIf(present)
                m.Add(pose == 0).OnlyEnforceIf(present.Not())
                if previous is not None:
                    m.Add(present <= previous[0]); m.Add(pose > previous[1]).OnlyEnforceIf(present)
                previous = present, pose
                states = {}
                for variant in household.variants:
                    day_state = m.NewBoolVar(identity+":"+variant.name+":day_state") if len(item.states) > 1 and strategy == "S1" else None
                    for slot in household.slots:
                        state = (0 if len(item.states) == 1 else day_state if day_state is not None
                                 else m.NewBoolVar(f"{identity}:{variant.name}:{slot.name}:state"))
                        if not isinstance(state, int): m.Add(state <= present)
                        states[variant.name, slot.name] = state
                instance = Instance(identity, item, present, x, y, orient, states, pose)
                self.instances[identity] = instance
                if any(t.startswith(("work", "dine")) for s in item.states for t in s.serves):
                    costs = [0]+[int(round(window_distance[min(int(b), ny-1), min(int(a), nx-1)])) for a, b, _ in poses]
                    cost = m.NewIntVar(0, max(costs), identity+":window_distance")
                    m.AddElement(pose, costs, cost)
                    self.window_terms.append((cost, max(costs)))
                if strategy == "S2" and len(item.states) > 1:
                    for variant in household.variants:
                        cycle = [states[variant.name, slot.name] for slot in household.slots]
                        for index, state in enumerate(cycle):
                            change = m.NewBoolVar(f"{identity}:{variant.name}:change:{index}")
                            m.AddAbsEquality(change, state-cycle[index-1])
                            self.burden_terms.append((change, Fraction(str(item.effort))*Fraction(str(variant.frequency))))
        # Mirrored alternatives share one physical family inventory limit.
        for family, group in config["furniture"].get("instance_groups", {}).items():
            members = set(group["members"])
            m.Add(sum(instance.present for instance in self.instances.values()
                      if instance.item.name in members) <= group["max_instances"])
        for variant in household.variants:
            for slot in household.slots:
                key = variant.name, slot.name
                bodies = {i: self.rectangle(instance, key, "body") for i, instance in self.instances.items()}
                m.AddNoOverlap2D([v[0] for v in bodies.values()], [v[1] for v in bodies.values()])
                for identity, instance in self.instances.items():
                    for side in ("front", "back", "left", "right"):
                        if not any(s.clearance.get(side, 0) > 0 for s in instance.item.states): continue
                        strip = self.rectangle(instance, key, side)
                        group = [v for i, v in bodies.items() if i != identity]+[strip]
                        m.AddNoOverlap2D([v[0] for v in group], [v[1] for v in group])
                self.service(variant, slot)
        # Unused furniture cannot improve any objective or feasible service set.
        for identity, instance in self.instances.items():
            uses = [v for key, v in self.assignment.items() if key[-1] == identity]
            m.Add(instance.present <= sum(uses))
        primary_coeff, primary_scale = _integer_coefficients([v for _, v in self.primary_terms])
        self.primary = sum(c*x for c, (x, _) in zip(primary_coeff, self.primary_terms))
        self.primary_scale = primary_scale
        burden_coeff, self.burden_scale = _integer_coefficients([v for _, v in self.burden_terms])
        burden = sum(c*x for c, (x, _) in zip(burden_coeff, self.burden_terms))
        self.burden = burden
        self.primary_upper = math.ceil(relaxed_capacity_bound(self.instances, household)*self.primary_scale)
        window = sum(v for v, _ in self.window_terms)
        window_bound = sum(bound for _, bound in self.window_terms)
        burden_bound = sum(burden_coeff)
        secondary_scale = window_bound+1
        primary_weight = max(math.ceil(config["solver"]["weights"]["served"]), burden_bound*secondary_scale+window_bound+1)
        self.objective_primary_weight = primary_weight
        m.Maximize(self.primary*primary_weight-burden*secondary_scale-window)

    def rectangle(self, instance, slot_key, kind):
        """Create one optional interval pair for an active body or clearance strip."""
        m, item = self.model, instance.item
        state = instance.states[slot_key]
        cache_key = instance.identity, str(state), kind
        if cache_key in self.rect_cache: return self.rect_cache[cache_key]
        geometries = []
        for angle in (0, 90, 180, 270):
            for spec in item.states:
                body, strips, _ = rectangles(spec, self.grid.resolution, angle)
                sides = [s for s in ("front", "back", "left", "right") if spec.clearance.get(s, 0) > 0]
                geometries.append(body if kind == "body" else strips[sides.index(kind)] if kind in sides else (0, 0, 0, 0))
        prefix = f"{instance.identity}:{slot_key}:{kind}"
        index = m.NewIntVar(0, len(geometries)-1, prefix+":lookup")
        m.Add(index == instance.orientation*len(item.states)+state)
        values = []
        for coordinate in range(4):
            constants = [g[coordinate] for g in geometries]
            variable = m.NewIntVar(min(constants), max(constants), prefix+f":dim{coordinate}")
            m.AddElement(index, constants, variable); values.append(variable)
        dx, dy, width, height = values
        present = instance.present
        if kind != "body":
            nonempty = m.NewBoolVar(prefix+":nonempty")
            m.AddElement(index, [int(g[2] > 0 and g[3] > 0) for g in geometries], nonempty)
            active = m.NewBoolVar(prefix+":active")
            m.Add(active <= present); m.Add(active <= nonempty); m.Add(active >= present+nonempty-1)
            present = active
        bound = max(self.grid.labels.shape)*3
        starts = [m.NewIntVar(-bound, bound, prefix+f":start{i}") for i in range(2)]
        ends = [m.NewIntVar(-bound, bound, prefix+f":end{i}") for i in range(2)]
        m.Add(starts[0] == instance.x+dx); m.Add(starts[1] == instance.y+dy)
        m.Add(ends[0] == starts[0]+width); m.Add(ends[1] == starts[1]+height)
        intervals = (m.NewOptionalIntervalVar(starts[0], width, ends[0], present, prefix+":ix"),
                     m.NewOptionalIntervalVar(starts[1], height, ends[1], present, prefix+":iy"))
        self.rect_cache[cache_key] = intervals
        return intervals

    def service(self, variant, slot):
        """Allocate each simultaneous demand occurrence to distinct capable instances."""
        m, key, used = self.model, (variant.name, slot.name), {}
        def assign(identity, token, label):
            instance = self.instances[identity]
            allowed = [i for i, state in enumerate(instance.item.states) if token in state.serves]
            if not allowed: return None
            y = m.NewBoolVar(label+":"+identity)
            m.Add(y <= instance.present)
            state = instance.states[key]
            if len(allowed) < len(instance.item.states): m.Add(state == allowed[0]).OnlyEnforceIf(y)
            used.setdefault(identity, []).append(y)
            return y
        for demand in variant.demand[slot.name]:
            weight = Fraction(str(variant.frequency))*Fraction(str(slot.hours))*Fraction(str(demand.weight))/Fraction(str(demanded_hours(self.household, variant.name)))
            if demand.need == "storage":
                capacity = []
                for identity, instance in self.instances.items():
                    if not instance.item.storage_units: continue
                    y = assign(identity, "storage", demand.id)
                    if y is None: continue
                    self.assignment[variant.name, slot.name, demand.id, 0, 0, identity] = y
                    capacity.append(int(round(instance.item.storage_units*10))*y)
                required = int(round(demand.units*10))
                served = m.NewIntVar(0, required, demand.id+":capacity")
                m.AddMinEquality(served, [required, sum(capacity)])
                self.primary_terms.append((served, weight/required))
                self.credit[demand.id] = served, required
            else:
                options = []
                for alternative, tokens in enumerate(self.household.capability_rules[demand.need]["satisfied_by"]):
                    option = m.NewBoolVar(demand.id+f":alternative{alternative}"); options.append(option)
                    for t, token in enumerate(tokens):
                        assignments = []
                        for identity in self.instances:
                            y = assign(identity, token, demand.id+f":option{alternative}:token{t}")
                            if y is not None:
                                self.assignment[variant.name, slot.name, demand.id, alternative, t, identity] = y
                                assignments.append(y)
                        m.Add(sum(assignments) == option)
                served = m.NewBoolVar(demand.id+":served")
                m.Add(sum(options) == served)
                self.credit[demand.id] = served, 1
                self.primary_terms.append((served, weight))
        for values in used.values(): m.Add(sum(values) <= 1)

    def extract(self, solver, unit, strategy, digest):
        """Serialize poses, active states and actual simultaneous service assignments."""
        placed = []
        for identity, instance in self.instances.items():
            if not solver.Value(instance.present): continue
            states = {v.name: {s.name: instance.item.states[solver.Value(instance.states[v.name, s.name])].name
                      for s in self.household.slots} for v in self.household.variants}
            placed.append(dict(instance_id=identity, type=instance.item.name,
                x=round(self.grid.origin[0]+solver.Value(instance.x)*self.grid.resolution, 9),
                y=round(self.grid.origin[1]+solver.Value(instance.y)*self.grid.resolution, 9),
                orientation_deg=90*solver.Value(instance.orientation), states=states))
        service = {v.name: {s.name: [] for s in self.household.slots} for v in self.household.variants}
        for variant in self.household.variants:
            for slot in self.household.slots:
                for demand in variant.demand[slot.name]:
                    by = sorted({k[-1] for k, y in self.assignment.items() if k[:3] == (variant.name, slot.name, demand.id) and solver.Value(y)})
                    variable, scale = self.credit[demand.id]
                    service[variant.name][slot.name].append(dict(demand_id=demand.id, need=demand.need, by=by,
                        model_credit=solver.Value(variable)/scale))
        return dict(unit_key=unit.unit_key, source=unit.source, nia_m2=unit.interior.area,
            furnishable_area_m2=unit.classes["furnishable"].area, household=self.household.name, strategy=strategy,
            algorithm="cp_sat", resolution_m=self.grid.resolution, items=placed, service=service, config_hash=digest)

    def warm_start(self, layout, enforce_bound=True):
        """Seed a valid nested-strategy incumbent without removing any candidates."""
        m, indexed = self.model, {i["instance_id"]: i for i in layout["items"]}
        m.ClearHints()
        hinted_states = set()
        for identity, instance in self.instances.items():
            item = indexed.get(identity)
            m.AddHint(instance.present, int(item is not None))
            for i, variable in enumerate((instance.x, instance.y)):
                value = round((item[("x", "y")[i]]-self.grid.origin[i])/self.grid.resolution) if item else 0
                m.AddHint(variable, value)
            m.AddHint(instance.orientation, item["orientation_deg"]//90 if item else 0)
            pose_key = (round((item["x"]-self.grid.origin[0])/self.grid.resolution),
                        round((item["y"]-self.grid.origin[1])/self.grid.resolution), item["orientation_deg"]) if item else None
            pose_index = self.pose_indices[instance.item.name].get(pose_key) if item else 0
            if pose_index is not None:
                m.AddHint(instance.pose, pose_index)
            for (variant, slot), variable in instance.states.items():
                if isinstance(variable, int) or variable.Index() in hinted_states: continue
                hinted_states.add(variable.Index())
                value = [s.name for s in instance.item.states].index(item["states"][variant][slot]) if item else 0
                m.AddHint(variable, value)
        # A pose/state hint alone leaves the primary objective's assignment
        # literals unspecified. Hint one explicit capability allocation too,
        # without fixing it or removing any alternative from the model.
        selected = set()
        for variant in self.household.variants:
            for slot in self.household.slots:
                entries = {e["demand_id"]: e for e in layout.get("service", {}).get(variant.name, {}).get(slot.name, [])}
                for demand in variant.demand[slot.name]:
                    by = entries.get(demand.id, {}).get("by", [])
                    by = sorted(i for i in by if i in indexed and i in self.instances)
                    if demand.need == "storage":
                        selected.update((variant.name, slot.name, demand.id, 0, 0, i) for i in by)
                        continue
                    for alternative, tokens in enumerate(self.household.capability_rules[demand.need]["satisfied_by"]):
                        if len(tokens) != len(by):
                            continue
                        match = next((permutation for permutation in itertools.permutations(by) if all(
                            token in next(s.serves for s in self.instances[i].item.states
                                          if s.name == indexed[i]["states"][variant.name][slot.name])
                            for token, i in zip(tokens, permutation))), None)
                        if match is not None:
                            selected.update((variant.name, slot.name, demand.id, alternative, t, i)
                                            for t, i in enumerate(match))
                            break
        for key, variable in self.assignment.items():
            m.AddHint(variable, int(key in selected))
        if enforce_bound: m.Add(self.primary >= round(layout["fci"]*float(self.primary_scale)))

    def cut(self, problems, solver):
        """Require a certified barrier to open, or change/withdraw the target.

        Unlike reserving all old bottleneck rectangles, this disjunction retains
        alternate routes: at least one witness rectangle must cease to be fully
        covered by its current owner. Movable service targets are pose-guarded.
        """
        m = self.model
        count = 0
        signatures = set()
        for problem in problems:
            signature = str(problem)
            if signature in signatures: continue
            signatures.add(signature)
            alternatives = []
            def escape(expression, name):
                literal = m.NewBoolVar("access_open:"+name+":"+str(len(m.Proto().constraints)))
                m.Add(expression).OnlyEnforceIf(literal)
                alternatives.append(literal)
            for identity, (x0,y0,x1,y1) in problem["barrier_rectangles"].items():
                instance = self.instances[identity]
                ix, iy = self.rectangle(instance,(problem["variant"],problem["slot"]),"body")
                alternatives.append(instance.present.Not())
                for expression in (ix.StartExpr()>x0, iy.StartExpr()>y0, ix.EndExpr()<x1, iy.EndExpr()<y1):
                    escape(expression,identity)
            if problem["demand_id"]:
                instance = self.instances[problem["instance_id"]]
                # The service region moves with this pose; without this guard a
                # cut could wrongly eliminate a relocation beside the entrance.
                for variable in (instance.x,instance.y,instance.orientation,instance.states[problem["variant"],problem["slot"]]):
                    if not isinstance(variable,int): escape(variable != solver.Value(variable),"target")
                claimed = [y for key,y in self.assignment.items() if key[:3]==
                    (problem["variant"],problem["slot"],problem["demand_id"]) and key[-1]==problem["instance_id"] and solver.Value(y)]
                alternatives.extend(y.Not() for y in claimed)
            if alternatives:
                m.AddBoolOr(alternatives)
                count += 1
        return count


def solve_layout(unit, household, strategy, config, incumbent=None, prepared=None):
    """Optimize within one total time budget, retaining independently valid incumbents."""
    started = time.perf_counter()
    scale = household.overrides.get("global_clearance_scale", config["furniture"]["meta"]["global_clearance_scale"])
    width = household.overrides.get("walking_width", config["furniture"]["meta"]["walking_width"])
    items = library(config["furniture"], strategy, scale)
    if prepared is None:
        grid = rasterize(unit, config["raster"]["resolution_m"], width, config["raster"].get("source_gap_close_m",.15))
        candidates = generate_candidates(grid, items, config["raster"]["orientations_deg"], config["raster"].get("anchor_stride_m"))
    else:
        grid, candidates = prepared
    digest = config_hash(config)
    empty = dict(unit_key=unit.unit_key, source=unit.source, nia_m2=unit.interior.area,
        furnishable_area_m2=unit.classes["furnishable"].area, household=household.name, strategy=strategy,
        algorithm="cp_sat", resolution_m=grid.resolution, items=[], service={}, config_hash=digest)
    baseline = validate_layout(empty, grid, config, household)
    best = deepcopy(incumbent) if incumbent is not None else empty
    best["strategy"] = strategy
    best_validation = validate_layout(best, grid, config, household)
    best.update({k: best_validation[k] for k in ("fci", "fci_by_variant", "tb", "served_hours", "demanded_hours")})
    if not baseline["pass"]:
        best = empty; best_validation = baseline
        best.update({k: baseline[k] for k in ("fci", "fci_by_variant", "tb", "served_hours", "demanded_hours")})
        best["solver"] = dict(status="STRUCTURAL_UNREACHABLE", time_s=time.perf_counter()-started,
            objective=None, bound=None, reach_iterations=0, fci_solver=0., termination="fixed_service_unreachable_without_furniture")
        best["validator"] = best_validation
        return best
    first_valid = time.perf_counter()-started if best_validation["pass"] and best["fci"]>0 else None
    greedy_started = time.perf_counter()
    greedy = greedy_layout(empty, grid, items, candidates, household, config,
        min(started+config["solver"]["time_limit_s"]*.15, greedy_started+6.))
    greedy_time = time.perf_counter()-greedy_started
    if greedy["fci"]>best["fci"]+1e-9:
        best = greedy
        best_validation = validate_layout(best, grid, config, household)
    if first_valid is None and greedy["fci"]>0:
        first_valid = greedy_started-started + greedy.get("greedy",{}).get("first_positive_s",greedy_time)
    model = Model(grid, household, items, candidates, strategy, config)
    if best_validation["pass"] and best["tb"] == 0 and round(best["fci"]*float(model.primary_scale)) >= model.primary_upper:
        best["validator"] = best_validation
        best["solver"] = dict(status="FEASIBLE", termination="primary_bound_incumbent", time_s=time.perf_counter()-started,
            first_valid_time_s=first_valid, greedy_time_s=greedy_time, greedy_fci=greedy["fci"],
            build_time_s=time.perf_counter()-started, objective=None, bound=None, reach_iterations=0,
            fci_solver=best["fci"], retained_previous_incumbent=True, window_tiebreak_optimized=False,
            primary_upper_bound=model.primary_upper/float(model.primary_scale))
        return best
    if best_validation["pass"]: model.warm_start(best)
    error = model.model.Validate()
    if error: raise ValueError("Invalid CP-SAT model: "+error)
    built = time.perf_counter()
    deadline = started+config["solver"]["time_limit_s"]
    status_name, objective, bound, iterations = "TIMEOUT_WITH_INCUMBENT", None, None, 0
    raw_fci, selected_fci, found = 0., best["fci"], False
    selected_status = "TIMEOUT_WITH_INCUMBENT"
    diagnostics = []
    geometric_cuts = 0
    round_limit = float(config["solver"].get("reachability_round_s", 5.))
    for iteration in range(config["solver"]["reachability_max_iterations"]):
        remaining = deadline-time.perf_counter()
        if remaining <= .01: break
        solver = cp_model.CpSolver()
        solver.parameters.max_time_in_seconds = min(remaining, round_limit)
        solver.parameters.num_search_workers = config["solver"]["num_workers"]
        solver.parameters.random_seed = config["seed"]
        callback = PrimaryBoundStop(model)
        status = solver.Solve(model.model, callback)
        status_name = solver.StatusName(status)
        iterations = iteration+1
        if status == cp_model.UNKNOWN:
            # A slice can expire during presolve, before any incumbent exists.
            # Retry with a larger slice instead of wasting the remaining budget.
            diagnostics.append(dict(status=status_name, slice_limit_s=min(remaining,round_limit),
                elapsed_s=time.perf_counter()-started, reachability_failures=None))
            round_limit = min(deadline-time.perf_counter(), round_limit*2)
            continue
        if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE): break
        round_limit = float(config["solver"].get("reachability_round_s", 5.))
        objective, bound = solver.ObjectiveValue(), solver.BestObjectiveBound()
        layout = model.extract(solver, unit, strategy, digest)
        raw_fci = solver.Value(model.primary)/float(model.primary_scale)
        problems = check_connectivity(layout, grid, items, household, width)
        # At a budget/iteration limit, unreachable assigned instances are explicitly
        # removed before independently scoring the retained feasible geometry.
        for problem in problems:
            if not problem["demand_id"]: continue
            entries = layout["service"][problem["variant"]][problem["slot"]]
            for entry in entries:
                if entry["demand_id"] == problem["demand_id"] and problem["instance_id"] in entry["by"]:
                    entry["by"].remove(problem["instance_id"])
                    if entry["need"] != "storage": entry["by"] = []
        checked = validate_layout(layout, grid, config, household)
        if not problems and abs(checked["fci"]-raw_fci) > 1e-6:
            raise RuntimeError(f"Solver/validator FCI mismatch: {raw_fci} vs {checked['fci']}")
        diagnostics.append(dict(status=status_name, model_fci=raw_fci, validator_fci=checked["fci"],
                                reachability_failures=len(problems), validator_violations=checked["violations"],
                                stopped_at_primary_bound=callback.reached))
        if checked["pass"] and checked["fci"]>0 and first_valid is None: first_valid = time.perf_counter()-started
        if checked["pass"] and (checked["fci"] > best["fci"]+1e-9 or
            (abs(checked["fci"]-best["fci"]) <= 1e-9 and checked["tb"] <= best["tb"])):
            best, best_validation, found = layout, checked, True
            selected_status = status_name if not problems else "FEASIBLE_ACCESS_ADJUSTED"
            best.update({k: checked[k] for k in ("fci", "fci_by_variant", "tb", "served_hours", "demanded_hours")})
            # Recompute the solver-side score of the retained explicit assignment.
            totals = {}
            for variant in household.variants:
                served = 0.
                for slot in household.slots:
                    for demand, assignment in zip(variant.demand[slot.name], best["service"][variant.name][slot.name]):
                        credit = min(1., sum(items[i.rsplit('#', 1)[0]].storage_units for i in assignment["by"])/demand.units) if demand.need == "storage" else float(bool(assignment["by"]))
                        served += slot.hours*demand.weight*credit
                totals[variant.name] = served/demanded_hours(household, variant.name)
            selected_fci = sum(v.frequency*totals[v.name] for v in household.variants)
            if abs(selected_fci-best["fci"]) > 1e-6: raise RuntimeError("Adjusted assignment/validator mismatch")
        if not problems and (status==cp_model.OPTIMAL or callback.reached): break
        geometric_cuts += model.cut(problems, solver)
        hint = deepcopy(layout)
        offenders = {i for problem in problems for i in problem["blockers"]}
        offenders.update(problem["instance_id"] for problem in problems if problem["instance_id"])
        hint["items"] = [i for i in hint["items"] if i["instance_id"] not in offenders]
        for slots in hint["service"].values():
            for entries in slots.values():
                for entry in entries:
                    if offenders.intersection(entry["by"]):
                        entry["by"] = [i for i in entry["by"] if i not in offenders] if entry["need"]=="storage" else []
        model.warm_start(hint, enforce_bound=False)
        model.model.Add(model.primary >= round(best["fci"]*float(model.primary_scale)))
    best["validator"] = best_validation
    best["solver"] = dict(status=selected_status, last_search_status=status_name,
        time_s=time.perf_counter()-started, build_time_s=built-started, objective=objective, bound=bound,
        first_valid_time_s=first_valid, greedy_time_s=greedy_time, greedy_fci=greedy["fci"], geometric_cuts=geometric_cuts,
        reach_iterations=iterations, fci_solver=selected_fci, raw_last_model_fci=raw_fci,
        objective_bound_scope="last solution-bearing raw CP-SAT search; may differ from retained validated layout",
        retained_previous_incumbent=not found and incumbent is not None, trace=diagnostics,
        primary_upper_bound=model.primary_upper/float(model.primary_scale), window_tiebreak_optimized=selected_status == "OPTIMAL",
        encoding="configured anchor tables + optional rectangle intervals + guarded geometric frontier cuts")
    return best
