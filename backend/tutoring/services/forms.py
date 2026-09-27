from __future__ import annotations

import re
import shlex
from collections.abc import Iterable
from dataclasses import dataclass

from curriculum.models import CommandForm
from simulator.services import normalize_command

_PLACEHOLDER = re.compile(r"(<[^>]+>|\{[^}]+\})")
_VARIADIC_PLACEHOLDER = re.compile(r"<[^>]+\.\.\.>")

# Git accepts several common long/short spellings.  Command-form matching is
# teaching identity, not grading, so normalize only spelling aliases that keep
# the same semantics.
_OPTION_ALIASES = {
    "init": {"--initial-branch": "-b", "--quiet": "-q"},
    "clone": {"--branch": "-b"},
    "status": {"--short": "-s"},
    "config": {"-l": "--list"},
    "log": {"--max-count": "-n"},
    "diff": {"--cached": "--staged"},
    "add": {"--all": "-A", "--update": "-u", "--patch": "-p"},
    "commit": {"--all": "-a", "--message": "-m", "--gpg-sign": "-S"},
    "rm": {"--recursive": "-r"},
    "check-ignore": {"--verbose": "-v"},
    "restore": {"--patch": "-p"},
    "branch": {"--verbose": "-v", "--delete": "-d"},
    "switch": {"--create": "-c"},
    "checkout": {"--branch": "-b"},
    "revert": {"--mainline": "-m"},
    "shortlog": {"--summary": "-s", "--numbered": "-n"},
    "tag": {"--annotate": "-a", "--delete": "-d", "--sign": "-s", "--message": "-m"},
}

# Families whose first operand is a subcommand word, not a value.
_SUBCOMMAND_FAMILIES = frozenset({
    "stash", "remote", "worktree", "submodule", "bisect", "sparse-checkout", "notes",
    "reflog", "lfs", "maintenance", "rerere",
})

# Learners who completed the first introductions before teaching keys became
# syntax-based keep those completions.
_LEGACY_KEYS = {
    "git init": "git-init/current-directory",
    "git add <file>": "git-add/file",
    "git add <path>...": "git-add/file",
    "git commit -m <message>": "git-commit/message",
}


@dataclass(frozen=True)
class FormGuide:
    """One command form, identified by its syntax rather than a seed slug."""

    teaching_key: str
    family: str
    usage_form: str
    label: str
    summary: str

    def payload(self) -> dict:
        return {
            "teaching_key": self.teaching_key,
            "usage_form": self.usage_form,
            "label": self.label,
            "summary": self.summary,
        }


def teaching_key_for_usage(usage_form: str) -> str:
    """Seed-independent identity: the same syntax is the same lesson everywhere."""

    usage = " ".join(str(usage_form).split())
    return _LEGACY_KEYS.get(usage, f"form:{usage}")[:160]


def guide_for_form(form: CommandForm) -> FormGuide | None:
    family = command_family(form.usage_form)
    if family is None:
        return None
    return FormGuide(
        teaching_key=teaching_key_for_usage(form.usage_form),
        family=family,
        usage_form=" ".join(form.usage_form.split()),
        label=form.label,
        summary=form.summary or form.command_skill.summary,
    )


def resolve_form(command: str, preferred: Iterable[CommandForm] = ()) -> FormGuide | None:
    """The authored form a concrete command is an instance of.

    Forms attached to the current wave win over the wider catalog, and a more
    specific syntax (``git add .``) wins over a generic one (``git add <file>``).
    Commands with no authored form still get a syntax shape derived from the
    command itself, so any seeded solution can be taught.
    """

    family = command_family(command)
    if family is None:
        return None
    preferred = [form for form in preferred if command_family(form.usage_form) == family]
    catalog = CommandForm.objects.filter(
        is_published=True, usage_form__startswith=f"git {family}"
    ).select_related("command_skill")
    for pool in (preferred, catalog):
        matches = [form for form in pool if command_matches_form(command, form.usage_form)]
        if matches:
            best = max(matches, key=lambda form: (form.is_playable, _specificity(form.usage_form)))
            return guide_for_form(best)
    shape = _command_shape(command)
    return FormGuide(
        teaching_key=teaching_key_for_usage(shape),
        family=family,
        usage_form=shape,
        label=f"git {family}",
        summary="",
    )


def command_family(command: str) -> str | None:
    tokens = _tokens(command)
    if len(tokens) < 2 or tokens[0] != "git":
        return None
    return tokens[1]


def command_matches_form(command: str, usage_form: str) -> bool:
    """Match an executed command to an authored usage shape.

    Placeholders and optional bracketed operands are understood, so this works
    for the complete command catalog rather than a hand-written allowlist.  It
    intentionally answers only "which form was used"; the normal evaluator
    remains authoritative for whether that route solves the level.
    """

    actual = _canonical_tokens(normalize_command(command))
    pattern = _canonical_tokens(usage_form, pattern=True)
    if not actual or not pattern:
        return False
    return _match_tokens(actual, pattern, 0, 0)


def _specificity(usage_form: str) -> tuple[int, int, int]:
    tokens = _canonical_tokens(usage_form, pattern=True)
    literal = sum(1 for value, optional in tokens if not optional and not _PLACEHOLDER.search(value))
    optional = sum(1 for _, is_optional in tokens if is_optional)
    variadic = sum(1 for value, _ in tokens if _VARIADIC_PLACEHOLDER.search(value))
    return literal, -optional, -variadic


def _command_shape(command: str) -> str:
    tokens = _tokens(normalize_command(command))
    shape = tokens[:2]
    rest = tokens[2:]
    if len(tokens) > 1 and tokens[1] in _SUBCOMMAND_FAMILIES and rest and not rest[0].startswith("-"):
        shape.append(rest.pop(0))
    for token in rest:
        if token.startswith("-") and token != "--":
            shape.append(token.split("=", 1)[0])
        elif token == "--":
            shape.append(token)
        elif not shape or shape[-1] != "<value>":
            shape.append("<value>")
    return " ".join(shape)


def _tokens(command: str) -> list[str]:
    # Brackets in usage forms mark optional operands; shlex leaves them intact.
    try:
        return shlex.split(str(command).strip())
    except ValueError:
        return str(command).strip().split()


def _canonical_tokens(command: str, *, pattern: bool = False) -> list[tuple[str, bool]]:
    raw = _tokens(command)
    if len(raw) < 2:
        return []
    family = raw[1]
    aliases = _OPTION_ALIASES.get(family, {})
    result: list[tuple[str, bool]] = []
    for token in raw:
        optional = pattern and token.startswith("[") and token.endswith("]")
        value = token[1:-1] if optional else token
        option, separator, attached = value.partition("=")
        canonical = aliases.get(option, option)
        if separator and option in aliases:
            result.append((canonical, optional))
            result.append((attached, optional))
        else:
            result.append((aliases.get(value, value), optional))
    return result


def _token_matches(actual: str, pattern: str) -> bool:
    if not _PLACEHOLDER.search(pattern):
        return actual == pattern
    pieces = []
    cursor = 0
    for match in _PLACEHOLDER.finditer(pattern):
        pieces.append(re.escape(pattern[cursor : match.start()]))
        pieces.append(r".+")
        cursor = match.end()
    pieces.append(re.escape(pattern[cursor:]))
    return bool(re.fullmatch("".join(pieces), actual))


def _match_tokens(
    actual: list[tuple[str, bool]],
    pattern: list[tuple[str, bool]],
    actual_index: int,
    pattern_index: int,
) -> bool:
    if pattern_index == len(pattern):
        return actual_index == len(actual)
    expected, optional = pattern[pattern_index]
    if optional and _match_tokens(actual, pattern, actual_index, pattern_index + 1):
        return True
    if _VARIADIC_PLACEHOLDER.fullmatch(expected):
        return any(
            _match_tokens(actual, pattern, end, pattern_index + 1)
            for end in range(actual_index + 1, len(actual) + 1)
        )
    if actual_index == len(actual):
        return False
    value = actual[actual_index][0]
    if not _token_matches(value, expected):
        return False
    return _match_tokens(actual, pattern, actual_index + 1, pattern_index + 1)
