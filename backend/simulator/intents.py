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

    def _map_status(self, parsed: ParsedGitCommand) -> CommandIntent:
        short = (
            parsed.has_option("-s")
            or parsed.has_option("--short")
            or parsed.has_option("--porcelain")
        )
        return CommandIntent(
            command="status",
            operations=(CommandOperation("InspectStatus", {"short": short}),),
            diagnostic_metadata=("inspected_short_status" if short else "inspected_status",),
            output_mode="short" if short else "default",
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
                operations=(CommandOperation("IntentToAdd", {"paths": parsed.pathspecs}),),
            )
        return CommandIntent(
            command="add",
            operations=(CommandOperation("StagePathspecs", {"paths": parsed.pathspecs}),),
        )

    def _map_commit(self, parsed: ParsedGitCommand) -> CommandIntent:
        operations: list[CommandOperation] = []
        if parsed.has_option("-a") or parsed.has_option("--all"):
            operations.append(CommandOperation("StageTrackedChangesOnly", {"paths": ()}))
        operations.append(
            CommandOperation(
                "AmendCommit" if parsed.has_option("--amend") else "CreateCommit",
                {
                    "message": parsed.message,
                    "allow_empty": parsed.has_option("--allow-empty"),
                    "no_edit": parsed.has_option("--no-edit"),
                },
            )
        )
        return CommandIntent(command="commit", operations=tuple(operations))

    def _map_diff(self, parsed: ParsedGitCommand) -> CommandIntent:
        staged = parsed.has_option("--staged") or parsed.has_option("--cached")
        return CommandIntent(
            command="diff",
            operations=(
                CommandOperation("InspectDiff", {"staged": staged, "paths": parsed.pathspecs}),
            ),
            diagnostic_metadata=("inspected_staged_diff" if staged else "inspected_diff",),
            output_mode="staged" if staged else "default",
        )

    def _map_log(self, parsed: ParsedGitCommand) -> CommandIntent:
        oneline = parsed.has_option("--oneline")
        graph = parsed.has_option("--graph")
        all_refs = parsed.has_option("--all")
        return CommandIntent(
            command="log",
            operations=(
                CommandOperation(
                    "InspectLog", {"oneline": oneline, "graph": graph, "all": all_refs}
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
                    "InspectObject", {"target": parsed.args[0] if parsed.args else "HEAD"}
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
        if parsed.has_option("-d") or parsed.has_option("-D"):
            return CommandIntent(
                command="branch",
                operations=(
                    CommandOperation(
                        "DeleteBranch",
                        {"name": parsed.args[0], "force": parsed.has_option("-D")},
                    ),
                ),
            )
        return CommandIntent(
            command="branch",
            operations=(
                CommandOperation(
                    "CreateBranch",
                    {
                        "name": parsed.args[0],
                        "start_point": parsed.args[1] if len(parsed.args) > 1 else None,
                    },
                ),
            ),
        )

    def _map_checkout(self, parsed: ParsedGitCommand) -> CommandIntent:
        if parsed.has_option("-b"):
            return CommandIntent(
                command="checkout",
                operations=(
                    CommandOperation(
                        "CreateAndSwitchBranch",
                        {
                            "name": parsed.args[0],
                            "start_point": parsed.args[1] if len(parsed.args) > 1 else None,
                        },
                    ),
                ),
            )
        return CommandIntent(
            command="checkout",
            operations=(CommandOperation("SwitchBranch", {"name": parsed.args[0]}),),
        )

    def _map_switch(self, parsed: ParsedGitCommand) -> CommandIntent:
        if parsed.has_option("-c"):
            return CommandIntent(
                command="switch",
                operations=(
                    CommandOperation(
                        "CreateAndSwitchBranch",
                        {
                            "name": parsed.args[0],
                            "start_point": parsed.args[1] if len(parsed.args) > 1 else None,
                        },
                    ),
                ),
            )
        return CommandIntent(
            command="switch",
            operations=(CommandOperation("SwitchBranch", {"name": parsed.args[0]}),),
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

    def _map_reset(self, parsed: ParsedGitCommand) -> CommandIntent:
        mode = (
            "soft"
            if parsed.has_option("--soft")
            else "hard"
            if parsed.has_option("--hard")
            else "mixed"
        )
        if mode == "mixed" and parsed.args and parsed.args[0] == "HEAD" and len(parsed.args) > 1:
            return CommandIntent(
                command="reset",
                operations=(CommandOperation("UnstagePaths", {"paths": tuple(parsed.args[1:])}),),
            )
        return CommandIntent(
            command="reset",
            operations=(CommandOperation("ResetHead", {"mode": mode, "target": parsed.args[-1]}),),
        )

    def _map_rm(self, parsed: ParsedGitCommand) -> CommandIntent:
        return CommandIntent(
            command="rm",
            operations=(
                CommandOperation(
                    "RemovePaths",
                    {"paths": parsed.pathspecs, "cached": parsed.has_option("--cached")},
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
        action = parsed.args[0]
        if action == "add":
            return CommandIntent(
                command="remote",
                operations=(
                    CommandOperation("AddRemote", {"name": parsed.args[1], "url": parsed.args[2]}),
                ),
            )
        if action in {"remove", "rm"}:
            return CommandIntent(
                command="remote",
                operations=(CommandOperation("RemoveRemote", {"name": parsed.args[1]}),),
            )
        if action == "rename":
            return CommandIntent(
                command="remote",
                operations=(
                    CommandOperation(
                        "RenameRemote", {"old": parsed.args[1], "new": parsed.args[2]}
                    ),
                ),
            )
        return CommandIntent(
            command="remote",
            operations=(CommandOperation("UnsupportedRemoteAction", {"action": action}),),
        )

    def _map_reflog(self, parsed: ParsedGitCommand) -> CommandIntent:
        return CommandIntent(
            command="reflog",
            operations=(CommandOperation("InspectReflog", {}),),
            diagnostic_metadata=("inspected_reflog",),
        )
