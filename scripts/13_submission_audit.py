"""Audit manuscript source and basic submission package structure without editing either."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import subprocess
import unicodedata
from xml.etree import ElementTree as ET
from zipfile import ZipFile

SECTION = re.compile(r"^#{1,6}\s+(.+?)\s*$")
CAPTION = re.compile(r"^\s*\*\*(Figure|Table)\s+(S?\d+)\.")
REF_YEAR = r"(?:19|20)\d{2}[a-z]?"
REFERENCE = re.compile(rf"^-\s+(.+?)\s+\(({REF_YEAR})\)\.")
CITATION_NAME = r"[^\W\d_][\w.'’\-]*(?:\s+[^\W\d_][\w.'’\-]*)*"
PARENTHETICAL = re.compile(rf"^(?P<name>{CITATION_NAME}),\s*(?P<year>{REF_YEAR})$")
BRACKET_GROUP = re.compile(r"\(([^()]*)\)")
TOKEN = r"S?\d+(?:[A-Z](?:[-–][A-Z])?)?(?![\w.,]\d|\w)"
CROSS_REFERENCE = re.compile(
    rf"\b(Figure|Table)s?\s+({TOKEN}(?:\s*(?:[-–,]|\band\b)\s*{TOKEN})*)"
)
POINTER = re.compile(r"(S?)(\d+)(?:[A-Z](?:[-–][A-Z])?)?")
PLACEHOLDER = re.compile(r"\[\s*(AUTHOR TO FILL|CITE\b|NEEDS\b)|\b(TO MINT)\b", re.I)
LEGEND_PATH = re.compile(r"(?<![\w/])(?:paper|results|config|scripts|docs|data|src|manuscript|reports)/[^ \t)<>'\x60]+")
INLINE_MATH = re.compile(r"(?<![\\$])\$(?!\$)[^\n$]+?(?<!\\)\$(?!\$)")
DISPLAY_MATH = re.compile(r"(?<![\\$])\$\$(?!\$).*?(?<!\\)\$\$(?!\$)", re.S)
EXPECTED_IDS = {"Figure": 6, "Table": 4, "Figure S": 6, "Table S": 4}
PACKAGE_NAMES = {
    "Manuscript.docx", "Manuscript.pdf", "GraphicalAbstract.pdf", "GraphicalAbstract.tif",
    "Highlights.txt", "SupplementalInformation.pdf", "CoverLetter.docx", "CHECKLIST.md", "ISSUES.md",
} | {f"Figure{number}.{extension}" for number in range(1, 7) for extension in ("pdf", "tif")}
NS = {
    "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
    "m": "http://schemas.openxmlformats.org/officeDocument/2006/math",
}


def alphabetical_key(text: str) -> str:
    """Sort accented characters alongside their base letters."""
    return "".join(
        char for char in unicodedata.normalize("NFKD", text.casefold())
        if not unicodedata.combining(char)
    )


def citation_label(authors: str) -> str:
    if "," not in authors:
        return authors
    surname = authors.split(",", 1)[0]
    if ", and " in authors:
        leading, final = authors.rsplit(", and ", 1)
        if leading.count(",") == 1:
            return f"{surname} and {final.split(',', 1)[0]}"
        return f"{surname} et al."
    return surname


def citations_in(line: str, labels: list[str]):
    """Yield author and year from parenthetical groups and narrative forms."""
    for group in BRACKET_GROUP.finditer(line):
        contents = group.group(1)
        if re.fullmatch(REF_YEAR, contents):
            prefix = line[:group.start()].rstrip()
            matching = next(
                (
                    label
                    for label in labels
                    if re.search(rf"(?<!\w){re.escape(label)}(?:['’]s)?$", prefix)
                ), None,
            )
            if matching:
                yield matching, contents
            elif re.search(r"[^\W\d_]$", prefix):
                fallback = re.search(r"(?<!\w)([A-ZÀ-ÖØ-Þ][\w.'’\-]*(?: et al\.)?(?:['’]s)?)$", prefix)
                yield (fallback.group(1) if fallback else "[unrecognized narrative author]"), contents
            continue
        for candidate in contents.split(";"):
            citation = PARENTHETICAL.fullmatch(candidate.strip())
            if citation:
                yield citation.group("name"), citation.group("year")


def cited_ids(line: str):
    """Expand compact references such as Figures 3 and 4 or Figures S1–S3."""
    for match in CROSS_REFERENCE.finditer(line):
        kind, sequence = match.groups()
        previous = None
        for pointer in POINTER.finditer(sequence):
            prefix, digits = pointer.groups()
            number = int(digits)
            prior_prefix, prior_number, end = previous if previous else ("", 0, 0)
            separator = sequence[end:pointer.start()].strip()
            prefix = prefix or prior_prefix
            if previous and separator in {"-", "–"} and prefix == prior_prefix and number > prior_number:
                for in_range in range(prior_number + 1, number):
                    yield f"{kind} {prefix}{in_range}"
            yield f"{kind} {prefix}{number}"
            previous = (prefix, number, pointer.end())


def title_lines(lines: list[str]) -> dict[str, int]:
    return {
        match.group(1): position
        for position, line in enumerate(lines, start=1)
        if (match := SECTION.fullmatch(line))
    }


def audit_manuscript(markdown: str, cover_letter: str = "") -> dict:
    """Check source declarations, references, citations and visible author placeholders."""
    lines = markdown.splitlines()
    sections = title_lines(lines)
    bibliography = sections["References"]
    legends = sections["Figure legends"]
    supplement = sections["Supplemental information"]
    summary = sections["Summary"]

    definitions = {}
    duplicate_declarations = set()
    for index, line in enumerate(lines, 1):
        caption = CAPTION.match(line)
        if caption:
            item = " ".join(caption.groups())
            if item in definitions:
                duplicate_declarations.add(item)
            definitions[item] = index

    expected = {
        f"{kind} {number}" if not kind.endswith(" S") else f"{kind}{number}"
        for kind, count in EXPECTED_IDS.items()
        for number in range(1, count + 1)
    }
    first = {}
    cited_at = {}
    for index, line in enumerate(lines, 1):
        if summary <= index < bibliography or index >= legends:
            caption = CAPTION.match(line)
            if caption:
                line = line[caption.end():]
            for cited in cited_ids(line):
                cited_at.setdefault(cited, index)
                if index < bibliography:
                    first.setdefault(cited, index)
    first_citation = {}
    order = {}
    issues = []
    for kind, count in EXPECTED_IDS.items():
        prefix = kind if kind.endswith(" S") else f"{kind} "
        actual = [item for item in first if item.startswith(prefix) and item[len(prefix):].isdigit()]
        requested = [f"{prefix}{number}" for number in range(1, count + 1)]
        first_citation[kind] = {item: first[item] for item in actual}
        order[kind] = actual == requested
        if actual != requested:
            found = ", ".join(f"{item.rsplit(' ', 1)[1]} (line {first[item]})" for item in actual)
            issues.append(f"{kind} items occur in first-citation order {found or 'none'}; the frozen manuscript text is retained.")
    undefined = sorted(cited_at.keys() - definitions.keys())
    missing = sorted(expected - definitions.keys())
    undeclared = sorted(set(definitions) - expected)
    for note, items in (
        ("Cited items with no caption or legend", undefined),
        ("Expected items with no caption or legend", missing),
        ("Unexpected item declarations", undeclared),
        ("Duplicate item declarations", sorted(duplicate_declarations)),
    ):
        if items:
            issues.append(f"{note} — {', '.join(items)}.")

    references = []
    for index in range(bibliography, legends - 1):
        match = REFERENCE.match(lines[index])
        if match:
            authors, year = match.groups()
            references.append((citation_label(authors), year))
    labels = sorted({entry[0] for entry in references}, key=len, reverse=True)
    in_text = {}
    occurrences = 0
    for index, line in enumerate(lines, 1):
        if index < summary or bibliography <= index < legends:
            continue
        for citation in citations_in(line, labels):
            occurrences += 1
            in_text.setdefault(citation, index)
    no_reference = sorted(set(in_text) - set(references))
    uncited = sorted(set(references) - set(in_text))
    alphabetical = [a for a, _ in references] == sorted([a for a, _ in references], key=alphabetical_key)
    if no_reference:
        values = ", ".join(f"{author} ({year}) at line {in_text[(author,year)]}" for author,year in no_reference)
        issues.append(f"In-text author–year citations without a matching reference — {values}.")
    if uncited:
        values = ", ".join(f"{author} ({year})" for author,year in uncited)
        issues.append(f"Uncited reference entries — {values}.")
    if not alphabetical:
        issues.append("The reference list is out of alphabetical order by first author.")

    placeholders = []
    for filename, document in (("manuscript.md", markdown), ("cover_letter.md", cover_letter)):
        for index, line in enumerate(document.splitlines(), 1):
            for match in PLACEHOLDER.finditer(line):
                placeholders.append({"file": filename, "line": index, "kind": next(g for g in match.groups() if g)})
    acknowledgments = sections["Acknowledgments"]
    contributions = sections["Author contributions"]
    only_funding = (
        len(placeholders) == 1
        and placeholders[0]["file"] == "manuscript.md"
        and placeholders[0]["kind"] == "AUTHOR TO FILL"
        and acknowledgments < placeholders[0]["line"] < contributions
        and "funding" in lines[placeholders[0]["line"] - 1].casefold()
    )
    if not only_funding:
        issues.append("The visible placeholders differ from the single acknowledged funding placeholder.")
    legend_paths = []
    for index, line in enumerate(lines, 1):
        if index > legends and not line.lstrip().startswith("|"):
            legend_paths.extend({"line": index, "path": match.group()} for match in LEGEND_PATH.finditer(line))
    if legend_paths:
        issues.append("One or more figure or table legends contain repository paths.")

    main_text = "\n".join(lines[:supplement-1])
    inline_count = len(INLINE_MATH.findall(main_text))
    display_count = len(DISPLAY_MATH.findall(main_text))
    return {
        "cross_references": {
            "declared": len(definitions),
            "cited_items": len(cited_at),
            "first_citation": first_citation,
            "in_number_order": order,
            "undefined": undefined,
            "missing": missing,
        },
        "citations": {
            "reference_entries": len(references),
            "unique_cited_keys": len(in_text),
            "citation_occurrences": occurrences,
            "missing_reference": [f"{author} ({year})" for author,year in no_reference],
            "uncited_reference": [f"{author} ({year})" for author,year in uncited],
            "alphabetical_by_author": alphabetical,
        },
        "placeholders": placeholders,
        "only_funding_placeholder": only_funding,
        "legend_paths": legend_paths,
        "source_structure": {
            "main_inline_equations": inline_count,
            "main_display_equations": display_count,
            "main_equations": inline_count + display_count,
            "supplemental_inline_equations": len(INLINE_MATH.findall("\n".join(lines[supplement:]))),
        },
        "issues": issues,
    }


def audit_package(package: Path, expected_main_equations: int | None = None) -> dict:
    """Inspect deliverable existence and visible Word structures."""
    files = {path.name: path.stat().st_size for path in package.iterdir() if path.is_file()}
    result = {"sizes_bytes": files, "missing_or_empty": sorted(PACKAGE_NAMES - {name for name, size in files.items() if size > 0})}
    manuscript = package / "Manuscript.docx"
    if manuscript.exists() and manuscript.stat().st_size:
        with ZipFile(manuscript) as document:
            content = ET.fromstring(document.read("word/document.xml"))
            styles = ET.fromstring(document.read("word/styles.xml"))
        equations = len(content.findall(".//m:oMath", NS))
        highlight = f"{{{NS['w']}}}val"
        paragraphs = content.findall(".//w:p", NS)
        yellow = False
        for paragraph in paragraphs:
            text, coverage = "", []
            for run in paragraph.findall(".//w:r", NS):
                segment = "".join(node.text or "" for node in run.findall(".//w:t", NS))
                text += segment
                color = run.find("w:rPr/w:highlight", NS)
                coverage.extend([color is not None and color.get(highlight) == "yellow"] * len(segment))
            funding = re.search(r"\[AUTHOR TO FILL[^\]]*\]", text)
            if funding:
                yellow = all(coverage[funding.start():funding.end()])
                break
        tables = content.findall(".//w:tbl", NS)
        expected_key_resources = ["REAGENT or RESOURCE", "SOURCE", "IDENTIFIER"]
        key_resources_table = False
        for table in tables:
            headers = [
                "".join(node.text or "" for node in cell.findall(".//w:t", NS)).strip()
                for cell in table.findall("w:tr[1]/w:tc", NS)
            ]
            if headers == expected_key_resources:
                key_resources_table = True
                break
        result["manuscript_docx"] = {
            "native_equations": equations,
            "matches_expected_equations": None if expected_main_equations is None else equations == expected_main_equations,
            "real_tables": len(tables),
            "key_resources_is_word_table": key_resources_table,
            "line_number_sections": len(content.findall(".//w:lnNumType", NS)),
            "has_1_5_line_spacing_setting": any(
                item.get(f"{{{NS['w']}}}line") == "360" and item.get(f"{{{NS['w']}}}lineRule", "auto") == "auto"
                for root in (content, styles)
                for item in root.findall(".//w:spacing", NS)
            ),
            "funding_yellow_highlight": yellow,
        }
    highlights = package / "Highlights.txt"
    if highlights.exists():
        lines = highlights.read_text(encoding="utf-8-sig").splitlines()
        result["highlight_lengths"] = [len(line) for line in lines if line.strip()]
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=Path.cwd(), help="repository checkout")
    parser.add_argument("--ref", help="read manuscript and letter from this Git ref")
    parser.add_argument("--package", type=Path, help="also inspect a built submission package")
    args = parser.parse_args()

    def source(path: str) -> str:
        if args.ref:
            return subprocess.check_output(
                ["git", "show", f"{args.ref}:{path}"], cwd=args.repo
            ).decode("utf-8-sig")
        return (args.repo / path).read_text(encoding="utf-8-sig")

    report = audit_manuscript(source("paper/manuscript.md"), source("paper/cover_letter.md"))
    if args.package:
        report["package"] = audit_package(
            args.package, report["source_structure"]["main_equations"]
        )
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
