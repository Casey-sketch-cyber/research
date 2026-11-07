"""Round-3 gates must reject biased means, missing pairs and changed physics."""
from copy import deepcopy
import importlib.util

import pandas as pd
import pytest


def module():
    spec = importlib.util.spec_from_file_location("round3", "scripts/06_round3_acceptance.py")
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def pilot():
    return pd.DataFrame([dict(unit_key=f"{source}:{nia}", source=source, nia_m2=nia,
        household="H1", strategy=strategy, fci_validator=.8, validator_pass=True)
        for source in ("D1", "D2", "D3") for nia in (18, 24) for strategy in ("S0", "S1", "S2")])


def test_source_mean_loss_and_small_loss_are_separate_gates():
    reference = pilot()
    candidate = reference.copy()
    candidate.loc[candidate.source == "D1", "fci_validator"] -= .03
    _, q = module().quality_checks(candidate, reference)
    assert not q.set_index("group").loc["D1", "passes"]
    candidate = reference.copy()
    candidate.loc[candidate.nia_m2 <= 20, "fci_validator"] -= .015
    _, q = module().quality_checks(candidate, reference)
    assert q[q.group != "NIA<=20"].passes.all()
    assert not q.set_index("group").loc["NIA<=20", "passes"]


def test_missing_strategy_case_cannot_disappear_from_the_comparison():
    with pytest.raises(ValueError, match="missing"):
        module().quality_checks(pilot().iloc[1:], pilot())


def test_nonfinite_scores_cannot_be_silently_excluded_from_means():
    frame = pilot()
    frame.loc[0, "fci_validator"] = float("nan")
    with pytest.raises(ValueError, match="Nonfinite"):
        module().quality_checks(frame, pilot())


def test_only_inactive_review_metadata_can_bridge_configurations():
    before = dict(ablations={}, furniture={"clearance": .6})
    after = deepcopy(before)
    after["ablations"]["double_bed_one_side_access"] = {"status": "sensitivity only"}
    assert module().config_transition(before, after)["main_numerical_configuration_unchanged"]
    after["furniture"]["clearance"] = .5
    with pytest.raises(ValueError):
        module().config_transition(before, after)


def test_json_snapshot_integer_keys_do_not_create_a_false_physical_change():
    before = dict(ablations={}, thresholds={"1": 30, "2": 45})
    after = dict(ablations={}, thresholds={1: 30, 2: 45})
    assert module().config_transition(before, after)["main_numerical_configuration_unchanged"]


def test_unrepresented_small_sources_use_full_cap_not_easy_shell_mean():
    sample = pd.DataFrame([dict(unit_key="a", source="D1", nia_m2=18), dict(unit_key="b", source="D3", nia_m2=18)])
    observed = pd.DataFrame([dict(source="D3", nia_m2=18, solve_time_s=10.)])
    summary = dict(concurrent_solves=3, wall_time_s=4., time_limit_s=120)
    _, costs = module().runtime_costs(sample, observed, summary, observed, summary)
    small = costs[costs.group == "small"].set_index("source")
    assert small.loc["D1", "mean_solve_s"] == 120
    assert small.loc["D3", "mean_solve_s"] == 10


def test_caps_preserve_review_floors_and_every_small_d3():
    rows = []
    for source, count, nia in (("D1", 510, 24), ("D2", 210, 24), ("D3", 70, 24), ("D3", 8, 12)):
        rows.extend(dict(unit_key=f"{source}:{nia}:{i}", source=source, nia_m2=nia,
                         nia_bin_2m2=nia, n_rooms=1, projected_hours_with_margin=1.) for i in range(count))
    result, actions = module().cap_sample(pd.DataFrame(rows), 7)
    assert result.source.value_counts().to_dict() == {"D1": 500, "D2": 200, "D3": 68}
    assert len(result[(result.source == "D3")&(result.nia_m2 <= 20)]) == 8
    assert [a["source"] for a in actions] == ["D1", "D2", "D3"]
    assert result.projected_hours_with_margin.sum() > 36  # failure remains visible
