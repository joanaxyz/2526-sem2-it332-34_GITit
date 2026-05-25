from __future__ import annotations

import codecs
import re
import shlex
from dataclasses import dataclass

from simulator.git_commands import shell_join


class FileCommandParseError(ValueError):
    """Raised when a supported file-authoring command has invalid syntax."""

    exit_code = 129


class NonFileCommandError(ValueError):
    """Raised when input is not one of the supported file-authoring commands."""

    exit_code = 127

    def __init__(self, command_name: str) -> None:
        self.command_name = command_name
        super().__init__(f"{command_name}: command not found")


@dataclass(frozen=True)
class ParsedFileCommand:
    raw_text: str
    normalized_text: str
    argv: tuple[str, ...]
    command_name: str
    paths: tuple[str, ...] = ()
    path: str | None = None
    content: str = ""
    append: bool = False


class FileCommandParser:
    """Parse the small safe subset of shell file-authoring forms we simulate."""

    supported_commands = frozenset({"touch", "echo", "printf"})

    def parse(self, command: str) -> ParsedFileCommand:
        raw_text = command
        stripped = command.strip()
        if not stripped:
            raise FileCommandParseError("No command entered.")

        try:
            tokens = self._split_safely(stripped)
        except ValueError as exc:
            raise FileCommandParseError("fatal: could not parse command line") from exc
        if not tokens:
            raise FileCommandParseError("No command entered.")
        if tokens[0] not in self.supported_commands:
            raise NonFileCommandError(tokens[0])
        if tokens[0] == "touch":
            return self._parse_touch(raw_text, tokens)
        return self._parse_redirecting_write(raw_text, tokens)

    def _split_safely(self, command: str) -> list[str]:
        lexer = shlex.shlex(command, posix=True, punctuation_chars=";&|<>")
        lexer.whitespace_split = True
        tokens = list(lexer)
        forbidden = {";", "&&", "&", "|", "||", "<", "<<"}
        bad_token = next((token for token in tokens if token in forbidden), None)
        if bad_token:
            raise FileCommandParseError(f"fatal: unsupported shell syntax near '{bad_token}'")
        if any("$(" in token or "`" in token for token in tokens):
            raise FileCommandParseError("fatal: command substitution is not supported")
        return tokens

    def _parse_touch(self, raw_text: str, tokens: list[str]) -> ParsedFileCommand:
        if any(token in {">", ">>"} for token in tokens):
            raise FileCommandParseError("touch: output redirection is not supported")
        args = tokens[1:]
        if not args:
            raise FileCommandParseError("touch: missing file operand")
        if any(arg.startswith("-") for arg in args):
            raise FileCommandParseError("touch: options are not supported")
        paths = tuple(self._normalize_path(path) for path in args)
        normalized = shell_join(("touch", *paths))
        return ParsedFileCommand(
            raw_text=raw_text,
            normalized_text=normalized,
            argv=("touch", *paths),
            command_name="touch",
            paths=paths,
        )

    def _parse_redirecting_write(
        self, raw_text: str, tokens: list[str]
    ) -> ParsedFileCommand:
        redirect_indexes = [index for index, token in enumerate(tokens) if token in {">", ">>"}]
        if len(redirect_indexes) != 1:
            raise FileCommandParseError(
                f"{tokens[0]}: exactly one output redirection is supported"
            )
        redirect_index = redirect_indexes[0]
        redirect = tokens[redirect_index]
        target_tokens = tokens[redirect_index + 1 :]
        if len(target_tokens) != 1:
            raise FileCommandParseError(f"{tokens[0]}: expected exactly one output path")
        source_tokens = tokens[1:redirect_index]
        path = self._normalize_path(target_tokens[0])

        if tokens[0] == "echo":
            decode_escapes = bool(source_tokens and source_tokens[0] == "-e")
            if decode_escapes:
                source_tokens = source_tokens[1:]
            no_newline = bool(source_tokens and source_tokens[0] == "-n")
            if no_newline:
                source_tokens = source_tokens[1:]
            content = " ".join(source_tokens)
            if decode_escapes:
                content = codecs.decode(content, "unicode_escape")
            if not no_newline:
                content += "\n"
        else:
            if not source_tokens:
                raise FileCommandParseError("printf: missing format string")
            content = codecs.decode(" ".join(source_tokens), "unicode_escape")

        normalized_source = " ".join(source_tokens)
        normalized = " ".join(
            part
            for part in (
                tokens[0],
                shell_join((normalized_source,)) if normalized_source else "",
                redirect,
                shell_join((path,)),
            )
            if part
        )
        return ParsedFileCommand(
            raw_text=raw_text,
            normalized_text=normalized,
            argv=(tokens[0], normalized_source, redirect, path),
            command_name=tokens[0],
            path=path,
            content=content,
            append=redirect == ">>",
        )

    def _normalize_path(self, path: str) -> str:
        normalized = path.replace("\\", "/").strip()
        if not normalized:
            raise FileCommandParseError("fatal: empty paths are not supported")
        if re.match(r"^[A-Za-z]:", normalized) or normalized.startswith("/"):
            raise FileCommandParseError("fatal: absolute paths are not supported")
        parts = [part for part in normalized.split("/") if part not in {"", "."}]
        if not parts or any(part == ".." for part in parts):
            raise FileCommandParseError("fatal: parent-directory paths are not supported")
        if parts[0] == ".git":
            raise FileCommandParseError("fatal: writing inside .git is not supported")
        if any(any(char in part for char in "<>|") for part in parts):
            raise FileCommandParseError("fatal: unsupported path characters")
        return "/".join(parts)
