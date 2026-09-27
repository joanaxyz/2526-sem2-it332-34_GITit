"""Read a command's syntax part by part, for learners who have never typed one.

`git switch -c <branch>` becomes: git (runs Git), switch (the Git command),
-c (create the branch first), <branch> (you fill this in: the branch name).
Option and placeholder meanings come from small glossaries; anything unknown
still gets an honest generic description, so every form can be explained.
"""

from __future__ import annotations

import re
import shlex

# (family, option) -> meaning; (None, option) applies to every family.
_OPTIONS: dict[tuple[str | None, str], str] = {
    ("switch", "-c"): "create the branch first, then switch to it",
    ("switch", "--create"): "create the branch first, then switch to it",
    ("switch", "--detach"): "look at a commit without being on a branch",
    ("checkout", "-b"): "create the branch first, then switch to it",
    ("init", "-b"): "choose the name of the first branch",
    ("init", "--initial-branch"): "choose the name of the first branch",
    ("commit", "-m"): "write the commit message right here",
    ("commit", "-a"): "stage every change to tracked files first",
    ("commit", "-am"): "stage tracked changes and write the message in one go",
    ("commit", "--amend"): "replace the last commit instead of adding a new one",
    ("commit", "--no-edit"): "keep the existing commit message",
    ("add", "-A"): "include every change in the project",
    ("add", "-u"): "include changes to files Git already tracks",
    ("add", "-p"): "pick the changes piece by piece",
    ("restore", "--staged"): "work on the staging area instead of your files",
    ("restore", "--source"): "take the file from another commit",
    ("reset", "--soft"): "move the branch but keep the changes staged",
    ("reset", "--mixed"): "move the branch and unstage the changes",
    ("reset", "--hard"): "move the branch and discard the changes in your files",
    ("branch", "-d"): "delete the branch (only if its work is merged)",
    ("branch", "-D"): "delete the branch even if its work is not merged",
    ("branch", "-m"): "rename the branch",
    ("merge", "--no-ff"): "always record a merge commit",
    ("merge", "--abort"): "cancel the merge and go back",
    ("rebase", "-i"): "edit the commits one by one",
    ("rebase", "--onto"): "choose a new base for the commits",
    ("rebase", "--continue"): "carry on after fixing a conflict",
    ("rebase", "--abort"): "cancel the rebase and go back",
    ("push", "-u"): "remember this remote branch for later pushes and pulls",
    ("push", "--force-with-lease"): "overwrite the remote branch, but only if nobody else changed it",
    ("log", "--oneline"): "show one line per commit",
    ("log", "--graph"): "draw how branches split and join",
    ("log", "--all"): "include every branch",
    ("stash", "-u"): "include new files that Git does not track yet",
    ("rm", "--cached"): "stop tracking the file but keep it on disk",
    (None, "-q"): "work quietly, printing less",
    (None, "--quiet"): "work quietly, printing less",
}

_PLACEHOLDERS: dict[str, str] = {
    "branch": "the branch name",
    "new-branch": "the new branch name",
    "file": "a file, written as its path from the project folder",
    "path": "a file or folder path",
    "paths": "one or more file paths",
    "commit": "a commit, by its ID or a name like HEAD",
    "message": "your message, in quotes",
    "remote": "the remote's name, like origin",
    "url": "the repository's address",
    "directory": "a folder name",
    "tag": "the tag name",
    "n": "a number",
    "pattern": "a pattern such as '*.css', in quotes",
    "start-point": "where the new branch should start",
    "from": "where the range starts",
    "to": "where the range ends",
    "key": "the setting's name",
    "value": "a value you choose",
}
_PLACEHOLDER = re.compile(r"<([^>]+)>")


def anatomy(usage_form: str) -> list[dict[str, str]]:
    try:
        tokens = shlex.split(usage_form)
    except ValueError:
        tokens = usage_form.split()
    if len(tokens) < 2 or tokens[0] != "git":
        return []
    family = tokens[1]
    parts = [
        {"token": "git", "text": "runs Git"},
        {"token": family, "text": "the Git command to run"},
    ]
    for token in tokens[2:]:
        parts.append({"token": token, "text": _describe(family, token)})
    return parts


def _describe(family: str, token: str) -> str:
    optional = token.startswith("[") and token.endswith("]")
    bare = token[1:-1] if optional else token
    text = _describe_bare(family, bare)
    return f"optional: {text}" if optional else text


def _describe_bare(family: str, token: str) -> str:
    if token == "--":
        return "everything after this is a file path"
    if token == ".":
        return "this folder and everything inside it"
    if token.startswith("-"):
        option = token.split("=", 1)[0]
        return _OPTIONS.get((family, option)) or _OPTIONS.get((None, option)) or "an option that changes how it works"
    names = _PLACEHOLDER.findall(token)
    if names and _PLACEHOLDER.fullmatch(token.removesuffix("...")):
        name = names[0].removesuffix("...")
        meaning = _PLACEHOLDERS.get(name, f"the {name.replace('-', ' ')}")
        several = token.endswith("...") or names[0].endswith("...")
        return f"you fill this in: {meaning}" + (", one or more" if several else "")
    if names:
        return "you fill in the " + " and ".join(
            f"<{name}> part" for name in names
        )
    return "type this exactly"
