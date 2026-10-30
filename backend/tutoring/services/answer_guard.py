"""Server-side answer-key check for scenario-protected tutor replies.

Answer fields stay on the server: they are never put in a prompt, only compared
against what a provider wrote before the learner sees it.
"""

from __future__ import annotations

import json
import re
import shlex
from dataclasses import dataclass
from functools import cache

from tutoring.services.scenario_recognition import BANK_ROOT, BANKS

# Names every Git explanation uses. They count as answers only inside a command.
_COMMON = frozenset({"main", "master", "origin", "upstream", "head"})
_COMMON_SHAPE = re.compile(r"(?i)head(?:[~^]\d*)*|@\{\w+\}|\d{1,3}")
_SUBCOMMANDS = frozenset(
    {"stash", "remote", "worktree", "submodule", "bisect", "sparse-checkout", "reflog", "rerere"}
)
# Reading the repository is never the answer; changing it is.
_DIAGNOSTIC = frozenset({"status", "log", "show", "diff", "reflog"})
_REPLY_COMMAND = re.compile(r"\bgit[ \t]+[a-z][\w-]*[^\n`]*")


def _tokens(command):
    try:
        return shlex.split(command)
    except ValueError:
        return command.split()


def _operands(command):
    tokens = _tokens(command)
    if not tokens:
        return []
    skip = 1
    if tokens[0] == "git" and len(tokens) > 1:
        skip = 3 if tokens[1] in _SUBCOMMANDS and len(tokens) > 2 else 2
    values = []
    for token in tokens[skip:]:
        if token.startswith("-"):
            if "=" in token:
                values.append(token.split("=", 1)[1])
            continue
        values.append(token)
    return values


def _clean(value):
    value = value.strip().strip("'\"").removeprefix("./").rstrip("/")
    if value in {"", ".", "-", "--"} or (value.startswith("<") and value.endswith(">")):
        return ""
    return value


def shape(command):
    """Family, subcommand and options: the form of a command without its values."""
    tokens = _tokens(command)
    if len(tokens) < 2 or tokens[0] != "git":
        return None
    family = tokens[1]
    sub = tokens[2] if family in _SUBCOMMANDS and len(tokens) > 2 and tokens[2].isalpha() else ""
    flags = frozenset(
        token.split("=", 1)[0] for token in tokens[2:] if token.startswith("-") and token != "--"
    )
    return family, sub, flags


@dataclass(frozen=True)
class AnswerGuard:
    literals: frozenset[str] = frozenset()
    command_literals: frozenset[str] = frozenset()
    recipes: tuple[frozenset, ...] = ()

    def __or__(self, other):
        return AnswerGuard(
            self.literals | other.literals,
            self.command_literals | other.command_literals,
            self.recipes + other.recipes,
        )

    def __bool__(self):
        return bool(self.literals or self.command_literals or self.recipes)

    def leaks(self, reply):
        """Reasons this reply gives away an answer; empty when it only teaches."""
        reasons = []
        for literal in sorted(self.literals):
            if _mentions(reply, literal):
                reasons.append(f"value:{literal}")
        commands = [match.group(0).strip() for match in _REPLY_COMMAND.finditer(reply)]
        for literal in sorted(self.command_literals | self.literals):
            if any(_mentions(command, literal) for command in commands):
                reasons.append(f"command-value:{literal}")
        written = {shape(command) for command in commands} - {None}
        for recipe in self.recipes:
            if len(recipe) >= 2 and recipe <= written:
                reasons.append("solution-sequence")
        return list(dict.fromkeys(reasons))


def _mentions(text, literal):
    return re.search(rf"(?<![\w/.-]){re.escape(literal)}(?![\w/-]|\.\w)", text, re.I) is not None


def guard_from(commands, files=()):
    literals, common = set(), set()
    for command in commands:
        for value in map(_clean, _operands(command)):
            if not value:
                continue
            if len(value) < 3 or value.lower() in _COMMON or _COMMON_SHAPE.fullmatch(value):
                common.add(value)
            else:
                literals.add(value)
    for file in files:
        path = _clean(str(file.get("path", "")))
        if path:
            literals.add(path)
        literals.update(
            line.strip()
            for line in str(file.get("content", "")).splitlines()
            if len(line.strip()) >= 6
        )
    recipe = frozenset(
        found for found in map(shape, commands) if found is not None and found[0] not in _DIAGNOSTIC
    )
    return AnswerGuard(frozenset(literals), frozenset(common), (recipe,) if recipe else ())


@cache
def _bank_answers():
    answers = {}
    for bank in BANKS:
        source = json.loads((BANK_ROOT / f"{bank}.json").read_text(encoding="utf-8"))
        for case_id, row in source.items():
            keys = row.get("answer_key", [])
            commands = list(row.get("solution_commands", [])) + [
                key["command"] for key in keys if key.get("kind") == "command"
            ]
            files = list(row.get("solution_workspace_files", [])) + [
                key for key in keys if key.get("kind") == "file_edit"
            ]
            answers[f"{bank}:{case_id}"] = (tuple(dict.fromkeys(commands)), tuple(files))
    return answers


def guard_for_cases(case_ids):
    guard = AnswerGuard()
    for case_id in case_ids:
        found = _bank_answers().get(case_id)
        if found:
            guard |= guard_from(*found)
    return guard


def guard_for_variant(variant):
    if variant is None:
        return AnswerGuard()
    return guard_from(variant.solution_commands or [], variant.solution_workspace_files or [])
