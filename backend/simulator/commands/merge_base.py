from __future__ import annotations

from simulator.commands.base import BaseCommandHandler, CommandOutcome, SimulatorCommandError
from simulator.intents import CommandIntent


class MergeBaseCommandHandler(BaseCommandHandler):
    command = "merge-base"

    def apply(self, runtime, state: dict, intent: CommandIntent) -> CommandOutcome:
        operation = intent.first("InspectMergeBase")
        if operation is None:
            raise SimulatorCommandError("fatal: unsupported merge-base operation", exit_code=129)
        left_ref = str(operation.params.get("left") or "")
        right_ref = str(operation.params.get("right") or "")
        left = self._resolve_ref(runtime, state, left_ref)
        right = self._resolve_ref(runtime, state, right_ref)
        if not left or not right:
            raise SimulatorCommandError("fatal: Not a valid object name", exit_code=128)
        base = self._common_ancestor(runtime, state, left, right)
        if not base:
            raise SimulatorCommandError("fatal: no merge base found", exit_code=1)
        runtime._set_operation_metadata(
            state,
            last_merge_base_left=left_ref,
            last_merge_base_right=right_ref,
            last_merge_base=base,
        )
        return CommandOutcome(command="merge-base", stdout=base)

    def _resolve_ref(self, runtime, state: dict, ref: str) -> str | None:
        if ref in state.get("branches", {}):
            return state["branches"][ref]
        if ref in state.get("remote_branches", {}):
            return state["remote_branches"][ref]
        if runtime._commit_by_id(state, ref):
            return ref
        return None

    def _common_ancestor(self, runtime, state: dict, left: str, right: str) -> str | None:
        left_history = self._history(runtime, state, left)
        right_history = set(self._history(runtime, state, right))
        return next((commit_id for commit_id in left_history if commit_id in right_history), None)

    def _history(self, runtime, state: dict, commit_id: str) -> list[str]:
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
