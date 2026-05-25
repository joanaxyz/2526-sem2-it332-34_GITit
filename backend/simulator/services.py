import copy
import hashlib
import json
from dataclasses import dataclass

from simulator.commands import command_handlers
from simulator.commands.base import SimulatorCommandError
from simulator.git_commands import (
    GitCommandParseError,
    GitCommandParser,
    GitCommandRegistry,
    NonGitCommandError,
    ParsedGitCommand,
)
from simulator.intents import CommandIntentMapper
from simulator.output import GitLikeOutputFormatter
from simulator.output.errors import not_a_repository, unsupported_command
from simulator.state import RepositoryStateNormalizer

@dataclass(frozen=True)
class SimulatorResult:
    processed: bool
    state: dict
    output: str
    normalized_command: str
    stdout: str = ""
    stderr: str = ""
    exit_code: int = 0
    diagnostic_metadata: tuple[str, ...] = ()
    command_family: str = ""


def normalize_command(command: str) -> str:
    try:
        return GitCommandParser().parse(command).normalized_text
    except (GitCommandParseError, NonGitCommandError):
        return " ".join(command.strip().split())


def parse_git_command(command: str) -> list[str] | None:
    try:
        parsed = GitCommandParser().parse(command)
    except (GitCommandParseError, NonGitCommandError):
        return None
    return list(parsed.argv)


def is_diagnostic_command(command: str) -> bool:
    try:
        parsed = GitCommandParser().parse(command)
    except (GitCommandParseError, NonGitCommandError):
        return False
    return GitCommandRegistry().is_diagnostic(parsed)


class RepositoryStateSimulator:
    """Internal Git-like simulator boundary. Student input is never executed."""

    def __init__(self) -> None:
        self.normalizer = RepositoryStateNormalizer()
        self.intent_mapper = CommandIntentMapper()
        self.handlers = command_handlers()
        self.output_formatter = GitLikeOutputFormatter()

    def clone_state(self, state: dict) -> dict:
        return copy.deepcopy(state)

    def normalize_state(self, state: dict) -> dict:
        return self.normalizer.normalize(state)

    def state_hash(self, state: dict) -> str:
        payload = json.dumps(self.normalize_state(state), sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    def state_hash_for_normalized(self, state: dict) -> str:
        payload = json.dumps(state, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    def process(self, state: dict, command: str) -> SimulatorResult:
        try:
            parsed = GitCommandParser().parse(command)
        except GitCommandParseError as exc:
            return SimulatorResult(
                False, state, str(exc), normalize_command(command), stderr=str(exc), exit_code=129
            )
        except NonGitCommandError:
            message = "Only simulated git commands are accepted."
            return SimulatorResult(
                False, state, message, normalize_command(command), stderr=message, exit_code=127
            )

        return self.process_parsed(state, parsed)

    def process_parsed(
        self,
        state: dict,
        parsed: ParsedGitCommand,
        *,
        validate: bool = True,
    ) -> SimulatorResult:
        next_state = self.clone_state(state)
        self._ensure_state_shape(next_state)
        action = parsed.subcommand

        handler = self.handlers.get(action)
        if handler is None:
            return SimulatorResult(
                False,
                state,
                unsupported_command(action or parsed.normalized_text),
                parsed.normalized_text,
                stderr=unsupported_command(action or parsed.normalized_text),
                exit_code=129,
                command_family=action,
            )

        if validate:
            registry_spec = GitCommandRegistry().get(action)
            if registry_spec is None:
                message = unsupported_command(action or parsed.normalized_text)
                return SimulatorResult(
                    False,
                    state,
                    message,
                    parsed.normalized_text,
                    stderr=message,
                    exit_code=129,
                    command_family=action,
                )
            validation_error = registry_spec.validate(parsed) if registry_spec else None
            if validation_error:
                return SimulatorResult(
                    False,
                    state,
                    validation_error,
                    parsed.normalized_text,
                    stderr=validation_error,
                    exit_code=129,
                    command_family=action,
                )

        if not next_state.get("repository_initialized", True) and action not in {"init", "clone"}:
            message = not_a_repository()
            return SimulatorResult(
                True,
                next_state,
                message,
                parsed.normalized_text,
                stderr=message,
                exit_code=128,
                command_family=action,
            )

        intent = self.intent_mapper.map(parsed)
        try:
            outcome = handler.apply(self, next_state, intent)
            stdout, stderr = self.output_formatter.format(self, next_state, intent, outcome)
        except SimulatorCommandError as exc:
            return SimulatorResult(
                False,
                state,
                str(exc),
                parsed.normalized_text,
                stderr=str(exc),
                exit_code=exc.exit_code,
                command_family=action,
            )
        except (KeyError, IndexError, ValueError) as exc:
            return SimulatorResult(
                False,
                state,
                str(exc),
                parsed.normalized_text,
                stderr=str(exc),
                exit_code=128,
                command_family=action,
            )
        output = "\n".join(part for part in (stdout, stderr) if part)
        return SimulatorResult(
            True,
            next_state,
            output,
            parsed.normalized_text,
            stdout=stdout,
            stderr=stderr,
            exit_code=outcome.exit_code,
            diagnostic_metadata=intent.diagnostic_metadata,
            command_family=action,
        )

    def _ensure_state_shape(self, state: dict) -> None:
        self.normalizer.ensure_shape(state)
        self.normalizer.normalize_commits(state)
        self.normalizer.normalize_head(state)

    def _head_branch(self, state: dict) -> str | None:
        head = state.get("head", {})
        return head.get("name") if head.get("type") == "branch" else None

    def _head_commit(self, state: dict) -> str | None:
        head = state.get("head", {})
        if head.get("type") == "branch":
            return state.get("branches", {}).get(head.get("name"))
        return head.get("target")

    def _head_tree(self, state: dict) -> dict:
        return self._tree_for_commit(state, self._head_commit(state))

    def _tree_for_commit(self, state: dict, commit_id: str | None) -> dict:
        commit = self._commit_by_id(state, commit_id)
        if not commit:
            return {}
        return copy.deepcopy(commit.get("tree") or {})

    def _commit_payload(
        self,
        *,
        state: dict,
        commit_id: str,
        message: str,
        parents: list[str],
        tree: dict,
        changes: dict,
    ) -> dict:
        return {
            "id": commit_id,
            "message": message,
            "parents": parents,
            "tree": copy.deepcopy(tree),
            "changes": copy.deepcopy(changes),
            "files": self.normalizer.files_from_changes(changes),
            "author": "GIT it",
            "order": len(state.get("commits", [])),
            "is_merge": len(parents) > 1,
        }

    def _changes_from_entries(self, base_tree: dict, entries: dict) -> dict:
        return self.normalizer.changes_from_entries(base_tree, entries)

    def _apply_changes(self, base_tree: dict, changes: dict) -> dict:
        return self.normalizer.apply_changes(base_tree, changes)

    def _diff_trees(self, before: dict, after: dict) -> dict:
        return self.normalizer.diff_trees(before, after)

    def _set_operation_metadata(self, state: dict, **metadata: object) -> None:
        state.setdefault("operation_metadata", {}).update(metadata)
        for key, value in metadata.items():
            state[key] = value

    def _set_head_commit(self, state: dict, commit_id: str | None) -> None:
        branch = self._head_branch(state)
        if branch:
            state.setdefault("branches", {})[branch] = commit_id
        else:
            state.setdefault("head", {})["target"] = commit_id
        self.normalizer.normalize_head(state)
        self._record_reflog(state, commit_id, "move HEAD")

    def _record_reflog(self, state: dict, target: str | None, message: str) -> None:
        if not target:
            return
        state.setdefault("reflog", []).append(
            {
                "ref": f"HEAD@{{{len(state.get('reflog', []))}}}",
                "target": target,
                "message": message,
            }
        )

    def _commit_by_id(self, state: dict, commit_id: str | None) -> dict | None:
        if not commit_id:
            return None
        return next(
            (commit for commit in state.get("commits", []) if commit["id"] == commit_id), None
        )

    def _next_commit_id(self, state: dict) -> str:
        index = 0
        existing = {commit["id"] for commit in state.get("commits", [])}
        while f"c{index}" in existing:
            index += 1
        return f"c{index}"

    def _as_list(self, value: object | None) -> list:
        if value in (None, ""):
            return []
        return value if isinstance(value, list) else [value]

    def _entry_tokens(self, value: object | None) -> list[str]:
        if value is None:
            return []
        if isinstance(value, dict):
            for key in ("hunks", "tokens", "target_hunks", "leftover_hunks"):
                if key in value:
                    return [str(item) for item in self._as_list(value.get(key))]
        return (
            [self.normalizer.token_haystack(value)] if self.normalizer.token_haystack(value) else []
        )

    def _cleanup_partial_hunks_after_commit(self, state: dict, staged_entries: dict) -> None:
        partial_hunks = state.setdefault("partial_hunks", {})
        for path, staged_value in staged_entries.items():
            if self.normalizer.entry_status(staged_value) != "partial":
                continue
            authored = partial_hunks.get(path)
            if not isinstance(authored, dict):
                continue
            leftover = self._as_list(
                authored.get("leftover_hunks")
                or authored.get("remaining_hunks")
                or authored.get("leftover")
            )
            if leftover:
                partial_hunks[path] = {"target_hunks": [], "leftover_hunks": leftover}
            else:
                partial_hunks.pop(path, None)

    def _first_remote_target(self, remote_branches: dict) -> str:
        targets = [target for target in remote_branches.values() if target]
        return sorted(targets)[0] if targets else "r0"

    def _apply_remote_fixture_branches(self, state: dict) -> None:
        fixture = state.get("remote_fixtures") or {}
        if not isinstance(fixture, dict):
            return
        remote_branches = state.setdefault("remote_branches", {})
        branch_targets = {}
        authored_branches = fixture.get("branches")
        if isinstance(authored_branches, dict):
            branch_targets.update(authored_branches)
        for key, value in fixture.items():
            if key in {"commits", "branches", "remote_head", "head", "default_branch"}:
                continue
            if "/" in key and value:
                branch_targets[key] = value
        remote_head = fixture.get("remote_head") or fixture.get("head")
        default_branch = fixture.get("default_branch") or "origin/main"
        if remote_head:
            branch_targets.setdefault(default_branch, remote_head)
        for branch, target in branch_targets.items():
            remote_branches[branch] = target

    def _materialize_remote_commits(self, state: dict) -> None:
        commits = state.setdefault("commits", [])
        existing = {commit["id"] for commit in commits}
        fixture = state.get("remote_fixtures") or {}
        fixture_commits = fixture.get("commits", []) if isinstance(fixture, dict) else []
        for authored_commit in fixture_commits:
            if not isinstance(authored_commit, dict):
                continue
            commit_id = authored_commit.get("id")
            if not commit_id:
                continue
            if commit_id in existing:
                existing_commit = self._commit_by_id(state, commit_id)
                if existing_commit:
                    existing_commit.update(copy.deepcopy(authored_commit))
                continue
            commits.append(copy.deepcopy(authored_commit))
            existing.add(commit_id)
        self.normalizer.normalize_commits(state)
        existing = {commit["id"] for commit in commits}
        remote_ids = sorted(
            {target for target in state.get("remote_branches", {}).values() if target}
        )
        previous = None
        for commit_id in remote_ids:
            if commit_id not in existing:
                commits.append(
                    {
                        "id": commit_id,
                        "message": f"Remote commit {commit_id}",
                        "parents": [previous] if previous else [],
                        "tree": {},
                        "changes": {},
                        "files": {},
                        "is_merge": False,
                    }
                )
                existing.add(commit_id)
            previous = commit_id
        self.normalizer.normalize_commits(state)

class RepositorySnapshotService:
    def snapshot(self, state: dict) -> dict:
        normalizer = RepositoryStateNormalizer()
        state = normalizer.normalize(state)
        branches = state.get("branches", {})
        head = state.get("head", {})
        head_target = (
            branches.get(head.get("name")) if head.get("type") == "branch" else head.get("target")
        )
        visible_tree = normalizer.visible_project_tree(state)
        return {
            "repository_initialized": state.get("repository_initialized", True),
            "commits": state.get("commits", []),
            "branches": branches,
            "head": {**head, "target": head_target},
            "staging": state.get("staging", {}),
            "working_tree": state.get("working_tree", {}),
            "conflicts": state.get("conflicts", []),
            "remotes": state.get("remotes", {}),
            "remote_branches": state.get("remote_branches", {}),
            "upstream_tracking": state.get("upstream_tracking", {}),
            "stash_stack": state.get("stash_stack", []),
            "partial_hunks": state.get("partial_hunks", {}),
            "replaced_commits": state.get("replaced_commits", {}),
            "reflog": state.get("reflog", []),
            "operation_metadata": state.get("operation_metadata", {}),
            "project_tree": visible_tree,
            "visible_tree": visible_tree,
        }
