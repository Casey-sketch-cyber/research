"""Small artifact and command-line helpers, with project-local runtime directories."""
from __future__ import annotations

import argparse
import hashlib
import json
import logging
import os
import time
from pathlib import Path
from typing import Any

from .config import config_hash, load_config


def sha256_file(path: Path) -> str:
    """Stream a file digest without loading the file into memory."""
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def write_json(path: str | Path, value: Any) -> None:
    """Atomically write a UTF-8 JSON artifact with no nonfinite numbers."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + "\n",
                         encoding="utf-8")
    temporary.replace(path)


def prepare_cli(description: str) -> argparse.ArgumentParser:
    """Build the common phase-script command line."""
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("--config", default="config/project.yaml")
    parser.add_argument("--dry-run", action="store_true")
    return parser


def start_run(args: argparse.Namespace, name: str) -> tuple[dict[str, Any], str, float]:
    """Set local caches and initialize a private run log."""
    for directory in ("logs", ".tmp", ".cache", ".cache/matplotlib"):
        Path(directory).mkdir(parents=True, exist_ok=True)
    for variable, directory in (("TMPDIR", ".tmp"), ("TMP", ".tmp"), ("TEMP", ".tmp"),
                                ("XDG_CACHE_HOME", ".cache"), ("MPLCONFIGDIR", ".cache/matplotlib")):
        os.environ[variable] = str(Path(directory).resolve())
    logging.basicConfig(filename=Path("logs") / f"{name}_{time.strftime('%Y%m%d_%H%M%S', time.gmtime())}.log",
                        level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    config = load_config(args.config)
    digest = config_hash(config)
    logging.info("Start %s config_hash=%s dry_run=%s", name, digest, args.dry_run)
    return config, digest, time.perf_counter()
