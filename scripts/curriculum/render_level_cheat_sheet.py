#!/usr/bin/env python3
"""Render LEVEL_CHEAT_SHEET.md: every scenario's variants and answer keys, in play order.

Reads the scenario plan, the scenario banks and the gate composition, so the sheet
always matches what `seed_curriculum` publishes. Run from the repository root:

    python scripts/curriculum/render_level_cheat_sheet.py
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "backend"))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.test_settings")

import django  # noqa: E402

django.setup()

from curriculum.management.commands.seed_curriculum import (  # noqa: E402
    MODULE_1_LEVELS,
    MODULE_2_LEVELS,
    MODULE_3_LEVELS,
    MODULE_4_LEVELS,
)
from curriculum.seed_data.scenario_bank import scenario_for_case  # noqa: E402
from curriculum.seed_data.source.challenge_gates import CHALLENGE_GATES  # noqa: E402
from curriculum.seed_data.source.scenario_plan import MODULE_SCENARIO_PLAN  # noqa: E402

MODULES = {
    1: ("Local Repository Foundations", MODULE_1_LEVELS),
    2: ("Branching and Collaboration", MODULE_2_LEVELS),
    3: ("Conflict Resolution", MODULE_3_LEVELS),
    4: ("Advanced Recovery and History", MODULE_4_LEVELS),
}
TIERS = ("easy", "medium", "hard")


def _sequence(case_id: str) -> str:
    authored = scenario_for_case(case_id)
    edits: dict[int, list[str]] = {}
    for item in authored.get("solution_workspace_files") or []:
        edits.setdefault(int(item.get("after_command_index", 0)), []).append(item["path"])
    steps: list[str] = []
    for index, command in enumerate(authored["solution_commands"]):
        steps += [f"*edit `{path}`*" for path in edits.get(index, [])]
        steps.append(f"`{command}`")
    steps += [
        f"*edit `{path}`*"
        for index, paths in edits.items()
        if index >= len(authored["solution_commands"])
        for path in paths
    ]
    return " → ".join(steps)


def _row(label: str, case_id: str) -> str:
    authored = scenario_for_case(case_id)
    return f"| {label} | `{case_id}` {authored['label']} | {_sequence(case_id)} |"


def render() -> str:
    scenarios = sum(len(w) for tiers in MODULE_SCENARIO_PLAN.values() for w in tiers.values())
    variants = sum(
        len(scenario.variants)
        for tiers in MODULE_SCENARIO_PLAN.values()
        for scenarios_ in tiers.values()
        for scenario in scenarios_
    )
    lines = [
        "# GIT it! — Level answer sheet (STAFF ONLY)",
        "",
        "Generated from the scenario plan by `python scripts/curriculum/render_level_cheat_sheet.py`;",
        "do not edit by hand. "
        f"Covers {len(MODULE_SCENARIO_PLAN)} levels, {scenarios} scenarios and {variants} variants in Modules 1–4,",
        "plus each module's Challenge Gate.",
        "",
        "A tier's scenarios play in order. The first variant listed is a first-time learner's;",
        "a retry rotates within the same scenario. Commands run left to right, and file edits",
        "happen in Project Files at the point shown.",
    ]
    for module, (title, levels) in MODULES.items():
        lines += ["", f"## Module {module} — {title}"]
        for level in levels:
            plan = MODULE_SCENARIO_PLAN.get(level["slug"])
            if not plan:
                continue
            lines += ["", f"### {level['title']}", ""]
            lines += ["| Scenario | Variant | Answer key |", "|---|---|---|"]
            for tier in TIERS:
                for index, scenario in enumerate(plan[tier], start=1):
                    label = f"{tier.title()} {index}. {scenario.title} ({scenario.role})"
                    for position, case_id in enumerate(scenario.variants):
                        lines.append(_row(label if position == 0 else "", case_id))
        gate = CHALLENGE_GATES.get(module)
        if gate:
            lines += ["", f"### Challenge Gate — {gate['title']}", ""]
            lines += ["| Trial | Variant | Answer key |", "|---|---|---|"]
            for difficulty, case_ids in gate["trials"].items():
                for position, case_id in enumerate(case_ids):
                    lines.append(_row(difficulty.title() if position == 0 else "", case_id))
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    output = ROOT / "LEVEL_CHEAT_SHEET.md"
    output.write_text(render(), encoding="utf-8")
    print(f"Wrote {output.relative_to(ROOT)}")
