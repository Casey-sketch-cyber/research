"""Apply G2 round-3 mean-quality, provenance and separate A/K budget checks."""
import os
for _name in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ[_name] = "1"

from copy import deepcopy
import hashlib
import importlib.util
import json
import math
from pathlib import Path

import numpy as np
import pandas as pd

from fea.config import config_hash
from fea.geometry.raster import rasterize
from fea.geometry.unit import Unit
from fea.households import parse_households
from fea.io import prepare_cli, start_run, write_json, sha256_file
from fea.validate import validate_layout

ROOT = Path("results/pilot/round3")
KEYS = ["unit_key", "household", "strategy"]


def driver(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def config_transition(before: dict, after: dict) -> dict:
    """Accept only the explicitly inactive review addition, never a physical change."""
    comparable = deepcopy(after)
    key = "double_bed_one_side_access"
    added = key not in before.get("ablations", {}) and key in after.get("ablations", {})
    if added:
        del comparable["ablations"][key]
    # JSON snapshots stringify YAML's integer mapping keys (e.g. persons -> area).
    # Compare the same canonical representation used in config_hash.
    if json.loads(json.dumps(comparable)) != json.loads(json.dumps(before)):
        raise ValueError("Benchmark configuration differs beyond the inactive A2 declaration")
    return dict(benchmark_base_config_hash=config_hash(before), production_base_config_hash=config_hash(after),
                allowed_added_path="ablations."+key if added else None,
                main_numerical_configuration_unchanged=True)


def quality_checks(hybrid: pd.DataFrame, reference: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Require exact matched cases and compare means, including all three strategies."""
    for frame in (hybrid, reference):
        if frame.duplicated(KEYS).any() or not frame.validator_pass.all():
            raise ValueError("Duplicate or invalid pilot cases")
        if not np.isfinite(frame[["fci_validator", "nia_m2"]].to_numpy(float)).all():
            raise ValueError("Nonfinite pilot measurements must not disappear from means")
    paired = hybrid.merge(reference[KEYS+["fci_validator"]], on=KEYS, how="outer",
                          validate="one_to_one", indicator=True, suffixes=("", "_reference"))
    if len(paired) != len(hybrid) or not paired._merge.eq("both").all():
        raise ValueError("Pilot comparison has missing cases")
    paired = paired.drop(columns="_merge")
    paired["difference"] = paired.fci_validator-paired.fci_validator_reference
    rows = []
    for source in ("D1", "D2", "D3", "NIA<=20"):
        data = paired[paired.nia_m2 <= 20+1e-8] if source == "NIA<=20" else paired[paired.source == source]
        if data.empty:
            raise ValueError("Missing required quality group: "+source)
        loss = .01 if source == "NIA<=20" else .02
        rows.append(dict(group=source, cases=len(data), mean_fci=data.fci_validator.mean(),
            reference_mean=data.fci_validator_reference.mean(), mean_difference=data.difference.mean(),
            allowed_loss=loss, passes=bool(data.difference.mean() >= -loss-1e-9)))
    return paired, pd.DataFrame(rows)


def load_arm(name: str, baseline: dict, signature: str) -> tuple[pd.DataFrame, dict, list]:
    """Check exact frozen coverage and independently revalidate saved pilot layouts."""
    directory = Path("results/pilot/benchmarks")/name
    summary = json.loads((directory/"summary.json").read_text())
    if summary["code_hash"] != signature or not summary["fresh_throughput_measurement"]:
        raise ValueError("Stale or resumed benchmark cannot calibrate production")
    if summary["input_hash"] != sha256_file(Path("results/pilot/pilot_units.json")):
        raise ValueError("Frozen pilot inputs changed")
    config = deepcopy(baseline)
    config["solver"].update(num_workers=summary["num_workers"], time_limit_s=summary["time_limit_s"], reachability_round_s=5.)
    config["raster"]["anchor_stride_m"] = summary["anchor_stride_m"]
    if config_hash(config) != summary["config_hash"]:
        raise ValueError("Benchmark configuration does not match its preserved snapshot")
    units = {u["unit_key"]: Unit.from_dict(u) for u in json.loads(Path("results/pilot/pilot_units.json").read_text())["units"]}
    if summary["max_nia_m2"] is not None:
        units = {key: u for key, u in units.items() if u.interior.area <= summary["max_nia_m2"]+1e-8}
    expected = {(u, h, s) for u in units for h in config["households"]["main_households"] for s in ("S0", "S1", "S2")}
    frame = pd.read_csv(directory/"cases.csv")
    actual = set(frame[KEYS].itertuples(index=False, name=None))
    if actual != expected or len(frame) != len(expected) or not frame.validator_pass.all():
        raise ValueError("Incomplete/invalid pilot arm: "+name)
    if (not np.isfinite(frame[["fci_validator", "solve_time_s", "nia_m2", "tb"]].to_numpy(float)).all()
            or not frame.fci_validator.between(-1e-9, 1+1e-9).all() or (frame.solve_time_s < 0).any()):
        raise ValueError("Pilot has nonfinite or out-of-range measurements")
    if not frame.code_hash.eq(signature).all() or not frame.config_hash.eq(config_hash(config)).all():
        raise ValueError("Mixed pilot provenance")
    households = parse_households(config["households"], config["furniture"])
    audit = []
    for row in frame.itertuples(index=False):
        published = directory/"layouts"/row.layout_file
        assert Path(row.layout_file).name == row.layout_file
        cache = Path(summary["cache"])/"shared"/row.layout_file
        data = (cache if cache.exists() else published).read_bytes()
        layout = json.loads(data)
        unit, household = units[row.unit_key], households[row.household]
        assert all(layout[key] == getattr(row, key) for key in KEYS)
        grid = rasterize(unit, config["raster"]["resolution_m"],
            household.overrides.get("walking_width", config["furniture"]["meta"]["walking_width"]),
            config["raster"]["source_gap_close_m"])
        checked = validate_layout(layout, grid, config, household)
        if not checked["pass"] or abs(checked["fci"]-row.fci_validator) > 1e-7 or abs(checked["tb"]-row.tb) > 1e-7:
            raise ValueError("Pilot layout failed independent revalidation")
        published.parent.mkdir(exist_ok=True)
        published.write_bytes(data)
        audit.append(dict(arm=name, path=published.as_posix(), sha256=hashlib.sha256(data).hexdigest(),
                          validator_pass=True, fci=checked["fci"]))
    frame["arm"] = name
    return frame, summary, audit


def runtime_costs(sample: pd.DataFrame, large: pd.DataFrame, ls: dict,
                  small: pd.DataFrame, ss: dict) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Calibrate actual elapsed cost; unrepresented sources use the full small cap."""
    result = sample.copy()
    result["budget_group"] = np.where(result.nia_m2 <= 20+1e-8, "small", "large")
    rows = []
    for group, frame, summary in (("small", small, ss), ("large", large, ls)):
        concurrency = summary["concurrent_solves"]
        factor = max(1., summary["wall_time_s"]*concurrency/frame.solve_time_s.sum())
        selected = frame[frame.nia_m2 <= 20+1e-8] if group == "small" else frame[frame.nia_m2 > 20+1e-8]
        overrun = max(0., float(frame.solve_time_s.max())-summary["time_limit_s"])
        for source in ("D1", "D2", "D3"):
            observed = selected[selected.source == source]
            mean = float(observed.solve_time_s.mean()) if len(observed) else summary["time_limit_s"]+overrun
            cost = mean*12/concurrency*factor/3600*1.15
            mask = result.source.eq(source)&result.budget_group.eq(group)
            result.loc[mask, "projected_hours_with_margin"] = cost
            rows.append(dict(group=group, source=source, observed_cases=len(observed), mean_solve_s=mean,
                estimate_basis="observed_source_mean" if len(observed) else "unrepresented_source_full_cap_plus_overrun",
                calibration_factor=factor, concurrency=concurrency, margin=.15,
                selected_units=int(mask.sum()), hours_per_unit_with_margin=cost))
    if result.projected_hours_with_margin.isna().any():
        raise ValueError("Missing runtime cost")
    return result, pd.DataFrame(rows)


def cap_sample(sample: pd.DataFrame, seed: int) -> tuple[pd.DataFrame, list]:
    """Apply M7 in order without modifying the original frozen sample."""
    subset = driver("scripts/06_revision_report.py", "old_projection_helpers").stratified_subset
    retained = sample.copy()
    actions = []
    for source, floor in (("D1", 500), ("D2", 200), ("D3", 60)):
        mask = retained.source.eq(source)
        if source == "D3":
            mask &= retained.nia_m2 > 20+1e-8
        pool, other = retained[mask], retained[~mask]
        count = len(pool)
        floor = min(floor, count)
        while retained.projected_hours_with_margin.sum() > 36 and count > floor:
            excess = retained.projected_hours_with_margin.sum()-36
            count = max(floor, count-max(1, math.ceil(excess/pool.projected_hours_with_margin.mean())))
            retained = pd.concat([other, subset(pool, count, seed)])
        if count != len(pool):
            actions.append(dict(source=source, large_only=source == "D3", before=len(pool), retained=count))
    mandatory = set(sample.loc[sample.source.eq("D3")&(sample.nia_m2 <= 20+1e-8), "unit_key"])
    assert mandatory <= set(retained.unit_key)
    return retained.sort_values(["source", "nia_m2", "unit_key"]), actions


def k_projection(config: dict, small_frame: pd.DataFrame, ss: dict) -> dict:
    """Project full and reduced K scopes at the approved small-home budget."""
    old = pd.read_csv("results/pilot/expK_projection.csv")
    settings = config["experiments"]["K_kit_design"]
    factor = max(1., ss["wall_time_s"]*ss["concurrent_solves"]/small_frame.solve_time_s.sum())
    per_solve = (ss["time_limit_s"]+max(0., small_frame.solve_time_s.max()-ss["time_limit_s"]))
    hours = per_solve*factor/ss["concurrent_solves"]/3600*1.15
    rows = []
    for scope, divisor, households, exploratory in (
            ("full_grid", 1, settings["households"], False),
            ("drop_wardrobe_frontage", 3, settings["households"], False),
            ("also_drop_H3", 3, settings["households"][:2], False),
            ("exploratory_8_kits_30_train_15_holdout_15_real_H1_H2", 1, settings["households"][:2], True)):
        for household in households:
            prior = old[old.household == household].iloc[0]
            combinations = 8 if exploratory else int(prior.combinations)//divisor
            train = 30 if exploratory else int(prior.train_shells)
            holdout = 15 if exploratory else int(prior.holdout_shells)
            real = 15 if exploratory else int(prior.real_plan_checks)
            second = math.ceil(combinations*settings["search"]["stages"][0]["keep"])
            search = combinations*min(10, train)+second*min(30, train)+min(5, second)*train
            bespoke = min(settings["bespoke_subsample"], train)*combinations
            # Catalogue, kit and flat-quality kit each need S0/S1/S2 for A3.
            evaluations = 9*(train+holdout+real)
            total = 2*search+bespoke+evaluations
            rows.append(dict(scope=scope, household=household, combinations=combinations,
                train_shells=train, holdout_shells=holdout, real_plans=real, search_solves=search,
                flat_quality_search_solves=search, bespoke_solves=bespoke, evaluation_solves=evaluations,
                total_solves=total, projected_hours_with_margin=total*hours,
                time_limit_s=ss["time_limit_s"], num_workers=ss["num_workers"],
                scope_change_requires_review=scope != "full_grid"))
    table = pd.DataFrame(rows)
    table.to_csv(ROOT/"expK_workload_options.csv", index=False)
    totals = table.groupby("scope")[["total_solves", "projected_hours_with_margin"]].sum()
    totals["within_48h"] = totals.projected_hours_with_margin <= 48
    totals.to_csv(ROOT/"expK_projection.csv")
    return dict(full_scope_hours=float(totals.loc["full_grid", "projected_hours_with_margin"]),
        full_scope_within_48h=bool(totals.loc["full_grid", "within_48h"]),
        options=totals.reset_index().to_dict("records"), K_started=False,
        caveat="Conservative cap-based workload projection, not measured K runtime; design-domain/FCIq overhead requires a K pilot. Reduced scopes are options, not approved changes.")


def main():
    parser = prepare_cli(__doc__)
    parser.add_argument("--large-arm", default="refresh_large_w1_s20_t30")
    args = parser.parse_args()
    config, _, _ = start_run(args, "06_round3_acceptance")
    if args.dry_run:
        print("Would revalidate pilots, apply round-3 gates and freeze an accepted A selection; no solves.")
        return
    ROOT.mkdir(exist_ok=True)
    baseline = json.loads((ROOT/"benchmark_base_config.json").read_text())
    transition = config_transition(baseline, config)
    revision = driver("scripts/06_revision.py", "revision_signature")
    numerical = driver("scripts/06_round2.py", "round2_signature").code_hash()
    signature = revision.signature()
    frames, summaries, audit = {}, {}, []
    for role, name in (("large", args.large_arm), ("small", "refresh_small_w4_s10_t120"),
                       ("reference", "refresh_reference_w8_s10_t60")):
        frames[role], summaries[role], checked = load_arm(name, baseline, signature)
        audit.extend(checked)
    hybrid = pd.concat([frames["large"][frames["large"].nia_m2 > 20+1e-8], frames["small"]])
    if len(hybrid) != 240:
        raise ValueError("Hybrid must cover all frozen 240 cases")
    paired, quality = quality_checks(hybrid, frames["reference"])
    paired.to_csv(ROOT/"hybrid_reference_cases.csv", index=False)
    quality.to_csv(ROOT/"hybrid_quality.csv", index=False)
    pd.DataFrame(audit).to_csv(ROOT/"pilot_layout_audit.csv", index=False)
    write_json(ROOT/"config_transition.json", transition)
    sample_path = Path("results/corpus/expA_sample.csv")
    sample = pd.read_csv(sample_path)
    costed, costs = runtime_costs(sample, frames["large"], summaries["large"], frames["small"], summaries["small"])
    retained, actions = cap_sample(costed, config["seed"])
    costs.to_csv(ROOT/"expA_cost_calibration.csv", index=False)
    costed.to_csv(ROOT/"expA_unit_costs.csv", index=False)
    selected_path = ROOT/"expA_selected_sample.csv"
    retained[sample.columns].to_csv(selected_path, index=False)
    projection = dict(uncapped_hours=float(costed.projected_hours_with_margin.sum()),
        retained_hours=float(retained.projected_hours_with_margin.sum()), margin=.15, caps=actions,
        original_units=len(sample), retained_units=len(retained), selected_source_counts=retained.source.value_counts().to_dict(),
        original_sample_sha256=sha256_file(sample_path), within_36h=bool(retained.projected_hours_with_margin.sum() <= 36))
    write_json(ROOT/"expA_projection.json", projection)
    kp = k_projection(config, frames["small"], summaries["small"])
    write_json(ROOT/"expK_projection.json", kp)
    mechanism = json.loads(Path("results/pilot/round2/mechanism_verified_w4_t120/summary.json").read_text())
    mechanism_pass = (mechanism["completed_cases"] == 12 and mechanism["s2_below_witness"] == 0
                      and mechanism["s2_improved_pairs"] > 0 and mechanism["code_hash"] == numerical)
    source_pass = bool(quality[quality.group != "NIA<=20"].passes.all())
    small_pass = bool(quality[quality.group == "NIA<=20"].passes.all())
    settings = lambda role: {k: summaries[role][k] for k in ("num_workers", "time_limit_s", "anchor_stride_m")}
    result = dict(accepted=bool(mechanism_pass and source_pass and small_pass and projection["within_36h"]),
        mechanism_pass=mechanism_pass, source_quality_pass=source_pass, small_quality_pass=small_pass,
        needs_large_fallback=not source_pass and small_pass and args.large_arm == "refresh_large_w1_s20_t30",
        numerical_hash=numerical, benchmark_driver_hash=signature, base_config_hash=config_hash(config),
        projected_expA_hours=projection["retained_hours"], small_nia_max_m2=20, small=settings("small"), large=settings("large"),
        sample_path=selected_path.as_posix(), sample_sha256=sha256_file(selected_path),
        reviewer_record="reviews/G2_review_round3.md", main_double_bed_access="two_sides",
        audit_cases=len(audit), all_pilot_layouts_valid=True, K_requires_scope_decision=not kp["full_scope_within_48h"])
    write_json("results/pilot/round2/production_selection.json", result)
    write_json(ROOT/"acceptance.json", result)
    section = ["<!-- ROUND3_ACCEPTANCE_BEGIN -->", "## Measured round-3 acceptance", "",
        "Status: "+("PASS — authorized to start A without another review stop." if result["accepted"] else
                     "NOT ACCEPTED — do not start A; use only the specified large-setting fallback if eligible."), "",
        quality.to_markdown(index=False, floatfmt=".6f"), "",
        f"All {len(audit)} saved pilot layouts revalidate independently. The numerical implementation and input hashes match the current frozen code and pilot. The preserved configuration differs from the production configuration only by the inactive A2 declaration; see `results/pilot/round3/config_transition.json`.", "",
        f"Exp. A: {len(retained)} units, {len(retained)*12} solves, {projection['retained_hours']:.6f} projected hours including a 15% margin. Caps: {json.dumps(actions)}. Small sources absent from the pilot use the full 120 s cap plus observed overrun, rather than borrowing an easier source's mean. This is a measured-pilot projection, not a runtime guarantee.", "",
        "Separate K workload projections (not observed K runtimes):", "",
        pd.DataFrame(kp["options"]).to_markdown(index=False, floatfmt=".3f"), "",
        "The full K grid exceeds 48 hours. Keep per-solve budgets unchanged. The reduced scopes are proposals; K has not started. The exploratory option uses eight prespecified kits, 30 training shells, 15 held-out shells, 15 real plans, and H1/H2; a K pilot must confirm cost before any scope is selected. Evaluation counts include S0/S1/S2 for the separate time effect. Grid reduction would limit claims and must remain visible.", "",
        "Formal A outputs are not supplied by this acceptance report. A1 analysis requires a complete accepted A table. A2 remains a separate subsequent experiment with the main two-side defaults preserved.",
        "<!-- ROUND3_ACCEPTANCE_END -->"]
    phase = Path("reports/phase_07_expA.md")
    text = phase.read_text(encoding="utf-8")
    begin, end = "<!-- ROUND3_ACCEPTANCE_BEGIN -->", "<!-- ROUND3_ACCEPTANCE_END -->"
    if begin in text:
        a, tail = text.split(begin, 1)
        _, b = tail.split(end, 1)
        text = a+"\n".join(section)+b
    else:
        text += "\n\n"+"\n".join(section)+"\n"
    phase.write_text(text, encoding="utf-8")
    print(json.dumps(result))


if __name__ == "__main__":
    main()
