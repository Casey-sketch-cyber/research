"""Assemble and verify the K3 ranking, paired effects and Hong Kong addendum."""

from datetime import datetime, timezone
from hashlib import sha256
import importlib.util
from pathlib import Path
import subprocess

import pandas as pd
from tqdm import tqdm

from fea.config import config_hash
from fea.io import prepare_cli, sha256_file, start_run, write_json
from phase09_execution import apply_production, checked_inputs, fingerprint, hash_inputs, load_json


ROOT = Path("results/g3_review_k3")
K = Path("results/expK")
HK = Path("results/scenario_hk")
REVIEW = Path("results/g3_review")
PRODUCTION = Path("results/expA_f1/run.json")
BASE_MANIFEST = Path("results/g3/evidence_manifest.json")
ROUND2_COMMIT = "8d8a800876cde36a699d9d6517c7cfd94177aa71"
G3 = Path("reports/GATE_G3.md")
H3 = "H3_couple_one_remote"
H1 = "H1_single_commuter"


def driver(filename: str):
    """Load a numbered experiment entry point without running it."""
    path = Path("scripts") / filename
    spec = importlib.util.spec_from_file_location(path.stem, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def hk_kit_layouts(config: dict, corpus: pd.DataFrame, candidates: dict) -> pd.DataFrame:
    """Verify the accepted HK layouts for the requested dimensions and quality factors."""
    from phase11_kit_design import kit_configuration
    from phase11c_layouts import accepted, layout_inputs, read_scored_layout
    scenario = accepted(HK)
    run = load_json(HK / "run.json")
    choices = load_json(K / "kit.yaml")["by_household"]
    base, _ = apply_production(config, load_json(PRODUCTION)["production_settings"], 20.)
    _, shells = driver("11c_rescore_catalogue.py").saved_hk_references(config, corpus)
    source = pd.read_csv(HK / "cases.csv")
    rows = []
    for name, (design, strategy) in candidates.items():
        cfg, quality = kit_configuration(base, name, design)
        prior = choices[name]["kit"]
        if (prior["kit_id"] != design["kit_id"] or prior["dimensions"] != design["dimensions"]
                or prior["qualities"] != quality):
            raise ValueError("The approved HK kit and the candidate dimensions or qualities differ")
        reference = source[source.household.eq(name) & source.strategy.eq("S2_kit")]
        if (len(reference) != 390 or set(reference.unit_key) != set(shells.unit_key)
                or not reference.code_hash.eq(scenario["code_hash"]).all()):
            raise ValueError("Incomplete original HK kit scenario")
        for row in tqdm(reference.to_dict("records"), total=390, desc=f"Revalidate {name[:2]} HK kit"):
            unit_key = row["unit_key"]
            key = fingerprint([unit_key, name, design["kit_id"]])[:24]
            folder = Path(run["cache"]) / "kit" / key
            record = load_json(folder / "record.json")
            saved = record["rows"][0]
            if (record["code_hash"] != scenario["code_hash"] or saved["unit_key"] != unit_key
                    or saved["kit_id"] != design["kit_id"] or saved["household"] != name
                    or saved["layout_sha256"] != record["layouts"]["S2.json"]
                    or row["config_hash"] != config_hash(cfg)):
                raise ValueError("Prior HK kit checkpoint does not match the case")
            _, household, grid = layout_inputs({"config": cfg, "unit_json": corpus.loc[unit_key, "unit_json"], "household": name})
            _, checked, digest = read_scored_layout(
                {**row, "strategy": "S2", "path": str(folder / "S2.json"),
                 "layout_sha256": saved["layout_sha256"], "expected_fciq": row["fciq"]},
                grid, cfg, household, quality)
            rows.append({
                **row, "kit_id": design["kit_id"], "strategy": strategy, "fci": checked["fci"],
                "fciq": checked["fciq"], "validator_pass": True, "layout_sha256": digest,
                "evidence": "revalidated_original_HK_kit_layout",
            })
    return pd.DataFrame(rows)


def hong_kong(config: dict, alternatives: pd.DataFrame, selections: dict) -> tuple:
    """Attach the valid kit alternatives to the accepted scenario and calculate their crossings."""
    from phase11_hk_report import summarize
    from phase11c_layouts import accepted
    from phase11d_k3_analysis import OPTIMIZED, paired_rows

    scenario = REVIEW / "hong_kong"
    source = accepted(scenario)
    current = pd.read_csv(scenario / "cases.csv")
    if len(current) != 4290 or not current.validator_pass.all() or source["shells"] != 390:
        raise ValueError("Round-2 HK coverage differs")
    optimized = current[current.strategy.eq("S2_kit")]
    if len(optimized) != 780 or not optimized.kit_id.eq("catalogue").all():
        raise ValueError("The H3 optimized catalogue reference differs")
    tau = config["experiments"]["adequacy_tau"]
    pairs = [paired_rows(g, optimized, h, "hong_kong", tau, ("area_m2", "shape")).assign(kit_id=g.kit_id.iloc[0])
             for h, g in alternatives.groupby("household", sort=True)]
    mapping = alternatives.drop_duplicates("household").set_index("household")["strategy"].to_dict()
    selected_strategy = {h: OPTIMIZED if x["kit"]["kit_id"] == "catalogue" else mapping[h]
                         for h, x in selections.items()}
    for h, group in alternatives.groupby("household"):
        if group.strategy.nunique() != 1 or len(group) != 390:
            raise ValueError(f"Incomplete HK alternative for {h}")
    # Use the existing shape bootstrap with each alternative occupying the
    # fourth strategy column. The accepted catalogue summaries are carried over.
    alternate = pd.concat([
        current.loc[~(current.household.isin(mapping) & current.strategy.eq("S2_kit"))],
        alternatives.assign(strategy="S2_kit"),
    ], ignore_index=True)
    opts = config["experiments"]["bootstrap"]
    by_size, summary, _ = summarize(alternate, tau, opts["n"], opts["ci"], config["seed"])
    def append_strategy(name, addition):
        accepted_rows = pd.read_csv(scenario / (name + ".csv"))
        accepted_rows.loc[accepted_rows.strategy.eq("S2_kit"), "strategy"] = OPTIMIZED
        extra = addition[addition.household.isin(mapping) & addition.strategy.eq("S2_kit")].copy()
        extra["strategy"] = extra.household.map(mapping)
        extra = extra.replace({"percentile_unit_bootstrap": "percentile_shape_bootstrap"})
        combined = pd.concat([accepted_rows, extra], ignore_index=True)
        combined["selected_kit"] = combined.strategy.eq(combined.household.map(selected_strategy))
        return combined
    by_size = append_strategy("adequacy_by_size", by_size)
    summary = append_strategy("scenario_summary", summary)
    if len(by_size) != 13 * (11 + len(mapping)) or len(summary) != 11 + len(mapping):
        raise ValueError("The paired HK strategy coverage differs")
    pair = next(p for p in pairs if p.household.iloc[0] == H3)
    band_rows = []
    for lo, hi in [(8, 12), (13, 16), (17, 20)]:
        band = pair[pair.area_m2.between(lo, hi)]
        band_rows.append({
            "area_min_m2": lo, "area_max_m2": hi, "n_pairs": len(band),
            "kit_mean_fciq": band.kit_fciq.mean(), "catalogue_mean_fciq": band.catalogue_fciq.mean(),
            "kit_adequate": int(band.kit_adequate.sum()), "catalogue_adequate": int(band.catalogue_adequate.sum()),
        })
    return by_size, summary, pairs, pd.DataFrame(band_rows)


def report(config: dict, digest: str) -> None:
    """Produce K3 evidence without changing the prior numerical packages."""
    from phase11c_layouts import accepted
    from phase11d_k3_analysis import COMPACT, LARGER, catalogue_rule, k_pairs, paired_effect, training_vectors

    solve = accepted(ROOT, "solve_acceptance.json")
    if solve["config_hash"] != digest or solve["solves"] != 60:
        raise ValueError("The warm-start searches do not match the K3 review")
    catalogue_rule(config)
    accepted(REVIEW / "catalogue")
    original = driver("11d_run_k3.py")
    seeds, vectors, _ = original.saved_training()
    solves = pd.read_csv(ROOT / "warm_start_s2.csv")
    catalogue = pd.read_csv(REVIEW / "catalogue/k_optimized.csv")
    best, frontier, selections, bespoke = training_vectors(config, seeds, solves, catalogue, vectors, original.TRIALS)
    design = next(d for d in vectors[H3] if d["kit_id"] == original.TRIALS[H3])
    selected = selections[H3]["kit"]["kit_id"]
    if selected not in {"catalogue", design["kit_id"]}:
        raise ValueError("The selected H3 kit has no reviewed HK counterpart")
    candidates = {H3: (design, LARGER)}
    if selections[H1]["kit"]["kit_id"] != "catalogue":
        candidates[H1] = (selections[H1]["kit"], COMPACT)
    corpus_path = Path(config["paths"]["processed"]) / "corpus_units.parquet"
    inputs = hash_inputs([
        Path(__file__).resolve().relative_to(Path.cwd()), Path("scripts/phase11d_k3_analysis.py"),
        Path("scripts/phase11_hk_report.py"), Path("scripts/11c_rescore_catalogue.py"),
        Path("scripts/phase07_statistics.py"), Path("reviews/G3_review_round2.md"),
        ROOT / "solve_acceptance.json", K / "acceptance.json", K / "run.json", HK / "acceptance.json", HK / "run.json",
        REVIEW / "kit/acceptance.json", REVIEW / "catalogue/acceptance.json", REVIEW / "hong_kong/acceptance.json",
        BASE_MANIFEST, corpus_path,
    ])
    for path, value in solve["input_sha256"].items():
        if sha256_file(Path(path)) != value:
            raise ValueError(f"Source solve input changed for {path}")
    accepted(REVIEW / "kit")
    corpus = pd.read_parquet(corpus_path, columns=["unit_key", "unit_json"]).set_index("unit_key")
    alternatives = hk_kit_layouts(config, corpus, candidates)
    hk_sizes, hk_summary, hk_pairs, bands = hong_kong(config, alternatives, selections)
    pair_frames = [*k_pairs(config, best, catalogue, original.TRIALS, selections), *hk_pairs]
    opts = config["experiments"]["bootstrap"]
    effects = pd.DataFrame([paired_effect(frame, config["seed"], opts["n"], opts["ci"]) for frame in pair_frames])
    if (effects.cohort.eq("training_equal_effort").sum() != 2
            or len(effects[effects.household.eq(H3)]) != 5):
        raise ValueError("Unmatched K3 cohort comparison")
    frames = {
        "training_best": best, "design_frontier": frontier, "bespoke_choices": bespoke,
        "paired_cases": pd.concat(pair_frames, ignore_index=True), "paired_effects": effects,
        "hk_kit_cases": alternatives, "hk_adequacy_by_size": hk_sizes, "hk_scenario_summary": hk_summary,
        "hk_h3_size_bands": bands,
    }
    paths = []
    for name, frame in frames.items():
        path = ROOT / (name + ".csv")
        frame.assign(base_config_hash=digest).to_csv(path, index=False)
        paths.append(path)
    kit_path = ROOT / "kit.yaml"
    write_json(kit_path, {"config_hash": digest, "selection": "training_mean_fciq", "by_household": selections})
    paths.append(kit_path)
    checked_inputs(inputs)
    write_json(ROOT / "acceptance.json", {
        "passed": True, "config_hash": digest, "input_sha256": inputs, "outputs": hash_inputs(paths),
        "training_layouts": len(best), "revalidated_hk_layouts": len(alternatives),
        "revalidated_h3_layouts": int(alternatives.household.eq(H3).sum()), "new_hk_solves": 0,
        "selected": {h: row["kit"]["kit_id"] for h, row in selections.items()},
        "completed_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    })


def verify() -> None:
    """Check K3 evidence and the original round-2 package against its recorded bytes."""
    k3 = load_json(ROOT / "acceptance.json")
    solve = load_json(ROOT / "solve_acceptance.json")
    for gate in (solve, k3):
        if not gate["passed"]:
            raise ValueError("A K3 acceptance record did not pass")
        checked_inputs(gate["outputs"])
        checked_inputs({p: d for p, d in gate["input_sha256"].items() if p != "data/processed/corpus_units.parquet"})
    if solve["solves"] != 60 or k3["training_layouts"] != 540 or k3["revalidated_h3_layouts"] != 390:
        raise ValueError("K3 evidence scope differs")
    previous = load_json(BASE_MANIFEST)["files"]
    archived = subprocess.check_output(["git", "show", f"{ROUND2_COMMIT}:{G3.as_posix()}"])
    if sha256(archived).hexdigest() != previous[G3.as_posix()]:
        raise ValueError("Round-2 report digest differs")
    checked_inputs({p: d for p, d in previous.items() if p != G3.as_posix()})
    release = load_json(ROOT / "release_manifest.json")
    if not release["passed"]:
        raise ValueError("The K3 publication checks did not pass")
    checked_inputs(release["files"])
    tests = load_json(ROOT / "validation.json")
    if not tests["passed"] or tests["tests_passed"] < 185:
        raise ValueError("The K3 regression suite did not pass")
    checked_inputs(tests["tested_inputs"])
    figures = load_json(ROOT / "visual_review.json")
    if not figures["F12"]["passed"]:
        raise ValueError("The selected K3 dimension drawing was not verified")
    checked_inputs(figures["F12"]["files"])
    print(f"Verified {len(previous)} round-2 evidence files and {len(release['files'])} K3 publication files.")


def main() -> None:
    """Build the K3 addendum or verify its publication evidence."""
    parser = prepare_cli(__doc__)
    parser.add_argument("--verify", action="store_true")
    parser.add_argument("--draw-f12", action="store_true", help="Draw the selected K3 dimensions from accepted outputs.")
    args = parser.parse_args()
    config, digest, _ = start_run(args, "11d_report_k3")
    if args.dry_run:
        print("Rank nine vectors per household, report paired effects, and validate the larger H3 HK row.")
    elif args.verify:
        verify()
    elif args.draw_f12:
        from phase11c_layouts import accepted

        accepted(ROOT)
        driver("11_make_G3.py").draw_kit_release(
            Path.cwd(), (ROOT / "acceptance.json").as_posix(), ROOT / "kit.yaml", ROOT / "F12")
    else:
        report(config, digest)


if __name__ == "__main__":
    main()
