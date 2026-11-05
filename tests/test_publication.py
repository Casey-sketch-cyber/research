"""Publishing must reject private transport details while preserving research context."""
import importlib.util
from pathlib import Path

spec = importlib.util.spec_from_file_location("publication", Path(__file__).parents[1] / "scripts/check_publication.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def test_rejects_operational_details_without_echoing_them():
    private_path = "D:" + "/PROJECT/" + "private-run"
    endpoint = "root" + "@" + "host.example"
    assert "private_absolute_path" in module.inspect_text(private_path, [])
    assert "ssh_endpoint" in module.inspect_text(endpoint, [])
    assert module.inspect_text("sensitive-value", ["sensitive-value"]) == ["explicit_private_term"]


def test_allows_research_provenance():
    assert module.inspect_text("Swiss Dwellings; Hong Kong; doi:10.5281/zenodo.7788422; 0.60 m", []) == []
    assert module.inspect_text("0.1543218 abc54321def", ["54321"]) == []
    assert module.inspect_text("port: 54321", ["54321"]) == ["explicit_private_term"]


def test_doi_numeric_suffix_is_not_a_network_address():
    assert module.inspect_text("doi:10.1182/blood.v104.11.994.994", []) == []
    documentation_address = ".".join(map(str, (192, 0, 2, 1)))
    assert "ipv4_address" in module.inspect_text(documentation_address, [])
    assert "explicit_private_term" in module.inspect_text("104.11.994.994", ["104.11.994.994"])
