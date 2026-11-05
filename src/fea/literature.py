"""Cached scholarly retrieval and provenance-preserving bibliographic merging."""
from __future__ import annotations

import hashlib
import html
import json
import logging
import re
import time
import unicodedata
import xml.etree.ElementTree as ET
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import parse_qs, urlparse

import requests

from fea.io import write_json


def clean_text(value: str | None) -> str:
    """Remove publisher XML markup and normalize whitespace without rewriting text."""
    return " ".join(html.unescape(re.sub(r"<[^>]+>", " ", value or "")).split())


def title_key(value: str) -> str:
    """Normalize titles for exact deduplication, retaining letters and digits."""
    value = unicodedata.normalize("NFKC", clean_text(value)).casefold()
    return " ".join(re.sub(r"[^\w\s]", " ", value).split())


def doi_key(value: str | None) -> str:
    """Normalize supplied DOI identifiers; never infer an identifier from a title."""
    return re.sub(r"^(?:https?://(?:dx\.)?doi\.org/|doi:\s*)", "", (value or "").strip(), flags=re.I).lower()


def translated_query(boolean: str, source: str) -> str:
    """Translate configured Boolean expressions without dropping their grouping."""
    tokens = re.findall(r'"[^"]+"|\(|\)|[^\s()]+', boolean)
    if source == "semantic_scholar":
        return " ".join({"AND": "+", "OR": "|", "NOT": "-"}.get(t, t) for t in tokens)
    if source == "arxiv":
        return " ".join(t if t in {"AND", "OR", "ANDNOT", "(", ")"} else ("ANDNOT" if t == "NOT" else "all:" + t) for t in tokens)
    return boolean


class CachedAPI:
    """One sequential client per source, with bounded retries and raw response evidence."""

    def __init__(self, source: str, directory: Path):
        self.source, self.directory = source, directory / source
        self.directory.mkdir(parents=True, exist_ok=True)
        self.session = requests.Session()
        self.session.headers["User-Agent"] = "FEA-literature-confirmation/0.1"
        self.last_request = 0.
        self.interval = {"arxiv": 3.1, "semantic_scholar": 2., "crossref": 1., "openalex": 0.5}[source]
        self.manifest: list[dict] = []

    def get(self, endpoint: str, params: dict, query_id: str) -> dict:
        """Return a successful cache entry or a recorded final failure."""
        request = requests.Request("GET", endpoint, params=params).prepare()
        assert not any(k.lower() in {"mailto", "api_key", "key", "email"} for k in params)
        key = hashlib.sha256(request.url.encode()).hexdigest()
        cache = self.directory / (key + ".json")
        attempts = []
        if cache.exists():
            entry = json.loads(cache.read_text(encoding="utf8"))
            if entry["status"] == 200:
                self.manifest.append({k: entry[k] for k in ("source", "query_id", "url", "retrieved_at", "status", "attempts")})
                return entry
            attempts = entry["attempts"].copy()
        for attempt in range(4):
            time.sleep(max(0., self.interval - (time.monotonic() - self.last_request)))
            self.last_request = time.monotonic()
            stamp = datetime.now(timezone.utc).isoformat()
            retry_after = 0.
            try:
                response = self.session.send(request, timeout=(15, 60))
                status, body, error = response.status_code, response.text, ""
                try:
                    retry_after = min(60., float(response.headers.get("Retry-After", 0)))
                except ValueError:
                    retry_after = 0.
            except requests.RequestException as exc:
                status, body, error = 0, "", type(exc).__name__
            attempts.append({"date": stamp, "status": status, "error_type": error})
            entry = {"source": self.source, "query_id": query_id, "url": request.url,
                     "retrieved_at": stamp, "status": status, "body": body, "attempts": attempts}
            write_json(cache, entry)
            if status == 200 or (status not in {0, 408, 429} and status < 500):
                break
            logging.warning("Source %s query %s attempt %s status %s", self.source, query_id, attempt + 1, status)
            print(f"{self.source} {query_id}: attempt {attempt + 1}, HTTP {status}", flush=True)
            if attempt < 3:
                time.sleep(max(retry_after, (4, 12, 30)[attempt]))
        self.manifest.append({k: entry[k] for k in ("source", "query_id", "url", "retrieved_at", "status", "attempts")})
        return entry


def inverted_abstract(index: dict | None) -> str:
    """Reconstruct only the word positions actually supplied by OpenAlex."""
    if not index:
        return ""
    return " ".join(word for _, word in sorted((position, word) for word, positions in index.items() for position in positions))


def normalized_record(item: dict, source: str, query_id: str, evidence_url: str) -> dict:
    """Extract metadata from one API record without filling fields from memory."""
    if source == "openalex":
        location = item.get("primary_location") or {}
        fields = {"source_id": item["id"], "doi": doi_key(item.get("doi")), "title": item.get("title"),
                  "year": item.get("publication_year"), "venue": (location.get("source") or {}).get("display_name", ""),
                  "type": item.get("type", ""), "authors": [(a.get("author") or {}).get("display_name", "") for a in item.get("authorships", [])],
                  "cited_by": item.get("cited_by_count", 0), "abstract": inverted_abstract(item.get("abstract_inverted_index")),
                  "url": item.get("doi") or location.get("landing_page_url") or item["id"],
                  "oa_url": (item.get("open_access") or {}).get("oa_url") or location.get("pdf_url") or ""}
    elif source == "semantic_scholar":
        fields = {"source_id": item["paperId"], "doi": doi_key((item.get("externalIds") or {}).get("DOI")),
                  "title": item.get("title"), "year": item.get("year"), "venue": item.get("venue", ""),
                  "type": "|".join(item.get("publicationTypes") or []), "authors": [a["name"] for a in item.get("authors", [])],
                  "cited_by": item.get("citationCount", 0), "abstract": item.get("abstract") or "", "url": item.get("url") or "",
                  "oa_url": (item.get("openAccessPdf") or {}).get("url") or ""}
    elif source == "crossref":
        date = item.get("published", item.get("issued", {})).get("date-parts", [[]])[0]
        fields = {"source_id": item["DOI"], "doi": doi_key(item["DOI"]), "title": (item.get("title") or [""])[0],
                  "year": date[0] if date else None, "venue": (item.get("container-title") or [""])[0], "type": item.get("type", ""),
                  "authors": [" ".join(filter(None, [a.get("given"), a.get("family")])) or a.get("name", "") for a in item.get("author", [])],
                  "cited_by": item.get("is-referenced-by-count", 0), "abstract": item.get("abstract") or "", "url": item.get("URL", ""),
                  "oa_url": ""}
    else:
        fields = item.copy()
    fields.update(source=source, query_id=query_id, evidence_url=evidence_url)
    for key in ("title", "abstract", "venue"):
        fields[key] = clean_text(fields.get(key))
    return fields


def parse_arxiv(body: str) -> tuple[int, list[dict]]:
    """Parse the Atom API response, including its supplied DOI and journal reference."""
    ns = {"a": "http://www.w3.org/2005/Atom", "o": "http://a9.com/-/spec/opensearch/1.1/", "x": "http://arxiv.org/schemas/atom"}
    root = ET.fromstring(body)
    total_text = root.findtext("o:totalResults", namespaces=ns)
    if total_text is None:
        raise ValueError("Missing arXiv totalResults; response is not a successful search")
    records = []
    for item in root.findall("a:entry", ns):
        url = item.findtext("a:id", "", ns)
        if "api/errors" in url:
            raise ValueError("arXiv error feed")
        date = item.findtext("a:published", "", ns)
        records.append({"source_id": url, "doi": doi_key(item.findtext("x:doi", "", ns)),
                        "title": item.findtext("a:title", "", ns), "year": int(date[:4]) if date else None,
                        "venue": item.findtext("x:journal_ref", "", ns), "type": "preprint",
                        "authors": [a.findtext("a:name", "", ns) for a in item.findall("a:author", ns)],
                        "cited_by": None, "abstract": item.findtext("a:summary", "", ns), "url": url,
                        "oa_url": next((l.attrib["href"] for l in item.findall("a:link", ns) if l.attrib.get("title") == "pdf"), "")})
    return int(total_text), records


def retrieve_source(source: str, config: dict, cache: Path) -> tuple[list[dict], list[dict], list[dict]]:
    """Execute all configured queries sequentially for one scholarly API."""
    client = CachedAPI(source, cache)
    endpoint = config["sources"][source]["endpoint"]
    if source == "arxiv":
        endpoint = endpoint.replace("http://", "https://", 1)
    lower, upper = config["years"]
    cap = config["max_records_per_query_per_source"]
    records, summaries = [], []
    for query_id, query in config["queries"].items():
        start, cursor, total, current, error = 0, "*", None, [], ""
        while len(current) < cap:
            boolean = translated_query(query["boolean"], source)
            if source == "openalex":
                params = {"filter": f"from_publication_date:{lower}-01-01,to_publication_date:{upper}-12-31,language:en,title_and_abstract.search:{boolean}",
                          "per_page": min(100, cap), "page": 1 + start // min(100, cap)}
            elif source == "semantic_scholar":
                params = {"query": boolean, "year": f"{lower}:{upper}",
                          "fields": "title,year,venue,publicationTypes,authors,abstract,citationCount,externalIds,openAccessPdf,url"}
                if cursor != "*":
                    params["token"] = cursor
            elif source == "crossref":
                params = {"query.bibliographic": query["keywords"], "filter": f"from-pub-date:{lower}-01-01,until-pub-date:{upper}-12-31",
                          "rows": cap, "offset": start}
            else:
                params = {"search_query": f"({boolean}) AND submittedDate:[{lower}01010000 TO {upper}12312359]",
                          "start": start, "max_results": min(500, cap - len(current)), "sortBy": "relevance", "sortOrder": "descending"}
            response = client.get(endpoint, params, query_id)
            if response["status"] != 200:
                error = "HTTP_" + str(response["status"])
                break
            try:
                if source == "arxiv":
                    total, items = parse_arxiv(response["body"])
                    next_cursor = None
                else:
                    data = json.loads(response["body"])
                    if source == "openalex":
                        total, items, next_cursor = data["meta"]["count"], data["results"], data["meta"].get("next_cursor")
                    elif source == "semantic_scholar":
                        total, items, next_cursor = data["total"], data["data"], data.get("token")
                    else:
                        total, items, next_cursor = data["message"]["total-results"], data["message"]["items"], None
                current.extend(normalized_record(item, source, query_id, response["url"]) for item in items[:cap - len(current)])
            except (KeyError, ValueError, ET.ParseError) as exc:
                error = "PARSE_" + type(exc).__name__
                break
            start += len(items)
            if not items or len(current) >= cap or len(current) >= total:
                break
            if source == "semantic_scholar":
                if not next_cursor or next_cursor == cursor:
                    error = "MISSING_OR_REPEATED_CURSOR"
                    break
                cursor = next_cursor
        records.extend(current)
        summaries.append({"source": source, "query_id": query_id, "reported_hits": total,
                          "retrieved": len(current), "cap": cap, "capped": total is not None and total > len(current) and len(current) == cap,
                          "error": error})
        print(f"{source} {query_id}: retrieved={len(current)} total={total} {error}", flush=True)
        write_json(cache / f"{source}_progress.json", {"queries": summaries, "records": records, "requests": client.manifest})
    return records, summaries, client.manifest


def deduplicate(records: list[dict]) -> list[dict]:
    """Merge DOI and title/year equivalence classes, retaining all evidence records."""
    parent = list(range(len(records)))
    def root(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i
    seen = {}
    for i, row in enumerate(records):
        keys = []
        if row["doi"]:
            keys.append(("doi", doi_key(row["doi"])))
        if title_key(row["title"]) and row["year"] is not None:
            keys.append(("title_year", title_key(row["title"]), row["year"]))
        if not keys:
            keys.append(("source", row["source"], row["source_id"]))
        for key in keys:
            if key in seen:
                parent[root(i)] = root(seen[key])
            else:
                seen[key] = i
    groups = defaultdict(list)
    for i, row in enumerate(records):
        groups[root(i)].append(row)
    merged = []
    priority = {"crossref": 0, "openalex": 1, "semantic_scholar": 2, "arxiv": 3}
    for group in groups.values():
        group.sort(key=lambda r: (priority[r["source"]], r["source_id"], r["query_id"]))
        row = {}
        for key in ("doi", "title", "year", "venue", "type", "authors", "url"):
            row[key] = next((r[key] for r in group if r.get(key)), "")
        identity = row["doi"] or (title_key(row["title"]) + "|" + str(row["year"]))
        row.update(rec_id="L_" + hashlib.sha256(identity.encode()).hexdigest()[:12],
                   sources=sorted({r["source"] for r in group}), query_ids=sorted({r["query_id"] for r in group}),
                   cited_by=max((r["cited_by"] for r in group if r.get("cited_by") is not None), default=None),
                   abstracts=list(dict.fromkeys(r["abstract"] for r in group if r["abstract"])),
                   oa_urls=sorted({r["oa_url"] for r in group if r["oa_url"]}),
                   evidence=group, doi_variants=sorted({r["doi"] for r in group if r["doi"]}),
                   year_variants=sorted({r["year"] for r in group if r["year"] is not None}))
        merged.append(row)
    return sorted(merged, key=lambda r: r["rec_id"])


def collect_cached_queries(config: dict, cache: Path) -> tuple[list[dict], list[dict], list[dict]]:
    """Recover successful pages across retries; a later failure cannot erase earlier evidence.

    Cache directories are dedicated to this configured search. Only the six configured
    query IDs are included; metadata-completion requests have separate identifiers.
    """
    records, summaries, manifest = [], [], []
    cap = config["max_records_per_query_per_source"]
    for source in config["sources"]:
        entries = []
        for path in (cache / source).glob("*.json"):
            entry = json.loads(path.read_text(encoding="utf8"))
            if entry.get("query_id") in config["queries"] and request_matches_config(entry, config):
                entries.append(entry)
        entries.sort(key=lambda r: (r["retrieved_at"], r["url"]))
        for query_id in config["queries"]:
            unique, totals, failures, attempts = {}, [], [], 0
            for entry in (e for e in entries if e["query_id"] == query_id):
                manifest.append({**{k: entry[k] for k in ("source", "query_id", "url", "retrieved_at", "status", "attempts")},
                                 "response_sha256": hashlib.sha256(entry["body"].encode()).hexdigest()})
                attempts += len(entry["attempts"])
                if entry["status"] != 200:
                    failures.append("HTTP_" + str(entry["status"]))
                    continue
                try:
                    if source == "arxiv":
                        total, items = parse_arxiv(entry["body"])
                    else:
                        data = json.loads(entry["body"])
                        if source == "openalex":
                            total, items = data["meta"]["count"], data["results"]
                        elif source == "semantic_scholar":
                            total, items = data["total"], data["data"]
                        else:
                            total, items = data["message"]["total-results"], data["message"]["items"]
                    totals.append(total)
                    for item in items:
                        row = normalized_record(item, source, query_id, entry["url"])
                        if row["source_id"] not in unique and len(unique) < cap:
                            unique[row["source_id"]] = row
                except (KeyError, ValueError, ET.ParseError) as exc:
                    failures.append("PARSE_" + type(exc).__name__)
            total = totals[-1] if totals else None
            complete = total is not None and len(unique) >= min(total, cap)
            summaries.append({"source": source, "query_id": query_id, "reported_hits": total,
                              "retrieved": len(unique), "cap": cap,
                              "capped": total is not None and total > cap and len(unique) == cap,
                              "error": "" if complete else "|".join(sorted(set(failures))) or "INCOMPLETE",
                              "historical_errors": "|".join(sorted(set(failures))), "attempts": attempts})
            records.extend(unique.values())
    return records, summaries, manifest


def request_matches_config(entry: dict, config: dict) -> bool:
    """Reject old cache entries when a query or its year bounds change."""
    source = entry["source"]
    params = parse_qs(urlparse(entry["url"]).query)
    query = config["queries"][entry["query_id"]]
    lower, upper = config["years"]
    boolean = translated_query(query["boolean"], source)
    if source == "openalex":
        expected = f"from_publication_date:{lower}-01-01,to_publication_date:{upper}-12-31,language:en,title_and_abstract.search:{boolean}"
        return params.get("filter") == [expected]
    if source == "semantic_scholar":
        return params.get("query") == [boolean] and params.get("year") == [f"{lower}:{upper}"]
    if source == "crossref":
        return params.get("query.bibliographic") == [query["keywords"]] and params.get("filter") == [f"from-pub-date:{lower}-01-01,until-pub-date:{upper}-12-31"]
    return params.get("search_query") == [f"({boolean}) AND submittedDate:[{lower}01010000 TO {upper}12312359]"]


def collect_retry_events(directory: Path) -> list[dict]:
    """Export only structured retry messages, never private log contents or paths."""
    pattern = re.compile(r"^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d+) WARNING Source (\w+) query (\w+) attempt (\d+) status (\d+)$")
    events = []
    for path in sorted(directory.glob("00b_lit_search_*.log")):
        for line in path.read_text(encoding="utf8").splitlines():
            match = pattern.fullmatch(line)
            if not match:
                continue
            stamp, source, query_id, attempt, status = match.groups()
            # Logging uses local runtime time; convert it before publication.
            utc = datetime.strptime(stamp, "%Y-%m-%d %H:%M:%S,%f").astimezone(timezone.utc)
            events.append(dict(date=utc.isoformat(), source=source, query_id=query_id,
                               attempt=int(attempt), status=int(status)))
    return events
