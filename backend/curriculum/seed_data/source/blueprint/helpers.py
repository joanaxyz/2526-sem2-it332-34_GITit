"""Shared helpers for authored blueprint seed data."""

from __future__ import annotations


def _wave(
    slug: str,
    usage: str,
    title: str,
    solution: list[str],
    *,
    required: list[str] | None = None,
    forms: list[str] | None = None,
    state: str = "worktree",
    story: str | None = None,
    details: list[dict] | None = None,
    checks: list[dict] | None = None,
    evaluation: dict | None = None,
    workspace_files: list[dict] | None = None,
) -> dict:
    wave = {
        "slug": slug,
        "id": slug,
        "usage": usage,
        "title": title,
        "solution": solution,
        "required": required or [_required_from_usage(usage)],
        "forms": forms or [],
        "state": state,
    }
    if story:
        wave["story"] = story
    if details:
        wave["details"] = details
    if checks:
        wave["checks"] = checks
    if evaluation:
        wave["evaluation"] = evaluation
    if workspace_files:
        wave["workspace_files"] = workspace_files
    return wave

def _required_from_usage(usage: str) -> str:
    family = usage.split("/", 1)[0]
    command_map = {
        "git-cherry-pick": "git cherry-pick",
        "git-checkout-conflict": "git checkout",
        "git-diff-conflict": "git diff",
        "git-ls-files": "git ls-files",
        "git-merge-base": "git merge-base",
    }
    if family in command_map:
        return command_map[family]
    if family.startswith("git-"):
        return "git " + family[4:]
    return family.replace("-", " ")

