"""Learner-brief details derived from a scenario's authored evaluation.

``seed_curriculum`` adds these to every seeded variant's brief so a required
commit message the learner cannot infer from repository state is shown.
"""

from __future__ import annotations

import shlex
from typing import Any


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
