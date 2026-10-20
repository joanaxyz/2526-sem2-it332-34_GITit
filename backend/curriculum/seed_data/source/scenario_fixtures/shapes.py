"""Small builders shared by the wave scenario fixture modules."""

from __future__ import annotations

from typing import Any


def commit(commit_id: str, message: str, parents: list[str], tree: dict[str, Any]) -> dict:
    return {"id": commit_id, "message": message, "parents": parents, "tree": tree}


def repo(
    *,
    commits: list[dict] | None = None,
    branches: dict[str, str] | None = None,
    head: str = "main",
    working_tree: dict[str, Any] | None = None,
    staging: dict[str, Any] | None = None,
    initialized: bool = True,
    **extra: Any,
) -> dict[str, Any]:
    return {
        "repository_initialized": initialized,
        "commits": commits or [],
        "branches": branches or {},
        "head": {"type": "branch", "name": head},
        "staging": staging or {},
        "working_tree": working_tree or {},
        "conflicts": [],
        **extra,
    }


def modified(content: str) -> dict[str, str]:
    return {"status": "modified", "content": content}


def untracked(content: str) -> dict[str, str]:
    return {"status": "untracked", "content": content}


def hunks(*tokens: str) -> dict[str, Any]:
    return {"status": "modified", "hunks": list(tokens)}


def tip(branch: str, **conditions: Any) -> dict[str, Any]:
    """A ``branch_tip_commit`` rule; ``branch`` may name an ancestor (``main~1``)."""
    return {"type": "branch_tip_commit", "branch": branch, **conditions}


def amended(old: str) -> list[dict[str, Any]]:
    return [
        {"type": "operation_metadata_equals", "key": "last_amend_replaced_commit", "value": old},
        {"type": "branch_tip_replaces_commit", "old": old},
        {"type": "commit_replaced_by_amend", "old": old},
    ]


def remote_fixture(url: str, commits: list[dict], tip_id: str) -> dict[str, Any]:
    return {
        "url": url,
        "default_branch": "origin/main",
        "branches": {"origin/main": tip_id},
        "commits": commits,
    }


ORIGIN = "https://example.test/team/{name}.git"


def origin(
    name: str,
    *,
    branches: dict[str, str],
    updates: dict[str, str] | None = None,
    tracking: dict[str, str] | None = None,
    stale: list[str] | None = None,
) -> dict[str, Any]:
    """An ``origin`` remote: fetched tips, tips the server has moved to, and refs it deleted."""
    remote: dict[str, Any] = {
        "remotes": {"origin": ORIGIN.format(name=name)},
        "remote_branches": branches,
        "upstream_tracking": tracking or {},
    }
    if updates:
        remote["remote_updates"] = updates
    if stale:
        remote["remote_stale_branches"] = stale
    return remote


def clean(head: str, *rules: dict[str, Any], **extra: Any) -> dict[str, Any]:
    """Requirements that finish on ``head`` with nothing staged or modified."""
    return {
        "head_branch": head,
        "staging_empty": True,
        "working_tree_clean": True,
        "rules": list(rules),
        **extra,
    }


def points_to(branch: str, commit_id: str) -> dict[str, Any]:
    return {"type": "branch_points_to", "branch": branch, "commit": commit_id}


def matches_origin(branch: str) -> dict[str, Any]:
    return {"type": "remote_branch_matches_local", "remote_branch": f"origin/{branch}", "branch": branch}
