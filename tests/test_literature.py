"""Query fidelity and bibliographic identity merging."""
from fea.literature import deduplicate, inverted_abstract, parse_arxiv, translated_query
from fea.literature_report import screening_rows
import pytest


def test_boolean_translation_preserves_phrases_and_grouping():
    query = '(transformable OR "wall bed") AND furniture'
    assert translated_query(query, "semantic_scholar") == '( transformable | "wall bed" ) + furniture'
    assert translated_query(query, "arxiv") == '( all:transformable OR all:"wall bed" ) AND all:furniture'
    assert inverted_abstract({"A": [0, 2], "room": [1]}) == "A room A"


def test_deduplication_retains_source_union_and_missing_metadata():
    def row(source, title, doi, year, query):
        return dict(source=source, source_id=source+query, title=title, doi=doi, year=year,
                    venue="", type="", authors=[], url="", query_id=query, cited_by=0,
                    abstract="", oa_url="", evidence_url="https://example.invalid/")
    records = [row("openalex", "A dwelling: layout", "10.test/a", 2020, "Q1"),
               row("crossref", "A dwelling layout", "10.test/a", 2021, "Q2"),
               row("arxiv", "A dwelling layout", "", 2021, "Q3"),
               row("arxiv", "Different study", "", 2021, "Q1")]
    result = deduplicate(records)
    assert len(result) == 2
    merged = next(r for r in result if r["doi"])
    assert merged["sources"] == ["arxiv", "crossref", "openalex"]
    assert merged["query_ids"] == ["Q1", "Q2", "Q3"]
    assert merged["year_variants"] == [2020, 2021]
    assert merged["abstracts"] == [] and merged["venue"] == ""


def test_arxiv_feed_preserves_supplied_bibliographic_values():
    total, records = parse_arxiv('''<feed xmlns="http://www.w3.org/2005/Atom" xmlns:o="http://a9.com/-/spec/opensearch/1.1/" xmlns:x="http://arxiv.org/schemas/atom"><o:totalResults>1</o:totalResults><entry><id>https://arxiv.org/abs/0000.00000</id><title>A test title</title><published>2020-01-01T00:00:00Z</published><summary>Original abstract.</summary><author><name>A Researcher</name></author><x:doi>10.test/ABC</x:doi></entry></feed>''')
    assert total == 1 and records[0]["doi"] == "10.test/abc"
    assert records[0]["authors"] == ["A Researcher"]
    assert records[0]["abstract"] == "Original abstract."


def test_unreviewed_records_are_pending_not_negative():
    records = [dict(rec_id="r1", doi="10.test/a", title="A", year=2020, venue="V",
                    evidence=[], abstracts=["Supplied evidence."]),
               dict(rec_id="r2", doi="", title="B", year=2021, venue="", evidence=[], abstracts=[])]
    decisions = {"10.test/a": dict(stage1="KEEP", stage2="A_overlap", claim_affected="C3",
                                    note="Analytical area comparison.", fulltext_checked=True, abstract_read=True)}
    rows = screening_rows(records, decisions)
    assert rows[0]["stage2"] == "A_overlap"
    assert rows[1]["stage2"] == "PENDING" and not rows[1]["abstract_read"]
    with pytest.raises(ValueError, match="unavailable"):
        screening_rows([dict(records[0], abstracts=[])], decisions)


def test_failed_retry_does_not_erase_successful_query_evidence(tmp_path):
    import json
    from urllib.parse import urlencode
    from fea.literature import collect_cached_queries
    config = dict(years=[2000, 2026], max_records_per_query_per_source=500,
                  sources={"crossref": {}}, queries={"Q1": {"boolean": "furniture", "keywords": "furniture"}})
    base = dict(source="crossref", query_id="Q1", retrieved_at="2026-11-05", attempts=[])
    directory = tmp_path / "crossref"
    directory.mkdir()
    url = "https://api.crossref.org/works?" + urlencode({"query.bibliographic": "furniture", "filter": "from-pub-date:2000-01-01,until-pub-date:2026-12-31"})
    good = dict(base, url=url, status=200, body=json.dumps({"message": {"total-results": 1, "items": [{"DOI": "10.test/a", "title": ["A"], "published": {"date-parts": [[2020]]}}]}}))
    bad = dict(base, url=url+"&offset=1", status=429, body='{"error":"limited"}')
    (directory / "good.json").write_text(json.dumps(good), encoding="utf8")
    (directory / "bad.json").write_text(json.dumps(bad), encoding="utf8")
    rows, queries, manifest = collect_cached_queries(config, tmp_path)
    assert len(rows) == 1 and queries[0]["retrieved"] == 1
    assert queries[0]["error"] == "" and queries[0]["historical_errors"] == "HTTP_429"
    assert len(manifest) == 2
    config["queries"]["Q1"]["keywords"] = "different"
    assert collect_cached_queries(config, tmp_path)[0] == []
