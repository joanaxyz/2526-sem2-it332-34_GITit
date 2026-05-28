from __future__ import annotations

from simulator.commands.base import BaseCommandHandler, CommandOutcome, SimulatorCommandError
from simulator.intents import CommandIntent


class RevListCommandHandler(BaseCommandHandler):
    command = "rev-list"

    def apply(self, runtime, state: dict, intent: CommandIntent) -> CommandOutcome:
        operation = intent.first("InspectRevListCount")
        if operation is None:
            raise SimulatorCommandError("fatal: unsupported rev-list operation", exit_code=129)
        range_expr = str(operation.params.get("range") or "")
        if ".." not in range_expr:
            raise SimulatorCommandError("fatal: rev-list range is required", exit_code=129)
        left_ref, right_ref = range_expr.split("..", 1)
        left = self._resolve_ref(runtime, state, left_ref)
        right = self._resolve_ref(runtime, state, right_ref)
        if not right:
            raise SimulatorCommandError(f"fatal: bad revision '{right_ref}'", exit_code=128)
        right_history = set(self._history(runtime, state, right))
        left_history = set(self._history(runtime, state, left)) if left else set()
        count = len(right_history - left_history)
        runtime._set_operation_metadata(
            state,
            last_rev_list_range=range_expr,
            last_rev_list_count=count,
        )
        return CommandOutcome(command="rev-list", stdout=str(count))

    def _resolve_ref(self, runtime, state: dict, ref: str) -> str | None:
        if ref in state.get("branches", {}):
            return state["branches"][ref]
        if ref in state.get("remote_branches", {}):
            return state["remote_branches"][ref]
        if runtime._commit_by_id(state, ref):
            return ref
        return None

    def _history(self, runtime, state: dict, commit_id: str | None) -> list[str]:
        if not commit_id:
            return []
        commits = {commit["id"]: commit for commit in state.get("commits", [])}
        stack = [commit_id]
        seen: list[str] = []
        while stack:
            current = stack.pop()
            if current in seen or current not in commits:
                continue
            seen.append(current)
            stack.extend(commits[current].get("parents", []))
        return seen
