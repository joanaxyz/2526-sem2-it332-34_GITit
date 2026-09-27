"""Shell syntax for the workspace terminal.

Mirrors the browser simulator's shell syntax: tokenizing with quotes and ``>``/``>>`` redirection, resolving paths against the terminal's
working directory, and expanding ``*``/``?`` globs against the working copy.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from common.git.workspace_tree import directory_entries, path_kind

_UNSUPPORTED_OPERATORS = {"|", ";", "&", "<", "`"}


class ShellSyntaxError(ValueError):
    pass


@dataclass(frozen=True)
class ShellWord:
    text: str
    glob: bool


@dataclass(frozen=True)
class Redirect:
    append: bool
    target: str


@dataclass(frozen=True)
class ShellInvocation:
    program: str
    args: list[ShellWord]
    redirect: Redirect | None


def tokenize_shell(command: str) -> list[ShellWord | Redirect]:
    """Split a command into words and redirect markers (``Redirect.target`` unset)."""

    tokens: list[ShellWord | Redirect] = []
    text = ""
    glob = False
    in_word = False
    quote: str | None = None
    index = 0

    def end_word() -> None:
        nonlocal text, glob, in_word
        if in_word:
            tokens.append(ShellWord(text=text, glob=glob))
        text, glob, in_word = "", False, False

    while index < len(command):
        char = command[index]
        if quote == "'":
            if char == "'":
                quote = None
            else:
                text += char
            index += 1
            continue
        if char == "$" and command[index + 1 : index + 2] == "(":
            raise ShellSyntaxError("command substitution is not supported")
        if quote == '"':
            following = command[index + 1 : index + 2]
            if char == "\\" and following and following in '"\\$`':
                text += following
                index += 2
                continue
            if char == '"':
                quote = None
            elif char == "`":
                raise ShellSyntaxError("command substitution is not supported")
            else:
                text += char
            index += 1
            continue
        if char == "\\" and index + 1 < len(command):
            text += command[index + 1]
            in_word = True
            index += 2
            continue
        if char in {'"', "'"}:
            quote = char
            in_word = True
            index += 1
            continue
        if char.isspace():
            end_word()
            index += 1
            continue
        if char == ">":
            end_word()
            append = command[index + 1 : index + 2] == ">"
            tokens.append(Redirect(append=append, target=""))
            index += 2 if append else 1
            continue
        if char in _UNSUPPORTED_OPERATORS:
            raise ShellSyntaxError(
                f"syntax error near unexpected token '{char}' (run one command at a time)"
            )
        if char in {"*", "?"}:
            glob = True
        text += char
        in_word = True
        index += 1
    if quote:
        raise ShellSyntaxError(f"unexpected EOF while looking for matching `{quote}'")
    end_word()
    return tokens


def parse_shell_command(command: str) -> ShellInvocation:
    tokens = tokenize_shell(command.strip())
    words: list[ShellWord] = []
    redirect: Redirect | None = None
    index = 0
    while index < len(tokens):
        token = tokens[index]
        if isinstance(token, ShellWord):
            words.append(token)
            index += 1
            continue
        target = tokens[index + 1] if index + 1 < len(tokens) else None
        if not isinstance(target, ShellWord):
            raise ShellSyntaxError("syntax error near unexpected token 'newline'")
        if redirect is not None:
            raise ShellSyntaxError("only one output redirection is supported")
        redirect = Redirect(append=token.append, target=target.text)
        index += 2
    if not words:
        raise ShellSyntaxError("No command entered.")
    return ShellInvocation(program=words[0].text, args=words[1:], redirect=redirect)


def resolve_shell_path(cwd: str, value: str) -> str | None:
    """Project-relative path for ``value`` typed at ``cwd``; ``None`` leaves the project."""

    if not value:
        return None
    base, rest = cwd, value
    if rest == "~" or rest.startswith("~/"):
        base, rest = "", rest[1:]
    elif rest.startswith("/"):
        parts = [part for part in rest.split("/") if part]
        if len(parts) < 2 or parts[0] != "workspace":
            return None
        base, rest = "", "/".join(parts[2:])
    segments = base.split("/") if base else []
    for part in rest.split("/"):
        if not part or part == ".":
            continue
        if part == "..":
            if not segments:
                return None
            segments.pop()
            continue
        segments.append(part)
    return "/".join(segments)


def is_inside_git_directory(path: str) -> bool:
    return path == ".git" or path.startswith(".git/")


def expand_shell_words(state: dict, cwd: str, words: list[ShellWord]) -> list[str]:
    expanded: list[str] = []
    for word in words:
        expanded.extend(_expand_glob(state, cwd, word.text) if word.glob else [word.text])
    return expanded


def _expand_glob(state: dict, cwd: str, pattern: str) -> list[str]:
    if pattern.startswith(("/", "~")):
        return [pattern]
    segments = pattern.split("/")
    candidates: list[tuple[str, str]] = [("", cwd)]
    for index, segment in enumerate(segments):
        last = index == len(segments) - 1
        following: list[tuple[str, str]] = []
        for display, resolved in candidates:
            if not segment:
                following.append((f"{display}/", resolved))
                continue
            if "*" not in segment and "?" not in segment:
                target = resolve_shell_path(resolved, segment)
                if target is not None:
                    following.append((_join_display(display, segment), target))
                continue
            if path_kind(state, resolved) != "directory":
                continue
            matcher = _glob_matcher(segment)
            for entry in directory_entries(state, resolved):
                if not matcher(entry["name"]):
                    continue
                if not last and entry["kind"] != "directory":
                    continue
                following.append((_join_display(display, entry["name"]), entry["path"]))
        candidates = following
    matches = [
        display for display, resolved in candidates if path_kind(state, resolved) is not None
    ]
    return matches or [pattern]


def _join_display(display: str, segment: str) -> str:
    if not display:
        return segment
    return f"{display}{segment}" if display.endswith("/") else f"{display}/{segment}"


def _glob_matcher(segment: str):
    source = "".join(
        "[^/]*" if char == "*" else "[^/]" if char == "?" else re.escape(char) for char in segment
    )
    pattern = re.compile(f"^{source}$", re.DOTALL)
    matches_hidden = segment.startswith(".")
    return lambda name: (matches_hidden or not name.startswith(".")) and bool(pattern.match(name))
