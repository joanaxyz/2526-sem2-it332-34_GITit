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

READ_ONLY_PREFIXES = (
    "git status",
    "git log",
    "git branch",
    "git diff",
    "git show",
    "git remote",
    "git reflog",
)

BRANCH_LISTING_OPTIONS = {"-v", "-vv", "-a", "--all", "--list"}


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

        legacy_handlers = {
            "fetch": self._fetch,
            "pull": self._pull,
            "push": self._push,
            "merge": self._merge,
            "stash": self._stash,
            "revert": self._revert,
            "cherry-pick": self._cherry_pick,
        }
        handler = self.handlers.get(action)
        legacy_handler = legacy_handlers.get(action)
        if handler is None and legacy_handler is None:
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

        if legacy_handler is not None:
            try:
                output = legacy_handler(next_state, parsed.executor_args)
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
            return SimulatorResult(
                True,
                next_state,
                output,
                parsed.normalized_text,
                stdout=output,
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

    def _validate_syntax(self, action: str, args: list[str]) -> None:
        if action == "status":
            self._reject_unknown_options(
                args, {"-s", "--short", "--porcelain"}, "error: unknown option `{}`."
            )
        elif action == "log":
            self._reject_unknown_options(
                args, {"--oneline", "--graph", "--all"}, "fatal: unrecognized argument: {}"
            )
        elif action == "diff":
            self._reject_unknown_options(
                args, {"--staged", "--cached"}, "error: invalid option: {}"
            )

    def _reject_unknown_options(
        self, args: list[str], allowed_options: set[str], message: str
    ) -> None:
        bad_option = next(
            (arg for arg in args if arg.startswith("-") and arg not in allowed_options), None
        )
        if bad_option:
            raise ValueError(message.format(bad_option))

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

    def _diff_trees_as_entries(self, before: dict, after: dict) -> dict:
        entries: dict[str, object] = {}
        for path, change in self._diff_trees(before, after).items():
            entries[path] = (
                change.get("change_type") if change.get("after") is None else change.get("after")
            )
        return entries

    def _merge_trees(self, current_tree: dict, other_tree: dict) -> dict:
        merged = copy.deepcopy(current_tree)
        merged.update(copy.deepcopy(other_tree))
        return merged

    def _set_operation_metadata(self, state: dict, **metadata: object) -> None:
        state.setdefault("operation_metadata", {}).update(metadata)
        for key, value in metadata.items():
            state[key] = value

    def _clear_operation_metadata(self, state: dict, *keys: str) -> None:
        operation_metadata = state.setdefault("operation_metadata", {})
        for key in keys:
            operation_metadata.pop(key, None)
            state.pop(key, None)

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

    def _init(self, state: dict, args: list[str]) -> str:
        target_directory = next((arg for arg in args if not arg.startswith("-")), None)
        state["repository_initialized"] = True
        state["remotes"] = {}
        state["remote_branches"] = {}
        state["upstream_tracking"] = {}
        branches = state.setdefault("branches", {})
        branches.setdefault("main", None)
        state["head"] = {"type": "branch", "name": "main"}
        self._set_operation_metadata(
            state,
            last_init_current_directory=target_directory is None,
        )
        if target_directory:
            self._set_operation_metadata(state, last_init_directory=target_directory)
        else:
            self._clear_operation_metadata(state, "last_init_directory")
        return "Initialized empty Git repository."

    def _clone(self, state: dict, args: list[str]) -> str:
        if state.get("repository_initialized", True):
            raise ValueError(
                "Clone starts a new repository and is only available before initialization."
            )
        if not args:
            raise ValueError("Specify a repository URL to clone.")
        url = args[0]
        target_dir = (
            args[1] if len(args) > 1 else url.rstrip("/").rsplit("/", 1)[-1].removesuffix(".git")
        )
        state["repository_initialized"] = True
        state["remotes"] = {"origin": url}
        remote_branches = state.setdefault("remote_branches", {})
        self._apply_remote_fixture_branches(state)
        remote_branches.setdefault("origin/main", self._first_remote_target(remote_branches))
        self._materialize_remote_commits(state)
        main_target = remote_branches.get("origin/main")
        state["branches"] = {"main": main_target}
        state["head"] = {"type": "branch", "name": "main"}
        state["upstream_tracking"] = {"main": "origin/main"}
        state["working_tree"] = {}
        state["staging"] = {}
        state["conflicts"] = []
        self._set_operation_metadata(
            state,
            last_clone_url=url,
            last_clone_destination=target_dir,
        )
        return f"Cloning into '{target_dir}'...\ndone."

    def _status(self, state: dict, args: list[str]) -> str:
        branch = self._head_branch(state) or "HEAD (detached)"
        staged = state.get("staging", {}) or {}
        working = state.get("working_tree", {}) or {}
        conflict_paths = sorted(state.get("conflicts", []))

        def label_for(value: object | None) -> str:
            value = self.normalizer.entry_status(value)
            if value in ("untracked",):
                return "new file:"
            if value in ("added", "new"):
                return "new file:"
            if value in ("deleted", "removed"):
                return "deleted:"
            return "modified:"

        lines: list[str] = [f"On branch {branch}"]
        upstream = state.get("upstream_tracking", {}).get(branch)
        if upstream:
            lines.append(f"Your branch is tracking {upstream}.")

        if conflict_paths:
            lines += [
                "",
                "You have unmerged paths.",
                '  (fix conflicts and run "git commit")',
                "",
                "Unmerged paths:",
            ]
            lines += [f"  both modified:   {path}" for path in conflict_paths]

        staged_paths = sorted(staged.keys())
        if staged_paths:
            lines += ["", "Changes to be committed:"]
            lines += [f"  {label_for(staged.get(path)):<11} {path}" for path in staged_paths]

        working_paths = sorted(
            path
            for path, value in working.items()
            if self.normalizer.entry_status(value) != "ignored"
        )
        untracked = [
            path
            for path in working_paths
            if self.normalizer.entry_status(working.get(path)) == "untracked"
        ]
        modified = [path for path in working_paths if path not in untracked]
        if modified:
            lines += ["", "Changes not staged for commit:"]
            lines += [f"  {label_for(working.get(path)):<11} {path}" for path in modified]
            lines += ['  (use "git add <file>..." to update what will be committed)']

        if untracked:
            lines += ["", "Untracked files:"]
            lines += [f"  {path}" for path in untracked]
            lines += ['  (use "git add <file>..." to include in what will be committed)']

        if not staged_paths and not working_paths and not conflict_paths:
            lines += ["", "nothing to commit, working tree clean"]

        return "\n".join(lines)

    def _log(self, state: dict, args: list[str]) -> str:
        commits = state.get("commits", [])
        if not commits:
            return "No commits yet."
        graph = "--graph" in args
        lines = []
        for commit in reversed(commits[-8:]):
            prefix = "* " if graph else ""
            lines.append(f"{prefix}{commit['id']} {commit.get('message', '')}".rstrip())
        return "\n".join(lines)

    def _branch(self, state: dict, args: list[str]) -> str:
        branches = state.setdefault("branches", {})
        if not args or all(arg in BRANCH_LISTING_OPTIONS for arg in args):
            current = self._head_branch(state)
            return "\n".join(
                f"{'*' if name == current else ' '} {name} {target or '(no commits)'}"
                for name, target in sorted(branches.items())
            )
        if args[0] in ("-d", "-D"):
            if len(args) < 2:
                raise ValueError("error: branch name required.")
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
        if name.startswith("-"):
            raise ValueError(f"error: unknown switch `{name}`.")
        start_point = args[1] if len(args) > 1 else None
        branches[name] = (
            self._resolve_ref(state, start_point) if start_point else self._head_commit(state)
        )
        return f"Created branch {name}."

    def _diff(self, state: dict, args: list[str]) -> str:
        if args and args[0] in ("--staged", "--cached"):
            staged_paths = sorted(state.get("staging", {}).keys())
            if staged_paths:
                return f"Staged changes: {self._format_paths(staged_paths)}"
            return "No staged differences."
        conflict_paths = sorted(state.get("conflicts", []))
        if conflict_paths:
            return f"Conflict markers are present in: {self._format_paths(conflict_paths)}"
        working_paths = sorted(
            path
            for path, value in state.get("working_tree", {}).items()
            if self.normalizer.entry_status(value) != "ignored"
        )
        if working_paths:
            return f"Working tree changes: {self._format_paths(working_paths)}"
        return "No working tree differences."

    def _show(self, state: dict, args: list[str]) -> str:
        target = args[0] if args else self._head_commit(state)
        commit = self._commit_by_id(state, target)
        if not commit:
            return "Object details available in the simulated repository."
        paths = sorted((commit.get("changes") or commit.get("files") or {}).keys())
        suffix = f"\nChanged paths: {self._format_paths(paths)}" if paths else ""
        return f"commit {commit['id']}\n{commit.get('message', '')}{suffix}"

    def _remote(self, state: dict, args: list[str]) -> str:
        remotes = state.setdefault("remotes", {})
        if not args:
            return "\n".join(sorted(remotes))
        if args in (["-v"], ["--verbose"]):
            return "\n".join(
                f"{name}\t{url} (fetch)\n{name}\t{url} (push)"
                for name, url in sorted(remotes.items())
            )
        if args[0] == "add":
            if len(args) < 3:
                raise ValueError("Specify a remote name and URL.")
            name, url = args[1], args[2]
            if name in remotes:
                raise ValueError("Remote already exists.")
            remotes[name] = url
            return f"Added remote {name}."
        raise ValueError("Only git remote and git remote add are simulated.")

    def _fetch(self, state: dict, args: list[str]) -> str:
        remote = args[0] if args else "origin"
        if remote not in state.get("remotes", {}):
            raise ValueError("Remote not found.")
        self._materialize_remote_commits(state)
        self._set_operation_metadata(
            state,
            remote_tracking_updated=True,
            last_fetch_remote=remote,
            last_fetch_local_before=self._head_commit(state),
        )
        return f"Fetched updates from {remote}."

    def _pull(self, state: dict, args: list[str]) -> str:
        branch = self._head_branch(state)
        if not branch:
            raise ValueError("Cannot pull into detached HEAD.")
        upstream = state.setdefault("upstream_tracking", {}).get(branch, f"origin/{branch}")
        target = state.setdefault("remote_branches", {}).get(upstream)
        if target is None:
            raise ValueError("Upstream branch not found.")
        self._materialize_remote_commits(state)
        state.setdefault("branches", {})[branch] = target
        self.normalizer.normalize_head(state)
        self._set_operation_metadata(
            state,
            remote_tracking_updated=False,
            last_pull_remote_branch=upstream,
            last_pull_local_branch=branch,
            last_pull_target=target,
        )
        self._record_reflog(state, target, f"pull {upstream}")
        return f"Pulled {upstream} into {branch}."

    def _push(self, state: dict, args: list[str]) -> str:
        branch = self._head_branch(state)
        if not branch:
            raise ValueError("Cannot push detached HEAD.")
        upstream = state.setdefault("upstream_tracking", {}).get(branch, f"origin/{branch}")
        remote = upstream.split("/", 1)[0]
        if remote not in state.get("remotes", {}):
            raise ValueError("Remote not found.")
        state.setdefault("remote_branches", {})[upstream] = state.get("branches", {}).get(branch)
        self._set_operation_metadata(
            state,
            last_push_remote_branch=upstream,
            last_push_local_branch=branch,
            last_push_target=state.get("branches", {}).get(branch),
        )
        return f"Pushed {branch} to {upstream}."

    def _add(self, state: dict, args: list[str]) -> str:
        if not args:
            raise ValueError("Specify a path to add.")
        if args[0] == "-p":
            return self._add_patch(state, args[1:])
        working_tree = state.setdefault("working_tree", {})
        paths = (
            [
                path
                for path, value in working_tree.items()
                if self.normalizer.entry_status(value) != "ignored"
            ]
            if args[0] in (".", "-A")
            else args
        )
        if not paths:
            return ""
        staging = state.setdefault("staging", {})
        conflicts = set(state.get("conflicts", []))
        for path in paths:
            if self.normalizer.entry_status(working_tree.get(path)) == "ignored":
                continue
            staging[path] = working_tree.pop(path, "updated")
            conflicts.discard(path)
        state["conflicts"] = sorted(conflicts)
        return ""

    def _add_patch(self, state: dict, args: list[str]) -> str:
        working_tree = state.setdefault("working_tree", {})
        partial_hunks = state.setdefault("partial_hunks", {})
        paths = (
            args
            or list(partial_hunks)
            or [
                path
                for path, value in working_tree.items()
                if self.normalizer.entry_status(value) not in {"ignored", "untracked"}
            ]
        )
        if not paths:
            raise ValueError("No tracked changes available for patch staging.")
        staging = state.setdefault("staging", {})
        for path in paths:
            if path not in working_tree and path not in partial_hunks:
                continue
            if self.normalizer.entry_status(working_tree.get(path)) == "ignored":
                continue
            authored = partial_hunks.get(path) or {}
            if isinstance(authored, dict):
                target_hunks = self._as_list(
                    authored.get("target_hunks")
                    or authored.get("staged_hunks")
                    or authored.get("stage")
                )
                leftover_hunks = self._as_list(
                    authored.get("leftover_hunks")
                    or authored.get("remaining_hunks")
                    or authored.get("leftover")
                )
            else:
                authored_hunks = self._as_list(authored)
                target_hunks = authored_hunks[:1]
                leftover_hunks = authored_hunks[1:]
            if target_hunks or leftover_hunks:
                staging[path] = {"status": "partial", "hunks": target_hunks}
                if leftover_hunks:
                    working_tree[path] = {"status": "modified", "hunks": leftover_hunks}
                else:
                    working_tree.pop(path, None)
            else:
                staging[path] = {
                    "status": "partial",
                    "hunks": self._entry_tokens(working_tree.get(path)),
                }
                working_tree[path] = "modified"
        return "Staged selected hunks."

    def _rm(self, state: dict, args: list[str]) -> str:
        if not args or args[0] != "--cached":
            raise ValueError("Only git rm --cached <path> is simulated.")
        paths = [path for path in args[1:] if path != "--"]
        if not paths:
            raise ValueError("Specify a path to remove from the index.")
        staging = state.setdefault("staging", {})
        working_tree = state.setdefault("working_tree", {})
        head_tree = self._head_tree(state)
        removed_paths: list[str] = []
        for path in paths:
            if path not in head_tree and path not in staging:
                raise ValueError(f"pathspec '{path}' did not match any tracked file.")
            staging[path] = "deleted"
            existing = working_tree.get(path)
            if existing is None:
                working_tree[path] = {
                    "status": "ignored",
                    "content": copy.deepcopy(head_tree.get(path)),
                    "preserved": True,
                }
            elif self.normalizer.entry_status(existing) not in {"ignored", "untracked"}:
                working_tree[path] = {
                    "status": "ignored",
                    "content": copy.deepcopy(existing),
                    "preserved": True,
                }
            removed_paths.append(path)
        self._set_operation_metadata(state, last_rm_cached_paths=removed_paths)
        return f"rm '{self._format_paths(removed_paths)}'"

    def _commit(self, state: dict, args: list[str]) -> str:
        if "--amend" in args:
            return self._commit_amend(state, args)
        if not state.get("staging") and not state.get("merge_parent"):
            raise ValueError("Nothing staged to commit.")
        message = "commit"
        if "-m" in args:
            idx = args.index("-m")
            if idx + 1 >= len(args):
                raise ValueError("error: switch `m' requires a value.")
            message = args[idx + 1]
        current = self._head_commit(state)
        parents = [p for p in [current, state.pop("merge_parent", None)] if p]
        commit_id = self._next_commit_id(state)
        base_tree = self._tree_for_commit(state, current)
        staged_entries = copy.deepcopy(state.get("staging", {}))
        staged_changes = self._changes_from_entries(base_tree, staged_entries)
        tree = self._apply_changes(base_tree, staged_changes)
        state.setdefault("commits", []).append(
            self._commit_payload(
                state=state,
                commit_id=commit_id,
                message=message,
                parents=parents,
                tree=tree,
                changes=staged_changes,
            )
        )
        state["staging"] = {}
        self._cleanup_partial_hunks_after_commit(state, staged_entries)
        self._set_head_commit(state, commit_id)
        return f"[{self._head_branch(state) or 'detached'} {commit_id}] {message}"

    def _commit_amend(self, state: dict, args: list[str]) -> str:
        current = self._head_commit(state)
        old_commit = self._commit_by_id(state, current)
        if not old_commit:
            raise ValueError("No commit available to amend.")
        message = old_commit.get("message", "commit")
        if "-m" in args:
            idx = args.index("-m")
            if idx + 1 >= len(args):
                raise ValueError("error: switch `m' requires a value.")
            message = args[idx + 1]
        parent_ids = list(old_commit.get("parents", []))
        parent_id = (parent_ids or [None])[0]
        parent_tree = self._tree_for_commit(state, parent_id)
        current_tree = copy.deepcopy(old_commit.get("tree") or parent_tree)
        staged_entries = copy.deepcopy(state.get("staging", {}))
        staged_changes = self._changes_from_entries(current_tree, staged_entries)
        amended_tree = self._apply_changes(current_tree, staged_changes)
        commit_id = self._next_commit_id(state)
        changes = self._diff_trees(parent_tree, amended_tree)
        state.setdefault("commits", []).append(
            self._commit_payload(
                state=state,
                commit_id=commit_id,
                message=message,
                parents=parent_ids,
                tree=amended_tree,
                changes=changes,
            )
        )
        state.setdefault("replaced_commits", {})[current] = commit_id
        self._set_operation_metadata(
            state,
            last_amend_replaced_commit=current,
            last_amend_created_commit=commit_id,
        )
        state["staging"] = {}
        self._cleanup_partial_hunks_after_commit(state, staged_entries)
        self._set_head_commit(state, commit_id)
        self._record_reflog(state, commit_id, f"commit --amend: replaced {current}")
        return f"[{self._head_branch(state) or 'detached'} {commit_id}] amended commit"

    def _checkout(self, state: dict, args: list[str]) -> str:
        if not args:
            raise ValueError("You must specify a branch or path to checkout.")
        if args and args[0] == "-b":
            if len(args) < 2:
                raise ValueError("error: switch `b' requires a value.")
            return self._create_and_switch(state, args[1], args[2] if len(args) > 2 else None)
        return self._switch_to_ref(state, args[0])

    def _switch(self, state: dict, args: list[str]) -> str:
        if not args:
            raise ValueError("fatal: missing branch or commit argument.")
        if args and args[0] == "-c":
            if len(args) < 2:
                raise ValueError("error: switch `c' requires a value.")
            return self._create_and_switch(state, args[1], args[2] if len(args) > 2 else None)
        return self._switch_to_ref(state, args[0])

    def _create_and_switch(self, state: dict, name: str, start_point: str | None = None) -> str:
        branches = state.setdefault("branches", {})
        if name in branches:
            raise ValueError("Branch already exists.")
        branches[name] = (
            self._resolve_ref(state, start_point) if start_point else self._head_commit(state)
        )
        state["head"] = {"type": "branch", "name": name}
        return f"Switched to a new branch '{name}'."

    def _switch_to_ref(self, state: dict, name: str) -> str:
        branches = state.setdefault("branches", {})
        if name in branches:
            state["head"] = {"type": "branch", "name": name}
            return f"Switched to branch '{name}'."
        target = self._resolve_ref(state, name)
        state["head"] = {"type": "detached", "target": target}
        return f"HEAD is now detached at {target}."

    def _merge(self, state: dict, args: list[str]) -> str:
        if not args:
            raise ValueError("Specify a branch to merge.")
        other = args[0]
        branches = state.setdefault("branches", {})
        if other not in branches:
            raise ValueError("Branch not found.")
        if state.get("conflict_on_merge"):
            conflict_paths = sorted(state.get("conflict_files", ["app.py"]))
            state["conflicts"] = conflict_paths
            for path in conflict_paths:
                state.setdefault("working_tree", {}).setdefault(path, "conflict")
            state["merge_parent"] = branches[other]
            self._set_operation_metadata(
                state,
                merge_conflict=True,
                merge_source=other,
                merge_target=branches[other],
            )
            return "Automatic merge stopped because conflicts need resolution."

        current = self._head_commit(state)
        other_target = branches[other]
        if current == other_target:
            return "Already up to date."
        if self._is_ancestor(state, current, other_target):
            self._set_head_commit(state, other_target)
            return f"Fast-forwarded to {other_target}."
        commit_id = self._next_commit_id(state)
        current_tree = self._tree_for_commit(state, current)
        other_tree = self._tree_for_commit(state, other_target)
        merged_tree = self._merge_trees(current_tree, other_tree)
        changes = self._diff_trees(current_tree, merged_tree)
        state.setdefault("commits", []).append(
            self._commit_payload(
                state=state,
                commit_id=commit_id,
                message=f"Merge {other}",
                parents=[p for p in [current, other_target] if p],
                tree=merged_tree,
                changes=changes,
            )
        )
        self._set_head_commit(state, commit_id)
        return f"Merge made by the simulated recursive strategy at {commit_id}."

    def _reset(self, state: dict, args: list[str]) -> str:
        if not args:
            raise ValueError("Specify a reset target.")
        mode = "--mixed"
        target_args = []
        for arg in args:
            if arg in {"--soft", "--mixed", "--hard"}:
                mode = arg
            else:
                target_args.append(arg)
        if not target_args:
            raise ValueError("Specify a reset target.")
        if mode == "--mixed" and target_args[0] == "HEAD" and len(target_args) > 1:
            for path in target_args[1:]:
                value = state.setdefault("staging", {}).pop(path, "modified")
                state.setdefault("working_tree", {})[path] = value
            return "Unstaged paths."
        target = self._resolve_reset_target(state, target_args[-1])
        current = self._head_commit(state)
        current_tree = self._tree_for_commit(state, current)
        target_tree = self._tree_for_commit(state, target)
        self._set_head_commit(state, target)
        if mode == "--hard":
            state["staging"] = {}
            state["working_tree"] = {}
            state["conflicts"] = []
        elif mode == "--soft":
            state["staging"] = self._diff_trees_as_entries(target_tree, current_tree)
        else:
            state["staging"] = {}
            state.setdefault("working_tree", {}).update(
                self._diff_trees_as_entries(target_tree, current_tree)
            )
        self._set_operation_metadata(
            state,
            last_reset_mode=mode.removeprefix("--"),
            last_reset_from=current,
            last_reset_to=target,
        )
        return f"Moved branch pointer to {target}."

    def _restore(self, state: dict, args: list[str]) -> str:
        if not args:
            raise ValueError("Specify a path to restore.")
        if args[0] == "--staged":
            paths = args[1:]
            if not paths:
                raise ValueError("Specify a staged path to restore.")
            for path in paths:
                value = state.setdefault("staging", {}).pop(path, "modified")
                state.setdefault("working_tree", {})[path] = value
            return "Unstaged paths."
        for path in args:
            state.setdefault("working_tree", {}).pop(path, None)
            conflicts = set(state.get("conflicts", []))
            conflicts.discard(path)
            state["conflicts"] = sorted(conflicts)
        return "Restored working tree paths."

    def _stash(self, state: dict, args: list[str]) -> str:
        if args and args[0] == "pop":
            stack = state.setdefault("stash_stack", [])
            if not stack:
                raise ValueError("No stash entries found.")
            entry = stack.pop()
            state.setdefault("working_tree", {}).update(entry.get("working_tree", {}))
            state.setdefault("staging", {}).update(entry.get("staging", {}))
            state["conflicts"] = sorted(
                set(state.get("conflicts", [])) | set(entry.get("conflicts", []))
            )
            self._set_operation_metadata(
                state,
                last_stash_pop_restored_paths=sorted(
                    set(entry.get("working_tree", {})) | set(entry.get("staging", {}))
                ),
            )
            return "Applied stash and dropped it."

        if not state.get("working_tree") and not state.get("staging"):
            return "No local changes to save."
        state.setdefault("stash_stack", []).append(
            {
                "working_tree": copy.deepcopy(state.get("working_tree", {})),
                "staging": copy.deepcopy(state.get("staging", {})),
                "conflicts": copy.deepcopy(state.get("conflicts", [])),
            }
        )
        self._set_operation_metadata(
            state,
            last_stash_saved_paths=sorted(
                set(state.get("working_tree", {})) | set(state.get("staging", {}))
            ),
        )
        state["working_tree"] = {}
        state["staging"] = {}
        state["conflicts"] = []
        return "Saved working directory and index state."

    def _reflog(self, state: dict, args: list[str]) -> str:
        entries = state.get("reflog", [])
        if not entries:
            return "HEAD@{0} current position"
        return "\n".join(
            f"{entry.get('ref')} {entry.get('target')} {entry.get('message')}" for entry in entries
        )

    def _revert(self, state: dict, args: list[str]) -> str:
        if not args:
            raise ValueError("Specify a commit to revert.")
        target = args[0]
        commit = self._commit_by_id(state, target)
        if not commit:
            raise ValueError("Commit not found.")
        current = self._head_commit(state)
        commit_id = self._next_commit_id(state)
        current_tree = self._tree_for_commit(state, current)
        state.setdefault("commits", []).append(
            self._commit_payload(
                state=state,
                commit_id=commit_id,
                message=f"Revert {commit.get('message', target)}",
                parents=[current] if current else [],
                tree=current_tree,
                changes={},
            )
        )
        self._set_operation_metadata(
            state, last_revert_commit=target, last_revert_created=commit_id
        )
        self._set_head_commit(state, commit_id)
        return f"Created revert commit {commit_id}."

    def _cherry_pick(self, state: dict, args: list[str]) -> str:
        if not args:
            raise ValueError("Specify a commit to cherry-pick.")
        source_id = args[0]
        source = self._commit_by_id(state, source_id)
        if not source:
            raise ValueError("Commit not found.")
        current = self._head_commit(state)
        commit_id = self._next_commit_id(state)
        base_tree = self._tree_for_commit(state, current)
        source_changes = copy.deepcopy(source.get("changes") or {})
        if not source_changes:
            source_changes = self._changes_from_entries(base_tree, source.get("files", {}))
        tree = self._apply_changes(base_tree, source_changes)
        state.setdefault("commits", []).append(
            self._commit_payload(
                state=state,
                commit_id=commit_id,
                message=source.get("message", "cherry-pick"),
                parents=[current] if current else [],
                tree=tree,
                changes=source_changes,
            )
        )
        self._set_operation_metadata(
            state,
            last_cherry_pick_source=source_id,
            last_cherry_pick_created=commit_id,
        )
        self._set_head_commit(state, commit_id)
        return f"Applied changes as {commit_id}."

    def _resolve_ref(self, state: dict, ref: str | None) -> str | None:
        if ref is None:
            return self._head_commit(state)
        if ref in state.get("branches", {}):
            return state["branches"][ref]
        if ref in state.get("remote_branches", {}):
            return state["remote_branches"][ref]
        if self._commit_by_id(state, ref):
            return ref
        raise ValueError("Reference not found.")

    def _resolve_reset_target(self, state: dict, target: str) -> str | None:
        if target == "HEAD~1":
            current = self._head_commit(state)
            parents = (self._commit_by_id(state, current) or {}).get("parents", [])
            if not parents:
                raise ValueError("No parent commit available.")
            return parents[0]
        return self._resolve_ref(state, target)

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

    def _is_ancestor(self, state: dict, ancestor: str | None, descendant: str | None) -> bool:
        if ancestor is None or descendant is None:
            return False
        commits = {commit["id"]: commit for commit in state.get("commits", [])}
        stack = [descendant]
        seen: set[str] = set()
        while stack:
            current = stack.pop()
            if current == ancestor:
                return True
            if current in seen or current not in commits:
                continue
            seen.add(current)
            stack.extend(commits[current].get("parents", []))
        return False

    def _files_for_soft_reset(self, commit: dict | None) -> dict:
        if not commit:
            return {}
        files = copy.deepcopy(commit.get("files") or {})
        if files:
            return files
        message = commit.get("message", "").lower()
        topics = ["auth", "payment", "search", "export", "profile"]
        topic = next((item for item in topics if item in message), "update")
        if any(word in message for word in ("combined", "scope", "messy")):
            return {"README.md": "modified", f"{topic}.py": "modified"}
        return {f"{topic}.py": "modified"}

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

    def _format_paths(self, paths: list[str]) -> str:
        return ", ".join(paths)


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
