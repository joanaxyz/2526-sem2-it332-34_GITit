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
            if self.has_option("-a") or self.has_option("--all"):
                args.append("-a")
            if self.has_option("--amend"):
                args.append("--amend")
            if self.has_option("--allow-empty"):
                args.append("--allow-empty")
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
    return any(character.isspace() for character in value) or any(
        character in value for character in "\"';&|<>`$"
    )


class GitCommandParser:
    """Parse student input with shell-like quoting while accepting only git."""

    def parse(self, command: str) -> ParsedGitCommand:
        raw_text = command
        stripped = command.strip()
        if not stripped:
            raise GitCommandParseError("No command entered.")

        try:
            argv = self._split_safely(stripped)
        except GitCommandParseError:
            raise
        except ValueError as exc:
            raise GitCommandParseError("fatal: could not parse command line") from exc

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

    def _split_safely(self, command: str) -> list[str]:
        lexer = shlex.shlex(command, posix=True, punctuation_chars=";&|<>")
        lexer.whitespace_split = True
        tokens = list(lexer)
        forbidden = {";", "&&", "&", "|", "||", ">", ">>", "<", "<<"}
        bad_token = next((token for token in tokens if token in forbidden), None)
        if bad_token:
            raise GitCommandParseError(f"fatal: unsupported shell syntax near '{bad_token}'")
        if any("$(" in token or "`" in token for token in tokens):
            raise GitCommandParseError("fatal: command substitution is not supported")
        return tokens

    def _parse_tail(
        self,
        *,
        subcommand: str,
        tokens: list[str],
    ) -> tuple[dict[str, tuple[str | bool, ...]], list[str], list[str], str | None, list[str]]:
        if subcommand == "commit":
            return self._parse_commit_tail(tokens)
        if subcommand == "init":
            return self._parse_init_tail(tokens)
        if subcommand == "clone":
            return self._parse_clone_tail(tokens)
        if subcommand == "log":
            return self._parse_log_tail(tokens)
        return self._parse_generic_tail(tokens)

    def _append_option(
        self,
        options: dict[str, list[str | bool]],
        option: str,
        value: str | bool = True,
    ) -> None:
        options.setdefault(option, []).append(value)

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
                self._append_option(options, "-m", message)
                normalized.extend(["-m", message])
                index += 2
                continue
            if token.startswith("-am") and token != "-am":
                message = token.removeprefix("-am")
                self._append_option(options, "-a")
                self._append_option(options, "-m", message)
                normalized.extend(["-a", "-m", message])
                index += 1
                continue
            if token == "-am":
                if index + 1 >= len(tokens):
                    raise GitCommandParseError("error: switch `m' requires a value.")
                message = tokens[index + 1]
                self._append_option(options, "-a")
                self._append_option(options, "-m", message)
                normalized.extend(["-a", "-m", message])
                index += 2
                continue
            if token.startswith("--message="):
                message = token.split("=", 1)[1]
                self._append_option(options, "-m", message)
                normalized.extend(["-m", message])
                index += 1
                continue
            if token in {"-a", "--all"}:
                self._append_option(options, token)
                normalized.append(token)
                index += 1
                continue
            if token == "--allow-empty":
                self._append_option(options, token)
                normalized.append(token)
                index += 1
                continue
            if token == "--amend":
                self._append_option(options, token)
                normalized.append(token)
                index += 1
                continue
            if token == "--no-edit":
                self._append_option(options, token)
                normalized.append(token)
                index += 1
                continue
            if token.startswith("-"):
                self._append_option(options, token)
                normalized.append(token)
                index += 1
                continue
            args.append(token)
            pathspecs.append(token)
            normalized.append(token)
            index += 1
        return (
            {key: tuple(value) for key, value in options.items()},
            args,
            pathspecs,
            message,
            normalized,
        )

    def _parse_init_tail(
        self,
        tokens: list[str],
    ) -> tuple[dict[str, tuple[str | bool, ...]], list[str], list[str], str | None, list[str]]:
        options: dict[str, list[str | bool]] = {}
        args: list[str] = []
        pathspecs: list[str] = []
        normalized: list[str] = []
        index = 0
        while index < len(tokens):
            token = tokens[index]
            if token in {"-b", "--initial-branch"}:
                if index + 1 >= len(tokens):
                    raise GitCommandParseError(f"error: option `{token}` requires a value.")
                value = tokens[index + 1]
                self._append_option(options, token, value)
                normalized.extend([token, value])
                index += 2
                continue
            if token.startswith("--initial-branch="):
                value = token.split("=", 1)[1]
                self._append_option(options, "--initial-branch", value)
                normalized.extend(["--initial-branch", value])
                index += 1
                continue
            if token in {"-q", "--quiet"}:
                self._append_option(options, token)
                normalized.append(token)
                index += 1
                continue
            if token.startswith("-"):
                self._append_option(options, token)
                normalized.append(token)
                index += 1
                continue
            args.append(token)
            pathspecs.append(token)
            normalized.append(token)
            index += 1
        return (
            {key: tuple(value) for key, value in options.items()},
            args,
            pathspecs,
            None,
            normalized,
        )

    def _parse_clone_tail(
        self,
        tokens: list[str],
    ) -> tuple[dict[str, tuple[str | bool, ...]], list[str], list[str], str | None, list[str]]:
        options: dict[str, list[str | bool]] = {}
        args: list[str] = []
        pathspecs: list[str] = []
        normalized: list[str] = []
        index = 0
        while index < len(tokens):
            token = tokens[index]
            if token in {"-b", "--branch", "--depth"}:
                if index + 1 >= len(tokens):
                    raise GitCommandParseError(f"error: option `{token}` requires a value.")
                value = tokens[index + 1]
                self._append_option(options, token, value)
                normalized.extend([token, value])
                index += 2
                continue
            if token.startswith("-"):
                self._append_option(options, token)
                normalized.append(token)
                index += 1
                continue
            args.append(token)
            pathspecs.append(token)
            normalized.append(token)
            index += 1
        return (
            {key: tuple(value) for key, value in options.items()},
            args,
            pathspecs,
            None,
            normalized,
        )

    def _parse_log_tail(
        self,
        tokens: list[str],
    ) -> tuple[dict[str, tuple[str | bool, ...]], list[str], list[str], str | None, list[str]]:
        options: dict[str, list[str | bool]] = {}
        args: list[str] = []
        pathspecs: list[str] = []
        normalized: list[str] = []
        index = 0
        while index < len(tokens):
            token = tokens[index]
            if token == "-n":
                if index + 1 >= len(tokens):
                    raise GitCommandParseError("error: option `-n` requires a value.")
                value = tokens[index + 1]
                self._append_option(options, "-n", value)
                normalized.extend(["-n", value])
                index += 2
                continue
            if token.startswith("--max-count="):
                value = token.split("=", 1)[1]
                self._append_option(options, "--max-count", value)
                normalized.extend(["--max-count", value])
                index += 1
                continue
            if token == "--max-count":
                if index + 1 >= len(tokens):
                    raise GitCommandParseError("error: option `--max-count` requires a value.")
                value = tokens[index + 1]
                self._append_option(options, "--max-count", value)
                normalized.extend(["--max-count", value])
                index += 2
                continue
            if token.startswith("-"):
                self._append_option(options, token)
                normalized.append(token)
                index += 1
                continue
            args.append(token)
            pathspecs.append(token)
            normalized.append(token)
            index += 1
        return (
            {key: tuple(value) for key, value in options.items()},
            args,
            pathspecs,
            None,
            normalized,
        )

    def _parse_generic_tail(
        self,
        tokens: list[str],
    ) -> tuple[dict[str, tuple[str | bool, ...]], list[str], list[str], str | None, list[str]]:
        options: dict[str, list[str | bool]] = {}
        args: list[str] = []
        pathspecs: list[str] = []
        after_double_dash = False
        normalized: list[str] = []
        index = 0
        while index < len(tokens):
            token = tokens[index]
            normalized.append(token)
            if token == "--" and not after_double_dash:
                after_double_dash = True
                index += 1
                continue
            if not after_double_dash and token.startswith("-"):
                if "=" in token and token.startswith("--"):
                    option, value = token.split("=", 1)
                    options.setdefault(option, []).append(value)
                    normalized[-1:] = [option, value]
                else:
                    options.setdefault(token, []).append(True)
                index += 1
                continue
            args.append(token)
            pathspecs.append(token)
            index += 1
        return (
            {key: tuple(value) for key, value in options.items()},
            args,
            pathspecs,
            None,
            normalized,
        )


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
        unsupported = [option for option in parsed.options if option not in self.supported_options]
        if unsupported:
            return _unknown_option_message(parsed.subcommand, unsupported[0])
        return self.parser_validation(parsed)


class GitCommandRegistry:
    """Supported Module 1 git command metadata and parser validation."""

    def __init__(self) -> None:
        self._specs = {
            "init": GitCommandSpec(
                "init",
                frozenset({"-b", "--initial-branch", "-q", "--quiet"}),
                diagnostic=False,
                counted=True,
                executor="teaching_state",
                parser_validation=_validate_init,
            ),
            "clone": GitCommandSpec(
                "clone",
                frozenset({"-b", "--branch", "--depth"}),
                diagnostic=False,
                counted=True,
                executor="teaching_state",
                parser_validation=_validate_clone,
            ),
            "status": GitCommandSpec(
                "status",
                frozenset({"-s", "-sb", "--short", "--porcelain", "--ignored"}),
                diagnostic=True,
                counted=False,
                executor="teaching_state",
                parser_validation=_validate_no_path_limit,
            ),
            "add": GitCommandSpec(
                "add",
                frozenset({"-p", "--patch", "-A", "--all", "-u", "--update"}),
                diagnostic=False,
                counted=True,
                executor="teaching_state",
                parser_validation=_validate_add,
            ),
            "commit": GitCommandSpec(
                "commit",
                frozenset({"-m", "-a", "--all", "--amend", "--no-edit"}),
                diagnostic=False,
                counted=True,
                executor="teaching_state",
                parser_validation=_validate_commit,
            ),
            "diff": GitCommandSpec(
                "diff",
                frozenset({"--staged", "--cached", "--name-only"}),
                diagnostic=True,
                counted=False,
                executor="teaching_state",
                parser_validation=_validate_diff,
            ),
            "log": GitCommandSpec(
                "log",
                frozenset({"--oneline", "--graph", "--all", "-n", "--max-count"}),
                diagnostic=True,
                counted=False,
                executor="teaching_state",
                parser_validation=_validate_log,
            ),
            "branch": GitCommandSpec(
                "branch",
                frozenset({"-v"}),
                diagnostic=_branch_is_diagnostic,
                counted=lambda parsed: not _branch_is_diagnostic(parsed),
                executor="teaching_state",
                parser_validation=_validate_branch_list,
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
                frozenset({"--cached", "-r"}),
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
                frozenset({"--name-only"}),
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
            "check-ignore": GitCommandSpec(
                "check-ignore",
                frozenset({"-v"}),
                diagnostic=True,
                counted=False,
                executor="teaching_state",
                parser_validation=_validate_check_ignore,
            ),
            "ls-files": GitCommandSpec(
                "ls-files",
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
    if subcommand == "clone":
        return (
            f"error: unknown option `{option}`. "
            "Module 1 clone supports only -b/--branch and --depth."
        )
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


def _positive_int_option(value: str | bool, option: str) -> str | None:
    if value is True or not str(value).isdigit() or int(str(value)) < 1:
        return f"fatal: invalid {option} value: {value}"
    return None


def _validate_init(parsed: ParsedGitCommand) -> str | None:
    if len(parsed.args) > 1:
        return "usage: git init [-q | --quiet] [--initial-branch=<branch-name>] [<directory>]"
    branch_values = parsed.options.get("-b", ()) + parsed.options.get("--initial-branch", ())
    if len(branch_values) > 1:
        return "error: only one initial branch may be specified"
    if any(value in ("", True) for value in branch_values):
        return "error: option `--initial-branch` requires a value."
    return None


def _validate_clone(parsed: ParsedGitCommand) -> str | None:
    if not parsed.args:
        return "fatal: You must specify a repository to clone."
    if len(parsed.args) > 2:
        return "usage: git clone <repository> [<directory>]"
    branch_values = parsed.options.get("-b", ()) + parsed.options.get("--branch", ())
    if len(branch_values) > 1:
        return "error: only one branch may be specified for clone"
    if any(value in ("", True) for value in branch_values):
        return "error: option `--branch` requires a value."
    depth_values = parsed.options.get("--depth", ())
    if len(depth_values) > 1:
        return "fatal: only one clone depth may be specified"
    if depth_values:
        return _positive_int_option(depth_values[0], "depth")
    return None


def _validate_add(parsed: ParsedGitCommand) -> str | None:
    if parsed.has_option("-p") or parsed.has_option("--patch"):
        return None
    if parsed.has_option("-A") or parsed.has_option("--all"):
        return None
    if parsed.has_option("-u") or parsed.has_option("--update"):
        return None
    if not parsed.pathspecs:
        return "Nothing specified, nothing added."
    return None


def _validate_commit(parsed: ParsedGitCommand) -> str | None:
    if len(parsed.options.get("-m", ())) > 1:
        return "error: only one -m option is supported in this lesson."
    if parsed.has_option("--allow-empty"):
        return _unknown_option_message(parsed.subcommand, "--allow-empty")
    if parsed.has_option("--no-edit") and not parsed.has_option("--amend"):
        return "fatal: options '--no-edit' and '--amend' must be used together"
    if parsed.pathspecs:
        return "fatal: paths with git commit are not supported in this simulator"
    return None


def _validate_diff(parsed: ParsedGitCommand) -> str | None:
    non_path_args = [arg for arg in parsed.args if arg != "HEAD"]
    if "HEAD" in parsed.args and parsed.args[0] != "HEAD":
        return "fatal: ambiguous argument 'HEAD'"
    if parsed.args.count("HEAD") > 1:
        return "fatal: ambiguous argument 'HEAD'"
    if len(non_path_args) > 1:
        return "fatal: only one pathspec is supported for this diff form"
    return None


def _validate_log(parsed: ParsedGitCommand) -> str | None:
    if parsed.args:
        return f"fatal: ambiguous argument '{parsed.args[0]}'"
    limits = [*parsed.options.get("-n", ()), *parsed.options.get("--max-count", ())]
    if len(limits) > 1:
        return "fatal: only one log count option is supported"
    if limits:
        return _positive_int_option(limits[0], "count")
    return None


def _validate_branch_list(parsed: ParsedGitCommand) -> str | None:
    if parsed.args:
        return "fatal: only branch listing is supported in Module 1"
    return None


def _validate_remote(parsed: ParsedGitCommand) -> str | None:
    if parsed.has_option("-v") or parsed.has_option("--verbose"):
        if parsed.args:
            return "usage: git remote [-v]"
        return None
    if not parsed.args:
        return None
    return "Only git remote and git remote -v are supported in Module 1."


def _validate_rm(parsed: ParsedGitCommand) -> str | None:
    if not parsed.pathspecs:
        return "fatal: No pathspec was given."
    if parsed.has_option("-r") and not parsed.has_option("--cached"):
        return "fatal: git rm -r is only supported with --cached in Module 1"
    return None


def _validate_restore(parsed: ParsedGitCommand) -> str | None:
    if not parsed.pathspecs:
        return "fatal: you must specify path(s) to restore"
    return None


def _validate_check_ignore(parsed: ParsedGitCommand) -> str | None:
    if not parsed.has_option("-v"):
        return "usage: git check-ignore -v <path>"
    if len(parsed.pathspecs) != 1:
        return "usage: git check-ignore -v <path>"
    return None


def _branch_is_diagnostic(parsed: ParsedGitCommand) -> bool:
    return not parsed.args and set(parsed.options).issubset({"-v"})


def _remote_is_diagnostic(parsed: ParsedGitCommand) -> bool:
    return not parsed.args and set(parsed.options).issubset({"-v", "--verbose"})
