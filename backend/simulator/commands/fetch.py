from __future__ import annotations

import copy

from simulator.commands.base import BaseCommandHandler, CommandOutcome, SimulatorCommandError
from simulator.intents import CommandIntent


class FetchCommandHandler(BaseCommandHandler):
    command = "fetch"

    def apply(self, runtime, state: dict, intent: CommandIntent) -> CommandOutcome:
        operation = intent.first("FetchRemote")
        remote = operation.params.get("remote") or "origin"
        remotes = state.setdefault("remotes", {})
        if remote not in remotes and not state.get("remote_fixtures"):
            raise SimulatorCommandError(f"fatal: '{remote}' does not appear to be a git repository")

        updates = state.get("remote_updates") or {}
        if isinstance(updates, dict):
            state.setdefault("remote_branches", {}).update(copy.deepcopy(updates))
        runtime._apply_remote_fixture_branches(state)
        runtime._materialize_remote_commits(state)
        runtime._set_operation_metadata(
            state,
            remote_tracking_updated=True,
            last_fetch_remote=remote,
        )
        url = remotes.get(remote, f"https://example.test/{remote}.git")
        return CommandOutcome(command="fetch", stdout=f"From {url}\n * simulated fetch updated {remote}")
