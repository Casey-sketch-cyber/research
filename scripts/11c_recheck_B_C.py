"""Add the production reference in B and a post-hoc adequacy AUC in C."""

from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score

from fea.io import prepare_cli, sha256_file, start_run, write_json
from phase09_execution import checked_inputs, hash_inputs, load_json


ROOT = Path("results/g3_review/benchmark")
B = Path("results/expB")
C = Path("results/expC")
A = Path("results/expA_f1")
KEYS = ["unit_key", "household"]
FRESH = ["cp_sat", "greedy_footprint", "simulated_annealing"]
PRODUCTION = "production_pipeline"
TOL = 1e-9


def production_comparison() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, dict]:
    """Join the exact B sample to accepted production scores and triplet timings."""
    gate = load_json(B / "report_acceptance.json")
    corrected_gate = load_json(A / "acceptance.json")
    if not gate["passed"] or not corrected_gate["passed"]:
        raise ValueError("B or corrected A lacks acceptance")
    checked_inputs({
        (B / "cases.csv").as_posix(): gate["cases_sha256"],
        (A / "solutions.csv").as_posix(): corrected_gate["combined_sha256"],
    })
    cases = pd.read_csv(B / "cases.csv")
    reference = pd.read_csv(B / "corrected_main_reference.csv")
    pairs = cases.pivot(index=KEYS, columns="algorithm", values="fci_validator")
    if len(pairs) != 200 or set(pairs) != set(FRESH) or pairs.isna().any().any():
        raise ValueError("Expected 200 matched pairs for all three standalone arms")
    corrected = pd.read_csv(A / "solutions.csv", low_memory=False).merge(
        pairs.reset_index()[KEYS], on=KEYS, validate="many_to_one")
    metadata = corrected[corrected.strategy.eq("S2")][
        KEYS + ["source", "nia_m2", "fci_validator", "result_origin", "config_hash", "code_hash"]]
    validated = metadata.merge(reference, on=KEYS, validate="one_to_one", suffixes=("", "_reference"))
    if len(validated) != 200 or not np.allclose(validated.fci_validator, validated.fci_validator_reference, rtol=0, atol=TOL):
        raise ValueError("The matched production scores differ from the frozen B reference")
    for column in ("result_origin", "config_hash", "code_hash"):
        if not validated[column].eq(validated[column + "_reference"]).all():
            raise ValueError(f"Production reference provenance differs for {column}")
    times = corrected.pivot(index=KEYS, columns="strategy", values="solve_time_s")
    if list(times) != ["S0", "S1", "S2"] or len(times) != 200 or not np.isfinite(times).all().all() or (times < 0).any().any():
        raise ValueError("Production triplet timings are incomplete")
    if not corrected.validator_pass.all() or not cases.validator_pass.all():
        raise ValueError("The reviewed benchmark contains invalid cases")
    times = times.rename(columns={s: f"{s.lower()}_solve_time_s" for s in times})
    joined = (metadata.set_index(KEYS).rename(columns={"fci_validator": PRODUCTION})
              .join(pairs, validate="one_to_one").join(times, validate="one_to_one").reset_index())
    joined["production_solve_time_sum_s"] = joined[list(times)].sum(axis=1)
    joined["best_observed_fci"] = joined[FRESH + [PRODUCTION]].max(axis=1)
    joined["production_shortfall"] = joined.best_observed_fci - joined[PRODUCTION]
    joined["best_fresh_algorithm"] = joined[FRESH].idxmax(axis=1)
    for arm in FRESH:
        joined["production_minus_" + arm] = joined[PRODUCTION] - joined[arm]
    gaps = joined[joined.production_shortfall > TOL].sort_values(["production_shortfall", *KEYS],
                                                                ascending=[False, True, True])
    summary = cases.groupby("algorithm").agg(
        n_pairs=("fci_validator", "size"), validity_rate=("validator_pass", "mean"),
        mean_fci=("fci_validator", "mean"), median_fci=("fci_validator", "median"),
        mean_time_s=("elapsed_time_s", "mean"), median_time_s=("elapsed_time_s", "median"),
    ).reset_index()
    summary["timing_basis"] = "standalone S2 elapsed including preparation and validation"
    production = pd.DataFrame([{
        "algorithm": PRODUCTION, "n_pairs": len(joined), "validity_rate": 1.,
        "mean_fci": joined[PRODUCTION].mean(), "median_fci": joined[PRODUCTION].median(),
        "mean_time_s": joined.production_solve_time_sum_s.mean(),
        "median_time_s": joined.production_solve_time_sum_s.median(),
        "timing_basis": "accepted production S0 + S1 + S2 recorded solve time",
    }])
    audit = {
        "pairs": len(joined), "production_at_best_observed": int((joined.production_shortfall <= TOL).sum()),
        "production_at_or_above_annealing": int((joined.production_minus_simulated_annealing >= -TOL).sum()),
        "production_shortfall_pairs": len(gaps), "mean_shortfall_all_pairs": float(joined.production_shortfall.mean()),
        "largest_shortfall": float(joined.production_shortfall.max()),
    }
    return joined, pd.concat([summary, production], ignore_index=True), gaps, audit


def paired_effects(pairs: pd.DataFrame, config: dict) -> pd.DataFrame:
    """Use B's physical-unit, within-source bootstrap on the matched differences."""
    options = config["experiments"]["bootstrap"]
    rng = np.random.default_rng(config["seed"])
    clusters = [[g.index.to_numpy() for _, g in subset.groupby("unit_key")]
                for _, subset in pairs.groupby("source")]
    differences = pairs[["production_minus_" + arm for arm in FRESH]].to_numpy()
    draws = []
    for _ in range(options["n"]):
        sampled = np.concatenate([group[i] for group in clusters
                                  for i in rng.integers(len(group), size=len(group))])
        draws.append(differences[sampled].mean(axis=0))
    alpha = (1 - options["ci"]) / 2
    low, high = np.quantile(draws, [alpha, 1 - alpha], axis=0)
    return pd.DataFrame([{
        "comparison": "production minus " + arm, "n_pairs": len(pairs),
        "mean_difference": float(differences[:, i].mean()), "ci_lo": low[i], "ci_hi": high[i],
        "n_better": int((differences[:, i] > TOL).sum()), "n_worse": int((differences[:, i] < -TOL).sum()),
        "n_equal": int((np.abs(differences[:, i]) <= TOL).sum()), "bootstrap_resamples": options["n"],
    } for i, arm in enumerate(FRESH)])


def adequacy_auc(config: dict) -> pd.DataFrame:
    """Use the frozen continuous predictions for a secondary binary ranking check."""
    gate = load_json(C / "acceptance.json")
    source = C / "predictions.csv"
    if not gate["passed"] or sha256_file(source) != gate["outputs"][source.as_posix()]:
        raise ValueError("C predictions differ from accepted evidence")
    frame = pd.read_csv(source)
    tau = config["experiments"]["adequacy_tau"]
    frame = frame[frame.target.isin(["fci_S0", "fci_S2"])]
    rows = []
    for (split, household, target), part in frame.groupby(["test_set", "household", "target"]):
        adequate = part.y_true >= tau - TOL
        status = "identified" if adequate.nunique() == 2 else "one_outcome_class"
        for model in gate["models"]:
            scores = part["y_pred_" + model]
            if not np.isfinite(scores).all() or not np.isfinite(part.y_true).all():
                raise ValueError("Nonfinite C predictions or labels")
            rows.append({
                "test_set": split, "household": household, "target": target, "model": model,
                "roc_auc": roc_auc_score(adequate, scores) if status == "identified" else None,
                "status": status, "n": len(part), "n_adequate": int(adequate.sum()),
                "n_at_full_fci": int(np.isclose(part.y_true, 1., atol=TOL, rtol=0).sum()), "tau": tau,
            })
    return pd.DataFrame(rows)


def main() -> None:
    """Generate the review tables with hashes of the original accepted inputs."""
    args = prepare_cli(__doc__).parse_args()
    config, digest, _ = start_run(args, "11c_recheck_B_C")
    if args.dry_run:
        print("Join the original 200 B pairs and score adequacy AUC from accepted C predictions.")
        return
    inputs = hash_inputs([Path(__file__).resolve().relative_to(Path.cwd()), B / "report_acceptance.json", B / "cases.csv",
                          B / "corrected_main_reference.csv", A / "acceptance.json", A / "solutions.csv",
                          C / "acceptance.json", C / "predictions.csv"])
    pairs, summary, gaps, audit = production_comparison()
    effects = paired_effects(pairs, config)
    auc = adequacy_auc(config)
    ROOT.mkdir(parents=True, exist_ok=True)
    frames = {"production_pairs": pairs, "algorithm_summary": summary, "production_shortfalls": gaps,
              "production_paired_effects": effects, "c_adequacy_auc": auc}
    outputs = []
    for name, frame in frames.items():
        path = ROOT / (name + ".csv")
        frame.assign(base_config_hash=digest).to_csv(path, index=False)
        outputs.append(path)
    checked_inputs(inputs)
    write_json(ROOT / "acceptance.json", {
        "passed": True, "config_hash": digest, "input_sha256": inputs, "outputs": hash_inputs(outputs),
        "production": audit, "auc_rows": len(auc),
        "completed_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    })
    print(audit)


if __name__ == "__main__":
    main()
