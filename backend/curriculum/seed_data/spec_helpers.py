"""Shared builders for authoring seed_data repository-state specs.

Both the adventure level specs (``adventure_levels.py``) and the challenge
specs (``challenges.py``) author initial repository states and evaluation
specs with these helpers.
"""

from __future__ import annotations

import copy
import shlex
from typing import Any


def commit(
    commit_id: str, message: str, parents: list[str] | None = None, tree: dict | None = None
) -> dict:
    return {"id": commit_id, "message": message, "parents": parents or [], "tree": tree or {}}


def repo(
    *,
    commits: list[dict] | None = None,
    branches: dict | None = None,
    head: str = "main",
    working_tree: dict | None = None,
    staging: dict | None = None,
    conflicts: list[str] | None = None,
    **extra,
) -> dict:
    commits = copy.deepcopy(
        commits or [commit("c0", "Initial project", [], {"README.md": "Project notes"})]
    )
    branches = copy.deepcopy(branches or {head: commits[-1]["id"] if commits else None})
    state = {
        "repository_initialized": True,
        "commits": commits,
        "branches": branches,
        "head": {"type": "branch", "name": head},
        "working_tree": copy.deepcopy(working_tree or {}),
        "staging": copy.deepcopy(staging or {}),
        "conflicts": list(conflicts or []),
    }
    state.update(copy.deepcopy(extra))
    return state


def uninitialized(working_tree: dict | None = None, **extra) -> dict:
    state = {
        "repository_initialized": False,
        "commits": [],
        "branches": {},
        "head": {"type": "none"},
        "working_tree": copy.deepcopy(
            {"README.md": "Project notes"} if working_tree is None else working_tree
        ),
        "staging": {},
        "conflicts": [],
    }
    state.update(copy.deepcopy(extra))
    return state


def ev(
    state_requirements: dict | None = None,
    *,
    required: list[str] | None = None,
    forbidden: list[str] | None = None,
) -> dict:
    return {
        "state_requirements": state_requirements or {},
        "process_requirements": {
            "required_commands": required or [],
            "forbidden_commands": forbidden or [],
        },
        "completion_policy": {"mode": "rules"},
    }


def meta_equals(key: str, value) -> dict:
    return {"type": "operation_metadata_equals", "key": key, "value": value}


def required_commit_message_details(
    solution_commands: list[str] | None,
    evaluation_spec: dict[str, Any] | None,
) -> list[dict[str, str]]:
    """Return copyable commit messages that the evaluator explicitly requires.

    A command family belongs in hints and lessons, not in the story brief. An
    arbitrary message fragment required by ``message_contains`` is different:
    the learner cannot infer it from repository state. Only messages supplied
    to an authored ``git commit -m`` command and checked by the evaluator are
    exposed, so automatic merge/revert messages and unrelated solution tokens
    stay hidden.
    """

    required_fragments = {
        fragment.casefold()
        for fragment in _evaluation_message_fragments(evaluation_spec or {})
        if fragment
    }
    if not required_fragments:
        return []

    messages: list[str] = []
    seen: set[str] = set()
    for command in solution_commands or []:
        for message in _commit_messages_from_command(command):
            normalized = message.casefold()
            if normalized in seen:
                continue
            if not any(fragment in normalized for fragment in required_fragments):
                continue
            seen.add(normalized)
            messages.append(message)

    if len(messages) == 1:
        return [{"label": "Commit message", "value": messages[0]}]
    return [
        {"label": f"Commit message {index}", "value": message}
        for index, message in enumerate(messages, start=1)
    ]


def enrich_context_with_required_details(
    context: dict[str, Any],
    *,
    solution_commands: list[str] | None,
    evaluation_spec: dict[str, Any] | None,
) -> dict[str, Any]:
    """Expose otherwise-uninferable required literals in the learner brief.

    Copy rows intentionally render only their value. The prose therefore names
    the value's role, while the row remains a compact copy target.
    """

    enriched = copy.deepcopy(context)
    required_details = required_commit_message_details(solution_commands, evaluation_spec)
    if not required_details:
        return enriched

    details = list(enriched.get("details") or [])
    seen = {
        str(detail.get("value", "")).strip().casefold()
        for detail in details
        if isinstance(detail, dict) and str(detail.get("value", "")).strip()
    }
    for detail in required_details:
        key = detail["value"].casefold()
        if key not in seen:
            details.append(detail)
            seen.add(key)
    enriched["details"] = details

    prose = f"{enriched.get('story', '')} {enriched.get('task', '')}".casefold()
    if "commit message" not in prose:
        note = (
            "Use the required commit message shown below."
            if len(required_details) == 1
            else "Use the required commit messages shown below in workflow order."
        )
        destination = "task" if str(enriched.get("task", "")).strip() else "story"
        existing = str(enriched.get(destination, "")).strip()
        enriched[destination] = f"{existing} {note}".strip()

    return enriched


def _evaluation_message_fragments(value: Any) -> list[str]:
    fragments: list[str] = []
    if isinstance(value, dict):
        for key, item in value.items():
            if key in {"message_contains", "message_equals"}:
                fragments.extend(_as_text_list(item))
            elif value.get("type") in {
                "latest_commit_message_contains",
                "latest_commit_message_equals",
            } and key == "text":
                fragments.extend(_as_text_list(item))
            fragments.extend(_evaluation_message_fragments(item))
    elif isinstance(value, list):
        for item in value:
            fragments.extend(_evaluation_message_fragments(item))
    return fragments


def _as_text_list(value: Any) -> list[str]:
    values = value if isinstance(value, list) else [value]
    return [str(item).strip() for item in values if str(item).strip()]


def _commit_messages_from_command(command: str) -> list[str]:
    try:
        parts = shlex.split(command)
    except ValueError:
        return []
    if len(parts) < 2 or parts[:2] != ["git", "commit"]:
        return []

    messages: list[str] = []
    index = 2
    while index < len(parts):
        token = parts[index]
        if token in {"-m", "--message"}:
            if index + 1 < len(parts):
                messages.append(parts[index + 1])
                index += 2
                continue
        elif token.startswith("--message="):
            messages.append(token.split("=", 1)[1])
        elif token.startswith("-m") and len(token) > 2:
            messages.append(token[2:])
        elif token.startswith("-") and "m" in token[1:] and token.endswith("m"):
            # Common compact form: ``git commit -am 'message'``.
            if index + 1 < len(parts):
                messages.append(parts[index + 1])
                index += 2
                continue
        index += 1
    return [message.strip() for message in messages if message.strip()]
