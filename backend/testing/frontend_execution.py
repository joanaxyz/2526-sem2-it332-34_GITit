from copy import deepcopy

from simulator.services import normalize_command, parse_git_command
from simulator.state import RepositoryStateNormalizer


def frontend_execution_payload(
    command: str,
    next_state: dict,
    *,
    processed: bool = True,
    diagnostic: bool = False,
    output: str = "",
    exit_code: int = 0,
    command_family: str | None = None,
    diagnostic_metadata: list[str] | None = None,
    client_run_revision: int | None = None,
) -> dict:
    """Build the command execution payload the browser now submits."""

    normalized = normalize_command(command)
    parsed = parse_git_command(normalized) or []
    family = command_family if command_family is not None else (parsed[1] if len(parsed) > 1 else "")
    normalized_state = RepositoryStateNormalizer().normalize(deepcopy(next_state))
    payload = {
        "processed": processed,
        "next_state": normalized_state,
        "output": output,
        "normalized_command": normalized,
        "exit_code": exit_code,
        "diagnostic": diagnostic,
        "stdout": output if exit_code == 0 else "",
        "stderr": "" if exit_code == 0 else output,
        "command_family": family,
        "diagnostic_metadata": diagnostic_metadata or [],
    }
    if client_run_revision is not None:
        payload["client_run_revision"] = client_run_revision
    return payload


def unprocessed_git_payload(command: str, state: dict) -> dict:
    return frontend_execution_payload(
        command,
        state,
        processed=False,
        diagnostic=False,
        output=f"git: '{command}' is not a git command.",
        exit_code=129,
        command_family="",
    )


def diagnostic_payload(command: str, state: dict, *, output: str = "") -> dict:
    return frontend_execution_payload(
        command,
        state,
        diagnostic=True,
        output=output,
        diagnostic_metadata=["inspected_status"],
    )
