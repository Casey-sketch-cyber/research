"""Guard K3's duplicate selection and shell-paired comparisons."""

import importlib.util
from pathlib import Path
import sys

import pandas as pd
import pytest


SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))
from phase11d_k3_analysis import paired_effect, paired_rows


def test_retains_best_validated_layout_per_vector_and_shell():
    path = SCRIPTS / "11d_run_k3.py"
    spec = importlib.util.spec_from_file_location(path.stem, path)
    driver = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(driver)
    records = pd.DataFrame([
        ("H3", "kit", "a", "first", .60, 0., True),
        ("H3", "kit", "a", "higher", .80, 2., True),
        ("H3", "kit", "a", "lower_burden", .80, 1., True),
        ("H3", "kit", "a", "invalid", 1., 0., False),
        ("H3", "kit", "b", "other_shell", .55, 0., True),
    ], columns=["household", "kit_id", "unit_key", "task_key", "fciq", "tb", "validator_pass"])
    assert driver.best_per_shell(records).set_index("unit_key").task_key.to_dict() == {
        "a": "lower_burden", "b": "other_shell",
    }


def test_paired_effect_uses_shell_identity_and_threshold():
    kib = pd.DataFrame({"household": ["H3"] * 3, "unit_key": ["b", "a", "c"], "fci": [.8, 1., .95],
                        "fciq": [.8, 1., .95]})
    cat = pd.DataFrame({"household": ["H3"] * 3, "unit_key": ["a", "c", "b"], "fci": [.9, .95, 1.],
                        "fciq": [.9, .95, 1.]})
    pairs = paired_rows(kib, cat, "H3", "train", .95)
    result = paired_effect(pairs, 20261105, 1000, .95)
    assert result["mean_kit_minus_catalogue"] == pytest.approx(-.1 / 3)
    assert result["kit_better"] == result["equal"] == result["kit_worse"] == 1
    assert result["kit_adequate"] == result["catalogue_adequate"] == 2
    assert result["adequate_kit_only"] == result["adequate_catalogue_only"] == 1
    assert result["ci_lo"] < 0 < result["ci_hi"]
