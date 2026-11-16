"""Export Figure 1 thumbnails from the validated F3 showcase."""

import argparse
from collections.abc import Iterable
from importlib import import_module
from pathlib import Path

from matplotlib.patches import Polygon
from tqdm import tqdm

from fea.geometry.unit import Unit


G4 = import_module("12_make_figures")
OUTPUT = Path("paper/figures/fig1/assets")


def export_plan(
    stem: Path,
    unit: Unit,
    items: Iterable[tuple[str, list[tuple[float, float]], str, str]] = (),
) -> None:
    """Keep one framing for each shell; draw only its plan and furniture bodies."""
    xmin, ymin, xmax, ymax = unit.interior.union(unit.walls).bounds
    margin = 0.23
    width = xmax - xmin + 2 * margin
    height = ymax - ymin + 2 * margin
    scale = 1.1 / max(width, height)
    with G4.plt.rc_context({"svg.hashsalt": "fea-fig1-plan", "hatch.linewidth": 0.45}):
        fig = G4.plt.figure(figsize=(width * scale, height * scale))
        ax = fig.add_axes([0, 0, 1, 1])
        G4.draw_unit(ax, unit, short=True)
        ax.set(xlim=(xmin - margin, xmax + margin), ylim=(ymin - margin, ymax + margin), title="")
        ax.axis("off")
        for _, vertices, state, function in items:
            ax.add_patch(Polygon(
                vertices,
                facecolor=G4.FUNCTIONS[function],
                edgecolor=G4.INK,
                linewidth=0.50,
                alpha=0.87,
                hatch="////" if state == "stowed" else None,
                zorder=2,
            ))
        fig.savefig(stem.with_suffix(".svg"), transparent=True, metadata={"Date": None})
        fig.savefig(stem.with_suffix(".png"), transparent=True, dpi=600)
        G4.plt.close(fig)


def main() -> None:
    """Export the two source thumbnails and the three matched normal-day slots."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=G4.CONFIG)
    parser.add_argument("--dry-run", action="store_true", help="Audit the source layouts without exporting.")
    args = parser.parse_args()

    config = G4.load_config(args.config)
    production = G4.document(G4.A / "run.json")["production_settings"]
    showcases = {area: (unit, household, layouts) for area, unit, household, layouts in G4.accepted_showcases()}
    generated, household, layouts = showcases[18]
    observed = showcases[30][0]
    tasks = [("home_D1_observed", observed, ()), ("home_D3_generated", generated, ())]
    for strategy, (layout, _) in layouts.items():
        for slot in G4.SLOT_LABELS:
            items = tuple(G4.footprints(layout, generated, config, production, household, slot))
            tasks.append((f"plan_{strategy}_{slot}", generated, items))

    message = f"Audited {len(tasks)} Figure 1 plans from {observed.unit_key} and {generated.unit_key}"
    if args.dry_run:
        print(message)
        return

    OUTPUT.mkdir(parents=True, exist_ok=True)
    for name, unit, items in tqdm(tasks, desc="Exporting plans", unit="plan"):
        export_plan(OUTPUT / name, unit, items)
    log = Path("logs/figure1_plans.log")
    log.parent.mkdir(exist_ok=True)
    log.write_text(message + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
