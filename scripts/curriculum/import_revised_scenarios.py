#!/usr/bin/env python3
"""Compile the revised GIT it! Markdown scenario bank into seed JSON.

The Markdown is an authoring/interchange format.  The generated JSON is the
committed source consumed by Django; this importer is deliberately strict so a
partially parsed document cannot silently replace the production bank.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import textwrap
from pathlib import Path
from typing import Any

SCENARIO_RE = re.compile(
    r"^### (?P<number>\d+\.\d+\.\d+) (?P<title>.+?) · "
    r"(?P<difficulty>Easy|Medium|Hard)\s*$",
    re.MULTILINE,
)
VARIANT_RE = re.compile(r"^\*\*Variant ID:\*\* `([^`]+)`\s*$", re.MULTILINE)
HEADING_RE = re.compile(r"^\*\*(?P<heading>[^*\n]+)\*\*(?P<tail>[^\n]*)$", re.MULTILINE)
ORDERED_STEP_RE = re.compile(r"(?ms)^\d+\.\s+(.*?)(?=^\d+\.\s+|\Z)")
REQUIRED_FILE_RE = re.compile(
    r"(?ms)^`(?P<path>[^`\n]+)`\s*\n+\s*```[^\n]*\n(?P<content>.*?)\n\s*```"
)
COMMAND_PREFIXES = ("git ", "mkdir ", "cd ", "ls", "pwd")
REQUIRED_HEADINGS = (
    "Story",
    "Starting point:",
    "Real-World Context",
    "Your Task",
    "Objective Checklist",
    "Answer Key",
    "Accepted Alternatives",
    "Expected Result",
    "Evaluation",
)
EXPECTED_COUNTS = {"Easy": 99, "Medium": 82, "Hard": 84}


class ImportError(ValueError):
    """Raised when the authoring document does not satisfy the seed contract."""


def _clean_markdown_text(value: str) -> str:
    lines = [line.rstrip().removesuffix("  ").rstrip() for line in value.strip().splitlines()]
    return "\n".join(lines).strip()


def _canonical_heading(raw: str) -> str:
    heading = raw.strip()
    heading = re.sub(r"\s*\(STAFF ONLY[^)]*\)\s*$", "", heading).strip()
    return heading


def _blocks(section: str) -> dict[str, str]:
    matches = list(HEADING_RE.finditer(section))
    blocks: dict[str, str] = {}
    for index, match in enumerate(matches):
        heading = _canonical_heading(match.group("heading"))
        if heading == "Variant ID:":
            continue
        if heading in blocks:
            raise ImportError(f"Duplicate section heading: {heading}")
        end = matches[index + 1].start() if index + 1 < len(matches) else len(section)
        tail = match.group("tail").strip()
        body = section[match.end() : end].strip()
        value = "\n".join(part for part in (tail, body) if part).strip()
        blocks[heading] = value
    return blocks


def _list_items(value: str, *, checklist: bool = False) -> list[str]:
    prefix = r"-\s+\[\s*\]\s+" if checklist else r"-\s+"
    matches = list(re.finditer(rf"(?m)^{prefix}(.+?)(?=\n{prefix}|\Z)", value.strip()))
    return [_clean_markdown_text(match.group(1)) for match in matches]


def _required_files(value: str) -> list[dict[str, str]]:
    return [
        {
            "path": match.group("path").strip(),
            "content": textwrap.dedent(match.group("content")).rstrip("\r\n"),
        }
        for match in REQUIRED_FILE_RE.finditer(value)
    ]


def _answer_key(
    value: str,
) -> tuple[list[dict[str, Any]], list[str], list[dict[str, Any]]]:
    steps: list[dict[str, Any]] = []
    commands: list[str] = []
    workspace_files: list[dict[str, Any]] = []
    for match in ORDERED_STEP_RE.finditer(value):
        raw = match.group(1).strip()
        code = re.match(r"^`([^`]+)`", raw)
        if code and code.group(1).strip().startswith(COMMAND_PREFIXES):
            command = code.group(1).strip()
            commands.append(command)
            steps.append({"kind": "command", "command": command})
            continue

        editor = re.search(
            r"In the simulator's (?:file editor|merge tool), set `([^`]+)` to exactly:",
            raw,
        )
        content = re.search(r"(?ms)```[^\n]*\n(.*?)\n\s*```", raw)
        if editor and content:
            edit = {
                "kind": "file_edit",
                "path": editor.group(1).strip(),
                "content": textwrap.dedent(content.group(1)).rstrip("\r\n"),
                "after_command_index": len(commands),
            }
            steps.append(edit)
            workspace_files.append(
                {
                    "mode": "write",
                    "path": edit["path"],
                    "content": edit["content"],
                    "after_command_index": edit["after_command_index"],
                }
            )
            continue

        raise ImportError(f"Unsupported Answer Key step: {raw.splitlines()[0]!r}")

    if not commands:
        raise ImportError("Answer Key contains no executable command")
    return steps, commands, workspace_files


def _evaluation(value: str) -> tuple[list[str], int, int, list[str]]:
    bullets = _list_items(value)
    budget = re.search(
        r"Minimum counted commands:\s*(\d+)\s*·\s*Maximum counted commands:\s*(\d+)",
        value,
    )
    if not budget:
        raise ImportError("Evaluation is missing a minimum/maximum counted-command budget")
    minimum, maximum = int(budget.group(1)), int(budget.group(2))
    if minimum < 0 or maximum < minimum:
        raise ImportError(f"Invalid counted-command budget: {minimum}..{maximum}")
    seed_notes = [
        item.removeprefix("Seed notes:").strip()
        for item in bullets
        if item.startswith("Seed notes:")
    ]
    return bullets, minimum, maximum, seed_notes


def parse_document(text: str, *, enforce_bank_counts: bool = True) -> dict[str, dict[str, Any]]:
    matches = list(SCENARIO_RE.finditer(text))
    if enforce_bank_counts and len(matches) != 265:
        raise ImportError(f"Expected 265 scenarios, found {len(matches)}")

    scenarios: dict[str, dict[str, Any]] = {}
    difficulty_counts = {difficulty: 0 for difficulty in EXPECTED_COUNTS}
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        section = text[match.end() : end]
        variant_match = VARIANT_RE.search(section)
        if not variant_match:
            raise ImportError(f"Scenario {match.group('number')} is missing Variant ID")
        variant_id = variant_match.group(1).strip()
        if variant_id in scenarios:
            raise ImportError(f"Duplicate Variant ID: {variant_id}")

        blocks = _blocks(section)
        missing = [heading for heading in REQUIRED_HEADINGS if not blocks.get(heading, "").strip()]
        if missing:
            raise ImportError(
                f"Scenario {match.group('number')} ({variant_id}) is missing: {', '.join(missing)}"
            )

        required_files = _required_files(blocks.get("Required resolved file content", ""))
        answer_steps, commands, workspace_files = _answer_key(blocks["Answer Key"])
        required_pairs = {(item["path"], item["content"]) for item in required_files}
        edited_pairs = {(item["path"], item["content"]) for item in workspace_files}
        if required_pairs != edited_pairs:
            raise ImportError(
                f"Scenario {match.group('number')} ({variant_id}) has different required-file "
                "and Answer Key editor content"
            )
        evaluation, minimum, maximum, seed_notes = _evaluation(blocks["Evaluation"])
        difficulty = match.group("difficulty")
        difficulty_counts[difficulty] += 1
        objective_checks = _list_items(blocks["Objective Checklist"], checklist=True)
        if not objective_checks:
            raise ImportError(
                f"Scenario {match.group('number')} ({variant_id}) has no checklist items"
            )
        scenarios[variant_id] = {
            "scenario_number": match.group("number"),
            "difficulty": difficulty.lower(),
            "label": match.group("title").strip(),
            "story": _clean_markdown_text(blocks["Story"]),
            "starting_point": _clean_markdown_text(blocks["Starting point:"]),
            "real_world_context": _clean_markdown_text(blocks["Real-World Context"]),
            "task": _clean_markdown_text(blocks["Your Task"]),
            "required_files": required_files,
            "objective_checks": objective_checks,
            "expected_result": _clean_markdown_text(blocks["Expected Result"]),
            "answer_key": answer_steps,
            "solution_commands": commands,
            "solution_workspace_files": workspace_files,
            "accepted_alternatives": _list_items(blocks["Accepted Alternatives"]),
            "not_accepted": _list_items(blocks.get("Not accepted", "")),
            "evaluation": evaluation,
            "minimum_counted_commands": minimum,
            "maximum_counted_commands": maximum,
            "seed_notes": seed_notes,
        }

    if enforce_bank_counts and difficulty_counts != EXPECTED_COUNTS:
        raise ImportError(
            f"Difficulty counts differ: expected {EXPECTED_COUNTS}, found {difficulty_counts}"
        )
    return scenarios


def render_document(path: Path) -> str:
    scenarios = parse_document(path.read_text(encoding="utf-8-sig"))
    return json.dumps(scenarios, indent=2, ensure_ascii=False) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path, help="Revised Markdown scenario bank")
    parser.add_argument(
        "--output",
        type=Path,
        default=(
            Path(__file__).resolve().parents[2]
            / "backend"
            / "curriculum"
            / "seed_data"
            / "scenario_bank.json"
        ),
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Fail if the output differs instead of rewriting it",
    )
    args = parser.parse_args(argv)

    try:
        rendered = render_document(args.source)
    except (OSError, ImportError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    if args.check:
        current = args.output.read_text(encoding="utf-8") if args.output.exists() else ""
        if current != rendered:
            print(f"error: {args.output} is stale", file=sys.stderr)
            return 1
        print(f"Validated {args.output}")
        return 0

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(rendered, encoding="utf-8")
    print(f"Wrote {len(json.loads(rendered))} scenarios to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
