"""Validate household schedules and generate Table T3 from unchanged defaults."""
from __future__ import annotations

import json
import subprocess
import sys
import time
from pathlib import Path

import pandas as pd
from tqdm import tqdm

from fea.households import demanded_hours, parse_households, schedule_rows
from fea.io import prepare_cli, sha256_file, start_run, write_json


def main() -> None:
    """Generate schedules and acceptance evidence; this short operation is repeatable."""
    args = prepare_cli(__doc__).parse_args()
    config, digest, started = start_run(args, "05_schedules")
    if args.dry_run:
        print("Would validate unchanged households and generate Table T3; no calibration applied.")
        return
    source = Path(args.config).parent / "households.yaml"
    original = sha256_file(source)
    households = parse_households(config["households"], config["furniture"])
    rows = list(tqdm(schedule_rows(households, config["households"], digest), desc="Schedule rows"))
    table = pd.DataFrame(rows)
    output = Path(config["paths"]["results"]) / "tables"
    output.mkdir(parents=True, exist_ok=True)
    table.to_csv(output / "T3_households.csv", index=False)
    totals = pd.DataFrame([{"household": h.name, "persons": h.persons, "variants": len(h.variants),
                            "scope": "main" if h.name in config["households"]["main_households"] else "ablation",
                            "mean_demanded_hours": demanded_hours(h), "config_hash": digest}
                           for h in households.values()])
    totals.to_csv(output / "T3_household_totals.csv", index=False)
    markdown = ["# T3. Household schedules", "", "Author defaults; not empirically calibrated. Units: hours. Cooking and hygiene in fixed rooms are outside the demand denominator.", "",
                totals.drop(columns="config_hash").to_markdown(index=False), "",
                "Each repeated demand is a separate simultaneous requirement. Storage units affect capacity credit, not demand weight. Alternative days retain their configured frequencies. The mean denominator is descriptive only: FCI must be the frequency-weighted mean of per-variant FCI ratios.", "",
                "H5 is an ablation only: walking width 0.90 m and global clearance scale 1.2. Full weights, distinct demand IDs and overrides are retained in the CSV.", ""]
    for (name, variant), group in table.groupby(["household", "variant"], sort=False):
        markdown += [f"## {name} / {variant} (frequency {group.iloc[0].frequency:g})", "",
                     group[["slot", "start_hour", "end_hour", "duration_h", "demands", "slot_demanded_hours"]].to_markdown(index=False), ""]
    markdown += [f"Configuration hash: `{digest}`.", ""]
    (output / "T3_households.md").write_text("\n".join(markdown), encoding="utf-8")
    test = subprocess.run([sys.executable, "-m", "pytest", "-q", "tests/test_households.py"], capture_output=True, text=True)
    checks = {"all_schedules_validated": True, "table_exists": (output / "T3_households.csv").exists(),
              "household_defaults_unchanged": sha256_file(source) == original, "tests_pass": test.returncode == 0}
    write_json("reports/households_audit.json", {"config_hash": digest, "households_sha256": original,
        "rows": len(table), "households": len(households), "variants": sum(len(h.variants) for h in households.values()),
        "mean_demanded_hours": dict(zip(totals.household, totals.mean_demanded_hours)),
        "checks": checks, "pass": all(checks.values()), "pytest_summary": test.stdout.strip().splitlines()[-1],
        "runtime_s": time.perf_counter() - started})
    print(json.dumps(checks))
    raise SystemExit(not all(checks.values()))


if __name__ == "__main__":
    main()
