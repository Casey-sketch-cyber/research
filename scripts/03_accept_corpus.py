"""Independently check the generated corpus package and run source-loader tests."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pandas as pd
from tqdm import tqdm

from fea.geometry.unit import Unit
from fea.io import prepare_cli, start_run, write_json


def main():
    args = prepare_cli(__doc__).parse_args()
    config, digest, _ = start_run(args, "03_accept_corpus")
    if args.dry_run:
        print("Would compare corpus CSV/parquet, source counts, inclusion flags and sample geometry, then run tests.")
        return
    corpus = pd.read_csv("results/corpus/corpus_units.csv", keep_default_na=False)
    corpus["furnishable_area_m2"] = pd.to_numeric(corpus.furnishable_area_m2, errors="coerce")
    audit = json.loads(Path("reports/corpus_audit.json").read_text())
    samples = json.loads(Path("results/corpus/sample_units.json").read_text())
    processed = pd.read_parquet(Path(config["paths"]["processed"]) / "corpus_units.parquet")
    checks = {
        "unique_keys": corpus.unit_key.is_unique,
        "csv_parquet_same_keys": corpus.unit_key.tolist() == processed.unit_key.tolist(),
        "current_config_hash": set(corpus.config_hash) == {digest} and audit["config_hash"] == digest,
        "D1_grouping_shared": corpus[corpus.source == "D1"].group_id.nunique() < len(corpus[corpus.source == "D1"]),
        "D1_gross_not_fabricated": (corpus.loc[corpus.source == "D1", "gross_area_m2"] == "").all(),
        "all_D3_retained": int((corpus.source == "D3").sum()) == __import__("math").prod(len(config["shells_D3"][k]) for k in ("areas_m2", "aspect_ratios", "entrance_positions", "window_positions")),
        "inclusion_reason_consistent": (corpus.include == (corpus.exclude_reason == "")).all(),
        "included_areas_in_range": corpus[corpus.include].furnishable_area_m2.between(config["corpus"]["min_furnishable_area_m2"], audit["effective_max_furnishable_area_m2"]).all(),
        "included_geometry_checks_pass": (corpus.loc[corpus.include, "geometry_failures"] == "").all(),
        "included_normalization_preserves_area": audit["max_included_normalization_area_change_m2"] <= 1e-6,
        "24_sample_images": len(list(Path("results/corpus/samples").glob("*.png"))) == 24,
        "histogram_formats": all(Path("results/figures/F2_corpus_area" + suffix).exists() for suffix in (".png", ".pdf")),
        "eight_samples_per_source": pd.Series([u["source"] for u in samples["units"]]).value_counts().to_dict() == {"D1": 8, "D2": 8, "D3": 8},
    }
    sample_ok = True
    local_coordinates = True
    for record in tqdm(samples["units"], desc="Sample audit"):
        unit = Unit.from_dict(record)
        row = corpus.set_index("unit_key").loc[unit.unit_key]
        sample_ok &= bool(row.include and abs(unit.classes["furnishable"].area - row.furnishable_area_m2) < 1e-6)
        sample_ok &= unit.entrance is not None and bool(unit.windows)
        local_coordinates &= max(abs(x) for x in unit.interior.bounds[:2]) < 1e-8
    checks["sample_metadata_matches_csv"] = sample_ok
    checks["published_samples_use_local_coordinates"] = local_coordinates
    result = subprocess.run([sys.executable, "-m", "pytest", "-q"], capture_output=True, text=True)
    checks["tests_pass_without_skips"] = result.returncode == 0 and "skipped" not in result.stdout
    write_json("reports/phase02_acceptance.json", {"config_hash": digest,
        "checks": {k: bool(v) for k, v in checks.items()}, "pass": bool(all(checks.values())),
        "pytest_summary": result.stdout.strip().splitlines()[-1], "visual_review": "human review pending at G1"})
    if result.returncode:
        Path("logs/phase02_test_failure.log").write_text(result.stdout + result.stderr)
    print(json.dumps({k: bool(v) for k, v in checks.items()}))
    raise SystemExit(not all(checks.values()))


if __name__ == "__main__":
    main()
