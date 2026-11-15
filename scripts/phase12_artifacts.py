"""Write stable UTF-8 manifests on every supported output platform."""

import json
from pathlib import Path


def write_manifest(path: Path, contents: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(contents, indent=2, ensure_ascii=False, allow_nan=False) + "\n",
                         encoding="utf-8", newline="\n")
    temporary.replace(path)
