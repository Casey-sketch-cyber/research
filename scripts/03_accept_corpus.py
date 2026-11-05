"""Independently check the generated corpus package and run source-loader tests."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pandas as pd
from tqdm import tqdm

from fea.geometry.unit import Unit
from fea.corpus import freeze_sample
from fea.io import prepare_cli, start_run, write_json


def main():
    args = prepare_cli(__doc__).parse_args()
    config, digest, _ = start_run(args, "03_accept_corpus")
    if args.dry_run:
        print("Would compare corpus CSV/parquet, source counts, inclusion flags and sample geometry, then run tests.")
        return
    corpus = pd.read_csv("results/corpus/corpus_units.csv", keep_default_na=False)
    corpus["furnishable_area_m2"] = pd.to_numeric(corpus.furnishable_area_m2, errors="coerce")
    corpus["nia_m2"] = pd.to_numeric(corpus.nia_m2, errors="coerce")
    audit = json.loads(Path("reports/corpus_audit.json").read_text())
    samples = json.loads(Path("results/corpus/sample_units.json").read_text())
    processed = pd.read_parquet(Path(config["paths"]["processed"]) / "corpus_units.parquet")
    included = corpus[corpus.include]
    frozen = pd.read_csv("results/corpus/expA_sample.csv", keep_default_na=False)
    d1_sample = frozen[frozen.source == "D1"]
    sample_settings = config["corpus"]["expA_sample"]["D1"]
    d2 = included[included.source == "D2"]
    d3 = corpus[corpus.source == "D3"]
    checks = {
        "unique_keys": corpus.unit_key.is_unique,
        "csv_parquet_same_keys": corpus.unit_key.tolist() == processed.unit_key.tolist(),
        "current_config_hash": set(corpus.config_hash) == {digest} and audit["config_hash"] == digest,
        "D1_grouping_shared": corpus[corpus.source == "D1"].group_id.nunique() < len(corpus[corpus.source == "D1"]),
        "D1_gross_not_fabricated": (corpus.loc[corpus.source == "D1", "gross_area_m2"] == "").all(),
        "all_D3_retained": int((corpus.source == "D3").sum()) == __import__("math").prod(len(config["shells_D3"][k]) for k in ("areas_m2", "aspect_ratios", "entrance_positions", "window_positions")),
        "inclusion_reason_consistent": (corpus.include == (corpus.exclude_reason == "")).all(),
        "included_NIA_in_range": included.nia_m2.between(config["corpus"]["min_nia_m2"] - 1e-6, config["corpus"]["max_nia_m2"] + 1e-6).all(),
        "complete_dwellings": ((included.n_rooms >= 1) & (included.furnishable_area_m2 > 0) & included.has_sanitary & included.has_kitchen).all(),
        "unique_included_geometry": included.geometry_hash.is_unique and (included.geometry_hash != "").all(),
        "duplicate_multiplicities": int(included.n_duplicates.sum()) == int(corpus.eligible_before_dedup.sum() - corpus.include.sum()),
        "frozen_sample_matches_flags": set(frozen.unit_key) == set(corpus.loc[corpus.in_expA_sample, "unit_key"]),
        "frozen_sample_reproducible": freeze_sample(corpus, config).in_expA_sample.equals(corpus.in_expA_sample),
        "sample_included_only": frozen.include.all() and frozen.geometry_hash.is_unique,
        "D1_sample_cap": len(d1_sample) <= sample_settings["n_max"],
        "D1_site_cap": d1_sample.groupby("group_id").size().max() <= sample_settings["max_per_site"],
        "all_eligible_D2_D3_sampled": corpus.loc[corpus.include & corpus.source.isin(["D2", "D3"]), "in_expA_sample"].all(),
        "D2_scale_bounds": pd.to_numeric(d2.median_door_span_m).between(.6, 1.3).all() and pd.to_numeric(d2.median_wall_thickness_m).between(.05, .5).all(),
        "D3_entrance_keepout_clear": pd.to_numeric(d3.entrance_keepout_overlap_m2).max() <= 1e-8,
        "D3_service_placement_present": set(d3.service_placement) <= {"near_entrance", "far_end"} and (d3.service_placement != "").all(),
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
        sample_ok &= bool(row.in_expA_sample and abs(unit.classes["furnishable"].area - row.furnishable_area_m2) < 1e-6
                          and abs(unit.interior.area - row.nia_m2) < 1e-6)
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
