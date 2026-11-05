"""Audit the exact tracked/staged publication set for private operational details."""
from __future__ import annotations

import json
import os
import re
import subprocess
from pathlib import Path

from tqdm import tqdm

from fea.io import prepare_cli, start_run


def inspect_text(text: str, private_terms: list[str]) -> list[str]:
    """Return finding categories without echoing any sensitive value."""
    patterns = {
        "private_absolute_path": r"(?i)(?:[A-Z]:[\\/](?:Users|PROJECT|CodexData)|/(?:root|home)/[^\s`\"']+)",
        "ssh_endpoint": r"(?i)(?:ssh\s+[^\n]*@|(?:root|ubuntu)@[\w.-]+|connect\.[\w.-]+)",
        "private_key": r"-----BEGIN (?:RSA |OPENSSH |EC )?PRIVATE KEY-----",
        "access_token": r"(?:gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|AKIA[A-Z0-9]{16})",
        "machine_identifier": r"(?i)(?:GPU-[0-9a-f-]{16,}|(?:hostname|machine_id|mac_address)\s*[:=]\s*['\"]?[^\s,}\]]+)",
    }
    findings = [name for name, pattern in patterns.items() if re.search(pattern, text)]
    # Bibliographic identifiers can contain dotted number sequences. An octet
    # above 255 is not an IPv4 address; genuine address-shaped values still fail.
    ipv4_pattern = r"(?<![\d.])(?:\d{1,3}\.){3}\d{1,3}(?![\d.])"
    if any(all(int(part) <= 255 for part in match.group().split("."))
           for match in re.finditer(ipv4_pattern, text)):
        findings.append("ipv4_address")
    def matches_private_term(term: str) -> bool:
        if not term:
            return False
        # Short numeric IDs/ports must not match substrings of scientific
        # measurements or opaque hashes. Complete literal values still fail.
        if term.isdigit() and len(term) < 8:
            return re.search(r"(?<![\w.])" + re.escape(term) + r"(?![\w.])", text) is not None
        return term.casefold() in text.casefold()

    if any(matches_private_term(term) for term in private_terms):
        findings.append("explicit_private_term")
    return findings


def main() -> None:
    """Fail publication if a tracked file contains operational secrets or raw data."""
    parser = prepare_cli(__doc__)
    parser.add_argument("--staged", action="store_true")
    args = parser.parse_args()
    start_run(args, "check_publication")
    names = subprocess.check_output(["git", "ls-files", "-z"]).decode().split("\0")
    terms = json.loads(os.environ.get("FEA_PRIVATE_TERMS_JSON", "[]"))
    failures = []
    for name in tqdm([n for n in names if n], desc="Publication audit"):
        path = Path(name)
        if not path.is_file():
            continue
        if any(name.startswith(p) for p in ("data/raw/", "data/interim/", "data/private/", ".local/", ".tmp/", "logs/", ".cache/")):
            failures.append({"file": name, "category": "private_directory"})
            continue
        data = subprocess.check_output(["git", "show", f":{name}"]) if args.staged else path.read_bytes()
        if len(data) >= 50_000_000:
            failures.append({"file": name, "category": "oversized_file"})
        if path.suffix.lower() in {".png", ".jpg", ".jpeg", ".pdf"}:
            # Binary metadata also receives the literal-term scan.
            categories = ["explicit_private_term"] if any(t.encode() in data for t in terms if t) else []
        else:
            categories = inspect_text(data.decode("utf-8", "replace"), terms)
        failures.extend({"file": name, "category": category} for category in categories)
    print(json.dumps({"files_checked": len([n for n in names if n]), "findings": failures}, indent=2))
    raise SystemExit(bool(failures))


if __name__ == "__main__":
    main()
