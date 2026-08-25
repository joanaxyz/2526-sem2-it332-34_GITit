"""Neutral repository fixtures shared by advanced adventure and challenge specs.

This module owns reusable repository state, evaluation requirements, and
placeholder rendering. Authored ``v3_*`` ledgers consume these helpers but are
never imported here.
"""

from __future__ import annotations

from curriculum.seed_data.spec_helpers import commit, repo


def _base_commits(prefix: str) -> list[dict]:
    return [
        commit(
            f"{prefix}0",
            "Establish shared foundation",
            [],
            {
                "README.md": "Operations repository\n",
                "src/app.ts": "export const mode = 'base'\n",
            },
        ),
        commit(
            f"{prefix}1",
            "Harden the main service",
            [f"{prefix}0"],
            {
                "README.md": "Operations repository\n",
                "src/app.ts": "export const mode = 'stable'\n",
                "src/health.ts": "export const healthy = true\n",
            },
        ),
        commit(
            f"{prefix}2",
            "Introduce the failing deployment",
            [f"{prefix}1"],
            {
                "README.md": "Operations repository\n",
                "src/app.ts": "export const mode = 'unsafe'\n",
                "src/health.ts": "export const healthy = false\n",
            },
        ),
        commit(
            f"{prefix}3",
            "Prepare isolated relay repair",
            [f"{prefix}0"],
            {
                "README.md": "Operations repository\n",
                "src/app.ts": "export const mode = 'base'\n",
                "src/relay.ts": "export const relay = 'repaired'\n",
            },
        ),
        commit(
            f"{prefix}4",
            "Draft earlier patch series",
            [f"{prefix}0"],
            {
                "README.md": "Operations repository\n",
                "src/app.ts": "export const mode = 'candidate-v1'\n",
            },
        ),
    ]


def _metadata(prefix: str) -> dict:
    return {
        "bisect_good": f"{prefix}0",
        "bisect_bad": f"{prefix}2",
        "first_bad_commit": f"{prefix}2",
        "rerere_paths": ["src/app.ts"],
        "rerere_before": "mode = unsafe",
        "rerere_after": "mode = stable",
        "worktrees": [
            {
                "path": "/workspace/repository",
                "commit": f"{prefix}2",
                "branch": "main",
            },
            {
                "path": "/workspace/hotfix",
                "commit": f"{prefix}3",
                "branch": "donor/relay",
            },
        ],
        "sparse_paths": ["src", "docs/runbooks"],
        "submodules": [
            {
                "commit": "a11ce00",
                "path": "vendor/telemetry",
                "describe": "heads/main",
                "initialized": True,
            }
        ],
        "signatures": {
            f"{prefix}1": {"signer": "Release Bot"},
            "v1.0": {"signer": "Release Bot"},
        },
    }


def build_advanced_story_state(prefix: str, *, mode: str) -> dict:
    """Build the shared advanced-story repository fixture for one strategy."""

    commits = _base_commits(prefix)
    branches = {
        "main": f"{prefix}2" if mode == "revert" else f"{prefix}1",
        "feature/work": f"{prefix}3",
        "donor/patch": f"{prefix}3",
        "old/series": f"{prefix}4",
    }
    state = repo(
        commits=commits,
        branches=branches,
        head="main",
        tags={"v1.0": {"target": f"{prefix}0", "annotated": True, "message": "stable base"}},
        remotes={"origin": "https://example.test/nexus/operations.git"},
        remote_branches={"origin/main": branches["main"]},
        upstream_tracking={"main": "origin/main"},
        config={"user.name": "Repository Marshal", "user.email": "marshal@example.test"},
        operation_metadata=_metadata(prefix),
    )
    if mode == "author":
        state["working_tree"] = {
            "src/repair.ts": {
                "status": "untracked",
                "content": "export const repair = 'verified'\n",
            }
        }
    return state


def build_advanced_story_requirements(
    branch: str,
    message: str,
    path: str | None = None,
) -> dict:
    """Build the shared end-state contract for advanced repair workflows."""

    latest = {"branch": branch, "message_contains": [message]}
    if path:
        latest["contains_paths"] = [path]
    return {
        "head_branch": branch,
        "latest_commit": latest,
        "working_tree_clean": True,
        "staging_empty": True,
        "min_commits_on_branch": {branch: 3},
        "rules": [
            {
                "type": "required_command_sequence",
                "commands": ["git tag", "git log"],
            }
        ],
    }


def render_advanced_story_command(command: str, prefix: str) -> str:
    """Render commit placeholders used by advanced authored commands."""

    return (
        command.replace("{p}", prefix)
        .replace("{head}", f"{prefix}2")
        .replace("{stable}", f"{prefix}1")
    )


__all__ = [
    "build_advanced_story_requirements",
    "build_advanced_story_state",
    "render_advanced_story_command",
]
