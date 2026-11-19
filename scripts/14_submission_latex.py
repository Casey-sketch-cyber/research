
"""Prepare the iScience main-document source and compile the LaTeX proof."""

from __future__ import annotations

import argparse
import json
import os
from importlib import import_module
from pathlib import Path
import re
import subprocess

from pypdf import PdfReader, PdfWriter

ROOT = Path(__file__).resolve().parents[1]
AUDIT = import_module("13_submission_audit")
FUNDING_MARKER = re.compile(r"^\[AUTHOR TO FILL:.*\]\s*$", re.M)
LEAKED_EDITING_NOTES = re.compile(r"Title options|Selected by the author|Not used:|\[AUTHOR TO FILL", re.I)
SOURCE_BIB_KEY = re.compile(r"^@\w+\{\s*([a-z0-9:_-]+),", re.M)
DISCLOSURE = (
    "During preparation of this manuscript, Gemini and Claude assisted with drafting and editing, "
    "and OpenAI Codex assisted with formatting and preparation of submission files."
)
HEADER = r"""
\usepackage{pdflscape}
\usepackage{setspace}
\usepackage{lineno}
\usepackage[numbers,super,sort&compress]{natbib}
\newcommand{\SubmissionCite}[1]{\unskip\citep{#1}}
\AtBeginDocument{\onehalfspacing\linenumbers}
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


def make_submission_text(draft: str) -> tuple[str, str]:
    front = draft.split("\n## Summary\n", 1)[0].strip()
    title, authors = front.split("\n", 1)
    title = title.removeprefix("# ").strip()
    authors = re.sub(r"(?m)^\*\*Keywords:\*\*[^\n]*\n?", "", authors).strip()
    summary = extract_between(draft, "## Summary", "## Highlights")
    intro = draft.split("\n## Introduction\n", 1)[1].split("\n## Discussion\n", 1)[0].strip()
    discussion = extract_between(draft, "## Discussion", "### Limitations of the study")
    limitations = extract_between(draft, "### Limitations of the study", "## STAR Methods")
    resource_availability = extract_between(draft, "### Resource availability", "### Method details")
    resource_availability = re.sub(r"(?m)^#### ", "### ", resource_availability)
    methods = draft.split("\n### Method details\n", 1)[1].split("\n## Acknowledgments\n", 1)[0].strip()
    acknowledgments = extract_between(draft, "## Acknowledgments", "## Author contributions")
    acknowledgments = FUNDING_MARKER.sub("", acknowledgments).strip()
    contributions = extract_between(draft, "## Author contributions", "## Declaration of interests")
    interests = extract_between(draft, "## Declaration of interests", "## References")
    figures, tables = captions_and_tables(draft)
    table_s4 = re.search(r"(?ms)^\*\*Table S4\..*?(?=^\|\s*Household\b)", draft)
    if table_s4 is None:
        raise ValueError("Could not locate the approved Table S4 Excel legend")
    blocks = [
        authors.strip(), r"\clearpage",
        f"## Summary\n\n{summary}",
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
        "## Declaration of generative AI and AI-assisted technologies in the manuscript preparation process\n\n"
        + DISCLOSURE,
        f"## Figure Titles and Legends\n\n{figures}",
        "```{=latex}\n" + r"\clearpage\begin{landscape}\small" + "\n```"
        + f"\n\n## Tables\n\n{tables}\n\n"
        + "```{=latex}\n" + r"\normalsize\end{landscape}" + "\n```",
        f"## STAR Methods\n\n### Method details\n\n{methods}",
        f"## Supplemental Information\n\n{table_s4.group(0).strip()}",
        r"\input{Manuscript.bbl}",
    ])
    content = "\n\n".join(blocks) + "\n"
    if LEAKED_EDITING_NOTES.search(content):
        raise ValueError("Internal editing notes found in the main document")
    return title, content


def pandoc_tex(pandoc, source, *options):
    return subprocess.run(
        [str(pandoc), "--from=markdown-smart+raw_tex", "--to=latex", "--wrap=none", *options],
        input=source, encoding="utf-8", capture_output=True, check=True,
    ).stdout


def export_tex(repo, pandoc, output):
    """Export one main TeX file plus the exact reviewed reference strings."""
    output.mkdir(parents=True, exist_ok=True)
    draft = (repo/"paper/manuscript.md").read_text(encoding="utf-8-sig")
    bib = (repo/"paper/references.bib").read_text(encoding="utf-8-sig")
    title, body = make_submission_text(draft)
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
    for digit, glyph in enumerate("⁰¹²³⁴⁵⁶⁷⁸⁹"):
        section_body = section_body.replace(glyph, rf"\textsuperscript{{{digit}}}")
    header = output/"submission-header.tex"
    header.write_text(HEADER.lstrip(), encoding="utf-8", newline="\n")
    tex = pandoc_tex(
        pandoc, section_body, "--standalone", f"--metadata=title:{title}", "--variable=fontsize:11pt",
        "--variable=geometry:letterpaper,margin=0.82in", f"--include-in-header={header}",
    )
    # The header is embedded by Pandoc; the main TeX file only needs the companion bibliography output.
    (output/"Manuscript.tex").write_text(tex,encoding="utf-8",newline="\n")
    header.unlink()
    bibliography = [r"\begin{thebibliography}{99}"]
    for key in order:
        bibliography.extend([rf"\bibitem{{{key}}}", pandoc_tex(pandoc, entries[key]).strip(), ""])
    bibliography.append(r"\end{thebibliography}")
    (output/"Manuscript.bbl").write_text("\n".join(bibliography)+"\n",encoding="utf-8",newline="\n")
    (output/"references.bib").write_text(bib,encoding="utf-8",newline="\n")
    return {"bibliography_entries":len(order), "citations":occurrences, "ordered_keys":order}


def build_pdf(tex_dir, tectonic, work):
    """Run the XeTeX-based Tectonic engine and retain the compiler diagnostic log in the build directory."""
    work.mkdir(parents=True, exist_ok=True)
    env = os.environ | {name:str(work) for name in ("TEMP","TMP","TMPDIR")}
    env.setdefault("TECTONIC_CACHE_DIR",str(work/"tex-cache"))
    subprocess.run(
        [str(tectonic), "-X", "compile", "--keep-logs", "--keep-intermediates",
         "--outdir", str(work), "Manuscript.tex"],
        cwd=tex_dir, env=env, check=True,
    )
    log = (work/"Manuscript.log").read_text(encoding="utf-8",errors="replace")
    if re.search(r"undefined citations|Citation .+ undefined|Missing character:|There were undefined references",log):
        raise ValueError("LaTeX logged a missing glyph, citation, or reference")
    raw = PdfReader(work/"Manuscript.pdf")
    writer = PdfWriter(clone_from=raw)
    writer.metadata = None
    writer.root_object.pop("/Metadata",None)
    writer.add_metadata({"/Title":"Manuscript","/Producer":"Tectonic / XeTeX"})
    with (tex_dir/"Manuscript.pdf").open("wb") as file:
        writer.write(file)
    return len(raw.pages)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pandoc",default="pandoc")
    parser.add_argument("--tectonic",default="tectonic")
    parser.add_argument("--out",type=Path,required=True)
    parser.add_argument("--work-dir",type=Path,required=True)
    args=parser.parse_args()
    output, work=args.out.resolve(), args.work_dir.resolve()
    result=export_tex(ROOT,args.pandoc,output)
    result["pages"]=build_pdf(output,args.tectonic,work)
    print(json.dumps(result,indent=2))


if __name__=="__main__":
    main()
