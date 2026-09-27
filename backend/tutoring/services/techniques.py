"""Techniques: ways of using a command that deserve their own introduction.

A command form says *which* command to type (`git add <file>`). A technique is
how its operands are written: several paths at once, `.` for the current
folder, `HEAD~2`, `main..feature`... Detectors read only the shape of a
command, never a particular level, so any seeded or authored solution that
uses a technique triggers its guide.
"""

from __future__ import annotations

import re
import shlex
from collections.abc import Callable
from dataclasses import dataclass

from tutoring.services.forms import FormGuide, command_family

# Families whose operands are all paths, so consecutive calls can be merged
# into one command and several operands mean "several files".
BATCHABLE_FAMILIES = frozenset({"add", "rm", "restore", "check-ignore"})
PATH_FAMILIES = BATCHABLE_FAMILIES | {"reset", "checkout", "diff", "log", "stash", "ls-files", "clean"}
REF_FAMILIES = frozenset({
    "log", "show", "diff", "reset", "revert", "rebase", "switch", "checkout", "branch",
    "cherry-pick", "merge", "tag", "rev-list", "shortlog", "rev-parse", "restore",
})
# Options whose value is a message, name, or count - never a path or ref to teach.
_VALUE_OPTIONS = frozenset({
    "-m", "--message", "-F", "--file", "--author", "--format", "--pretty", "-n", "--max-count",
    "--grep", "-b", "-B", "-c", "-C", "--since", "--until", "--date", "--set-upstream-to",
})
# Options whose value *is* a ref, so ref techniques apply to it.
_REF_VALUE_OPTIONS = frozenset({"--source", "-s", "--onto"})
_DEFAULT_REMOTES = ("origin", "upstream")
# Interactive modes walk one file at a time; never merge their steps.
_INTERACTIVE_OPTIONS = frozenset({"-p", "--patch", "-i", "--interactive", "-e", "--edit"})
_RELATIVE_REF = re.compile(r"[\w./@{}-]+(?:[~^]\d*)+")


@dataclass(frozen=True)
class ParsedCommand:
    family: str
    operands: tuple[str, ...]
    paths_after_separator: tuple[str, ...]
    # Values of options that name a commit (--source=HEAD~1): refs, never paths.
    option_refs: tuple[str, ...] = ()

    @property
    def refs(self) -> tuple[str, ...]:
        return self.operands + self.option_refs


@dataclass(frozen=True)
class Technique:
    key: str
    title: str
    summary: str
    syntax: Callable[[str], str]
    detect: Callable[[ParsedCommand, dict | None], bool]

    @property
    def teaching_key(self) -> str:
        return f"technique:{self.key}"

    def guide(self, family: str) -> FormGuide:
        return FormGuide(
            teaching_key=self.teaching_key,
            family=family,
            usage_form=self.syntax(family),
            label=self.title,
            summary=self.summary,
            technique=self.key,
        )


def parse_command(command: str) -> ParsedCommand | None:
    try:
        tokens = shlex.split(str(command).strip())
    except ValueError:
        tokens = str(command).strip().split()
    family = command_family(command)
    if family is None:
        return None
    rest = tokens[2:]
    if family == "stash" and rest and not rest[0].startswith("-"):
        rest = rest[1:]  # push / apply / pop ...
    operands: list[str] = []
    after: list[str] = []
    option_refs: list[str] = []
    separator = False
    skip_next = False
    ref_next = False
    for token in rest:
        if separator:
            after.append(token)
        elif skip_next:
            skip_next = False
        elif ref_next:
            option_refs.append(token)
            ref_next = False
        elif token == "--":
            separator = True
        elif token.startswith("-"):
            option, _, value = token.partition("=")
            if option in _REF_VALUE_OPTIONS:
                if value:
                    option_refs.append(value)
                else:
                    ref_next = True
            elif option in _VALUE_OPTIONS and not value:
                skip_next = True
        else:
            operands.append(token)
    return ParsedCommand(family, tuple(operands), tuple(after), tuple(option_refs))


def _paths(parsed: ParsedCommand) -> tuple[str, ...]:
    if parsed.family in BATCHABLE_FAMILIES:
        return parsed.operands + parsed.paths_after_separator
    return parsed.paths_after_separator


def _remotes(state: dict | None) -> tuple[str, ...]:
    remotes = (state or {}).get("remotes")
    return tuple(remotes) if isinstance(remotes, dict) and remotes else _DEFAULT_REMOTES


TECHNIQUES: tuple[Technique, ...] = (
    Technique(
        "several-paths",
        "Name several files at once",
        "List more than one path after the command and Git applies it to each of them.",
        lambda family: f"git {family} <path> <path>",
        lambda parsed, _state: parsed.family in BATCHABLE_FAMILIES and len(_paths(parsed)) >= 2,
    ),
    Technique(
        "current-folder",
        "Use . for this folder",
        "A dot means the current folder and everything inside it.",
        lambda family: f"git {family} .",
        lambda parsed, _state: parsed.family in PATH_FAMILIES and "." in _paths(parsed),
    ),
    Technique(
        "path-pattern",
        "Match files with a pattern",
        "Quote a pattern like '*.css' and Git picks every file it fits.",
        lambda family: f"git {family} '<pattern>'",
        lambda parsed, _state: parsed.family in PATH_FAMILIES
        and any("*" in path or "?" in path for path in _paths(parsed)),
    ),
    Technique(
        "path-separator",
        "Mark where file names start",
        "Everything after -- is read as a file path, even if it looks like a branch name.",
        lambda family: f"git {family} -- <path>",
        lambda parsed, _state: parsed.family in PATH_FAMILIES and bool(parsed.paths_after_separator),
    ),
    Technique(
        "relative-commit",
        "Count back from a commit",
        "HEAD~2 is two commits before HEAD, and HEAD^ is the one right before it.",
        lambda family: f"git {family} HEAD~<n>",
        lambda parsed, _state: parsed.family in REF_FAMILIES
        and any(_RELATIVE_REF.fullmatch(ref) for ref in parsed.refs),
    ),
    Technique(
        "commit-range",
        "Name a range of commits",
        "a..b means the commits on b that are not on a.",
        lambda family: f"git {family} <from>..<to>",
        lambda parsed, _state: parsed.family in REF_FAMILIES
        and any(".." in ref and "..." not in ref for ref in parsed.refs),
    ),
    Technique(
        "remote-branch",
        "Use a remote-tracking branch",
        "origin/main is where main was on origin the last time you fetched.",
        lambda family: f"git {family} <remote>/<branch>",
        lambda parsed, state: parsed.family in REF_FAMILIES
        and any(
            ref.startswith(f"{remote}/") for ref in parsed.refs for remote in _remotes(state)
        ),
    ),
    Technique(
        "upstream",
        "Refer to the upstream branch",
        "@{upstream}, or @{u}, is the remote branch your current branch tracks.",
        lambda family: f"git {family} @{{upstream}}",
        lambda parsed, _state: any("@{u" in ref for ref in parsed.refs),
    ),
)
_BY_KEY = {technique.key: technique for technique in TECHNIQUES}


def techniques_in(command: str, state: dict | None = None) -> list[Technique]:
    parsed = parse_command(command)
    if parsed is None:
        return []
    return [technique for technique in TECHNIQUES if technique.detect(parsed, state)]


def technique_used(key: str, command: str, state: dict | None = None) -> bool:
    technique = _BY_KEY.get(key)
    parsed = parse_command(command)
    return bool(technique and parsed and technique.detect(parsed, state))


def batch_command(steps: list[dict], index: int) -> tuple[str, int]:
    """Merge back-to-back solution steps that one multi-path command can do.

    `git add README.md` then `git add app.py` becomes `git add README.md
    app.py`. Only path-only families merge, options must match exactly, and a
    step that needs an authored file edit first ends the batch. Returns the
    command and the index of the last step it covers.
    """

    first = parse_command(steps[index]["command"])
    if first is None or first.family not in BATCHABLE_FAMILIES or not _paths(first):
        return steps[index]["command"], index
    base = _option_signature(steps[index]["command"])
    if _INTERACTIVE_OPTIONS & set(base):
        return steps[index]["command"], index
    paths = list(_paths(first))
    last = index
    for later_index in range(index + 1, len(steps)):
        later = steps[later_index]
        if later.get("diagnostic"):
            continue
        if len(later.get("positions") or []) > 1:
            break  # an authored edit has to happen before this step
        parsed = parse_command(later["command"])
        if parsed is None or parsed.family != first.family or _option_signature(later["command"]) != base:
            break
        new_paths = [path for path in _paths(parsed) if path not in paths]
        if not new_paths:
            break
        paths.extend(new_paths)
        last = later_index
    if last == index:
        return steps[index]["command"], index
    prefix = ["git", first.family, *base]
    separator = ["--"] if first.paths_after_separator else []
    return shlex.join([*prefix, *separator, *paths]), last


def _option_signature(command: str) -> tuple[str, ...]:
    try:
        tokens = shlex.split(str(command).strip())
    except ValueError:
        tokens = str(command).strip().split()
    return tuple(token for token in tokens[2:] if token.startswith("-") and token != "--")
