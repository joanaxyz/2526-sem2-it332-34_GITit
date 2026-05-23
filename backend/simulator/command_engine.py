from __future__ import annotations

import time
from dataclasses import dataclass

from simulator.git_commands import (
    GitCommandParseError,
    GitCommandParser,
    GitCommandRegistry,
    NonGitCommandError,
)
from simulator.pygit2_services import RepositoryStateBridge
from simulator.services import RepositoryStateSimulator, normalize_command


@dataclass(frozen=True)
class CommandExecutionResult:
    processed: bool
    state: dict
    output: str
    normalized_command: str
    exit_code: int | None = None
    diagnostic: bool = False
    elapsed_ms: float = 0.0


class GitCommandExecutor:
    """Execute allowlisted Git commands without arbitrary shell access.

    Student input crosses a typed parser and registry before any state change is
    attempted. The executor currently uses the teaching-state adapter for the
    authored JSON scenarios, with RepositoryStateBridge available for libgit2
    materialization/snapshot boundaries when a command needs repository-backed
    behavior. Unsupported Git subcommands intentionally fail with Git-like
    errors instead of falling through to the system shell.
    """

    def __init__(
        self,
        *,
        parser: GitCommandParser | None = None,
        registry: GitCommandRegistry | None = None,
        simulator: RepositoryStateSimulator | None = None,
        bridge: RepositoryStateBridge | None = None,
    ) -> None:
        self.parser = parser or GitCommandParser()
        self.registry = registry or GitCommandRegistry()
        self.simulator = simulator or RepositoryStateSimulator()
        self.bridge = bridge or RepositoryStateBridge()

    def execute(self, state: dict, command: str) -> CommandExecutionResult:
        start = time.perf_counter()
        normalized_fallback = normalize_command(command)
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

        normalized_state = self.bridge.normalize(state)
        result = self.simulator.process_parsed(normalized_state, parsed, validate=False)
        return self._result(
            processed=result.processed,
            state=result.state,
            output=result.output,
            normalized_command=result.normalized_command,
            exit_code=0 if result.processed else 129,
            diagnostic=spec.is_diagnostic(parsed),
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
    ) -> CommandExecutionResult:
        return CommandExecutionResult(
            processed=processed,
            state=state,
            output=output,
            normalized_command=normalized_command,
            exit_code=exit_code,
            diagnostic=diagnostic,
            elapsed_ms=(time.perf_counter() - start) * 1000,
        )


class GitCommandEngine:
    """Public command engine used by scenario sessions."""

    def __init__(self, *, timeout_seconds: float = 3.0) -> None:
        self.timeout_seconds = timeout_seconds
        self.executor = GitCommandExecutor()

    def process(self, state: dict, command: str) -> CommandExecutionResult:
        return self.executor.execute(state, command)


class Pygit2CommandEngine(GitCommandEngine):
    """Backward-compatible name for existing imports.

    The implementation is no longer a misleading direct pygit2 facade; it is a
    parser/registry/executor pipeline with a libgit2 bridge at the repository
    boundary and no arbitrary command execution.
    """
