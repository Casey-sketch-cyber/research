"""Revalidate and archive every completed small-home comparison layout."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path

import pandas as pd
from tqdm import tqdm

from fea.config import config_hash
from fea.geometry.raster import rasterize
from fea.geometry.unit import Unit
from fea.households import parse_households
from fea.io import prepare_cli, start_run, write_json
from fea.validate import validate_layout


def main() -> None:
    """Check Cartesian coverage, provenance, scores and independently valid layouts."""
    parser = prepare_cli(__doc__)
    parser.add_argument("--base-config-snapshot", help="Preserved full configuration JSON for historical arms")
    args = parser.parse_args()
    base, _, _ = start_run(args, "06_round2_audit")
    if args.dry_run:
        print("Would revalidate completed comparisons and archive portable layout evidence.")
        return
    if args.base_config_snapshot:
        base = json.loads(Path(args.base_config_snapshot).read_text())
    root = Path("results/pilot/round2")
    raw_units = json.loads((root/"small_units.json").read_text())["units"]
    units = {u["unit_key"]: Unit.from_dict(u) for u in raw_units}
    names = base["households"]["main_households"]
    expected = {(u, h, s) for u in units for h in names for s in ("S1", "S2")}
    inputs_hash = hashlib.sha256(json.dumps([raw_units, names], sort_keys=True).encode()).hexdigest()
    arms = ("small_final_w8_t300", "small_final_w4_t120", "small_final_w1_t30")
    rows, signatures = [], set()
    for arm in arms:
        directory = root/arm
        manifest = json.loads((directory/"run.json").read_text())
        frame = pd.read_csv(directory/"cases.csv")
        actual = set(frame[["unit_key", "household", "strategy"]].itertuples(index=False, name=None))
        assert actual == expected and len(frame) == len(expected) == manifest["expected_cases"]
        assert manifest["inputs_hash"] == inputs_hash
        signatures.add(manifest["code_hash"])
        config = deepcopy(base)
        config["solver"].update(num_workers=manifest["num_workers"], time_limit_s=manifest["time_limit_s"])
        config["raster"]["anchor_stride_m"] = manifest["anchor_stride_m"]
        assert config_hash(config) == manifest["config_hash"]
        households = parse_households(config["households"], config["furniture"])
        for row in tqdm(frame.itertuples(index=False), total=len(frame), desc=arm):
            filename = row.layout_file
            assert Path(filename).name == filename
            published = directory/"layouts"/filename
            source = Path(manifest["cache"])/"validated"/filename
            # A clean clone can rerun this audit using the published exact bytes.
            data = (source if source.exists() else published).read_bytes()
            layout = json.loads(data)
            for field in ("unit_key", "household", "strategy", "code_hash", "config_hash"):
                assert layout[field] == getattr(row, field), (arm, filename, field)
            assert row.code_hash == manifest["code_hash"] and row.config_hash == config_hash(config)
            unit, household = units[row.unit_key], households[row.household]
            grid = rasterize(unit, config["raster"]["resolution_m"],
                household.overrides.get("walking_width", config["furniture"]["meta"]["walking_width"]),
                config["raster"]["source_gap_close_m"])
            checked = validate_layout(layout, grid, config, household)
            assert checked["pass"], (arm, filename, checked["violations"])
            assert abs(checked["fci"]-row.fci_validator) < 1e-7
            assert abs(checked["fci"]-layout["fci"]) < 1e-7
            assert abs(checked["tb"]-row.tb) < 1e-7
            assert abs(unit.interior.area-row.nia_m2) < 1e-7
            published.parent.mkdir(parents=True, exist_ok=True)
            published.write_bytes(data)
            rows.append(dict(arm=arm, unit_key=row.unit_key, household=row.household,
                strategy=row.strategy, validator_pass=True, fci=checked["fci"], tb=checked["tb"],
                path=published.as_posix(), sha256=hashlib.sha256(data).hexdigest(), bytes=len(data)))
    assert len(signatures) == 1
    pd.DataFrame(rows).to_csv(root/"completed_layout_audit.csv", index=False)
    result = dict(expected_cases=len(expected)*len(arms), audited_cases=len(rows),
        validator_pass_cases=len(rows), exact_case_coverage=True, score_mismatches=0,
        common_numerical_hash=next(iter(signatures)), layout_bytes=sum(r["bytes"] for r in rows),
        manifest="results/pilot/round2/completed_layout_audit.csv",
        formal_experiment_acceptance=False)
    write_json(root/"completed_layout_audit.json", result)
    print(json.dumps(result))


if __name__ == "__main__":
    main()
