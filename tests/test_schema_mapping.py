"""Every observed D1 area subtype must have exactly one explicit class."""
import json
from pathlib import Path

import pytest

from fea.config import load_config


def test_explicit_d1_mapping_covers_observed_types():
    mapping = load_config("config/project.yaml")["corpus"]["d1_subtype_classes"]
    entries = sum(mapping.values(), [])
    assert len(entries) == len(set(entries))
    assert all("TODO" not in value for value in entries)
    summary = Path("reports/schemas/D1_summary.json")
    if not summary.exists():
        pytest.skip("Run schema inspection to check against observed data")
    observed = set(json.loads(summary.read_text(encoding="utf-8"))["area_subtypes"])
    assert set(entries) == observed
