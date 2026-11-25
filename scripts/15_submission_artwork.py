"""Package the approved, unchanged artwork for Buildings and set its supplementary legends."""

from __future__ import annotations

import argparse
from html import escape
from importlib import import_module
from math import ceil
import os
from pathlib import Path
import re
from shutil import copyfile
import subprocess
from tempfile import TemporaryDirectory

from pypdf import PdfReader, PdfWriter, Transformation
from pypdf.generic import NameObject, RectangleObject
import pypdfium2 as pdfium


ARTWORK_DPI = 600
# PNG records an integer number of pixels per metre.
PNG_DPI = ceil(ARTWORK_DPI / 0.0254) * 0.0254
# Page order in the frozen iScience supplement. Figure S2 has two plates.
FIGURE_NUMBERS = (1, 2, 2, 3, 4, 5, 6, 7)
POINTS_PER_MM = 72 / 25.4
TOP_MARGIN_MM = 14
TITLE_HEIGHT_MM = 29
# Share the established Pandoc/MathML and Chromium rendering setup.
submission_layout = import_module("14_submission_supplement")


def export_figures(source: Path, figures: Path) -> None:
    """Keep source vectors and render matching full-size 600 dpi RGB PNGs."""
    figures.mkdir(parents=True, exist_ok=True)
    for number in range(1, 7):
        stem = f"Figure{number}"
        vector = source / f"{stem}.pdf"
        with pdfium.PdfDocument(vector) as document:
            if len(document) != 1:
                raise ValueError(f"{vector.name} must have exactly one page")
            page = document[0]
            bitmap = page.render(scale=ARTWORK_DPI / 72)
            rendered = bitmap.to_pil().convert("RGB")
        rendered.save(figures / f"{stem}.png", dpi=(PNG_DPI, PNG_DPI), optimize=True)
        copyfile(vector, figures / vector.name)
        print(f"{stem}: {rendered.width} × {rendered.height} pixels at {ARTWORK_DPI} dpi")

    for extension in ("pdf", "tif"):
        filename = f"GraphicalAbstract.{extension}"
        copyfile(source / filename, figures / filename)


def split_items(section: str, item_type: str, count: int) -> dict[int, str]:
    marker = rf"^\*\*{item_type} S(\d+):\*\*"
    labels = list(re.finditer(marker, section, flags=re.M))
    if [int(item.group(1)) for item in labels] != list(range(1, count + 1)):
        raise ValueError(f"Supplementary {item_type.lower()} numbers do not match the approved order")
    result = {}
    for number, item in enumerate(labels, start=1):
        end = labels[number].start() if number < count else len(section)
        result[number] = section[item.start():end].strip()
    return result


def caption_source(repo: Path) -> tuple[str, dict[int, str], dict[int, str]]:
    """Read the locked Buildings legends and use the shared MDPI citation numbering."""
    base = repo / "paper/buildings"
    manuscript = (base / "manuscript.md").read_text(encoding="utf-8")
    manuscript_title = re.search(r"^# (.+)$", manuscript, flags=re.M).group(1)
    bib = (repo / "paper/references.bib").read_text(encoding="utf-8")
    entries = set(re.findall(r"(?im)^@\w+\s*\{\s*([^,\s]+)", bib))
    main_keys = [key for key in dict.fromkeys(re.findall(r"@([\w:-]+)", manuscript)) if key in entries]
    citation_numbers = {key: number for number, key in enumerate(main_keys, start=1)}
    legend_text = (base / "supplementary_legends.md").read_text(encoding="utf-8")
    if manuscript_title not in legend_text.split("\n## Supplementary Figures\n", 1)[0]:
        raise ValueError("The two approved sources disagree on the manuscript title")
    figure_text, table_text = legend_text.split("\n## Supplementary Figures\n", 1)[1].split(
        "\n## Supplementary Tables\n", 1,
    )
    figure_text = figure_text.removesuffix("\n").removesuffix("\n---").strip()

    def replace_citation(match: re.Match) -> str:
        keys = re.findall(r"@([\w:-]+)", match.group(0))
        try:
            return "[" + ",".join(str(citation_numbers[key]) for key in keys) + "]"
        except KeyError as exc:
            raise ValueError(f"Supplementary citation {exc} is missing from the cited main bibliography") from exc

    def render_citations(text: str) -> str:
        rendered = re.sub(r"\[\s*@[\w:-]+(?:\s*;\s*@[\w:-]+)*\s*\]", replace_citation, text)
        if re.search(r"@[\w:-]+", rendered):
            raise ValueError("Unexpected unresolved citation in supplementary text")
        return rendered

    return manuscript_title, split_items(render_citations(figure_text), "Figure", 7), split_items(
        render_citations(table_text), "Table", 4,
    )


def extract_plate(archived_page, owner: PdfWriter):
    """Recover the source vector plate, the archive page's first graphics group."""
    page = owner.add_page(archived_page)
    stream = page.get_contents()
    operations = stream.operations
    if [operator for _, operator in operations[:5]] != [b"q", b"cm", b"re", b"W", b"n"]:
        raise ValueError("Cannot identify the frozen plate's placement and clipping rectangle")
    matrix = tuple(float(value) for value in operations[1][0])
    rect = tuple(float(value) for value in operations[2][0])
    if matrix[:4] != (1, 0, 0, 1) or rect[:2] != (0, 0):
        raise ValueError("The archived plate is not at its original physical size")
    _, _, width, height = rect
    depth = 1
    for i, (_, operator) in enumerate(operations[1:], start=1):
        if operator == b"q":
            depth += 1
        elif operator == b"Q":
            depth -= 1
            if depth == 0:
                break
    else:
        raise ValueError("The archived plate's graphics group is incomplete")
    # Remove just the old position transform, retaining the clipping and all original art.
    stream.operations = operations[:1] + operations[2:i + 1]
    page.replace_contents(stream)
    for key in ("/Annots", "/StructParents", "/TrimBox", "/BleedBox", "/ArtBox"):
        page.pop(key, None)
    page.mediabox = RectangleObject((0, 0, width, height))
    page.cropbox = RectangleObject((0, 0, width, height))
    return page


def caption_for_plate(captions: dict[int, str], index: int) -> str:
    """Place the two approved Figure S2 panel descriptions next to their plates."""
    number = FIGURE_NUMBERS[index]
    full = captions[number]
    if number != 2:
        return full
    heading, panel_a_b = full.split(" (A) ", 1)
    panel_a, panel_b = panel_a_b.split(" (B) ", 1)
    if index == 1:
        return f"{heading}\n\n\\(A) {panel_a}"
    return f"{heading}\n\n\\(B) {panel_b}"


def building_supplement(repo: Path, source: Path, out: Path, pandoc: str, work_dir: Path) -> None:
    """Place unaltered vector plates over a PDF of the approved Buildings legends and tables."""
    title, figures, tables = caption_source(repo)
    archive = PdfReader(source / "SupplementalInformation.pdf")
    plate_store = PdfWriter()
    plates = [extract_plate(archive.pages[i], plate_store) for i in range(len(FIGURE_NUMBERS))]
    work_dir.mkdir(parents=True, exist_ok=True)
    with TemporaryDirectory(prefix="buildings-supplement-", dir=work_dir) as folder:
        build = Path(folder).resolve()
        env = os.environ | {name: str(build) for name in ("TEMP", "TMP", "TMPDIR")}
        body = []
        for index, plate in enumerate(plates):
            width, height = float(plate.mediabox.width), float(plate.mediabox.height)
            header = (
                f'<header class="supplement-title"><h1>Supplementary Materials</h1>'
                f'<p>{escape(title)}</p></header>' if index == 0 else ""
            )
            caption = submission_layout.markdown_to_html(pandoc, caption_for_plate(figures, index), env)
            body.append(f'<article>{header}'
                        f'<div class="picture" style="width:{width:.5f}pt;height:{height:.5f}pt"></div>'
                        f'<div class="legend">{caption}</div></article>')
        for number, table in tables.items():
            heading = "<h1>Supplementary Tables</h1>" if number == 1 else ""
            text = submission_layout.markdown_to_html(pandoc, table, env)
            text = text.replace("<p><strong>Table S", '<p class="table-title"><strong>Table S', 1)
            body.append(f'<article class="wide">{heading}{text}</article>')
        html = build / "SupplementaryMaterials.html"
        styles = submission_layout.STYLES + f"""
.supplement-title {{ height: {TITLE_HEIGHT_MM}mm; }}
.supplement-title h1 {{ margin: 0 0 5pt; }}
.supplement-title p {{ margin: 0; font-size: 12pt; }}
"""
        html.write_text(
            '<!doctype html><html lang="en"><meta charset="utf-8">'
            f'<title>Supplementary Materials</title><style>{styles}</style>'
            f'<body>{"".join(body)}</body></html>',
            encoding="utf-8",
        )
        typeset = build / "legends-and-tables.pdf"
        subprocess.run([
            submission_layout.detect_browser(), "--headless=new", "--disable-gpu", "--no-first-run",
            "--no-default-browser-check", "--disable-background-networking",
            f"--user-data-dir={build / 'browser-profile'}", f"--disk-cache-dir={build / 'browser-cache'}",
            "--no-pdf-header-footer", f"--print-to-pdf={typeset}", html.as_uri(),
        ], env=env, check=True, capture_output=True, timeout=90)

        writer = PdfWriter(clone_from=typeset)
        for index, (number, plate) in enumerate(zip(FIGURE_NUMBERS, plates, strict=True)):
            page = writer.pages[index]
            text = page.extract_text()
            if f"Figure S{number}:" not in text:
                raise RuntimeError(f"Figure S{number} caption overflowed its page")
            width, height = float(plate.mediabox.width), float(plate.mediabox.height)
            top = float(page.mediabox.height) - TOP_MARGIN_MM * POINTS_PER_MM
            if index == 0:
                top -= TITLE_HEIGHT_MM * POINTS_PER_MM
            left = (float(page.mediabox.width) - width) / 2
            page.merge_transformed_page(plate, Transformation().translate(left, top - height), over=False)
        writer.metadata = None
        writer.root_object.pop(NameObject("/Metadata"), None)
        writer.add_metadata({"/Title": "Supplementary Materials"})
        writer.write(out)

    exported = PdfReader(out)
    later_pages_text = "\n".join(page.extract_text() for page in exported.pages[len(plates):])
    for number in tables:
        if f"Table S{number}:" not in later_pages_text:
            raise RuntimeError(f"Table S{number} is missing from the supplement")
    print(f"SupplementaryMaterials.pdf: {len(exported.pages)} pages, seven figures and four tables")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=Path.cwd())
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--pandoc", default="pandoc")
    parser.add_argument("--work-dir", type=Path, required=True)
    parser.add_argument("--supplement-only", action="store_true")
    args = parser.parse_args()
    source = args.repo / "paper/submission-v2/upload"
    args.out.mkdir(parents=True, exist_ok=True)
    if not args.supplement_only:
        export_figures(source, args.out / "figures")
        copyfile(source / "TableS4.xlsx", args.out / "TableS4.xlsx")
    building_supplement(args.repo, source, args.out / "SupplementaryMaterials.pdf",
                        args.pandoc, args.work_dir)


if __name__ == "__main__":
    main()
