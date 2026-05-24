from __future__ import annotations

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
    ("git remote -v", "git-remote-v"),
    ("git remote", "git-remote-v"),
    ("git log", "git-log"),
    ("git status", "git-status"),
    ("git diff", "git-diff"),
    ("git show", "git-show"),
    ("git branch", "git-branch"),
    ("git reflog", "git-reflog"),
    ("git init", "git-init"),
    ("git clone", "git-clone"),
    ("git add", "git-add"),
    ("git commit", "git-commit"),
    ("git restore", "git-restore"),
    (".gitignore", "gitignore"),
)


def command_content_key_for_command(command: str) -> str:
    normalized = normalize_command_text(command)
    for prefix, key in COMMAND_KEY_PREFIXES:
        if normalized == prefix or normalized.startswith(f"{prefix} "):
            return key
    return normalized.replace(" ", "-").replace("/", "-").replace(".", "dot")


def _paragraph(body: str) -> dict[str, Any]:
    return {"type": "paragraph", "body": body}


def _commands(items: list[str]) -> dict[str, Any]:
    return {"type": "command", "title": "Command forms", "items": items}


def _bullets(title: str, items: list[str]) -> dict[str, Any]:
    return {"type": "bullet_list", "title": title, "items": items}


def _warning(body: str) -> dict[str, Any]:
    return {"type": "warning", "title": "Watch for", "body": body}


def _callout(title: str, body: str) -> dict[str, Any]:
    return {"type": "callout", "title": title, "body": body}


def _terminal(body: str) -> dict[str, Any]:
    return {"type": "terminal_output", "title": "Typical output", "body": body}


def _pages(
    *,
    summary: str,
    syntax: list[str],
    effects: list[str],
    boundaries: list[str],
    watch_for: str,
    readiness: list[str],
    terminal_output: str = "",
) -> list[dict[str, Any]]:
    overview_blocks = [_paragraph(summary)]
    if terminal_output:
        overview_blocks.append(_terminal(terminal_output))
    return [
        {
            "id": "overview",
            "title": "Overview",
            "blocks": overview_blocks,
        },
        {
            "id": "behavior",
            "title": "Behavior",
            "subtitle": "What Git does when this command runs.",
            "blocks": [
                _commands(syntax),
                _bullets("Repository effect", effects),
                _bullets("Boundaries", boundaries),
            ],
        },
        {
            "id": "readiness",
            "title": "Readiness",
            "subtitle": "Checks to make before using it in a scenario.",
            "blocks": [
                _warning(watch_for),
                _bullets("Before running it", readiness),
            ],
        },
    ]


def _content(
    *,
    key: str,
    display_name: str,
    canonical_command: str,
    aliases: list[str],
    summary: str,
    tags: list[str],
    syntax: list[str],
    effects: list[str],
    boundaries: list[str],
    watch_for: str,
    readiness: list[str],
    terminal_output: str = "",
) -> dict[str, Any]:
    return {
        "key": key,
        "display_name": display_name,
        "canonical_command": canonical_command,
        "aliases": aliases,
        "summary": summary,
        "tags": tags,
        "pages": _pages(
            summary=summary,
            syntax=syntax,
            effects=effects,
            boundaries=boundaries,
            watch_for=watch_for,
            readiness=readiness,
            terminal_output=terminal_output,
        ),
    }


GIT_COMMAND_CONTENT_LIBRARY: list[dict[str, Any]] = [
    _content(
        key="git-status",
        display_name="git status",
        canonical_command="git status",
        aliases=["git st", "git status --short", "git status --porcelain"],
        summary=(
            "git status reports the current branch, staged changes, unstaged changes, "
            "and untracked files without changing repository state."
        ),
        tags=["diagnostic", "working-tree", "index"],
        syntax=["git status", "git status --short"],
        effects=["Reports repository state only."],
        boundaries=["It does not stage, commit, discard, or rewrite files."],
        watch_for="Treating status output as a fix instead of evidence.",
        readiness=["Name the branch, staged paths, unstaged paths, and untracked paths."],
        terminal_output="On branch main\nChanges to be committed:\n  modified: demo.txt",
    ),
    _content(
        key="git-log",
        display_name="git log",
        canonical_command="git log --oneline",
        aliases=["git log", "git log --oneline --graph --all"],
        summary=(
            "git log reads commit history. Formatting flags change how the history is "
            "shown, not the commits themselves."
        ),
        tags=["diagnostic", "history"],
        syntax=["git log --oneline", "git log --oneline --graph --all"],
        effects=["Reports commit history and branch shape only."],
        boundaries=["It does not move HEAD, create commits, or edit files."],
        watch_for="Reading only the newest line when the task asks for branch or graph context.",
        readiness=["Identify the latest commit, message, and relevant branch tips."],
    ),
    _content(
        key="git-diff",
        display_name="git diff",
        canonical_command="git diff",
        aliases=["git diff -- <path>"],
        summary="git diff shows unstaged working-tree changes compared with the index.",
        tags=["diagnostic", "working-tree", "diff"],
        syntax=["git diff", "git diff -- <path>"],
        effects=["Reports unstaged content changes only."],
        boundaries=["It does not show staged changes unless you use a staged diff command."],
        watch_for="Assuming plain git diff includes changes already staged for commit.",
        readiness=["Use it before staging when you need to inspect working-tree edits."],
    ),
    _content(
        key="git-diff-staged",
        display_name="git diff --staged",
        canonical_command="git diff --staged",
        aliases=["git diff --cached"],
        summary="git diff --staged shows what is already in the index for the next commit.",
        tags=["diagnostic", "index", "diff"],
        syntax=["git diff --staged", "git diff --cached"],
        effects=["Reports staged content changes only."],
        boundaries=["It does not include unstaged working-tree edits."],
        watch_for="Checking only plain diff and missing what is already staged.",
        readiness=["Compare staged diff with status before committing."],
    ),
    _content(
        key="git-show",
        display_name="git show",
        canonical_command="git show",
        aliases=["git show <commit>"],
        summary="git show displays details for the current or named Git object, usually a commit.",
        tags=["diagnostic", "history", "object"],
        syntax=["git show", "git show <commit>"],
        effects=["Reports commit metadata and patch details only."],
        boundaries=["It does not change branches, files, or the index."],
        watch_for="Inspecting the wrong commit when the task names a specific revision.",
        readiness=["Confirm whether you need HEAD or a named commit."],
    ),
    _content(
        key="git-branch",
        display_name="git branch",
        canonical_command="git branch",
        aliases=["git branch -v"],
        summary="git branch lists local branches; -v also shows the commit each branch points to.",
        tags=["diagnostic", "branches"],
        syntax=["git branch", "git branch -v"],
        effects=["Reports local branch names and tips when used as a listing command."],
        boundaries=["Listing branches does not create, delete, or switch branches."],
        watch_for="Confusing a branch listing with changing the current branch.",
        readiness=["Identify the current branch marker and any named branch tips."],
    ),
    _content(
        key="git-remote-v",
        display_name="git remote -v",
        canonical_command="git remote -v",
        aliases=["git remote"],
        summary="git remote -v lists configured remote names and their fetch/push URLs.",
        tags=["diagnostic", "remotes"],
        syntax=["git remote", "git remote -v"],
        effects=["Reports configured remote relationships only."],
        boundaries=["It does not contact the remote or change remote-tracking branches."],
        watch_for="Assuming a remote listing proves local history is up to date.",
        readiness=["Confirm the remote name and URL before clone or remote-related work."],
    ),
    _content(
        key="git-reflog",
        display_name="git reflog",
        canonical_command="git reflog",
        aliases=[],
        summary="git reflog shows recent HEAD movements so you can orient or recover local work.",
        tags=["diagnostic", "history", "recovery"],
        syntax=["git reflog"],
        effects=["Reports local reference movements only."],
        boundaries=["It does not restore anything by itself."],
        watch_for="Using reflog entries as commands before confirming the current state.",
        readiness=["Use it with status and log when you need to verify where HEAD has been."],
    ),
    _content(
        key="git-init",
        display_name="git init",
        canonical_command="git init",
        aliases=["git init <directory>"],
        summary=(
            "git init creates Git metadata for a folder so future snapshots can be "
            "tracked there."
        ),
        tags=["action", "repository-setup"],
        syntax=["git init", "git init <directory>"],
        effects=["Creates a repository at the current or named directory."],
        boundaries=["It does not stage files, create commits, or rewrite file contents."],
        watch_for="Initializing the parent folder when the scenario names a child directory.",
        readiness=["Check whether the task names the current folder or a destination folder."],
    ),
    _content(
        key="git-clone",
        display_name="git clone",
        canonical_command="git clone <url>",
        aliases=["git clone <url> <folder>"],
        summary=(
            "git clone creates a local working copy from a remote repository and sets "
            "up the origin relationship."
        ),
        tags=["action", "remote", "repository-setup"],
        syntax=["git clone <url>", "git clone <url> <folder>"],
        effects=["Creates a local repository, checks out the default branch, and configures origin."],
        boundaries=["It does not modify the remote repository."],
        watch_for="Forgetting the destination folder when the scenario names one.",
        readiness=["Confirm the remote URL and destination folder before cloning."],
    ),
    _content(
        key="git-add",
        display_name="git add",
        canonical_command="git add <path>",
        aliases=["git add .", "git add -A"],
        summary="git add copies selected working-tree changes into the staging area.",
        tags=["action", "index", "staging"],
        syntax=["git add <path>", "git add .", "git add -A"],
        effects=["Moves selected path changes from the working tree into the index."],
        boundaries=["It does not create a commit or remove the edits from your files."],
        watch_for="Staging every file when only one path belongs in the next commit.",
        readiness=["Use status and diff to confirm the path before staging."],
    ),
    _content(
        key="git-add-p",
        display_name="git add -p",
        canonical_command="git add -p <path>",
        aliases=["git add --patch <path>"],
        summary="git add -p lets you stage selected hunks instead of an entire file.",
        tags=["action", "index", "partial-staging"],
        syntax=["git add -p <path>"],
        effects=["Moves selected hunks from the working tree into the index."],
        boundaries=["It leaves unselected hunks in the working tree."],
        watch_for="Accepting unrelated hunks because they happen to be in the same file.",
        readiness=["Read each hunk and match it to the scenario's requested change."],
    ),
    _content(
        key="git-rm-cached",
        display_name="git rm --cached",
        canonical_command="git rm --cached <path>",
        aliases=[],
        summary="git rm --cached removes a path from the index while leaving the local file present.",
        tags=["action", "index", "ignore"],
        syntax=["git rm --cached <path>"],
        effects=["Stages removal of the tracked path from future commits."],
        boundaries=["It does not delete the local working-tree file."],
        watch_for="Using a removal command that deletes a local file you meant to keep.",
        readiness=["Use it with ignore rules when a generated file is already tracked."],
    ),
    _content(
        key="git-commit",
        display_name="git commit",
        canonical_command='git commit -m "message"',
        aliases=["git commit"],
        summary="git commit saves the staged snapshot and advances the current branch tip.",
        tags=["action", "history", "snapshot"],
        syntax=['git commit -m "message"'],
        effects=["Creates a new commit from the index and moves the current branch to it."],
        boundaries=["It does not include unstaged changes or ignored files."],
        watch_for="Committing before checking exactly what is staged.",
        readiness=["Confirm staged paths and the required message before committing."],
    ),
    _content(
        key="git-commit-amend",
        display_name="git commit --amend",
        canonical_command="git commit --amend",
        aliases=['git commit --amend -m "message"'],
        summary=(
            "git commit --amend replaces the latest local commit with a corrected "
            "commit instead of adding a follow-up commit."
        ),
        tags=["action", "history", "rewrite"],
        syntax=["git commit --amend", 'git commit --amend -m "message"'],
        effects=["Replaces the latest local commit with a new commit object."],
        boundaries=["It should not be used to rewrite shared history in these local-only scenarios."],
        watch_for="Creating a second commit instead of repairing the latest one.",
        readiness=["Confirm the commit is local and the staged content/message are correct."],
    ),
    _content(
        key="git-restore",
        display_name="git restore",
        canonical_command="git restore <path>",
        aliases=[],
        summary="git restore discards selected working-tree changes by restoring paths from the index or HEAD.",
        tags=["action", "working-tree", "discard"],
        syntax=["git restore <path>"],
        effects=["Replaces selected working-tree paths with the chosen source version."],
        boundaries=["It does not affect unrelated paths."],
        watch_for="Restoring the wrong path and losing edits you meant to keep.",
        readiness=["Separate paths to discard from paths to keep before running it."],
    ),
    _content(
        key="git-restore-staged",
        display_name="git restore --staged",
        canonical_command="git restore --staged <path>",
        aliases=[],
        summary="git restore --staged moves selected changes out of the staging area.",
        tags=["action", "index", "unstage"],
        syntax=["git restore --staged <path>"],
        effects=["Updates the index so selected changes are no longer staged."],
        boundaries=["It does not discard the working-tree file content."],
        watch_for="Leaving off --staged and discarding work instead of unstaging it.",
        readiness=["Use status after unstaging to verify the path moved back to unstaged."],
    ),
    _content(
        key="gitignore",
        display_name=".gitignore",
        canonical_command=".gitignore",
        aliases=[],
        summary=".gitignore tells Git which untracked generated or local files to ignore.",
        tags=["ignore", "working-tree"],
        syntax=[".gitignore", "git add .gitignore"],
        effects=["Changes ignore rules once the .gitignore file is edited and staged."],
        boundaries=["It does not remove files that are already tracked."],
        watch_for="Adding ignore rules but forgetting to untrack a generated file already in Git.",
        readiness=["Pair ignore rules with git status and git rm --cached when needed."],
    ),
]


def seed_git_command_content_library() -> int:
    from scenarios.models import GitCommandContent

    active_keys = []
    for sort_order, item in enumerate(GIT_COMMAND_CONTENT_LIBRARY, start=1):
        active_keys.append(item["key"])
        GitCommandContent.objects.update_or_create(
            key=item["key"],
            defaults={
                "display_name": item["display_name"],
                "canonical_command": item["canonical_command"],
                "aliases": item["aliases"],
                "summary": item["summary"],
                "tags": item["tags"],
                "pages": item["pages"],
                "is_active": True,
                "version": 1,
                "sort_order": sort_order,
            },
        )
    return len(active_keys)
