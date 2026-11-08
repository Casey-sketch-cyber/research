"""Freeze E1 evaluability and E3 exclusion-bias evidence without reading outcomes."""
import os
for _name in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ[_name] = "1"

from concurrent.futures import ProcessPoolExecutor
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd
from tqdm import tqdm

from fea.config import config_hash
from fea.geometry.unit import Unit
from fea.io import prepare_cli, sha256_file, start_run, write_json
from phase07_evaluability import RULE, evaluate_empty


def evaluate_job(job):
    serialized, resolution, max_gap, cache = job
    unit = Unit.from_dict(json.loads(serialized))
    path = Path(cache)/(unit.unit_key.replace(":", "_")+".json")
    if path.exists():
        return json.loads(path.read_text())
    record = evaluate_empty(unit, resolution, max_gap)
    write_json(path, record)
    return record


def bias_outputs(frame, root):
    """Compare composition without using any experimental outcome."""
    rows = []
    for source in ["all"]+sorted(frame.source.unique()):
        source_frame = frame if source == "all" else frame[frame.source == source]
        for included, group in source_frame.groupby("evaluable", sort=True):
            row = dict(source=source, group="retained" if included else "excluded", n_units=len(group),
                fraction_within_source=len(group)/len(source_frame),
                source_share_within_group=len(group)/int((frame.evaluable == included).sum()))
            for column in ("nia_m2", "n_rooms"):
                values = group[column]
                row.update({column+"_mean":float(values.mean()), column+"_median":float(values.median()),
                    column+"_q25":float(values.quantile(.25)), column+"_q75":float(values.quantile(.75)),
                    column+"_min":float(values.min()), column+"_max":float(values.max())})
            rows.append(row)
    summary = pd.DataFrame(rows)
    summary.to_csv(root/"exclusion_bias.csv", index=False)
    frame.groupby(["source", "evaluable", "n_rooms"]).size().rename("n_units").reset_index().to_csv(
        root/"exclusion_room_counts.csv", index=False)
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    sources = sorted(frame.source.unique())
    fig, axes = plt.subplots(2, len(sources), figsize=(13, 7), squeeze=False)
    for column, source in enumerate(sources):
        for included, colour in [(True, "#286c91"), (False, "#ba513d")]:
            group = frame[(frame.source == source) & (frame.evaluable == included)]
            if group.empty:
                continue
            label = f"{'Retained' if included else 'Excluded'} (n={len(group)})"
            axes[0, column].hist(group.nia_m2, bins=np.arange(8, 52.1, 2), density=True,
                histtype="step", lw=1.7, color=colour, label=label)
            axes[1, column].hist(group.n_rooms, bins=np.arange(-.5, frame.n_rooms.max()+1.6, 1),
                density=True, histtype="step", lw=1.7, color=colour, label=label)
        axes[0, column].set(title=source, xlabel="Net internal area (m²)", ylabel="Within-group density")
        axes[1, column].set(xlabel="Habitable room count", ylabel="Within-group proportion")
        axes[0, column].legend(fontsize=8)
    fig.suptitle("Empty-raster evaluability: retained and excluded composition")
    fig.tight_layout()
    for suffix in ("png", "pdf"):
        fig.savefig(root/("exclusion_bias."+suffix), dpi=300, bbox_inches="tight")
    plt.close(fig)
    return summary


def main():
    parser = prepare_cli(__doc__)
    parser.add_argument("--jobs", type=int, default=4)
    args = parser.parse_args()
    config, _, _ = start_run(args, "07_evaluability")
    if args.dry_run:
        print("Would evaluate all frozen units from empty geometry and report exclusion composition; no outcome files.")
        return
    if config["furniture"]["meta"]["walking_width"] != RULE["walking_width_m"]:
        raise ValueError("E1 is fixed at the reviewed main 0.60 m walking width")
    sample_path = Path("results/pilot/round3/expA_selected_sample.csv")
    sample = pd.read_csv(sample_path)
    if sample.unit_key.duplicated().any():
        raise ValueError("Duplicate frozen units")
    corpus = pd.read_parquet(Path(config["paths"]["processed"])/"corpus_units.parquet",
        columns=["unit_key", "unit_json"]).set_index("unit_key")
    units = corpus.loc[sample.unit_key, "unit_json"].to_dict()
    inputs_hash = hashlib.sha256("".join(units[key] for key in sorted(units)).encode()).hexdigest()
    implementation = {str(p):sha256_file(p) for p in [Path(__file__).relative_to(Path.cwd())
        if Path(__file__).is_absolute() else Path(__file__), Path("scripts/phase07_evaluability.py")]}
    signature = hashlib.sha256(json.dumps([RULE, inputs_hash, config_hash(config), implementation], sort_keys=True).encode()).hexdigest()
    cache = Path(config["paths"]["interim"])/"evaluability"/signature[:16]
    cache.mkdir(parents=True, exist_ok=True)
    root = Path("results/expA")
    jobs = ((units[key], config["raster"]["resolution_m"], config["raster"]["source_gap_close_m"], str(cache))
            for key in sorted(units))
    rows = []
    with ProcessPoolExecutor(max_workers=args.jobs) as pool:
        for record in tqdm(pool.map(evaluate_job, jobs, chunksize=5), total=len(units), desc="Empty evaluability"):
            rows.append(record)
            if len(rows) % 100 == 0 or len(rows) == len(units):
                write_json(root/"evaluability_progress.json", dict(completed_units=len(rows), expected_units=len(units)))
    frame = pd.DataFrame(rows).sort_values("unit_key")
    required = ["unit_key", "source", "nia_m2", "a_pass", "b_reachable_share", "evaluable", "reason"]
    frame[required].to_csv(root/"evaluability.csv", index=False)
    frame.to_csv(root/"evaluability_details.csv", index=False)
    excluded = frame[~frame.evaluable].sort_values("unit_key")
    rng = np.random.default_rng(config["seed"])
    chosen = excluded.iloc[rng.choice(len(excluded), min(20, len(excluded)), replace=False)].sort_values("unit_key")
    chosen[required].to_csv(root/"exclusion_audit_sample.csv", index=False)
    summary = bias_outputs(frame, root)
    write_json(root/"evaluability_manifest.json", dict(rule=RULE, seed=config["seed"],
        frozen_sample_sha256=sha256_file(sample_path), frozen_input_hash=inputs_hash,
        config_hash=config_hash(config), resolution_m=config["raster"]["resolution_m"],
        source_gap_close_m=config["raster"]["source_gap_close_m"], implementation=implementation,
        evaluability_sha256=sha256_file(root/"evaluability.csv"), details_sha256=sha256_file(root/"evaluability_details.csv"),
        frozen_units=len(frame), evaluable_units=int(frame.evaluable.sum()), excluded_units=int((~frame.evaluable).sum()),
        a_fail_units=int((~frame.a_pass).sum()), b_fail_units=int((frame.b_reachable_share < .5-1e-12).sum()),
        reasons=excluded.reason.value_counts().to_dict(),
        outcome_files_read=[], audit_sample_sha256=sha256_file(root/"exclusion_audit_sample.csv")))
    lines = ["# E1 evaluability and E3 exclusion composition", "",
        "Evaluability was computed from empty rasters only, before outcome analysis. No furniture, solver output or FCI was read.", "",
        f"Frozen units: {len(frame)}; retained: {int(frame.evaluable.sum())}; excluded: {len(excluded)}.", "",
        "The 0.60 m walking disc must reach every fixed-service target. At least 50% of raster-furnishable cells must be covered or within 0.60 m extra free-cell travel. The eight-neighbour expansion cannot cross walls or cut blocked corners. Raster-furnishable cells exclude door keepouts and blocked partial boundary cells. Existing 0.15 m source-gap treatment is unchanged; no repair is introduced.", "",
        summary.to_markdown(index=False, floatfmt=".3f"), "",
        "Pooled outcome means must state this source/size composition shift. NIA-bin and source-specific results describe the retained sample only; binning does not eliminate all within-bin selection bias. D3 is a designed grid, not a population sample.", "",
        "The fixed-seed E2 sample is in `exclusion_audit_sample.csv`. Cause rendering and classification are a separate no-repair audit.", ""]
    Path("reports/expA_evaluability.md").write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps(dict(frozen=len(frame), retained=int(frame.evaluable.sum()), excluded=len(excluded))))


if __name__ == "__main__":
    main()
