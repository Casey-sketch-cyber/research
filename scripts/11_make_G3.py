"""Verify the G3 evidence chain and summarize support-aware area gains by bin."""

from __future__ import annotations

import argparse
import csv
import io
import json
import os
import re
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from math import floor, inf, isfinite
from pathlib import Path
from statistics import median

from fea.io import sha256_file


P1 = Path("results/expA_f1/analysis_p1")
F11_SOURCE = Path("results/expR/figures/F11_supporting_R.pdf")
F11_RELEASE = Path("results/g3/figures/F11_supporting_R.pdf")
F12_RELEASE = Path("results/g3/figures/F12_kit")
REVIEW_ROOT = Path("results/g3_review")
PHASE_GATES = {
    "F1": "results/expA_f1/acceptance.json",
    "F2": "results/expA_f1/analysis/package_acceptance.json",
    "P1": "results/expA_f1/analysis_p1/package_acceptance.json",
    "F3": "results/expA_f3/package_acceptance.json",
    "B": "results/expB/report_acceptance.json",
    "D": "results/expD/acceptance.json",
    "R": "results/expR/package_acceptance.json",
    "ablations": "results/ablations/report_acceptance.json",
    "C": "results/expC/acceptance.json",
    "K": "results/expK/acceptance.json",
    "HK": "results/scenario_hk/acceptance.json",
    "literature": "results/literature/acceptance.json",
}


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def read_rows(path: Path) -> list[dict]:
    with path.open(encoding="utf-8", newline="") as stream:
        return list(csv.DictReader(stream))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def atomic_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(content, encoding="utf-8", newline="\n")
    temporary.replace(path)


def f11_release_bytes(repo: Path) -> bytes:
    """Normalize the accepted F11 creation timestamp without altering its drawing."""
    data = (repo / F11_SOURCE).read_bytes()
    pattern = rb"(/CreationDate\s*\()D:(\d{14})([+-])(\d{2})'(\d{2})'(\))"

    def to_utc(match: re.Match[bytes]) -> bytes:
        sign = 1 if match[3] == b"+" else -1
        offset = timedelta(minutes=sign * (60 * int(match[4]) + int(match[5])))
        value = datetime.strptime(match[2].decode("ascii"), "%Y%m%d%H%M%S")
        value = value.replace(tzinfo=timezone(offset)).astimezone(timezone.utc)
        return match[1] + value.strftime("D:%Y%m%d%H%M%S+00'00'").encode("ascii") + match[6]

    cleaned, count = re.subn(pattern, to_utc, data)
    require(count == 1 and len(cleaned) == len(data), "Unexpected F11 metadata layout")
    return cleaned


def draw_kit_release(
    repo: Path,
    acceptance_path: str = PHASE_GATES["K"],
    design_path: Path = Path("results/expK/kit.yaml"),
    output_path: Path = F12_RELEASE,
) -> None:
    """Draw the accepted K dimensions with the storage labels outside the bodies."""
    cache = repo / ".tmp" / "g3-matplotlib"
    cache.mkdir(parents=True, exist_ok=True)
    os.environ["MPLCONFIGDIR"] = str(cache)
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Rectangle

    from fea.config import config_hash, load_config
    from phase11_kit_design import BED, kit_configuration

    accepted = read_json(repo / acceptance_path)
    require(accepted["passed"] and sha256_file(repo / design_path) == accepted["outputs"][design_path.as_posix()],
            "The chosen dimensions differ from the accepted kit")
    design = read_json(repo / design_path)
    config = load_config(repo / "config/project.yaml")
    require(config_hash(config) == design["config_hash"] == accepted["config_hash"],
            "The current furniture configuration differs from the kit run")

    heights = (2.8, 1.2, 1.4, 1.25)
    households = {"H1_single_commuter": "H1 commuter", "H3_couple_one_remote": "H3 couple"}
    fig, axes = plt.subplots(4, 4, figsize=(10.4, 8.2), layout="constrained", height_ratios=heights)
    for column, (household, label) in enumerate(households.items()):
        choice = design["by_household"][household]["kit"]
        kit, qualities = kit_configuration(config, household, choice)
        require(qualities == choice["qualities"], "Quality factors differ from the accepted kit")
        furniture = kit["furniture"]
        items = (BED[household][0], "fold_down_desk", "drop_leaf_table", "wardrobe")
        labels = ("Wall bed", "Fold-down desk", "Drop-leaf table", "Wardrobe")
        for row, (name, item_label) in enumerate(zip(items, labels)):
            for offset, state in enumerate(("deployed", "stowed")):
                ax = axes[row, 2 * column + offset]
                ax.set_axis_off()
                if name == "wardrobe":
                    if offset:
                        continue
                    body = furniture["static_items"][name]
                    title = f"{household[:2]} {item_label.lower()} · {body['storage_units']:.1f} storage units"
                else:
                    body = furniture["transformable_items"][name]["states"][state]
                    title = f"{label} · {item_label}, {state}"
                width, depth = body["footprint"]
                ax.set(xlim=(-.14, 1.94), ylim=(-.31, heights[row] - .31), aspect="equal")
                ax.add_patch(Rectangle((0, 0), width, depth, facecolor="#deedf2",
                                       edgecolor="#1c6d8b", linewidth=1.2))
                arrow = dict(arrowstyle="<->", color=".25", lw=.7, shrinkA=0, shrinkB=0)
                ax.annotate("", (width, -.09), (0, -.09), arrowprops=arrow)
                ax.annotate("", (width + .10, depth), (width + .10, 0), arrowprops=arrow)
                ax.text(width / 2, -.22, f"{width:.2f} m", ha="center", va="center", fontsize=8)
                ax.text(width + .21, depth / 2, f"{depth:.2f} m", rotation=90,
                        ha="center", va="center", fontsize=8)
                if name in qualities:
                    ax.text(width / 2, depth / 2, f"q = {qualities[name]:.2f}",
                            ha="center", va="center", fontsize=8)
                ax.set_title(title, fontsize=8.5)
    fig.suptitle("F12  Selected quality-aware kits\nTop-view body dimensions in metres", fontsize=13)
    output = repo / output_path
    output.parent.mkdir(parents=True, exist_ok=True)
    for extension in ("pdf", "png"):
        path = output.with_suffix("." + extension)
        temporary = path.with_suffix(path.suffix + ".tmp")
        metadata = {"CreationDate": datetime.now(timezone.utc)} if extension == "pdf" else {}
        fig.savefig(temporary, format=extension, dpi=220, metadata=metadata)
        temporary.replace(path)
    plt.close(fig)


def summarize_area(repo: Path) -> str:
    """Keep P1's positive-gain statistics and derive all-pair median bounds."""
    method = "median_bin_cummax"
    pairs = defaultdict(list)
    for row in read_rows(repo / P1 / "paired_equivalent_area.csv"):
        if row["method"] != method:
            continue
        key = row["pooling"], row["reference_pooling"], row["household"]
        area = float(row["nia_m2"])
        area_bin = 2 * floor((area + 1e-8) / 2)
        lower = float(row["delta_ea_lower_bound_m2"])
        upper = inf if row["delta_ea_upper_bound_unbounded"] == "True" else float(row["delta_ea_upper_bound_m2"])
        require(isfinite(lower) and lower >= 0 and upper >= lower, "Invalid P1 area interval")
        result = lower, upper, 100 * lower / area, 100 * upper / area
        pairs[(*key, None)].append(result)
        pairs[(*key, area_bin)].append(result)
    data = []
    matched = set()
    for row in read_rows(repo / P1 / "area_gain_summary.csv"):
        if row["method"] != method:
            continue
        area_bin = int(float(row["area_bin_lo"])) if row["area_bin_lo"] else None
        key = row["pooling"], row["reference_pooling"], row["household"], area_bin
        values = pairs[key]
        require(len(values) == int(row["n_units"]) and key not in matched, "P1 cohort counts differ")
        matched.add(key)
        lower, upper, relative_lower, relative_upper = map(median, zip(*values))
        data.append({
            **row,
            "all_pair_median_delta_ea_lower_m2": f"{lower:.10g}",
            "all_pair_median_delta_ea_upper_m2": f"{upper:.10g}" if isfinite(upper) else "",
            "all_pair_median_delta_ea_upper_unbounded": not isfinite(upper),
            "all_pair_median_delta_ea_lower_pct_nia": f"{relative_lower:.10g}",
            "all_pair_median_delta_ea_upper_pct_nia": f"{relative_upper:.10g}" if isfinite(relative_upper) else "",
            "all_pair_median_delta_ea_upper_pct_nia_unbounded": not isfinite(relative_upper),
        })
    require(data and matched == set(pairs), "P1 cohort coverage differs")
    stream = io.StringIO()
    writer = csv.DictWriter(stream, fieldnames=list(data[0]), lineterminator="\n")
    writer.writeheader()
    writer.writerows(data)
    return stream.getvalue()


def evidence_files(repo: Path) -> dict[str, str]:
    hashes = {}

    def bind(path: str | Path, expected: str | None = None) -> Path:
        full = (repo / path).resolve()
        require(full.is_relative_to(repo) and full.is_file(), f"Missing evidence {path}")
        observed = sha256_file(full)
        require(expected is None or observed == expected, f"Evidence digest differs for {path}")
        hashes[full.relative_to(repo).as_posix()] = observed
        return full

    phases = {}
    for phase, name in PHASE_GATES.items():
        phases[phase] = read_json(bind(name))
        require(phases[phase]["passed"] is True, f"Unaccepted phase {phase}")

    for phase, path in (
        ("F2", "results/expA_f1/analysis/acceptance.json"),
        ("P1", "results/expA_f1/analysis_p1/acceptance.json"),
        ("F3", "results/expA_f3/report_acceptance.json"),
        ("R", "results/expR/acceptance.json"),
    ):
        bind(path, phases[phase]["numerical_acceptance_sha256"])
    bind("results/expA_f1/solutions.csv", phases["F1"]["combined_sha256"])
    bind("results/expA_f3/solutions.csv", phases["F3"]["F3_solutions_sha256"])
    bind("results/expB/cases.csv", phases["B"]["cases_sha256"])
    bind("results/expB/run.json", phases["B"]["run_sha256"])

    f3_report_path = Path("results/expA_f3/report_acceptance.json")
    f3_report = read_json(bind(f3_report_path))
    require(f3_report["passed"] and f3_report["independently_revalidated"] == 1044,
            "F3 validation is incomplete")
    for filename, digest in f3_report["inputs"].items():
        bind(filename, digest)
    ablations = read_json(bind("results/ablations/acceptance.json"))
    require(ablations["passed"] and ablations["independent_validation"], "Ablation validation is incomplete")
    require(ablations["layouts"] == 14835 and ablations["triplets"] == 4945, "Unexpected ablation coverage")
    bind("results/ablations/cases.csv", ablations["cases_sha256"])
    for filename, digest in phases["ablations"]["input_sha256"].items():
        bind(filename, digest)
    runs = {}
    for phase in ("ablations", "expK", "scenario_hk"):
        runs[phase] = read_json(bind(f"results/{phase}/run.json"))
        require(runs[phase]["status"] == "complete", f"Unfinished run {phase}")
    # The processed corpus is reconstructed from separately obtained data. Its
    # digest stays in the phase receipts, while all published inputs are checked.
    for inputs in (runs["ablations"]["inputs"], *(phases[p]["input_sha256"] for p in ("C", "K", "HK"))):
        for filename, digest in inputs.items():
            if filename != "data/processed/corpus_units.parquet":
                bind(filename, digest)
    require(phases["B"]["independently_revalidated"] == 600, "Incomplete benchmark coverage")
    require(phases["D"]["n_pairs"] == 10476, "Incomplete conventional-indicator coverage")
    require(phases["C"]["geometry_only"] and phases["C"]["split_by"] == "D1 group_id"
            and phases["C"]["metric_rows"] == 144, "Unexpected surrogate inputs, split or metric coverage")
    require(phases["K"]["all_layouts_valid"] and phases["K"]["active_training_shells"] in {18, 24, 30},
            "Reduced kit acceptance differs from the reviewed scope")
    require(phases["K"]["elapsed_seconds"] <= 48 * 3600, "Reduced kit exceeded the reviewed time box")
    require(runs["expK"]["code_hash"] == phases["K"]["code_hash"] and runs["expK"]["inputs"] == phases["K"]["input_sha256"],
            "Kit run and acceptance evidence differ")
    pilot = read_json(bind("results/expK/runtime_pilot.json"))
    require(pilot["passed"] and pilot["selected_training_shells"] == phases["K"]["active_training_shells"],
            "The reduced kit pilot and evaluated scope differ")
    require(phases["HK"]["shells"] == 390 and phases["HK"]["cases"] == 4290, "Incomplete Hong Kong shell coverage")
    require(runs["scenario_hk"]["code_hash"] == phases["HK"]["code_hash"]
            and runs["scenario_hk"]["inputs"] == phases["HK"]["input_sha256"], "Scenario run and acceptance evidence differ")
    require(phases["literature"]["status"] == "COMPLETE_RETRIEVED_SNAPSHOT", "Literature screening is incomplete")

    gates_with_outputs = [
        (f3_report_path, f3_report),
        *[(Path(PHASE_GATES[name]), phases[name]) for name in ("B", "D", "ablations", "C", "K", "HK", "literature")],
        *[(p, read_json(repo / p)) for p in (
            Path("results/expA_f1/analysis/acceptance.json"), P1 / "acceptance.json",
            Path("results/expR/acceptance.json"),
        )],
    ]
    for gate_path, gate in gates_with_outputs:
        for filename, digest in gate["outputs"].items():
            path = Path(filename)
            if path.parts[0] not in {"results", "reports", "config", "scripts"}:
                path = gate_path.parent / path
            bind(path, digest)

    release = bind(F11_RELEASE)
    require(release.read_bytes() == f11_release_bytes(repo), "The released F11 differs from the accepted drawing")
    for extension in (".pdf", ".png"):
        bind(F12_RELEASE.with_suffix(extension))
    suite = read_json(bind("results/g3/test_receipt.json"))
    require(suite["passed"] is True and suite["tests_passed"] == 183 and suite["coarse_grid_smoke_layouts"] == 3,
            "The corrected compute version has not passed its recorded checks")
    for path, digest in suite["test_inputs"].items():
        bind(path, digest)
    review = read_json(bind("config/g3_visual_review.json"))
    require(set(review["figures"]) == {"F8", "F9", "F10", "F11", "F12"}, "Required figure review is incomplete")
    for figure, info in review["figures"].items():
        require(info["passed"] is True and info["observations"], f"Missing figure review for {figure}")
        require({Path(name).suffix for name in info["files"]} == {".png", ".pdf"}, f"Missing figure format for {figure}")
        for path, digest in info["files"].items():
            require(hashes.get(path) == digest, f"Figure {figure} differs from the accepted output")

    reviewed = {}
    for name in ("benchmark", "catalogue", "kit", "hong_kong"):
        gate = read_json(bind(REVIEW_ROOT / name / "acceptance.json"))
        require(gate["passed"] and gate["config_hash"] == phases["K"]["config_hash"],
                f"The G3 review checks differ for {name}")
        for path, digest in {**gate["input_sha256"], **gate["outputs"]}.items():
            if path != "data/processed/corpus_units.parquet":
                bind(path, digest)
        reviewed[name] = gate
    require(reviewed["benchmark"]["production"]["pairs"] == 200 and reviewed["benchmark"]["auc_rows"] == 96,
            "Incomplete B or C review coverage")
    catalogue = reviewed["catalogue"]
    require((catalogue["k_rescored"], catalogue["k_optimized"], catalogue["hk_rescored"]) == (360, 120, 3510),
            "Incomplete catalogue rescoring and optimization")
    kit = reviewed["kit"]
    require(kit["candidates_per_household"] == 9 and kit["confirmation_layouts"] == 1080
            and kit["bespoke_contains_catalogue_and_kit"], "Incomplete reviewed K comparisons")
    hk = reviewed["hong_kong"]
    require(hk["shells"] == 390 and hk["cases"] == 4290 and not hk["census_weighting"] and not hk["carbon_applied"],
            "Unexpected reviewed HK scope")
    review_checks = read_json(bind(REVIEW_ROOT / "validation.json"))
    require(review_checks["passed"] and review_checks["tests_passed"] >= suite["tests_passed"],
            "The revised suite did not pass")
    for path, digest in review_checks["tested_inputs"].items():
        bind(path, digest)
    figures = read_json(bind(REVIEW_ROOT / "visual_review.json"))
    require(set(figures) == {"F10", "F12"}, "The reviewed F10 and F12 checks are required")
    for figure, item in figures.items():
        require(item["passed"] and item["observations"] and {Path(p).suffix for p in item["files"]} == {".png", ".pdf"},
                f"Incomplete review for {figure}")
        for path, digest in item["files"].items():
            if figure == "F10":
                require(hk["outputs"].get(path) == digest, "Reviewed F10 differs from the HK export")
            bind(path, digest)
    bind("reports/GATE_G3_response.md")
    bind("reports/phase_11c_G3_review.md")
    bind("reviews/G3_review.md")
    bind("reports/GATE_G3.md")
    bind("reports/novelty_check.md")
    bind("reports/QUESTIONS.md")
    bind("results/g3/area_summary.csv")
    bind("scripts/11_make_G3.py")
    return dict(sorted(hashes.items()))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=Path("."))
    parser.add_argument("--prepare-area", action="store_true")
    parser.add_argument("--prepare-f11", action="store_true")
    parser.add_argument("--prepare-f12", action="store_true")
    parser.add_argument("--prepare-reviewed-f12", action="store_true")
    parser.add_argument("--verify", action="store_true")
    args = parser.parse_args()
    repo = args.repo.resolve()
    output = repo / "results" / "g3"
    if args.prepare_f12 or args.prepare_reviewed_f12:
        require(not args.verify, "Use --verify to check the accepted G3 release")
        if args.prepare_reviewed_f12:
            draw_kit_release(repo, "results/g3_review/kit/acceptance.json",
                             Path("results/g3_review/kit/kit.yaml"), Path("results/g3_review/kit/F12"))
        else:
            draw_kit_release(repo)
        print("Prepared F12 from the accepted kit dimensions")
        return
    if args.prepare_f11:
        path = repo / F11_RELEASE
        data = f11_release_bytes(repo)
        if args.verify:
            require(path.read_bytes() == data, "The released F11 differs from the accepted drawing")
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            temporary = path.with_suffix(".pdf.tmp")
            temporary.write_bytes(data)
            temporary.replace(path)
        print("Checked the F11 release copy with its creation date in UTC")
        return
    area = summarize_area(repo)
    if args.verify:
        require((output / "area_summary.csv").read_text(encoding="utf-8") == area, "G3 area table differs")
    else:
        atomic_text(output / "area_summary.csv", area)
    if args.prepare_area:
        print("Prepared the P1 area summary")
        return
    manifest = {"passed": True, "phase_gates": PHASE_GATES, "files": evidence_files(repo)}
    target = output / "evidence_manifest.json"
    if args.verify:
        require(read_json(target) == manifest, "G3 evidence manifest differs")
    else:
        atomic_text(target, json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
    print(f"Verified {len(manifest['files'])} G3 evidence files")


if __name__ == "__main__":
    main()
