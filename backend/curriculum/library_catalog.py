from __future__ import annotations

from typing import Any

from curriculum.library_commands import (
    COMMAND_KEY_ALWAYS_INCLUDED_SECTION_IDS,
    library_key_for_command,
)
from curriculum.library_data import COMMAND_EFFECTS, SEMANTIC_SECTION_COPY
from curriculum.library_preview import command_preview_syntax_for_command
from curriculum.library_preview_outputs import _sample_output_for_syntax

_READING_COMMANDS = {
    "git status",
    "git log",
    "git show",
    "git diff",
    "git branch",
    "git remote",
    "git reflog",
    "git check-ignore",
    "git merge-base",
    "git ls-files",
}

def _tags_for_module(module: str, base_command: str) -> list[str]:
    tags = ["diagnostic" if base_command in _READING_COMMANDS else "action"]
    tags_by_module = {
        "creating-inspecting-repositories": "setup",
        "tracking-changes-snapshots": "snapshot",
        "branching-switching": "branch",
        "merging-conflicts": "merge",
        "undoing-recovery": "recovery",
        "temporary-work-patches": "patch",
        "remotes-collaboration": "remote",
    }
    module_tag = tags_by_module.get(module)
    if module_tag and module_tag not in tags:
        tags.append(module_tag)
    return tags

def _semantic_items_for_key(key: str, prefix: str) -> list[dict[str, str]]:
    section_ids = COMMAND_KEY_ALWAYS_INCLUDED_SECTION_IDS.get(key, [])
    items = []
    for section_id in section_ids:
        if not section_id.startswith(prefix):
            continue
        copy = SEMANTIC_SECTION_COPY.get(section_id)
        if copy:
            items.append({"id": section_id, **copy})
    return items

def _catalog_library_entries(existing_entries: list[dict[str, Any]] | None = None) -> list[dict[str, Any]]:
    from curriculum.seed_data.command_catalog import COMMAND_CATALOG

    grouped: dict[str, dict[str, Any]] = {}
    for spec in COMMAND_CATALOG:
        base_command = spec["base_command"]
        key = library_key_for_command(base_command)
        grouped.setdefault(
            key,
            {
                "key": key,
                "display_name": spec["title"],
                "canonical_command": spec["usages"][0]["usage_form"],
                "base_command": base_command,
                "aliases": [],
                "summary": spec["summary"],
                "tags": _tags_for_module(spec["module"], base_command),
                "syntax": [],
            },
        )
        entry = grouped[key]
        if spec["summary"] not in entry["summary"]:
            entry["summary"] = f"{entry['summary']} Also: {spec['summary']}"
        for usage in spec.get("usages", []):
            usage_form = usage["usage_form"]
            entry["aliases"].append(usage_form)
            entry["syntax"].append(command_preview_syntax_for_command(usage_form))

    entries = []
    existing_keys = {entry["key"] for entry in (existing_entries or [])}
    for key, entry in grouped.items():
        if key in existing_keys:
            continue
        base_command = entry["base_command"]
        effects, boundaries, watch_for, readiness = COMMAND_EFFECTS.get(
            base_command,
            (
                [f"Applies the repository operation described by `{base_command}`."],
                ["It affects only the state named by the scenario."],
                "Running the command before reading the current repository state.",
                ["Inspect the repository state and scenario values before using it."],
            ),
        )
        entry["aliases"] = list(dict.fromkeys(entry["aliases"]))
        entry["syntax"] = list(dict.fromkeys(s for s in entry["syntax"] if s))
        entry["effects"] = effects
        entry["boundaries"] = boundaries
        entry["watch_for"] = watch_for
        entry["readiness"] = readiness
        entry["terminal_output"] = _sample_output_for_syntax(entry["canonical_command"])
        entry["options"] = _semantic_items_for_key(key, "option")
        entry["arguments"] = _semantic_items_for_key(key, "argument")
        entries.append(entry)
    return entries

