from __future__ import annotations

import time
from dataclasses import dataclass

from simulator.git_commands import (
    GitCommandParseError,
    GitCommandParser,
    GitCommandRegistry,
    NonGitCommandError,
)
from simulator.file_commands import FileCommandParseError, FileCommandParser, NonFileCommandError
from simulator.services import RepositoryStateSimulator, normalize_command
from simulator.state import RepositoryStateNormalizer


@dataclass(frozen=True)
class CommandExecutionResult:
    processed: bool
    state: dict
    output: str
    normalized_command: str
    exit_code: int | None = None
    diagnostic: bool = False
    elapsed_ms: float = 0.0
    stdout: str = ""
    stderr: str = ""
    command_family: str = ""
    diagnostic_metadata: tuple[str, ...] = ()


class GitCommandExecutor:
    """Execute allowlisted Git commands without arbitrary shell access.

    Student input crosses a typed parser and registry before any state change is
    attempted. The executor uses only the in-process teaching-state simulator
    for authored JSON scenarios. Unsupported Git subcommands intentionally fail
    with Git-like errors instead of falling through to the system shell.
    """

    def __init__(
        self,
        *,
        parser: GitCommandParser | None = None,
        file_parser: FileCommandParser | None = None,
        registry: GitCommandRegistry | None = None,
        simulator: RepositoryStateSimulator | None = None,
        normalizer: RepositoryStateNormalizer | None = None,
    ) -> None:
        self.parser = parser or GitCommandParser()
        self.file_parser = file_parser or FileCommandParser()
        self.registry = registry or GitCommandRegistry()
        self.simulator = simulator or RepositoryStateSimulator()
        self.normalizer = normalizer or RepositoryStateNormalizer()

    def execute(self, state: dict, command: str) -> CommandExecutionResult:
        start = time.perf_counter()
        normalized_fallback = normalize_command(command)
        try:
            parsed_file = self.file_parser.parse(command)
        except NonFileCommandError:
            parsed_file = None
        except FileCommandParseError as exc:
            return self._result(
                processed=False,
                state=state,
                output=str(exc),
                normalized_command=normalized_fallback,
                exit_code=exc.exit_code,
                start=start,
                command_family="file",
            )
        if parsed_file is not None:
            normalized_state = self.normalizer.normalize(state)
            result = self.simulator.process_file_parsed(normalized_state, parsed_file)
            return self._result(
                processed=result.processed,
                state=result.state,
                output=result.output,
                normalized_command=result.normalized_command,
                exit_code=result.exit_code,
                stdout=result.stdout,
                stderr=result.stderr,
                command_family=result.command_family,
                diagnostic_metadata=result.diagnostic_metadata,
                start=start,
            )

        try:
            parsed = self.parser.parse(command)
        except NonGitCommandError as exc:
            return self._result(
                processed=False,
                state=state,
                output=str(exc),
                normalized_command=normalized_fallback,
                exit_code=exc.exit_code,
                start=start,
            )
        except GitCommandParseError as exc:
            return self._result(
                processed=False,
                state=state,
                output=str(exc),
                normalized_command=normalized_fallback,
                exit_code=exc.exit_code,
                start=start,
            )

        spec = self.registry.get(parsed.subcommand)
        if spec is None:
            command_name = parsed.subcommand or parsed.normalized_text
            return self._result(
                processed=False,
                state=state,
                output=f"git: '{command_name}' is not a git command. See 'git --help'.",
                normalized_command=parsed.normalized_text,
                exit_code=129,
                start=start,
            )

        validation_error = spec.validate(parsed)
        if validation_error:
            return self._result(
                processed=False,
                state=state,
                output=validation_error,
                normalized_command=parsed.normalized_text,
                exit_code=129,
                diagnostic=spec.is_diagnostic(parsed),
                start=start,
            )

        normalized_state = self.normalizer.normalize(state)
        result = self.simulator.process_parsed(normalized_state, parsed, validate=False)
        return self._result(
            processed=result.processed,
            state=result.state,
            output=result.output,
            normalized_command=result.normalized_command,
            exit_code=result.exit_code,
            diagnostic=spec.is_diagnostic(parsed),
            stdout=result.stdout,
            stderr=result.stderr,
            command_family=result.command_family,
            diagnostic_metadata=result.diagnostic_metadata,
            start=start,
        )

    def _result(
        self,
        *,
        processed: bool,
        state: dict,
        output: str,
        normalized_command: str,
        exit_code: int,
        start: float,
        diagnostic: bool = False,
        stdout: str = "",
        stderr: str = "",
        command_family: str = "",
        diagnostic_metadata: tuple[str, ...] = (),
    ) -> CommandExecutionResult:
        if not stdout and not stderr and exit_code:
            stderr = output
        return CommandExecutionResult(
            processed=processed,
            state=state,
            output=output,
            normalized_command=normalized_command,
            exit_code=exit_code,
            diagnostic=diagnostic,
            elapsed_ms=(time.perf_counter() - start) * 1000,
            stdout=stdout,
            stderr=stderr,
            command_family=command_family,
            diagnostic_metadata=diagnostic_metadata,
        )


class GitCommandEngine:
    """Public command engine used by scenario sessions."""

    def __init__(self, *, timeout_seconds: float = 3.0) -> None:
        self.timeout_seconds = timeout_seconds
        self.executor = GitCommandExecutor()

    def process(self, state: dict, command: str) -> CommandExecutionResult:
        return self.executor.execute(state, command)


class SimulatedGitCommandEngine(GitCommandEngine):
    """Explicit name for the fully simulated command engine."""
