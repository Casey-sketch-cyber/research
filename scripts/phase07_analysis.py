"""Strict, whole-unit analysis selection under the reviewed E1 rule."""
import json
from pathlib import Path

import numpy as np
import pandas as pd

from fea.io import sha256_file, write_json
from fea.config import config_hash


def select_evaluable(solutions, evaluability, frozen_sample, households):
    """Require a complete cross-product and valid paired rows for retained units."""
    expected_units = set(frozen_sample.unit_key)
    if frozen_sample.unit_key.duplicated().any() or evaluability.unit_key.duplicated().any():
        raise ValueError("Duplicate frozen/evaluability unit")
    if set(evaluability.unit_key) != expected_units or set(solutions.unit_key) != expected_units:
        raise ValueError("Evaluability and raw case units must exactly match the frozen sample")
    if not evaluability.evaluable.map(lambda value: isinstance(value, (bool, np.bool_))).all():
        raise ValueError("Evaluability flags must be Boolean")
    if not solutions.validator_pass.map(lambda value: isinstance(value, (bool, np.bool_))).all():
        raise ValueError("Validator flags must be Boolean")
    keys = ["unit_key", "household", "strategy"]
    required = pd.MultiIndex.from_product([sorted(expected_units), households, ["S0", "S1", "S2"]], names=keys)
    actual = pd.MultiIndex.from_frame(solutions[keys])
    if actual.has_duplicates or len(actual) != len(required) or len(required.difference(actual)):
        raise ValueError("Missing, duplicate or unexpected unit/household/strategy cases")
    reference = evaluability.set_index("unit_key")
    if not (solutions.source.to_numpy() == solutions.unit_key.map(reference.source).to_numpy()).all():
        raise ValueError("Source metadata does not match evaluability")
    if not np.allclose(solutions.nia_m2, solutions.unit_key.map(reference.nia_m2), atol=1e-7, rtol=0):
        raise ValueError("NIA metadata does not match evaluability")
    retained = set(evaluability.loc[evaluability.evaluable, "unit_key"])
    filtered = solutions[solutions.unit_key.isin(retained)].copy()
    excluded = expected_units-retained
    if len(solutions)-len(filtered) != len(excluded)*len(households)*3:
        raise ValueError("Exclusion must remove every household and strategy together")
    if filtered.empty or not filtered.validator_pass.all():
        raise ValueError("Every evaluable case must pass independent validation")
    values = filtered.fci_validator.to_numpy(float)
    if not np.isfinite(values).all() or (values < -1e-9).any() or (values > 1+1e-9).any():
        raise ValueError("Invalid retained FCI")
    paired = filtered.pivot(index=["unit_key", "household"], columns="strategy", values="fci_validator")
    if ((paired.S1 < paired.S0-1e-8) | (paired.S2 < paired.S1-1e-8)).any():
        raise ValueError("Retained strategy ordering failed")
    return filtered, dict(passed=True, frozen_units=len(expected_units), evaluable_units=len(retained),
        excluded_units=len(excluded), raw_cases=len(solutions), included_cases=len(filtered),
        excluded_cases=len(solutions)-len(filtered), households=len(households), strategies=3,
        included_invalid_cases=0, ordering_failures=0, retained_zero_cases=int((values <= 1e-9).sum()))


def load_evaluable_solutions(config, root=Path("results/expA")):
    """Verify rule/input provenance and write a distinct analysis acceptance record."""
    run = json.loads((root/"run.json").read_text())
    if config_hash(config) != run["base_config_hash"]:
        raise ValueError("Historical A configuration differs; use the accepted F1 corrected evidence, not old scores with a new label")
    original_acceptance = json.loads((root/"solve_acceptance.json").read_text())
    manifest = json.loads((root/"evaluability_manifest.json").read_text())
    if run["status"] != "complete" or original_acceptance["completed_cases"] != run["expected_cases"]:
        raise ValueError("A solves must be complete")
    if manifest["frozen_input_hash"] != run["inputs_hash"] or manifest["frozen_sample_sha256"] != run["sample_sha256"]:
        raise ValueError("Evaluability uses different frozen inputs")
    if manifest["config_hash"] != run["base_config_hash"] or manifest["outcome_files_read"]:
        raise ValueError("Evaluability configuration or outcome independence is invalid")
    for filename, digest in manifest["implementation"].items():
        if sha256_file(Path(filename)) != digest:
            raise ValueError("Evaluability implementation changed after freezing")
    if sha256_file(root/"evaluability.csv") != manifest["evaluability_sha256"]:
        raise ValueError("Evaluability table changed after freezing")
    sample_path = Path(run["production_settings"]["sample_path"])
    if sha256_file(sample_path) != run["sample_sha256"]:
        raise ValueError("Frozen sample changed")
    sample = pd.read_csv(sample_path)
    evaluation = pd.read_csv(root/"evaluability.csv")
    raw = pd.read_csv(root/"solutions.csv", low_memory=False)
    selected, record = select_evaluable(raw, evaluation, sample, config["households"]["main_households"])
    if record["excluded_units"] != manifest["excluded_units"] or record["evaluable_units"] != manifest["evaluable_units"]:
        raise ValueError("Analysis exclusions do not equal the frozen E1 counts")
    invalid_units = set(raw.loc[~raw.validator_pass, "unit_key"])
    a_failed = set(evaluation.loc[~evaluation.a_pass, "unit_key"])
    if not invalid_units <= a_failed:
        raise ValueError("A structural failure is not explained by E1(a)")
    valid = raw[raw.validator_pass]
    zero_d1 = valid[valid.source == "D1"].groupby("unit_key").fci_validator.agg(["count", "max"])
    zero_d1 = set(zero_d1.index[(zero_d1["count"] == len(config["households"]["main_households"])*3) & (zero_d1["max"] <= 1e-9)])
    b_failed = set(evaluation.loc[evaluation.b_reachable_share < .5-1e-12, "unit_key"])
    record.update(original_solve_acceptance_passed=original_acceptance["passed"],
        raw_solutions_sha256=sha256_file(root/"solutions.csv"),
        evaluability_sha256=manifest["evaluability_sha256"],
        evaluability_manifest_sha256=sha256_file(root/"evaluability_manifest.json"),
        structural_failure_units=len(invalid_units), all_structural_failures_fail_a=True,
        valid_all_zero_D1_units=len(zero_d1), valid_all_zero_D1_units_failing_b=len(zero_d1 & b_failed),
        retained_D3_zero_cases=int(((selected.source == "D3") & (selected.fci_validator <= 1e-9)).sum()),
        rule="phase07_review E1/E4; whole-unit filtering; genuine valid zeros retained")
    write_json(root/"analysis_acceptance.json", record)
    return selected, record
