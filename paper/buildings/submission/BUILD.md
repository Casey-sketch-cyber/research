# Build the Buildings submission package

The approved Stage 2b input is commit `c10053e` on main, which includes Claude's edits to the numbers-trim revision. Run the commands from the repository root. Use Pandoc 3.14, Tectonic 0.17, Python 3.12, pypdf, pypdfium2, Pillow and python-docx. The Word proof was paginated with Microsoft Word.

1. Download the MDPI ACS archive linked in the journal instructions. The build expects the 12 November 2026 archive, SHA-256 `f6d5ae546a3d246bd73ee1dbaefc60a8b7398496ef7cfc8e10b7cc83d26067b7`. Download the official Buildings Word template. [MDPI LaTeX archive](https://res.mdpi.com/data/MDPI_template_ACS.zip?v=20261112) · [Buildings Word template](https://mdpi-res.com/files/word-templates/buildings-template.dot)
2. Set `TEMP`, `TMP`, `TMPDIR` and `TECTONIC_CACHE_DIR` to directories in the scratch area. Use a separate output directory for the journal-format build.

```text
python scripts/15_submission_artwork.py --repo . --out OFFICIAL --work-dir SCRATCH --pandoc PANDOC
python scripts/15_build_buildings.py --repo . --template MDPI_ACS.zip --out OFFICIAL --scratch SCRATCH --pandoc PANDOC --tectonic TECTONIC
python scripts/15_build_buildings_word.py --repo . --template buildings-template.dot --bbl OFFICIAL/manuscript.bbl --figure-dir OFFICIAL/figures --pandoc PANDOC --work-dir SCRATCH --out OFFICIAL
```

The LaTeX command uses the official `buildings,article,submit,moreauthors` class and ACS bibliography style. The rendering bridge uses the vector from the publisher's compiled sample in place of the supplied EPS during XeTeX compilation. The original class and style are preserved. The supplementary build renders the approved legend and table text with the existing vector figure plates.

3. For public review, render the same approved text, equations, tables and figures using standard Word styles and the numbered references from the verified BibTeX build. The journal reserves its templates for submission. [Buildings instructions for authors](https://www.mdpi.com/journal/buildings/instructions)

```text
python scripts/15_submission_artwork.py --repo . --out REVIEW --work-dir SCRATCH --pandoc PANDOC
python scripts/15_build_buildings_word.py --repo . --review-copy --bbl OFFICIAL/manuscript.bbl --figure-dir OFFICIAL/figures --pandoc PANDOC --work-dir SCRATCH --out REVIEW
```

The local distribution includes `LaTeX_Source.zip` with the manuscript, BibTeX and its dependencies. Unzip it and compile `manuscript.tex` from its root. The cover letter, supplementary PDF, editable Table S4 and optional graphical abstract accompany either the LaTeX or Word submission route. See the [format audit](CHECKLIST.md) and [review decisions](ISSUES.md).
