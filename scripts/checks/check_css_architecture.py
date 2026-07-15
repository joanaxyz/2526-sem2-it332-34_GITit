#!/usr/bin/env python3
"""Guard the CSS/theme cleanup.

Feature CSS should be split into understandable files. Semantic theme tokens must
not regress to product-specific legacy names.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
STYLES = ROOT / "frontend" / "src" / "styles"
MAX_CSS_LINES = 500
FORBIDDEN_PATTERNS = [
    re.compile(r"--tower", re.IGNORECASE),
    re.compile(r"tower-map\.png", re.IGNORECASE),
]


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def main() -> int:
    violations: list[str] = []
    for path in sorted(STYLES.rglob("*.css")):
        text = path.read_text(encoding="utf-8", errors="ignore")
        line_count = len(text.splitlines())
        if line_count > MAX_CSS_LINES:
            violations.append(
                f"{rel(path)}: {line_count} lines; split feature CSS files above {MAX_CSS_LINES} lines"
            )
        for lineno, line in enumerate(text.splitlines(), start=1):
            for pattern in FORBIDDEN_PATTERNS:
                if pattern.search(line):
                    violations.append(f"{rel(path)}:{lineno}: forbidden legacy CSS token/reference: {line.strip()}")
    if violations:
        print("CSS architecture violations found:", file=sys.stderr)
        for violation in violations:
            print(f"  {violation}", file=sys.stderr)
        return 1
    print("CSS architecture looks clean.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
