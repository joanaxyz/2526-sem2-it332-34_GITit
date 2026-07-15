"""Cheap backend-side verification for client-submitted Git transitions.

The browser simulator still owns instant UI feedback. This verifier mirrors the
supported mutating command transitions that can affect persisted progress/rewards
without shelling out to Git, so a forged client next_state cannot silently earn
completion.
"""

from __future__ import annotations

from common.exceptions import BadRequest
from simulator.services import RepositoryStateSimulator

from .assertions import TransitionAssertionMixin
from .commit_history import CommitHistoryVerificationMixin
from .init_clone_remote import InitCloneRemoteVerificationMixin
from .merge_stash import MergeStashVerificationMixin
from .refs import RefVerificationMixin
from .staging import StagingVerificationMixin


class ClientTransitionVerifier(
    TransitionAssertionMixin,
    InitCloneRemoteVerificationMixin,
    StagingVerificationMixin,
    RefVerificationMixin,
    CommitHistoryVerificationMixin,
    MergeStashVerificationMixin,
):
    """Validate that a normalized next_state is plausible for one Git command."""

    NO_COMMIT_CREATION_FAMILIES = {
        "add",
        "restore",
        "rm",
        "reset",
        "switch",
        "checkout",
        "branch",
        "tag",
        "stash",
        "remote",
        "push",
        "config",
        "init",
        "mergetool",
    }
    ADD_IMMUTABLE_KEYS = {
        "repository_initialized",
        "commits",
        "branches",
        "head",
        "remotes",
        "remote_branches",
        "upstream_tracking",
        "tags",
        "remote_tags",
        "stash_stack",
        "reflog",
        "replaced_commits",
        "config",
    }
    INDEX_WORKTREE_IMMUTABLE_KEYS = {
        "commits",
        "branches",
        "head",
        "remotes",
        "remote_branches",
        "upstream_tracking",
        "tags",
        "remote_tags",
        "stash_stack",
        "reflog",
        "replaced_commits",
        "config",
    }
    REF_ONLY_IMMUTABLE_KEYS = {
        "commits",
        "staging",
        "working_tree",
        "conflicts",
        "conflict_details",
        "partial_hunks",
        "remotes",
        "remote_branches",
        "tags",
        "remote_tags",
        "stash_stack",
        "replaced_commits",
        "config",
    }

    VERIFY_HANDLERS = {
        "init": "_verify_init",
        "clone": "_verify_clone",
        "add": "_verify_add",
        "rm": "_verify_rm",
        "restore": "_verify_restore",
        "reset": "_verify_reset",
        "branch": "_verify_branch",
        "switch": "_verify_switch",
        "checkout": "_verify_checkout",
        "tag": "_verify_tag",
        "config": "_verify_config",
        "remote": "_verify_remote",
        "fetch": "_verify_fetch",
        "pull": "_verify_pull",
        "push": "_verify_push",
        "stash": "_verify_stash",
        "merge": "_verify_merge",
        "mergetool": "_verify_mergetool",
        "rebase": "_verify_rebase",
        "commit": "_verify_commit",
        "revert": "_verify_revert",
        "cherry-pick": "_verify_cherry_pick",
    }

    def __init__(self) -> None:
        self.tools = RepositoryStateSimulator()
        self.normalizer = self.tools.normalizer

    def verify(
        self,
        *,
        command: str,
        previous_state: dict,
        next_state: dict,
        command_family: str,
        exit_code: int,
    ) -> None:
        # Failed commands should not mutate persisted state. The browser can still
        # display stdout/stderr instantly, but the DB state remains authoritative.
        if exit_code != 0:
            # Some Git operations, most notably a merge that stops on conflicts,
            # intentionally mutate the index/worktree while returning a non-zero
            # code. Verify those exact transitions instead of blanket-rejecting
            # them; keep every other failed command immutable.
            if command_family in {"merge", "pull"}:
                try:
                    if command_family == "merge":
                        self._verify_merge(command=command, previous_state=previous_state, next_state=next_state)
                    else:
                        self._verify_pull(command=command, previous_state=previous_state, next_state=next_state)
                    return
                except BadRequest:
                    # A merge/pull can stop with conflicts and mutate state, or
                    # fail before changing anything. The latter is accepted only
                    # when the submitted state is unchanged.
                    self._require_same_state(
                        previous_state,
                        next_state,
                        "Failed command executions cannot mutate repository state.",
                    )
                    return
            self._require_same_state(
                previous_state,
                next_state,
                "Failed command executions cannot mutate repository state.",
            )
            return

        if command_family in self.NO_COMMIT_CREATION_FAMILIES:
            self._require_same_key("commits", previous_state, next_state)

        handler_name = self.VERIFY_HANDLERS.get(command_family)
        if handler_name is None:
            raise BadRequest(f"Unsupported mutating command family cannot persist state: {command_family}.")
        getattr(self, handler_name)(command=command, previous_state=previous_state, next_state=next_state)
