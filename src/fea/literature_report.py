"""Export explicit screening judgements without treating unreviewed papers as negatives."""
from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from pathlib import Path

from fea.io import write_json


def screening_rows(records: list[dict], decisions: dict) -> list[dict]:
    """Apply reviewed identifiers; all other records remain visibly pending."""
    rows, matched = [], set()
    for record in records:
        identifiers = {record["doi"], record["rec_id"]}
        identifiers.update(r["source_id"] for r in record["evidence"])
        keys = identifiers & decisions.keys()
        if len(keys) > 1:
            raise ValueError("More than one judgement matches a merged record")
        decision = decisions[next(iter(keys))] if keys else None
        row = {key: record[key] for key in ("rec_id", "doi", "title", "year", "venue")}
        row.update(stage1="PENDING", stage2="PENDING", claim_affected="",
                   note="Not screened before the protocol stop; no negative judgement is implied.",
                   fulltext_checked=False, abstract_read=False)
        if decision:
            matched.update(keys)
            row.update(decision)
            if row["abstract_read"] and not record["abstracts"]:
                raise ValueError("Cannot mark an unavailable API abstract as read")
            if row["stage2"] in {"A_overlap", "B_related", "KNOWN", "C_irrelevant"} and not row["abstract_read"]:
                raise ValueError("Stage 2 classification requires an explicitly read API abstract")
            if row["stage2"] in {"A_overlap", "B_related"} and not row["claim_affected"]:
                raise ValueError("A/B judgements require affected claims")
        rows.append(row)
    if set(decisions) != matched:
        raise ValueError("A screening decision has no retrieved evidence record")
    return rows


def export_screening(records: list[dict], output: Path, reports: Path, digest: str,
                     decisions_path: Path) -> None:
    """Write counts, evidence links, all A/B decisions and an explicit partial-review status."""
    decisions_bytes = decisions_path.read_bytes()
    review = json.loads(decisions_bytes)
    rows = screening_rows(records, review["decisions"])
    columns = "rec_id doi title year venue stage1 stage2 claim_affected note fulltext_checked abstract_read config_hash".split()
    with (output / "screened.csv").open("w", encoding="utf8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=columns)
        writer.writeheader()
        writer.writerows({**r, "config_hash": digest} for r in rows)
    stage1 = Counter(r["stage1"] for r in rows)
    stage2 = Counter(r["stage2"] for r in rows)
    blockers = [r["rec_id"] for r in rows if r["stage2"] == "A_overlap"
                and {"C2", "C3"} & set(r["claim_affected"].split("|"))]
    summary = {"config_hash": digest, "decisions_sha256": hashlib.sha256(decisions_bytes).hexdigest(),
               "status": "STOP_REQUIRED_PARTIAL_SCREENING" if blockers else "SCREENING_PENDING",
               "records": len(rows), "stage1": dict(stage1), "stage2": dict(stage2),
               "abstracts_read": sum(r["abstract_read"] for r in rows),
               "fulltexts_checked": sum(r["fulltext_checked"] for r in rows),
               "stop_records": blockers,
               "records_without_api_abstract": sum(not r["abstracts"] for r in records)}
    write_json(output / "screening_summary.json", summary)
    retrieval = json.loads((output / "retrieval_summary.json").read_text(encoding="utf8"))
    retrieval["screening_status"] = summary["status"]
    write_json(output / "retrieval_summary.json", retrieval)
    counts = Counter()
    for query in retrieval["queries"]:
        counts[query["source"]] += query["retrieved"]
    text = ["## Systematic confirmation (task L)", "", f"**Status: {summary['status']}.**",
            "The configured retrieval was run; screening stopped early after a full-text-confirmed C3 overlap triggered §5 of docs/LITERATURE_SEARCH.md. This is an interim evidence report, not a completed systematic review or an exhaustive novelty clearance.", "",
            "### Retrieval and screening flow", "", "| Step | Count |", "|---|---:|"]
    for source, count in sorted(counts.items()):
        text.append(f"| Retrieved query records: {source} (before deduplication) | {count} |")
    text.extend([f"| After DOI / normalized-title-and-year deduplication | {len(rows)} |",
                 f"| Title decisions completed | {len(rows)-stage1['PENDING']} |",
                 f"| Titles retained among those reviewed | {stage1['KEEP']} |",
                 f"| Titles excluded among those reviewed | {stage1['EXCLUDE']} |",
                 f"| Titles still pending | {stage1['PENDING']} |",
                 f"| API abstracts actually read | {summary['abstracts_read']} |"])
    for category in ("A_overlap", "B_related", "KNOWN", "C_irrelevant", "PENDING", "NOT_APPLICABLE"):
        text.append(f"| Abstract-stage {category} | {stage2[category]} |")
    text.extend([f"| Full texts checked | {summary['fulltexts_checked']} |",
                 f"| All retrieved records without an API abstract | {summary['records_without_api_abstract']} |", "",
                 "Counts are produced from screening_decisions.json; pending records are not counted as irrelevant. The initial order prioritized titles/abstracts about transformable furniture, daily activity and quantified area. No automated keyword rule assigned a negative screening decision.", "",
                 "### Every reviewed A/B record", "",
                 "| Citation (API metadata) | DOI / source | Rating | Claim | Judgement |",
                 "|---|---|---|---|---|"])
    metadata = {r["rec_id"]: r for r in records}
    for row in rows:
        if row["stage2"] not in {"A_overlap", "B_related"}:
            continue
        record = metadata[row["rec_id"]]
        citation = "; ".join(record["authors"][:3]) + f" ({row['year']}). {row['title']}. {row['venue']}"
        url = "https://doi.org/" + row["doi"] if row["doi"] else record["url"]
        cells = [citation, f"[{row['doi'] or 'source'}]({url})", row["stage2"], row["claim_affected"], row["note"]]
        text.append("| " + " | ".join(str(c).replace("|", ";").replace("\n", " ") for c in cells) + " |")
    text.extend(["", "### Updated contribution assessment", "", "| Claim | Verdict | Scope of judgement |", "|---|---|---|"])
    for key, value in review["verdicts"].items():
        text.append(f"| {key} | {value['verdict']} | {value['note']} |")
    text.extend(["", "### Full-text overlap evidence", "", review["overlap_evidence"], "",
                 "### Proposed citation additions", "", review["proposals"], "",
                 "### Limits and reproducibility", "", review["limitations"], "",
                 "Query-level totals, dates, URLs and retry outcomes are in results/literature/retrieval_queries.csv and request_manifest.json. Raw responses and the paper remain in ignored data/interim/lit_cache/; abstracts and full texts are not republished.", "",
                 "Reproduce retrieval: `python scripts/00b_lit_search.py`. Reproduce this interim report from the saved cache: `python scripts/00b_lit_search.py --cached-only --screening-decisions results/literature/screening_decisions.json`. Resume by extending explicit screening decisions after reviewer guidance. Do not interpret a successful script exit as permission to cross the research gate.", "",
                 f"Config hash: `{digest}`. Screening decision hash: `{summary['decisions_sha256']}`.", ""])
    section = "\n".join(text)
    target = reports / "novelty_check.md"
    original = target.read_text(encoding="utf8")
    marker = "## Systematic confirmation (task L)"
    if marker in original:
        original = original[:original.index(marker)]
    target.write_text(original.rstrip() + "\n\n" + section, encoding="utf8")
