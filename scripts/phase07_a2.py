"""Explicit one-side sensitivity configuration and independent acceptance checks."""
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

from fea.config import merge_override


HOUSEHOLDS = ["H3_couple_one_remote", "H4_parent_child"]


def variant_config(base):
    override = yaml.safe_load(Path("config/a2_overrides.yaml").read_text())
    return merge_override(base, override["config"])


def acceptance(frame, unit_keys):
    keys = ["unit_key", "household", "strategy"]
    expected = pd.MultiIndex.from_product([sorted(unit_keys), HOUSEHOLDS, ["S0", "S1", "S2"]], names=keys)
    actual = pd.MultiIndex.from_frame(frame[keys])
    if actual.has_duplicates or len(actual) != len(expected) or len(expected.difference(actual)):
        raise ValueError("A2 must have all frozen units by two households and three strategies")
    if not frame.validator_pass.eq(True).all() or not np.isfinite(frame.fci_validator.to_numpy(float)).all():
        raise ValueError("A2 has invalid or nonfinite cases")
    paired = frame.pivot(index=["unit_key", "household"], columns="strategy", values="fci_validator")
    ordering_failures = int(((paired.S1 < paired.S0-1e-8) | (paired.S2 < paired.S1-1e-8)).sum())
    if ordering_failures:
        raise ValueError("A2 strategy ordering failed")
    return dict(passed=True, expected_cases=len(expected), completed_cases=len(frame),
        units=len(unit_keys), invalid_cases=0, ordering_failures=0,
        zero_cases=int((frame.fci_validator <= 1e-9).sum()),
        status_distribution=frame.status.value_counts().to_dict())
