#!/usr/bin/env python3
"""Remove generated cache/build artifacts from the repository tree."""
from __future__ import annotations

import os
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

ARTIFACT_DIR_NAMES = {
    "__pycache__",
    ".pytest_cache",
    ".ruff_cache",
    ".mypy_cache",
    ".vite",
    ".parcel-cache",
    "dist",
    "build",
    "coverage",
    "node_modules",
    ".venv",
    "venv",
}
ARTIFACT_SUFFIXES = {".pyc", ".pyo", ".pyd", ".log", ".sqlite3", ".sqlite3-shm", ".sqlite3-wal"}
SKIP_DIR_NAMES = {".git"}


def main() -> int:
    removed: list[str] = []

    for current_root, dir_names, file_names in os.walk(ROOT, topdown=True):
        current = Path(current_root)

        for dir_name in list(dir_names):
            if dir_name in SKIP_DIR_NAMES:
                dir_names.remove(dir_name)
                continue
            if dir_name in ARTIFACT_DIR_NAMES:
                path = current / dir_name
                shutil.rmtree(path)
                removed.append(path.relative_to(ROOT).as_posix())
                dir_names.remove(dir_name)

        for file_name in file_names:
            path = current / file_name
            if path.suffix in ARTIFACT_SUFFIXES:
                path.unlink()
                removed.append(path.relative_to(ROOT).as_posix())

    if removed:
        print(f"Removed {len(removed)} repository artifact(s):")
        for item in removed[:50]:
            print(f"- {item}")
        if len(removed) > 50:
            print(f"... and {len(removed) - 50} more")
    else:
        print("No repository artifacts needed cleaning.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
