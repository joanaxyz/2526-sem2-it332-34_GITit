"""Versioned command and command-form coverage matrix for curriculum v3."""

from __future__ import annotations

import json
from pathlib import Path

from curriculum.seed_data.command_catalog import COMMAND_CATALOG

_INVENTORY = Path(__file__).resolve().parents[1] / "git_inventory" / "baseline.json"

_ENGINE_COMMANDS = {
    "add", "bisect", "blame", "branch", "cat-file", "check-ignore", "checkout",
    "cherry-pick", "clone", "commit", "config", "count-objects", "describe", "diff",
    "fetch", "for-each-ref", "fsck", "grep", "init", "log", "ls-files", "ls-tree",
    "merge", "merge-base", "merge-tree", "mergetool", "pull", "push", "range-diff",
    "rebase", "reflog", "remote", "reset", "restore", "revert", "rerere", "rev-list",
    "rev-parse", "rm", "shortlog", "show", "show-ref", "sparse-checkout", "stash",
    "submodule", "switch", "symbolic-ref", "tag", "verify-commit", "verify-tag", "worktree",
}

_STATEFUL_COMMANDS = {
    "add", "branch", "checkout", "cherry-pick", "clone", "commit", "config", "fetch",
    "init", "merge", "mergetool", "pull", "push", "rebase", "remote", "reset", "restore",
    "revert", "rm", "stash", "switch", "tag",
}

_DEMONSTRATION_COMMANDS = {
    "archimport", "citool", "cvsexportcommit", "cvsimport", "cvsserver", "daemon",
    "gitk", "gitweb", "gui", "http-backend", "imap-send", "instaweb", "p4", "quiltimport",
    "send-email", "svn", "update-server-info", "latexdiff",
}

_PRACTICE_PLUMBING = {
    "apply", "cat-file", "checkout-index", "commit-graph", "commit-tree", "count-objects",
    "diff-files", "diff-index", "diff-tree", "fast-export", "fast-import", "for-each-ref",
    "fsck", "hash-object", "ls-files", "ls-remote", "ls-tree", "merge-base", "merge-file",
    "mktag", "mktree", "multi-pack-index", "name-rev", "pack-objects", "read-tree", "refs",
    "replace", "rev-list", "rev-parse", "show-index", "show-ref", "symbolic-ref", "update-index",
    "update-ref", "verify-pack", "write-tree",
}

_DEPRECATED = {
    "annotate": "Use git blame for the actively taught line-attribution workflow.",
    "filter-branch": "Prefer git filter-repo where available; filter-branch remains a controlled legacy demonstration.",
    "whatchanged": "Use git log with diff options for modern history inspection.",
}


def _catalog_index() -> dict[str, dict]:
    return {skill["base_command"].removeprefix("git "): skill for skill in COMMAND_CATALOG}


def _coverage_level(name: str, category: str, in_catalog: bool) -> str:
    if name in _DEMONSTRATION_COMMANDS:
        return "demonstration"
    if category.startswith("Low-level Commands / Internal Helpers"):
        return "reference"
    if category.startswith("Developer-facing") or category.startswith("User-facing"):
        return "reference"
    if name in _PRACTICE_PLUMBING:
        return "practice"
    if in_catalog and category in {
        "Main Porcelain Commands",
        "Ancillary Commands / Manipulators",
        "Ancillary Commands / Interrogators",
    }:
        return "mastery"
    if category == "Main Porcelain Commands":
        return "practice"
    if category.startswith("Interacting with Others"):
        return "demonstration"
    if category.startswith("Low-level Commands"):
        return "practice"
    return "reference"


def _visual_effect(name: str) -> str:
    if name in _STATEFUL_COMMANDS:
        return "working tree, index, commit, branch, tag, or remote-ref transition"
    if name in {"update-ref", "symbolic-ref", "commit-tree", "write-tree", "read-tree"}:
        return "object, index, or ref transition"
    if name in _ENGINE_COMMANDS:
        return "diagnostic evidence followed by a scored DAG/ref change in the containing incident"
    return "controlled output, library diagram, or sandbox demonstration"


def build_command_coverage() -> list[dict]:
    inventory = json.loads(_INVENTORY.read_text())
    catalog = _catalog_index()
    rows: list[dict] = []
    for item in inventory["commands"]:
        name = item["name"]
        skill = catalog.get(name)
        usages = list(skill.get("usages", [])) if skill else []
        module = (usages[0].get("module") if usages else None) or (skill.get("module") if skill else None)
        level = _coverage_level(name, item["category"], skill is not None)
        introduced_story = (
            "arcane-spire"
            if module and not module.startswith(("frost-", "skyline-"))
            else "frostbound-citadel"
            if module and module.startswith("frost-")
            else "neon-backstreets"
        )
        chapter = module or "skyline-command-laboratory"
        rows.append(
            {
                "command": item["command"],
                "category": item["category"],
                "coverage_level": level,
                "introduced_story": introduced_story,
                "introduced_chapter": chapter,
                "adventure_level_slugs": [],
                "challenge_slugs": [f"{chapter}-challenge"] if level in {"mastery", "practice"} else [],
                "later_retrieval_slugs": [],
                "engine_support": (
                    "stateful" if name in _STATEFUL_COMMANDS else "diagnostic" if name in _ENGINE_COMMANDS else "sandbox_or_reference"
                ),
                "backend_verification": (
                    "transition_verifier" if name in _STATEFUL_COMMANDS else "diagnostic_classifier" if name in _ENGINE_COMMANDS else "not_reward_bearing"
                ),
                "visual_effect": _visual_effect(name),
                "platform_constraints": (
                    "platform or external-tool dependent" if name in _DEMONSTRATION_COMMANDS else "none recorded"
                ),
                "deprecation_status": "legacy_or_superseded" if name in _DEPRECATED else "current",
                "replacement_guidance": _DEPRECATED.get(name, ""),
                "official_version": inventory["git_version"],
                "notes": item["summary"],
            }
        )
    return rows


def build_command_form_coverage() -> list[dict]:
    rows: list[dict] = []
    for skill in COMMAND_CATALOG:
        for usage in skill.get("usages", []):
            chapter = usage.get("module", skill["module"])
            rows.append(
                {
                    "command": skill["base_command"],
                    "usage_form": usage["usage_form"],
                    "introduced_chapter": chapter,
                    "engine_support": "reference" if usage.get("is_playable") is False else "playable",
                    "label": usage["label"],
                }
            )
    return rows


COMMAND_COVERAGE = build_command_coverage()
COMMAND_FORM_COVERAGE = build_command_form_coverage()

__all__ = ["COMMAND_COVERAGE", "COMMAND_FORM_COVERAGE", "build_command_coverage"]
