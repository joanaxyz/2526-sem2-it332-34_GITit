#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from curriculum.seed_data.command_coverage import COMMAND_COVERAGE  # noqa: E402

inventory = json.loads((ROOT / "backend/curriculum/git_inventory/baseline.json").read_text())
inventory_commands = {item["command"] for item in inventory["commands"]}
coverage_commands = {item["command"] for item in COMMAND_COVERAGE}
missing = sorted(inventory_commands - coverage_commands)
extra = sorted(coverage_commands - inventory_commands)
invalid = [
    row["command"]
    for row in COMMAND_COVERAGE
    if row["coverage_level"] not in {"mastery", "practice", "demonstration", "reference"}
]
required_fields = {
    "command", "category", "coverage_level", "introduced_story", "introduced_chapter",
    "adventure_level_slugs", "challenge_slugs", "later_retrieval_slugs", "engine_support",
    "backend_verification", "visual_effect", "platform_constraints", "deprecation_status",
    "replacement_guidance", "official_version", "notes",
}
incomplete = [row.get("command", "<unknown>") for row in COMMAND_COVERAGE if required_fields - row.keys()]
if missing or extra or invalid or incomplete:
    print("Git command coverage check failed.")
    if missing:
        print("Missing:", ", ".join(missing))
    if extra:
        print("Extra:", ", ".join(extra))
    if invalid:
        print("Invalid coverage levels:", ", ".join(invalid))
    if incomplete:
        print("Incomplete records:", ", ".join(incomplete))
    raise SystemExit(1)
print(f"Git command coverage is complete for {len(COMMAND_COVERAGE)} commands (Git {inventory['git_version']}).")
