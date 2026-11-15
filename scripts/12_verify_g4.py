"""Validate and fingerprint the Phase 12 package for G4 review."""

import argparse
from hashlib import sha256
import json
import re
from pathlib import Path

import numpy as np
import pandas as pd
import yaml
from PIL import Image

from fea.io import sha256_file
from phase12_artifacts import write_manifest


RESULTS = Path("results")
FIGURES = RESULTS / "figures/g4"
TABLES = RESULTS / "tables/g4"
RENDERS = RESULTS / "renders3d"
K = RESULTS / "g3_review_k3"
GATE = RESULTS / "g4"
MANIFEST = GATE / "release_manifest.json"
VISUAL = GATE / "visual_review.json"
TESTS = GATE / "test_receipt.json"
CONFIG = Path("config/render.yaml")
SCRIPTS = [Path(f"scripts/{name}.py") for name in (
    "12_make_figures", "12_make_tables", "12b_export_scenes", "12b_render3d", "12_verify_g4", "phase12_artifacts",
)]
SANITIZED = {Path(p) for p in ("docs/PROCEDURES.md", "reports/ENVIRONMENT.md",
                                "reports/environment.json", "scripts/00_env_report.py")}
DRAFTS = [Path("manuscript/draft_methods.md"), Path("manuscript/draft_results.md")]
REPORTS = [Path(f"reports/{name}.md") for name in (
    "GATE_G4", "FINAL_SUMMARY", "phase_12_G4", "DECISIONS",
)]


def require(ok, message):
    if not ok:
        raise ValueError(message)


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def hashes(records):
    for name, digest in records.items():
        path = Path(name)
        require(not path.is_absolute() and ".." not in path.parts, "Evidence paths must be repository-relative")
        require(path.is_file() and sha256_file(path) == digest, f"Changed evidence: {name}")
    return {Path(p) for p in records}


def figure_names():
    return [f"F{i}" for i in range(1, 13)] + ["F3b_10", "F3b_18", "F3b_30"]


def check_figures_and_tables():
    groups = [FIGURES / "manifest_2d.json", FIGURES / "manifest_3d.json", TABLES / "manifest.json"]
    files = set(groups)
    outputs = set()
    for path in groups:
        chart = read(path)
        require(chart["passed"], f"Incomplete evidence group: {path}")
        files |= hashes(chart["inputs"])
        outputs |= hashes(chart["outputs"])
    figure_set = {FIGURES / f"{name}.{ext}" for name in figure_names() for ext in ("pdf", "png")}
    table_set = {TABLES / f"T{n}.{ext}" for n in range(1, 8) for ext in ("csv", "md")}
    require(figure_set == {p for p in outputs if p.parent == FIGURES}, "Wrong figure scope")
    require(table_set == {p for p in outputs if p.parent == TABLES}, "Wrong table scope")
    for png in (p for p in figure_set if p.suffix == ".png"):
        with Image.open(png) as im:
            require(all(abs(d-300) < .1 for d in im.info.get("dpi", (0, 0))), f"Wrong resolution: {png}")
            im.verify()
    for pdf in (p for p in figure_set if p.suffix == ".pdf"):
        with pdf.open("rb") as stream:
            require(stream.read(5) == b"%PDF-", f"Invalid PDF: {pdf}")
    return files | outputs, figure_set


def verify_normalization(index, render, index_path):
    """Confirm that a normalized release points to exactly the original render inputs."""
    binding = render.get("config_normalization")
    if binding is None:
        return
    old = binding["original_config_sha256"]
    canonical = index["render_config_sha256"]
    require(binding["line_endings"] == "CRLF to LF" and
            sha256(CONFIG.read_bytes().replace(b"\n", b"\r\n")).hexdigest() == old,
            "Render configuration migration changed content")
    entries = binding["scene_bindings"]
    require(entries.keys() == index["outputs"].keys(), "Incomplete line-ending migration")
    for name, hashes in entries.items():
        data = Path(name).read_bytes()
        restored = data.replace(canonical.encode(), old.encode())
        require(data.count(canonical.encode()) == 1 and
                sha256(restored).hexdigest() == hashes["original"] and hashes["published"] == index["outputs"][name],
                "A scene changed beyond the configuration digest")
    restored = index_path.read_bytes().replace(canonical.encode(), old.encode())
    for row in entries.values():
        restored = restored.replace(row["published"].encode(), row["original"].encode())
    require(sha256(restored).hexdigest() == binding["original_scene_index_sha256"], "Original scene index differs")


def check_render_set():
    index_path, render_path = RENDERS / "scene_index.json", RENDERS / "render_manifest.json"
    sample_path = RENDERS / "sample_layouts/manifest.json"
    index, render, sample = read(index_path), read(render_path), read(sample_path)
    require(index["passed"] and render["passed"] and sample["passed"], "Incomplete render stage")
    require(index["source_H1_samples_sha256"] == sha256_file(sample_path), "H1 source changed")
    require(render["scene_index_sha256"] == sha256_file(index_path), "Scene index changed")
    require(render["render_config_sha256"] == index["render_config_sha256"] == sha256_file(CONFIG),
            "Render settings changed")
    require(render["renderer_sha256"] == sha256_file(SCRIPTS[3]), "Renderer changed")
    verify_normalization(index, render, index_path)
    source = read(RESULTS / "expA_f1/acceptance.json")
    require(index["source_F1_solutions_sha256"] == source["combined_sha256"], "Wrong F1 release")
    files = {index_path, render_path, sample_path, CONFIG} | hashes(index["outputs"]) | hashes(sample["files"])
    style = yaml.safe_load(CONFIG.read_text(encoding="utf-8"))
    slots = style["outputs"]["stills"]["slots"]
    strategies = style["outputs"]["stills"]["strategies"]
    aliases = {"showcase_10", "showcase_18", "showcase_30", "shell_08", "shell_12"}
    pairs = {(e["alias"], e["strategy"]): e for e in index["scenes"]}
    require(len(index["scenes"]) == index["layout_cases"] == len(pairs) == 10, "Wrong scene count")
    require(pairs.keys() == {(a, s) for a in aliases for s in strategies}, "Wrong scene scope")
    by_unit = {}
    for (alias, strategy), row in pairs.items():
        scene = read(Path(row["scene"]))
        require(index["outputs"][row["scene"]] == row["scene_sha256"], "Wrong scene receipt")
        require(row["slots"] == slots and scene["strategy"] == strategy and scene["render"] == {
            key: style[key] for key in ("tool", "scene", "palette")
        }, "Camera, light or strategy mismatch")
        unit = scene["unit_key"], scene["bounds_m"], scene["household"]
        require(by_unit.setdefault(alias, unit) == unit, "A strategy changed the viewing envelope")
    actual, projections = set(), set()
    for frame in render["frames"]:
        alias, strategy, slot = frame["alias"], frame["strategy"], frame["slot"]
        key = alias, strategy, slot
        require(key not in actual, "Duplicate render")
        actual.add(key)
        files |= hashes(frame["outputs"])
        require(pairs[(alias, strategy)]["scene_sha256"] == frame["scene_sha256"], "Wrong render source")
        still = Path(frame["still"])
        require(still.as_posix() in frame["outputs"], "Unbound render")
        with Image.open(still) as im:
            require(list(im.size) == style["tool"]["resolution"], f"Wrong frame dimensions: {still}")
            im.verify()
        if frame["audit"]:
            projections.add((alias, strategy, slot))
    require(len(actual) == render["stills"] == 30 and
            actual == {(a, s, t) for a, s in pairs for t in slots}, "Wrong render scope")
    require(projections == {(a, "S2", "day") for a in aliases if a.startswith("showcase")},
            "Wrong projection scope")
    audit_path = RENDERS / "geometry_audit.csv"
    audit = pd.read_csv(audit_path)
    require(tuple(sorted(audit.showcase.unique())) == (10, 18, 30) and audit.passed.all() and
            audit.error_m.between(0, .02, inclusive="left").all(), "Geometry acceptance failed")
    return files | {audit_path}, len(audit), float(audit.error_m.max())


def check_paper_and_review():
    refs = set()
    for path in DRAFTS + REPORTS[:3]:
        prose = path.read_text(encoding="utf-8")
        require("{{" not in prose, f"Unresolved field in {path}")
        for match in re.findall(r"\]\(([^)\s]+)\)", prose):
            if "://" not in match:
                target = match.split("#", 1)[0]
                require(not target or (path.parent / target).exists() or
                        (path.parent / target).resolve() == MANIFEST.resolve(),
                        f"Missing link target {target} in {path}")
        for ref in re.findall(r"(?:config|docs|reports|results|scripts|src)/[\w./-]+\.(?:yaml|md|csv|json|py)",
                              "\n".join(re.findall(r"<!--(.*?)-->", prose, re.S))):
            refs.add(Path(ref))
    require(len(refs) >= 25 and all(p.is_file() for p in refs), "A manuscript source is missing")
    workbook = read(K / "release_manifest.json")
    require(workbook["passed"], "Wrong K3 source revision")
    require(workbook["files"][(K / "kit.yaml").as_posix()] == sha256_file(K / "kit.yaml"), "K3 choices changed")
    kit = read(K / "kit.yaml")["by_household"]
    h1, h3 = "H1_single_commuter", "H3_couple_one_remote"
    require(kit[h1]["kit"]["kit_id"] == "H1_kit_01" and kit[h3]["kit"]["kit_id"] == "H3_kit_02",
            "K3 choice mismatch")
    roles = pd.read_csv(K / "paired_effects.csv").set_index(["household", "cohort"])
    commuter = roles.loc[(h1, "training_best_available")]
    couple = roles.loc[(h3, "training_equal_effort")]
    require(commuter.ci_lo < 0 < commuter.ci_hi and couple.ci_lo < 0 < couple.ci_hi,
            "Training uncertainty changed")
    require((commuter.kit_adequate, commuter.catalogue_adequate) == (11, 13) and
            (couple.kit_adequate, couple.catalogue_adequate) == (5, 2), "Training adequacy changed")
    hk1 = roles.loc[(h1, "hong_kong")]
    require((hk1.kit_adequate, hk1.catalogue_adequate) == (184, 246), "Commuter scenario changed")
    by_size = pd.read_csv(K / "hk_adequacy_by_size.csv")
    fit = pd.read_csv(K / "hk_scenario_summary.csv").set_index(["household", "strategy"])
    strategies = ("S2_larger_kit", "S2_catalogue_optimized")
    by_size = by_size[(by_size.household == h3) & by_size.strategy.isin(strategies)]
    band = by_size[by_size.area_m2.between(13, 16)].groupby("strategy")[["n_adequate", "n_shells"]].sum()
    require(band.loc[strategies[0]].tolist() == [51, 120] and band.loc[strategies[1]].tolist() == [30, 120],
            "The couple size-band counts changed")
    below = by_size[by_size.area_m2.lt(13)].groupby("strategy").mean_fciq.mean()
    require(np.allclose(below.loc[list(strategies)], [.448, .500], atol=.0005), "The small-shell trade-off changed")
    pairs = fit.loc[[(h3, s) for s in strategies]]
    require(np.allclose(pairs.a_min.to_numpy(), [15.39, 16.12], atol=.005, rtol=0), "HK crossings changed")
    return refs | {K / "release_manifest.json", Path("reviews/G3_review_round3.md")}


def check():
    files, figures = check_figures_and_tables()
    render_files, instances, error = check_render_set()
    visual, tests = read(VISUAL), read(TESTS)
    require(visual["passed"] and tests["passed"] and tests["exit_code"] == 0 and tests["test_count"] > 0,
            "Review evidence incomplete")
    seen = hashes(visual["files"])
    expected = {p for p in figures if p.suffix == ".pdf"} | {p for p in files if p.name.endswith("_overlay.png")}
    require(expected <= seen and len(expected) == 18, "Figure proof or geometry overlay missing")
    paper = check_paper_and_review()
    package = files | render_files | paper | seen | SANITIZED | {VISUAL, TESTS, *SCRIPTS, *REPORTS, *DRAFTS}
    return {
        "passed": True,
        "checks": {"publication_figures": len(figures)//2, "table_pairs": 7, "scenes": 10, "stills": 30,
                   "overlaid_examples": 3, "projected_instances": instances, "max_projection_error_m": error,
                   "reported_regression_tests": tests["test_count"]},
        "files": {p.as_posix(): sha256_file(p) for p in sorted(package)},
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--verify", action="store_true", help="Check exact published evidence without writing")
    mode.add_argument("--finalize", action="store_true", help="Write the review manifest after numerical and visual QA")
    args = parser.parse_args()
    result = check()
    if args.verify:
        require(read(MANIFEST) == result, "G4 release does not match its manifest")
    else:
        write_manifest(MANIFEST, result)
    print(json.dumps({"files": len(result["files"]), **result["checks"]}))


if __name__ == "__main__":
    main()
