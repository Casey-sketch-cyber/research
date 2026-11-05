"""Download authorized archives only; resume and verify every completed transfer."""
from __future__ import annotations

import csv
import datetime as dt
import hashlib
import json
import logging
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import requests
from tqdm import tqdm

from fea.io import prepare_cli, sha256_file, start_run, write_json


def expected_digest(path: Path, specification: dict) -> None:
    """Check the publisher's checksum when one is supplied."""
    if "md5" in specification:
        with path.open("rb") as stream:
            digest = hashlib.file_digest(stream, "md5").hexdigest()
        if digest != specification["md5"]:
            raise ValueError("Publisher checksum mismatch")


def acquire(resource: dict, root: Path, previous: dict, verify_only: bool, config_digest: str) -> dict:
    """Transfer with Range support; only atomically publish complete verified files."""
    path = root / resource["file"]
    path.parent.mkdir(parents=True, exist_ok=True)
    prior = previous.get(resource["file"])
    if path.exists():
        sha = sha256_file(path)
        if prior and sha != prior["sha256"]:
            raise ValueError("Existing file differs from manifest")
        if verify_only and not prior:
            raise ValueError("Existing file has no verification manifest")
        expected_digest(path, resource)
    else:
        if verify_only:
            raise FileNotFoundError("Required archive is missing")
        partial = path.with_suffix(path.suffix + ".part")
        for attempt in range(4):
            try:
                offset = partial.stat().st_size if partial.exists() else 0
                headers = {"Range": f"bytes={offset}-", "Accept-Encoding": "identity"} if offset else {"Accept-Encoding": "identity"}
                with requests.get(resource["url"], headers=headers, stream=True, timeout=(20, 90)) as response:
                    response.raise_for_status()
                    if offset and response.status_code == 206:
                        if not response.headers.get("Content-Range", "").startswith(f"bytes {offset}-"):
                            raise ValueError("Unexpected resume range")
                        mode = "ab"
                    else:
                        offset, mode = 0, "wb"
                    length = response.headers.get("Content-Length")
                    total = offset + int(length) if length else None
                    with partial.open(mode) as stream, tqdm(total=total, initial=offset, desc=resource["dataset"],
                                                            unit="B", unit_scale=True, mininterval=5) as bar:
                        for chunk in response.iter_content(chunk_size=1024 * 1024):
                            stream.write(chunk)
                            bar.update(len(chunk))
                if total is not None and partial.stat().st_size != total:
                    raise ValueError("Incomplete transfer")
                expected_digest(partial, resource)
                partial.replace(path)
                break
            except (requests.RequestException, OSError, ValueError) as exc:
                logging.warning("%s attempt=%s type=%s", resource["dataset"], attempt + 1, type(exc).__name__)
                if attempt == 3:
                    raise
                time.sleep(2 ** attempt)
        sha = sha256_file(path)
    return {"dataset": resource["dataset"], "file": resource["file"], "url": resource["url"],
            "bytes": path.stat().st_size, "sha256": sha,
            "date": prior["date"] if prior else dt.datetime.now(dt.timezone.utc).isoformat(),
            "config_hash": config_digest}


def main() -> None:
    """Download or verify the exact committed resource list."""
    parser = prepare_cli(__doc__)
    parser.add_argument("--verify-only", action="store_true")
    parser.add_argument("--datasets", nargs="+", help="Optional exact dataset IDs for staged acquisition")
    args = parser.parse_args()
    config, digest, start = start_run(args, "01_download")
    resources = config["downloads"]["resources"]
    total_required = len(resources)
    if args.datasets:
        known = {r["dataset"] for r in resources}
        if not set(args.datasets) <= known:
            parser.error("Unknown dataset ID")
        resources = [r for r in resources if r["dataset"] in args.datasets]
    if args.dry_run:
        print(json.dumps(resources, indent=2))
        return
    root = Path(config["paths"]["raw"])
    manifest = root / "MANIFEST.csv"
    prior = {row["file"]: row for row in csv.DictReader(manifest.open(encoding="utf-8"))} if manifest.exists() else {}
    records, errors = [], []
    with ThreadPoolExecutor(max_workers=3) as pool:
        pending = {pool.submit(acquire, r, root, prior, args.verify_only, digest): r for r in resources}
        for future in as_completed(pending):
            resource = pending[future]
            try:
                records.append(future.result())
                # Persist successes immediately so interrupted runs remain verifiable.
                combined = {**prior, **{row["file"]: row for row in records}}
                columns = ["dataset", "file", "url", "bytes", "sha256", "date", "config_hash"]
                temporary = manifest.with_suffix(".tmp")
                with temporary.open("w", encoding="utf-8", newline="") as stream:
                    writer = csv.DictWriter(stream, fieldnames=columns)
                    writer.writeheader()
                    writer.writerows(sorted(combined.values(), key=lambda row: row["file"]))
                temporary.replace(manifest)
            except Exception as exc:
                errors.append({"dataset": resource["dataset"], "error_type": type(exc).__name__})
    Path("reports").mkdir(exist_ok=True)
    if manifest.exists():
        Path("reports/data_manifest.csv").write_bytes(manifest.read_bytes())
    write_json("reports/acquisition.json", {"config_hash": digest, "successful": len(records), "errors": errors,
                                           "selected_count": len(resources), "required_count": total_required,
                                           "partial": len(resources) != total_required,
                                           "runtime_s": round(time.perf_counter() - start, 3)})
    print(json.dumps({"successful": len(records), "errors": errors}))
    raise SystemExit(bool(errors))


if __name__ == "__main__":
    main()
