from __future__ import annotations

import re
from typing import Any


def normalize_command_text(command: str) -> str:
    return " ".join(str(command).strip().split()).lower()


COMMAND_KEY_PREFIXES: tuple[tuple[str, str], ...] = (
    ("git diff --staged", "git-diff-staged"),
    ("git diff --cached", "git-diff-staged"),
    ("git add -p", "git-add-p"),
    ("git commit --amend", "git-commit-amend"),
    ("git restore --staged", "git-restore-staged"),
    ("git rm --cached", "git-rm-cached"),
    ("git cherry-pick", "git-cherry-pick"),
    ("git checkout --ours", "git-checkout-conflict-side"),
    ("git checkout --theirs", "git-checkout-conflict-side"),
    ("git checkout -b", "git-checkout-b"),
    ("git mergetool", "git-mergetool"),
    ("git merge --squash", "git-merge-squash"),
    ("git merge", "git-merge"),
    ("git switch", "git-switch"),
    ("git stash", "git-stash"),
    ("git push", "git-push"),
    ("git pull", "git-pull"),
    ("git config", "git-config"),
    ("git fetch", "git-fetch"),
    ("git remote -v", "git-remote-v"),
    ("git remote", "git-remote-v"),
    ("git log", "git-log"),
    ("git status", "git-status"),
    ("git diff", "git-diff"),
    ("git show", "git-show"),
    ("git branch", "git-branch"),
    ("git reflog", "git-reflog"),
    ("git check-ignore", "git-check-ignore"),
    ("git ls-files", "git-ls-files"),
    ("git init", "git-init"),
    ("git clone", "git-clone"),
    ("git add", "git-add"),
    ("git commit", "git-commit"),
    ("git restore", "git-restore"),
    (".gitignore", "gitignore"),
)


# For each command key, option and argument sections that should always appear in the
# preview regardless of which specific command syntax triggered the key. These teach
# the vocabulary (flags, placeholders, argument semantics) that students need when
# any variant of the command is used in an authored scenario.
COMMAND_KEY_ALWAYS_INCLUDED_SECTION_IDS: dict[str, list[str]] = {
    "git-status": ["option-s-short", "option-porcelain", "option-sb", "option-ignored"],
    "git-log": ["option-oneline", "option-graph", "option-all", "option-count"],
    "git-diff": [
        "option-staged-cached",
        "option-head",
        "option-name-only",
        "option-conflict-sides",
        "option-check",
        "argument-path",
    ],
    "git-diff-staged": ["option-staged-cached"],
    "git-show": ["argument-commit"],
    "git-branch": ["option-v", "option-a-all", "option-d-delete"],
    "git-switch": ["option-c-create", "option-detach", "argument-branch"],
    "git-checkout-b": ["option-b-create", "argument-branch", "argument-start-point"],
    "git-stash": ["option-pop", "option-apply", "option-drop", "option-list"],
    "git-push": ["option-u-upstream", "option-force-with-lease", "option-delete", "argument-remote", "argument-branch"],
    "git-pull": ["option-rebase", "argument-remote", "argument-branch"],
    "git-merge-squash": ["option-squash", "argument-branch"],
    "git-remote-v": ["option-v-verbose"],
    "git-check-ignore": ["option-v", "argument-path"],
    "git-init": ["option-b-initial-branch", "option-q-quiet", "argument-directory"],
    "git-clone": ["option-b-branch", "option-depth", "argument-url", "argument-directory", "argument-branch", "argument-number"],
    "git-add": ["option-a-all", "option-u-update", "option-p-patch", "argument-path"],
    "git-add-p": ["option-p-patch", "argument-path"],
    "git-rm-cached": ["option-cached", "argument-path"],
    "git-commit": ["option-m-message", "option-a-all", "option-amend"],
    "git-commit-amend": ["option-amend", "option-no-edit", "option-m-message"],
    "git-restore": ["argument-path"],
    "git-restore-staged": ["option-staged", "argument-path"],
    "git-merge": ["option-abort", "option-continue", "argument-branch"],
    "git-checkout-conflict-side": ["option-ours", "option-theirs", "argument-path"],
    "git-mergetool": ["option-tool"],
    "git-config": ["option-global", "argument-key", "argument-value"],
    "git-fetch": ["argument-remote", "option-prune"],
    "git-cherry-pick": ["option-no-commit", "option-abort", "argument-commit"],
    "git-ls-files": ["option-unmerged"],
}


def library_key_for_command(command: str) -> str:
    normalized = normalize_command_text(command)
    for prefix, key in COMMAND_KEY_PREFIXES:
        if normalized == prefix or normalized.startswith(f"{prefix} "):
            return key
    return normalized.replace(" ", "-").replace("/", "-").replace(".", "dot")


def base_command_for_command(command: str) -> str:
    normalized = normalize_command_text(command)
    if not normalized:
        return ""
    if normalized == ".gitignore":
        return ".gitignore"
    parts = normalized.split()
    if parts and parts[0] == "git":
        return "git" if len(parts) == 1 else f"git {parts[1]}"
    return str(command).strip()


def _slug(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", normalize_command_text(value))
    return slug.strip("-") or "section"


def _paragraph(body: str) -> dict[str, Any]:
    return {"type": "paragraph", "body": body}


def _commands(items: list[str]) -> dict[str, Any]:
    return {"type": "command", "title": "Command syntax", "items": items}


def _bullets(title: str, items: list[str]) -> dict[str, Any]:
    return {"type": "bullet_list", "title": title, "items": items}


def _warning(body: str) -> dict[str, Any]:
    return {"type": "warning", "title": "Watch for", "body": body}


def _callout(title: str, body: str) -> dict[str, Any]:
    return {"type": "callout", "title": title, "body": body}


def _terminal(body: str) -> dict[str, Any]:
    return {"type": "terminal_output", "title": "Typical output", "body": body}


def _diagram(
    *,
    kind: str,
    title: str = "",
    caption: str = "",
    nodes: list[dict[str, Any]] | None = None,
    edges: list[dict[str, Any]] | None = None,
    legend: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Authorable diagram block.

    ``kind`` selects how the Chapter Book renders it:
      - ``"dag"`` - a commit graph. ``nodes`` are ``{id, label, lane, type}``
        (type one of commit/head/branch/merge); ``edges`` are ``{from, to}``.
      - ``"flow"`` - left-to-right stages (e.g. working tree -> staging -> repo).
        ``nodes`` are ``{id, label, accent}``; ``edges`` are ``{from, to, label}``.

    The payload is stored verbatim, so new diagram kinds can be authored without a
    backend change as long as the renderer learns to read them.
    """
    block: dict[str, Any] = {"type": "diagram", "diagram_kind": kind}
    if title:
        block["title"] = title
    if caption:
        block["caption"] = caption
    if nodes is not None:
        block["nodes"] = nodes
    if edges is not None:
        block["edges"] = edges
    if legend:
        block["legend"] = legend
    return block

def command_syntax_section_id(command: str) -> str:
    value = str(command).replace("=", " equals ").replace('"', " quote ")
    return f"syntax-{_slug(value)}"
