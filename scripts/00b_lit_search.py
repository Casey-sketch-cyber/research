"""Retrieve reproducible scholarly evidence for Task L; screening is a separate judgement."""
from __future__ import annotations

import csv
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import yaml
from tqdm import tqdm

from fea.config import config_hash
from fea.io import prepare_cli, start_run, write_json
from fea.literature import collect_cached_queries, collect_retry_events, deduplicate, retrieve_source


def main() -> None:
    """Cache each API response and export metadata, request logs and pending screening rows."""
    parser = prepare_cli(__doc__)
    parser.add_argument("--sources", nargs="+", choices=["openalex", "semantic_scholar", "crossref", "arxiv"])
    parser.add_argument("--cached-only", action="store_true", help="Re-export saved evidence without network calls")
    parser.add_argument("--screening-decisions", type=Path, help="Explicit reviewed decisions; unreviewed records stay pending")
    args = parser.parse_args()
    project, project_hash, started = start_run(args, "00b_lit_search")
    config = yaml.safe_load((Path(args.config).parent / "lit_search.yaml").read_text(encoding="utf8"))
    digest = config_hash({"project_hash": project_hash, "literature": config})
    if args.dry_run:
        print("Would retrieve configured queries, cache raw evidence, and export metadata without inventing screening decisions.")
        return
    cache = Path(project["paths"]["interim"]) / "lit_cache"
    cache.mkdir(parents=True, exist_ok=True)
    sources = args.sources or list(config["sources"])
    # Each source has one worker. Requests to the same provider never overlap.
    if not args.cached_only:
        with ThreadPoolExecutor(max_workers=len(sources)) as pool:
            futures = {pool.submit(retrieve_source, source, config, cache): source for source in sources}
            for future in tqdm(as_completed(futures), total=len(futures), desc="Literature sources"):
                future.result()
    records, summaries, requests = collect_cached_queries(config, cache)
    merged = deduplicate(records)
    if not requests:
        raise ValueError("No cached queries; run retrieval before using --cached-only")
    write_json(cache / "merged_records.json", merged)
    output = Path(project["paths"]["results"]) / "literature"
    output.mkdir(parents=True, exist_ok=True)
    columns = "rec_id doi title year venue type authors_first3 sources query_ids cited_by abstract_available url config_hash".split()
    with (output / "raw_hits.csv").open("w", encoding="utf8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=columns)
        writer.writeheader()
        for item in merged:
            row = {k: item[k] for k in columns if k in item}
            row.update(authors_first3="; ".join(item["authors"][:3]), sources="|".join(item["sources"]),
                       query_ids="|".join(item["query_ids"]), abstract_available=bool(item["abstracts"]), config_hash=digest)
            writer.writerow(row)
    with (output / "retrieval_queries.csv").open("w", encoding="utf8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=[*summaries[0], "config_hash"])
        writer.writeheader()
        writer.writerows({**row, "config_hash": digest} for row in summaries)
    write_json(output / "request_manifest.json", {"config_hash": digest, "requests": requests})
    write_json(output / "retry_events.json", {"config_hash": digest,
        "note": "Retry warnings from saved run logs; overlap with manifest attempts, so do not add the counts. Initial cache versions retained the latest response per URL; this log also preserves earlier failed-pass warnings.",
        "events": collect_retry_events(Path("logs"))})
    write_json(output / "retrieval_summary.json", {"config_hash": digest, "project_hash": project_hash,
        "raw_query_records": len(records), "deduplicated_records": len(merged),
        "records_with_abstracts": sum(bool(row["abstracts"]) for row in merged), "queries": summaries,
        "runtime_s": time.perf_counter() - started, "screening_status": "PENDING"})
    print(f"Retrieved {len(records)} query records; {len(merged)} unique records; screening pending.")
    if args.screening_decisions:
        from fea.literature_report import export_screening
        export_screening(merged, output, Path(project["paths"]["reports"]), digest, args.screening_decisions)
        print("Exported explicit screening decisions; check screening_summary.json for the research gate.")


if __name__ == "__main__":
    main()
