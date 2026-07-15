#!/usr/bin/env python3
"""Create a clean source zip without runtime/build artifacts."""
from __future__ import annotations

import argparse
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

EXCLUDED_DIRS = {
    ".git",
    ".pytest_cache",
    ".ruff_cache",
    ".mypy_cache",
    ".vite",
    ".parcel-cache",
    "__pycache__",
    "node_modules",
    "dist",
    "build",
    "coverage",
    ".venv",
    "venv",
}
EXCLUDED_SUFFIXES = {".pyc", ".pyo", ".pyd", ".log", ".sqlite3", ".sqlite3-shm", ".sqlite3-wal"}


def should_exclude(path: Path) -> bool:
    rel_parts = path.relative_to(ROOT).parts
    return any(part in EXCLUDED_DIRS for part in rel_parts) or path.suffix in EXCLUDED_SUFFIXES


def package(output: Path) -> int:
    output = output.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
        for path in ROOT.rglob("*"):
            if path == output or should_exclude(path) or path.is_dir():
                continue
            archive.write(path, path.relative_to(ROOT))
            count += 1
    print(f"Packaged {count} source files into {output}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path, help="Destination .zip path")
    args = parser.parse_args()
    return package(args.output)


if __name__ == "__main__":
    raise SystemExit(main())
