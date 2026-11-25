# Build the Buildings submission package

The approved input is commit `3a1e040` on main, including the author-selected title. Run these commands from the repository root, using an output directory and scratch space on D:. Use Pandoc 3.14, Tectonic 0.17, Python 3.12, pypdf, pypdfium2, Pillow and python-docx. The Word proof was paginated with Microsoft Word.

1. Download the MDPI ACS archive linked in the journal instructions. The build expects the 12 November 2026 archive, SHA-256 `f6d5ae546a3d246bd73ee1dbaefc60a8b7398496ef7cfc8e10b7cc83d26067b7`. Download the official Buildings Word template. [MDPI LaTeX archive](https://res.mdpi.com/data/MDPI_template_ACS.zip?v=20261112) · [Buildings Word template](https://mdpi-res.com/files/word-templates/buildings-template.dot)
2. Set `TEMP`, `TMP`, `TMPDIR` and `TECTONIC_CACHE_DIR` to directories in the scratch area. Generate the artwork and compiled documents.

```text
python scripts/15_submission_artwork.py --repo . --out OUT --work-dir SCRATCH --pandoc PANDOC
python scripts/15_build_buildings.py --repo . --template MDPI_ACS.zip --out OUT --scratch SCRATCH --pandoc PANDOC --tectonic TECTONIC
python scripts/15_build_buildings_word.py --repo . --template buildings-template.dot --bbl OUT/manuscript.bbl --figure-dir OUT/figures --pandoc PANDOC --work-dir SCRATCH --out OUT
```

The LaTeX command uses the official `buildings,article,submit,moreauthors` class and ACS bibliography style. The rendering bridge uses the vector from the publisher's compiled sample in place of the supplied EPS during XeTeX compilation. The original class and style are preserved. The supplementary build renders the approved legend and table text with the existing vector figure plates.

The local distribution includes `LaTeX_Source.zip` with the manuscript, BibTeX and all dependencies necessary to recompile it. Unzip it and compile `manuscript.tex` from its root. For submission, use either that source archive with the compiled manuscript PDF or the editable main Word manuscript. The cover letter, supplementary PDF, editable Table S4 and optional graphical abstract accompany either route. See the [format audit](CHECKLIST.md) and [author review items](ISSUES.md).
