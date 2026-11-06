"""Configuration provenance must change when a scientific input changes."""
from fea.config import config_hash, merge_override


def test_hash_semantics_and_explicit_merge():
    base = {"seed": 42, "solver": {"workers": 2, "seconds": 60}}
    assert config_hash(base) == config_hash(dict(reversed(list(base.items()))))
    changed = merge_override(base, {"solver": {"seconds": 30}})
    assert changed["solver"]["workers"] == 2
    assert base["solver"]["seconds"] == 60
    assert config_hash(changed) != config_hash(base)


def test_g2_freeze_preserves_ablation_budget_and_other_inputs(tmp_path):
    import importlib.util
    from copy import deepcopy
    from pathlib import Path
    import shutil
    from fea.config import load_config

    spec = importlib.util.spec_from_file_location('g2_report', Path('scripts/06_revision_report.py'))
    report = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(report)
    target = tmp_path / 'config'
    shutil.copytree('config', target)
    path = target / 'project.yaml'
    before = load_config(path)
    expected = deepcopy(before)
    expected['solver'].update(num_workers=1, time_limit_s=30, reachability_round_s=5.0)
    result = report.freeze_configuration({'workers': 1, 'time_limit_s': 30, 'anchor_stride_m': .2}, path)
    assert result == expected
    assert result['ablations']['time_limit_s'] == {'values': [30, 60, 120], 'subset': 50}
    assert result['experiments']['K_kit_design']['search']['time_limit_s'] == 20
    assert report.freeze_configuration({'workers': 1, 'time_limit_s': 30, 'anchor_stride_m': .2}, path) == expected
