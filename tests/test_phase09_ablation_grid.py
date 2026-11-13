"""Exercise the coarse-grid recovery and its checkpoint boundary."""

import json
import sys
from pathlib import Path

import pytest

from fea.config import config_hash
from fea.io import sha256_file

sys.path.insert(0, str(Path("scripts").resolve()))
from phase09_ablation_jobs import STRATEGIES, changed_config, verified_grid_recovery


def test_resolution_sweep_keeps_the_reviewed_stride_when_representable():
    for stride in (0.10, 0.20):
        base = {"raster": {"resolution_m": 0.10, "anchor_stride_m": stride}, "solver": {"time_limit_s": 120}}
        for res in (0.05, 0.10, 0.20):
            changed = changed_config(base, "resolution_m", res)
            assert changed["raster"]["anchor_stride_m"] == max(stride, res)
            assert changed["raster"]["resolution_m"] == res
            assert changed["solver"] == base["solver"]
        assert base["raster"] == {"resolution_m": 0.10, "anchor_stride_m": stride}


def test_recovery_keeps_old_digests_and_rejects_modified_layouts(tmp_path):
    config = {"raster": {"resolution_m": 0.05, "anchor_stride_m": 0.10}}
    job = dict(task_key="example", household="H1", sample="fixed50", kind="resolution_m", value=0.05,
               config=config, anchor_adjusted=False)
    root = tmp_path / job["task_key"]
    root.mkdir()
    old_fingerprint = "prior"
    layouts, rows = {}, []
    for strategy in STRATEGIES:
        file = root / (strategy + ".json")
        file.write_text(json.dumps({"strategy": strategy}), encoding="utf-8")
        layouts[file.name] = sha256_file(file)
        rows.append(dict(strategy=strategy, task_key=job["task_key"], household=job["household"],
                         sample=job["sample"], ablation=job["kind"], value=job["value"],
                         code_hash=old_fingerprint, config_hash=config_hash(config), layout_sha256=layouts[file.name]))
    (root / "record.json").write_text(json.dumps(dict(fingerprint=old_fingerprint, layouts=layouts, rows=rows)), encoding="utf-8")
    assert verified_grid_recovery(dict(job, anchor_adjusted=True), tmp_path, old_fingerprint) is None
    inherited = verified_grid_recovery(job, tmp_path, old_fingerprint)
    assert [row["layout_sha256"] for row in inherited] == [row["layout_sha256"] for row in rows]
    assert all(row["code_hash"] == old_fingerprint for row in inherited)
    (root / "S2.json").write_text("{}", encoding="utf-8")
    with pytest.raises(ValueError, match="layout digest differs"):
        verified_grid_recovery(job, tmp_path, old_fingerprint)
