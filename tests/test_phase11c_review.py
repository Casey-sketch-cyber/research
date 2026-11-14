"""Check the quality correction and matched review estimates on frozen evidence."""

import importlib.util
from pathlib import Path
import sys

import numpy as np
import pandas as pd
import pytest

from fea.config import load_config


SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))
from phase11c_layouts import catalogue_qualities


def driver(name):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / (name + ".py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_production_benchmarks_retain_pairs_times_and_observed_shortfalls():
    benchmark = driver("11c_recheck_B_C")
    pairs, summary, gaps, audit = benchmark.production_comparison()
    assert len(pairs) == 200 and len(summary) == 4
    assert audit["production_at_best_observed"] == 189
    assert audit["production_at_or_above_annealing"] == 189
    assert len(gaps) == 11
    assert audit["mean_shortfall_all_pairs"] == pytest.approx(.0034056033781033794)
    assert audit["largest_shortfall"] == pytest.approx(.23076923076923084)
    assert summary.set_index("algorithm").loc["production_pipeline", "mean_time_s"] == pytest.approx(53.859689785987136)


def test_catalogue_vector_keeps_geometry_and_can_win_training_ranking():
    kit = driver("11c_recheck_kit")
    config = load_config("config/project.yaml")
    actual = catalogue_qualities(config)
    assert actual == {"wall_bed_single": 1., "wall_bed_double": 1.,
                      "fold_down_desk": .9, "drop_leaf_table": .9}
    grid = kit.load_json(kit.K / "candidate_kits.json")
    shells = pd.read_csv(kit.K / "active_shell_sets.csv")
    train = shells[shells["set"].eq("train")]
    cases = pd.read_csv(kit.K / "cases.csv")
    search = cases[cases["mode"].eq("search") & ~cases.flat_quality & cases.strategy.eq("S2")
                   & cases.unit_key.isin(train.unit_key)]
    catalog = pd.DataFrame([
        {"unit_key": unit, "household": household, "set": "train", "fci": .99, "fciq": .98,
         "validator_pass": True}
        for household in grid for unit in train.unit_key
    ])
    selected, frontier = kit.select(config, train, grid, search, catalog)
    assert all(c["kit_id"] == "catalogue" for c in selected.values())
    assert len(frontier) == 18 and (frontier.n_shells == 30).all()
    assert np.allclose(frontier[frontier.kit_id.eq("catalogue")].mean_item_q, (1 + .9 + .9) / 3)
