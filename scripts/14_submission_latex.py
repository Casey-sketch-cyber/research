
"""Prepare the iScience main-document source and compile the LaTeX proof."""

from __future__ import annotations

import argparse
from hashlib import sha256
import json
import os
from importlib import import_module
from pathlib import Path
import re
import subprocess
from shutil import copyfile
from zipfile import ZipFile

from pypdf import PdfReader, PdfWriter

ROOT = Path(__file__).resolve().parents[1]
AUDIT = import_module("13_submission_audit")
FUNDING_MARKER = re.compile(r"^\[AUTHOR TO FILL:.*\]\s*$", re.M)
LEAKED_EDITING_NOTES = re.compile(r"Title options|Selected by the author|Not used:|\[AUTHOR TO FILL", re.I)
SOURCE_BIB_KEY = re.compile(r"^@\w+\{\s*([a-z0-9:_-]+),", re.M)
DISCLOSURE_HEADING = "## Declaration of generative AI and AI-assisted technologies in the manuscript preparation process"
TEMPLATE_SHA256 = "d5fea9a7718bd857ae5e71753eed4a7dfc62303992656775ee15d5b2068b5dfe"
SUPERSCRIPTS = "⁰¹²³⁴⁵⁶⁷⁸⁹"
TITLE_MARKERS = str.maketrans(SUPERSCRIPTS, "0123456789")
TABLE_SUPPORT = r"""
\usepackage{array,booktabs,calc,longtable}
\usepackage{pdflscape}
\usepackage{xurl}
\newcommand{\SubmissionCite}[1]{\unskip\citep{#1}}
\providecommand{\tightlist}{\setlength{\itemsep}{0pt}\setlength{\parskip}{0pt}}
\setcounter{secnumdepth}{0}
\setcounter{Maxaffil}{0}
\setlength{\emergencystretch}{3em}
\setlength{\tabcolsep}{3pt}
\renewcommand{\arraystretch}{1.12}
"""


def extract_between(source: str, start: str, end: str) -> str:
    return source.split(f"{start}\n", 1)[1].split(f"\n{end}\n", 1)[0].strip()


def captions_and_tables(source: str) -> tuple[str, str]:
    figures = extract_between(source, "## Figure legends", "## Tables")
    tables = extract_between(source, "## Tables", "## Supplemental information")
    return figures, tables


def match_references(draft: str, bib: str) -> tuple[dict, dict]:
    """Match the approved reference strings to the committed bibliographic keys."""
    approved = extract_between(draft, "## References", "## Figure legends")
    bib_keys = SOURCE_BIB_KEY.findall(bib)
    labels, entries = {}, {}
    aliases = {"Government of the Hong Kong Special Administrative Region": "hksar",
               "Mustafa": "qaradaghi", "Özer": "ozer"}
    for line in approved.splitlines():
        if not line.strip():
            continue
        match = AUDIT.REFERENCE.match(line)
        if not match:
            raise ValueError("Found a reference entry that does not match the approved format")
        authors, year = match.groups()
        surname = authors.split(",", 1)[0]
        stem = aliases.get(surname, surname.lower())
        choices = [key for key in bib_keys if key.startswith(stem + year)]
        if len(choices) != 1:
            raise ValueError(f"Could not match {AUDIT.citation_label(authors)} {year} to a unique key")
        key = choices[0]
        labels[(AUDIT.citation_label(authors), year)] = key
        entries[key] = line.removeprefix("- ")
    return labels, entries


def number_citations(source: str, labels: dict) -> tuple[str, list[str], int]:
    """Convert recognized author–year citations and retain narrative wording."""
    longest_labels = sorted({label for label, _ in labels}, key=len, reverse=True)
    order = {}
    occurrences = 0

    def macro(keys):
        nonlocal occurrences
        occurrences += len(keys)
        for key in keys:
            order.setdefault(key, None)
        return r"\SubmissionCite{" + ",".join(keys) + "}"

    def replace(source_line):
        def group(match):
            content = match.group(1)
            if re.fullmatch(AUDIT.REF_YEAR, content):
                prefix = source_line[:match.start()].rstrip()
                for label in longest_labels:
                    if (label, content) in labels and re.search(
                        rf"(?<!\w){re.escape(label)}(?:['’]s)?$", prefix
                    ):
                        return macro([labels[label, content]])
                return match.group()

            pieces = [value.strip() for value in content.split(";")]
            recognized = [
                labels.get((part["name"], part["year"])) if (part := AUDIT.PARENTHETICAL.fullmatch(piece)) else None
                for piece in pieces
            ]
            if all(recognized):
                return macro(recognized)
            if any(recognized):
                remaining = " (" + "; ".join(piece for key, piece in zip(recognized, pieces) if key is None) + ")"
                return macro([key for key in recognized if key is not None]) + remaining
            return match.group()
        return AUDIT.BRACKET_GROUP.sub(group, source_line)

    converted = "\n".join(replace(line) for line in source.splitlines())
    unresolved = [found for line in converted.splitlines() for found in AUDIT.citations_in(line, longest_labels)]
    if unresolved:
        raise ValueError(f"Unconverted author–year citations: {sorted(set(unresolved))}")
    return converted, list(order), occurrences


def make_submission_text(draft: str) -> str:
    summary = extract_between(draft, "## Summary", "## Highlights")
    keywords = draft.split("**Keywords:** ", 1)[1].splitlines()[0]
    intro = draft.split("\n## Introduction\n", 1)[1].split("\n## Discussion\n", 1)[0].strip()
    discussion = extract_between(draft, "## Discussion", "### Limitations of the study")
    limitations = extract_between(draft, "### Limitations of the study", "## STAR Methods")
    resource_availability = extract_between(draft, "### Resource availability", "### Method details")
    resource_availability = re.sub(r"(?m)^#### ", "### ", resource_availability)
    methods = draft.split("\n### Method details\n", 1)[1].split("\n## Acknowledgments\n", 1)[0].strip()
    acknowledgments = extract_between(draft, "## Acknowledgments", "## Author contributions")
    acknowledgments = FUNDING_MARKER.sub("", acknowledgments).strip()
    contributions = extract_between(draft, "## Author contributions", "## Declaration of interests")
    interests = extract_between(draft, "## Declaration of interests", DISCLOSURE_HEADING)
    disclosure = extract_between(draft, DISCLOSURE_HEADING, "## References")
    figures, tables = captions_and_tables(draft)
    table_s4 = re.search(r"(?ms)^\*\*Table S4\..*?(?=^\|\s*Household\b)", draft)
    if table_s4 is None:
        raise ValueError("Could not locate the approved Table S4 Excel legend")
    blocks = [
        f"## Summary\n\n{summary}",
        f"## Keywords\n\n{keywords}",
        f"## Introduction\n\n{intro}",
        f"## Discussion\n\n{discussion}",
        f"## Resource Availability\n\n{resource_availability}",
        f"## Limitations of Study\n\n{limitations}",
    ]
    if acknowledgments:
        blocks.append(f"## Acknowledgments\n\n{acknowledgments}")
    blocks.extend([
        f"## Author Contributions\n\n{contributions}",
        f"## Declaration of Interests\n\n{interests}",
        f"{DISCLOSURE_HEADING}\n\n{disclosure}",
        f"## Figure Titles and Legends\n\n{figures}",
        "```{=latex}\n" + r"\clearpage\begin{landscape}\small" + "\n```"
        + f"\n\n## Tables\n\n{tables}\n\n"
        + "```{=latex}\n" + r"\normalsize\end{landscape}" + "\n```",
        f"## STAR Methods\n\n### Method details\n\n{methods}",
        f"## Supplemental Information\n\n{table_s4.group(0).strip()}",
        r"\bibliography{\SubmissionUploadPath references}",
    ])
    content = "\n\n".join(blocks) + "\n"
    if LEAKED_EDITING_NOTES.search(content):
        raise ValueError("Internal editing notes found in the main document")
    return content


def pandoc_tex(pandoc, source, *options):
    return subprocess.run(
        [str(pandoc), "--from=markdown-smart+raw_tex+autolink_bare_uris", "--to=latex", "--ascii", "--wrap=none", *options],
        input=source, encoding="utf-8", capture_output=True, check=True,
    ).stdout


def official_preamble(template_zip, output):
    if sha256(Path(template_zip).read_bytes()).hexdigest() != TEMPLATE_SHA256:
        raise ValueError("Expected the verified Cell Press LaTeX template archive")
    root = "cell-press-latex-template/"
    with ZipFile(template_zip) as archive:
        sample = archive.read(root+"article-template.tex").decode("utf-8-sig")
        for file in ("numbered.bst", "numcompress.sty"):
            (output/file).write_bytes(archive.read(root+file))
    header = sample.split("%%%  Insert title below", 1)[0].strip()
    if "version 1.10" not in header or r"\usepackage{authblk}" not in header:
        raise ValueError("The archive does not contain the expected publisher preamble")
    # XeTeX needs an OpenType Helvetica-compatible face to retain the template's sans serif.
    xetex_fonts = r"""
\ifdefined\XeTeXversion
\usepackage{fontspec}
\setsansfont[BoldFont=texgyreheros-bold.otf,ItalicFont=texgyreheros-italic.otf,BoldItalicFont=texgyreheros-bolditalic.otf]{texgyreheros-regular.otf}
\fi
"""
    header = header.replace(r"\usepackage{helvet}", r"\usepackage{helvet}" + "\n" + xetex_fonts.strip(), 1)
    # A reading copy can compile from the package root using sibling upload files.
    header = header.replace(r"\bibliographystyle{numbered}",
                            "\n" + r"\providecommand{\SubmissionUploadPath}{}" + "\n"
                            + r"\bibliographystyle{\SubmissionUploadPath numbered}", 1)
    header = "\n".join(line.rstrip() for line in header.splitlines())
    return header + "\n" + TABLE_SUPPORT.strip()


def title_commands(pandoc, draft):
    rows = [row.strip() for row in draft.split("\n## Summary\n", 1)[0].splitlines() if row.strip()]
    title = rows[0].removeprefix("# ")
    authors = rows[1].removeprefix("**Authors:** ")
    if rows[2] != "**Affiliations:**" or len(title) > 145:
        raise ValueError("The approved title-page metadata could not be parsed")
    commands = [rf"\title{{{pandoc_tex(pandoc, title).strip()}}}", r"\date{}"]
    for person in re.split(r",\s+(?:and\s+)?", authors):
        match = re.fullmatch(rf"([^,]+?)([{SUPERSCRIPTS}][{SUPERSCRIPTS},*]*)", person)
        if not match:
            raise ValueError("An author is missing the approved affiliation markers")
        name, markers = match.groups()
        commands.append(rf"\author[{markers.translate(TITLE_MARKERS)}]{{{pandoc_tex(pandoc, name).strip()}}}")
    for row in rows[3:]:
        if row[0] in SUPERSCRIPTS:
            marker, label = row[0].translate(TITLE_MARKERS), row[1:].strip()
        elif row.startswith("**Correspondence:** "):
            marker, label = "*", row.replace("**Correspondence:**", "Correspondence:", 1)
        elif row.startswith("**Keywords:** "):
            continue
        else:
            raise ValueError("Unexpected text before the Summary")
        commands.append(rf"\affil[{marker}]{{{pandoc_tex(pandoc, label).strip()}}}")
    return "\n".join(commands)


def figure_appendix(pandoc, draft):
    legends, _ = captions_and_tables(draft)
    titles = re.findall(r"(?m)^\*\*(Figure [1-6]\. .+?)\*\*$", legends)
    if len(titles) != 6:
        raise ValueError("Expected six approved figure titles for the reading copy")
    commands = [r"\ifdefined\SubmissionWithFigures"]
    for number, title in enumerate(titles, 1):
        commands.extend([
            r"\clearpage",
            r"\begin{center}",
            r"\large\bfseries " + pandoc_tex(pandoc, title).strip() + r"\par\medskip",
            rf"\includegraphics[width=\linewidth,height=.80\textheight,keepaspectratio]{{\SubmissionUploadPath Figure{number}.pdf}}",
            r"\end{center}",
        ])
    commands.append(r"\fi")
    return "\n".join(commands)


def export_tex(repo, pandoc, output, template_zip):
    """Build the manuscript on the official Cell Press preamble and numeric style."""
    output.mkdir(parents=True, exist_ok=True)
    draft = (repo/"paper/manuscript.md").read_text(encoding="utf-8-sig")
    bib = (repo/"paper/references.bib").read_text(encoding="utf-8-sig")
    body = make_submission_text(draft)
    labels, entries = match_references(draft, bib)
    body, order, occurrences = number_citations(body, labels)
    if set(order) != set(entries):
        raise ValueError(f"Main references did not all resolve: {set(entries)-set(order)}")
    if len(order) != 30:
        raise ValueError("Expected 30 approved references")
    section_body = re.sub(r"(?m)^#(?=#)","",body)
    # Map the editorial superscripts and arrows to text in the TeX engine.
    for glyph, macro in {"⇄":r"\ensuremath{\rightleftarrows}", "↑":r"\ensuremath{\uparrow}",
                         "↓":r"\ensuremath{\downarrow}", "≥":r"\ensuremath{\geq}",
                         "≤":r"\ensuremath{\leq}"}.items():
        section_body = section_body.replace(glyph, macro)
    for digit, glyph in enumerate(SUPERSCRIPTS):
        section_body = section_body.replace(glyph, rf"\textsuperscript{{{digit}}}")
    tex = "\n\n".join([
        official_preamble(template_zip, output),
        title_commands(pandoc, draft),
        r"\begin{document}", r"\maketitle", r"\clearpage",
        pandoc_tex(pandoc, section_body).strip(),
        figure_appendix(pandoc, draft), r"\end{document}",
    ]) + "\n"
    (output/"Manuscript.tex").write_text(tex,encoding="utf-8",newline="\n")
    (output/"references.bib").write_text(bib,encoding="utf-8",newline="\n")
    return {"bibliography_entries":len(order), "citations":occurrences, "ordered_keys":order}


def compile_pdf(source, output, cwd, tectonic, work, pdf_title):
    """Compile TeX with Tectonic and save a PDF with neutral metadata."""
    work.mkdir(parents=True, exist_ok=True)
    env = os.environ | {name:str(work) for name in ("TEMP","TMP","TMPDIR")}
    env.setdefault("TECTONIC_CACHE_DIR",str(work/"tex-cache"))
    subprocess.run(
        [str(tectonic), "-X", "compile", "--keep-logs", "--keep-intermediates",
         "--outdir", str(work), str(source.relative_to(cwd))],
        cwd=cwd, env=env, check=True,
    )
    log = (work/f"{source.stem}.log").read_text(encoding="utf-8",errors="replace")
    if re.search(r"undefined citations|Citation .+ undefined|Missing character:|There were undefined references",log):
        raise ValueError("LaTeX logged a missing glyph, citation, or reference")
    raw = PdfReader(work/f"{source.stem}.pdf")
    writer = PdfWriter(clone_from=raw)
    writer.metadata = None
    writer.root_object.pop("/Metadata",None)
    writer.add_metadata({"/Title":pdf_title,"/Producer":"Tectonic / XeTeX"})
    with output.open("wb") as file:
        writer.write(file)
    return len(raw.pages)


def build_pdf(tex_dir, tectonic, work):
    pages = compile_pdf(tex_dir/"Manuscript.tex",tex_dir/"Manuscript.pdf",tex_dir,tectonic,work,"Manuscript")
    copyfile(work/"Manuscript.bbl", tex_dir/"Manuscript.bbl")
    return pages


def build_reading_pdf(tex_dir, review_dir, tectonic, work):
    package = tex_dir.parent
    if review_dir.parent != package or tex_dir.name != "upload":
        raise ValueError("The LaTeX reading copy requires sibling upload and review directories")
    review_dir.mkdir(parents=True, exist_ok=True)
    source = package/"Manuscript_LaTeX_with_figures.tex"
    source.write_text(
        "\\def\\SubmissionWithFigures{1}\n"
        "\\def\\SubmissionUploadPath{upload/}\n"
        "\\input{upload/Manuscript.tex}\n",
        encoding="utf-8",newline="\n",
    )
    return compile_pdf(source, review_dir/(source.stem + ".pdf"), package, tectonic, work, "Manuscript with figures")


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pandoc",default="pandoc")
    parser.add_argument("--tectonic",default="tectonic")
    parser.add_argument("--template",type=Path,required=True,help="Verified Cell Press LaTeX template ZIP")
    parser.add_argument("--out",type=Path,required=True)
    parser.add_argument("--work-dir",type=Path,required=True)
    parser.add_argument("--review-dir",type=Path,help="Optional sibling review directory for a LaTeX proof with Figures 1–6")
    args=parser.parse_args()
    output, work=args.out.resolve(), args.work_dir.resolve()
    result=export_tex(ROOT,args.pandoc,output,args.template)
    result["pages"]=build_pdf(output,args.tectonic,work)
    if args.review_dir:
        result["reading_pages"]=build_reading_pdf(output,args.review_dir.resolve(),args.tectonic,work)
    print(json.dumps(result,indent=2))


if __name__=="__main__":
    main()
