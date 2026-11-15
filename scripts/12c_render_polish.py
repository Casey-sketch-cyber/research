"""Render the presentation views requested in the G4 review."""

import argparse
from copy import deepcopy
from importlib import import_module
import json
import logging
from pathlib import Path
import sys
import time


sys.path.insert(0, str(Path(__file__).resolve().parent))
base = import_module("12b_render3d")
ROOT = base.ROOT
OUTPUT = ROOT / "polish"
CHECKPOINTS = Path(".tmp/phase12c_render")
SLOTS = ("night", "day", "dinner")
STRATEGIES = ("S0", "S2")


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def presentation_views(index: dict):
    """Prepare cutaway and matched room views from the approved scene geometry."""
    scenes = {}
    for entry in index["scenes"]:
        if entry["alias"] not in ("showcase_10", "showcase_30"):
            continue
        source = Path(entry["scene"])
        if base.digest(source) != entry["scene_sha256"]:
            raise ValueError(f"Approved scene differs: {source}")
        scenes[(entry["alias"], entry["strategy"])] = entry, load(source)

    # The furniture in both accepted daytime layouts sets the same close-up framing.
    points = [point for strategy in STRATEGIES
              for item in scenes[("showcase_30", strategy)][1]["furniture"]
              for point in item["normal_day"]["day"]["outline_m"]]
    x, y = zip(*points)
    detail_bounds = [min(x), min(y), max(x), max(y)]

    for strategy in STRATEGIES:
        entry, original = scenes[("showcase_10", strategy)]
        cutaway = deepcopy(original)
        pod, = [fixture for fixture in cutaway["fixed_fixtures"] if fixture["item_type"] == "fixed_toilet_pod"]
        pod["height_m"] = .34
        for slot in SLOTS:
            yield entry, cutaway, slot, "cutaway", {"toilet_enclosure_cutaway_height_m": pod["height_m"]}

        entry, original = scenes[("showcase_30", strategy)]
        detail = deepcopy(original)
        detail["bounds_m"] = detail_bounds
        detail["render"]["scene"]["camera"]["elevation_deg"] = 60
        # Low wall sections keep the room footprint and reveal furniture behind the foreground walls.
        wall_cut = .38
        detail["walls"] = [{**wall, "top": min(wall["top"], wall_cut)}
                           for wall in detail["walls"] if wall["base"] < wall_cut]
        yield entry, detail, "day", "detail", {
            "camera_bounds_m": detail_bounds, "camera_elevation_deg": 60, "wall_cutaway_height_m": wall_cut,
        }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=Path("config/render.yaml"))
    parser.add_argument("--threads", type=int, default=4)
    parser.add_argument("--device", choices=["cpu", "cuda"], default="cpu")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else None)
    if args.dry_run:
        print("Render six cutaway views of showcase_10 and two daytime detail views of showcase_30.")
        return

    import bpy

    started = time.perf_counter()
    logs = Path("logs")
    logs.mkdir(exist_ok=True)
    logging.basicConfig(filename=logs / "12c_render_polish.log", level=logging.INFO, encoding="utf-8")
    index_path = ROOT / "scene_index.json"
    index = load(index_path)
    accepted = load(ROOT / "render_manifest.json")
    index_sha = base.digest(index_path)
    base_sha = base.digest(Path(base.__file__))
    if (not index["passed"] or not accepted["passed"] or accepted["scene_index_sha256"] != index_sha
            or index["render_config_sha256"] != base.digest(args.config) or accepted["renderer_sha256"] != base_sha):
        raise ValueError("The approved Phase 12b scenes or renderer differ")
    header = {
        "scene_index_sha256": index_sha, "base_renderer_sha256": base_sha,
        "polish_renderer_sha256": base.digest(Path(__file__)),
        "blender_version": bpy.app.version_string, "cycles_backend": args.device,
    }
    frames = []
    for entry, scene, slot, view, parameters in presentation_views(index):
        stem = f"{entry['alias']}_{entry['strategy']}_{slot}_{view}"
        still = OUTPUT / (stem + ".png")
        checkpoint = CHECKPOINTS / (stem + ".json")
        identity = {**header, "scene_sha256": entry["scene_sha256"], "slot": slot,
                    "view": view, "parameters": parameters}
        prior = load(checkpoint) if checkpoint.is_file() else {}
        if not (prior.get("identity") == identity and still.is_file()
                and base.digest(still) == prior["sha256"]):
            base.render_view(bpy, scene, slot, still, args.threads, False, None, args.device)
            base.write(checkpoint, {"identity": identity, "sha256": base.digest(still)})
        frames.append({
            "alias": entry["alias"], "strategy": entry["strategy"], "slot": slot, "view": view,
            "parameters": parameters, "scene_sha256": entry["scene_sha256"],
            "still": still.as_posix(), "sha256": base.digest(still),
        })
        logging.info("Verified %s", stem)
        print(f"Presentation views {len(frames)} / 8: {stem}", flush=True)
    if len(frames) != 8:
        raise ValueError("Incomplete G4 presentation views")
    base.write(OUTPUT / "manifest.json", {
        "passed": True, **header, "frames": frames, "elapsed_seconds": time.perf_counter() - started,
    })


if __name__ == "__main__":
    main()
