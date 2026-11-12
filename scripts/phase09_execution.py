"""Runtime helpers for independent case jobs with bounded solver concurrency."""
from concurrent.futures import FIRST_COMPLETED, ProcessPoolExecutor, wait
from copy import deepcopy
import hashlib
import json
import os
from pathlib import Path

from fea.io import sha256_file


def load_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def hash_inputs(paths):
    return {Path(path).as_posix(): sha256_file(Path(path)) for path in paths}


def fingerprint(values):
    return hashlib.sha256(json.dumps(values, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def cpu_slots():
    """Use both affinity and the process quota where available."""
    count = len(os.sched_getaffinity(0)) if hasattr(os, "sched_getaffinity") else os.cpu_count() or 1
    v2 = Path("/sys/fs/cgroup/cpu.max")
    if v2.is_file():
        quota, period = v2.read_text().split()
        if quota != "max":
            count = min(count, max(1, int(quota) // int(period)))
    return count


def run_weighted(worker, tasks, slots):
    """Yield results while allocating each task its configured solver workers."""
    queue = sorted(tasks, key=lambda task: -task["threads"])
    if queue and queue[0]["threads"] > slots:
        raise ValueError("A solve requires more workers than the available CPU budget")
    with ProcessPoolExecutor(max_workers=slots) as pool:
        active = {}
        available = slots
        while queue or active:
            while queue:
                index = next((i for i, task in enumerate(queue) if task["threads"] <= available), None)
                if index is None:
                    break
                task = queue.pop(index)
                future = pool.submit(worker, task)
                active[future] = task["threads"]
                available -= task["threads"]
            completed, _ = wait(active, return_when=FIRST_COMPLETED)
            for future in completed:
                available += active.pop(future)
                yield future.result()


def apply_production(base, production, nia):
    """Apply the reviewed small/large solve settings for a physical unit."""
    cfg = deepcopy(base)
    group = "small" if nia <= 20 + 1e-8 else "large"
    settings = production[group]
    cfg["solver"].update({key: settings[key] for key in ("time_limit_s", "num_workers")})
    cfg["raster"]["anchor_stride_m"] = settings["anchor_stride_m"]
    return cfg, group


def checked_inputs(manifest):
    for path, digest in manifest.items():
        if sha256_file(Path(path)) != digest:
            raise ValueError("Input or accepted artifact changed: " + path)

