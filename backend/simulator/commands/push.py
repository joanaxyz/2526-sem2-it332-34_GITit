from __future__ import annotations

from simulator.commands.base import BaseCommandHandler, CommandOutcome, SimulatorCommandError
from simulator.intents import CommandIntent


class PushCommandHandler(BaseCommandHandler):
    command = "push"

    def apply(self, runtime, state: dict, intent: CommandIntent) -> CommandOutcome:
        operation = intent.first("PushBranch")
        if operation is None:
            raise SimulatorCommandError("fatal: unsupported push operation", exit_code=129)

        remote = str(operation.params.get("remote") or "origin")
        branch = str(operation.params.get("branch") or runtime._head_branch(state) or "")
        if not branch:
            raise SimulatorCommandError(
                "fatal: unable to determine current branch for push",
                exit_code=128,
            )
        if remote not in state.get("remotes", {}):
            raise SimulatorCommandError(f"fatal: '{remote}' does not appear to be a git repository")

        local_tip = state.get("branches", {}).get(branch)
        if not local_tip:
            raise SimulatorCommandError(f"error: src refspec {branch} does not match any", exit_code=1)
        remote_branch = f"{remote}/{branch}"
        state.setdefault("remote_branches", {})[remote_branch] = local_tip
        if operation.params.get("set_upstream"):
            state.setdefault("upstream_tracking", {})[branch] = remote_branch
        runtime._set_operation_metadata(
            state,
            last_push_remote=remote,
            last_push_branch=branch,
            last_push_remote_branch=remote_branch,
            last_push_commit=local_tip,
        )
        return CommandOutcome(
            command="push",
            stdout=f"To {state['remotes'][remote]}\n   {branch} -> {branch}",
        )
