#!/usr/bin/env python3
"""Fail when generated cache/build artifacts are present in the repository tree.

This project ships source zips for review. Runtime/build cache directories make diffs
noisy and can hide stale generated state, so they must never be committed or packaged.
The walk prunes ignored directories so the guard stays fast even when artifacts exist.
"""
from __future__ import annotations

import os
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
ALLOWLISTED_DIRS = {
    ".git",
}
FORBIDDEN_TOP_LEVEL_DIRS = {
    "REFERENCE",
    "GIT_PEDAGOGY_BLUEPRINT_PACK",
}
MAX_VIOLATIONS = 50


def relative(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def main() -> int:
    violations: list[str] = []

    for current_root, dir_names, file_names in os.walk(ROOT):
        current = Path(current_root)
        rel_parts = current.relative_to(ROOT).parts

        if any(part in ALLOWLISTED_DIRS for part in rel_parts):
            dir_names[:] = []
            continue

        for dir_name in list(dir_names):
            path = current / dir_name
            top_level_forbidden = not rel_parts and dir_name in FORBIDDEN_TOP_LEVEL_DIRS
            forbidden_cache_dir = dir_name in FORBIDDEN_DIR_NAMES
            if top_level_forbidden or forbidden_cache_dir:
                violations.append(relative(path))
                dir_names.remove(dir_name)
                if len(violations) >= MAX_VIOLATIONS:
                    break
        if len(violations) >= MAX_VIOLATIONS:
            break

        for file_name in file_names:
            path = current / file_name
            if path.suffix in FORBIDDEN_SUFFIXES:
                violations.append(relative(path))
                if len(violations) >= MAX_VIOLATIONS:
                    break
        if len(violations) >= MAX_VIOLATIONS:
            break

    if violations:
        print("Generated/cache artifacts are present in the source tree:")
        for item in violations:
            print(f"- {item}")
        print("\nRemove them before committing or packaging the project.")
        return 1

    print("No generated/cache artifacts found in the source tree.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
