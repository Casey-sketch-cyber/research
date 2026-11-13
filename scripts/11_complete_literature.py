from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter
from pathlib import Path

from fea.io import sha256_file


def read_index(path: Path) -> dict[str, dict]:
    with path.open(encoding="utf-8", newline="") as stream:
        rows = list(csv.DictReader(stream))
    indexed = {row["rec_id"]: row for row in rows}
    if len(rows) != len(indexed) or "" in indexed:
        raise ValueError(f"Duplicate or empty record IDs in {path.name}")
    return indexed


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: dict) -> None:
    temporary = path.with_suffix(".json.tmp")
    temporary.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    temporary.replace(path)


def has_hash(value: str) -> bool:
    return re.fullmatch(r"[a-f0-9]{64}", value) is not None


def as_bool(value: str) -> bool:
    if value.lower() not in {"true", "false"}:
        raise ValueError("Invalid boolean in screening evidence")
    return value.lower() == "true"


def verify_screening(output: Path) -> tuple[dict, list[dict]]:
    raw = read_index(output / "raw_hits.csv")
    screened = read_index(output / "screened.csv")
    attempts = read_index(output / "abstract_lookup_receipts.csv")
    evidence = read_json(output / "fulltext_checks_g3.json")["records"]
    retrieval = read_json(output / "retrieval_summary.json")
    q1 = read_json(output / "openalex_q1_retry.json")
    original = read_json(output / "fulltext_checks.json")

    if raw.keys() != screened.keys() or not raw or len(raw) != retrieval["deduplicated_records"]:
        raise ValueError("Title decisions do not cover the retrieved records")
    if not attempts.keys() <= raw.keys() or not evidence.keys() <= raw.keys():
        raise ValueError("Evidence record has no retrieved title")
    if not has_hash(q1["response_sha256"]) or q1["query_id"] != "Q1_transformable_layout":
        raise ValueError("OpenAlex Q1 retry is missing a verifiable response receipt")

    accepted_classes = {"A_overlap", "B_related", "C_irrelevant", "KNOWN"}
    accepted_claims = {"C2", "C3", "C4", "H2"}
    fulltext_statuses = {"fulltext_checked", "abstract_only", "project_summary_checked"}
    missing = []
    for record_id, row in screened.items():
        metadata = raw[record_id]
        attempt = attempts.get(record_id)
        fulltext = evidence.get(record_id)
        stage2 = row["stage2"]
        available = as_bool(metadata["abstract_available"])
        kept = row["stage1"] == "KEEP"
        if any(" ".join(row[key].split()) != " ".join(metadata[key].split())
               for key in ("doi", "title", "year", "venue", "config_hash")):
            raise ValueError(f"Bibliographic metadata differs from the retrieval ledger for {record_id}")
        if row["stage1"] not in {"KEEP", "EXCLUDE"} or not row["title_reason"]:
            raise ValueError(f"Invalid title decision for {record_id}")
        if attempt:
            if available or not kept or not has_hash(attempt["response_sha256"]):
                raise ValueError(f"Unexpected abstract lookup receipt for {record_id}")
            available = attempt["reason"] == "abstract_found"

        abstract_read = as_bool(row["abstract_read"])
        if abstract_read != (available and kept):
            raise ValueError(f"Abstract evidence is incomplete for {record_id}")
        if abstract_read:
            if stage2 not in accepted_classes or not has_hash(row["abstract_sha256"]) or not row["note"]:
                raise ValueError(f"Invalid abstract decision for {record_id}")
        elif kept:
            if stage2 != "NO_ABSTRACT_TITLE_RELEVANT":
                raise ValueError(f"Missing abstract status for {record_id}")
            expected = attempt["reason"] if attempt else "not_attempted"
            if row["abstract_lookup"] != expected:
                raise ValueError(f"Missing abstract lookup disposition for {record_id}")
            missing.append(row)
        elif stage2 != "NOT_APPLICABLE":
            raise ValueError(f"Unexpected classification for an excluded title {record_id}")

        if stage2 in {"A_overlap", "B_related"}:
            if not set(row["claim_affected"].split("|")) <= accepted_claims:
                raise ValueError(f"Unexpected claim for {record_id}")
            if not row["established"] or not row["how_we_add"]:
                raise ValueError(f"Missing positioning notes for {record_id}")
        if stage2 == "A_overlap" and not fulltext:
            raise ValueError(f"Missing full-text disposition for {record_id}")
        if fulltext:
            if fulltext["status"] not in fulltext_statuses or not abstract_read:
                raise ValueError(f"Unexpected full-text disposition for {record_id}")
            if row["source_url"] != fulltext["source_url"] or row["fulltext_status"] != fulltext["status"]:
                raise ValueError(f"Inconsistent source evidence for {record_id}")
        if as_bool(row["fulltext_checked"]) != bool(fulltext and fulltext["status"] == "fulltext_checked"):
            raise ValueError(f"Inconsistent full-text check for {record_id}")
        if metadata["doi"] == original["doi"]:
            if not fulltext or fulltext.get("source_sha256") != original["sha256"]:
                raise ValueError("The original full-text evidence changed")

    queries = retrieval["queries"]
    by_source = Counter()
    for query in queries:
        by_source[query["source"]] += query["retrieved"]
    if sum(by_source.values()) != retrieval["raw_query_records"]:
        raise ValueError("Source counts do not reconcile with retrieved query records")
    return {
        "status": "COMPLETE_RETRIEVED_SNAPSHOT",
        "config_hash": retrieval["config_hash"],
        "raw_query_records": retrieval["raw_query_records"],
        "retrieved_by_source": dict(sorted(by_source.items())),
        "records": len(raw),
        "stage1": dict(sorted(Counter(row["stage1"] for row in screened.values()).items())),
        "stage2": dict(sorted(Counter(row["stage2"] for row in screened.values()).items())),
        "abstracts_read": sum(as_bool(row["abstract_read"]) for row in screened.values()),
        "missing_abstracts": len(missing),
        "crossref_lookup_attempts": len(attempts),
        "crossref_lookup_outcomes": dict(sorted(Counter(row["reason"] for row in attempts.values()).items())),
        "fulltext_dispositions": dict(sorted(Counter(item["status"] for item in evidence.values()).items())),
        "openalex_q1_retry_status_code": q1["status_code"],
        "openalex_q1_retry_records_returned": q1["records_returned"],
    }, missing


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate the completed G3 literature screening ledger.")
    parser.add_argument("--repo", type=Path, default=Path("."))
    parser.add_argument("--verify", action="store_true")
    args = parser.parse_args()
    output = args.repo / "results" / "literature"
    summary, missing = verify_screening(output)
    summary_path = output / "screening_summary.json"
    missing_path = output / "missing_abstracts.csv"
    acceptance_path = output / "acceptance.json"
    retrieval_path = output / "retrieval_summary.json"

    if args.verify:
        if read_json(summary_path) != summary or read_index(missing_path).keys() != {row["rec_id"] for row in missing}:
            raise ValueError("Exported screening totals differ from the verified ledger")
        if read_json(retrieval_path)["screening_status"] != summary["status"]:
            raise ValueError("Retrieval snapshot does not record completed screening")
    else:
        fields = "rec_id doi title year venue title_reason abstract_lookup".split()
        temporary = missing_path.with_suffix(".csv.tmp")
        with temporary.open("w", encoding="utf-8", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
            writer.writeheader()
            writer.writerows(missing)
        temporary.replace(missing_path)
        write_json(summary_path, summary)
        retrieval = read_json(retrieval_path)
        retrieval["screening_status"] = summary["status"]
        write_json(retrieval_path, retrieval)

    filenames = (
        "raw_hits.csv", "retrieval_queries.csv", "retrieval_summary.json", "request_manifest.json",
        "retry_events.json", "openalex_q1_retry.json", "screened.csv", "screening_summary.json",
        "missing_abstracts.csv", "abstract_lookup_receipts.csv", "fulltext_checks_g3.json",
        "fulltext_checks.json",
    )
    acceptance = {
        "passed": True,
        "status": summary["status"],
        "records": summary["records"],
        "abstracts_read": summary["abstracts_read"],
        "outputs": {f"results/literature/{name}": sha256_file(output / name) for name in filenames},
    }
    if args.verify:
        if read_json(acceptance_path) != acceptance:
            raise ValueError("Screening artifacts differ from the acceptance record")
    else:
        write_json(acceptance_path, acceptance)
    print(json.dumps(summary, ensure_ascii=True))


if __name__ == "__main__":
    main()
