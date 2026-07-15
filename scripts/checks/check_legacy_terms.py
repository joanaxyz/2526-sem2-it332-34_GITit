#!/usr/bin/env python3
"""Fail CI when removed product concepts leak back into active code.

The current product vocabulary is story / story world / level map / lesson / adventure / challenge.
Removed tower-map/tome/fake-theme product concepts are allowed only in explicit
legacy route redirects. Natural narrative uses of words such as "tower" remain
valid inside story content and must not be confused with the deprecated UI model.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

SCAN_ROOTS = [
    ROOT / "backend",
    ROOT / "frontend" / "src",
    ROOT / "frontend" / "scripts",
    ROOT / ".github",
    ROOT / "scripts",
]

ROOT_MARKDOWN_FILES = [
    ROOT / "README.md",
    ROOT / "ARCHITECTURE.md",
    ROOT / "DESIGN.md",
    ROOT / "PRODUCT.md",
    ROOT / "CONTENT_AUTHORING_GUIDE.md",
    ROOT / "CURRICULUM_AUTHORING_PLAN.md",
]

TEXT_SUFFIXES = {
    ".css",
    ".html",
    ".js",
    ".jsx",
    ".json",
    ".mjs",
    ".py",
    ".ts",
    ".tsx",
    ".yml",
    ".yaml",
    ".md",
}

ALLOWLIST = {
    # The only active source file allowed to spell deprecated URL vocabulary.
    "frontend/src/shared/navigation/legacyRoutes.ts",
    # The matching test proves old bookmarks still redirect while product code uses current names.
    "frontend/src/shared/navigation/legacyRoutes.test.ts",
    "scripts/check_legacy_terms.py",
    "scripts/check_css_architecture.py",
    "scripts/check_documentation_current.py",
    "scripts/checks/check_legacy_terms.py",
    "scripts/checks/check_css_architecture.py",
    "scripts/checks/check_documentation_current.py",
}

FORBIDDEN_PATTERNS = [
    re.compile(r"--tower", re.IGNORECASE),
    re.compile(r"tower-map\.png", re.IGNORECASE),
    re.compile(r"my-tower", re.IGNORECASE),
    re.compile(r"\btomes?\b", re.IGNORECASE),
    re.compile(r"command-adventures", re.IGNORECASE),
    re.compile(r"Command Adventures?", re.IGNORECASE),
    re.compile(r"Git-it Challenges?", re.IGNORECASE),
    re.compile(r"command_adventures", re.IGNORECASE),
    re.compile(r"battle_catalog", re.IGNORECASE),
    re.compile(r"obsidian-forge", re.IGNORECASE),
    re.compile(r"void-athenaeum", re.IGNORECASE),
    re.compile(r"the-convergence", re.IGNORECASE),
]


def iter_files() -> list[Path]:
    files: list[Path] = []
    for root in SCAN_ROOTS:
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if not path.is_file() or path.suffix.lower() not in TEXT_SUFFIXES:
                continue
            if any(part in {"__pycache__", "node_modules", "dist", "build"} for part in path.parts):
                continue
            files.append(path)
    for path in ROOT_MARKDOWN_FILES:
        if path.exists() and path.is_file():
            files.append(path)
    return files


def main() -> int:
    violations: list[str] = []
    for path in iter_files():
        rel = path.relative_to(ROOT).as_posix()
        text = path.read_text(encoding="utf-8", errors="ignore")
        for lineno, line in enumerate(text.splitlines(), start=1):
            for pattern in FORBIDDEN_PATTERNS:
                if not pattern.search(line):
                    continue
                if rel in ALLOWLIST:
                    break
                violations.append(f"{rel}:{lineno}: {line.strip()}")
                break

    if violations:
        print("Legacy product vocabulary found in active code:", file=sys.stderr)
        for violation in violations:
            print(f"  {violation}", file=sys.stderr)
        print("\nUse current terms: story, story world, level map, lesson, adventure, challenge, companion.", file=sys.stderr)
        return 1

    print("No forbidden legacy product vocabulary found in active code.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
