
"""Regenerate the iScience review package from the locked, committed sources.

Requires Pandoc, python-docx, pypdf, pypdfium2, Pillow, ReportLab, Chromium
and either Microsoft Word (Windows) or LibreOffice (other platforms).
"""

import argparse
from importlib import import_module
import os
from pathlib import Path
import shutil
from tempfile import TemporaryDirectory

from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]
AUDIT = import_module("13_submission_audit")
FIGURES = import_module("13_submission_figures")
SUPPLEMENT = import_module("13_submission_supplement")
WORD = import_module("13_submission_word")
JOURNAL_DATE = "2026-11-19"
FILE_SIZE_PREFERENCE = 2_000_000


def filename_inventory(package, checklist_bytes):
    files = {p.name: p.stat().st_size for p in package.iterdir() if p.is_file()}
    files["CHECKLIST.md"] = checklist_bytes
    return "\n".join(f"| {name} | {size:,} |" for name, size in sorted(files.items()))


def reference_order(audit, group):
    return ", ".join(
        f"{item} (line {line})"
        for item, line in audit["cross_references"]["first_citation"][group].items()
    )


def highlights(markdown):
    section = markdown.split("\n## Highlights\n", 1)[1].split("\n## ", 1)[0]
    items = [line[2:] for line in section.splitlines() if line.startswith("- ")]
    if len(items) != 4:
        raise ValueError("Expected the four approved highlights")
    return items


def size_exceptions(package):
    return [f"{p.name} ({p.stat().st_size:,} bytes)"
            for p in sorted(package.glob("Figure*")) if p.stat().st_size > FILE_SIZE_PREFERENCE]


def make_issues(audit, package):
    details = [
        "- The approved title page still includes its title-options and author-selection text. "
        "The conversion preserves this source text for review.",
        "- Figure 2 uses all three floor-plan rows in F3 for panel A and the 18.00 m² 3D views from "
        "F3b_18 for panel B, as described in its legend. The handoff shorthand highlights the 18.00 m² example.",
        "- Figure S5 reproduces F9, which includes a 30 s solver-limit condition in addition to "
        "the 60 s and 120 s conditions named in the approved legend.",
        f"- Supplemental figure first-citation order is {reference_order(audit, 'Figure S')}.",
        f"- Supplemental table first-citation order is {reference_order(audit, 'Table S')}.",
        "- The Acknowledgments funding placeholder is still visible and highlighted in yellow in the manuscript.",
        "- Cell Press's graphical-abstract guide specifies Arial at 12–16 pt and advises using a graphical form "
        "for data. The final approved abstract uses 10.56 pt body text, 11.52 pt column headings "
        "and a +3.5 m² example callout. The exports preserve the approved design.",
        "- Existing labels on portions of Figures 2–6 are about 3.8–5.7 pt at 174 mm, below the "
        "handoff target of about 7 pt. The package preserves the approved plots and their labels. "
        "New panel letters are 8 pt.",
        "- Figure 6 combines all seven panels in a 174 × 268 mm separate file. The review copy "
        "in the manuscript scales it to fit on one page.",
        "- The journal-specific iScience Information for Authors and ScienceDirect Guide for Authors returned "
        "HTTP 403 on the check date. Journal-specific initial submission rules remain unconfirmed.",
    ]
    oversized = size_exceptions(package)
    if oversized:
        details.append("- These figure files exceed the handoff's preferred 2 MB size. " + ", ".join(oversized) + ".")
    return "# Submission issues\n\n" + "\n".join(details) + "\n"


def make_checklist(audit, package, word_receipt, items):
    cross = audit["cross_references"]
    citations = audit["citations"]
    main_pages = len(PdfReader(package / "Manuscript.pdf").pages)
    supplement_pages = len(PdfReader(package / "SupplementalInformation.pdf").pages)
    oversized = size_exceptions(package)
    sizes = ", ".join(oversized) if oversized else "All separate main figure files are under 2 MB."
    text = f"""# iScience submission package checklist

## Publisher guidance checked on {JOURNAL_DATE}

- The [iScience Information for Authors](https://www.cell.com/iscience/authors) is linked from the official [iScience pre-submission page](https://info.cell.com/iscience-pre-submission). The author page and the [ScienceDirect Guide for Authors](https://www.sciencedirect.com/journal/iscience/publish/guide-for-authors) returned HTTP 403. The package follows the committed handoff for the Word/PDF manuscript, separate figure options and the 2 MB size preference. See ISSUES.md for the verification limit.
- The [Cell Press graphical abstract guide](https://crosstalk.cell.com/hubfs/Files/GA_guide.pdf) specifies a single 5.5-inch square at 300 dpi, which gives 1,650 × 1,650 pixels, and lists TIFF and PDF among the preferred formats. The package includes both. The approved sizes and numeric callout are recorded in ISSUES.md.
- [Elsevier graphical abstract guidance](https://www.elsevier.com/researcher/author/tools-and-resources/graphical-abstract) calls for a separate file. [Elsevier artwork sizing guidance](https://www.elsevier.com/about/policies-and-standards/author/artwork-and-media-instructions/artwork-sizing) gives general size and resolution recommendations. The main figures use the handoff's 174 mm width, and the TIFFs are RGB, LZW-compressed at 300 dpi.
- Separate figure file sizes relative to the handoff's 2 MB preference. {sizes}

## Content checks

- {cross['cited_items']} distinct figure and table references match {cross['declared']} declared items. Main figures and tables follow first-citation order. Supplemental order exceptions are listed in ISSUES.md.
- All {citations['reference_entries']} author–year references match citations in both directions. The reference list is alphabetical.
- The legend audit found no repository paths. The placeholder audit found one acknowledged funding line and no CITE, NEEDS or TO MINT markers. The funding line is yellow in Word.
- The main Word file has {word_receipt['native_equations']} native equations and {word_receipt['native_tables']} editable tables, including the Key resources table. It uses line numbers and 1.5 line spacing in its text. The PDF proof has {main_pages} pages with one titled main figure on each of its last six pages.
- The four highlights are copied verbatim to separate lines, with lengths {', '.join(str(len(item)) for item in items)} characters.
- The {supplement_pages}-page supplement contains Figures S1–S6 and Tables S1–S4 with the approved text. S2 uses one page per 3D panel.
- The cover letter is converted from the committed source. The package retains the wording and numbers of the approved manuscript, legends, tables and cover letter.

## Figure assembly map

| Item | Committed source |
| --- | --- |
| Figure 1 | Final Figure1.pdf |
| Figure 2 | F3 and F3b_18 |
| Figures 3–5 | F4, F5 and F6, respectively |
| Figure 6 | F10 and F12 |
| Graphical abstract | Final GraphicalAbstract.pdf |
| Figures S1–S6 | F2, F3b_10 and F3b_30, F7, F8, F9, F11 |
| Tables S1–S3 | T2, T5 and the D1 portion of T6 |
| Table S4 | Committed K3 kit and paired-effects/size-band outputs |

## Files

| File | Size (bytes) |
| --- | ---: |
"""
    size = 0
    while True:
        checklist = text + filename_inventory(package, size) + "\n"
        calculated = len(checklist.encode("utf-8"))
        if calculated == size:
            return checklist
        size = calculated


def validate_documents(audit, package):
    result = AUDIT.audit_package(package, audit["source_structure"]["main_equations"])
    if result["missing_or_empty"]:
        raise ValueError(f"Missing or empty deliverables {result['missing_or_empty']}")
    word = result["manuscript_docx"]
    if not all([
        word["matches_expected_equations"], word["key_resources_is_word_table"],
        word["has_1_5_line_spacing_setting"], word["funding_yellow_highlight"],
        word["line_number_sections"] >= 3, word["real_tables"] == 5,
        len(result["highlight_lengths"]) == 4,
    ]):
        raise ValueError(f"Word structure validation failed {word}")
    pdf = PdfReader(package / "Manuscript.pdf")
    for number, page in enumerate(pdf.pages[-6:], 1):
        if f"Figure {number}." not in " ".join((page.extract_text() or "").split()):
            raise ValueError(f"Missing figure {number} page in the manuscript PDF")
    return len(result["sizes_bytes"])


def build(pandoc, output, work, browser):
    markdown = (ROOT / "paper/manuscript.md").read_text(encoding="utf-8")
    cover_letter = (ROOT / "paper/cover_letter.md").read_text(encoding="utf-8")
    audit = AUDIT.audit_manuscript(markdown, cover_letter)
    items = highlights(markdown)
    work.mkdir(parents=True, exist_ok=True)
    with TemporaryDirectory(prefix="package-", dir=work) as build_dir:
        stage = Path(build_dir)
        for variable in ("TEMP", "TMP", "TMPDIR"):
            os.environ[variable] = build_dir
        package = stage / "output"
        package.mkdir()
        FIGURES.build_submission_figures(package)
        print("Main and graphical-abstract figures exported.", flush=True)
        word_receipt = WORD.build_word(ROOT, pandoc, stage / "word", package, package)
        print(f"Word and PDF proofs built with {word_receipt['native_equations']} native equations.", flush=True)
        SUPPLEMENT.build_supplement(ROOT, package / "SupplementalInformation.pdf", str(pandoc),
                                    stage / "supplement", browser)
        (package / "Highlights.txt").write_text("\n".join(items) + "\n", encoding="utf-8", newline="\n")
        (package / "ISSUES.md").write_text(make_issues(audit, package), encoding="utf-8", newline="\n")
        (package / "CHECKLIST.md").write_text(
            make_checklist(audit, package, word_receipt, items), encoding="utf-8", newline="\n")
        count = validate_documents(audit, package)
        output.mkdir(parents=True, exist_ok=True)
        for path in package.iterdir():
            shutil.copy2(path, output / path.name)
    print(f"Built and checked {count} submission files.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pandoc", default="pandoc", help="Pandoc executable")
    parser.add_argument("--browser", help="Optional Chromium executable for the supplement")
    parser.add_argument("--out", type=Path, default=ROOT / "paper/submission")
    parser.add_argument("--work-dir", type=Path, help="Directory for temporary build data")
    args = parser.parse_args()
    output = args.out.resolve()
    work = (args.work_dir or output.parent).resolve()
    build(args.pandoc, output, work, args.browser)


if __name__ == "__main__":
    main()
