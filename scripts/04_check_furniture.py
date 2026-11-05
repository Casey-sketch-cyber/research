"""Compare author footprints with observed ABO reference distributions."""
from __future__ import annotations

import json
import subprocess
import sys
import time
from pathlib import Path

import pandas as pd
from tqdm import tqdm

from fea.data.abo import dimensions_m, listings, product_types
from fea.furniture.checks import REFERENCE_TYPES, configured_rows, outside_interval, summary, trim_type
from fea.io import prepare_cli, sha256_file, start_run, write_json


def main():
    args = prepare_cli(__doc__).parse_args()
    config, digest, started = start_run(args, "04_check_furniture")
    if args.dry_run:
        print("Would audit ABO dimensions and every author footprint; no defaults will be changed.")
        return
    source = Path(config["paths"]["raw"]) / "abo/abo-listings.tar"
    furniture_path = Path(args.config).parent / "furniture.yaml"
    original_hash = sha256_file(furniture_path)
    records = []
    for index, item in enumerate(tqdm(listings(source), desc="ABO listings")):
        dimensions = dimensions_m(item)
        if dimensions is not None:
            records.extend({"listing_index": index, "abo_type": kind, **dimensions}
                           for kind in product_types(item) if kind in REFERENCE_TYPES)
    frame = pd.DataFrame(records)
    trimmed, type_rows = [], []
    for kind, group in frame.groupby("abo_type"):
        clean, thresholds = trim_type(group)
        trimmed.append(clean)
        type_rows.append({"abo_type": kind, "n_before": len(group), "n_dropped": len(group) - len(clean),
                          **{f"p99_{k}_m": v for k, v in thresholds.items()}, **summary(clean), "config_hash": digest})
    clean = pd.concat(trimmed, ignore_index=True)
    comparisons = []
    for name, state, dimensions, types, unvalidated, reason in configured_rows(config["furniture"]):
        group = clean[clean.abo_type.isin(types)].drop_duplicates("listing_index")
        statistics = summary(group)
        flags = []
        if group.empty:
            flags.append("NO_MATCH")
        elif outside_interval(*dimensions, statistics):
            flags.append("OUTSIDE_IQR")
        if unvalidated:
            flags.append("UNVALIDATED_STATE")
        comparisons.append({"item": name, "state": state, "config_w": dimensions[0], "config_d": dimensions[1],
                            "abo_type": "|".join(types), **statistics, "flag": ";".join(flags) or "WITHIN_IQR",
                            "comparison_scope": "ordinary-product analogue only" if unvalidated else "broad category reference only",
                            "decision": "KEEP_PENDING_REVIEW", "justification": reason, "config_hash": digest})
    output = Path(config["paths"]["results"]) / "furniture"
    output.mkdir(parents=True, exist_ok=True)
    comparison = pd.DataFrame(comparisons)
    comparison.to_csv(output / "abo_dimension_check.csv", index=False)
    pd.DataFrame(type_rows).to_csv(output / "abo_type_statistics.csv", index=False)
    notes = ["# ABO comparison interpretation", "", "Width is the listing width; depth is listing length. Axes are not swapped. IQR columns are q75-q25; quartile endpoint columns define the comparison interval.", "",
             "Outliers are dropped above the untrimmed 99th percentile on any dimension within each product type (linear quantile interpolation). Combined reference cohorts deduplicate listings after type-specific trimming.", "",
             "The categories mix sizes and uses. Being within the IQR is not validation of a configured item. State-specific geometry, mechanisms, clearance, storage capacity and occupant capacity are not observed by this check.", "",
             "## Item/state decisions", "", comparison[["item", "state", "flag", "justification"]].to_markdown(index=False), ""]
    (output / "interpretation.md").write_text("\n".join(notes), encoding="utf-8")
    test = subprocess.run([sys.executable, "-m", "pytest", "-q", "tests/test_furniture.py"], capture_output=True, text=True)
    checks = {"comparison_csv_exists": (output / "abo_dimension_check.csv").exists(),
              "every_footprint_compared": len(comparison) == len(list(configured_rows(config["furniture"]))),
              "all_rows_have_decisions": comparison.justification.notna().all(),
              "furniture_defaults_unchanged": sha256_file(furniture_path) == original_hash,
              "tests_pass": test.returncode == 0}
    write_json("reports/furniture_audit.json", {"config_hash": digest, "source_sha256": sha256_file(source),
        "furniture_sha256": original_hash, "comparisons": len(comparison),
        "outside_IQR": int(comparison.flag.str.contains("OUTSIDE_IQR").sum()),
        "unvalidated_states": int(comparison.flag.str.contains("UNVALIDATED_STATE").sum()),
        "no_match": int(comparison.flag.str.contains("NO_MATCH").sum()),
        "reference_listings_before": int(frame.listing_index.nunique()), "reference_listings_after": int(clean.listing_index.nunique()),
        "checks": {k: bool(v) for k, v in checks.items()}, "pass": bool(all(checks.values())),
        "pytest_summary": test.stdout.strip().splitlines()[-1], "runtime_s": time.perf_counter() - started})
    print(json.dumps({k: bool(v) for k, v in checks.items()}))
    raise SystemExit(not all(checks.values()))


if __name__ == "__main__":
    main()
