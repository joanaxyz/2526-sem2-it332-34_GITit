from __future__ import annotations

from dataclasses import dataclass

from simulator.services import RepositoryStateSimulator, normalize_command, parse_git_command


@dataclass(frozen=True)
class CommandExecutionResult:
    processed: bool
    state: dict
    output: str
    normalized_command: str
    exit_code: int | None = None


class Pygit2CommandEngine:
    """Process student Git commands without invoking the system Git executable.

    Scenario state is authored and evaluated as a compact JSON graph. The
    simulator mutates that graph and formats Git-like terminal output; pygit2
    remains the only Git implementation dependency for repository materializing
    and snapshot tests elsewhere in the simulator boundary.
    """

    def __init__(self, *, timeout_seconds: float = 3.0) -> None:
        self.timeout_seconds = timeout_seconds
        self.simulator = RepositoryStateSimulator()

    def process(self, state: dict, command: str) -> CommandExecutionResult:
        normalized = normalize_command(command)
        result = self.simulator.process(state, command)
        return CommandExecutionResult(
            processed=result.processed,
            state=result.state,
            output=self._terminal_output(
                command=normalized,
                simulator_output=result.output,
                processed=result.processed,
            ),
            normalized_command=result.normalized_command or normalized,
            exit_code=0 if result.processed else self._error_exit_code(normalized),
        )

    def _terminal_output(self, *, command: str, simulator_output: str, processed: bool) -> str:
        if not command:
            return simulator_output

        if parse_git_command(command) is None:
            command_name = command.split(maxsplit=1)[0] if command.split() else command
            return f"{command_name}: command not found"

        return simulator_output

    def _error_exit_code(self, command: str) -> int:
        if parse_git_command(command) is None:
            return 127
        return 129
