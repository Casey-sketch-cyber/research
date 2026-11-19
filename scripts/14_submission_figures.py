"""Compose regenerated iScience plots and export the upload figure files.

Run from the repository root with its plotting dependencies, Pillow, pypdf
and pypdfium2 installed. This build leaves the frozen G4 figures untouched.
"""

from argparse import ArgumentParser
from pathlib import Path
import os
from shutil import copyfile
from tempfile import TemporaryDirectory
from unittest.mock import patch

from PIL import Image
from pypdf import PdfReader, PdfWriter, Transformation
from pypdfium2 import PdfDocument

ROOT = Path(__file__).resolve().parents[1]
PT_PER_MM = 72 / 25.4
FINAL_WIDTH = 174 * PT_PER_MM
DPI = 300


def stack_figure_two(parts: Path, output: Path) -> None:
    """Place panels A and B vertically at their regenerated physical width."""
    pages = [PdfReader(parts / f"Figure2{panel}.pdf").pages[0] for panel in "AB"]
    for page in pages:
        if abs(float(page.mediabox.width) - FINAL_WIDTH) > .01:
            raise ValueError("Panel width is inconsistent with the final Figure 2 width")
    heights = [float(page.mediabox.height) for page in pages]
    writer = PdfWriter()
    destination = writer.add_blank_page(width=FINAL_WIDTH, height=sum(heights))
    destination.merge_transformed_page(pages[0], Transformation().translate(0, heights[1]))
    destination.merge_page(pages[1])
    destination.compress_content_streams(level=9)
    writer.compress_identical_objects()
    writer.metadata = None
    writer.add_metadata({"/Title": "Figure 2"})
    with output.open("wb") as stream:
        writer.write(stream)


def save_bitmap(image: Image.Image, pdf: Path, preview_dir: Path | None) -> None:
    """Write metadata-free RGB review and submission bitmaps."""
    with Image.frombytes("RGB", image.size, image.convert("RGB").tobytes()) as rendered:
        rendered.save(
            pdf.with_suffix(".tif"), compression="tiff_lzw", dpi=(DPI, DPI),
            tiffinfo={317: 2},  # TIFF Predictor: reversible horizontal differencing.
        )
        if preview_dir is not None:
            rendered.save(preview_dir / f"{pdf.stem}.png", dpi=(DPI, DPI))


def export_bitmap(pdf: Path, preview_dir: Path | None) -> None:
    """Rasterize at publication size or use the approved GA's exact PNG pixels."""
    if pdf.stem == "GraphicalAbstract":
        with Image.open(ROOT / "paper/figures/fig1/GraphicalAbstract.png") as approved:
            if approved.size != (1650, 1650):
                raise ValueError("Graphical abstract PNG must be 1650 × 1650")
            save_bitmap(approved, pdf, preview_dir)
        return
    with PdfDocument(pdf) as doc:
        page = doc[0]
        bitmap = page.render(scale=DPI / 72, fill_color=(255, 255, 255, 255))
        try:
            save_bitmap(bitmap.to_pil(), pdf, preview_dir)
        finally:
            bitmap.close()
            page.close()


def build_submission_figures(
    out: Path, previews: Path | None = None, supplement_dir: Path | None = None,
    include_ga: bool = True,
) -> None:
    """Build the upload pairs and optionally retain the eight supplement plates."""
    out.mkdir(parents=True, exist_ok=True)
    if previews is not None:
        previews.mkdir(parents=True, exist_ok=True)
    final_sources = ROOT / "paper/figures/fig1"
    approved_stems = ("Figure1", "GraphicalAbstract") if include_ga else ("Figure1",)
    for stem in approved_stems:
        copyfile(final_sources / f"{stem}.pdf", out / f"{stem}.pdf")
    with TemporaryDirectory(prefix="submission-plates-", dir=out.parent) as scratch:
        plates = Path(scratch)
        with patch.dict(os.environ, {"MPLCONFIGDIR": str(plates / ".matplotlib")}):
            from submission_figure_render import render_submission_plots
            render_submission_plots(plates)
        stack_figure_two(plates, out / "Figure2.pdf")
        for number in range(3, 7):
            filename = f"Figure{number}.pdf"
            copyfile(plates / filename, out / filename)
        if supplement_dir is not None:
            supplement_dir.mkdir(parents=True, exist_ok=True)
            for source in sorted(plates.glob("FigureS*.pdf")):
                copyfile(source, supplement_dir / source.name)
    main_figures = [f"Figure{number}" for number in range(1, 7)]
    if include_ga:
        main_figures.append("GraphicalAbstract")
    for stem in main_figures:
        pdf = out / f"{stem}.pdf"
        export_bitmap(pdf, previews)
        print(f"{pdf.name}: {pdf.stat().st_size:,} bytes | "
              f"{pdf.with_suffix('.tif').name}: {pdf.with_suffix('.tif').stat().st_size:,} bytes")


def main() -> None:
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=ROOT / "paper/submission")
    parser.add_argument("--previews-dir", type=Path, help="Optional 300 dpi PNG copies")
    parser.add_argument("--supplement-dir", type=Path, help="Retain the final-size supplemental PDFs")
    parser.add_argument("--skip-ga", action="store_true", help="Build only the main figures and supplement plates")
    args = parser.parse_args()
    build_submission_figures(args.out, args.previews_dir, args.supplement_dir, not args.skip_ga)


if __name__ == "__main__":
    main()
