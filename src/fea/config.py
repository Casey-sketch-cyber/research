"""Configuration loading, explicit overrides and reproducibility hashes."""
from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
from typing import Any

import yaml


def load_config(path: str | Path) -> dict[str, Any]:
    """Read project plus furniture and household files without applying proposals."""
    path = Path(path)
    project = yaml.safe_load(path.read_text(encoding="utf-8"))
    for name in ("furniture", "households"):
        project[name] = yaml.safe_load((path.parent / f"{name}.yaml").read_text(encoding="utf-8"))
    return project


def config_hash(config: dict[str, Any]) -> str:
    """Hash semantic configuration, independent of machine paths and YAML layout."""
    return hashlib.sha256(json.dumps(config, sort_keys=True, separators=(",", ":"),
                                     ensure_ascii=False).encode()).hexdigest()


def merge_override(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    """Return a deep merge; callers must explicitly opt into approved overrides."""
    result = copy.deepcopy(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = merge_override(result[key], value)
        else:
            result[key] = copy.deepcopy(value)
    return result
