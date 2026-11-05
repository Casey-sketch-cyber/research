"""Reject executable pickle globals, archive path traversal and incorrect unit conversion."""
import io
import pickle
import zipfile

import pytest

from fea.data.abo import dimensions_m
from fea.data.archives import extract_named, read_geometry_pickle


def test_restricted_pickle_rejects_code_globals():
    with pytest.raises(pickle.UnpicklingError):
        read_geometry_pickle(io.BytesIO(b"cos\nsystem\n."))


def test_extraction_uses_explicit_destination(tmp_path):
    archive = tmp_path / "fixture.zip"
    with zipfile.ZipFile(archive, "w") as stream:
        stream.writestr("../../escape.txt", "safe fixture")
    destination = tmp_path / "contained" / "output.txt"
    extract_named(archive, "escape.txt", destination)
    assert destination.read_text() == "safe fixture"
    assert not (tmp_path / "escape.txt").exists()
    destination.write_text("bad  fixture")
    extract_named(archive, "escape.txt", destination)
    assert destination.read_text() == "safe fixture"


def test_mixed_units_and_missing_dimensions():
    item = {"item_dimensions": {"width": {"value": 100, "unit": "centimeters"},
                                "length": {"value": 20, "unit": "inches"},
                                "height": {"value": 800, "unit": "millimeters"}}}
    assert dimensions_m(item) == pytest.approx({"width": 1.0, "depth": 0.508, "height": 0.8})
    item["item_dimensions"]["width"]["unit"] = "unspecified"
    assert dimensions_m(item) is None
