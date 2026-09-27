"""Plain-language ideas behind a guide, for learners meeting Git for the first time.

Concepts are chosen from what the next move changes in the repository, never
from a particular level, and each is shown until the learner has completed one
guide that explained it. The first guide a learner ever sees also explains
what a command is.
"""

from __future__ import annotations

from collections.abc import Iterable

# (title, text). Short, concrete, no Git jargon inside the definitions.
CONCEPTS: dict[str, tuple[str, str]] = {
    "commands": (
        "Commands",
        "You type a command in the terminal and press Enter. Git commands start with git, "
        "then the name of what you want Git to do.",
    ),
    "repository": (
        "Repository",
        "A project folder that Git keeps track of. Git stores the history in a hidden .git "
        "folder inside it; your own files stay where they are.",
    ),
    "working-tree": (
        "Working tree",
        "Your files as they are right now, including edits Git has not saved yet.",
    ),
    "staging-area": (
        "Staging area",
        "A waiting area for the changes you want in your next commit. You choose what goes in.",
    ),
    "commit": (
        "Commit",
        "A saved snapshot of the staged changes, with a message saying what changed. "
        "Commits line up into the project's history.",
    ),
    "branch": (
        "Branch",
        "A name that points at a commit. When you commit on a branch, the name moves forward "
        "to the new commit.",
    ),
    "head": (
        "HEAD",
        "Git's marker for where you are right now, usually the branch you are working on.",
    ),
    "remote": (
        "Remote",
        "Another copy of the repository, usually on a server, that you send work to and get "
        "work from.",
    ),
    "conflict": (
        "Conflict",
        "Two changes touched the same lines, so Git needs you to decide what the file should say.",
    ),
    "stash": (
        "Stash",
        "A shelf where Git keeps unfinished work so your files are clean, until you take it back.",
    ),
    "tag": ("Tag", "A fixed label on one commit, often used to mark a release."),
    "config": ("Configuration", "Settings Git uses, like the name that appears on your commits."),
    "in-progress": (
        "Paused operation",
        "A merge or rebase that Git has paused until you finish or cancel it.",
    ),
}

_BY_CHANGE_KIND = {
    "repository": "repository",
    "working_tree": "working-tree",
    "staging": "staging-area",
    "commit": "commit",
    "branch": "branch",
    "head": "head",
    "remote": "remote",
    "conflict": "conflict",
    "stash": "stash",
    "tag": "tag",
    "config": "config",
    "operation": "in-progress",
}
MAX_CONCEPTS = 3


def concept_key(key: str) -> str:
    return f"concept:{key}"


def concepts_for(changes: Iterable[dict], seen: set[str], *, first_guide: bool) -> list[dict]:
    """Unseen concepts for a guide, most basic first, at most ``MAX_CONCEPTS``."""

    keys = ["commands"] if first_guide else []
    changes = list(changes)
    creates_repository = any(change.get("kind") == "repository" for change in changes)
    for change in changes:
        key = _BY_CHANGE_KIND.get(str(change.get("kind")))
        if creates_repository and key in {"branch", "head"}:
            continue  # init's first branch is a detail; branches get their own guide later

        if key and key not in keys:
            keys.append(key)
        # Staging only makes sense next to the files it takes changes from.
        if key == "staging-area" and "working-tree" not in keys:
            keys.insert(keys.index(key), "working-tree")
    fresh = [key for key in keys if concept_key(key) not in seen]
    return [
        {"key": key, "title": CONCEPTS[key][0], "text": CONCEPTS[key][1]} for key in fresh[:MAX_CONCEPTS]
    ]
