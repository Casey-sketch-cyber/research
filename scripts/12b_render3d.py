"""Render the validated scene descriptions with headless Blender."""

import argparse
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import sys
import time


ROOT = Path("results/renders3d")


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    temporary.replace(path)


def linear_color(hex_color: str) -> tuple:
    """Convert the display palette to linear RGB for Blender materials."""
    values = [int(hex_color[i:i+2], 16)/255 for i in (1, 3, 5)]
    return (*[x/12.92 if x <= .04045 else ((x+.055)/1.055)**2.4 for x in values], 1.)


def materials(bpy, palette: dict) -> dict:
    """Use the same palette and surface finish throughout the render set."""
    colors = {**palette, "floor": "#E7D4B7", "wall": "#EAE8E2", "glazing": "#C1DCEB",
              "ground": "#F3F5F6", "service": "#D0D6D8", "linen": "#CFDFF2"}
    result = {}
    for name, color in colors.items():
        mat = bpy.data.materials.new(name)
        mat.diffuse_color = linear_color(color)
        mat.use_nodes = True
        surface = mat.node_tree.nodes.get("Principled BSDF")
        surface.inputs["Base Color"].default_value = mat.diffuse_color
        surface.inputs["Roughness"].default_value = .73
        if name == "glazing":
            surface.inputs["Roughness"].default_value = .24
        result[name] = mat
    return result


def slab(bpy, name: str, triangles: list, bottom: float, top: float, material):
    """Extrude a triangulation with solid boundary faces and open polygon holes."""
    if not triangles:
        return None
    indices, vertices, faces, segments = {}, [], [], {}
    for tri in triangles:
        ids = []
        for value in tri:
            point = tuple(value)
            if point not in indices:
                indices[point] = len(vertices)
                vertices.extend([(point[0], point[1], bottom), (point[0], point[1], top)])
            ids.append(indices[point])
        faces.extend([tuple(reversed(ids)), tuple(i + 1 for i in ids)])
        for i, j in zip(ids, ids[1:] + ids[:1]):
            edge = tuple(sorted((i, j)))
            if edge in segments:
                segments[edge] = None
            else:
                segments[edge] = (i, j)
    faces.extend((a, b, b+1, a+1) for item in segments.values() if item for a, b in [item])
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    obj.data.materials.append(material)
    return obj


def box(bpy, name: str, bounds: tuple, z0: float, z1: float, material, bevel: float = .006):
    """Place a beveled box at a known footprint without changing its extents."""
    x0, y0, x1, y1 = bounds
    ring = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
    obs = slab(bpy, name, [ring[:3], [ring[0], ring[2], ring[3]]], z0, z1, material)
    if bevel:
        mod = obs.modifiers.new("Edge bevel", "BEVEL")
        mod.width = bevel
        mod.segments = 3
        mod.limit_method = "ANGLE"
    return obs


def furnish(bpy, item: dict, slot: str, palette: dict):
    """Build a state-specific body with simple legs or insets where appropriate."""
    data = item["normal_day"][slot]
    x, y = zip(*data["outline_m"])
    xmin, ymin, xmax, ymax = min(x), min(y), max(x), max(y)
    bounds = xmin, ymin, xmax, ymax
    height = data["height_m"]
    mat, kind, ids = palette[data["material"]], item["item_type"], item["instance_id"]
    if ("table" in kind or "desk" in kind) and data["state"] != "stowed":
        top = box(bpy, ids, bounds, height-.065, height, mat)
        leg = min(.055, (xmax-xmin)/6, (ymax-ymin)/6)
        for u in (xmin+leg/2, xmax-1.5*leg):
            for v in (ymin+leg/2, ymax-1.5*leg):
                box(bpy, ids + " support", (u, v, u+leg, v+leg), 0., height-.06, mat, bevel=.003)
        return top
    if "bed" in kind and data["state"] != "stowed":
        body = box(bpy, ids, bounds, 0., height-.045, mat)
        margin = .045
        inset = xmin+margin, ymin+margin, xmax-margin, ymax-margin
        if inset[0] < inset[2] and inset[1] < inset[3]:
            box(bpy, ids + " bedding", inset, height-.06, height, palette["linen"], bevel=.008)
        return body
    return box(bpy, ids, bounds, 0., height, mat)


def camera(bpy, name: str):
    data = bpy.data.cameras.new(name)
    obj = bpy.data.objects.new(name, data)
    bpy.context.scene.collection.objects.link(obj)
    data.type = "ORTHO"
    data.clip_end = 200
    bpy.context.scene.camera = obj
    return obj


def render_view(bpy, record: dict, slot: str, target: Path, threads: int, preview: bool,
                audit: Path | None, backend: str) -> None:
    """Render one axonometric view and optionally capture its top projection."""
    from mathutils import Vector
    from bpy_extras.object_utils import world_to_camera_view

    bpy.ops.wm.read_factory_settings(use_empty=True)
    active = bpy.context.scene
    cfg = record["render"]
    pal = materials(bpy, cfg["palette"])
    active.render.engine = cfg["tool"]["engine"]
    active.render.threads_mode = "FIXED"
    active.render.threads = threads
    active.render.resolution_x, active.render.resolution_y = cfg["tool"]["resolution"]
    active.render.resolution_percentage = 48 if preview else 100
    active.render.image_settings.file_format = "PNG"
    active.render.image_settings.color_mode = "RGB"
    active.render.image_settings.compression = 50
    active.render.use_stamp = False
    active.render.film_transparent = False
    if backend == "cuda":
        prefs = bpy.context.preferences.addons["cycles"].preferences
        prefs.compute_device_type = "CUDA"
        prefs.refresh_devices()
        if not any(device.type == "CUDA" for device in prefs.devices):
            raise RuntimeError("No CUDA device available. Use the default CPU backend.")
        for device in prefs.devices:
            device.use = device.type == "CUDA"
    active.cycles.device = "GPU" if backend == "cuda" else "CPU"
    active.cycles.samples = 10 if preview else cfg["tool"]["samples"]
    active.cycles.use_denoising = cfg["tool"]["denoise"]
    active.cycles.seed = 12
    active.cycles.adaptive_threshold = .025
    active.world = bpy.data.worlds.new("Soft environment")
    active.world.use_nodes = True
    active.world.node_tree.nodes.get("Background").inputs[0].default_value = (.72, .77, .83, 1.)
    active.world.node_tree.nodes.get("Background").inputs[1].default_value = .42
    active.view_settings.view_transform = "AgX"
    x0, y0, x1, y1 = record["bounds_m"]
    cx, cy = (x0+x1)/2, (y0+y1)/2
    box(bpy, "Backdrop", (cx-40, cy-40, cx+40, cy+40), -.20, -.145, pal["ground"], 0.)
    slab(bpy, "Floor", record["floor_triangles"], -.13, 0., pal["floor"])
    slab(bpy, "Service floor", record["service_floor_triangles"], -.01, .006, pal["service"])
    for part in record["walls"]:
        slab(bpy, part["material"], part["triangles"], part["base"], part["top"], pal[part["material"]])
    for fixture in record["fixed_fixtures"]:
        slab(bpy, fixture["item_type"], fixture["triangles"], 0., fixture["height_m"], pal["fixed"])
    bodies = {i["instance_id"]: furnish(bpy, i, slot, pal) for i in record["furniture"]}
    sun = bpy.data.lights.new("Daylight", "SUN")
    light = bpy.data.objects.new("Daylight", sun)
    active.collection.objects.link(light)
    light.rotation_euler = (math.radians(29), math.radians(-25), math.radians(-35))
    sun.energy, sun.angle = 1.65, math.radians(14)
    specification = cfg["scene"]["camera"]
    azimuth = math.radians(specification["azimuth_deg"])
    elevation = math.radians(specification["elevation_deg"])
    look = Vector((math.cos(azimuth)*math.cos(elevation), math.sin(azimuth)*math.cos(elevation), math.sin(elevation)))
    target_center = Vector((cx, cy, cfg["scene"]["ceiling_height"]*.40))
    cam = camera(bpy, "Locked axonometric camera")
    cam.location = target_center + 18*look
    cam.rotation_euler = (-look).to_track_quat("-Z", "Y").to_euler()
    bpy.context.view_layer.update()
    inverse = cam.matrix_world.inverted()
    points = [inverse @ Vector((x, y, z)) for x in (x0-.18, x1+.18) for y in (y0-.18, y1+.18)
              for z in (-.13, cfg["scene"]["ceiling_height"])]
    width, depth = [2 * max(abs(p[i]) for p in points) for i in (0, 1)]
    ratio = active.render.resolution_x / active.render.resolution_y
    cam.data.ortho_scale = 1.085 * max(width, depth*ratio)
    target.parent.mkdir(parents=True, exist_ok=True)
    active.render.filepath = str(target)
    bpy.ops.render.render(write_still=True)
    if audit is not None:
        top = camera(bpy, "Orthographic geometry audit")
        edge = max(x1-x0, y1-y0) + .5
        top.location = (cx, cy, 22.)
        top.rotation_euler = (0., 0., 0.)
        top.data.ortho_scale = edge
        active.render.resolution_x = active.render.resolution_y = 1200
        active.render.resolution_percentage = 100
        active.cycles.samples = 12
        bpy.context.view_layer.update()
        depsgraph = bpy.context.evaluated_depsgraph_get()
        projected = {}
        for name, body in bodies.items():
            evaluated = body.evaluated_get(depsgraph)
            projected[name] = []
            for pt in evaluated.data.vertices:
                vec = world_to_camera_view(active, top, evaluated.matrix_world @ pt.co)
                projected[name].append([float(cx + (vec.x-.5)*edge), float(cy + (vec.y-.5)*edge)])
        audit.parent.mkdir(parents=True, exist_ok=True)
        active.render.filepath = str(audit.with_suffix(".png"))
        bpy.ops.render.render(write_still=True)
        write(audit.with_suffix(".json"), {
            "unit_key": record["unit_key"], "slot": slot, "strategy": record["strategy"],
            "bounds_m": [cx-edge/2, cy-edge/2, cx+edge/2, cy+edge/2],
            "pixels": [1200, 1200], "projected_body_vertices_m": projected,
            "top_render_sha256": digest(audit.with_suffix(".png")),
        })


def main() -> None:
    """Render all configured stills or one size preview, with per-view checkpoints."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=Path("config/render.yaml"))
    parser.add_argument("--threads", type=int, default=4)
    parser.add_argument("--device", choices=["cpu", "cuda"], default="cpu")
    parser.add_argument("--preview", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(sys.argv[sys.argv.index("--")+1:] if "--" in sys.argv else None)
    if args.dry_run:
        print("Render 30 stills from 10 accepted descriptions and check three S2 daytime projections.")
        return
    import bpy

    if bpy.app.version < (4, 2, 0):
        raise ValueError("The headless renderer requires Blender 4.2 or newer")
    started = time.perf_counter()
    source = ROOT / "scene_index.json"
    index = json.loads(source.read_text(encoding="utf-8"))
    cfg_sha = digest(args.config)
    if not index["passed"] or index["render_config_sha256"] != cfg_sha:
        raise ValueError("Render configuration differs from scene descriptions")
    if args.preview:
        output = Path(".tmp/g4_render/preview")
    else:
        output = ROOT / "stills"
    state = Path(".tmp/g4_render")
    state.mkdir(parents=True, exist_ok=True)
    header = {"renderer_sha256": digest(Path(__file__)), "render_config_sha256": cfg_sha,
              "blender_version": bpy.app.version_string, "cycles_backend": args.device}
    frames = []
    for entry in index["scenes"]:
        alias, strategy = entry["alias"], entry["strategy"]
        if args.preview and (alias, strategy) != ("showcase_18", "S2"):
            continue
        path = Path(entry["scene"])
        if digest(path) != entry["scene_sha256"]:
            raise ValueError("Scene digest differs")
        record = json.loads(path.read_text(encoding="utf-8"))
        for slot in entry["slots"]:
            if args.preview and slot != "day":
                continue
            label = f"{alias}_{strategy}_{slot}"
            target = output / (label + ".png")
            audit = (ROOT / "audits" / label) if not args.preview and (
                alias.startswith("showcase") and strategy == "S2" and slot == "day"
            ) else None
            mark = state / ("preview.json" if args.preview else label + ".json")
            inputs = {**header, "scene_sha256": entry["scene_sha256"], "slot": slot, "preview": args.preview}
            prior = json.loads(mark.read_text(encoding="utf-8")) if mark.exists() else {}
            if prior.get("inputs") == inputs and all(Path(p).is_file() and digest(Path(p)) == d
                                                     for p, d in prior["outputs"].items()):
                outputs = prior["outputs"]
            else:
                render_view(bpy, record, slot, target, args.threads, args.preview, audit, args.device)
                paths = [target] if audit is None else [target, audit.with_suffix(".png"), audit.with_suffix(".json")]
                outputs = {p.as_posix(): digest(p) for p in paths}
                write(mark, {"inputs": inputs, "outputs": outputs})
            frames.append({**entry, "slot": slot, "still": target.as_posix(), "audit": audit.as_posix() if audit else None,
                           "outputs": outputs})
            print(f"Rendered {len(frames)} / {1 if args.preview else 30}: {label}", flush=True)
    if not args.preview:
        if len(frames) != 30 or sum(bool(row["audit"]) for row in frames) != 3:
            raise ValueError("Incomplete rendering scope")
        write(ROOT / "render_manifest.json", {
            "passed": True, **header, "scene_index_sha256": digest(source), "stills": len(frames),
            "frames": frames, "elapsed_seconds": time.perf_counter()-started,
            "completed_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        })


if __name__ == "__main__":
    main()
