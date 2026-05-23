from __future__ import annotations

import shlex
from collections.abc import Callable
from dataclasses import dataclass, field


class GitCommandParseError(ValueError):
    """Raised when input looks like a git command but cannot be parsed."""

    exit_code = 129


class NonGitCommandError(ValueError):
    """Raised when input is a shell command outside the allowed git boundary."""

    exit_code = 127

    def __init__(self, command_name: str) -> None:
        self.command_name = command_name
        super().__init__(f"{command_name}: command not found")


COMMAND_ALIASES = {
    "st": "status",
    "ci": "commit",
    "co": "checkout",
    "br": "branch",
}


@dataclass(frozen=True)
class ParsedGitCommand:
    raw_text: str
    normalized_text: str
    argv: tuple[str, ...]
    command_name: str
    subcommand: str
    original_subcommand: str
    args: tuple[str, ...]
    options: dict[str, tuple[str | bool, ...]] = field(default_factory=dict)
    pathspecs: tuple[str, ...] = ()
    message: str | None = None

    @property
    def executor_args(self) -> list[str]:
        """Arguments normalized for the teaching-state command adapters."""
        if self.subcommand == "commit":
            args: list[str] = []
            if self.has_option("--amend"):
                args.append("--amend")
            if self.message is not None:
                args.extend(["-m", self.message])
            args.extend(self.pathspecs)
            return args
        if self.subcommand == "remote" and self.has_option("--verbose"):
            return ["--verbose", *self.args]
        return list(self.argv[2:])

    def has_option(self, option: str) -> bool:
        return option in self.options


def shell_join(parts: list[str] | tuple[str, ...]) -> str:
    return " ".join(shlex.quote(part) if _needs_quote(part) else part for part in parts)


def _needs_quote(value: str) -> bool:
    return any(character.isspace() for character in value) or '"' in value or "'" in value


class GitCommandParser:
    """Parse student input with shell-like quoting while accepting only git."""

    def parse(self, command: str) -> ParsedGitCommand:
        raw_text = command
        stripped = command.strip()
        if not stripped:
            raise GitCommandParseError("No command entered.")

        try:
            argv = shlex.split(stripped, posix=True)
        except ValueError as exc:
            raise GitCommandParseError("The command could not be parsed.") from exc

        if not argv:
            raise GitCommandParseError("No command entered.")
        if argv[0] != "git":
            raise NonGitCommandError(argv[0])
        if len(argv) == 1:
            original_subcommand = ""
            subcommand = ""
        else:
            original_subcommand = argv[1]
            subcommand = COMMAND_ALIASES.get(original_subcommand, original_subcommand)

        options, args, pathspecs, message, normalized_tail = self._parse_tail(
            subcommand=subcommand,
            tokens=argv[2:],
        )
        normalized_argv = ["git"]
        if subcommand:
            normalized_argv.append(subcommand)
        normalized_argv.extend(normalized_tail)
        return ParsedGitCommand(
            raw_text=raw_text,
            normalized_text=shell_join(normalized_argv),
            argv=tuple(["git", subcommand, *normalized_tail] if subcommand else ["git"]),
            command_name="git",
            subcommand=subcommand,
            original_subcommand=original_subcommand,
            args=tuple(args),
            options=options,
            pathspecs=tuple(pathspecs),
            message=message,
        )

    def _parse_tail(
        self,
        *,
        subcommand: str,
        tokens: list[str],
    ) -> tuple[dict[str, tuple[str | bool, ...]], list[str], list[str], str | None, list[str]]:
        if subcommand == "commit":
            return self._parse_commit_tail(tokens)
        return self._parse_generic_tail(tokens)

    def _parse_commit_tail(
        self,
        tokens: list[str],
    ) -> tuple[dict[str, tuple[str | bool, ...]], list[str], list[str], str | None, list[str]]:
        options: dict[str, list[str | bool]] = {}
        args: list[str] = []
        pathspecs: list[str] = []
        normalized: list[str] = []
        message: str | None = None
        index = 0
        while index < len(tokens):
            token = tokens[index]
            if token == "--":
                pathspecs.extend(tokens[index + 1 :])
                normalized.extend(tokens[index:])
                break
            if token in {"-m", "--message"}:
                if index + 1 >= len(tokens):
                    raise GitCommandParseError("error: switch `m' requires a value.")
                message = tokens[index + 1]
                options.setdefault("-m", []).append(message)
                normalized.extend(["-m", message])
                index += 2
                continue
            if token.startswith("--message="):
                message = token.split("=", 1)[1]
                options.setdefault("-m", []).append(message)
                normalized.extend(["-m", message])
                index += 1
                continue
            if token == "--amend":
                options.setdefault("--amend", []).append(True)
                normalized.append(token)
                index += 1
                continue
            if token == "--no-edit":
                options.setdefault("--no-edit", []).append(True)
                normalized.append(token)
                index += 1
                continue
            if token.startswith("-"):
                options.setdefault(token, []).append(True)
                normalized.append(token)
                index += 1
                continue
            args.append(token)
            pathspecs.append(token)
            normalized.append(token)
            index += 1
        return {key: tuple(value) for key, value in options.items()}, args, pathspecs, message, normalized

    def _parse_generic_tail(
        self,
        tokens: list[str],
    ) -> tuple[dict[str, tuple[str | bool, ...]], list[str], list[str], str | None, list[str]]:
        options: dict[str, list[str | bool]] = {}
        args: list[str] = []
        pathspecs: list[str] = []
        after_double_dash = False
        normalized: list[str] = []
        for token in tokens:
            normalized.append(token)
            if token == "--" and not after_double_dash:
                after_double_dash = True
                continue
            if not after_double_dash and token.startswith("-"):
                options.setdefault(token, []).append(True)
                continue
            args.append(token)
            pathspecs.append(token)
        return {key: tuple(value) for key, value in options.items()}, args, pathspecs, None, normalized


ParserValidator = Callable[[ParsedGitCommand], str | None]
DiagnosticPredicate = Callable[[ParsedGitCommand], bool]


@dataclass(frozen=True)
class GitCommandSpec:
    command_name: str
    supported_options: frozenset[str]
    diagnostic: bool | DiagnosticPredicate
    counted: bool | DiagnosticPredicate
    executor: str
    parser_validation: ParserValidator
    output_formatter: str = "git_like"

    def is_diagnostic(self, parsed: ParsedGitCommand) -> bool:
        if callable(self.diagnostic):
            return bool(self.diagnostic(parsed))
        return self.diagnostic

    def is_counted(self, parsed: ParsedGitCommand) -> bool:
        if callable(self.counted):
            return bool(self.counted(parsed))
        return self.counted

    def validate(self, parsed: ParsedGitCommand) -> str | None:
        unsupported = [
            option
            for option in parsed.options
            if option not in self.supported_options
        ]
        if unsupported:
            return _unknown_option_message(parsed.subcommand, unsupported[0])
        return self.parser_validation(parsed)


class GitCommandRegistry:
    """Supported Module 1 git command metadata and parser validation."""

    def __init__(self) -> None:
        self._specs = {
            "init": GitCommandSpec(
                "init",
                frozenset(),
                diagnostic=False,
                counted=True,
                executor="teaching_state",
                parser_validation=_validate_init,
            ),
            "clone": GitCommandSpec(
                "clone",
                frozenset(),
                diagnostic=False,
                counted=True,
                executor="teaching_state",
                parser_validation=_validate_clone,
            ),
            "status": GitCommandSpec(
                "status",
                frozenset({"-s", "--short", "--porcelain"}),
                diagnostic=True,
                counted=False,
                executor="teaching_state",
                parser_validation=_validate_no_path_limit,
            ),
            "add": GitCommandSpec(
                "add",
                frozenset({"-p", "-A"}),
                diagnostic=False,
                counted=True,
                executor="teaching_state",
                parser_validation=_validate_add,
            ),
            "commit": GitCommandSpec(
                "commit",
                frozenset({"-m", "--amend", "--no-edit"}),
                diagnostic=False,
                counted=True,
                executor="teaching_state",
                parser_validation=_validate_commit,
            ),
            "diff": GitCommandSpec(
                "diff",
                frozenset({"--staged", "--cached"}),
                diagnostic=True,
                counted=False,
                executor="teaching_state",
                parser_validation=_validate_no_path_limit,
            ),
            "log": GitCommandSpec(
                "log",
                frozenset({"--oneline", "--graph", "--all"}),
                diagnostic=True,
                counted=False,
                executor="teaching_state",
                parser_validation=_validate_no_path_limit,
            ),
            "branch": GitCommandSpec(
                "branch",
                frozenset({"-v", "-vv", "-a", "--all", "--list", "-d", "-D"}),
                diagnostic=_branch_is_diagnostic,
                counted=lambda parsed: not _branch_is_diagnostic(parsed),
                executor="teaching_state",
                parser_validation=_validate_no_path_limit,
            ),
            "remote": GitCommandSpec(
                "remote",
                frozenset({"-v", "--verbose"}),
                diagnostic=_remote_is_diagnostic,
                counted=lambda parsed: not _remote_is_diagnostic(parsed),
                executor="teaching_state",
                parser_validation=_validate_remote,
            ),
            "rm": GitCommandSpec(
                "rm",
                frozenset({"--cached"}),
                diagnostic=False,
                counted=True,
                executor="teaching_state",
                parser_validation=_validate_rm,
            ),
            "restore": GitCommandSpec(
                "restore",
                frozenset({"--staged"}),
                diagnostic=False,
                counted=True,
                executor="teaching_state",
                parser_validation=_validate_restore,
            ),
            "show": GitCommandSpec(
                "show",
                frozenset(),
                diagnostic=True,
                counted=False,
                executor="teaching_state",
                parser_validation=_validate_at_most_one_arg,
            ),
            "reflog": GitCommandSpec(
                "reflog",
                frozenset(),
                diagnostic=True,
                counted=False,
                executor="teaching_state",
                parser_validation=_validate_no_path_limit,
            ),
        }

    def get(self, command_name: str) -> GitCommandSpec | None:
        return self._specs.get(command_name)

    def require(self, command_name: str) -> GitCommandSpec:
        spec = self.get(command_name)
        if spec is None:
            raise KeyError(command_name)
        return spec

    def is_diagnostic(self, parsed: ParsedGitCommand) -> bool:
        spec = self.get(parsed.subcommand)
        return bool(spec and spec.is_diagnostic(parsed))

    def supported_commands(self) -> tuple[str, ...]:
        return tuple(sorted(self._specs))


def _unknown_option_message(subcommand: str, option: str) -> str:
    if subcommand == "log":
        return f"fatal: unrecognized argument: {option}"
    if subcommand == "branch":
        return f"error: unknown switch `{option}`."
    return f"error: unknown option `{option}`."


def _validate_no_path_limit(parsed: ParsedGitCommand) -> str | None:
    return None


def _validate_at_most_one_arg(parsed: ParsedGitCommand) -> str | None:
    if len(parsed.args) > 1:
        return f"fatal: ambiguous argument '{parsed.args[1]}'"
    return None


def _validate_init(parsed: ParsedGitCommand) -> str | None:
    if len(parsed.args) > 1:
        return "usage: git init [<directory>]"
    return None


def _validate_clone(parsed: ParsedGitCommand) -> str | None:
    if not parsed.args:
        return "fatal: You must specify a repository to clone."
    if len(parsed.args) > 2:
        return "usage: git clone <repository> [<directory>]"
    return None


def _validate_add(parsed: ParsedGitCommand) -> str | None:
    if parsed.has_option("-p"):
        return None
    if parsed.has_option("-A"):
        return None
    if not parsed.pathspecs:
        return "Nothing specified, nothing added."
    return None


def _validate_commit(parsed: ParsedGitCommand) -> str | None:
    if len(parsed.options.get("-m", ())) > 1:
        return "error: only one -m option is supported in this lesson."
    if parsed.has_option("--no-edit") and not parsed.has_option("--amend"):
        return "fatal: options '--no-edit' and '--amend' must be used together"
    return None


def _validate_remote(parsed: ParsedGitCommand) -> str | None:
    if parsed.has_option("-v") or parsed.has_option("--verbose"):
        if parsed.args:
            return "usage: git remote [-v]"
        return None
    if not parsed.args:
        return None
    if parsed.args[0] == "add":
        if len(parsed.args) != 3:
            return "usage: git remote add <name> <url>"
        return None
    return "Only git remote, git remote -v, and git remote add are supported."


def _validate_rm(parsed: ParsedGitCommand) -> str | None:
    if not parsed.has_option("--cached"):
        return "Only git rm --cached <path> is supported."
    if not parsed.pathspecs:
        return "fatal: No pathspec was given."
    return None


def _validate_restore(parsed: ParsedGitCommand) -> str | None:
    if not parsed.pathspecs:
        return "fatal: you must specify path(s) to restore"
    return None


def _branch_is_diagnostic(parsed: ParsedGitCommand) -> bool:
    listing_options = {"-v", "-vv", "-a", "--all", "--list"}
    return not parsed.args and set(parsed.options).issubset(listing_options)


def _remote_is_diagnostic(parsed: ParsedGitCommand) -> bool:
    return not parsed.args and set(parsed.options).issubset({"-v", "--verbose"})
