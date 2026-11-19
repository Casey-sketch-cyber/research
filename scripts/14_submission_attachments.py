"""Build the standalone iScience Word attachments and Table S4 input."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import subprocess
from tempfile import TemporaryDirectory


from docx import Document
from docx.oxml import OxmlElement
from docx.shared import Inches, Pt, RGBColor


def content_between(text: str, begin: str, end: str) -> str:
    return text.split(begin, 1)[1].split(end, 1)[0].strip()


def render_docx(pandoc: str, markdown: str, output: Path) -> None:
    subprocess.run(
        [pandoc, "--from=markdown-smart", "--to=docx", "--fail-if-warnings",
         "--output", str(output)],
        check=True, input=markdown.encode("utf-8"),
    )


def set_common_layout(document, title: str) -> None:
    for section in document.sections:
        section.page_width, section.page_height = Inches(8.5), Inches(11)
        section.top_margin, section.bottom_margin = Inches(0.65), Inches(0.65)
        section.left_margin, section.right_margin = Inches(0.65), Inches(0.65)
    normal = document.styles["Normal"]
    normal.font.name, normal.font.size = "Arial", Pt(11)
    normal.font.color.rgb = RGBColor(0, 0, 0)
    normal.paragraph_format.space_after = Pt(5)
    normal.paragraph_format.line_spacing = 1.08

    heading = document.styles["Title"]
    heading.font.name, heading.font.size, heading.font.bold = "Arial", Pt(15), True
    heading.font.color.rgb = RGBColor(0, 0, 0)
    heading.paragraph_format.space_after = Pt(8)
    heading.paragraph_format.keep_with_next = True
    for border in heading._element.xpath(".//w:pBdr"):
        border.getparent().remove(border)

    props = document.core_properties
    props.title, props.subject = title, ""
    props.author = props.last_modified_by = props.keywords = props.comments = ""
    props.created = datetime(2000, 1, 1, tzinfo=timezone.utc)
    props.modified = props.created


def write_highlights(manuscript: str, output: Path) -> None:
    block = content_between(manuscript, "\n## Highlights\n", "\n## eTOC blurb\n")
    statements = [line.removeprefix("- ").strip() for line in block.splitlines()]
    assert len(statements) == 4 and all(0 < len(text) <= 85 for text in statements)
    document = Document()
    set_common_layout(document, "Highlights")
    document.add_paragraph("Highlights", "Title")
    for text in statements:
        paragraph = document.add_paragraph(text, "List Bullet")
        paragraph.paragraph_format.space_after = Pt(6)
        paragraph.paragraph_format.keep_together = True
    document.save(output)
    reopened = Document(output)
    assert [p.text for p in reopened.paragraphs] == ["Highlights", *statements]
    assert [p.style.name for p in reopened.paragraphs[1:]] == ["List Bullet"] * 4


def word_text(node) -> str:
    return "".join(node.xpath(".//w:t/text()"))


def write_key_resources(manuscript: str, pandoc: str, work_dir: Path, output: Path) -> None:
    source = content_between(manuscript, "\n### Key resources table\n", "\n### Resource availability\n")
    expected = read_pipe_table(source)
    with TemporaryDirectory(prefix="key-resources-", dir=work_dir) as staging:
        scratch = Path(staging) / "KeyResourcesTable.docx"
        render_docx(pandoc, source, scratch)
        document = Document(scratch)
    set_common_layout(document, "Key resources table")
    title = document.add_paragraph("Key resources table", "Title")
    table, = document.tables

    title._element.getparent().remove(title._element)
    table._tbl.addprevious(title._element)
    table.autofit = False
    widths = (2.00, 1.37, 3.83)
    for width, column in zip(widths, table.columns, strict=True):
        column.width = Inches(width)
    for index, row in enumerate(table.rows):
        row._tr.get_or_add_trPr().append(OxmlElement("w:cantSplit"))
        group = index > 0 and not expected[index][1] and not expected[index][2]
        if not index:
            row._tr.get_or_add_trPr().append(OxmlElement("w:tblHeader"))
        for width, cell in zip(widths, row.cells, strict=True):
            cell.width = Inches(width)
            for paragraph in cell.paragraphs:
                paragraph.style = document.styles["Normal"]
                paragraph.paragraph_format.space_after = Pt(3)
                paragraph.paragraph_format.space_before = Pt(2)
                paragraph.paragraph_format.keep_with_next = group
                paragraph.paragraph_format.line_spacing = 1.05
                for run in paragraph.runs:
                    run.font.name = "Arial"
                    run.font.size = Pt(10)
                    if index == 0 or group:
                        run.bold = True
    document.save(output)
    reopened = Document(output)
    found, = reopened.tables
    actual = [[word_text(c._tc) for c in row.cells] for row in found.rows]
    assert actual == expected, "Key resources row, link, or identifier changed during conversion"


def read_pipe_table(markdown: str) -> list[list[str]]:
    lines = [line.strip() for line in markdown.splitlines() if line.startswith("| ")]
    rows = [[c.strip().replace("**", "") for c in line.strip("|").split("|")] for line in lines]
    return [rows[0], *rows[2:]]


S4_MATH = {r"\Delta\text{EA}": "ΔEA", r"\text{FCI}\ge 0.95": "FCI ≥ 0.95",
           r"\text{FCI} \ge 0.95": "FCI ≥ 0.95", r"R^2": "R²", r"\rho": "ρ", "n": "n", "n = 172": "n = 172",
           "n = 873": "n = 873", "n = 510": "n = 510"}


def workbook_input(manuscript: str) -> dict[str, object]:
    table = manuscript.split("\n**Table S4.", 1)[1].strip()
    intro, data = table.split("\n\n| ", 1)
    title, legend = intro.split("**\n", 1)

    def display(value):
        return re.sub(r"\$(.*?)\$", lambda m: S4_MATH[m.group(1)], value)

    table_rows = read_pipe_table("| " + data)
    assert len(table_rows) == 49 and {len(row) for row in table_rows} == {11}
    return {
        "title": "Table S4. " + title.strip(),
        "legend": display(legend),
        "rows": [[display(cell) for cell in row] for row in table_rows],
    }


def build_attachments(repo: Path, output: Path, pandoc: str, work_dir: Path) -> None:
    work_dir.mkdir(parents=True, exist_ok=True)
    output.mkdir(parents=True, exist_ok=True)
    manuscript = (repo / "paper/manuscript.md").read_text(encoding="utf-8")
    write_highlights(manuscript, output / "Highlights.docx")
    write_key_resources(manuscript, pandoc, work_dir, output / "KeyResourcesTable.docx")
    (work_dir / "TableS4-input.json").write_text(json.dumps(workbook_input(manuscript),
        ensure_ascii=False, indent=2), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=Path.cwd())
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--pandoc", default="pandoc")
    parser.add_argument("--work-dir", type=Path, required=True)
    args = parser.parse_args()
    build_attachments(args.repo, args.output, args.pandoc, args.work_dir)


if __name__ == "__main__":
    main()
