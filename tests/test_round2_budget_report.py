"""A known paired score gap must select the reviewed budget without cherry-picking."""
import importlib.util
import json
from pathlib import Path
import sys

import pandas as pd


def test_complete_pair_comparison_selects_and_rejects_medium_budget(tmp_path, monkeypatch):
    repository = Path.cwd()
    spec = importlib.util.spec_from_file_location("budget_report", repository/"scripts/06_round2_budget_report.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    root = tmp_path/"results/pilot/round2"
    arms = [("small_final_w8_t300", 8, 300, .7), ("small_final_w4_t120", 4, 120, .695),
            ("small_final_w1_t30", 1, 30, .5)]
    for name, workers, limit, score in arms:
        folder = root/name
        folder.mkdir(parents=True)
        (folder/"summary.json").write_text(json.dumps(dict(code_hash="same", inputs_hash="frozen",
            num_workers=workers, time_limit_s=limit)))
        rows = [dict(unit_key=f"test:{u}", household=f"H{h}", strategy=s, source="D3", nia_m2=9+u*.4,
                     fci_validator=score if s == "S2" else .5, tb=0., solve_time_s=1., validator_pass=True)
                for u in range(16) for h in range(1, 5) for s in ("S1", "S2")]
        pd.DataFrame(rows).to_csv(folder/"cases.csv", index=False)
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(sys, "argv", ["report", "--config", str(repository/"config/project.yaml")])
    module.main()
    assessment = json.loads((root/"small_budget_assessment.json").read_text())
    assert assessment["time_limit_s"] == 120
    assert assessment["long_gain_missing_in_short_pairs"] == 64
    assert assessment["formal_experiment_authorized_by_this_file"] is False
    path = root/"small_final_w4_t120/cases.csv"
    medium = pd.read_csv(path)
    medium.loc[medium.strategy == "S2", "fci_validator"] = .68
    medium.to_csv(path, index=False)
    module.main()
    assert json.loads((root/"small_budget_assessment.json").read_text())["time_limit_s"] == 300
