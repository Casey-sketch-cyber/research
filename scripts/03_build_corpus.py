"""Build, audit and render the complete source-normalized corpus."""
from __future__ import annotations

import hashlib
import json
import time
from dataclasses import replace
from pathlib import Path

import numpy as np
import pandas as pd
from tqdm import tqdm
from shapely.errors import GEOSException
from shapely.geometry import GeometryCollection

from fea.corpus import exclusion_reasons, deduplicate_frame, freeze_sample, distribution_rows
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
        iterator = loader(config, completed_keys=set(records)) if source in {"D1", "D2"} else loader(config)
        for unit in iterator:
            if unit.unit_key in records:
                continue
            before = {name: geometry.area for name, geometry in unit.classes.items()}
            try:
                unit = normalize(unit)
                delta = max(abs(before[name] - geometry.area) for name, geometry in unit.classes.items())
                scalars = describe(unit)
                if delta > 1e-6:
                    scalars["geometry_failures"] = ";".join(filter(None, [scalars["geometry_failures"], "normalization_changed_area"]))
            except GEOSException:
                # A source-specific topology failure excludes the record. Do not
                # publish source-frame geometry or invent an area for a failed unit.
                source_counts = {"n_windows": len(unit.windows), "n_doors": len(unit.doors)}
                unit = replace(unit, classes={k: GeometryCollection() for k in unit.classes},
                               walls=GeometryCollection(), doors=[], windows=[], entrance=None,
                               meta={"geometry_unavailable": "GEOS topology error during normalization/audit"})
                scalars = describe(unit)
                scalars.update(furnishable_area_m2=None, nia_m2=None,
                               geometry_failures="geometry_processing_error")
                scalars.update(source_counts)
                delta = None
            record = {"unit": unit.to_dict(), "scalars": scalars, "max_area_change_m2": delta}
            stream.write(json.dumps(record, allow_nan=False) + "\n")
            stream.flush()
            records[unit.unit_key] = record
    stats = {"source": source, "records": len(records), "processing_seconds_this_attempt": time.perf_counter() - started,
             "config_hash": digest, "code_hash": signature}
    write_json(done, stats)
    return list(records.values()), stats


def main():
    parser = prepare_cli(__doc__)
    parser.add_argument("--source-only", choices=["D1", "D2", "D3"])
    args = parser.parse_args()
    config, digest, started = start_run(args, "03_build_corpus")
    if args.dry_run:
        print("Would convert sources, apply NIA/complete-dwelling filters, deduplicate and freeze the sample.")
        return
    code_files = [Path("src/fea") / p for p in (
        "data/archives.py", "data/d1_swiss.py", "data/d2_resplan.py", "data/d3_shells.py",
        "geometry/unit.py", "geometry/normalize.py", "geometry/audit.py", "geometry/scale.py",
        "geometry/raster.py", "validate.py")]
    signature = hashlib.sha256(b"".join(path.read_bytes() for path in code_files)).hexdigest()
    pipeline_signature = hashlib.sha256((signature + Path(__file__).read_text() + Path("src/fea/corpus.py").read_text()).encode()).hexdigest()
    records, runtimes = [], []
    for source, loader in (("D1", load_d1), ("D2", load_d2), ("D3", load_d3)):
        if args.source_only and source != args.source_only:
            continue
        values, stats = source_cache(source, loader, config, digest, signature)
        records.extend(values)
        runtimes.append(stats)
    if args.source_only:
        print(json.dumps(runtimes))
        return
    frame = pd.DataFrame([record["scalars"] for record in records])
    frame["exclude_reason"] = frame.apply(lambda row: exclusion_reasons(row, config), axis=1)
    frame = freeze_sample(deduplicate_frame(frame, records, config), config)
    frame["config_hash"] = digest
    frame["code_hash"] = pipeline_signature
    output = Path(config["paths"]["results"]) / "corpus"
    output.mkdir(parents=True, exist_ok=True)
    frame.to_csv(output / "corpus_units.csv", index=False)
    sample_frame = frame[frame.in_expA_sample].sort_values(["source", "nia_m2", "unit_key"])
    sample_frame.to_csv(output / "expA_sample.csv", index=False)
    histogram = frame[frame.include].groupby(["source", "nia_bin_2m2", "n_rooms"]).agg(
        full_unique=("unit_key", "size"), sampled=("in_expA_sample", "sum")).reset_index()
    histogram["config_hash"] = digest
    histogram.to_csv(output / "sample_strata.csv", index=False)
    processed = frame.copy()
    processed["unit_json"] = [json.dumps(record["unit"], allow_nan=False) for record in records]
    target = Path(config["paths"]["processed"]) / "corpus_units.parquet"
    target.parent.mkdir(parents=True, exist_ok=True)
    processed.to_parquet(target, index=False)
    counts = frame.groupby("source").agg(total=("include", "size"), eligible_before_dedup=("eligible_before_dedup", "sum"),
        included=("include", "sum"), expA_sample=("in_expA_sample", "sum"),
        missing_gross=("gross_area_m2", lambda values: int(values.isna().sum())))
    counts["duplicate_copies_removed"] = counts.eligible_before_dedup - counts.included
    counts["excluded"] = counts.total - counts.included
    counts["config_hash"] = digest
    counts.to_csv(output / "counts.csv")
    reasons = frame.loc[~frame.include, ["source", "exclude_reason"]].assign(exclude_reason=lambda values: values.exclude_reason.str.split(";")).explode("exclude_reason").value_counts().rename("n").reset_index()
    reasons["config_hash"] = digest
    reasons.to_csv(output / "exclusion_reasons.csv", index=False)
    d2_columns = ["unit_key", "nia_m2", "median_door_span_m", "median_wall_thickness_m", "wall_thickness_sections", "released_wall_depth_m", "include", "exclude_reason", "config_hash"]
    frame.loc[frame.source == "D2", d2_columns].to_csv(output / "d2_scale_audit.csv", index=False)
    rows = []
    entrance_reasons = {"entrance_not_touching_known_spaces", "missing_entrance"}
    entrance_only = frame.exclude_reason.apply(lambda value: bool(value) and set(value.split(";")) <= entrance_reasons)
    for category, subset in (("included_unique", frame[frame.include]), ("eligible_before_dedup", frame[frame.eligible_before_dedup]),
                             ("entrance_only_exclusion", frame[entrance_only])):
        for measure in ("nia_m2", "n_rooms"):
            rows.extend(distribution_rows(subset, measure, category))
    for measure in ("median_door_span_m", "median_wall_thickness_m", "released_wall_depth_m"):
        rows.extend(distribution_rows(frame[frame.source == "D2"], measure, "D2_all"))
    distributions = pd.DataFrame(rows)
    distributions["config_hash"] = digest
    distributions.to_csv(output / "review_distributions.csv", index=False)
    rng = np.random.default_rng(config["seed"])
    selected = []
    for source in ("D1", "D2", "D3"):
        indices = frame.index[(frame.source == source) & frame.in_expA_sample].to_numpy()
        if len(indices) < 8:
            raise ValueError(f"Not enough sampled {source} units for review contact sheet")
        selected.extend(sorted(rng.choice(indices, size=8, replace=False).tolist()))
    samples = [Unit.from_dict(records[i]["unit"]) for i in selected]
    write_json(output / "sample_units.json", {"seed": config["seed"], "config_hash": digest, "code_hash": pipeline_signature,
        "units": [unit.to_dict() for unit in samples]})
    from fea.viz.corpus import render_samples, render_histogram
    render_samples(samples, output / "samples")
    render_histogram(frame, Path(config["paths"]["figures"]) / "F2_corpus_area", digest)
    d3 = frame[frame.source == "D3"]
    write_json("reports/corpus_audit.json", {"config_hash": digest, "code_hash": pipeline_signature,
        "conversion_code_hash": signature, "counts": counts.reset_index().to_dict("records"), "sources": runtimes,
        "area_measure": "nia_m2", "min_nia_m2": config["corpus"]["min_nia_m2"], "max_nia_m2": config["corpus"]["max_nia_m2"],
        "max_normalization_area_change_m2": max(record["max_area_change_m2"] for record in records if record["max_area_change_m2"] is not None),
        "max_included_normalization_area_change_m2": max(records[i]["max_area_change_m2"] for i in frame.index[frame.include]),
        "D1_with_simulations": int(((frame.source == "D1") & (frame.simulation_fields > 0)).sum()),
        "sample_count": len(samples), "total_seconds_this_invocation": time.perf_counter() - started,
        "expA_kitchen_dining_units": int(sample_frame.has_kitchen_dining.sum()),
        "D3_max_entrance_keepout_overlap_m2": float(d3.entrance_keepout_overlap_m2.max()),
        "D3_service_placement": d3.service_placement.value_counts().to_dict(),
        "geometry_hash_grid_m": 1e-6, "duplicate_count_definition": "additional eligible copies; multiplicity = n_duplicates + 1",
        "gross_area_note": "D1 missing; D2 source declaration with geometric calibration; D3 internal shell area; primary analysis uses NIA"})
    print(counts.to_string())


if __name__ == "__main__":
    main()
