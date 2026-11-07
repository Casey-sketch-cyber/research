"""Prevent expensive formal experiments under stale or failed pilot acceptance."""
import importlib.util
from copy import deepcopy

import pytest


def driver():
    spec = importlib.util.spec_from_file_location("expA_driver", "scripts/07_run_expA.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def selection():
    return dict(accepted=True, mechanism_pass=True, source_quality_pass=True, small_quality_pass=True,
                numerical_hash="tested", projected_expA_hours=20, small_nia_max_m2=20,
                small=dict(num_workers=4, time_limit_s=120, anchor_stride_m=.1),
                large=dict(num_workers=1, time_limit_s=30, anchor_stride_m=.2))


@pytest.mark.parametrize("key", ["accepted", "mechanism_pass", "source_quality_pass", "small_quality_pass"])
def test_failure_cannot_be_used_as_formal_acceptance(key):
    record = selection()
    record[key] = False
    with pytest.raises(ValueError):
        driver().check_selection(record, "tested")


def test_stale_source_and_over_budget_are_rejected():
    module = driver()
    module.check_selection(selection(), "tested")
    with pytest.raises(ValueError):
        module.check_selection(selection(), "changed")
    over_budget = deepcopy(selection())
    over_budget["projected_expA_hours"] = 36.01
    with pytest.raises(ValueError):
        module.check_selection(over_budget, "tested")


def test_configuration_and_benchmark_provenance_are_required_at_launch():
    m = driver()
    record = selection()
    record.update(base_config_hash="config", benchmark_driver_hash="driver")
    m.check_selection(record, "tested", "config", "driver")
    with pytest.raises(ValueError):
        m.check_selection(record, "tested", "changed", "driver")
    with pytest.raises(ValueError):
        m.check_selection(record, "tested", "config", "changed")


def test_only_reviewed_size_budgets_can_launch():
    record = selection()
    record["small"]["time_limit_s"] = 30
    with pytest.raises(ValueError, match="small-home"):
        driver().check_selection(record, "tested")
