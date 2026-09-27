"""Rewrite git pathspecs typed in a subfolder to project-root paths.

Mirrors the browser simulator's pathspec rewrite. The simulator models paths
from the project root, so ``git add app.ts`` typed inside ``src``
is verified as ``git add src/app.ts``. Positional arguments are paths for the
families below; for every other family only arguments after ``--`` are.
"""

from __future__ import annotations

import shlex

from common.git.shell_syntax import resolve_shell_path

_ALIASES = {"st": "status", "ci": "commit", "co": "checkout", "br": "branch"}
_PATH_ARGUMENT_FAMILIES = frozenset({"add", "rm", "restore", "commit", "check-ignore", "ls-files"})
_VALUE_OPTIONS = {
    "commit": frozenset(
        {
            "-m",
            "--message",
            "-am",
            "-F",
            "--file",
            "-C",
            "-c",
            "--author",
            "--date",
            "--fixup",
            "--squash",
        }
    ),
    "restore": frozenset({"-s", "--source"}),
}


def rebase_git_pathspecs(command: str, cwd: str) -> str:
    if not cwd:
        return command
    try:
        words = shlex.split(command.strip())
    except ValueError:
        return command
    if len(words) < 3 or words[0] != "git":
        return command

    family = _ALIASES.get(words[1], words[1])
    value_options = _VALUE_OPTIONS.get(family, frozenset())
    path_arguments = family in _PATH_ARGUMENT_FAMILIES
    rebased = words[:2]
    positional_only = False
    index = 2
    while index < len(words):
        word = words[index]
        if not positional_only and word == "--":
            positional_only = True
            rebased.append(word)
        elif not positional_only and word.startswith("-") and word != "-":
            rebased.append(word)
            if word in value_options and index + 1 < len(words):
                rebased.append(words[index + 1])
                index += 1
        else:
            rebased.append(_rebase_path(word, cwd) if positional_only or path_arguments else word)
        index += 1
    if rebased == words:
        return command
    return " ".join(shlex.quote(word) if _needs_quote(word) else word for word in rebased)


def _rebase_path(path: str, cwd: str) -> str:
    if path.startswith(":"):
        return path
    resolved = resolve_shell_path(cwd, path)
    if resolved is None:
        return path
    return resolved or "."


def _needs_quote(word: str) -> bool:
    return not word or any(char.isspace() or char in "\"';&|<>`$" for char in word)
