from __future__ import annotations

import copy

from simulator.commands.base import BaseCommandHandler, CommandOutcome, SimulatorCommandError
from simulator.intents import CommandIntent


class FetchCommandHandler(BaseCommandHandler):
    command = "fetch"

    def apply(self, runtime, state: dict, intent: CommandIntent) -> CommandOutcome:
        operation = intent.first("FetchRemote")
        remote = operation.params.get("remote") or "origin"
        prune = bool(operation.params.get("prune"))
        remotes = state.setdefault("remotes", {})
        if remote not in remotes and not state.get("remote_fixtures") and not state.get("remote_updates"):
            raise SimulatorCommandError(f"fatal: '{remote}' does not appear to be a git repository")

        updates = state.get("remote_updates") or {}
        if isinstance(updates, dict):
            state.setdefault("remote_branches", {}).update(copy.deepcopy(updates))
        runtime._apply_remote_fixture_branches(state)
        runtime._materialize_remote_commits(state)

        pruned: list[str] = []
        if prune:
            stale = list(state.get("remote_stale_branches") or [])
            remote_branches = state.get("remote_branches", {})
            for ref in stale:
                full_ref = ref if "/" in ref else f"{remote}/{ref}"
                if full_ref in remote_branches:
                    del remote_branches[full_ref]
                    pruned.append(full_ref)

        runtime._set_operation_metadata(
            state,
            remote_tracking_updated=True,
            last_fetch_remote=remote,
            fetch_pruned_refs=pruned if pruned else None,
        )
        url = remotes.get(remote, f"https://example.test/{remote}.git")
        prune_lines = "".join(f"\n - [deleted]         (none) -> {ref}" for ref in pruned)
        return CommandOutcome(
            command="fetch",
            stdout=f"From {url}\n * simulated fetch updated {remote}{prune_lines}",
        )
