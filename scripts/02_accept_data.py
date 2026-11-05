"""Validate the Phase 1 publication package against the current configuration."""
from __future__ import annotations

import csv
import json
import subprocess
import sys
from pathlib import Path

from fea.io import prepare_cli, start_run, write_json


def main() -> None:
    """Write explicit acceptance evidence; never silently accept a partial run."""
    args = prepare_cli(__doc__).parse_args()
    config, digest, _ = start_run(args, "02_accept_data")
    if args.dry_run:
        print("Would validate manifests, schema coverage, configuration hashes and tests.")
        return
    acquisition = json.loads(Path("reports/acquisition.json").read_text())
    run = json.loads(Path("reports/schema_run.json").read_text())
    manifest = list(csv.DictReader(Path("reports/data_manifest.csv").open()))
    summaries = {key: json.loads(Path(f"reports/schemas/{key}_summary.json").read_text()) for key in ("D1", "D2", "D4", "D6")}
    mapped = sum(config["corpus"]["d1_subtype_classes"].values(), [])
    checks = {
        "all_authorized_resources_present": {row["dataset"] for row in manifest} == {row["dataset"] for row in config["downloads"]["resources"]},
        "checksums_present": all(len(row["sha256"]) == 64 and int(row["bytes"]) > 0 for row in manifest),
        "acquisition_complete": not acquisition["partial"] and not acquisition["errors"],
        "schema_run_complete": not run["partial"] and set(run["datasets"]) == set(summaries),
        "all_schema_reports_present": all(Path(f"reports/schemas/{key}.md").exists() for key in summaries),
        "configuration_hashes_current": all(value["config_hash"] == digest for value in [acquisition, run, *summaries.values()]),
        "mapping_complete_and_disjoint": len(mapped) == len(set(mapped)) and set(mapped) == set(summaries["D1"]["area_subtypes"]),
    }
    tests = subprocess.run([sys.executable, "-m", "pytest", "-q"], capture_output=True, text=True)
    checks["tests_pass"] = tests.returncode == 0
    write_json("reports/phase01_acceptance.json", {"config_hash": digest, "checks": checks,
                "pass": all(checks.values()), "pytest_summary": tests.stdout.strip().splitlines()[-1]})
    print(json.dumps(checks))
    raise SystemExit(not all(checks.values()))


if __name__ == "__main__":
    main()
