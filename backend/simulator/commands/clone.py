from __future__ import annotations

import copy

from simulator.commands.base import BaseCommandHandler, CommandOutcome, SimulatorCommandError
from simulator.intents import CommandIntent


class CloneCommandHandler(BaseCommandHandler):
    command = "clone"

    def apply(self, runtime, state: dict, intent: CommandIntent) -> CommandOutcome:
        operation = intent.first("CloneRepository")
        params = operation.params if operation else {}
        url = params.get("url")
        if not url:
            raise SimulatorCommandError("Specify a repository URL to clone.")
        if state.get("repository_initialized", True):
            raise SimulatorCommandError(
                "Clone starts a new repository and is only available before initialization."
            )

        remote_name = str(params.get("remote_name") or "origin")
        destination = params.get("destination") or _destination_from_url(str(url))
        requested_branch = params.get("branch")
        depth = params.get("depth")

        state["repository_initialized"] = True
        state["remotes"] = {remote_name: str(url)}
        state["remote_branches"] = {}
        runtime._apply_remote_fixture_branches(state)
        remote_branches = state.setdefault("remote_branches", {})

        default_remote_branch = _default_remote_branch(state, remote_name)
        remote_branches.setdefault(
            default_remote_branch,
            runtime._first_remote_target(remote_branches),
        )
        default_branch = _local_branch_name(default_remote_branch, remote_name)
        selected_branch = str(requested_branch or default_branch)
        selected_remote_branch = f"{remote_name}/{selected_branch}"
        if selected_remote_branch not in remote_branches:
            raise SimulatorCommandError(
                f"fatal: Remote branch {selected_branch!r} was not found in the simulated remote."
            )

        runtime._materialize_remote_commits(state)
        selected_target = remote_branches.get(selected_remote_branch)
        if depth:
            _limit_to_shallow_history(runtime, state, selected_target, int(depth))
            state["remote_branches"] = {selected_remote_branch: selected_target}

        state["branches"] = {selected_branch: selected_target}
        state["head"] = {"type": "branch", "name": selected_branch, "target": selected_target}
        state["upstream_tracking"] = {selected_branch: selected_remote_branch}
        state["working_tree"] = {}
        state["staging"] = {}
        state["conflicts"] = []
        runtime._set_operation_metadata(
            state,
            last_clone_url=str(url),
            last_clone_destination=destination,
            last_clone_branch=selected_branch,
            last_clone_depth=depth,
            last_clone_remote_name=remote_name,
            last_clone_default_branch=default_branch,
            last_clone_shallow=depth is not None,
        )
        return CommandOutcome(
            command="clone",
            details={
                "destination": destination,
                "branch": selected_branch,
                "depth": depth,
                "shallow": depth is not None,
            },
        )


def _destination_from_url(url: str) -> str:
    trimmed = url.rstrip("/")
    tail = trimmed.rsplit("/", 1)[-1]
    if ":" in tail:
        tail = tail.rsplit(":", 1)[-1]
    destination = tail.removesuffix(".git")
    return destination or "repository"


def _default_remote_branch(state: dict, remote_name: str) -> str:
    fixture = state.get("remote_fixtures") or {}
    raw_default = fixture.get("default_branch") if isinstance(fixture, dict) else None
    if raw_default:
        return str(raw_default) if "/" in str(raw_default) else f"{remote_name}/{raw_default}"
    remote_branches = state.get("remote_branches") or {}
    main_ref = f"{remote_name}/main"
    if main_ref in remote_branches:
        return main_ref
    return sorted(remote_branches)[0] if remote_branches else main_ref


def _local_branch_name(remote_branch: str, remote_name: str) -> str:
    prefix = f"{remote_name}/"
    return remote_branch.removeprefix(prefix)


def _limit_to_shallow_history(runtime, state: dict, target: str | None, depth: int) -> None:
    commits_by_id = {commit.get("id"): commit for commit in state.get("commits", [])}
    keep_order: list[str] = []
    current = target
    while current and current in commits_by_id and len(keep_order) < depth:
        keep_order.append(current)
        parents = commits_by_id[current].get("parents") or []
        current = parents[0] if parents else None

    if not keep_order:
        return
    keep = set(keep_order)
    filtered = []
    for commit in state.get("commits", []):
        if commit.get("id") not in keep:
            continue
        copied = copy.deepcopy(commit)
        copied["parents"] = [parent for parent in copied.get("parents", []) if parent in keep]
        filtered.append(copied)
    state["commits"] = filtered
    runtime.normalizer.normalize_commits(state)
