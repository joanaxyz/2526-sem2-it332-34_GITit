from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from simulator.git_commands import ParsedGitCommand


@dataclass(frozen=True)
class CommandOperation:
    name: str
    params: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class CommandIntent:
    command: str
    operations: tuple[CommandOperation, ...]
    diagnostic_metadata: tuple[str, ...] = ()
    output_mode: str = "default"

    @property
    def is_diagnostic(self) -> bool:
        return bool(self.diagnostic_metadata)

    def has_operation(self, name: str) -> bool:
        return any(operation.name == name for operation in self.operations)

    def first(self, name: str) -> CommandOperation | None:
        return next((operation for operation in self.operations if operation.name == name), None)


class CommandIntentMapper:
    """Map parsed Git syntax variants to simulator operations."""

    def map(self, parsed: ParsedGitCommand) -> CommandIntent:
        mapper = getattr(self, f"_map_{parsed.subcommand.replace('-', '_')}", None)
        if mapper is None:
            return CommandIntent(
                command=parsed.subcommand,
                operations=(
                    CommandOperation("UnsupportedCommand", {"command": parsed.subcommand}),
                ),
            )
        return mapper(parsed)

    def _map_init(self, parsed: ParsedGitCommand) -> CommandIntent:
        branch_values = parsed.options.get("-b", ()) + parsed.options.get("--initial-branch", ())
        initial_branch = str(branch_values[-1]) if branch_values else "main"
        directory = parsed.args[0] if parsed.args else None
        return CommandIntent(
            command="init",
            operations=(
                CommandOperation(
                    "InitializeRepository",
                    {
                        "initial_branch": initial_branch,
                        "directory": directory,
                        "quiet": parsed.has_option("-q") or parsed.has_option("--quiet"),
                    },
                ),
            ),
        )

    def _map_clone(self, parsed: ParsedGitCommand) -> CommandIntent:
        branch_values = parsed.options.get("-b", ()) + parsed.options.get("--branch", ())
        depth_values = parsed.options.get("--depth", ())
        return CommandIntent(
            command="clone",
            operations=(
                CommandOperation(
                    "CloneRepository",
                    {
                        "url": parsed.args[0],
                        "destination": parsed.args[1] if len(parsed.args) > 1 else None,
                        "branch": str(branch_values[-1]) if branch_values else None,
                        "depth": int(str(depth_values[-1])) if depth_values else None,
                        "remote_name": "origin",
                    },
                ),
            ),
        )

    def _map_status(self, parsed: ParsedGitCommand) -> CommandIntent:
        short = (
            parsed.has_option("-s")
            or parsed.has_option("-sb")
            or parsed.has_option("--short")
            or parsed.has_option("--porcelain")
        )
        branch = parsed.has_option("-sb")
        ignored = parsed.has_option("--ignored")
        return CommandIntent(
            command="status",
            operations=(
                CommandOperation(
                    "InspectStatus",
                    {"short": short, "branch": branch, "ignored": ignored},
                ),
            ),
            diagnostic_metadata=(
                "inspected_ignored_status"
                if ignored
                else "inspected_short_status"
                if short
                else "inspected_status",
            ),
            output_mode="short_branch" if branch else "short" if short else "default",
        )

    def _map_add(self, parsed: ParsedGitCommand) -> CommandIntent:
        if parsed.has_option("-p") or parsed.has_option("--patch"):
            return CommandIntent(
                command="add",
                operations=(CommandOperation("StagePatch", {"paths": parsed.pathspecs}),),
            )
        if parsed.has_option("-u") or parsed.has_option("--update"):
            return CommandIntent(
                command="add",
                operations=(
                    CommandOperation("StageTrackedChangesOnly", {"paths": parsed.pathspecs}),
                ),
            )
        if parsed.has_option("-A") or parsed.has_option("--all") or "." in parsed.pathspecs:
            return CommandIntent(
                command="add",
                operations=(CommandOperation("StageAllChanges", {"paths": parsed.pathspecs}),),
            )
        if parsed.has_option("--intent-to-add"):
            return CommandIntent(
                command="add",
                operations=(CommandOperation("UnsupportedCommand", {"command": "add"}),),
            )
        return CommandIntent(
            command="add",
            operations=(CommandOperation("StagePathspecs", {"paths": parsed.pathspecs}),),
        )

    def _map_commit(self, parsed: ParsedGitCommand) -> CommandIntent:
        if parsed.has_option("--allow-empty"):
            return CommandIntent(
                command="commit",
                operations=(CommandOperation("UnsupportedCommand", {"command": "commit"}),),
            )
        operations: list[CommandOperation] = []
        if parsed.has_option("-a") or parsed.has_option("--all"):
            operations.append(CommandOperation("StageTrackedChangesOnly", {"paths": ()}))
        operations.append(
            CommandOperation(
                "AmendCommit" if parsed.has_option("--amend") else "CreateCommit",
                {
                    "message": parsed.message,
                    "no_edit": parsed.has_option("--no-edit"),
                },
            )
        )
        return CommandIntent(command="commit", operations=tuple(operations))

    def _map_diff(self, parsed: ParsedGitCommand) -> CommandIntent:
        staged = parsed.has_option("--staged") or parsed.has_option("--cached")
        head = bool(parsed.args and parsed.args[0] == "HEAD")
        name_only = parsed.has_option("--name-only")
        check = parsed.has_option("--check")
        conflict_side = next(
            (
                option.removeprefix("--")
                for option in ("--ours", "--theirs", "--base")
                if parsed.has_option(option)
            ),
            None,
        )
        branch_range = parsed.args[0] if len(parsed.args) == 1 and ".." in parsed.args[0] else None
        paths = tuple(arg for arg in parsed.pathspecs if arg != "HEAD")
        return CommandIntent(
            command="diff",
            operations=(
                CommandOperation(
                    "InspectDiff",
                    {
                        "staged": staged,
                        "head": head,
                        "name_only": name_only,
                        "check": check,
                        "conflict_side": conflict_side,
                        "paths": () if branch_range else paths,
                        "range": branch_range,
                    },
                ),
            ),
            diagnostic_metadata=(
                "inspected_conflict_marker_check"
                if check
                else "inspected_conflict_side"
                if conflict_side
                else "inspected_range_diff"
                if branch_range
                else "inspected_head_diff"
                if head
                else "inspected_staged_diff"
                if staged
                else "inspected_diff",
            ),
            output_mode=(
                "name_only"
                if name_only
                else "head"
                if head
                else "staged"
                if staged
                else "default"
            ),
        )

    def _map_merge(self, parsed: ParsedGitCommand) -> CommandIntent:
        if parsed.has_option("--abort"):
            return CommandIntent(
                command="merge",
                operations=(CommandOperation("AbortMerge", {}),),
            )
        if parsed.has_option("--continue"):
            return CommandIntent(
                command="merge",
                operations=(CommandOperation("ContinueMerge", {}),),
            )
        return CommandIntent(
            command="merge",
            operations=(CommandOperation("MergeBranch", {"branch": parsed.args[0]}),),
        )

    def _map_mergetool(self, parsed: ParsedGitCommand) -> CommandIntent:
        tool_values = parsed.options.get("--tool", ())
        return CommandIntent(
            command="mergetool",
            operations=(
                CommandOperation(
                    "RunMergeTool",
                    {
                        "tool": str(tool_values[-1]) if tool_values else None,
                        "paths": parsed.pathspecs,
                    },
                ),
            ),
        )

    def _map_checkout(self, parsed: ParsedGitCommand) -> CommandIntent:
        side = None
        if parsed.has_option("--ours"):
            side = "ours"
        elif parsed.has_option("--theirs"):
            side = "theirs"
        if side is None:
            return CommandIntent(
                command="checkout",
                operations=(CommandOperation("UnsupportedCommand", {"command": "checkout"}),),
            )
        return CommandIntent(
            command="checkout",
            operations=(
                CommandOperation(
                    "CheckoutConflictSide",
                    {
                        "side": side,
                        "paths": parsed.pathspecs,
                    },
                ),
            ),
        )

    def _map_config(self, parsed: ParsedGitCommand) -> CommandIntent:
        if parsed.has_option("--list") or parsed.has_option("-l"):
            return CommandIntent(
                command="config",
                operations=(CommandOperation("ListConfig", {}),),
                diagnostic_metadata=("inspected_config",),
            )
        return CommandIntent(
            command="config",
            operations=(
                CommandOperation(
                    "SetConfig",
                    {
                        "scope": "global" if parsed.has_option("--global") else "local",
                        "key": parsed.args[0],
                        "value": parsed.args[1],
                    },
                ),
            ),
        )

    def _map_fetch(self, parsed: ParsedGitCommand) -> CommandIntent:
        return CommandIntent(
            command="fetch",
            operations=(CommandOperation("FetchRemote", {"remote": parsed.args[0] if parsed.args else "origin"}),),
        )

    def _map_cherry_pick(self, parsed: ParsedGitCommand) -> CommandIntent:
        if parsed.has_option("--abort"):
            return CommandIntent(
                command="cherry-pick",
                operations=(CommandOperation("AbortCherryPick", {}),),
            )
        return CommandIntent(
            command="cherry-pick",
            operations=(
                CommandOperation(
                    "CherryPickCommit",
                    {
                        "commit": parsed.args[0],
                        "no_commit": parsed.has_option("--no-commit") or parsed.has_option("-n"),
                    },
                ),
            ),
        )

    def _map_reset(self, parsed: ParsedGitCommand) -> CommandIntent:
        return CommandIntent(
            command="reset",
            operations=(
                CommandOperation(
                    "ResetHard",
                    {
                        "target": parsed.args[0],
                    },
                ),
            ),
        )

    def _map_revert(self, parsed: ParsedGitCommand) -> CommandIntent:
        return CommandIntent(
            command="revert",
            operations=(
                CommandOperation(
                    "RevertCommit",
                    {
                        "commit": parsed.args[0],
                        "no_edit": parsed.has_option("--no-edit"),
                    },
                ),
            ),
        )

    def _map_push(self, parsed: ParsedGitCommand) -> CommandIntent:
        remote = parsed.args[0] if parsed.args else "origin"
        branch = parsed.args[1] if len(parsed.args) > 1 else None
        return CommandIntent(
            command="push",
            operations=(
                CommandOperation(
                    "PushBranch",
                    {
                        "remote": remote,
                        "branch": branch,
                        "set_upstream": parsed.has_option("-u"),
                    },
                ),
            ),
        )

    def _map_rebase(self, parsed: ParsedGitCommand) -> CommandIntent:
        if parsed.has_option("--abort"):
            return CommandIntent(
                command="rebase",
                operations=(CommandOperation("AbortRebase", {}),),
            )
        if parsed.has_option("--continue"):
            return CommandIntent(
                command="rebase",
                operations=(CommandOperation("ContinueRebase", {}),),
            )
        return CommandIntent(
            command="rebase",
            operations=(
                CommandOperation(
                    "StartRebase",
                    {
                        "target": parsed.args[0],
                        "interactive": parsed.has_option("-i"),
                    },
                ),
            ),
        )

    def _map_merge_base(self, parsed: ParsedGitCommand) -> CommandIntent:
        return CommandIntent(
            command="merge-base",
            operations=(
                CommandOperation(
                    "InspectMergeBase",
                    {
                        "left": parsed.args[0],
                        "right": parsed.args[1],
                    },
                ),
            ),
            diagnostic_metadata=("inspected_merge_base",),
        )

    def _map_rev_list(self, parsed: ParsedGitCommand) -> CommandIntent:
        return CommandIntent(
            command="rev-list",
            operations=(
                CommandOperation(
                    "InspectRevListCount",
                    {
                        "range": parsed.args[0],
                    },
                ),
            ),
            diagnostic_metadata=("inspected_rev_list",),
        )

    def _map_switch(self, parsed: ParsedGitCommand) -> CommandIntent:
        if parsed.has_option("-c"):
            return CommandIntent(
                command="switch",
                operations=(
                    CommandOperation(
                        "CreateAndSwitchBranch",
                        {
                            "branch": parsed.args[0],
                            "start_point": parsed.args[1] if len(parsed.args) > 1 else None,
                        },
                    ),
                ),
            )
        return CommandIntent(
            command="switch",
            operations=(CommandOperation("SwitchBranch", {"branch": parsed.args[0]}),),
        )

    def _map_log(self, parsed: ParsedGitCommand) -> CommandIntent:
        oneline = parsed.has_option("--oneline")
        graph = parsed.has_option("--graph")
        all_refs = parsed.has_option("--all")
        count_values = parsed.options.get("-n", ()) + parsed.options.get("--max-count", ())
        limit = int(str(count_values[-1])) if count_values else None
        return CommandIntent(
            command="log",
            operations=(
                CommandOperation(
                    "InspectLog",
                    {"oneline": oneline, "graph": graph, "all": all_refs, "limit": limit},
                ),
            ),
            diagnostic_metadata=("inspected_log",),
            output_mode="oneline_graph_all"
            if oneline and graph and all_refs
            else "oneline"
            if oneline
            else "default",
        )

    def _map_show(self, parsed: ParsedGitCommand) -> CommandIntent:
        return CommandIntent(
            command="show",
            operations=(
                CommandOperation(
                    "InspectObject",
                    {
                        "target": parsed.args[0] if parsed.args else "HEAD",
                        "name_only": parsed.has_option("--name-only"),
                    },
                ),
            ),
            diagnostic_metadata=("inspected_show",),
        )

    def _map_branch(self, parsed: ParsedGitCommand) -> CommandIntent:
        if not parsed.args:
            return CommandIntent(
                command="branch",
                operations=(
                    CommandOperation(
                        "InspectBranchList",
                        {"verbose": parsed.has_option("-v") or parsed.has_option("-vv")},
                    ),
                ),
                diagnostic_metadata=("inspected_branch_list",),
                output_mode="verbose"
                if parsed.has_option("-v") or parsed.has_option("-vv")
                else "default",
            )
        return CommandIntent(
            command="branch",
            operations=(CommandOperation("UnsupportedCommand", {"command": "branch"}),),
        )

    def _map_restore(self, parsed: ParsedGitCommand) -> CommandIntent:
        return CommandIntent(
            command="restore",
            operations=(
                CommandOperation(
                    "RestoreStaged" if parsed.has_option("--staged") else "RestoreWorkingTree",
                    {"paths": parsed.pathspecs},
                ),
            ),
        )

    def _map_rm(self, parsed: ParsedGitCommand) -> CommandIntent:
        return CommandIntent(
            command="rm",
            operations=(
                CommandOperation(
                    "RemovePaths",
                    {
                        "paths": parsed.pathspecs,
                        "cached": parsed.has_option("--cached"),
                        "recursive": parsed.has_option("-r"),
                    },
                ),
            ),
        )

    def _map_remote(self, parsed: ParsedGitCommand) -> CommandIntent:
        if not parsed.args:
            return CommandIntent(
                command="remote",
                operations=(
                    CommandOperation(
                        "InspectRemoteList",
                        {"verbose": parsed.has_option("-v") or parsed.has_option("--verbose")},
                    ),
                ),
                diagnostic_metadata=("inspected_remote_list",),
                output_mode="verbose"
                if parsed.has_option("-v") or parsed.has_option("--verbose")
                else "default",
            )
        return CommandIntent(
            command="remote",
            operations=(
                CommandOperation("UnsupportedRemoteAction", {"action": parsed.args[0]}),
            ),
        )

    def _map_reflog(self, parsed: ParsedGitCommand) -> CommandIntent:
        return CommandIntent(
            command="reflog",
            operations=(CommandOperation("InspectReflog", {}),),
            diagnostic_metadata=("inspected_reflog",),
        )

    def _map_check_ignore(self, parsed: ParsedGitCommand) -> CommandIntent:
        return CommandIntent(
            command="check-ignore",
            operations=(CommandOperation("InspectIgnoredPath", {"path": parsed.pathspecs[0]}),),
            diagnostic_metadata=("inspected_check_ignore",),
        )

    def _map_ls_files(self, parsed: ParsedGitCommand) -> CommandIntent:
        return CommandIntent(
            command="ls-files",
            operations=(
                CommandOperation(
                    "InspectTrackedFiles",
                    {"unmerged": parsed.has_option("-u") or parsed.has_option("--unmerged")},
                ),
            ),
            diagnostic_metadata=(
                "inspected_unmerged_index"
                if parsed.has_option("-u") or parsed.has_option("--unmerged")
                else "inspected_ls_files",
            ),
        )
