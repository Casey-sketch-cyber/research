"""Run the reviewed, time-boxed H1/H3 furniture-kit experiment."""
from datetime import datetime, timezone
import fcntl
import math
from pathlib import Path
import time

import pandas as pd
import yaml
from tqdm import tqdm

from fea.config import config_hash
from fea.io import prepare_cli, start_run, write_json
from phase09_execution import apply_production, checked_inputs, cpu_slots, fingerprint, hash_inputs, load_json, run_weighted
from phase11_kit_design import candidate_grid, kit_configuration, select_shells
from phase11_kit_jobs import run_kit_case
from phase11_kit_report import export_results

ROOT = Path("results/expK")
F1 = Path("results/expA_f1")
POLICY = Path("config/execution_policy.yaml")
C_GATE = Path("results/expC/acceptance.json")


def policy_config():
    policy = yaml.safe_load(POLICY.read_text())["K_kit_design"]
    if policy["full_grid_enabled"] or not policy["two_day_limit_enforced"] or policy["replacement_deadline_days"] != 2:
        raise ValueError("K requires the approved reduced two-day scope")
    scope = policy["reduced_scope"]
    if scope["households"] != ["H1_single_commuter", "H3_couple_one_remote"]:
        raise ValueError("K households differ from D-39")
    if [scope[k] for k in ("candidate_kits", "training_shells", "heldout_shells", "real_plans")] != [8, 30, 15, 15]:
        raise ValueError("K scope differs from D-38")
    return scope


def freeze(config, scope, corpus):
    sample = pd.read_csv(F1/"sample.csv")
    shells = select_shells(config, scope, sample, corpus)
    grid = candidate_grid(config, scope["households"], scope["candidate_kits"])
    paths = ROOT/"shell_sets.csv", ROOT/"candidate_kits.json"
    shells["shell_id"], shells["config_hash"] = shells.unit_key, config_hash(config)
    encoded = shells.to_csv(index=False).encode()
    if paths[0].exists() and paths[0].read_bytes() != encoded:
        raise ValueError("Frozen kit sample changed")
    if paths[1].exists() and load_json(paths[1]) != grid:
        raise ValueError("Frozen kit vectors changed")
    paths[0].write_bytes(encoded)
    write_json(paths[1], grid)
    return shells, grid


def approved_small_settings():
    production = load_json(F1/"run.json")["production_settings"]
    small = production["small"]
    if [small[k] for k in ("time_limit_s", "num_workers", "anchor_stride_m")] != [120, 4, .1]:
        raise ValueError("K production settings differ from reviewed small-home settings")
    return production


def projected_solves(train, scope):
    combos = scope["candidate_kits"]
    finalists = math.ceil(combos*.2)
    search = combos*min(10, train)+finalists*min(30, train)+min(5, finalists)*train
    bespoke = combos*train
    confirmation = 9*(train+scope["heldout_shells"]+scope["real_plans"])
    return len(scope["households"])*(2*search+bespoke+confirmation)


class Experiment:
    def __init__(self, config, scope, corpus, shells, grid, cache, code, deadline):
        self.config, self.scope, self.corpus, self.shells, self.grid = config, scope, corpus, shells, grid
        self.cache, self.code, self.deadline = cache, code, deadline
        self.slots = cpu_slots()
        self.production = approved_small_settings()
        self.rows, self.search_log, self.confirmations = {}, [], []
        self.prepared = {}

    def task(self, unit_key, household, kit, flat, mode):
        kit_id = kit["kit_id"] if kit else "catalogue"
        key = household, kit_id
        if key not in self.prepared:
            base, _ = apply_production(self.config, self.production, 20.)
            self.prepared[key] = kit_configuration(base, household, kit)
        cfg, qualities = self.prepared[key]
        task_key = fingerprint([unit_key, household, kit_id, flat, mode])[:24]
        return dict(task_key=task_key, unit_json=self.corpus.loc[unit_key, "unit_json"], household=household,
                    config=cfg, qualities=qualities, kit_id=kit_id, flat=flat, mode=mode,
                    code_hash=self.code, threads=cfg["solver"]["num_workers"], cache=self.cache.as_posix(),
                    deadline_epoch=self.deadline)

    def evaluate(self, stage, jobs):
        task_keys = {job["task_key"] for job in jobs}
        if len(task_keys) != len(jobs):
            raise ValueError("Duplicate kit tasks in one stage")
        before = set(self.rows)
        pending = [job for job in jobs if job["task_key"] not in before]
        for index, rows in enumerate(tqdm(run_weighted(run_kit_case, pending, self.slots), total=len(pending), desc=stage), 1):
            self.rows[rows[0]["task_key"]] = rows
            if index % 5 == 0 or index == len(pending):
                write_json(ROOT/"progress.json", dict(status="running", stage=stage, completed_tasks=index+len(jobs)-len(pending),
                           expected_tasks=len(jobs), unique_audited_layouts=sum(len(r) for r in self.rows.values())))
        return pd.DataFrame([row for key in sorted(task_keys) for row in self.rows[key]])

    def pilot(self):
        began = time.perf_counter()
        training = self.shells[self.shells["set"] == "train"]
        real = self.shells[self.shells["set"] == "real"]
        jobs = []
        for hh in self.scope["households"]:
            first, largest = self.grid[hh][:2]
            jobs += [self.task(training.iloc[0].unit_key, hh, first, False, "search"),
                     self.task(training.iloc[9].unit_key, hh, largest, True, "search"),
                     self.task(training.iloc[19].unit_key, hh, None, False, "confirm"),
                     self.task(real.iloc[len(real)//2].unit_key, hh, first, False, "confirm")]
        measured = self.evaluate("runtime_pilot", jobs)
        measured.to_csv(ROOT/"runtime_pilot.csv", index=False)
        saved_seconds = sum(load_json(self.cache/job["task_key"]/"record.json")["elapsed_seconds"] for job in jobs)
        prior = ROOT/"runtime_pilot.json"
        if prior.exists():
            return load_json(prior)
        elapsed = time.perf_counter()-began
        concurrent = self.slots//self.production["small"]["num_workers"]
        cap = max(120., float(measured.own_search_time_s.max())) + float(measured.preparation_time_s.max())
        longest_case = max(load_json(self.cache/job["task_key"]/"record.json")["elapsed_seconds"] for job in jobs)
        tail_allowance = longest_case*(concurrent-1)/concurrent
        factor = max(1., (elapsed-tail_allowance)*concurrent/max(saved_seconds, 1e-9))
        projection = []
        for train in (30, 24, 18):
            count = projected_solves(train, self.scope)
            hours = count*cap*factor*1.15/concurrent/3600 + elapsed/3600
            projection.append(dict(train_shells=train, conservative_solve_count=count, projected_hours=hours, within_48h=hours <= 48))
        chosen = next((row["train_shells"] for row in projection if row["within_48h"]), None)
        result = dict(passed=chosen is not None, selected_training_shells=chosen, pilot_layouts=len(measured),
                      pilot_wall_seconds=elapsed, max_observed_per_solve_s=float(measured.own_search_time_s.max()),
                      max_candidate_prep_s=float(measured.preparation_time_s.max()),
                      conservative_per_solve_seconds=cap, concurrent_solves=concurrent, calibration_factor=factor,
                      pilot_tail_allowance_s=tail_allowance, safety_margin=.15, projection=projection, code_hash=self.code)
        write_json(prior, result)
        return result

    def search(self, household, kits, keys, flat, stage):
        name = household.split("_")[0]+"_"+("flat_" if flat else "quality_")+stage
        data = self.evaluate(name, [self.task(key, household, kit, flat, "search") for kit in kits for key in keys])
        mean = data.groupby("kit_id").agg(fciq_mean=("fciq", "mean"), fci_mean=("fci", "mean"),
                                         objective_mean=("objective_score", "mean"), n_shells=("unit_key", "nunique"),
                                         solve_time_s=("own_search_time_s", "sum")).reset_index()
        tau = self.config["experiments"]["adequacy_tau"]
        shares = data.assign(adequate=data.objective_score >= tau-1e-9).groupby("kit_id").adequate.mean()
        mean["adequacy_share"] = mean.kit_id.map(shares)
        lookup = {kit["kit_id"]: kit for kit in kits}
        for row in mean.to_dict("records"):
            self.search_log.append(dict(household=household, stage=stage, flat_quality=flat,
                                        **lookup[row["kit_id"]]["dimensions"], **row))
        ranked = mean.sort_values(["objective_mean", "kit_id"], ascending=[False, True])
        return [lookup[name] for name in ranked.kit_id], data

    def halving(self, household, train):
        choices = {}
        keys = train.unit_key.tolist()
        for flat in (False, True):
            kits = self.grid[household]
            ranked, _ = self.search(household, kits, keys[:10], flat, "halving_10")
            keep = math.ceil(len(kits)*self.config["experiments"]["K_kit_design"]["search"]["stages"][0]["keep"])
            ranked, _ = self.search(household, ranked[:keep], keys, flat, "halving_active")
            ranked, _ = self.search(household, ranked[:5], keys, flat, "halving_final_reused")
            choices["flat_quality" if flat else "kit"] = ranked[0]
        return choices

    def confirm(self, choices, shells):
        for household, selected in choices.items():
            for condition, kit in [("catalogue", None), ("kit", selected["kit"]), ("flat_quality", selected["flat_quality"])]:
                jobs = [self.task(key, household, kit, condition=="flat_quality", "confirm") for key in shells.unit_key]
                result = self.evaluate(household.split("_")[0]+"_confirm_"+condition, jobs)
                result["condition"] = condition
                self.confirmations.append(result.merge(shells[["unit_key", "set", "rank"]], on="unit_key", validate="many_to_one"))
        return pd.concat(self.confirmations, ignore_index=True)


def wait_for_c(wait):
    while not C_GATE.exists():
        if not wait:
            raise ValueError("C is not complete")
        state = Path(".tmp/g3_ablations_report_pipeline.json")
        if state.exists() and load_json(state)["status"] == "failed":
            raise ValueError("The prerequisite workflow failed")
        time.sleep(30)
    gate = load_json(C_GATE)
    if not gate["passed"]:
        raise ValueError("C has not passed")
    checked_inputs(gate["outputs"])


def run(config, digest, scope, corpus, shells, grid):
    inputs = hash_inputs([POLICY, C_GATE, F1/"acceptance.json", F1/"run.json",
                          ROOT/"candidate_kits.json", ROOT/"shell_sets.csv",
                          Path(config["paths"]["processed"])/"corpus_units.parquet",
                          "scripts/11b_run_expK.py", *sorted(Path("scripts").glob("phase11_kit_*.py")),
                          "scripts/phase09_execution.py", *sorted(Path("src/fea").rglob("*.py"))])
    code = fingerprint(dict(config_hash=digest, inputs=inputs))
    cache = Path(config["paths"]["interim"])/"expK"/code[:18]
    manifest = ROOT/"run.json"
    old = load_json(manifest) if manifest.exists() else None
    if old and old["code_hash"] != code:
        raise ValueError("K inputs changed after its deadline was set")
    started = old["started_epoch"] if old else time.time()
    deadline = started+48*3600
    record = dict(status="running", code_hash=code, config_hash=digest, inputs=inputs, cache=cache.as_posix(),
                  started_epoch=started, deadline_hours=48, households=scope["households"])
    write_json(manifest, record)
    experiment = Experiment(config, scope, corpus, shells, grid, cache, code, deadline)
    pilot = experiment.pilot()
    if not pilot["passed"]:
        raise TimeoutError("The runtime pilot exceeds 48 hours even with 18 training shells")
    size = pilot["selected_training_shells"]
    active = shells[(shells["set"] != "train") | (shells["rank"] <= size)].copy()
    active.to_csv(ROOT/"active_shell_sets.csv", index=False)
    training = active[active["set"] == "train"].sort_values("rank")
    choices, bespoke = {}, []
    for household in scope["households"]:
        choices[household] = experiment.halving(household, training)
        _, data = experiment.search(household, grid[household], training.unit_key.tolist(), False, "bespoke_grid")
        bespoke.append(data)
    confirmed = experiment.confirm(choices, active)
    gate = export_results(config, digest, experiment, choices, active, confirmed, pd.concat(bespoke, ignore_index=True))
    elapsed = time.time()-started
    if elapsed > 48*3600:
        raise TimeoutError("K exceeded the reviewed wall-time limit")
    checked_inputs(inputs)
    write_json(manifest, {**record, "status": "complete", "elapsed_seconds": elapsed, "active_training_shells": size,
                          "completed_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds")})
    write_json(ROOT/"acceptance.json", dict(passed=True, code_hash=code, config_hash=digest, input_sha256=inputs,
               elapsed_seconds=elapsed, time_box_hours=48, active_training_shells=size, **gate))
    print(f"Completed reduced K with {gate['audited_layouts']} independently validated layouts")


def main():
    parser = prepare_cli(__doc__)
    parser.add_argument("--prepare", action="store_true")
    parser.add_argument("--wait", action="store_true")
    args = parser.parse_args()
    cfg, digest, _ = start_run(args, "11b_run_expK")
    if args.dry_run:
        print("Run H1/H3 eight-candidate reduced kit design and transfer evaluation within 48 hours.")
        return
    scope = policy_config()
    ROOT.mkdir(parents=True, exist_ok=True)
    corpus = pd.read_parquet(Path(cfg["paths"]["processed"])/"corpus_units.parquet",
                             columns=["unit_key", "unit_json"]).set_index("unit_key")
    shells, grid = freeze(cfg, scope, corpus)
    if args.prepare:
        print(f"Froze {len(shells)} units and {sum(map(len, grid.values()))} household-specific kits")
        return
    with (ROOT/".run.lock").open("w") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX|fcntl.LOCK_NB)
        write_json(ROOT/"status.json", dict(status="waiting_for_C"))
        try:
            wait_for_c(args.wait)
            write_json(ROOT/"status.json", dict(status="running"))
            run(cfg, digest, scope, corpus, shells, grid)
            write_json(ROOT/"status.json", dict(status="complete"))
        except Exception as error:
            write_json(ROOT/"status.json", dict(status="failed", exception_type=type(error).__name__))
            raise


if __name__ == "__main__":
    main()
