"""Attempt one Crossref abstract lookup per clearly relevant, title-retained record."""

import argparse
import csv
from datetime import datetime, timezone
import json
from pathlib import Path
import time
from urllib.parse import quote

import requests

from fea.io import write_json
from fea.literature import clean_text, doi_key, title_key


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", required=True, type=Path)
    parser.add_argument("--cache", required=True, type=Path)
    args = parser.parse_args()
    if args.plan.suffix == ".csv":
        with args.plan.open(encoding="utf-8", newline="") as stream:
            plans = list(csv.DictReader(stream))
    else:
        plans = json.loads(args.plan.read_text(encoding="utf-8"))
    args.cache.mkdir(parents=True, exist_ok=True)
    client = requests.Session()
    client.headers["User-Agent"] = "FEA-literature-confirmation/0.1"
    pause = 1.05
    endpoint = "https://api.crossref.org/works"
    for row in plans:
        target = args.cache / (row["rec_id"] + ".json")
        if target.exists():
            continue
        doi = doi_key(row.get("doi"))
        url = endpoint + "/" + quote(doi, safe="/") if doi else endpoint
        params = {} if doi else {"query.title": row["title"], "rows": 1}
        request = requests.Request("GET", url, params=params).prepare()
        time.sleep(pause)
        pause = 1.05
        stamp = datetime.now(timezone.utc).isoformat(timespec="seconds")
        body, abstract, reason = "", "", ""
        status = 0
        try:
            response = client.send(request, timeout=(8, 12))
            status, body = response.status_code, response.text
            if status == 429:
                try:
                    pause = max(5.0, min(60.0, float(response.headers.get("Retry-After", 10))))
                except ValueError:
                    pause = 10.0
            if status == 200:
                payload = response.json()["message"]
                if doi:
                    paper = payload
                    matched = doi_key(paper.get("DOI")) == doi
                else:
                    items = payload.get("items", [])
                    paper = items[0] if items else {}
                    same_title = title_key((paper.get("title") or [""])[0]) == title_key(row["title"])
                    dates = (paper.get("issued", {}).get("date-parts") or [[None]])[0]
                    same_year = not row.get("year") or not dates[0] or abs(int(row["year"]) - int(dates[0])) <= 1
                    matched = same_title and same_year
                if matched:
                    abstract = clean_text(paper.get("abstract"))
                    reason = "abstract_found" if abstract else "matched_record_without_abstract"
                else:
                    reason = "no_exact_metadata_match"
            else:
                reason = f"HTTP_{status}"
        except requests.RequestException as exc:
            reason = type(exc).__name__
        except (KeyError, ValueError, TypeError) as exc:
            reason = "PARSE_" + type(exc).__name__
        write_json(target, {
            "rec_id": row["rec_id"],
            "source": "crossref",
            "url": request.url,
            "retrieved_at_utc": stamp,
            "status_code": status,
            "reason": reason,
            "abstract": abstract,
            "body": body,
        })
    print(f"Completed {len(plans)} planned abstract lookup attempts")


if __name__ == "__main__":
    main()
