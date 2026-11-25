"""Build the approved Buildings manuscript with the official MDPI ACS template."""

import argparse
from hashlib import sha256
import io
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
from zipfile import ZipFile

from pypdf import PdfReader, PdfWriter
from pypdf.generic import DecodedStreamObject, DictionaryObject, NameObject


TEMPLATE_HASH = "f6d5ae546a3d246bd73ee1dbaefc60a8b7398496ef7cfc8e10b7cc83d26067b7"
CITE = re.compile(r"\\cite[pt]\{([^{}]+)\}")
BACK = {
    "Supplementary Materials": "supplementary",
    "Author Contributions": "authorcontributions",
    "Funding": "funding",
    "Institutional Review Board Statement": "institutionalreview",
    "Informed Consent Statement": "informedconsent",
    "Data Availability Statement": "dataavailability",
    "Acknowledgments": "acknowledgments",
    "Conflicts of Interest": "conflictsofinterest",
}


def pandoc_latex(pandoc, source):
    latex = subprocess.run(
        [str(pandoc), "-f", "markdown-smart+raw_tex+autolink_bare_uris", "-t", "latex",
         "--natbib", "--ascii", "--wrap=none", "--columns=150"],
        input=source, encoding="utf-8", stdout=subprocess.PIPE, check=True,
    ).stdout.strip()
    symbols = {"⇄":r"\rightleftarrows", "↑":r"\uparrow", "↓":r"\downarrow",
               "≥":r"\geq", "≤":r"\leq", "±":r"\pm"}
    return re.sub("[" + "".join(symbols) + "]", lambda m:r"\ensuremath{" + symbols[m[0]] + "}", latex)


def title_parts(source):
    front, split, body = source.partition("\n## 1. Introduction\n")
    if not split:
        raise ValueError("The approved first section was not found")
    fields = dict(re.findall(r"(?m)^\*\*(Abstract|Keywords):\*\* (.+)$", front))
    authors = re.search(r"(?m)^\*\*Authors:\*\* (.+)$", front)[1]
    affiliations = re.findall(r"(?m)^([¹²³]) (.+)$", front)
    correspondence = re.search(r"(?m)^\\\* Correspondence: (.+)$", front)[1]
    if len(affiliations) != 3:
        raise ValueError("Expected three approved affiliations")
    return front.splitlines()[0].removeprefix("# "), authors, affiliations, correspondence, fields, split + body


def logo_pdf(template, output):
    # The publisher's compiled sample contains the exact EPS logo as a vector form.
    reader = PdfReader(io.BytesIO(template.read("template.pdf")))
    vector = reader.pages[0]["/Resources"]["/XObject"]["/Im1"]
    if list(vector["/BBox"]) != [0, 0, 74, 49]:
        raise ValueError("The official sample logo has changed")
    writer = PdfWriter()
    page = writer.add_blank_page(width=74, height=49)
    page[NameObject("/Resources")] = DictionaryObject({
        NameObject("/XObject"): DictionaryObject({
            NameObject("/SubmissionLogo"): vector.clone(writer).indirect_reference,
        }),
    })
    content = DecodedStreamObject()
    content.set_data(b"q /SubmissionLogo Do Q")
    page[NameObject("/Contents")] = writer._add_object(content)
    with output.open("wb") as file:
        writer.write(file)


def unpack_template(template_file, destination):
    if sha256(template_file.read_bytes()).hexdigest() != TEMPLATE_HASH:
        raise ValueError("Expected the verified MDPI ACS template release of 12 November 2026")
    with ZipFile(template_file) as template:
        for member in ("mdpi.cls", "mdpi.bst", "journalnames.tex", "unicode.tex",
                       "logo-mdpi.eps", "logo-orcid.pdf", "logo-updates.eps"):
            path = destination / "Definitions" / member
            path.parent.mkdir(exist_ok=True)
            path.write_bytes(template.read("Definitions/" + member))
        logo_pdf(template, destination/"Definitions/logo-mdpi.pdf")
        sample = template.read("template.tex").decode("utf-8-sig")
    preamble = sample[sample.index("\\firstpage{1}"):sample.index("% Add packages and commands here.")]
    return "\n".join(line.rstrip() for line in preamble.splitlines() if not line.lstrip().startswith("%")).strip()


def compile_body(pandoc, body):
    body = latex_ready_markdown(body)
    latex = pandoc_latex(pandoc, body)
    # Pandoc keeps each raw marker on a separate paragraph.
    for count in range(1, 7):
        rex = rf"BUILDINGSFIGURE{count}START\s*\n+(?P<caption>.*?)\n+BUILDINGSFIGURE{count}END"
        def insert_figure(match):
            return "\n".join((
                r"\begin{figure}[H]", r"\begin{adjustwidth}{-\extralength}{0cm}", r"\centering",
                rf"\includegraphics[width=\linewidth,height=0.65\textheight,keepaspectratio]{{figures/Figure{count}.pdf}}",
                r"\caption{" + match["caption"].strip() + "}", r"\end{adjustwidth}", r"\end{figure}",
            ))
        latex, changed = re.subn(rex, insert_figure, latex, flags=re.S)
        if changed != 1:
            raise ValueError(f"Expected one Figure {count} caption")
    table_widths = (
        (5, 15, 10, 9, 8, 8, 18, 27),
        (16, 7, 11, 7, 12, 16, 31),
        (12, 6, 6, 6, 9, 9, 6, 10, 6, 9, 10, 11),
        (15, 7, 19, 10, 7, 7, 7, 7, 7, 14),
    )
    for count, widths in enumerate(table_widths, 1):
        rex = (
            rf"BUILDINGSTABLE{count}START\s*\n+(?P<caption>.*?)\n+BUILDINGSTABLE{count}END\s*\n+"
            r"\{\\def\\LTcaptype\{none\}[^\n]*\n\\begin\{longtable\}.*?"
            r"(?P<head>\\toprule.*?)(?:\\endhead)(?P<rows>.*?)\\end\{longtable\}\n\}"
        )
        def insert_table(match):
            caption = match["caption"].strip()
            extra = 2 * (len(widths) - 1)
            columns = "".join(
                r">{\raggedright\arraybackslash}p{"
                rf"(\linewidth-{extra}\tabcolsep)*\real{{{value/sum(widths):.7f}}}" + "}"
                for value in widths
            )
            return "\n".join((
                r"\begin{landscape}", r"\begingroup\fontsize{8.5}{10.5}\selectfont",
                r"\setlength{\tabcolsep}{2.5pt}", r"\setlength{\LTcapwidth}{\linewidth}",
                r"\begin{longtable}{@{}" + columns + r"@{}}",
                r"\caption{" + caption + r"}\\", match["head"] + r"\endfirsthead",
                match["head"] + r"\endhead", match["rows"],
                r"\end{longtable}", r"\endgroup", r"\end{landscape}",
            ))
        latex, changed = re.subn(rex, insert_table, latex, flags=re.S)
        if changed != 1:
            raise ValueError(f"Expected one longtable for Table {count}")
    if len(re.findall("BUILDINGS(?:FIGURE|TABLE)", latex)):
        raise ValueError("Unconverted figure/table markup")
    for key, macro in BACK.items():
        pattern = re.escape(r"\textbf{" + key + ":}") + r" (.*?)(?=\n\n|$)"
        latex, count = re.subn(pattern, lambda m: "\\" + macro + "{" + m[1] + "}", latex, count=1, flags=re.S)
        if count != 1:
            raise ValueError(f"Missing approved back-matter entry {key}")
    return latex


def latex_ready_markdown(body):
    body = body.split("\n## References\n", 1)[0]
    body = re.sub(r"(?m)^(#{2,3}) \d+(?:\.\d+)?\. ", lambda m: m[1][1:] + " ", body)
    body = re.sub(r"(?m)^---\s*$", "", body)
    return re.sub(r"(?m)^\*\*(Figure|Table) ([1-6])\.\*\* (.+)$",
                  lambda m: f"BUILDINGS{m[1].upper()}{m[2]}START\n\n{m[3]}\n\nBUILDINGS{m[1].upper()}{m[2]}END",
                  body)


def make_tex(args, stage):
    source = (args.repo/"paper/buildings/manuscript.md").read_text(encoding="utf-8-sig")
    title, authors, addresses, correspondence, fields, body = title_parts(source)
    words = dict(zip(("title", "Abstract", "Keywords"), pandoc_latex(
        args.pandoc, "\n\n".join([title, fields["Abstract"], fields["Keywords"]])
    ).split("\n\n"), strict=True))
    author_names = re.sub(r" [¹²³](?:,\*)?", "", authors)
    author_tex = re.sub(r" ([¹²³])(?:,(\*))?", lambda m: r"\textsuperscript{" + str("¹²³".index(m[1])+1) + (",*" if m[2] else "") + "}", authors)
    address = ("\\\\\n").join(
        rf"\textsuperscript{{{index}}} \quad {row}" for index, (_, row) in enumerate(addresses, 1)
    )
    preamble = unpack_template(args.template, stage)
    body_tex = compile_body(args.pandoc, body)
    packages = r"""
\usepackage{longtable}
\usepackage{pdflscape}
\usepackage{xurl}
\ifdefined\XeTeXversion
\usepackage{newunicodechar}
\newunicodechar{−}{\ensuremath{-}}
\newunicodechar{’}{\textquoteright}
\newunicodechar{‘}{\textquoteleft}
\newunicodechar{–}{\textendash}
\fi
\providecommand{\tightlist}{\setlength{\itemsep}{0pt}\setlength{\parskip}{0pt}}
\providecommand{\pandocbounded}[1]{#1}
\setlength{\headheight}{18.5pt}
\setlength{\emergencystretch}{3em}
% Use the official vector logo in PDF form for both PDF and XeTeX engines.
\makeatletter
\patchcmd{\@maketitle}{Definitions/logo-mdpi.eps}{Definitions/logo-mdpi.pdf}{}{\PackageError{buildings-build}{MDPI title logo hook changed}{}}
\makeatother
"""
    parts = [
        r"\documentclass[buildings,article,submit,moreauthors]{Definitions/mdpi}", packages, preamble,
        r"\Title{" + words["title"] + "}", r"\Author{" + author_tex + "}",
        r"\AuthorNames{" + author_names + "}", r"\address{" + address + "}",
        r"\corres{Correspondence: " + correspondence + "}",
        r"\abstract{" + words["Abstract"] + "}", r"\keyword{" + words["Keywords"] + "}",
        r"\begin{document}", body_tex, r"\reftitle{References}", r"\bibliography{references}", r"\end{document}",
    ]
    manuscript = "\n\n".join(parts).replace("²", r"\textsuperscript{2}")
    (stage/"manuscript.tex").write_text(manuscript + "\n", encoding="utf-8", newline="\n")
    shutil.copyfile(args.repo/"paper/references.bib", stage/"references.bib")
    first_keys = list(dict.fromkeys(key.strip() for group in CITE.findall(body_tex) for key in group.split(",")))
    source_keys = list(dict.fromkeys(re.findall(r"@([a-z][a-z0-9]+[0-9]{4}[a-z0-9]+)", body)))
    if first_keys != source_keys or len(first_keys) != 30:
        raise ValueError(f"Converted citation order differs from the 30 approved keys: {first_keys}")
    return first_keys


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", required=True, type=Path)
    parser.add_argument("--template", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--scratch", required=True, type=Path)
    parser.add_argument("--pandoc", required=True, type=Path)
    parser.add_argument("--tectonic", required=True, type=Path)
    args = parser.parse_args()
    args.repo = args.repo.resolve()
    stage = args.out.resolve()
    args.scratch = args.scratch.resolve()
    stage.mkdir(parents=True, exist_ok=True)
    args.scratch.mkdir(parents=True, exist_ok=True)
    fig_dir = stage/"figures"
    fig_dir.mkdir(exist_ok=True)
    for number in range(1, 7):
        name = f"Figure{number}.pdf"
        shutil.copyfile(args.repo/"paper/submission-v2/upload"/name, fig_dir/name)
    expected = make_tex(args, stage)
    env = os.environ | {name:str(args.scratch) for name in ("TEMP", "TMP", "TMPDIR")}
    subprocess.run([str(args.tectonic.resolve()), "-X", "compile", "--keep-logs", "--keep-intermediates",
                    "manuscript.tex"], cwd=stage, env=env, check=True)
    files = stage/"manuscript.bbl"
    refs = re.findall(r"\\bibitem(?:\[[^\]]*\])?\{([^{}]+)\}", files.read_text(encoding="utf-8"))
    if refs != expected:
        raise ValueError(f"MDPI BibTeX output has an unexpected first-citation order: {refs}")
    pdf = PdfReader(stage/"manuscript.pdf")
    text = " ".join(page.extract_text() for page in pdf.pages)
    if re.search(r"\[NEEDS|\[CITE|\[@[a-z]|paper/references\.bib|BUILDINGS(?:FIGURE|TABLE)", text, re.I):
        raise ValueError("The rendered PDF contains unresolved source markers")
    log = (stage/"manuscript.log").read_text(encoding="utf-8", errors="replace")
    if re.search(r"Missing character:|Citation .+ undefined|There were undefined (?:citations|references)", log):
        raise ValueError("LaTeX reported a missing glyph or unresolved citation/reference")
    print(json.dumps({"pages":len(pdf.pages), "reference_keys":refs}, indent=2))


if __name__ == "__main__":
    main()
