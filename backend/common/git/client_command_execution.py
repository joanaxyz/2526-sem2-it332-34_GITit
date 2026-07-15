"""Client command-execution boundary for persisted run submissions.

The browser still executes Git commands first so the terminal feels instant. This
module is the backend trust boundary around that client-owned result: it
normalizes the submitted state, validates command metadata that the backend can
check cheaply, and blocks impossible payloads such as diagnostic commands that
mutate repository state.

It intentionally does not shell out to real Git and does not yet replay the full
frontend simulator. Reward-affecting services must still evaluate the verified
state after this boundary.
"""

from __future__ import annotations

import json
from contextlib import nullcontext
from dataclasses import dataclass
from typing import Any

from common.constants import COMMAND_COUNTED, COMMAND_DIAGNOSTIC, COMMAND_UNPROCESSABLE
from common.exceptions import BadRequest, PayloadTooLarge
from common.git.command_transition_verifier import ClientTransitionVerifier
from common.schemas.schema_validation import validate_repository_state_payload
from common.services.performance import timing
from simulator.services import (
    RepositoryStateSimulator,
    is_diagnostic_command,
    normalize_command,
    parse_git_command,
)

# Cap for the serialized repository_state JSON. Stored states are typically a
# few KB; anything near this size means a runaway command sequence, and letting
# it grow bloats the DB row and every subsequent response payload.
MAX_REPOSITORY_STATE_BYTES = 256 * 1024


class CommandCountClassifier:
    def classify(self, *, command: str, processed: bool, diagnostic: bool | None = None) -> tuple[str, int]:
        if not processed:
            # Any command the engine can't process is a wasted turn - a miss that
            # burns budget. Git subcommand typos (`git comit`), misspellings of
            # `git` itself (`gti commit`), and plain non-git input (`ls`,
            # gibberish) all make zero progress toward the target repository
            # state, so each costs a counted command. Only a truly empty
            # submission stays free.
            if not command.strip():
                return COMMAND_UNPROCESSABLE, 0
            return COMMAND_COUNTED, 1
        if diagnostic:
            return COMMAND_DIAGNOSTIC, 0
        return COMMAND_COUNTED, 1


@dataclass(frozen=True)
class ClientCommandResult:
    processed: bool
    state: dict
    output: str
    normalized_command: str
    exit_code: int = 0
    diagnostic: bool = False
    stdout: str = ""
    stderr: str = ""
    command_family: str = ""
    diagnostic_metadata: tuple[str, ...] = ()
    client_run_revision: int | None = None


@dataclass(frozen=True)
class ExecutedCommand:
    """Outcome of accepting one client-submitted command execution payload."""

    previous_state: dict
    next_state: dict
    result: Any
    classification: str
    increment: int
    # True only when the command actually changed repository state. Read-only
    # (diagnostic), unprocessable, and invalid commands leave the state untouched,
    # so callers can skip persisting the full repository_state JSON for them.
    state_mutated: bool


class ClientCommandExecutionService:
    """Validate and normalize the browser-owned command execution payload.

    Fast command processing is preserved because the frontend still simulates
    immediately. The backend then performs cheap, deterministic integrity checks
    before evaluation/persistence:

    - normalized command must match the submitted raw command
    - processed/non-processed state must match whether the command is Git-shaped
    - diagnostic flag must match backend-known read-only command families
    - diagnostic and unprocessed commands may not mutate repository state
    - command_family must match the normalized git subcommand
    """

    def __init__(self) -> None:
        self.state_tools = RepositoryStateSimulator()
        self.transition_verifier = ClientTransitionVerifier()

    def from_payload(
        self,
        *,
        repository_state: dict,
        command: str,
        execution: dict,
        timing_label: str | None = None,
        run_id: int | None = None,
        expected_client_revision: int | None = None,
    ) -> ExecutedCommand:
        tools = self.state_tools

        def span(stage: str):
            return timing(f"{timing_label}.{stage}", run_id=run_id) if timing_label else nullcontext()

        with span("repository_state_clone"):
            validate_repository_state_payload(repository_state, field_name="repository_state")
            previous_state = tools.normalize_state(repository_state)
            validate_repository_state_payload(previous_state, field_name="repository_state")

        processed = self._require_bool(execution, "processed")
        diagnostic = self._require_bool(execution, "diagnostic")

        with span("repository_state_normalize"):
            if processed and not diagnostic:
                raw_next_state = (
                    execution.get("next_state")
                    if "next_state" in execution and execution.get("next_state") is not None
                    else previous_state
                )
                validate_repository_state_payload(raw_next_state, field_name="execution.next_state")
                next_state = tools.normalize_state(raw_next_state)
                validate_repository_state_payload(next_state, field_name="execution.next_state")
            else:
                # Read-only diagnostics (git status/log) and unprocessable input
                # (misspells like `git sjfs`, non-git commands) cannot change the
                # repository, so the authoritative next state is the unchanged
                # previous state. We deliberately ignore the browser's submitted
                # next_state here: response snapshots fill default empties ({}, [],
                # False) that a freshly persisted initial_state omits, so the
                # client's local copy legitimately differs from the stored state
                # before the first mutating command. Trusting it would spuriously
                # trip the "cannot mutate repository state" guard and surface a
                # false "Command failed" instead of recording the miss.
                next_state = previous_state

        expected_normalized = normalize_command(command)
        submitted_normalized = str(execution.get("normalized_command") or command).strip()
        client_run_revision = self._parse_client_run_revision(execution.get("client_run_revision"))
        result = ClientCommandResult(
            processed=processed,
            state=next_state,
            output=str(execution.get("output") or ""),
            normalized_command=submitted_normalized,
            exit_code=self._parse_exit_code(execution.get("exit_code")),
            diagnostic=diagnostic,
            stdout=str(execution.get("stdout") or ""),
            stderr=str(execution.get("stderr") or ""),
            command_family=str(execution.get("command_family") or ""),
            diagnostic_metadata=tuple(str(item) for item in (execution.get("diagnostic_metadata") or ())),
            client_run_revision=client_run_revision,
        )

        self._validate_payload_integrity(
            command=command,
            previous_state=previous_state,
            next_state=next_state,
            expected_normalized=expected_normalized,
            result=result,
            expected_client_revision=expected_client_revision,
        )

        # Repository state is stored as an unbounded JSON column and shipped in
        # every payload; a pathological command sequence (mass file/commit
        # creation) must not grow it past what a row and response can carry.
        if result.processed and not result.diagnostic:
            self.transition_verifier.verify(
                command=expected_normalized,
                previous_state=previous_state,
                next_state=next_state,
                command_family=result.command_family,
                exit_code=result.exit_code,
            )
            state_size = len(json.dumps(next_state, separators=(",", ":"), default=str))
            if state_size > MAX_REPOSITORY_STATE_BYTES:
                raise PayloadTooLarge(
                    "This scenario's repository grew too large to continue. "
                    "Retry the run to start from a clean state."
                )

        classification, increment = CommandCountClassifier().classify(
            command=command,
            processed=result.processed,
            diagnostic=result.diagnostic,
        )
        return ExecutedCommand(
            previous_state=previous_state,
            next_state=next_state,
            result=result,
            classification=classification,
            increment=increment,
            # Only processed, non-diagnostic commands write to the repository.
            state_mutated=result.processed and not result.diagnostic,
        )

    @staticmethod
    def _require_bool(execution: dict, field: str) -> bool:
        value = execution.get(field)
        if not isinstance(value, bool):
            raise BadRequest(f"execution.{field} must be a boolean.")
        return value

    @staticmethod
    def _parse_exit_code(value: Any) -> int:
        if isinstance(value, bool) or not isinstance(value, int):
            raise BadRequest("execution.exit_code must be an integer.")
        if value < -255 or value > 255:
            raise BadRequest("execution.exit_code is outside the supported range.")
        return value

    def _parse_client_run_revision(self, value: Any) -> int | None:
        if value is None or value == "":
            return None
        try:
            revision = int(value)
        except (TypeError, ValueError):
            raise BadRequest("execution.client_run_revision must be an integer.") from None
        if revision < 0:
            raise BadRequest("execution.client_run_revision must be non-negative.")
        return revision

    def _validate_payload_integrity(
        self,
        *,
        command: str,
        previous_state: dict,
        next_state: dict,
        expected_normalized: str,
        result: ClientCommandResult,
        expected_client_revision: int | None = None,
    ) -> None:
        if result.normalized_command != expected_normalized:
            raise BadRequest("execution.normalized_command does not match the submitted command.")

        if expected_client_revision is not None and result.client_run_revision != expected_client_revision:
            raise BadRequest("execution.client_run_revision is stale for this run.")

        parsed = parse_git_command(expected_normalized)
        is_git_command = parsed is not None
        is_cd_command = expected_normalized == "cd" or expected_normalized.startswith("cd ")
        expected_family = "cd" if is_cd_command else (parsed[1] if parsed and len(parsed) > 1 else "")
        expected_diagnostic = is_cd_command or is_diagnostic_command(expected_normalized)

        if result.processed and not (is_git_command or is_cd_command):
            raise BadRequest("Only Git commands and supported shell no-ops may be submitted as processed executions.")

        if result.diagnostic and not expected_diagnostic:
            raise BadRequest("execution.diagnostic does not match the submitted command.")
        if result.processed and expected_diagnostic and not result.diagnostic:
            raise BadRequest("execution.diagnostic does not match the submitted command.")

        if result.processed and result.command_family != expected_family:
            raise BadRequest("execution.command_family does not match the submitted command.")
        if not result.processed:
            if not (is_git_command or is_cd_command) and result.command_family:
                raise BadRequest("Non-Git executions must not include a command family.")
            if (is_git_command or is_cd_command) and result.command_family not in {"", expected_family}:
                raise BadRequest("execution.command_family does not match the submitted command.")

        # Unprocessed and diagnostic commands can never mutate the repository:
        # `from_payload` pins their next_state to the previous state and ignores
        # the browser's submitted next_state entirely, so no hash comparison is
        # needed (and comparing the client's drift-prone snapshot here would only
        # produce false rejections). Only processed, non-diagnostic commands carry
        # a real transition, verified against previous_state by the transition
        # verifier in `from_payload`.

