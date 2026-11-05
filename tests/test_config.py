"""Configuration provenance must change when a scientific input changes."""
from fea.config import config_hash, merge_override


def test_hash_semantics_and_explicit_merge():
    base = {"seed": 42, "solver": {"workers": 2, "seconds": 60}}
    assert config_hash(base) == config_hash(dict(reversed(list(base.items()))))
    changed = merge_override(base, {"solver": {"seconds": 30}})
    assert changed["solver"]["workers"] == 2
    assert base["solver"]["seconds"] == 60
    assert config_hash(changed) != config_hash(base)
