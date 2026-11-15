"""Compare nine frozen furniture vectors with symmetric quality scoring."""

from datetime import datetime, timezone
import fcntl
from pathlib import Path
import time

import numpy as np
import pandas as pd
from tqdm import tqdm

from fea.config import config_hash
from fea.io import prepare_cli, start_run, write_json
from phase09_execution import apply_production, checked_inputs, cpu_slots, fingerprint, hash_inputs, load_json, run_weighted
from phase11_kit_design import BED, kit_configuration
from phase11_kit_jobs import run_kit_case
from phase11_kit_report import comparison
from phase11c_layouts import K, REVIEW, TOL, accepted, catalogue_dimensions, catalogue_qualities


ROOT = REVIEW / "kit"
CATALOGUE = REVIEW / "catalogue"
F1 = Path("results/expA_f1")


def catalogue_candidate(config: dict, household: str) -> dict:
    """Add the catalogue to each household's original six-dimensional grid."""
    values = catalogue_dimensions(config)
    variables = config["experiments"]["K_kit_design"]["variables"]
    dimensions = {key: values[key] for key, spec in variables.items()
                  if household in spec.get("applies_to", [household])}
    candidate = {"kit_id": "catalogue", "dimensions": dimensions}
    rebuilt, qualities = kit_configuration(config, household, candidate)
    if config_hash(config) != config_hash(rebuilt):
        raise ValueError("The catalogue vector changes the reference furniture configuration")
    actual = catalogue_qualities(config)
    if any(quality != actual[name] for name, quality in qualities.items()):
        raise ValueError("The catalogue vector and reference use different quality curves")
    return candidate


def select(config: dict, training: pd.DataFrame, grid: dict, old_search: pd.DataFrame,
           catalogue: pd.DataFrame) -> tuple[dict, pd.DataFrame]:
    """Rank each original vector and the catalogue on the same training shells."""
    tau = config["experiments"]["adequacy_tau"]
    training_keys = set(training.unit_key)
    rows, selected = [], {}
    for household, designs in grid.items():
        add = catalogue_candidate(config, household)
        if len(designs) != 8 or any(d["dimensions"] == add["dimensions"] for d in designs):
            raise ValueError("The catalogue is not a distinct ninth vector")
        candidates = {d["kit_id"]: d for d in [*designs, add]}
        train = old_search[old_search.household.eq(household)]
        reference = catalogue[catalogue.household.eq(household) & catalogue["set"].eq("train")]
        outcomes = pd.concat([train, reference.assign(kit_id="catalogue")], ignore_index=True)
        if set(outcomes.kit_id) != set(candidates):
            raise ValueError("Training vector coverage differs")
        subset = []
        for kit_id, group in outcomes.groupby("kit_id", sort=True):
            if len(group) != len(training_keys) or set(group.unit_key) != training_keys or not group.validator_pass.all():
                raise ValueError("Incomplete matched training set")
            candidate = candidates[kit_id]
            _, quality = kit_configuration(config, household, candidate)
            mean_q = float(np.mean(list(quality.values())))
            subset.append({
                "household": household, "kit_id": kit_id, "n_shells": len(group),
                **candidate["dimensions"], "q_bed": quality[BED[household][0]],
                "q_desk": quality["fold_down_desk"], "q_table": quality["drop_leaf_table"],
                "mean_item_q": mean_q, "mean_fci": group.fci.mean(),
                "mean_fciq": group.fciq.mean(), "adequacy_share": (group.fciq >= tau - 1e-9).mean(),
                "evidence": "warm_started_catalogue_S2" if kit_id == "catalogue" else "accepted_K_S2_search",
            })
        ranked = pd.DataFrame(subset).sort_values(["mean_fciq", "kit_id"], ascending=[False, True])
        ranked["selection_rank"] = np.arange(1, len(ranked) + 1)
        ranked["fci_q_frontier"] = [
            not ((ranked.mean_fci.ge(r.mean_fci - TOL) & ranked.mean_item_q.ge(r.mean_item_q - TOL))
                 & (ranked.mean_fci.gt(r.mean_fci + TOL) | ranked.mean_item_q.gt(r.mean_item_q + TOL))).any()
            for r in ranked.itertuples(index=False)
        ]
        selected[household] = candidates[ranked.iloc[0].kit_id]
        rows.append(ranked)
    return selected, pd.concat(rows, ignore_index=True)


def reference_rows(rescored: pd.DataFrame, optimized: pd.DataFrame, gate: dict) -> pd.DataFrame:
    """Keep rescored S0/S1 and the improved S2 with explicit layout provenance."""
    static = rescored[rescored.strategy.ne("S2")].copy()
    static["layout_origin"] = "rescored_original_catalogue"
    static["layout_sha256"] = static.source_layout_sha256
    static["search_time_s"] = 0.
    dynamic = optimized.copy()
    dynamic["layout_origin"] = "quality_optimized_catalogue"
    if not dynamic.code_hash.eq(gate["code_hash"]).all():
        raise ValueError("Optimized catalogue uses another implementation")
    return pd.concat([static, dynamic], ignore_index=True).assign(condition="catalogue", kit_id="catalogue")


def confirm_new(config: dict, household: str, design: dict, shells: pd.DataFrame, corpus: pd.DataFrame,
                cache: Path, code: str, deadline: float) -> pd.DataFrame:
    """Run the original K confirmation chain for a newly selected non-catalogue vector."""
    production = load_json(F1 / "run.json")["production_settings"]
    base, _ = apply_production(config, production, 20.)
    cfg, qualities = kit_configuration(base, household, design)
    jobs = [{
        "task_key": fingerprint([row.unit_key, household, design["kit_id"], False, "confirm"])[:24],
        "unit_json": corpus.loc[row.unit_key, "unit_json"], "household": household,
        "kit_id": design["kit_id"], "config": cfg, "qualities": qualities, "flat": False, "mode": "confirm",
        "code_hash": code, "threads": cfg["solver"]["num_workers"], "cache": cache.as_posix(),
        "deadline_epoch": deadline,
    } for row in shells.itertuples(index=False)]
    rows = []
    for i, results in enumerate(tqdm(run_weighted(run_kit_case, jobs, cpu_slots()),
                                    total=len(jobs), desc=household + " confirm"), 1):
        rows.extend(results)
        if i % 5 == 0 or i == len(jobs):
            write_json(ROOT / "progress.json", {"status": "running", "stage": household, "done": i, "total": len(jobs)})
    frame = pd.DataFrame(rows).rename(columns={"own_search_time_s": "search_time_s"})
    return frame.merge(shells[["unit_key", "set", "rank"]], on="unit_key", validate="many_to_one").assign(
        condition="kit", layout_origin="review_selected_kit")


def run(config: dict, digest: str) -> None:
    """Publish the reviewed K comparisons using accepted and newly validated layouts."""
    began = time.perf_counter()
    catalogue_gate = accepted(CATALOGUE)
    k_gate = accepted(K)
    inputs = hash_inputs([
        Path(__file__).resolve().relative_to(Path.cwd()), Path("scripts/phase11c_layouts.py"), K / "acceptance.json", K / "run.json",
        CATALOGUE / "acceptance.json", F1 / "run.json", Path("scripts/phase09_execution.py"),
        *sorted(Path("scripts").glob("phase11_kit_*.py")), *sorted(Path("src/fea").rglob("*.py")),
    ])
    code = fingerprint({"config_hash": digest, "inputs": inputs})
    cache = Path(config["paths"]["interim"]) / "g3_review_kit" / code[:18]
    shells = pd.read_csv(K / "active_shell_sets.csv")
    training = shells[shells["set"].eq("train")]
    if shells["set"].value_counts().to_dict() != {"train": 30, "heldout": 15, "real": 15}:
        raise ValueError("The accepted K cohorts have changed")
    grid = load_json(K / "candidate_kits.json")
    original = load_json(K / "kit.yaml")["by_household"]
    cases = pd.read_csv(K / "cases.csv")
    search = cases[cases["mode"].eq("search") & ~cases.flat_quality & cases.strategy.eq("S2")
                   & cases.unit_key.isin(training.unit_key)]
    if len(search) != 480 or not search.code_hash.eq(k_gate["code_hash"]).all():
        raise ValueError("Original eight-vector training evidence differs")
    old = pd.read_csv(K / "confirmations.csv").rename(columns={"own_search_time_s": "search_time_s"})
    old = old.assign(layout_origin="accepted_original_K")
    rescored = pd.read_csv(CATALOGUE / "k_rescored.csv")
    optimized = pd.read_csv(CATALOGUE / "k_optimized.csv")
    if not catalogue_gate["config_hash"] == k_gate["config_hash"] == digest:
        raise ValueError("The catalogue scoring and K configurations differ")
    reference = reference_rows(rescored, optimized, catalogue_gate)
    selected, frontier = select(config, training, grid, search, optimized)
    write_json(ROOT / "selection.json", {
        "status": "selected_on_training_only", "config_hash": digest,
        "selected": {household: candidate["kit_id"] for household, candidate in selected.items()},
    })
    pieces = [reference, old[old.condition.eq("flat_quality")]]
    new_solves = 0
    corpus_path = Path(config["paths"]["processed"]) / "corpus_units.parquet"
    corpus = None
    for household, design in selected.items():
        kit_id = design["kit_id"]
        if kit_id == "catalogue":
            current = reference[reference.household.eq(household)].assign(condition="kit")
        elif kit_id == original[household]["kit"]["kit_id"]:
            current = old[old.household.eq(household) & old.condition.eq("kit")]
        else:
            if corpus is None:
                corpus = pd.read_parquet(corpus_path, columns=["unit_key", "unit_json"]).set_index("unit_key")
            current = confirm_new(config, household, design, shells, corpus, cache, code, time.time() + 48 * 3600)
            new_solves += len(current)
        pieces.append(current)
    confirmed = pd.concat(pieces, ignore_index=True)
    keys = ["unit_key", "household", "condition", "strategy"]
    if (len(confirmed) != 1080 or confirmed.duplicated(keys).any()
            or not confirmed.validator_pass.all() or (confirmed.fciq > confirmed.fci + TOL).any()):
        raise ValueError("Revised K confirmation coverage or validity differs")
    old_incumbents = old[old.condition.eq("kit") & old.strategy.eq("S2") & old["set"].eq("train")]
    bespoke = pd.concat([search, old_incumbents, optimized[optimized["set"].eq("train")].assign(kit_id="catalogue")],
                        ignore_index=True)
    rescored_arm = rescored.assign(condition="catalogue_rescored", kit_id="catalogue")
    outcomes, effects, best = comparison(config, pd.concat([confirmed, rescored_arm], ignore_index=True), bespoke)
    cat = reference[reference.strategy.eq("S2") & reference["set"].eq("train")]
    check = best.merge(cat, on=["unit_key", "household"], suffixes=("", "_catalogue"), validate="one_to_one")
    if len(check) != 60 or (check.fciq + TOL < check.fciq_catalogue).any():
        raise ValueError("Bespoke misses an optimized catalogue incumbent")
    sensitivity = pd.read_csv(K / "comparison.csv").assign(sensitivity="catalogue_credited_at_full_quality")
    designs = {}
    for household, design in selected.items():
        cfg, quality = kit_configuration(config, household, design)
        designs[household] = {
            "kit": {**design, "qualities": quality, "dimension_config_hash": config_hash(cfg)},
            "flat_quality": original[household]["flat_quality"],
        }
    frames = {
        "confirmations": confirmed.sort_values(keys), "comparison": outcomes,
        "form_time_effects": effects, "bespoke_choices": best, "design_frontier": frontier,
        "catalogue_full_quality_sensitivity": sensitivity,
    }
    outputs = []
    for name, frame in frames.items():
        path = ROOT / (name + ".csv")
        frame.assign(base_config_hash=digest).to_csv(path, index=False)
        outputs.append(path)
    kit = ROOT / "kit.yaml"
    write_json(kit, {"config_hash": digest, "selection": "review_nine_vector_training_ranking", "by_household": designs})
    outputs.extend([kit, ROOT / "selection.json"])
    checked_inputs(inputs)
    write_json(ROOT / "acceptance.json", {
        "passed": True, "code_hash": code, "config_hash": digest, "input_sha256": inputs,
        "outputs": hash_inputs(outputs), "cache": cache.as_posix(), "candidates_per_household": 9,
        "training_shells": 30, "heldout_shells": 15, "real_plans": 15, "confirmation_layouts": len(confirmed),
        "new_solves": new_solves, "bespoke_contains_catalogue_and_kit": True,
        "elapsed_seconds": time.perf_counter() - began,
        "completed_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    })
    write_json(ROOT / "progress.json", {"status": "complete"})


def main() -> None:
    """Reassess the selected kit on the accepted K scope."""
    args = prepare_cli(__doc__).parse_args()
    config, digest, _ = start_run(args, "11c_recheck_kit")
    if args.dry_run:
        print("Rank nine vectors on 30 frozen training shells and confirm the selected kit on the original cohorts.")
        return
    ROOT.mkdir(parents=True, exist_ok=True)
    with (ROOT / ".run.lock").open("w") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        try:
            run(config, digest)
        except Exception as error:
            write_json(ROOT / "progress.json", {"status": "failed", "error_type": type(error).__name__})
            raise


if __name__ == "__main__":
    main()
