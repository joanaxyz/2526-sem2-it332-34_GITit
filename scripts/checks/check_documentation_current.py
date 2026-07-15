#!/usr/bin/env python3
"""Validate that root documentation describes the current architecture.

The project intentionally does not use a /docs tree. This guard keeps the root
markdown files useful and prevents stale refactor-era labels from becoming a
second source of truth.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

REQUIRED_FILES = [
    "README.md",
    "ARCHITECTURE.md",
    "CLAUDE.md",
    "CONTENT_AUTHORING_GUIDE.md",
    "CURRICULUM_AUTHORING_PLAN.md",
    "DESIGN.md",
    "PRODUCT.md",
]

REQUIRED_ARCHITECTURE_SECTIONS = [
    "## Domain Glossary",
    "## Layer Ownership",
    "## Frontend Import Rules",
    "## Normalized Frontend Shape",
    "## Backend Rules",
    "## Command Execution Boundary",
    "## API Contract",
    "## StoryWorld System",
    "## Generated Curriculum Targets",
    "## Testing Strategy",
    "## Compatibility",
    "## CI Guards",
]

REQUIRED_README_SNIPPETS = [
    "frontend/src/shared/navigation/legacyRoutes.ts",
    "python scripts/check_api_contract.py",
    "python scripts/check_documentation_current.py",
    "npm run api:type-adoption-check",
]

STALE_DOC_SNIPPETS = [
    "Command Adventure",
    "Command Adventures",
    "Git-it Challenge",
    "Git-it Challenges",
    "command_adventures",
    "backend/command_adventures",
    "mastery-target-one-level-per-form",
    "legacy single-check behavior",
    "features/track-map/select/",
    "features/track-map/viewer/",
    "Tr" + "ack" + "` —",
    "Th" + "eme" + "` —",
]


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def main() -> int:
    violations: list[str] = []

    docs_dir = ROOT / "docs"
    if docs_dir.exists():
        violations.append("/docs must remain absent; root markdown files are the documentation source.")

    for rel in REQUIRED_FILES:
        path = ROOT / rel
        if not path.exists():
            violations.append(f"Missing required root documentation file: {rel}")
            continue
        if not read(path).strip():
            violations.append(f"Root documentation file is empty: {rel}")

    architecture = read(ROOT / "ARCHITECTURE.md") if (ROOT / "ARCHITECTURE.md").exists() else ""
    for section in REQUIRED_ARCHITECTURE_SECTIONS:
        if section not in architecture:
            violations.append(f"ARCHITECTURE.md missing section: {section}")

    readme = read(ROOT / "README.md") if (ROOT / "README.md").exists() else ""
    for snippet in REQUIRED_README_SNIPPETS:
        if snippet not in readme:
            violations.append(f"README.md missing current setup/check snippet: {snippet}")

    for rel in ["README.md", "ARCHITECTURE.md", "CLAUDE.md", "CONTENT_AUTHORING_GUIDE.md", "CURRICULUM_AUTHORING_PLAN.md"]:
        path = ROOT / rel
        if not path.exists():
            continue
        text = read(path)
        for stale in STALE_DOC_SNIPPETS:
            if stale in text:
                violations.append(f"{rel} contains stale documentation label/path: {stale}")

    if violations:
        print("Documentation currentness check failed:", file=sys.stderr)
        for violation in violations:
            print(f"  {violation}", file=sys.stderr)
        return 1

    print("Root documentation is current and /docs is absent.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
