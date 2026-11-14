"""Rescore the saved K and Hong Kong catalogue layouts and reoptimize K S2."""

from copy import deepcopy
from datetime import datetime, timezone
import fcntl
import json
from pathlib import Path
import time

import numpy as np
import pandas as pd
from tqdm import tqdm

from fea.data.d3_shells import load_d3
from fea.geometry.normalize import normalize
from fea.io import prepare_cli, start_run, write_json
from phase07_corrected import load_corrected
from phase09_execution import apply_production, checked_inputs, cpu_slots, fingerprint, hash_inputs, load_json, run_weighted
from phase11c_layouts import HK, K, REVIEW, STRATEGIES, accepted, catalogue_dimensions, catalogue_qualities, run_catalogue_job


ROOT = REVIEW / "catalogue"
F1 = Path("results/expA_f1")
ORIGINAL = Path("results/expA")


def saved_k_references() -> tuple[dict, pd.DataFrame]:
    """Locate the catalogue confirmation triplets frozen in the original K."""
    gate = accepted(K)
    run = load_json(K / "run.json")
    if run["status"] != "complete" or gate["code_hash"] != run["code_hash"]:
        raise ValueError("Original K run and acceptance differ")
    shells = pd.read_csv(K / "active_shell_sets.csv")
    if shells["set"].value_counts().to_dict() != {"train": 30, "heldout": 15, "real": 15}:
        raise ValueError("Unexpected K cohorts")
    confirmed = pd.read_csv(K / "confirmations.csv")
    catalogue = confirmed[confirmed.condition.eq("catalogue")].copy()
    if len(catalogue) != 360 or not catalogue.code_hash.eq(gate["code_hash"]).all():
        raise ValueError("The frozen K catalogue evidence is incomplete")
    catalogue["path"] = [str(Path(run["cache"]) / task / (strategy + ".json"))
                         for task, strategy in zip(catalogue.task_key, catalogue.strategy)]
    return split_references(catalogue), shells


def split_references(frame: pd.DataFrame) -> dict:
    """Index one complete saved triplet per unit and household."""
    output = {}
    for key, group in frame.groupby(["unit_key", "household"], sort=True):
        if len(group) != 3 or set(group.strategy) != set(STRATEGIES):
            raise ValueError("Saved catalogue strategy coverage differs")
        output[key] = {row["strategy"]: row for row in group.to_dict("records")}
    return output


def saved_hk_references(config: dict, corpus: pd.DataFrame) -> tuple[dict, pd.DataFrame]:
    """Resolve all 3,510 original HK catalogue layouts with their evidence."""
    gate = accepted(HK)
    run = load_json(HK / "run.json")
    if run["status"] != "complete" or run["code_hash"] != gate["code_hash"]:
        raise ValueError("Original HK run and acceptance differ")
    shells = pd.read_csv(HK / "shells.csv")
    scenario = pd.read_csv(HK / "cases.csv")
    households = config["hk_scenario"]["households"]
    if (len(shells) != 390 or not shells.evaluable.all() or len(scenario) != 4290
            or shells.groupby("area_m2").size().to_dict() != {a: 30 for a in range(8, 21)}):
        raise ValueError("The frozen HK grid is incomplete")
    corrected, _ = load_corrected(config)
    original = corrected[corrected.unit_key.isin(shells.unit_key) & corrected.household.isin(households)].copy()
    original["fci"] = original["fci_validator"]
    old_root = Path(load_json(ORIGINAL / "run.json")["cache"])
    fixed_root = Path(load_json(F1 / "run.json")["cache"])
    original["path"] = [
        str((old_root if origin == "original_A_H1H2_verified_unaffected" else fixed_root)
            / budget / "shared" / file)
        for origin, budget, file in zip(original.result_origin, original.budget_group, original.layout_file)
    ]
    extension = deepcopy(config)
    extension["shells_D3"]["areas_m2"] = [17, 19]
    units = {u.unit_key: json.dumps(u.to_dict()) for u in map(normalize, load_d3(extension))}
    missing = shells.loc[shells.origin.eq("integer_size_completion"), "unit_key"]
    if set(units) != set(missing):
        raise ValueError("Regenerated missing-size shell identities differ")
    additions = []
    for unit_key in sorted(units):
        corpus.loc[unit_key, "unit_json"] = units[unit_key]
        for household in households:
            task_key = fingerprint([unit_key, household, "catalogue"])[:24]
            cache = Path(run["cache"]) / "catalogue" / task_key
            record = load_json(cache / "record.json")
            if record["fingerprint"] != gate["code_hash"]:
                raise ValueError("Saved missing-size checkpoint differs")
            for row in record["rows"]:
                filename = row["strategy"] + ".json"
                if row["layout_sha256"] != record["layouts"][filename]:
                    raise ValueError("Saved missing-size digest differs")
                additions.append({**row, "path": str(cache / filename), "fci": row["fci_validator"]})
    references = pd.concat([original, pd.DataFrame(additions)], ignore_index=True)
    keys = ["unit_key", "household", "strategy"]
    evidence = scenario[scenario.strategy.isin(STRATEGIES)]
    matched = references.merge(evidence, on=keys, validate="one_to_one", suffixes=("", "_accepted"))
    if len(matched) != len(references) or len(matched) != len(evidence) or len(matched) != 3510:
        raise ValueError("Saved catalogue cases differ from the accepted scenario")
    for key in ("fci", "tb"):
        if not np.allclose(matched[key], matched[key + "_accepted"], rtol=0, atol=1e-8):
            raise ValueError("Saved catalogue scores differ from the scenario")
    for key in ("config_hash", "code_hash"):
        if not matched[key].eq(matched[key + "_accepted"]).all():
            raise ValueError("Saved catalogue provenance differs from the scenario")
    references["layout_sha256"] = references.layout_sha256.fillna("")
    return split_references(references), shells


def jobs_for(config: dict, corpus: pd.DataFrame, references: dict, cache: Path, code: str, optimize: bool) -> list:
    """Keep the 120 s, four-worker and 0.10 m small-home settings."""
    production = load_json(F1 / "run.json")["production_settings"]
    settings = production["small"]
    if tuple(settings[k] for k in ("time_limit_s", "num_workers", "anchor_stride_m")) != (120, 4, .1):
        raise ValueError("The reviewed solve budget changed")
    cfg, _ = apply_production(config, production, 20.)
    qualities = catalogue_qualities(cfg)
    jobs = []
    for (unit, household), records in references.items():
        jobs.append({
            "task_key": fingerprint([unit, household, "catalogue"])[:24], "cache": str(cache),
            "code_hash": code, "household": household, "unit_json": corpus.loc[unit, "unit_json"],
            "references": records, "qualities": qualities, "config": cfg,
            "threads": cfg["solver"]["num_workers"] if optimize else 1, "optimize": optimize,
        })
    return jobs


def evaluate(jobs: list, stage: str) -> list:
    """Resume completed cases and update the progress record."""
    output = []
    for i, result in enumerate(tqdm(run_weighted(run_catalogue_job, jobs, cpu_slots()),
                                   total=len(jobs), desc=stage), 1):
        output.append(result)
        if i % 5 == 0 or i == len(jobs):
            write_json(ROOT / "progress.json", {"status": "running", "stage": stage, "done": i, "total": len(jobs)})
    return output


def run(config: dict, digest: str) -> None:
    """Complete both catalogue cohorts against the accepted original evidence."""
    began = time.perf_counter()
    corpus_path = Path(config["paths"]["processed"]) / "corpus_units.parquet"
    inputs = hash_inputs([
        Path(__file__).resolve().relative_to(Path.cwd()), Path("scripts/phase11c_layouts.py"), Path("scripts/phase09_execution.py"),
        Path("scripts/phase11_kit_solver.py"), Path("scripts/phase11_kit_validator.py"),
        K / "acceptance.json", K / "run.json", HK / "acceptance.json", HK / "run.json",
        F1 / "acceptance.json", F1 / "run.json", ORIGINAL / "run.json", corpus_path,
        *sorted(Path("src/fea").rglob("*.py")),
    ])
    code = fingerprint({"config_hash": digest, "inputs": inputs})
    cache = Path(config["paths"]["interim"]) / "g3_review_catalogue" / code[:18]
    corpus = pd.read_parquet(corpus_path, columns=["unit_key", "unit_json"]).set_index("unit_key")
    refs, shells = saved_k_references()
    if len(refs) != 120:
        raise ValueError("Expected 120 K catalogue pairs")
    hk_refs, hk_shells = saved_hk_references(config, corpus)
    hk = evaluate(jobs_for(config, corpus, hk_refs, cache / "HK", code, False), "HK_catalogue_rescore")
    k = evaluate(jobs_for(config, corpus, refs, cache / "K", code, True), "K_catalogue_reoptimize")
    k_rescored = pd.DataFrame(row for record in k for row in record["rescored"])
    k_optimized = pd.DataFrame(record["optimized"] for record in k)
    hk_rescored = pd.DataFrame(row for record in hk for row in record["rescored"])
    outputs = []
    for name, data, keys in (
        ("k_rescored", k_rescored, ["unit_key", "household", "strategy"]),
        ("k_optimized", k_optimized, ["unit_key", "household"]),
        ("hk_rescored", hk_rescored, ["unit_key", "household", "strategy"]),
    ):
        if data.duplicated(keys).any() or not data.validator_pass.all():
            raise ValueError(f"Catalogue validation or coverage differs for {name}")
        data["base_config_hash"] = digest
        support = hk_shells[["unit_key", "nia_m2", "area_m2", "shape"]] if name.startswith("hk") else (
            shells[["unit_key", "source", "nia_m2", "set", "rank"]])
        path = ROOT / (name + ".csv")
        data.merge(support, on="unit_key", validate="many_to_one").sort_values(keys).to_csv(path, index=False)
        outputs.append(path)
    if (len(k_rescored), len(k_optimized), len(hk_rescored)) != (360, 120, 3510):
        raise ValueError("Incomplete catalogue evidence")
    checked_inputs(inputs)
    write_json(ROOT / "acceptance.json", {
        "passed": True, "config_hash": digest, "code_hash": code, "input_sha256": inputs,
        "outputs": hash_inputs(outputs), "cache": cache.as_posix(), "dimensions": catalogue_dimensions(config),
        "qualities": catalogue_qualities(config), "k_rescored": len(k_rescored), "k_optimized": len(k_optimized),
        "hk_rescored": len(hk_rescored), "elapsed_seconds": time.perf_counter() - began,
        "completed_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    })
    write_json(ROOT / "progress.json", {"status": "complete"})


def main() -> None:
    """Run the reviewed catalogue corrections with isolated checkpoints."""
    args = prepare_cli(__doc__).parse_args()
    config, digest, _ = start_run(args, "11c_rescore_catalogue")
    if args.dry_run:
        print("Rescore 360 K and 3,510 HK saved layouts, and reoptimize 120 K S2 layouts.")
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
