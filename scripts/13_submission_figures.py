"""Compose submission figures from the committed G4 PDFs and final figure assets.

Requires Pillow, pypdf, pypdfium2 and ReportLab. No analysis is performed.
Run: python scripts/13_submission_figures.py --out paper/submission
Optional PNG review copies for the manuscript: --previews-dir <directory>.
"""

from argparse import ArgumentParser
from copy import copy
from dataclasses import dataclass
from io import BytesIO
from pathlib import Path
from shutil import copyfile

from PIL import Image
from pypdf import PageObject, PdfReader, PdfWriter, Transformation
from pypdf.generic import ContentStream, NameObject, NumberObject, RectangleObject
from pypdfium2 import PdfDocument
import reportlab
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

ROOT = Path(__file__).resolve().parents[1]
PT_PER_MM = 72 / 25.4
FULL_WIDTH = 174 * PT_PER_MM
BOARD_MARGIN = PT_PER_MM
CONTENT_WIDTH = FULL_WIDTH - 2 * BOARD_MARGIN
DPI = 300
PANEL_FONT = "FigurePanelSansBold"
PANEL_FONT_SIZE = 8


@dataclass(frozen=True)
class Panel:
    """Bounds use the corresponding committed PNG's top-left pixel coordinates."""

    source: str
    bounds: tuple[int, int, int, int]
    labels: tuple[tuple[str, int, int], ...] = ()  # Letter and source x/y baseline.
    gap_after_mm: float = 0

    @property
    def height(self) -> float:
        left, top, right, bottom = self.bounds
        return CONTENT_WIDTH * (bottom - top) / (right - left)


def place_panel(
    page: PageObject, panel: Panel, source: PageObject, pixels: tuple[int, int], top: float
) -> None:
    """Crop and place vector contents without rasterizing source PDF geometry."""
    left, px_top, right, bottom = panel.bounds
    width, height = pixels
    if not (0 <= left < right <= width and 0 <= px_top < bottom <= height):
        raise ValueError(f"Invalid placement bounds for {panel.source}: {panel.bounds}")
    point_width = float(source.mediabox.width)
    point_height = float(source.mediabox.height)
    if tuple(map(float, source.mediabox.lower_left)) != (0.0, 0.0):
        raise ValueError(f"Unexpected media origin in {panel.source}.pdf")
    x_unit = point_width / width
    y_unit = point_height / height
    if abs(x_unit - y_unit) > 1e-5:
        raise ValueError(f"{panel.source}.png does not match the PDF aspect ratio")
    x_min, x_max = left * x_unit, right * x_unit
    y_min, y_max = point_height - bottom * y_unit, point_height - px_top * y_unit
    source = copy(source)
    source.cropbox = RectangleObject((x_min, y_min, x_max, y_max))
    source[NameObject("/Contents")] = limit_source_text(source, y_min, y_max)
    scale = CONTENT_WIDTH / (x_max - x_min)
    transform = Transformation().translate(-x_min, -y_max).scale(scale)
    page.merge_transformed_page(source, transform.translate(BOARD_MARGIN, top))


def limit_source_text(source: PageObject, bottom: float, top: float) -> ContentStream:
    """Keep only the Matplotlib text objects whose baselines are in this crop.

    The crop edges lie in whitespace. Discarding off-crop text keeps project
    figure IDs and clipped repeats out of the searchable PDF text as well.
    """
    contents = source.get_contents()
    operations = contents.operations
    selected = []
    keep = True
    for index, (arguments, operator) in enumerate(operations):
        if operator == b"BT":
            matrix, previous = operations[index - 1]
            if previous != b"cm" or len(matrix) != 6:
                raise ValueError("Expected a Matplotlib text object with a positioned baseline")
            keep = bottom <= float(matrix[5]) <= top
        if keep:
            selected.append((arguments, operator))
        if operator == b"ET":
            keep = True
    contents.operations = selected
    return contents


def resample_orthographic_images(source: PageObject) -> None:
    """Rescale the six 3D stills to about 380 ppi in panel 2B.

    Preserve the shared render scale and use lossless compression in the PDF.
    Resampling to a resolution above the TIFF export target keeps the large
    combined figure under the journal's preferred file size.
    """
    for reference in source["/Resources"]["/XObject"].values():
        image = reference.get_object()
        if (image.get("/Subtype"), image.get("/ColorSpace"), image.get("/BitsPerComponent")) != (
            "/Image", "/DeviceRGB", 8
        ):
            raise ValueError("Unexpected orthographic image encoding")
        size = int(image["/Width"]), int(image["/Height"])
        dimensions = tuple(round(dimension * 0.83) for dimension in size)
        with Image.frombytes("RGB", size, image.get_data()) as bitmap:
            with bitmap.resize(dimensions, Image.Resampling.LANCZOS) as resized:
                image.set_data(resized.tobytes())
        image.pop(NameObject("/DecodeParms"), None)
        image[NameObject("/Width")] = NumberObject(dimensions[0])
        image[NameObject("/Height")] = NumberObject(dimensions[1])


def letter_overlay(height: float, positions: list[tuple[str, float, float]]) -> PageObject:
    """Create vector panel letters in a sans-serif font embedded in the PDF."""
    font = Path(reportlab.__file__).parent / "fonts" / "VeraBd.ttf"
    pdfmetrics.registerFont(TTFont(PANEL_FONT, font))
    payload = BytesIO()
    sheet = canvas.Canvas(payload, pagesize=(FULL_WIDTH, height), invariant=1)
    sheet.setFillColorRGB(32 / 255, 48 / 255, 72 / 255)
    sheet.setFont(PANEL_FONT, PANEL_FONT_SIZE)
    for letter, x, y in positions:
        sheet.drawString(x, y, letter)
    sheet.showPage()
    sheet.save()
    return PdfReader(payload).pages[0]


def compose_figure(path: Path, panels: tuple[Panel, ...]) -> None:
    """Stack cropped panels at full width with their original aspect ratios."""
    root = ROOT / "results" / "figures" / "g4"
    height = 2 * BOARD_MARGIN + sum(
        panel.height + panel.gap_after_mm * PT_PER_MM for panel in panels
    )
    writer = PdfWriter()
    page = writer.add_blank_page(width=FULL_WIDTH, height=height)
    readers: dict[str, tuple[PageObject, tuple[int, int]]] = {}
    labels = []
    top = height - BOARD_MARGIN
    for panel in panels:
        if panel.source not in readers:
            pdf = PdfReader(root / f"{panel.source}.pdf")
            if len(pdf.pages) != 1:
                raise ValueError(f"{panel.source}.pdf must be one page")
            with Image.open(root / f"{panel.source}.png") as raster:
                size = raster.size
            if panel.source == "F3b_18":
                resample_orthographic_images(pdf.pages[0])
            readers[panel.source] = pdf.pages[0], size
        source, pixels = readers[panel.source]
        place_panel(page, panel, source, pixels, top)
        left, px_top, right, _ = panel.bounds
        point_per_px = CONTENT_WIDTH / (right - left)
        labels.extend(
            (letter, BOARD_MARGIN + (x - left) * point_per_px, top - (y - px_top) * point_per_px)
            for letter, x, y in panel.labels
        )
        top -= panel.height + panel.gap_after_mm * PT_PER_MM
    if labels:
        page.merge_page(letter_overlay(height, labels))
    page.compress_content_streams(level=9)
    writer.metadata = None
    writer.add_metadata({"/Title": path.stem.replace("Figure", "Figure ")})
    writer.compress_identical_objects()
    with path.open("wb") as output:
        writer.write(output)


# Strip repository-only headings and excess white space. Each clip starts and
# ends in a blank margin in the committed 300 dpi reference PNG.
FIGURES = {
    2: (
        Panel("F3", (184, 187, 4120, 2014), (("A", 205, 318),), gap_after_mm=4),
        Panel("F3b_18", (111, 184, 3232, 2007), (("B", 129, 275),)),
    ),
    3: (Panel("F4", (115, 199, 3860, 1966)),),
    4: (Panel("F5", (130, 201, 3854, 2048)),),
    5: (Panel("F6", (131, 193, 3850, 1859)),),
    6: (
        Panel(
            "F10",
            (78, 228, 3728, 2231),
            (("A", 94, 389), ("B", 1300, 389), ("C", 2571, 389),
             ("D", 94, 1411), ("E", 1300, 1411), ("F", 2563, 1411)),
            gap_after_mm=4,
        ),
        # Figure 6G retains the common scale of both kits. Close blank gaps
        # between rows without changing the scale, axes, values or table cells.
        Panel("F12", (166, 329, 3010, 416), (("G", 180, 399),), gap_after_mm=1),
        Panel("F12", (166, 466, 3010, 1269), gap_after_mm=2),
        Panel("F12", (166, 1392, 3010, 1445)),
        Panel("F12", (166, 1522, 3010, 1781), gap_after_mm=2),
        Panel("F12", (166, 1906, 3010, 1961)),
        Panel("F12", (166, 2033, 3010, 2352), gap_after_mm=2),
        Panel("F12", (166, 2477, 3010, 2532)),
        Panel("F12", (166, 2599, 3010, 2874), gap_after_mm=2),
        Panel("F12", (166, 2942, 3010, 3662)),
    ),
}


def save_bitmap(image: Image.Image, pdf: Path, preview_dir: Path | None) -> None:
    """Write metadata-free RGB review and submission bitmaps."""
    with Image.frombytes("RGB", image.size, image.convert("RGB").tobytes()) as rendered:
        rendered.save(
            pdf.with_suffix(".tif"), compression="tiff_lzw", dpi=(DPI, DPI),
            tiffinfo={317: 2},  # TIFF Predictor: horizontal differencing (reversible).
        )
        if preview_dir is not None:
            rendered.save(preview_dir / f"{pdf.stem}.png", dpi=(DPI, DPI))


def export_bitmap(pdf: Path, preview_dir: Path | None) -> None:
    """Rasterize the final figure at publication size, preserving the final GA pixels."""
    if pdf.stem == "GraphicalAbstract":
        with Image.open(ROOT / "paper" / "figures" / "fig1" / "GraphicalAbstract.png") as approved:
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


def build_submission_figures(out: Path, previews: Path | None = None) -> None:
    """Build all seven figure PDF/TIFF pairs from existing assets."""
    out.mkdir(parents=True, exist_ok=True)
    if previews is not None:
        previews.mkdir(parents=True, exist_ok=True)
    final_sources = ROOT / "paper" / "figures" / "fig1"
    for stem in ("Figure1", "GraphicalAbstract"):
        copyfile(final_sources / f"{stem}.pdf", out / f"{stem}.pdf")
    for number, panels in FIGURES.items():
        compose_figure(out / f"Figure{number}.pdf", panels)
    for stem in (*(f"Figure{number}" for number in range(1, 7)), "GraphicalAbstract"):
        pdf = out / f"{stem}.pdf"
        export_bitmap(pdf, previews)
        print(f"{pdf.name}: {pdf.stat().st_size:,} bytes | "
              f"{pdf.with_suffix('.tif').name}: {pdf.with_suffix('.tif').stat().st_size:,} bytes")


def main() -> None:
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=ROOT / "paper" / "submission")
    parser.add_argument("--previews-dir", type=Path, help="Optional 300 dpi PNGs for Word proofs")
    args = parser.parse_args()
    build_submission_figures(args.out, args.previews_dir)


if __name__ == "__main__":
    main()
