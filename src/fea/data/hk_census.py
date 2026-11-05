"""Read the bilingual D6 table while keeping codes separate from numeric counts."""
from __future__ import annotations

import csv
import io
import zipfile
from pathlib import Path

import pandas as pd


def census_table(path: Path) -> tuple[pd.DataFrame, dict[str, str], list[list[str]]]:
    """Return data rows, the supplied English field dictionary and source footnotes."""
    with zipfile.ZipFile(path) as archive:
        members = [n for n in archive.namelist() if n.lower().endswith(".csv")]
        if len(members) != 1:
            raise ValueError("Expected a single census CSV")
        rows = list(csv.reader(io.StringIO(archive.read(members[0]).decode("utf-8-sig"))))
    english, fields = rows[1], rows[2]
    data, notes = [], []
    for row in rows[3:]:
        if len(row) == len(fields) and row[1].strip().isdigit():
            data.append(row)
        else:
            notes.append(row)
    table = pd.DataFrame(data, columns=fields)
    for field in ("sdu_pop", "sdu_dh", "sdu_oq", "sdu_n"):
        table[field] = pd.to_numeric(table[field].str.replace(",", "", regex=False), errors="raise")
    return table, dict(zip(fields, english)), notes
