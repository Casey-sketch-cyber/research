"""E2: render a fixed excluded sample, then summarize explicit visual cause reviews."""
import json
from pathlib import Path

import numpy as np
import pandas as pd
from tqdm import tqdm

from fea.geometry.unit import Unit
from fea.io import prepare_cli, sha256_file, start_run, write_json
from phase07_evaluability import evaluate_empty


CATEGORIES = ["conversion of doors or openings", "rasterization",
              "genuinely narrow passage in the source drawing", "other"]


def geometry_layer(ax, geometry, color, alpha=1., linewidth=.7):
    if geometry.is_empty:
        return
    if geometry.geom_type == "Polygon":
        from shapely.plotting import plot_polygon
        plot_polygon(geometry, ax=ax, add_points=False, color=color, alpha=alpha, linewidth=linewidth)
    elif geometry.geom_type in ("LineString", "LinearRing"):
        x, y = geometry.xy
        ax.plot(x, y, color=color, alpha=alpha, lw=linewidth)
    else:
        for part in getattr(geometry, "geoms", []):
            geometry_layer(ax, part, color, alpha, linewidth)


def draw_grid(ax, grid, covered, expanded, title):
    colours = np.ones((*grid.labels.shape, 4))
    colours[:, :, :3] = .91
    colours[grid.walkable] = [.78, .78, .78, 1.]
    colours[expanded] = [.97, .79, .40, 1.]
    colours[covered] = [.38, .70, .89, 1.]
    colours[grid.entrance] = [.10, .62, .25, 1.]
    r = grid.resolution
    extent = [grid.origin[0], grid.origin[0]+grid.labels.shape[1]*r,
              grid.origin[1], grid.origin[1]+grid.labels.shape[0]*r]
    ax.imshow(colours, origin="lower", extent=extent, interpolation="nearest")
    for i, target in enumerate(grid.service_targets):
        if target.any():
            yy, xx = np.nonzero(target)
            passed = np.any(target & covered)
            colour = "#19662d" if passed else "#c02020"
            ax.scatter(grid.origin[0]+(xx+.5)*r, grid.origin[1]+(yy+.5)*r,
                s=7, facecolors="none", edgecolors=colour, linewidths=.45)
            ax.text(grid.origin[0]+(xx.mean()+.5)*r, grid.origin[1]+(yy.mean()+.5)*r,
                str(i), color=colour, fontsize=11, fontweight="bold")
        else:
            ax.text(.02, .95-.07*i, f"Target {i}: empty mask", color="#c02020", transform=ax.transAxes)
    ax.set(title=title, xlabel="Local x (m)", ylabel="Local y (m)", aspect="equal")


def render(unit, config, output):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Patch
    coarse, grid, coverage, expansion = evaluate_empty(unit, .1, config["raster"]["source_gap_close_m"], True)
    fine, fine_grid, fine_coverage, fine_expansion = evaluate_empty(unit, .05, config["raster"]["source_gap_close_m"], True)
    fig, axes = plt.subplots(1, 3, figsize=(15, 5.2))
    for name, colour in [("furnishable", "#d8d8d8"), ("storage_only", "#baa5cc"),
        ("walkable_only", "#b9dce8"), ("fixed_service", "#c1a5be")]:
        geometry_layer(axes[0], unit.classes.get(name, unit.interior.buffer(0).difference(unit.interior)), colour, .6)
    geometry_layer(axes[0], unit.walls, "#222222", 1., 1.5)
    for door in unit.doors:
        geometry_layer(axes[0], door, "#d86326", .8, 1.7)
    if unit.entrance is not None:
        geometry_layer(axes[0], unit.entrance, "#159447", 1., 3.)
    axes[0].set(title="Normalized source geometry; orange = openings", xlabel="Local x (m)", ylabel="Local y (m)", aspect="equal")
    draw_grid(axes[1], grid, coverage, expansion,
        f"Main 0.10 m raster: a={coarse['a_pass']}; b={coarse['b_reachable_share']:.1%}")
    draw_grid(axes[2], fine_grid, fine_coverage, fine_expansion,
        f"Diagnostic 0.05 m raster: a={fine['a_pass']}; b={fine['b_reachable_share']:.1%}")
    bounds = unit.interior.bounds
    for ax in axes:
        ax.set_xlim(bounds[0]-.8, bounds[2]+.8)
        ax.set_ylim(bounds[1]-.8, bounds[3]+.8)
    fig.suptitle(f"{unit.unit_key} | NIA {unit.interior.area:.2f} m² | no furniture; no geometry repair")
    fig.legend(handles=[Patch(color="#61b3e3", label="Walking-disc coverage"),
        Patch(color="#f7c966", label="Extra clearance reach"), Patch(color="#199e40", label="Entrance"),
        Patch(fill=False, edgecolor="#c02020", label="Unreachable fixed target")],
        loc="lower center", ncol=4, fontsize=9)
    fig.tight_layout(rect=(0, .07, 1, .94))
    fig.savefig(output, dpi=300, bbox_inches="tight")
    fig.savefig(output.with_suffix(".pdf"), bbox_inches="tight")
    plt.close(fig)
    widths = []
    for door in unit.doors:
        rectangle = door.minimum_rotated_rectangle
        if rectangle.geom_type == "Polygon":
            widths.append(float(np.linalg.norm(np.diff(np.asarray(rectangle.exterior.coords), axis=0), axis=1).max()))
        elif not rectangle.is_empty:
            widths.append(float(rectangle.length))
    return dict(unit_key=unit.unit_key, source=unit.source, nia_m2=unit.interior.area,
        main_a_pass=coarse["a_pass"], main_b_share=coarse["b_reachable_share"],
        diagnostic_fine_a_pass=fine["a_pass"], diagnostic_fine_b_share=fine["b_reachable_share"],
        diagnostic_fine_evaluable=fine["evaluable"], min_recorded_opening_width_m=min(widths) if widths else None,
        main_failed_targets=json.dumps(coarse["failed_targets"]),
        diagnostic_fine_failed_targets=json.dumps(fine["failed_targets"]),
        figure=output.as_posix(), figure_sha256=sha256_file(output))


def main():
    parser = prepare_cli(__doc__)
    parser.add_argument("--finalize", action="store_true")
    parser.add_argument("--classifications", default="config/exclusion_cause_reviews.json")
    args = parser.parse_args()
    config, _, _ = start_run(args, "07_exclusion_audit")
    if args.dry_run:
        print("Would render the fixed excluded sample, or summarize explicit cause classifications; no repairs.")
        return
    root = Path("results/expA")
    manifest = json.loads((root/"evaluability_manifest.json").read_text())
    sample_path = root/"exclusion_audit_sample.csv"
    assert sha256_file(sample_path) == manifest["audit_sample_sha256"]
    sample = pd.read_csv(sample_path)
    destination = root/"exclusion_audit"
    destination.mkdir(parents=True, exist_ok=True)
    if args.finalize:
        review_path = Path(args.classifications)
        choices = pd.DataFrame(json.loads(review_path.read_text())["records"])
        if choices.unit_key.duplicated().any() or set(choices.unit_key) != set(sample.unit_key):
            raise ValueError("Every selected audit unit needs exactly one explicit classification")
        if not choices.cause.isin(CATEGORIES).all() or not choices.visually_reviewed.eq(True).all() or choices.evidence.isna().any():
            raise ValueError("Incomplete cause review")
        features = pd.read_csv(destination/"diagnostics.csv")
        joined = choices.merge(features, on="unit_key", validate="one_to_one")
        choices.to_csv(destination/"cause_classification.csv", index=False)
        counts = choices.cause.value_counts().reindex(CATEGORIES, fill_value=0).rename_axis("cause").reset_index(name="n_units")
        counts.to_csv(destination/"cause_counts.csv", index=False)
        text = ["# E2 excluded-unit cause audit", "",
            f"Fixed-seed sample: {len(choices)} excluded units; seed {config['seed']}. No geometry or analysis rule was repaired.", "",
            counts.to_markdown(index=False), "",
            "These are visual/diagnostic attributions, not a demonstrated error rate for the full corpus. "
            "Fine-grid results are diagnostic only; the main E1 list and original solves stay unchanged. "
            "Ambiguous source-versus-conversion cases are classified as other and described explicitly.", "",
            "Source composition of this unstratified random audit sample: "+json.dumps(joined.source.value_counts().to_dict())+". Do not extrapolate its cause proportions to an unrepresented source.", "",
            joined[["unit_key", "cause", "evidence", "diagnostic_fine_evaluable"]].to_markdown(index=False), ""]
        Path("reports/expA_exclusion_causes.md").write_text("\n".join(text), encoding="utf-8")
        write_json(destination/"manifest.json", dict(seed=config["seed"], sample_sha256=sha256_file(sample_path),
            diagnostics_sha256=sha256_file(destination/"diagnostics.csv"),
            classification_sha256=sha256_file(destination/"cause_classification.csv"),
            classification_input_sha256=sha256_file(review_path),
            cause_counts=choices.cause.value_counts().to_dict(), geometry_repaired=False,
            main_evaluability_changed=False, sample_units=len(choices)))
        print(counts.to_json(orient="records"))
        return
    corpus = pd.read_parquet(Path(config["paths"]["processed"])/"corpus_units.parquet",
        columns=["unit_key", "unit_json"]).set_index("unit_key")
    rows = []
    for key in tqdm(sample.unit_key, desc="Excluded-unit figures"):
        unit = Unit.from_dict(json.loads(corpus.loc[key, "unit_json"]))
        rows.append(render(unit, config, destination/(key.replace(":", "_")+".png")))
    pd.DataFrame(rows).to_csv(destination/"diagnostics.csv", index=False)
    print(json.dumps(dict(rendered=len(rows), classification_pending=True)))


if __name__ == "__main__":
    main()
