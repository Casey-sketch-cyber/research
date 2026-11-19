"""Compose the reviewed supplemental legends, tables, and final-size supplemental plate PDFs."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import os
from pathlib import Path
import re
import shutil
import subprocess
from tempfile import TemporaryDirectory

from pypdf import PdfReader, PdfWriter, Transformation
from pypdf.generic import NameObject


POINTS_PER_MM = 72 / 25.4
TOP_MARGIN_MM = 14
TITLE_HEIGHT_MM = 16

# All source plates are generated at final physical size by the figure builder.
# Leave their geometry and embedded typography unchanged during placement.
@dataclass(frozen=True)
class FigurePage:
    number: int
    filename: str
    caption_part: int | None = None


FIGURE_PAGES = (
    FigurePage(1, "FigureS1"),
    FigurePage(2, "FigureS2A", caption_part=0),
    FigurePage(2, "FigureS2B", caption_part=1),
    FigurePage(3, "FigureS3"),
    FigurePage(4, "FigureS4"),
    FigurePage(5, "FigureS5"),
    FigurePage(6, "FigureS6"),
    FigurePage(7, "FigureS7"),
)


STYLES = """
@page portrait { size: A4; margin: 14mm 15mm 17mm; }
@page wide { size: A4 landscape; margin: 14mm 15mm 17mm; }
html { font-family: Arial, sans-serif; font-size: 10pt; color: #162433; }
body { margin: 0; line-height: 1.33; }
article { page: portrait; break-before: page; }
article:first-of-type { break-before: auto; }
article.wide { page: wide; }
h1 { font-size: 18pt; line-height: 1.22; }
.supplement-title { box-sizing: border-box; margin: 0; height: 16mm; }
.picture { box-sizing: content-box; margin: 0 auto; position: relative; }
.legend { margin-top: 4mm; }
.legend p { margin: 0 0 6pt; }
.legend > p:first-child { font-size: 11pt; line-height: 1.24; }
table { border-collapse: collapse; width: 100%; font-size: 9pt; margin: 8pt 0 12pt; }
thead { display: table-header-group; }
tr { break-inside: avoid; }
th, td { border-bottom: .45pt solid #c0c8d0; padding: 3.2pt 4.5pt; vertical-align: top; }
th { border-bottom: .8pt solid #748295; background: #eef2f6; }
tbody tr:nth-child(even) { background: #f6f8fa; }
table p, table ul { margin: 0; }
p { orphans: 2; widows: 2; }
p:has(> em:only-child) { font-size: 10pt; break-after: avoid; }
.table-title { font-size: 12pt; margin: 0 0 6pt; }
"""


def split_numbered(section: str, kind: str) -> dict[int, str]:
    parts = re.split(rf"(?m)(?=^\*\*{kind} S\d+\.)", section)
    numbered = {
        int(re.match(rf"\*\*{kind} S(\d+)\.", part).group(1)): part.strip()
        for part in parts[1:]
    }
    expected_count = 7 if kind == "Figure" else 4
    if set(numbered) != set(range(1, expected_count + 1)):
        raise ValueError(f"Unexpected supplemental {kind.lower()} numbers")
    return numbered


def markdown_groups(manuscript: str) -> tuple[dict[int, str], dict[int, str]]:
    supplement = manuscript.split("\n## Supplemental information\n", 1)[1]
    figures, tables = supplement.split("\n### Supplemental tables\n", 1)
    return split_numbered(figures, "Figure"), split_numbered(tables, "Table")


def caption_markdown(captions: dict[int, str], spec: FigurePage) -> str:
    full_caption = captions[spec.number]
    if spec.caption_part is None:
        return full_caption
    # Figure S2 has an approved paragraph for each panel. Keep each next to
    # the corresponding existing 3D view, with the same heading on both pages.
    lines = [line for line in full_caption.splitlines() if line.strip()]
    if len(lines) != 3 or not lines[1].startswith("(A)") or not lines[2].startswith("(B)"):
        raise ValueError("Figure S2 legend no longer has two named panel paragraphs")
    return f"{lines[0]}\n\n{lines[1 + spec.caption_part]}"


def markdown_to_html(pandoc: str, markdown: str, env: dict[str, str]) -> str:
    # Give a standalone visual line to the exact Markdown legend heading.
    markdown = re.sub(r"^(\*\*(?:Figure|Table) S\d+\.[^\n]+\*\*)\n(?!\n)", r"\1\n\n",
                      markdown, count=1)
    converted = subprocess.run(
        [pandoc, "--from=markdown-smart", "--to=html5", "--math-method=mathml"],
        input=markdown, capture_output=True, encoding="utf-8", check=True, env=env,
    )
    if converted.stderr.strip():
        raise RuntimeError(converted.stderr.strip())
    return converted.stdout


def detect_browser() -> str:
    for executable in ("chrome", "chromium", "chromium-browser", "msedge"):
        found = shutil.which(executable)
        if found:
            return found
    for variable in ("ProgramFiles", "ProgramFiles(x86)"):
        base = os.environ.get(variable)
        if not base:
            continue
        for relative in ("Google/Chrome/Application/chrome.exe", "Microsoft/Edge/Application/msedge.exe"):
            candidate = Path(base) / relative
            if candidate.is_file():
                return str(candidate)
    raise FileNotFoundError("Chrome, Chromium or Edge is required to render the supplemental tables")


def figure_html(source, caption: str, is_first: bool) -> str:
    width, height = float(source.mediabox.width), float(source.mediabox.height)
    if width > 180 * POINTS_PER_MM:
        raise ValueError("The final-size supplemental plate exceeds the A4 print area")
    title = '<h1 class="supplement-title">Supplemental information</h1>' if is_first else ""
    return (f'<article>{title}'
            f'<div class="picture" style="width:{width:.5f}pt;height:{height:.5f}pt"></div>'
            f'<div class="legend">{caption}</div></article>')


def supplement_citations(captions: dict[int, str], manuscript: str) -> str:
    citation = "Bu and Che Mat's (2026)"
    if captions[6].count(citation) != 1:
        raise ValueError("Review the supplemental citation mapping after the Figure S6 legend change")
    captions[6] = captions[6].replace(citation, "Bu and Che Mat's [S1]")
    references = manuscript.split("\n## References\n", 1)[1].split("\n## Figure legends\n", 1)[0]
    entry, = [line.removeprefix("- ") for line in references.splitlines()
              if line.startswith("- Bu, S., and Che Mat, R. (2026). ")]
    return "[S1] " + entry


def build_supplement(
    repo: Path, output: Path, pandoc: str, work_dir: Path, figure_dir: Path, browser: str | None = None,
) -> None:
    """Build only from committed plots and reviewed manuscript text."""
    work_dir.mkdir(parents=True, exist_ok=True)
    output.parent.mkdir(parents=True, exist_ok=True)
    manuscript = (repo / "paper/manuscript.md").read_text(encoding="utf-8")
    captions, tables = markdown_groups(manuscript)
    supplemental_reference = supplement_citations(captions, manuscript)
    source_pages = []
    for spec in FIGURE_PAGES:
        reader = PdfReader(figure_dir / f"{spec.filename}.pdf")
        if len(reader.pages) != 1:
            raise ValueError(f"{spec.filename} must be one final-size plate")
        source_pages.append(reader.pages[0])

    with TemporaryDirectory(dir=work_dir, prefix="supplement-") as directory:
        build = Path(directory)
        env = os.environ | {name: str(build) for name in ("TEMP", "TMP", "TMPDIR")}
        body = []
        for index, (spec, source) in enumerate(zip(FIGURE_PAGES, source_pages, strict=True)):
            caption = markdown_to_html(pandoc, caption_markdown(captions, spec), env)
            body.append(figure_html(source, caption, index == 0))
        for number in range(1, 4):
            table = tables[number]
            heading = "<h1>Supplemental tables</h1>" if number == 1 else ""
            rendered = markdown_to_html(pandoc, table, env)
            rendered = rendered.replace("<p><strong>Table S", '<p class="table-title"><strong>Table S', 1)
            body.append(f'<article class="wide">{heading}{rendered}</article>')

        reference = markdown_to_html(pandoc, supplemental_reference, env)
        body.append(f'<article><h1>Supplemental references</h1>{reference}</article>')

        html = build / "SupplementalInformation.html"
        html.write_text(
            '<!doctype html><html lang="en"><meta charset="utf-8">'
            f'<title>Supplemental Information</title><style>{STYLES}</style>'
            f'<body>{"".join(body)}</body></html>',
            encoding="utf-8",
        )
        base_pdf = build / "typeset.pdf"
        command = [
            browser or detect_browser(), "--headless=new", "--disable-gpu", "--no-first-run",
            "--no-default-browser-check", "--disable-background-networking",
            f"--user-data-dir={build / 'browser-profile'}", f"--disk-cache-dir={build / 'browser-cache'}",
            "--no-pdf-header-footer", f"--print-to-pdf={base_pdf}", html.as_uri(),
        ]
        result = subprocess.run(command, env=env, capture_output=True, check=True, timeout=90)
        if not base_pdf.is_file():
            raise RuntimeError(result.stderr.decode("utf-8", errors="replace"))

        typeset = PdfReader(base_pdf)
        if len(typeset.pages) <= len(FIGURE_PAGES):
            raise RuntimeError("Typeset supplement omitted figure or table pages")
        writer = PdfWriter(clone_from=typeset)
        for index, (spec, source) in enumerate(zip(FIGURE_PAGES, source_pages, strict=True)):
            destination = writer.pages[index]
            if f"Figure S{spec.number}." not in destination.extract_text():
                raise RuntimeError(f"Figure S{spec.number} caption overflowed its page")
            width, height = float(source.mediabox.width), float(source.mediabox.height)
            page_top = float(destination.mediabox.height)
            top = page_top - TOP_MARGIN_MM * POINTS_PER_MM
            if index == 0:
                top -= TITLE_HEIGHT_MM * POINTS_PER_MM
            left = (float(destination.mediabox.width) - width) / 2
            destination.merge_transformed_page(
                source, Transformation().translate(left, top - height), over=False,
            )
        writer.metadata = None
        writer.root_object.pop(NameObject("/Metadata"), None)
        writer.add_metadata({"/Title": "Supplemental Information"})
        writer.write(output)

    rendered = PdfReader(output)
    pages = [p.extract_text() for p in rendered.pages]
    for number in range(1, 4):
        if not any(f"Table S{number}." in page for page in pages[len(FIGURE_PAGES):]):
            raise RuntimeError(f"Table S{number} did not render")
    if "Supplemental references" not in pages[-1] or "[S1]" not in pages[-1]:
        raise RuntimeError("The numbered supplemental reference is missing")
    if any("Table S4. Geometry-only surrogate accuracy" in page for page in pages):
        raise RuntimeError("Excel-only Table S4 must not also appear in the PDF")
    print(f"Supplemental Information: {len(pages)} pages, seven figures, three PDF tables, and one reference")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=Path.cwd())
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--pandoc", default="pandoc")
    parser.add_argument("--work-dir", type=Path, required=True)
    parser.add_argument("--figure-dir", type=Path, required=True)
    parser.add_argument("--browser")
    args = parser.parse_args()
    build_supplement(args.repo, args.output, args.pandoc, args.work_dir.resolve(), args.figure_dir, args.browser)


if __name__ == "__main__":
    main()
