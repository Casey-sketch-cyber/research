"""Build the approved Buildings manuscript and cover letter as native Word files."""

from __future__ import annotations

import argparse
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
import re
import subprocess
from zipfile import ZipFile

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.opc.constants import RELATIONSHIP_TYPE as RT
from docx.shared import Mm, Pt
from docx.table import Table
from docx.text.paragraph import Paragraph
from PIL import Image


CITATION = re.compile(r"\[(@[\w:-]+(?:;\s*@[\w:-]+)*)\]")
BIBITEM = re.compile(r"\\bibitem(?:\[[^\]]*?\])?\{([^{}]+)\}\s*")
CAPTION = re.compile(r"^(Figure|Table) ([1-6])\.")
HEADING_STYLES = {
    "Heading1": "MDPI12title",
    "Heading2": "MDPI21heading1",
    "Heading3": "MDPI22heading2",
    "Heading4": "MDPI23heading3",
}
FRONT_STYLES = ("MDPI13authornames", *("MDPI16affiliation",) * 4, "MDPI17abstract", "MDPI18keywords")
TABLE_WIDTHS = (
    (10, 27, 17, 17, 14, 15, 37, 44),
    (28, 13, 19, 16, 17, 35, 53),
    (23, 8, 11, 12, 20, 20, 12, 16, 11, 16, 16, 16),
    (31, 11, 45, 16, 12, 9, 9, 9, 9, 30),
)
NEUTRAL_DATE = datetime(2000, 1, 1, tzinfo=timezone.utc)


def read_bibliography(bbl: Path) -> tuple[list[str], str]:
    """Extract the actual mdpi.bst entries and keep their ordered LaTeX markup."""
    data = bbl.read_text(encoding="utf-8-sig").split(r"\end{thebibliography}", 1)[0]
    _, *parts = BIBITEM.split(data)
    keys = parts[0::2]
    entries = []
    for entry in parts[1::2]:
        entry = re.sub(r"(?m)^%[^\n]*", "", entry)
        entry = entry.replace(r"\newblock", " ")
        entries.append(" ".join(entry.split()))
    if len(keys) != 30 or len(set(keys)) != len(keys):
        raise ValueError("Expected the 30 unique numbered entries from the reviewed LaTeX build")
    return keys, "\n\n".join(entries) + "\n"


def number_citations(source: str, keys: list[str]) -> str:
    first_use = list(dict.fromkeys(
        key for item in CITATION.finditer(source) for key in re.findall(r"@([\w:-]+)", item[1])
    ))
    if first_use != keys:
        raise ValueError("BibTeX order disagrees with first citation order in the approved manuscript")
    labels = {key: i for i, key in enumerate(keys, 1)}

    def replacement(match: re.Match) -> str:
        numbers = sorted({labels[key] for key in re.findall(r"@([\w:-]+)", match[1])})
        runs = [[numbers[0]]]
        for number in numbers[1:]:
            if number == runs[-1][-1] + 1:
                runs[-1].append(number)
            else:
                runs.append([number])
        rendered = []
        for run in runs:
            if len(run) >= 3:
                rendered.append(f"{run[0]}–{run[-1]}")
            else:
                rendered.extend(str(n) for n in run)
        return "[" + ",".join(rendered) + "]"

    numbered = CITATION.sub(replacement, source)
    if re.search(r"\[@|NEEDS EVIDENCE", numbered):
        raise ValueError("Unresolved citation keys or evidence markers in the approved text")
    # Affiliations are separate title-page paragraphs, not a Markdown soft-wrapped line.
    return re.sub(r"\n(?=(?:[¹²³] |\\\* Correspondence:))", "\n\n", numbered)


def convert(pandoc: str, source: str, output: Path, input_format: str) -> None:
    subprocess.run(
        [pandoc, "--from", input_format, "--to", "docx", "--fail-if-warnings", "--output", str(output)],
        input=source.encode("utf-8"),
        check=True,
    )


def normalized_template(template: Path, copy: Path) -> Document:
    """Open the publisher's OOXML .dot without changing the original archive."""
    with ZipFile(template) as packed, ZipFile(copy, "w") as unpacked:
        for item in packed.infolist():
            data = packed.read(item.filename)
            if item.filename == "[Content_Types].xml":
                data = data.replace(
                    b"wordprocessingml.template.main+xml",
                    b"wordprocessingml.document.main+xml",
                )
            unpacked.writestr(item, data)
    return Document(copy)


def atoms(node) -> tuple[str, ...]:
    return tuple(node.xpath(".//w:t/text() | .//m:t/text()"))


def transplant(node, source, target):
    clone = deepcopy(node)
    for hyperlink in clone.xpath(".//w:hyperlink[@r:id]"):
        relation = source.part.rels[hyperlink.get(qn("r:id"))]
        if not relation.is_external or relation.reltype != RT.HYPERLINK:
            raise ValueError("Unexpected link in the native Word conversion")
        hyperlink.set(qn("r:id"), target.part.relate_to(relation.target_ref, RT.HYPERLINK, is_external=True))
    target._body._element.insert_element_before(clone, "w:sectPr")
    return clone


def clean_chrome(doc: Document) -> None:
    """Remove sample-only publication placeholders, retaining the journal furniture."""
    for section in doc.sections:
        for header in (section.header, section.even_page_header, section.first_page_header):
            for paragraph in header.paragraphs:
                text = paragraph._p.xpath(".//w:t")
                if "FOR PEER REVIEW" in "".join(item.text or "" for item in text):
                    # These example publication fields sit between the journal name and review notice.
                    for item in text[1:]:
                        if "FOR PEER REVIEW" in (item.text or ""):
                            break
                        item.text = ""
        for footer in (section.footer, section.first_page_footer):
            for p in footer.paragraphs:
                if "10.3390/xxxxx" in p.text or "16, x" in p.text:
                    p.clear()
    settings = doc.settings._element
    settings.append(OxmlElement("w:doNotAutoCompressPictures"))
    update = OxmlElement("w:updateFields")
    update.set(qn("w:val"), "true")
    settings.append(update)


def scrub_core(doc: Document, title: str) -> None:
    props = doc.core_properties
    props.title = title
    props.subject = props.author = props.last_modified_by = props.keywords = props.comments = ""
    props.created = props.modified = NEUTRAL_DATE
    props.revision = 1


def journal_list(doc: Document, paragraph: Paragraph, template_id: int, lists: dict[int, int]) -> None:
    """Restart each source list using the corresponding MDPI numbering definition."""
    num_pr = paragraph._p.pPr.numPr
    source_id = num_pr.numId.val
    if source_id not in lists:
        numbering = doc.part.numbering_part.element
        next_id = max(int(n.get(qn("w:numId"))) for n in numbering.xpath("./w:num")) + 1
        style_num, = numbering.xpath(f"./w:num[@w:numId='{template_id}']")
        copy = deepcopy(style_num)
        copy.set(qn("w:numId"), str(next_id))
        if template_id == 22:
            override = OxmlElement("w:lvlOverride")
            override.set(qn("w:ilvl"), "0")
            restart = OxmlElement("w:startOverride")
            restart.set(qn("w:val"), "1")
            override.append(restart)
            copy.append(override)
        numbering.append(copy)
        lists[source_id] = next_id
    num_pr.numId.val = lists[source_id]


def figure_paragraph(doc: Document, before, number: int, directory: Path, styles) -> None:
    path = directory / f"Figure{number}.png"
    with Image.open(path) as rendered:
        width, height = rendered.size
        xdpi, ydpi = rendered.info["dpi"]
        if min(xdpi, ydpi) < 599.9:
            raise ValueError(f"{path.name} does not carry at least 600 dpi metadata")
    # Wider landscape plates use the full template layout. Reserve room for each caption.
    visual_width = min(174.0, 172.0 * width / height)
    art = Paragraph(before, doc._body).insert_paragraph_before(style=styles["MDPI52figure"])
    art.paragraph_format.keep_with_next = True
    shape = art.add_run().add_picture(str(path), width=Mm(visual_width))
    shape._inline.docPr.set("descr", f"Figure {number}. See the caption immediately below.")


def format_table(table: Table, index: int, styles) -> None:
    widths = TABLE_WIDTHS[index]
    if len(table.columns) != len(widths):
        raise ValueError(f"Table {index + 1} does not match the reviewed column structure")
    table.style = styles["MDPItable"]
    table.autofit = False
    properties = table._tbl.tblPr
    for remove in ("w:tblInd", "w:tblBorders", "w:tblCellMar"):
        for child in properties.xpath(f"./{remove}"):
            properties.remove(child)
    margins = OxmlElement("w:tblCellMar")
    for edge in ("top", "bottom", "left", "right"):
        prop = OxmlElement(f"w:{edge}")
        prop.set(qn("w:w"), "35" if edge in {"left", "right"} else "30")
        prop.set(qn("w:type"), "dxa")
        margins.append(prop)
    properties.append(margins)
    borders = OxmlElement("w:tblBorders")
    for edge in ("top", "bottom"):
        item = OxmlElement(f"w:{edge}")
        item.set(qn("w:val"), "single")
        item.set(qn("w:sz"), "6")
        item.set(qn("w:color"), "000000")
        borders.append(item)
    properties.append(borders)
    for col, width in zip(table.columns, widths, strict=True):
        col.width = Mm(width)
    for ri, row in enumerate(table.rows):
        row_pr = row._tr.get_or_add_trPr()
        row_pr.append(OxmlElement("w:cantSplit"))
        if ri == 0:
            row_pr.append(OxmlElement("w:tblHeader"))
        cells = row.cells
        group = ri > 0 and not any(atoms(cell._tc) for cell in cells[1:])
        for ci, (cell, width) in enumerate(zip(cells, widths, strict=True)):
            cell.width = Mm(width)
            if ri == 0:
                cb = OxmlElement("w:tcBorders")
                b = OxmlElement("w:bottom")
                b.set(qn("w:val"), "single")
                b.set(qn("w:sz"), "4")
                b.set(qn("w:color"), "000000")
                cb.append(b)
                cell._tc.get_or_add_tcPr().append(cb)
            for paragraph in cell.paragraphs:
                paragraph.style = styles["MDPI42tablebody"]
                paragraph.alignment = WD_ALIGN_PARAGRAPH.LEFT if ci == 0 else WD_ALIGN_PARAGRAPH.CENTER
                fmt = paragraph.paragraph_format
                fmt.space_before = Pt(0)
                fmt.space_after = Pt(0)
                fmt.line_spacing = 1.08
                fmt.keep_with_next = ri == 0 or group
                # Size ordinary text and native OMML runs together; template minimum is 8 pt.
                for node in paragraph._p.xpath(".//w:r | .//m:r"):
                    rpr = node.find(qn("w:rPr"))
                    if rpr is None:
                        rpr = OxmlElement("w:rPr")
                        node.insert(0 if node.tag == qn("w:r") else len(node) - 1, rpr)
                    for tag in ("w:sz", "w:szCs"):
                        size = rpr.find(qn(tag))
                        if size is None:
                            size = OxmlElement(tag)
                            rpr.append(size)
                        size.set(qn("w:val"), "16" if index == 2 else "18")
                    if ri == 0 and node.tag == qn("w:r") and rpr.find(qn("w:b")) is None:
                        rpr.append(OxmlElement("w:b"))


def build_manuscript(args) -> None:
    source_text = (args.repo / "paper/buildings/manuscript.md").read_text(encoding="utf-8")
    keys, references = read_bibliography(args.bbl)
    source_text = number_citations(source_text, keys)
    native = args.work_dir / "manuscript-native.docx"
    convert(args.pandoc, source_text, native, "markdown-smart+autolink_bare_uris")
    bib_docx = args.work_dir / "references-native.docx"
    convert(args.pandoc, references, bib_docx, "latex-smart")
    source = Document(native)
    bibliography = Document(bib_docx)
    doc = normalized_template(args.template, args.work_dir / "template-converted.docx")
    styles = {style.style_id: style for style in doc.styles}
    body = doc._body._element
    body.clear_content()
    for rid, relation in tuple(doc.part.rels.items()):
        if relation.reltype in (RT.IMAGE, RT.HYPERLINK):
            doc.part.drop_rel(rid)
    clean_chrome(doc)
    title = source.paragraphs[0].text
    scrub_core(doc, title)
    doc.add_paragraph("Article", style=styles["MDPI11articletype"])
    front_count, table_count = 0, 0
    main_text = False
    figures = []
    lists = {}
    for node in source._body._element:
        if node.tag not in {qn("w:p"), qn("w:tbl")}:
            continue
        plain = "".join(atoms(node))
        if not plain.strip() and not node.xpath(".//m:oMath"):
            # Pandoc writes the approved Markdown horizontal rule as an empty decorative paragraph.
            continue
        clone = transplant(node, source, doc)
        if clone.tag == qn("w:tbl"):
            format_table(Table(clone, doc._body), table_count, styles)
            table_count += 1
        else:
            paragraph = Paragraph(clone, doc._body)
            source_style = node.xpath("./w:pPr/w:pStyle/@w:val")
            role = source_style[0] if source_style else ""
            match = CAPTION.match(plain)
            if role in HEADING_STYLES:
                paragraph.style = styles[HEADING_STYLES[role]]
                paragraph.paragraph_format.keep_with_next = True
                if role == "Heading2":
                    main_text = True
            elif not main_text:
                paragraph.style = styles[FRONT_STYLES[front_count]]
                front_count += 1
                if front_count == len(FRONT_STYLES):
                    doc.add_paragraph(style=styles["MDPI19line"])
            elif match and match[1] == "Figure":
                number = int(match[2])
                figures.append(number)
                paragraph.style = styles["MDPI51figurecaption"]
                paragraph.paragraph_format.keep_together = True
                figure_paragraph(doc, clone, number, args.figure_dir, styles)
            elif match:
                paragraph.style = styles["MDPI41tablecaption"]
                paragraph.paragraph_format.keep_with_next = True
                paragraph.paragraph_format.keep_together = True
            elif plain.startswith(("Supplementary Materials:", "Author Contributions:", "Funding:",
                                  "Institutional Review Board Statement:", "Informed Consent Statement:",
                                  "Data Availability Statement:", "Acknowledgments:", "Conflicts of Interest:")):
                paragraph.style = styles["MDPI62backmatter"]
            elif clone.xpath("./w:pPr/w:numPr"):
                list_roles = ("MDPI38bullet", 20) if plain.startswith("RQ") else ("MDPI37itemize", 22)
                paragraph.style = styles[list_roles[0]]
                journal_list(doc, paragraph, list_roles[1], lists)
            else:
                paragraph.style = styles["MDPI31text"]
                if clone.xpath("./m:oMathPara"):
                    paragraph.style = styles["MDPI39equation"]
        if atoms(clone) != atoms(node):
            raise ValueError("Paragraph or table wording changed while applying the journal styles")
    if front_count != len(FRONT_STYLES) or table_count != len(TABLE_WIDTHS) or figures != list(range(1, 7)):
        raise ValueError("Missing a required title-page block, table, or figure")
    entries = [p for p in bibliography.paragraphs if p.text.strip()]
    if len(entries) != len(keys):
        raise ValueError("Pandoc bibliography formatting did not preserve each entry")
    for entry in entries:
        clone = transplant(entry._p, bibliography, doc)
        Paragraph(clone, doc._body).style = styles["MDPI81references"]
    doc.save(args.out / "manuscript.docx")


def build_cover(args) -> None:
    text = (args.repo / "paper/buildings/cover_letter.md").read_text(encoding="utf-8")
    raw = args.work_dir / "cover-letter-native.docx"
    convert(args.pandoc, text, raw, "markdown-smart+autolink_bare_uris")
    doc = Document(raw)
    original = atoms(doc._body._element)
    for section in doc.sections:
        section.page_width = Mm(210)
        section.page_height = Mm(297)
        section.top_margin = Mm(19)
        section.bottom_margin = Mm(18)
        section.left_margin = section.right_margin = Mm(20)
    for name in ("Normal", "Body Text", "First Paragraph", "Compact"):
        style = doc.styles[name]
        style.font.name = "Palatino Linotype"
        style.font.size = Pt(11)
        fmt = style.paragraph_format
        fmt.space_before = Pt(0)
        fmt.space_after = Pt(6)
        fmt.line_spacing = 1.08
        fmt.widow_control = True
    for paragraph in doc.paragraphs:
        if paragraph.text.strip() == "Sincerely,":
            paragraph.paragraph_format.keep_with_next = True
        paragraph.paragraph_format.keep_together = True
    if original != atoms(doc._body._element):
        raise ValueError("Cover letter text changed during formatting")
    scrub_core(doc, "Cover Letter")
    doc.save(args.out / "CoverLetter.docx")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=Path.cwd())
    parser.add_argument("--template", type=Path, required=True)
    parser.add_argument("--bbl", type=Path, required=True)
    parser.add_argument("--figure-dir", type=Path, required=True)
    parser.add_argument("--pandoc", required=True)
    parser.add_argument("--work-dir", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    for path in (args.work_dir, args.out):
        path.mkdir(parents=True, exist_ok=True)
    build_manuscript(args)
    build_cover(args)


if __name__ == "__main__":
    main()
