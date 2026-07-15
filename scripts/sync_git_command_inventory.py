#!/usr/bin/env python3
"""Generate the versioned Git command inventory used by curriculum coverage.

The script intentionally records the Git executable version available to the
repository toolchain. Upgrading Git changes the filename and requires an
explicit coverage review rather than silently changing the curriculum contract.
"""

from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "backend" / "curriculum" / "git_inventory"
CATEGORY_RE = re.compile(r"^[A-Za-z].*Commands|^Interacting with Others$|^User-facing |^Developer-facing |^External commands$")
COMMAND_RE = re.compile(r"^\s{3}([a-z0-9][a-z0-9-]*)\s{2,}(.+)$")


def _run(*args: str) -> str:
    completed = subprocess.run(args, check=True, text=True, capture_output=True)
    return completed.stdout


def collect() -> dict:
    version_text = _run("git", "--version").strip()
    version = version_text.removeprefix("git version ").strip()
    help_text = _run("git", "help", "-a")
    category = "Uncategorized"
    commands: list[dict[str, str]] = []
    for raw in help_text.splitlines():
        line = raw.rstrip()
        stripped = line.strip()
        if not stripped:
            continue
        if not line.startswith(" ") and CATEGORY_RE.search(stripped):
            category = stripped
            continue
        match = COMMAND_RE.match(line)
        if match:
            commands.append(
                {
                    "name": match.group(1),
                    "command": f"git {match.group(1)}",
                    "category": category,
                    "summary": match.group(2).strip(),
                }
            )
    return {
        "schema_version": 1,
        "git_version": version,
        "source": "git help -a",
        "command_count": len(commands),
        "commands": commands,
    }


def main() -> None:
    payload = collect()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    target = OUT_DIR / f"git-{payload['git_version']}.json"
    target.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    (OUT_DIR / "baseline.json").write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(f"Wrote {payload['command_count']} commands to {target.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
