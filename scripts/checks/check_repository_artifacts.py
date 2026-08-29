#!/usr/bin/env python3
"""Fail when generated cache/build artifacts are tracked by Git.

Developer environments legitimately contain ignored caches and dependencies. Source
packages are built from tracked files, so this guard checks that authoritative set and
does not fail merely because a local install has created ``node_modules`` or ``.venv``.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

FORBIDDEN_DIR_NAMES = {
    "__pycache__",
    ".pytest_cache",
    ".ruff_cache",
    ".mypy_cache",
    ".vite",
    ".parcel-cache",
    "node_modules",
    ".venv",
    "venv",
    "dist",
    "build",
    "coverage",
}
FORBIDDEN_SUFFIXES = {
    ".pyc",
    ".pyo",
    ".pyd",
    ".log",
    ".sqlite3",
    ".sqlite3-shm",
    ".sqlite3-wal",
}
FORBIDDEN_TOP_LEVEL_DIRS = {
    "REFERENCE",
    "GIT_PEDAGOGY_BLUEPRINT_PACK",
}
MAX_VIOLATIONS = 50


def main() -> int:
    violations: list[str] = []
    result = subprocess.run(
        ["git", "-C", str(ROOT), "ls-files", "-z"],
        check=True,
        capture_output=True,
    )
    tracked_files = result.stdout.decode("utf-8", errors="surrogateescape").split("\0")

    for tracked_file in filter(None, tracked_files):
        path = Path(tracked_file)
        if not (ROOT / path).exists():
            # A tracked file deleted by the current change is no longer part of
            # the source tree that will be committed or packaged.
            continue
        parts = path.parts
        top_level_forbidden = bool(parts) and parts[0] in FORBIDDEN_TOP_LEVEL_DIRS
        forbidden_cache_dir = any(part in FORBIDDEN_DIR_NAMES for part in parts[:-1])
        forbidden_suffix = path.suffix in FORBIDDEN_SUFFIXES
        if top_level_forbidden or forbidden_cache_dir or forbidden_suffix:
            violations.append(path.as_posix())
        if len(violations) >= MAX_VIOLATIONS:
            break

    if violations:
        print("Generated/cache artifacts are tracked by Git:")
        for item in violations:
            print(f"- {item}")
        print("\nRemove them before committing or packaging the project.")
        return 1

    print("No generated/cache artifacts are tracked by Git.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
