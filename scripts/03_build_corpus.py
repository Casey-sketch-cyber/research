"""Build, audit and render the complete source-normalized corpus."""
from __future__ import annotations

import hashlib
import json
import time
from pathlib import Path

import numpy as np
import pandas as pd
from tqdm import tqdm

from fea.data.d1_swiss import load_d1
from fea.data.d2_resplan import load_d2
from fea.data.d3_shells import load_d3
from fea.geometry.unit import Unit
from fea.geometry.normalize import normalize
from fea.geometry.audit import describe
from fea.io import prepare_cli, start_run, write_json


def source_cache(source, loader, config, digest, signature):
    """Resume completed units and bypass an entirely completed source."""
    directory = Path(config["paths"]["interim"]) / "corpus" / (digest[:12] + "_" + signature[:12])
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / f"{source}.jsonl"
    done = path.with_suffix(".done.json")
    records = {}
    if path.exists():
        with path.open("rb+") as stream:
            position = 0
            for line in stream:
                try:
                    record = json.loads(line)
                except (ValueError, UnicodeDecodeError):
                    stream.truncate(position)
                    break
                records[record["unit"]["unit_key"]] = record
                position = stream.tell()
    if done.exists():
        return list(records.values()), json.loads(done.read_text())
    started = time.perf_counter()
    with path.open("a", encoding="utf-8") as stream:
        for unit in loader(config):
            if unit.unit_key in records:
                continue
            before = {name: geometry.area for name, geometry in unit.classes.items()}
            unit = normalize(unit)
            delta = max(abs(before[name] - geometry.area) for name, geometry in unit.classes.items())
            if delta > 1e-6:
                raise ValueError("Rigid normalization changed an area")
            record = {"unit": unit.to_dict(), "scalars": describe(unit), "max_area_change_m2": delta}
            stream.write(json.dumps(record, allow_nan=False) + "\n")
            stream.flush()
            records[unit.unit_key] = record
    stats = {"source": source, "records": len(records), "processing_seconds_this_attempt": time.perf_counter() - started,
             "config_hash": digest, "code_hash": signature}
    write_json(done, stats)
    return list(records.values()), stats


def main():
    parser = prepare_cli(__doc__)
    args = parser.parse_args()
    config, digest, started = start_run(args, "03_build_corpus")
    if args.dry_run:
        print("Would convert and audit all authorized D1/D2/D3 units; render fixed-seed samples.")
        return
    code_files = sorted(Path("src/fea/data").glob("*.py")) + sorted(Path("src/fea/geometry").glob("*.py")) + [Path(__file__)]
    signature = hashlib.sha256(b"".join(path.read_bytes() for path in code_files)).hexdigest()
    records, runtimes = [], []
    for source, loader in (("D1", load_d1), ("D2", load_d2), ("D3", load_d3)):
        values, stats = source_cache(source, loader, config, digest, signature)
        records.extend(values)
        runtimes.append(stats)
    frame = pd.DataFrame([record["scalars"] for record in records])
    limit = config["corpus"]["max_furnishable_area_m2"]
    lower = config["corpus"]["min_furnishable_area_m2"]
    qualified_d1 = ((frame.source == "D1") & (frame.geometry_failures == "") & frame.furnishable_area_m2.between(lower, limit)).sum()
    if qualified_d1 < 300:
        limit = 55
    def exclusion(row):
        reasons = list(filter(None, row.geometry_failures.split(";")))
        if row.furnishable_area_m2 < lower:
            reasons.append("below_min_furnishable_area")
        if row.furnishable_area_m2 > limit:
            reasons.append("above_max_furnishable_area")
        return ";".join(reasons)
    frame["exclude_reason"] = frame.apply(exclusion, axis=1)
    frame["include"] = frame.exclude_reason == ""
    frame["config_hash"] = digest
    frame["code_hash"] = signature
    output = Path(config["paths"]["results"]) / "corpus"
    output.mkdir(parents=True, exist_ok=True)
    frame.to_csv(output / "corpus_units.csv", index=False)
    processed = frame.copy()
    processed["unit_json"] = [json.dumps(record["unit"], allow_nan=False) for record in records]
    target = Path(config["paths"]["processed"]) / "corpus_units.parquet"
    target.parent.mkdir(parents=True, exist_ok=True)
    processed.to_parquet(target, index=False)
    counts = frame.groupby("source").agg(total=("include", "size"), included=("include", "sum"), missing_gross=("gross_area_m2", lambda values: int(values.isna().sum())), missing_entrance=("entrance_method", lambda values: int((values == "unidentified").sum())))
    counts["excluded"] = counts.total - counts.included
    counts["config_hash"] = digest
    counts.to_csv(output / "counts.csv")
    reasons = frame.loc[~frame.include, ["source", "exclude_reason"]].assign(exclude_reason=lambda values: values.exclude_reason.str.split(";")).explode("exclude_reason").value_counts().rename("n").reset_index()
    reasons["config_hash"] = digest
    reasons.to_csv(output / "exclusion_reasons.csv", index=False)
    rng = np.random.default_rng(config["seed"])
    selected = []
    for source in ("D1", "D2", "D3"):
        indices = frame.index[(frame.source == source) & frame.include].to_numpy()
        if len(indices) < 8:
            raise ValueError(f"Not enough included {source} units for sample")
        selected.extend(sorted(rng.choice(indices, size=8, replace=False).tolist()))
    samples = [Unit.from_dict(records[i]["unit"]) for i in selected]
    write_json(output / "sample_units.json", {"seed": config["seed"], "config_hash": digest, "code_hash": signature, "units": [unit.to_dict() for unit in samples]})
    from fea.viz.corpus import render_samples, render_histogram
    render_samples(samples, output / "samples")
    render_histogram(frame, Path(config["paths"]["figures"]) / "F2_corpus_area", digest)
    write_json("reports/corpus_audit.json", {"config_hash": digest, "code_hash": signature,
        "counts": counts.reset_index().to_dict("records"), "initial_D1_qualified": int(qualified_d1),
        "effective_max_furnishable_area_m2": limit, "sources": runtimes,
        "max_normalization_area_change_m2": max(record["max_area_change_m2"] for record in records),
        "D1_with_simulations": int(((frame.source == "D1") & (frame.simulation_fields > 0)).sum()),
        "sample_count": len(samples), "total_seconds_this_invocation": time.perf_counter() - started,
        "gross_area_note": "D1 missing; D2 source declaration with explicit geometric calibration; D3 generated gross internal area"})
    print(counts.to_string())


if __name__ == "__main__":
    main()
