"""Benchmark conservative rasterization and all-state candidates on frozen review units."""
from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import time

import pandas as pd
from tqdm import tqdm

from fea.geometry.unit import Unit
from fea.geometry.raster import rasterize
from fea.furniture.library import library
from fea.furniture.candidates import generate_candidates
from fea.io import prepare_cli, start_run, write_json


def main():
    """Write all per-item counts and timing checks, without solving a layout."""
    args = prepare_cli(__doc__).parse_args()
    config, digest, _ = start_run(args, "05_candidates")
    if args.dry_run:
        print("Would benchmark raster/candidates on the 24 frozen-sample review units.")
        return
    units = [Unit.from_dict(u) for u in json.loads(Path("results/corpus/sample_units.json").read_text())["units"]]
    frozen = set(pd.read_csv("results/corpus/expA_sample.csv").unit_key)
    assert all(u.unit_key in frozen for u in units)
    rows = []
    for unit in tqdm(units, desc="Raster/candidates"):
        start = time.perf_counter()
        grid = rasterize(unit, config["raster"]["resolution_m"])
        raster_seconds = time.perf_counter()-start
        start = time.perf_counter()
        candidates = generate_candidates(grid, library(config["furniture"]), config["raster"]["orientations_deg"])
        seconds = time.perf_counter()-start
        for item, values in candidates.items():
            rows.append(dict(unit_key=unit.unit_key, source=unit.source, nia_m2=unit.interior.area,
                item=item, n_candidates=len(values), candidate_time_s=seconds, raster_time_s=raster_seconds,
                rows=grid.labels.shape[0], columns=grid.labels.shape[1], config_hash=digest))
    out = Path("results/candidates"); out.mkdir(parents=True, exist_ok=True)
    frame = pd.DataFrame(rows); frame.to_csv(out/"counts.csv", index=False)
    unique = frame.drop_duplicates("unit_key")
    test = subprocess.run([sys.executable, "-m", "pytest", "-q", "tests/test_candidates.py"], capture_output=True, text=True)
    checks = {"tests_pass": test.returncode == 0, "median_candidate_time_under_2s": unique.candidate_time_s.median() < 2,
              "all_units_in_frozen_sample": all(u.unit_key in frozen for u in units)}
    write_json("reports/candidates_audit.json", dict(config_hash=digest, units=len(units),
        median_candidate_time_s=unique.candidate_time_s.median(), max_candidate_time_s=unique.candidate_time_s.max(),
        median_raster_time_s=unique.raster_time_s.median(), tests=test.stdout.strip(),
        checks={k: bool(v) for k, v in checks.items()}, **{"pass": bool(all(checks.values()))}))
    print(json.dumps({k: bool(v) for k, v in checks.items()}))
    if test.returncode: print(test.stdout, test.stderr)
    raise SystemExit(not all(checks.values()))


if __name__ == "__main__":
    main()
