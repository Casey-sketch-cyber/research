"""Export the audited showcase layouts and two fixed-seed shells for Blender."""

import json
import math
import time
from pathlib import Path

import numpy as np
import pandas as pd
import yaml
from shapely import constrained_delaunay_triangles, from_wkt
from shapely.geometry import GeometryCollection, LineString
from shapely.geometry.polygon import orient
from shapely.ops import unary_union
from tqdm import tqdm

from fea.furniture.library import library, rectangles
from fea.geometry.raster import rasterize
from fea.geometry.unit import Unit, parts
from fea.households import parse_households
from fea.io import prepare_cli, sha256_file, start_run, write_json
from fea.validate import validate_layout
from phase07_corrected import load_corrected
from phase09_execution import apply_production, hash_inputs, load_json


ROOT = Path("results/renders3d")
F1 = Path("results/expA_f1")
ANALYSIS = F1 / "analysis"
SHOWCASE = ANALYSIS / "layouts/showcase"
RENDER = Path("config/render.yaml")
H1 = "H1_single_commuter"
H3 = "H3_couple_one_remote"
SHELLS = ROOT / "sample_layouts"
SHELL_MANIFEST = SHELLS / "manifest.json"


def triangles(geometry) -> list:
    """Triangulate the normalized area without filling holes."""
    faces = [face for polygon in parts(geometry)
             for face in constrained_delaunay_triangles(polygon).geoms if face.area > 1e-12]
    if abs(sum(t.area for t in faces) - geometry.area) > 1e-7:
        raise ValueError("Scene triangulation changed the source plan area")
    return [[list(point) for point in orient(face).exterior.coords[:-1]] for face in faces]


def scene_walls(unit: Unit, style: dict) -> list:
    """Keep known walls, open doors and windows, and cut away camera-facing edges."""
    spec = style["scene"]
    thickness = spec["wall_thickness"]
    interior = unit.interior
    outer = unary_union([interior, unit.walls])
    known_walls = unit.walls
    if not known_walls.area:
        known_walls = interior.buffer(thickness, join_style="mitre").difference(interior)
        outer = interior
    angle = math.radians(spec["camera"]["azimuth_deg"])
    front = np.array([math.cos(angle), math.sin(angle)])
    facing = []
    for p in parts(outer):
        points = np.asarray(orient(p).exterior.coords)
        for a, b in zip(points[:-1], points[1:]):
            edge = b - a
            length = np.linalg.norm(edge)
            if length > 1e-8 and np.dot(front, [edge[1], -edge[0]]) / length > .45:
                facing.append(LineString([a, b]).buffer(1.8 * thickness, cap_style="flat"))
    cutoff = known_walls.intersection(unary_union(facing))
    rear = known_walls.difference(cutoff)
    door_cut = unary_union([d if d.area > 0 else d.buffer(1.5 * thickness, cap_style="flat") for d in unit.doors])
    window_cut = unary_union([w if w.area > 0 else w.buffer(1.5 * thickness, cap_style="flat") for w in unit.windows])
    # Polygonal openings may already be separated from the wall layer.
    window_zone = rear.intersection(window_cut)
    sill, head, ceiling = .90, 2.20, spec["ceiling_height"]
    sections = [
        (rear.difference(door_cut.union(window_cut)), 0., ceiling, "wall"),
        (rear.intersection(door_cut), 2.10, ceiling, "wall"),
        (window_zone, 0., sill, "wall"),
        (window_zone, head, ceiling, "wall"),
        (window_zone, sill, head, "glazing"),
        (cutoff.difference(door_cut), 0., .07, "wall"),
    ]
    return [{"triangles": triangles(g), "base": base, "top": top, "material": mat}
            for g, base, top, mat in sections if g.area > 1e-8]


def body_polygon(placed: dict, state, resolution: float) -> list:
    """Use the same grid-aligned furniture body as the placement audit."""
    dx, dy, width, depth = rectangles(state, resolution, placed["orientation_deg"])[0]
    x, y = placed["x"] + dx * resolution, placed["y"] + dy * resolution
    w, h = width * resolution, depth * resolution
    return [[x, y], [x+w, y], [x+w, y+h], [x, y+h]]


def material_for(item) -> str:
    """Assign the function color by the furniture family."""
    name = item.name
    if "bed" in name:
        return "sleep"
    if "desk" in name:
        return "work"
    if "table" in name:
        return "dine"
    if "wardrobe" in name or "shelving" in name:
        return "storage"
    return "lounge" if "sofa" in name or "armchair" in name else "fixed"


def make_scene(unit: Unit, layout: dict, config: dict, style: dict, household, row: dict,
               layout_digest: str) -> dict:
    """Serialize masked geometry, all furniture states and validator scores."""
    raster = config["raster"]
    grid = rasterize(unit, raster["resolution_m"], config["furniture"]["meta"]["walking_width"],
                     raster["source_gap_close_m"])
    check = validate_layout(layout, grid, config, household)
    if not check["pass"] or abs(check["fci"] - row["fci_validator"]) > 1e-8 or abs(check["tb"] - row["tb"]) > 1e-8:
        raise ValueError("The scene must match the independently validated layout")
    items = library(config["furniture"], layout["strategy"], household.overrides.get("global_clearance_scale"))
    placed_items = []
    for placed in layout["items"]:
        item = items[placed["type"]]
        states = {s.name: s for s in item.states}
        heights = style["heights"][item.name]
        normal = {}
        for slot, state_name in placed["states"]["normal"].items():
            state = states[state_name]
            normal[slot] = {
                "state": state_name, "outline_m": body_polygon(placed, state, grid.resolution),
                "height_m": heights[state_name] if isinstance(heights, dict) else heights,
                "material": material_for(item),
            }
        placed_items.append({
            "instance_id": placed["instance_id"], "item_type": item.name,
            "anchor_m": [placed["x"], placed["y"]], "orientation_deg": placed["orientation_deg"],
            "states": placed["states"], "normal_day": normal,
        })
    service = unit.classes.get("fixed_service", GeometryCollection()).intersection(unit.interior)
    fixtures = []
    for key, item_type in [("kitchen_geometry", "fixed_kitchenette"), ("toilet_geometry", "fixed_toilet_pod")]:
        if unit.source == "D3" and key in unit.meta:
            area = from_wkt(unit.meta[key]).intersection(unit.interior)
            if area.area > 1e-8:
                fixtures.append({"item_type": item_type, "triangles": triangles(area),
                                 "height_m": style["heights"][item_type]})
    return {
        "unit_key": unit.unit_key, "source": unit.source, "household": household.name,
        "strategy": layout["strategy"], "nia_m2": unit.interior.area, "bounds_m": list(unit.interior.bounds),
        "fci": check["fci"], "tb": check["tb"], "layout_sha256": layout_digest,
        "layout_config_hash": layout["config_hash"], "render_config_sha256": sha256_file(RENDER),
        "floor_triangles": triangles(unit.interior), "service_floor_triangles": triangles(service),
        "walls": scene_walls(unit, style), "doors_wkt": [v.wkt for v in unit.doors],
        "windows_wkt": [v.wkt for v in unit.windows], "entrance_wkt": unit.entrance.wkt,
        "fixed_fixtures": fixtures, "furniture": placed_items,
        "render": {"tool": style["tool"], "scene": style["scene"], "palette": style["palette"]},
    }


def shell_evidence(config: dict, run: dict, picks: list, values, strategies: list, capture: bool) -> dict:
    """Save or read the four audited H1 sample layouts needed to rebuild the scenes."""
    if capture:
        corpus = pd.read_parquet(Path(config["paths"]["processed"]) / "corpus_units.parquet",
                                 columns=["unit_key", "unit_json"]).set_index("unit_key")
        original = load_json(Path("results/expA/run.json"))
        files = []
        for alias, key, hh in picks:
            unit_path = SHELLS / f"{alias}_unit.json"
            write_json(unit_path, Unit.from_dict(json.loads(corpus.loc[key, "unit_json"])).to_dict())
            files.append(unit_path)
            for strategy in strategies:
                row = values.loc[key, hh, strategy]
                stored = Path(original["cache"]) / row["budget_group"] / "shared" / row["layout_file"]
                target = SHELLS / f"{alias}_{strategy}.json"
                target.write_bytes(stored.read_bytes())
                files.append(target)
        write_json(SHELL_MANIFEST, {
            "passed": True,
            "source_solutions_sha256": run["inputs"]["original_solutions_sha256"],
            "picks": [list(row) for row in picks],
            "files": hash_inputs(files),
        })
    manifest = load_json(SHELL_MANIFEST)
    if (not manifest["passed"] or manifest["picks"] != [list(row) for row in picks]
            or manifest["source_solutions_sha256"] != run["inputs"]["original_solutions_sha256"]
            or len(manifest["files"]) != 6):
        raise ValueError("The H1 shell examples differ from the frozen sample")
    for name, sha in manifest["files"].items():
        if sha256_file(Path(name)) != sha:
            raise ValueError("A frozen H1 shell input changed")
    return manifest


def main() -> None:
    """Export all requested scenes and record their accepted layout sources."""
    parser = prepare_cli(__doc__)
    parser.add_argument("--capture-shell-evidence", action="store_true",
                        help="Freeze four H1 examples from the accepted solve cache and processed corpus")
    args = parser.parse_args()
    config, digest, started = start_run(args, "12b_export_scenes")
    if args.dry_run:
        print("Export 3 reviewed H3 showcases and 2 seed-selected H1 shells for S0 and S2.")
        return
    style = yaml.safe_load(RENDER.read_text(encoding="utf-8"))
    corrected, gate = load_corrected(config)
    run = load_json(F1 / "run.json")
    production = run["production_settings"]
    audit = pd.read_csv(ANALYSIS / "layout_audit.csv").set_index(["unit_key", "household", "strategy"])
    examples = pd.read_csv(ANALYSIS / "layout_selection.csv").query("purpose == 'showcase' and strategy == 'S2'")
    picks = [(f"showcase_{int(r.target_nia_m2):02d}", r.unit_key, H3) for r in examples.itertuples(index=False)]
    rng = np.random.default_rng(config["seed"])
    shell_picks = []
    for area in (8, 12):
        units = sorted(corrected[corrected.source.eq("D3") & corrected.nia_m2.sub(area).abs().lt(1e-6)].unit_key.unique())
        shell_picks.append((f"shell_{area:02d}", str(rng.choice(units)), H1))
    picks.extend(shell_picks)
    values = corrected.set_index(["unit_key", "household", "strategy"])
    strategies = style["outputs"]["stills"]["strategies"]
    shell_evidence(config, run, shell_picks, values, strategies, args.capture_shell_evidence)
    index = []
    for alias, unit_key, household in tqdm(picks, desc="Exporting reviewed 3D scenes"):
        for strategy in strategies:
            row = values.loc[unit_key, household, strategy].to_dict()
            if alias.startswith("showcase"):
                entry = audit.loc[unit_key, household, strategy]
                path = Path(entry.file_stem + ".json")
                if sha256_file(path) != entry.layout_sha256:
                    raise ValueError("A corrected showcase layout changed")
                unit = Unit.from_dict(load_json(SHOWCASE / (unit_key.replace(":", "_") + "_unit.json")))
            else:
                path = SHELLS / f"{alias}_{strategy}.json"
                unit = Unit.from_dict(load_json(SHELLS / f"{alias}_unit.json"))
            layout = load_json(path)
            if any(layout[name] != val for name, val in [
                ("unit_key", unit_key), ("household", household), ("strategy", strategy),
                ("config_hash", row["config_hash"]), ("code_hash", row["code_hash"]),
            ]):
                raise ValueError("A scene layout does not match its accepted case")
            cfg, _ = apply_production(config, production, unit.interior.area)
            hh = parse_households(cfg["households"], cfg["furniture"])[household]
            result = make_scene(unit, layout, cfg, style, hh, row, sha256_file(path))
            stem = f"{unit_key.replace(':', '_')}_{household.split('_')[0]}_{strategy}"
            target = ROOT / "scenes" / (stem + ".json")
            write_json(target, result)
            index.append({"scene": target.as_posix(), "scene_sha256": sha256_file(target),
                          "alias": alias, "strategy": strategy, "slots": style["outputs"]["stills"]["slots"]})
    if len(index) != 10 or len(picks) != 5:
        raise ValueError("Incomplete 3D scope")
    write_json(ROOT / "scene_index.json", {
        "passed": True, "config_hash": digest, "seed": config["seed"], "layout_cases": len(index),
        "source_H1_samples_sha256": sha256_file(SHELL_MANIFEST),
        "elapsed_seconds": round(time.perf_counter()-started, 3),
        "source_F1_solutions_sha256": gate["combined_sha256"], "render_config_sha256": sha256_file(RENDER),
        "scenes": index, "outputs": hash_inputs([r["scene"] for r in index]),
    })


if __name__ == "__main__":
    main()
