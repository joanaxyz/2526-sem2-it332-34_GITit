from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from simulator.intents import CommandIntent

if TYPE_CHECKING:
    from simulator.services import RepositoryStateSimulator


class SimulatorCommandError(ValueError):
    def __init__(self, message: str, *, exit_code: int = 128) -> None:
        self.exit_code = exit_code
        super().__init__(message)


@dataclass
class CommandOutcome:
    command: str
    details: dict[str, Any] = field(default_factory=dict)
    exit_code: int = 0
    stdout: str | None = None
    stderr: str | None = None


class BaseCommandHandler:
    command = ""

    def apply(
        self,
        runtime: RepositoryStateSimulator,
        state: dict,
        intent: CommandIntent,
    ) -> CommandOutcome:
        raise NotImplementedError


def selected_paths(
    runtime: RepositoryStateSimulator,
    state: dict,
    paths: tuple[str, ...] | list[str],
    *,
    include_untracked: bool,
    include_tracked: bool,
) -> list[str]:
    working_tree = state.setdefault("working_tree", {})
    head_tree = runtime._head_tree(state)
    requested = [path for path in paths if path not in {"--"}]
    if not requested or "." in requested:
        requested = sorted(working_tree)

    selected: list[str] = []
    missing: list[str] = []
    for requested_path in requested:
        matches = _matching_paths(working_tree, requested_path)
        if not matches and requested_path in working_tree:
            matches = [requested_path]
        if not matches:
            missing.append(requested_path)
            continue
        for path in matches:
            value = working_tree.get(path)
            status = runtime.normalizer.entry_status(value)
            if status == "ignored":
                continue
            tracked = path in head_tree or status in {"modified", "deleted", "removed"}
            untracked = not tracked or status == "untracked"
            if tracked and include_tracked:
                selected.append(path)
            elif untracked and include_untracked:
                selected.append(path)
    if missing:
        joined = "', '".join(missing)
        raise SimulatorCommandError(
            f"fatal: pathspec '{joined}' did not match any files",
            exit_code=128,
        )
    return sorted(dict.fromkeys(selected))


def _matching_paths(working_tree: dict, requested_path: str) -> list[str]:
    if requested_path.endswith("/"):
        prefix = requested_path
        return sorted(path for path in working_tree if path.startswith(prefix))
    if requested_path in working_tree:
        return [requested_path]
    prefix = f"{requested_path.rstrip('/')}/"
    return sorted(path for path in working_tree if path.startswith(prefix))
