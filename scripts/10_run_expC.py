"""Train and evaluate the four grouped, geometry-only surrogate families."""
from datetime import datetime, timezone
from pathlib import Path
import fcntl
import platform
import time

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import spearmanr
from sklearn import __version__ as sklearn_version
from tqdm import tqdm

from fea.io import prepare_cli, sha256_file, start_run, write_json
from phase07_corrected import load_corrected
from phase09_execution import checked_inputs, hash_inputs, load_json
from phase10_features import extract_geometry, split_groups, targets, NODE_NAMES, GLOBAL_NAMES
from phase10_models import MODELS, TARGETS, fit_tabular, fit_graph, timed_prediction

ROOT = Path("results/expC")
ABLATIONS = Path("results/ablations/report_acceptance.json")
TEST_SETS = ("D1_test", "D2_external", "D3_external")


def model_metrics(y_true, prediction):
    """Keep non-identification explicit for constant or missing target samples."""
    ok = np.isfinite(y_true)
    n = int(ok.sum())
    if not n:
        return dict(n_evaluated=0, mae=None, rmse=None, r2=None, spearman=None, rank_status="no_identified_labels")
    truth, predicted = y_true[ok], prediction[ok]
    error = predicted-truth
    ss = float(np.sum((truth-truth.mean())**2))
    rank_ok = n > 1 and np.ptp(truth) > 1e-10 and np.ptp(predicted) > 1e-10
    return dict(n_evaluated=n, mae=float(np.mean(np.abs(error))), rmse=float(np.sqrt(np.mean(error**2))),
                r2=1-float(np.sum(error**2))/ss if n > 1 and ss > 1e-14 else None,
                spearman=float(spearmanr(truth, predicted).statistic) if rank_ok else None,
                rank_status="identified" if rank_ok else "constant_or_insufficient")


def evaluate(models, frame, households):
    metric_rows, predictions = [], []
    for split in TEST_SETS:
        cohort = frame[frame.split == split]
        for household in households:
            block = cohort[cohort.household == household].reset_index(drop=True)
            estimates = {name: timed_prediction(model, block) for name, model in models.items()}
            for j, target in enumerate(TARGETS):
                truth = block[target].to_numpy()
                vals = block[["unit_key", "source", "household", "group_id", "nia_m2"]].copy()
                vals["test_set"], vals["target"], vals["y_true"] = split, target, truth
                vals["label_status"] = np.where(np.isfinite(truth), "identified", "lower_bound_only")
                vals["y_lower_bound"] = block.saving_lower_bound_m2 if target == "saving_m2" else np.nan
                for name, (est, ms) in estimates.items():
                    prediction = est[:, j]
                    if not np.isfinite(prediction).all():
                        raise ValueError("Nonfinite surrogate prediction")
                    vals["y_pred_"+name] = prediction
                    row = model_metrics(truth, prediction)
                    bounded = ~np.isfinite(truth)
                    violations = int((prediction[bounded]+1e-9 < vals.y_lower_bound.to_numpy()[bounded]).sum())
                    metric_rows.append(dict(model=name, target=target, household=household, test_set=split,
                                            n_total=len(block), n_bound_only=int(bounded.sum()),
                                            n_bound_violations=violations, infer_ms_per_unit=ms, **row))
                predictions.append(vals)
    return pd.DataFrame(metric_rows), pd.concat(predictions, ignore_index=True)


def parity(predictions, output):
    fig, axes = plt.subplots(3, 4, figsize=(13, 10), layout="constrained")
    colors = {"D1_test": "#156ea0", "D2_external": "#c16439", "D3_external": "#2b8a6d"}
    for i, target in enumerate(TARGETS):
        rows = predictions[(predictions.target == target) & predictions.y_true.notna()]
        lo = 0.
        columns = ["y_true", *["y_pred_"+m for m in MODELS]]
        high = 1. if i < 2 else max(1., float(rows[columns].max().max())*1.03)
        for j, model in enumerate(MODELS):
            ax = axes[i, j]
            ax.plot([lo, high], [lo, high], color="0.6", lw=.7)
            for name, block in rows.groupby("test_set"):
                ax.scatter(block.y_true, block["y_pred_"+model], label=name, s=8, alpha=.30,
                           color=colors[name], linewidths=0, rasterized=True)
            ax.set(xlim=(lo, high), ylim=(lo, high), xlabel="Validated label",
                   ylabel=TARGETS[i]+" prediction" if j == 0 else "")
            if i == 0:
                ax.set_title(model.replace("_", " "))
            if i == 0 and j == 0:
                ax.legend(fontsize=8, loc="upper left")
    fig.suptitle("F8  Surrogate predictions on held-out groups and external sources\n"
                 "Area-gain panels use identified labels under the D1 training reference", fontsize=12)
    output.parent.mkdir(parents=True, exist_ok=True)
    for extension in ("png", "pdf"):
        fig.savefig(output.with_suffix("."+extension), dpi=200, bbox_inches="tight")
    plt.close(fig)


def wait_for_ablations(wait):
    while not ABLATIONS.exists():
        if not wait:
            raise ValueError("The ablation report is incomplete")
        for name in ("g3_ablations", "g3_ablations_report"):
            path = Path(".tmp")/(name+"_pipeline.json")
            if path.exists() and load_json(path)["status"] == "failed":
                raise ValueError("Ablation execution or report failed")
        time.sleep(30)
    gate = load_json(ABLATIONS)
    if not gate["passed"]:
        raise ValueError("Ablation report did not pass")
    checked_inputs(gate["input_sha256"])
    checked_inputs(gate["outputs"])


def run(config, digest):
    import torch
    torch.set_num_threads(4)
    torch.set_num_interop_threads(1)
    torch.use_deterministic_algorithms(True)
    began = time.perf_counter()
    corrected, _ = load_corrected(config)
    corpus_path = Path(config["paths"]["processed"])/"corpus_units.parquet"
    inputs = hash_inputs([ABLATIONS, "results/expA_f1/solutions.csv", "results/expA_f1/acceptance.json",
                          corpus_path, "scripts/10_run_expC.py", "scripts/phase10_features.py", "scripts/phase10_models.py",
                          "scripts/phase07_p1_area.py", "scripts/phase07_paired_area.py", "scripts/phase07_statistics.py"])
    corpus = pd.read_parquet(corpus_path, columns=["unit_key", "unit_json"])
    corpus = corpus[corpus.unit_key.isin(corrected.unit_key)].sort_values("unit_key")
    if len(corpus) != corrected.unit_key.nunique():
        raise ValueError("C geometry membership differs from the accepted F1 sample")
    tolerance = config["raster"]["resolution_m"]/2
    features = [extract_geometry(v, tolerance) for v in tqdm(corpus.unit_json, desc="Plan graphs")]
    cfg = config["experiments"]["C_surrogate"]
    if tuple(cfg["models"]) != MODELS or tuple(cfg["targets"]) != TARGETS:
        raise ValueError("Unexpected surrogate model or target specification")
    split = split_groups(features, cfg["split"], config["seed"])
    labelled, curves = targets(corrected, split)
    split["config_hash"] = digest
    split.to_csv(ROOT/"splits.csv", index=False)
    curves["config_hash"] = digest
    curves.to_csv(ROOT/"training_area_reference.csv", index=False)
    train, val = labelled[labelled.split == "train"], labelled[labelled.split == "val"]
    features = {f.unit_key: f for f in features}
    households = config["households"]["main_households"]
    fits, trials = fit_tabular(train, val, features, households, config["seed"])
    weights = ROOT/"models"/"graphsage.pt"
    weights.parent.mkdir(parents=True, exist_ok=True)
    graph, neural_trials = fit_graph(train, val, features, households, config["seed"], torch, weights)
    if weights.stat().st_size >= 50_000_000:
        raise ValueError("GNN weights exceed publication limit")
    fits["gnn_graph"] = graph
    metrics, predictions = evaluate(fits, labelled, households)
    if len(metrics) != len(TEST_SETS)*len(households)*len(TARGETS)*len(MODELS):
        raise ValueError("C metrics incomplete")
    expected = labelled.split.isin(TEST_SETS).sum()*len(TARGETS)
    if len(predictions) != expected or predictions.duplicated(["unit_key", "household", "target"]).any():
        raise ValueError("C predictions do not match test membership")
    for name, table in [("metrics", metrics), ("predictions", predictions),
                        ("tuning", pd.DataFrame(trials+neural_trials))]:
        table["config_hash"] = digest
        table.to_csv(ROOT/(name+".csv"), index=False)
    figure = Path("results/figures/F8")
    parity(predictions, figure)
    counts = split.groupby("split").agg(units=("unit_key", "nunique"), groups=("group_id", "nunique")).reset_index()
    labels = metrics[(metrics.model == "gnn_graph") & (metrics.target == "saving_m2")]
    aggregate = metrics.groupby(["test_set", "target", "model"], as_index=False).agg(
        mean_household_mae=("mae", "mean"), mean_household_spearman=("spearman", "mean"))
    elapsed = time.perf_counter()-began
    report = Path("reports/phase_10_C_results.md")
    report.write_text("\n".join([
        "# Phase 10 — Grouped surrogate results", "",
        "Geometry features and adjacency derive from interior polygon components and openings. "
        "The household indicator is the only non-geometric feature. D1 site/group IDs are exclusive to one split. "
        "D2 and generated D3 shells remain external tests.", "", counts.to_markdown(index=False), "",
        "## Held-out metrics", "", aggregate.to_markdown(index=False, floatfmt=".5f"), "",
        "The table averages the four household metrics within each test set. Full metrics and exact denominators are in metrics.csv. "
        "Inference time is median repeated prediction time per feature-ready unit for the three targets together, measured separately within each household and test set.", "",
        "## Equivalent-area target support", "",
        labels[["test_set", "household", "n_total", "n_evaluated", "n_bound_only", "n_bound_violations"]].to_markdown(index=False), "",
        "The P1 static ruler is fitted to D1 training groups and applied consistently to all splits. "
        "Point errors use identified labels. Lower-bound cases retain a prediction and a bound-violation count. "
        "Source shifts and sparse positive, identified area gains limit the scope of these comparisons.", "",
        "## Reproduction", "",
        f"Training, evaluation and figure export took {elapsed:.3f} seconds. "
        "Run scripts/10_run_expC.py with the accepted phase-9 evidence and the reported software versions.", "",
    ]), encoding="utf-8")
    checked_inputs(inputs)
    output_paths = [ROOT/(n+".csv") for n in ("splits", "training_area_reference", "tuning", "metrics", "predictions")]
    output_paths += [weights, figure.with_suffix(".png"), figure.with_suffix(".pdf"), report]
    write_json(ROOT/"acceptance.json", dict(
        passed=True, numerical_checks_passed=True, config_hash=digest, input_sha256=inputs,
        outputs=hash_inputs(output_paths), geometry_only=True, split_by="D1 group_id",
        models=list(MODELS), targets=list(TARGETS), test_sets=list(TEST_SETS),
        label_reference="D1 train groups, P1 median bin curve", node_features=list(NODE_NAMES),
        graph_global_features=list(GLOBAL_NAMES), adjacency_tolerance_m=tolerance,
        software=dict(python=platform.python_version(), sklearn=sklearn_version, torch=str(torch.__version__)),
        metric_rows=len(metrics), prediction_rows=len(predictions), elapsed_seconds=elapsed,
        completed_at_utc=datetime.now(timezone.utc).isoformat(timespec="seconds"),
    ))
    print(f"Passed C with {len(metrics)} metric rows and {len(predictions)} prediction rows")


def main():
    parser = prepare_cli(__doc__)
    parser.add_argument("--wait", action="store_true")
    args = parser.parse_args()
    cfg, digest, _ = start_run(args, "10_run_expC")
    if args.dry_run:
        print("Would train four models on grouped D1 splits and evaluate D1/D2/D3.")
        return
    ROOT.mkdir(parents=True, exist_ok=True)
    with (ROOT/".run.lock").open("w") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX|fcntl.LOCK_NB)
        write_json(ROOT/"status.json", dict(status="waiting_for_ablations"))
        try:
            wait_for_ablations(args.wait)
            write_json(ROOT/"status.json", dict(status="running"))
            run(cfg, digest)
            write_json(ROOT/"status.json", dict(status="complete"))
        except Exception as error:
            write_json(ROOT/"status.json", dict(status="failed", exception_type=type(error).__name__))
            raise


if __name__ == "__main__":
    main()
