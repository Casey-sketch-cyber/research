
"""Convert the reviewed submission text and assemble the editable Word manuscript."""

import argparse
from collections import Counter
from io import BytesIO
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
from tempfile import TemporaryDirectory
from zipfile import ZipFile

from docx import Document
from docx.enum.section import WD_ORIENT, WD_SECTION
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_COLOR_INDEX
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor
from pypdf import PdfWriter
import pypdfium2 as pdfium


INPUT_FORMAT = "markdown-smart"
BODIES = "word/document.xml"
BODY_NS = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
MATH_NS = "{http://schemas.openxmlformats.org/officeDocument/2006/math}"
FUNDING = "[AUTHOR TO FILL: funding sources and acknowledgments, or delete if none]"


def parsed_pandoc(pandoc, source):
    result = subprocess.run(
        [str(pandoc), "--from", INPUT_FORMAT, "--to", "json", str(source)],
        check=True,
        capture_output=True,
        encoding="utf-8",
    )
    return json.loads(result.stdout)


def nodes(tree):
    if isinstance(tree, dict):
        yield tree
        if "c" in tree:
            yield from nodes(tree["c"])
    elif isinstance(tree, list):
        for child in tree:
            yield from nodes(child)


def inline_text(content):
    words = []
    for node in nodes(content):
        if node["t"] == "Str":
            words.append(node["c"])
        elif node["t"] in {"Space", "SoftBreak", "LineBreak"}:
            words.append(" ")
    return "".join(words).strip()


def main_manuscript(ast):
    blocks = ast["blocks"]
    cut = next(index for index, block in enumerate(blocks)
               if block["t"] == "Header" and inline_text(block["c"][2]) == "Supplemental information")
    return {**ast, "blocks": blocks[:cut]}


def figure_titles(blocks):
    captions = {}
    for block in blocks:
        if block["t"] not in {"Para", "Plain"} or not block["c"]:
            continue
        first = block["c"][0]
        title = inline_text(first["c"]) if first["t"] == "Strong" else ""
        match = re.match(r"Figure ([1-6])\.", title)
        if match:
            captions[int(match.group(1))] = title
    if sorted(captions) != list(range(1, 7)):
        raise ValueError("The six source figure titles are required for the manuscript")
    return captions


def write_pandoc_docx(pandoc, source, target):
    subprocess.run(
        [str(pandoc), "--from", "json", "--to", "docx", "--fail-if-warnings", "--output", str(target)],
        input=json.dumps(source, ensure_ascii=False).encode("utf-8"),
        check=True,
    )


def tune_style(style, size, spacing=1.5):
    style.font.name = "Arial"
    style.font.size = Pt(size)
    style.font.color.rgb = RGBColor(0, 0, 0)
    style.paragraph_format.line_spacing = spacing
    style.paragraph_format.space_after = Pt(5 if spacing == 1.5 else 3)
    style.paragraph_format.widow_control = True


def set_style(document, manuscript):
    spacing = 1.5 if manuscript else 1.05
    for name in ("Normal", "Body Text", "First Paragraph", "Compact", "Bibliography",
                 "List Paragraph", "Caption", "Table Caption", "Author", "Date"):
        if name in document.styles:
            tune_style(document.styles[name], 11, spacing)
    for level in range(1, 10):
        heading = document.styles[f"Heading {level}"]
        tune_style(heading, 14 if level <= 2 else 11)
        heading.font.bold = True
        heading.paragraph_format.space_before = Pt(10)
        heading.paragraph_format.keep_with_next = True
    title = document.styles["Title"]
    tune_style(title, 21)
    title.font.bold = True
    title.paragraph_format.space_after = Pt(14)


def title_page(document):
    first = document.paragraphs[0]
    first.style = document.styles["Title"]
    for paragraph in document.paragraphs[1:]:
        if paragraph.text == "Summary":
            paragraph.paragraph_format.page_break_before = True
            return
    raise ValueError("The title page has no Summary boundary")


def page_layout(section, landscape=False):
    section.orientation = WD_ORIENT.LANDSCAPE if landscape else WD_ORIENT.PORTRAIT
    section.page_width = Inches(11 if landscape else 8.5)
    section.page_height = Inches(8.5 if landscape else 11)
    section.top_margin = Inches(0.73)
    section.bottom_margin = Inches(0.73)
    section.left_margin = Inches(0.78)
    section.right_margin = Inches(0.78)
    section.footer_distance = Inches(0.36)


def line_numbers(section):
    node = section._sectPr.find(qn("w:lnNumType"))
    if node is None:
        node = OxmlElement("w:lnNumType")
        section._sectPr.insert_element_before(
            node, "w:pgNumType", "w:cols", "w:formProt", "w:vAlign", "w:docGrid")
    node.set(qn("w:countBy"), "1")
    node.set(qn("w:distance"), "255")
    node.set(qn("w:restart"), "continuous")


def number_pages(section):
    paragraph = section.footer.paragraphs[0]
    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    paragraph.paragraph_format.line_spacing = 1.0
    field = OxmlElement("w:fldSimple")
    field.set(qn("w:instr"), "PAGE")
    paragraph._p.append(field)


def layout_tables(document):
    tables_start = next(p for p in document.paragraphs if p.text == "Tables")
    landscape = document.add_section(WD_SECTION.NEW_PAGE)
    break_paragraph = document.paragraphs[-1]._p
    tables_start._p.addprevious(break_paragraph)
    page_layout(landscape, landscape=True)
    line_numbers(landscape)

    widths_by_columns = {
        3: (0.40, 0.29, 0.31),
        7: (0.15, 0.07, 0.12, 0.09, 0.09, 0.16, 0.32),
        8: (0.07, 0.15, 0.11, 0.11, 0.09, 0.09, 0.17, 0.21),
        10: (0.14, 0.08, 0.19, 0.09, 0.075, 0.06, 0.06, 0.06, 0.06, 0.13),
        12: (0.12, 0.13, 0.07, 0.07, 0.07, 0.075, 0.075, 0.075, 0.075, 0.08, 0.08, 0.08),
    }
    for index, table in enumerate(document.tables):
        count = len(table.columns)
        fractions = widths_by_columns.get(count, (1/count,) * count)
        total = sum(fractions)
        available = 6.94 if index == 0 else 9.44
        sizes = [Inches(available * fraction / total) for fraction in fractions]
        table.autofit = False
        for column, width in zip(table.columns, sizes):
            column.width = width
        for row_index, row in enumerate(table.rows):
            row_properties = row._tr.get_or_add_trPr()
            if row_index == 0:
                row_properties.append(OxmlElement("w:tblHeader"))
            row_properties.append(OxmlElement("w:cantSplit"))
            for column_index, cell in enumerate(row.cells):
                cell.width = sizes[column_index]
                if row_index == 0:
                    fill = OxmlElement("w:shd")
                    fill.set(qn("w:fill"), "F1F3F5")
                    cell._tc.get_or_add_tcPr().append(fill)
                for paragraph in cell.paragraphs:
                    paragraph.paragraph_format.line_spacing = 1.5
                    paragraph.paragraph_format.space_after = Pt(3)
                    if row_index == 0:
                        paragraph.paragraph_format.keep_with_next = True
                    for run in paragraph.runs:
                        run.font.size = Pt(10)
                        if row_index == 0:
                            run.bold = True


def picture_content(path):
    with pdfium.PdfDocument(path) as pdf:
        if len(pdf) != 1:
            raise ValueError(f"Expected one page in {path.name}")
        page = pdf[0]
        bitmap = page.render(scale=300 / 72)
        image = bitmap.to_pil().convert("RGB")
        result = BytesIO()
        image.save(result, format="PNG", dpi=(300, 300))
        result.seek(0)
        return result, image.width, image.height


def add_figure_pages(document, titles, figure_dir):
    section = document.add_section(WD_SECTION.NEW_PAGE)
    page_layout(section)
    line_numbers(section)
    for number, title in sorted(titles.items()):
        caption = document.add_paragraph(title, style="Heading 2")
        caption.paragraph_format.page_break_before = number > 1
        caption.paragraph_format.space_before = Pt(0)
        caption.paragraph_format.line_spacing = 1.15
        caption.paragraph_format.space_after = Pt(12)
        paragraph = document.add_paragraph()
        paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
        paragraph.paragraph_format.line_spacing = 1.0
        data, width, height = picture_content(figure_dir / f"Figure{number}.pdf")
        scale = min(6.88 / width, 8.70 / height)
        paragraph.add_run().add_picture(data, width=Inches(width*scale), height=Inches(height*scale))


def scrub_core(document, title):
    properties = document.core_properties
    properties.title = title
    properties.author = ""
    properties.last_modified_by = ""
    properties.subject = ""
    properties.keywords = ""
    properties.comments = ""
    properties.revision = 1


def primary_text_and_math(path):
    from xml.etree import ElementTree as ET

    with ZipFile(path) as doc:
        tree = ET.fromstring(doc.read(BODIES))
    atoms = [(elem.tag, elem.text or "") for elem in tree.iter()
             if elem.tag in {BODY_NS + "t", MATH_NS + "t"}]
    counts = Counter(element.tag for element in tree.iter())
    return atoms, counts


def make_manuscript(repo, pandoc, work, out, figure_dir=None):
    source = main_manuscript(parsed_pandoc(pandoc, repo / "paper/manuscript.md"))
    raw = work / "pandoc-manuscript.docx"
    write_pandoc_docx(pandoc, source, raw)
    atoms_before, counts_before = primary_text_and_math(raw)
    math = [node for block in source["blocks"] for node in nodes(block) if node["t"] == "Math"]
    if counts_before[MATH_NS + "oMath"] != len(math):
        raise ValueError("The source math count does not match the native Word equation count")

    document = Document(raw)
    set_style(document, manuscript=True)
    title_page(document)
    page_layout(document.sections[0])
    line_numbers(document.sections[0])
    number_pages(document.sections[0])
    highlighted = False
    for paragraph in document.paragraphs:
        if paragraph.text == FUNDING:
            for run in paragraph.runs:
                run.font.highlight_color = WD_COLOR_INDEX.YELLOW
            highlighted = True
        if re.match(r"^Table [1-4]\.", paragraph.text):
            paragraph.paragraph_format.keep_with_next = True
    if not highlighted:
        raise ValueError("The source funding placeholder could not be located in Word")
    layout_tables(document)
    titles = figure_titles(source["blocks"]) if figure_dir is not None else {}
    if titles:
        add_figure_pages(document, titles, figure_dir)
    scrub_core(document, "Manuscript")
    document.save(out)
    raw_text, counts = primary_text_and_math(out)
    after = atoms_before + [(BODY_NS + "t", titles[number]) for number in sorted(titles)]
    if raw_text != after or counts[MATH_NS + "oMath"] != len(math):
        raise ValueError("Manuscript words, numbers or math changed during layout")
    native_tables = counts[BODY_NS + "tbl"]
    if native_tables != sum(node["t"] == "Table" for node in nodes(source["blocks"])):
        raise ValueError("A source table was not preserved as a native Word table")
    return {"native_equations": len(math), "native_tables": native_tables,
            "figure_pages": len(titles)}


def make_cover_letter(repo, pandoc, work, output):
    source = parsed_pandoc(pandoc, repo / "paper/cover_letter.md")
    raw = work / "pandoc-cover-letter.docx"
    write_pandoc_docx(pandoc, source, raw)
    document = Document(raw)
    set_style(document, manuscript=False)
    section = document.sections[0]
    page_layout(section)
    section.top_margin = Inches(0.64)
    section.bottom_margin = Inches(0.64)
    for paragraph in document.paragraphs:
        if paragraph.text == "Sincerely,":
            paragraph.paragraph_format.keep_with_next = True
    scrub_core(document, "Cover letter")
    document.save(output)
    if primary_text_and_math(raw)[0] != primary_text_and_math(output)[0]:
        raise ValueError("The cover letter text changed during layout")


WORD_PDF_COMMAND = r"""
$ErrorActionPreference='Stop'
$word=$null
$doc=$null
$saveNothing=0
try {
    $word=New-Object -ComObject Word.Application
    $word.DisplayAlerts=0
    $doc=$word.Documents.Open($env:SUBMISSION_DOCX,$false,$true,$false)
    $doc.Repaginate()
    $doc.ExportAsFixedFormat($env:SUBMISSION_PDF,17,$false)
} finally {
    if ($null -ne $doc) {
        $doc.Close([ref]$saveNothing)
        [void][Runtime.InteropServices.Marshal]::ReleaseComObject($doc)
    }
    if ($null -ne $word) {
        if ($word.Documents.Count -eq 0) { $word.Quit([ref]$saveNothing) }
        [void][Runtime.InteropServices.Marshal]::ReleaseComObject($word)
    }
}
"""


def export_word_pdf(input_docx, output_pdf):
    """Use installed Word on Windows; support LibreOffice on other systems."""
    output_pdf = output_pdf.resolve()
    with TemporaryDirectory(prefix="pdf-export-", dir=output_pdf.parent) as staging:
        raw = Path(staging) / output_pdf.name
        if os.name == "nt":
            env = {**os.environ, "SUBMISSION_DOCX": str(input_docx.resolve()), "SUBMISSION_PDF": str(raw)}
            subprocess.run(
                ["powershell.exe", "-NoProfile", "-NonInteractive", "-Command", WORD_PDF_COMMAND],
                env=env, check=True, timeout=180,
            )
        else:
            soffice = shutil.which("soffice") or shutil.which("libreoffice")
            if not soffice:
                raise RuntimeError("Install LibreOffice for native Word-to-PDF export on this platform")
            subprocess.run(
                [soffice, f"-env:UserInstallation={(raw.parent/'office').as_uri()}",
                 "--headless", "--convert-to", "pdf", "--outdir", str(raw.parent), str(input_docx.resolve())],
                check=True, timeout=180,
            )
        publisher = PdfWriter(clone_from=raw)
        publisher.metadata = None
        publisher.root_object.pop("/Metadata", None)
        publisher.add_metadata({"/Title": output_pdf.stem})
        with output_pdf.open("wb") as stream:
            publisher.write(stream)


def build_word(repo, pandoc, work, output, figure_dir):
    work.mkdir(parents=True, exist_ok=True)
    output.mkdir(parents=True, exist_ok=True)
    manuscript = output / "Manuscript.docx"
    report = make_manuscript(repo, pandoc, work, manuscript, figure_dir)
    make_cover_letter(repo, pandoc, work, output / "CoverLetter.docx")
    export_word_pdf(manuscript, output / "Manuscript.pdf")
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--export-pdf", nargs=2, metavar=("DOCX", "PDF"), type=Path, required=True)
    args = parser.parse_args()
    export_word_pdf(*args.export_pdf)
