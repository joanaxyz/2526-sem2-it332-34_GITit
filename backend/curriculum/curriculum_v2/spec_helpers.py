"""Shared builders for authoring curriculum_v2 repository-state specs.

Both the adventure level specs (``adventure_levels.py``) and the challenge
specs (``challenges.py``) author initial repository states and evaluation
specs with these helpers.
"""

from __future__ import annotations

import copy


def commit(commit_id: str, message: str, parents: list[str] | None = None, tree: dict | None = None) -> dict:
    return {"id": commit_id, "message": message, "parents": parents or [], "tree": tree or {}}


def repo(
    *,
    commits: list[dict] | None = None,
    branches: dict | None = None,
    head: str = "main",
    working_tree: dict | None = None,
    staging: dict | None = None,
    conflicts: list[str] | None = None,
    **extra,
) -> dict:
    commits = copy.deepcopy(commits or [commit("c0", "Initial project", [], {"README.md": "Project notes"})])
    branches = copy.deepcopy(branches or {head: commits[-1]["id"] if commits else None})
    state = {
        "repository_initialized": True,
        "commits": commits,
        "branches": branches,
        "head": {"type": "branch", "name": head},
        "working_tree": copy.deepcopy(working_tree or {}),
        "staging": copy.deepcopy(staging or {}),
        "conflicts": list(conflicts or []),
    }
    state.update(copy.deepcopy(extra))
    return state


def uninitialized(working_tree: dict | None = None, **extra) -> dict:
    state = {
        "repository_initialized": False,
        "commits": [],
        "branches": {},
        "head": {"type": "none"},
        "working_tree": copy.deepcopy(working_tree or {"README.md": "Project notes"}),
        "staging": {},
        "conflicts": [],
    }
    state.update(copy.deepcopy(extra))
    return state


def ev(state_requirements: dict | None = None, *, required: list[str] | None = None, forbidden: list[str] | None = None) -> dict:
    return {
        "state_requirements": state_requirements or {},
        "process_requirements": {
            "required_commands": required or [],
            "forbidden_commands": forbidden or [],
        },
        "completion_policy": {"mode": "rules"},
    }


def meta_equals(key: str, value) -> dict:
    return {"type": "operation_metadata_equals", "key": key, "value": value}
