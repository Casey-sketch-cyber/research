"""Render reviewed G4 plots at the submission's physical width.

The frozen G4 generator supplies the artists and all data. This profile only
changes the page, axes spacing and lettering, and never updates G4 artifacts.
"""

from contextlib import contextmanager
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from unittest.mock import patch

from matplotlib.collections import LineCollection, PathCollection
from matplotlib.text import Text
from matplotlib.ticker import FixedFormatter, FixedLocator, MaxNLocator

ROOT = Path(__file__).resolve().parents[1]
FINAL_WIDTH_MM = 174
DPI = 300
BODY_PT = 6.5
TITLE_PT = 6.8

# Destination name, page height (mm) and original grid margins adjusted to
# leave space for the print-size labels. The rows and columns are unchanged.
FORMATS = {
    "F2": ("FigureS1", 134, dict(top=.96, bottom=.135, left=.095, right=.976)),
    "F3": ("Figure2A", 91, dict(top=.78, bottom=.035, left=.11, right=.984, hspace=.22, wspace=.16)),
    "F3b_18": ("Figure2B", 117, dict(top=.84, bottom=.03, left=.028, right=.979, hspace=.36, wspace=.055)),
    "F3b_10": ("FigureS2A", 117, dict(top=.84, bottom=.03, left=.028, right=.979, hspace=.36, wspace=.055)),
    "F3b_30": ("FigureS2B", 157, dict(top=.87, bottom=.03, left=.028, right=.979, hspace=.35, wspace=.12)),
    "F4": ("Figure3", 110, dict(top=.81, bottom=.14, left=.105, right=.984, hspace=.32, wspace=.18)),
    "F5": ("Figure4", 110, dict(top=.78, bottom=.14, left=.105, right=.984, hspace=.32, wspace=.18)),
    "F6": ("Figure5", 110, dict(top=.81, bottom=.14, left=.107, right=.984, hspace=.32, wspace=.18)),
    "F7": ("FigureS3", 69, dict(top=.93, bottom=.24, left=.21, right=.975, wspace=.18)),
    "F8": ("FigureS7", 177, dict(top=.89, bottom=.096, left=.106, right=.978, hspace=.62, wspace=.22)),
    "F9": ("FigureS4", 175, dict(top=.91, bottom=.144, left=.265, right=.98, hspace=.37, wspace=.22)),
    "F10": ("Figure6", 132, dict(top=.79, bottom=.12, left=.095, right=.969, wspace=.61, hspace=.64)),
    "F11": ("FigureS6", 109, dict(top=.86, bottom=.38, left=.09, right=.972, wspace=.61)),
    "F12": ("FigureS5", 205, dict(top=.858, left=.065, right=.982, bottom=.228, hspace=.36, wspace=.16)),
}
PANEL_LETTERS = {
    "F3": "A", "F3b_18": "B", "F3b_10": "A", "F3b_30": "B",
    "F10": "ABCDEF", "F11": "ABC",
}
KIT_LABELS = {
    "H1": "Single commuter: top-ranked compact kit (not adopted)",
    "H3": "Couple: larger kit",
}


def load_plotter():
    """Load a fresh instance of the accepted plotting module."""
    script = ROOT / "scripts" / "12_make_figures.py"
    spec = spec_from_file_location("reviewed_g4_plots", script)
    plotter = module_from_spec(spec)
    spec.loader.exec_module(plotter)
    return plotter


def report_heading(fig, label, title, subtitle):
    """Retain the G4 source key for layout without painting old report titles."""
    fig.set_label(label)


def paper_legend(fig, handles, columns, y=.879):
    """Fit the original key entries within the final physical width."""
    if fig.get_label() in {"F5", "F10"}:
        columns = 2 if fig.get_label() == "F5" else 3
    opts = dict(
        handles=handles, ncol=columns, loc="upper center", fontsize=BODY_PT,
        handlelength=1.45, handletextpad=.45, columnspacing=.85, borderaxespad=0,
    )
    if y < .1:
        fig.legend(bbox_to_anchor=(.5, .018), loc="lower center",
                   **{key: value for key, value in opts.items() if key != "loc"})
    else:
        fig.legend(bbox_to_anchor=(.5, .982), **opts)


def wrap_text(text: Text, max_width_pt: float, fig) -> None:
    """Wrap at whitespace according to physical text width, keeping every word."""
    renderer = fig.canvas.get_renderer()
    properties = text.get_fontproperties()
    max_width_px = max_width_pt * fig.dpi / 72
    lines = []
    for original in text.get_text().splitlines():
        current = ""
        for word in original.split():
            candidate = (current + " " + word).strip()
            width = renderer.get_text_width_height_descent(candidate, properties, False)[0]
            if current and width > max_width_px:
                lines.append(current)
                current = word
            else:
                current = candidate
        lines.append(current)
    text.set_text("\n".join(lines))


def place_panel_letters(fig, name: str) -> None:
    letters = PANEL_LETTERS.get(name, "")
    if len(letters) == 1:
        fig.text(.015, .968, letters, fontsize=7, fontweight="bold", va="top")
    elif letters:
        for letter, ax in zip(letters, fig.axes, strict=True):
            bounds = ax.get_position()
            fig.text(bounds.x0 - .039, bounds.y1 + .035, letter,
                     fontsize=7, fontweight="bold", va="baseline")


def adjust_labels(fig, name: str) -> None:
    """Set final-size typography and wrap headings and labels within their panels."""
    for ax in fig.axes:
        ax.tick_params(axis="both", labelsize=BODY_PT, pad=2, length=2.5)
        ax.xaxis.labelpad = 2.5
        ax.yaxis.labelpad = 2.5
    fig.canvas.draw()
    for text in fig.findobj(match=Text):
        text.set_fontsize(9.1 if name == "F10" and text.get_fontsize() > 12 else BODY_PT)
    for ax in fig.axes:
        bounds = ax.get_position()
        width = 72 * fig.get_figwidth() * bounds.width
        title = ax.title
        title.set_fontsize(TITLE_PT)
        if name == "F3" and title.get_text():
            title.set_text(title.get_text().replace(" · ", " ·\n"))
        if name != "F12":
            wrap_text(title, width * .99, fig)
        wrap_text(ax.xaxis.label, width * 1.02, fig)
        # The Figure 6 bottom-left and middle axes have the longest y-tick labels.
        if name == "F10" and ax is fig.axes[4]:
            ax.set_yticks(
                ax.get_yticks(),
                [tick.get_text().replace("Optimized catalogue", "Optimized\ncatalogue")
                 for tick in ax.get_yticklabels()],
            )
            ax.tick_params(axis="y", labelsize=BODY_PT)
        if name == "F10" and ax is fig.axes[5]:
            for text in ax.texts:
                wrap_text(text, width * 1.01, fig)
        if name == "F9" and ax is fig.axes[5]:
            # Keep all marks. Suppress alternating labels on this narrow
            # zero-centered axis so 6.5 pt labels do not run together.
            labels = [mark.get_text() for mark in ax.get_xticklabels()]
            ax.xaxis.set_major_formatter(FixedFormatter([
                label if index % 2 == 0 else "" for index, label in enumerate(labels)
            ]))
        if name == "F12":
            for table in ax.tables:
                for (_, column), cell in table.get_celld().items():
                    cell.set_fontsize(BODY_PT)
                    cell.PAD = .045
                    cell.set_width((.47, .29, .24)[column])
    for text in fig.texts:
        value = text.get_text()
        if name == "F12" and value[:2] in KIT_LABELS:
            text.set_text(KIT_LABELS[value[:2]])
            text.set_fontsize(TITLE_PT)
            wrap_text(text, 218, fig)
        if name == "F9":
            wrap_text(text, 455, fig)
    place_panel_letters(fig, name)


def set_f11_legends(fig) -> None:
    """Keep each of the three room-comparison keys within its own column."""
    for ax, columns in zip(fig.axes, (1, 2, 2), strict=True):
        old = ax.get_legend()
        handles = old.legend_handles
        labels = [text.get_text() for text in old.get_texts()]
        old.remove()
        ax.legend(handles, labels, loc="upper center", bbox_to_anchor=(.5, -.21),
                  ncol=columns, fontsize=BODY_PT, handlelength=1.1,
                  handletextpad=.35, columnspacing=.65, borderaxespad=0)


def retain_major_ticks(fig) -> None:
    """Retain numeric tick positions from the original physical layout."""
    for ax in fig.axes:
        for axis in (ax.xaxis, ax.yaxis):
            if isinstance(axis.get_major_locator(), MaxNLocator):
                lo, hi = sorted(axis.get_view_interval())
                values = [value for value in axis.get_majorticklocs() if lo <= value <= hi]
                axis.set_major_locator(FixedLocator(values))


def scale_marks(fig, scale: float) -> None:
    """Preserve the visual scale of plot lines and marker areas after resizing."""
    for ax in fig.axes:
        for line in ax.lines:
            line.set_linewidth(line.get_linewidth() * scale)
            line.set_markersize(line.get_markersize() * scale)
        for collection in ax.collections:
            if isinstance(collection, PathCollection):
                collection.set_sizes(collection.get_sizes() * scale**2)
                collection.set_linewidths(collection.get_linewidths() * scale)
            elif isinstance(collection, LineCollection):
                collection.set_linewidths(collection.get_linewidths() * scale)


def export_plot(fig, name: str, directory: Path) -> list[Path]:
    """Apply final geometry and save a PDF with live text from original artists."""
    label, height, margins = FORMATS[name]
    retain_major_ticks(fig)
    scale = FINAL_WIDTH_MM / (25.4 * fig.get_figwidth())
    scale_marks(fig, scale)
    fig.set_size_inches(FINAL_WIDTH_MM / 25.4, height / 25.4)
    fig.subplots_adjust(**margins)
    if name == "F11":
        set_f11_legends(fig)
    adjust_labels(fig, name)
    destination = directory / f"{label}.pdf"
    fig.savefig(destination, dpi=DPI, metadata={
        "Title": label, "Author": None, "Creator": None,
        "Producer": None, "CreationDate": None,
    })
    return [destination]


@contextmanager
def print_profile(directory: Path):
    """Keep this export profile independent of the frozen G4 build and manifests."""
    plotter = load_plotter()
    with plotter.plt.rc_context(), \
            patch.object(plotter, "figure", report_heading), \
            patch.object(plotter, "legend", paper_legend), \
            patch.object(plotter, "export", lambda fig, name: export_and_close(fig, name, directory, plotter)):
        plotter.start_style()
        yield plotter


def export_and_close(fig, name, directory, plotter):
    try:
        return export_plot(fig, name, directory)
    finally:
        plotter.plt.close(fig)


def render_submission_plots(directory: Path) -> None:
    """Render only the requested figures and source still-view plates."""
    directory.mkdir(parents=True, exist_ok=True)
    with print_profile(directory) as plotter:
        for build in (plotter.f2, plotter.f3, plotter.f4, plotter.f5, plotter.f6, plotter.f7,
                      plotter.f8, plotter.f9, plotter.f10, plotter.f11, plotter.f12):
            build()
        plotter.render_panels(panel_areas={10, 18, 30})
