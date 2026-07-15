#!/usr/bin/env python3
"""Reject UI font sizes below the documented 11px minimum."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FRONTEND = ROOT / "frontend" / "src"
CSS_REM = re.compile(r"font-size:\s*(0?\.\d+)rem")
CSS_PX = re.compile(r"font-size:\s*(\d+(?:\.\d+)?)px")
CLASS_REM = re.compile(r"text-\[(0?\.\d+)rem\]")
CLASS_PX = re.compile(r"text-\[(\d+(?:\.\d+)?)px\]")
MIN_PX = 11.0
ROOT_PX = 16.0


def main() -> int:
    violations: list[str] = []
    for path in FRONTEND.rglob("*"):
        if path.suffix not in {".css", ".tsx", ".ts"}:
            continue
        for lineno, line in enumerate(path.read_text(encoding="utf-8", errors="ignore").splitlines(), 1):
            if path.suffix == ".css":
                for match in CSS_REM.finditer(line):
                    value = float(match.group(1)) * ROOT_PX
                    if 0 < value < MIN_PX:
                        violations.append(f"{path.relative_to(ROOT)}:{lineno}: {match.group(0)}")
                for match in CSS_PX.finditer(line):
                    value = float(match.group(1))
                    if 0 < value < MIN_PX:
                        violations.append(f"{path.relative_to(ROOT)}:{lineno}: {match.group(0)}")
            else:
                for match in CLASS_REM.finditer(line):
                    if float(match.group(1)) * ROOT_PX < MIN_PX:
                        violations.append(f"{path.relative_to(ROOT)}:{lineno}: {match.group(0)}")
                for match in CLASS_PX.finditer(line):
                    if float(match.group(1)) < MIN_PX:
                        violations.append(f"{path.relative_to(ROOT)}:{lineno}: {match.group(0)}")
    if violations:
        print("UI typography minimum violations found:")
        for violation in violations:
            print(f"- {violation}")
        return 1
    print("UI typography respects the 11px minimum.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
