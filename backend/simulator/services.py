import copy
import hashlib
import json
import shlex
from dataclasses import dataclass

READ_ONLY_PREFIXES = (
    "git status",
    "git log",
    "git branch",
    "git diff",
    "git show",
)


@dataclass(frozen=True)
class SimulatorResult:
    processed: bool
    state: dict
    output: str
    normalized_command: str


class RepositoryStateSimulator:
    """Internal Git-like simulator boundary. Student input is never executed."""

    def clone_state(self, state: dict) -> dict:
        return copy.deepcopy(state)

    def state_hash(self, state: dict) -> str:
        payload = json.dumps(state, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    def process(self, state: dict, command: str) -> SimulatorResult:
        command = " ".join(command.strip().split())
        if not command:
            return SimulatorResult(False, state, "No command entered.", "")
        try:
            parts = shlex.split(command)
        except ValueError:
            return SimulatorResult(False, state, "The command could not be parsed.", command)
        if not parts or parts[0] != "git":
            return SimulatorResult(False, state, "Only simulated git commands are accepted.", command)

        next_state = self.clone_state(state)
        action = parts[1] if len(parts) > 1 else ""

        handlers = {
            "status": self._status,
            "log": self._log,
            "branch": self._branch,
            "diff": self._diff,
            "show": self._show,
            "add": self._add,
            "commit": self._commit,
            "checkout": self._checkout,
            "switch": self._switch,
            "merge": self._merge,
            "reset": self._reset,
            "cherry-pick": self._cherry_pick,
        }
        handler = handlers.get(action)
        if handler is None:
            return SimulatorResult(
                False,
                state,
                "That Git operation is not available in this scenario simulator.",
                command,
            )
        try:
            output = handler(next_state, parts[2:])
        except (KeyError, IndexError, ValueError) as exc:
            return SimulatorResult(False, state, str(exc), command)
        return SimulatorResult(True, next_state, output, command)

    def _head_branch(self, state: dict) -> str | None:
        head = state.get("head", {})
        return head.get("name") if head.get("type") == "branch" else None

    def _head_commit(self, state: dict) -> str | None:
        head = state.get("head", {})
        if head.get("type") == "branch":
            return state.get("branches", {}).get(head.get("name"))
        return head.get("target")

    def _set_head_commit(self, state: dict, commit_id: str | None) -> None:
        branch = self._head_branch(state)
        if branch:
            state.setdefault("branches", {})[branch] = commit_id
        else:
            state.setdefault("head", {})["target"] = commit_id

    def _status(self, state: dict, args: list[str]) -> str:
        branch = self._head_branch(state) or "detached HEAD"
        staged = len(state.get("staging", {}))
        changes = len(state.get("working_tree", {}))
        conflicts = len(state.get("conflicts", []))
        lines = [f"On {branch}"]
        if conflicts:
            lines.append(f"{conflicts} path(s) still have conflict markers.")
        if staged:
            lines.append(f"{staged} path(s) staged for commit.")
        if changes:
            lines.append(f"{changes} path(s) with working tree changes.")
        if not staged and not changes and not conflicts:
            lines.append("Working tree clean.")
        return "\n".join(lines)

    def _log(self, state: dict, args: list[str]) -> str:
        commits = state.get("commits", [])
        if not commits:
            return "No commits yet."
        return "\n".join(f"{c['id']} {c.get('message', '')}" for c in reversed(commits[-6:]))

    def _branch(self, state: dict, args: list[str]) -> str:
        branches = state.setdefault("branches", {})
        if not args or args == ["-v"]:
            current = self._head_branch(state)
            return "\n".join(
                f"{'*' if name == current else ' '} {name} {target or '(no commits)'}"
                for name, target in sorted(branches.items())
            )
        if args[0] in ("-d", "-D"):
            name = args[1]
            if name == self._head_branch(state):
                raise ValueError("Cannot delete the checked-out branch.")
            if name not in branches:
                raise ValueError("Branch not found.")
            del branches[name]
            return f"Deleted branch {name}."
        name = args[0]
        if name in branches:
            raise ValueError("Branch already exists.")
        branches[name] = self._head_commit(state)
        return f"Created branch {name}."

    def _diff(self, state: dict, args: list[str]) -> str:
        if state.get("conflicts"):
            return "Conflict markers are present in the working tree."
        if state.get("working_tree"):
            return "Working tree changes are present."
        if state.get("staging"):
            return "Staged changes are ready."
        return "No differences."

    def _show(self, state: dict, args: list[str]) -> str:
        return "Object details available in the simulated repository."

    def _add(self, state: dict, args: list[str]) -> str:
        if not args:
            raise ValueError("Specify a path to add.")
        paths = list(state.get("working_tree", {}).keys()) if args[0] in (".", "-A") else args
        if not paths:
            return "No paths changed."
        staging = state.setdefault("staging", {})
        working_tree = state.setdefault("working_tree", {})
        conflicts = set(state.get("conflicts", []))
        for path in paths:
            staging[path] = working_tree.pop(path, "updated")
            conflicts.discard(path)
        state["conflicts"] = sorted(conflicts)
        return f"Staged {len(paths)} path(s)."

    def _commit(self, state: dict, args: list[str]) -> str:
        if not state.get("staging") and not state.get("merge_parent"):
            raise ValueError("Nothing staged to commit.")
        message = "commit"
        if "-m" in args:
            idx = args.index("-m")
            message = args[idx + 1]
        current = self._head_commit(state)
        parents = [p for p in [current, state.pop("merge_parent", None)] if p]
        commit_id = f"c{len(state.get('commits', []))}"
        state.setdefault("commits", []).append(
            {
                "id": commit_id,
                "message": message,
                "parents": parents,
                "files": copy.deepcopy(state.get("staging", {})),
            }
        )
        state["staging"] = {}
        self._set_head_commit(state, commit_id)
        return f"[{self._head_branch(state) or 'detached'} {commit_id}] {message}"

    def _checkout(self, state: dict, args: list[str]) -> str:
        if args and args[0] == "-b":
            return self._create_and_switch(state, args[1])
        return self._switch_to_ref(state, args[0])

    def _switch(self, state: dict, args: list[str]) -> str:
        if args and args[0] == "-c":
            return self._create_and_switch(state, args[1])
        return self._switch_to_ref(state, args[0])

    def _create_and_switch(self, state: dict, name: str) -> str:
        branches = state.setdefault("branches", {})
        if name in branches:
            raise ValueError("Branch already exists.")
        branches[name] = self._head_commit(state)
        state["head"] = {"type": "branch", "name": name}
        return f"Switched to a new branch '{name}'."

    def _switch_to_ref(self, state: dict, name: str) -> str:
        branches = state.setdefault("branches", {})
        commits = {commit["id"] for commit in state.get("commits", [])}
        if name in branches:
            state["head"] = {"type": "branch", "name": name}
            return f"Switched to branch '{name}'."
        if name in commits:
            state["head"] = {"type": "detached", "target": name}
            return f"HEAD is now detached at {name}."
        raise ValueError("Reference not found.")

    def _merge(self, state: dict, args: list[str]) -> str:
        if not args:
            raise ValueError("Specify a branch to merge.")
        other = args[0]
        branches = state.setdefault("branches", {})
        if other not in branches:
            raise ValueError("Branch not found.")
        if state.get("conflict_on_merge"):
            state["conflicts"] = sorted(state.get("conflict_files", ["app.py"]))
            state["merge_parent"] = branches[other]
            return "Automatic merge stopped because conflicts need resolution."
        current = self._head_commit(state)
        other_target = branches[other]
        if current == other_target:
            return "Already up to date."
        commit_id = f"c{len(state.get('commits', []))}"
        state.setdefault("commits", []).append(
            {"id": commit_id, "message": f"Merge {other}", "parents": [current, other_target]}
        )
        self._set_head_commit(state, commit_id)
        return f"Merge made by the simulated recursive strategy at {commit_id}."

    def _reset(self, state: dict, args: list[str]) -> str:
        if not args:
            raise ValueError("Specify a reset target.")
        target = args[-1]
        if target == "HEAD~1":
            current = self._head_commit(state)
            commits = {commit["id"]: commit for commit in state.get("commits", [])}
            parents = commits.get(current, {}).get("parents", [])
            if not parents:
                raise ValueError("No parent commit available.")
            self._set_head_commit(state, parents[0])
            return "Moved branch pointer to the parent commit."
        if target in state.get("branches", {}):
            self._set_head_commit(state, state["branches"][target])
            return f"Moved branch pointer to {target}."
        raise ValueError("Reset target not found.")

    def _cherry_pick(self, state: dict, args: list[str]) -> str:
        if not args:
            raise ValueError("Specify a commit to cherry-pick.")
        source_id = args[0]
        source = next((commit for commit in state.get("commits", []) if commit["id"] == source_id), None)
        if not source:
            raise ValueError("Commit not found.")
        current = self._head_commit(state)
        commit_id = f"c{len(state.get('commits', []))}"
        state.setdefault("commits", []).append(
            {
                "id": commit_id,
                "message": source.get("message", "cherry-pick"),
                "parents": [current] if current else [],
                "files": copy.deepcopy(source.get("files", {})),
            }
        )
        self._set_head_commit(state, commit_id)
        return f"Applied changes as {commit_id}."


class RepositorySnapshotService:
    def snapshot(self, state: dict) -> dict:
        branches = state.get("branches", {})
        head = state.get("head", {})
        head_target = branches.get(head.get("name")) if head.get("type") == "branch" else head.get("target")
        return {
            "commits": state.get("commits", []),
            "branches": branches,
            "head": {**head, "target": head_target},
            "staging": state.get("staging", {}),
            "working_tree": state.get("working_tree", {}),
            "conflicts": state.get("conflicts", []),
        }
