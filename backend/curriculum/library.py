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

    ``kind`` selects how the Storey Book renders it:
      - ``"dag"`` — a commit graph. ``nodes`` are ``{id, label, lane, type}``
        (type one of commit/head/branch/merge); ``edges`` are ``{from, to}``.
      - ``"flow"`` — left-to-right stages (e.g. working tree → staging → repo).
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


def _command_words(command: str) -> list[str]:
    return str(command).strip().split()


def command_preview_syntax_for_command(command: str) -> str:
    """Return the reusable command-library syntax taught for a concrete scenario command."""
    raw = " ".join(str(command).strip().split())
    normalized = raw.lower()
    if not raw:
        return ""
    if normalized == ".gitignore":
        return ".gitignore"

    if normalized.startswith("git init"):
        return _git_init_preview_syntax(raw)
    if normalized.startswith("git clone"):
        return _git_clone_preview_syntax(raw)
    if normalized.startswith("git add -p") or normalized.startswith("git add --patch"):
        return "git add -p <path>" if len(_command_words(raw)) > 3 else "git add -p"
    if normalized.startswith("git add"):
        return _git_add_preview_syntax(raw)
    if normalized.startswith("git commit --amend"):
        if "--no-edit" in normalized:
            return "git commit --amend --no-edit"
        if " -m " in normalized or " --message " in normalized:
            return 'git commit --amend -m "message"'
        return "git commit --amend"
    if normalized.startswith("git commit"):
        if " -am " in normalized:
            return 'git commit -am "message"'
        if " -a " in normalized and " -m " in normalized:
            return 'git commit -a -m "message"'
        if "--message" in normalized:
            return 'git commit --message "message"'
        return 'git commit -m "message"'
    if normalized.startswith("git rm -r --cached"):
        return "git rm -r --cached <directory>"
    if normalized.startswith("git rm --cached"):
        return "git rm --cached <path>"
    if normalized.startswith("git restore --staged"):
        return _restore_preview_syntax(raw, staged=True)
    if normalized.startswith("git restore"):
        return _restore_preview_syntax(raw, staged=False)
    if normalized.startswith("git merge --abort"):
        return "git merge --abort"
    if normalized.startswith("git merge --continue"):
        return "git merge --continue"
    if normalized.startswith("git merge"):
        return "git merge <branch>"
    if normalized.startswith("git mergetool"):
        if "--tool" in normalized:
            return "git mergetool --tool <tool>"
        return "git mergetool"
    if normalized.startswith("git checkout --ours"):
        return "git checkout --ours <path>"
    if normalized.startswith("git checkout --theirs"):
        return "git checkout --theirs <path>"
    if normalized.startswith("git config"):
        if "merge.tool" in normalized:
            return "git config --global merge.tool <tool>"
        return "git config --global <key> <value>"
    if normalized.startswith("git fetch"):
        return "git fetch <remote>" if len(_command_words(raw)) > 2 else "git fetch"
    if normalized.startswith("git cherry-pick --abort"):
        return "git cherry-pick --abort"
    if normalized.startswith("git cherry-pick"):
        if "--no-commit" in normalized or " -n " in f" {normalized} ":
            return "git cherry-pick --no-commit <commit>"
        return "git cherry-pick <commit>"
    if normalized.startswith("git check-ignore -v"):
        return "git check-ignore -v <path>"
    if normalized.startswith("git ls-files -u") or normalized.startswith("git ls-files --unmerged"):
        return "git ls-files -u"
    if normalized.startswith("git diff --staged"):
        return "git diff --staged <path>" if len(_command_words(raw)) > 3 else "git diff --staged"
    if normalized.startswith("git diff --cached"):
        return "git diff --cached <path>" if len(_command_words(raw)) > 3 else "git diff --cached"
    if normalized.startswith("git diff"):
        for option in ("--ours", "--theirs", "--base"):
            if option in normalized:
                return f"git diff {option} <path>" if len(_command_words(raw)) > 3 else f"git diff {option}"
        if "--check" in normalized:
            return "git diff --check <path>" if len(_command_words(raw)) > 3 else "git diff --check"
        if "--name-only" in normalized:
            return "git diff --name-only"
        if normalized == "git diff head":
            return "git diff HEAD"
        return "git diff <path>" if len(_command_words(raw)) > 2 else "git diff"
    if normalized.startswith("git log"):
        if "--oneline --graph --all" in normalized:
            return "git log --oneline --graph --all"
        if "--max-count" in normalized:
            return "git log --max-count=<number>"
        if " -n " in normalized or normalized.startswith("git log -n"):
            return "git log -n <number>"
        if "--oneline" in normalized:
            return "git log --oneline"
        return "git log"
    if normalized.startswith("git show"):
        if "--name-only" in normalized:
            return "git show --name-only"
        return "git show <commit>" if len(_command_words(raw)) > 2 else "git show"
    if normalized.startswith("git switch --detach"):
        return "git switch --detach <commit>"
    if normalized.startswith("git switch -c") or normalized.startswith("git switch --create"):
        return "git switch -c <branch>"
    if normalized.startswith("git switch"):
        return "git switch <branch>"
    if normalized.startswith("git checkout -b"):
        words = _command_words(raw)
        positional = [w for w in words[2:] if not w.startswith("-")]
        return "git checkout -b <branch> <start-point>" if len(positional) >= 2 else "git checkout -b <branch>"
    if normalized.startswith("git stash list"):
        return "git stash list"
    if normalized.startswith("git stash pop"):
        return "git stash pop"
    if normalized.startswith("git stash apply"):
        return "git stash apply"
    if normalized.startswith("git stash drop"):
        return "git stash drop"
    if normalized.startswith("git stash"):
        return "git stash"
    if normalized.startswith("git push --force-with-lease") or normalized.startswith("git push -f") or normalized.startswith("git push --force"):
        return "git push --force-with-lease <remote> <branch>"
    if normalized.startswith("git push") and " --delete " in f" {normalized} ":
        return "git push <remote> --delete <branch>"
    if normalized.startswith("git push -u") or normalized.startswith("git push --set-upstream"):
        return "git push -u <remote> <branch>"
    if normalized.startswith("git push"):
        words = _command_words(raw)
        positional = [w for w in words[2:] if not w.startswith("-")]
        return "git push <remote> <branch>" if len(positional) >= 2 else "git push"
    if normalized.startswith("git pull --rebase"):
        return "git pull --rebase"
    if normalized.startswith("git pull"):
        words = _command_words(raw)
        positional = [w for w in words[2:] if not w.startswith("-")]
        return "git pull <remote> <branch>" if len(positional) >= 2 else "git pull"
    if normalized.startswith("git merge --squash"):
        return "git merge --squash <branch>"
    if normalized.startswith("git branch -v"):
        return "git branch -v"
    if normalized.startswith("git branch -a"):
        return "git branch -a"
    if normalized.startswith("git branch -d") or normalized.startswith("git branch --delete"):
        return "git branch -d <branch>"
    if normalized.startswith("git branch -D"):
        return "git branch -D <branch>"
    if normalized.startswith("git branch"):
        return "git branch"
    if normalized.startswith("git remote -v"):
        return "git remote -v"
    if normalized.startswith("git remote"):
        return "git remote"
    if normalized.startswith("git status"):
        for syntax in ("git status --ignored", "git status --porcelain", "git status -sb", "git status --short", "git status -s"):
            if normalized == syntax:
                return syntax
        return "git status"
    return raw


def command_preview_section_ids_for_command(command: str) -> list[str]:
    """Return the ordered content section IDs to include for this command syntax preview.

    Always includes: overview, the specific syntax section, all option/argument sections
    for the command key, effects, mistakes, and practice-notes. The option/argument
    sections are included unconditionally because they teach flag vocabulary that any
    variant of the command may require, even when the specific syntax being previewed
    does not use that flag.
    """
    syntax = command_preview_syntax_for_command(command)
    key = library_key_for_command(syntax or command)
    ids: list[str] = ["overview"]
    if syntax:
        ids.append(command_syntax_section_id(syntax))
    ids.extend(COMMAND_KEY_ALWAYS_INCLUDED_SECTION_IDS.get(key, []))
    ids.extend(["effects", "mistakes", "practice-notes"])
    # Preserve insertion order while deduplicating.
    seen: set[str] = set()
    unique: list[str] = []
    for section_id in ids:
        if section_id not in seen:
            seen.add(section_id)
            unique.append(section_id)
    return unique


def _git_init_preview_syntax(command: str) -> str:
    words = _command_words(command)
    opts = [word.lower() for word in words[2:] if word.startswith("-")]
    has_quiet = any(word in {"-q", "--quiet"} for word in opts)
    has_short_branch = "-b" in opts
    has_long_branch = any(word == "--initial-branch" or word.startswith("--initial-branch=") for word in opts)
    # Any non-option token after `git init` that is not the branch value is treated as a directory.
    args = words[2:]
    directory = False
    skip_next = False
    for word in args:
        lowered = word.lower()
        if skip_next:
            skip_next = False
            continue
        if lowered in {"-b", "--initial-branch"}:
            skip_next = True
            continue
        if lowered.startswith("--initial-branch=") or lowered in {"-q", "--quiet"}:
            continue
        if word == ".":
            return "git init ."
        if not word.startswith("-"):
            directory = True
    if has_quiet and has_short_branch and directory:
        return "git init -q -b <branch> <directory>"
    if has_quiet and has_long_branch and directory:
        return "git init --quiet --initial-branch=<branch> <directory>"
    if has_short_branch and directory:
        return "git init -b <branch> <directory>"
    if has_long_branch and directory:
        return "git init --initial-branch=<branch> <directory>"
    if has_short_branch:
        return "git init -b <branch>"
    if has_long_branch:
        return "git init --initial-branch=<branch>"
    if has_quiet and directory:
        return "git init --quiet <directory>"
    if has_quiet:
        return "git init --quiet"
    if directory:
        return "git init <directory>"
    return "git init"


def _git_clone_preview_syntax(command: str) -> str:
    normalized = normalize_command_text(command)
    words = _command_words(command)
    has_depth = "--depth" in normalized
    has_short_branch = " -b " in f" {normalized} "
    has_long_branch = "--branch" in normalized
    # Count URL-ish non-option args after option values. The first is URL, the second is destination.
    positional = []
    skip_next = False
    for word in words[2:]:
        lowered = word.lower()
        if skip_next:
            skip_next = False
            continue
        if lowered in {"-b", "--branch", "--depth"}:
            skip_next = True
            continue
        if word.startswith("-"):
            continue
        positional.append(word)
    has_directory = len(positional) >= 2
    branch_flag = "--branch" if has_long_branch and not has_short_branch else "-b"
    if has_depth and (has_short_branch or has_long_branch) and has_directory:
        return f"git clone --depth <number> {branch_flag} <branch> <url> <directory>"
    if has_depth and has_directory:
        return "git clone --depth <number> <url> <directory>"
    if has_depth:
        return "git clone --depth <number> <url>"
    if (has_short_branch or has_long_branch) and has_directory:
        return f"git clone {branch_flag} <branch> <url> <directory>"
    if has_short_branch or has_long_branch:
        return f"git clone {branch_flag} <branch> <url>"
    if has_directory:
        return "git clone <url> <directory>"
    return "git clone <url>"


def _git_add_preview_syntax(command: str) -> str:
    raw = " ".join(str(command).strip().split())
    normalized = normalize_command_text(command)
    words = _command_words(command)
    if raw == "git add .":
        return "git add ."
    if raw == "git add -A" or raw.startswith("git add -A "):
        return "git add -A"
    if normalized == "git add --all" or normalized.startswith("git add --all "):
        return "git add --all"
    if normalized.startswith("git add -u"):
        return "git add -u"
    if normalized.startswith("git add --update"):
        return "git add --update"
    path_count = max(0, len([word for word in words[2:] if not word.startswith("-")]))
    if path_count >= 2:
        return "git add <path> <path>"
    if words[-1].endswith("/") if words else False:
        return "git add <directory>/"
    return "git add <path>"


def _restore_preview_syntax(command: str, *, staged: bool) -> str:
    normalized = normalize_command_text(command)
    words = _command_words(command)
    base = "git restore --staged" if staged else "git restore"
    if normalized.endswith(" ."):
        return f"{base} ."
    # Ignore the command words and --staged flag, then count path-like args.
    args = [word for word in words[2:] if word != "--staged" and not word.startswith("--source")]
    if len(args) >= 2:
        return f"{base} <path> <path>"
    return f"{base} <path>"


def _sample_output_for_syntax(command: str) -> str:
    normalized = normalize_command_text(command)
    prompt = f"student@git-it $ {command}"
    if normalized.startswith("git init"):
        if "--quiet" in normalized or " -q" in f" {normalized}":
            return f"{prompt}\n# no terminal output when quiet initialization succeeds"
        if "<directory>" in command:
            return f"{prompt}\nInitialized empty Git repository in /workspace/{_sample_directory_for(command)}/.git/"
        return f"{prompt}\nInitialized empty Git repository in /workspace/.git/"
    if normalized.startswith("git clone"):
        directory = "demo-repository" if "<directory>" in command else "repository"
        return "\n".join([
            prompt,
            f"Cloning into '{directory}'...",
            "remote: Enumerating objects: 6, done.",
            "remote: Counting objects: 100% (6/6), done.",
            "Receiving objects: 100% (6/6), done.",
        ])
    if normalized.startswith("git add") or normalized.startswith("git restore") or normalized.startswith("git rm"):
        return f"{prompt}\n# no output means the command was accepted; run git status to verify the state change"
    if normalized.startswith("git switch -c") or normalized.startswith("git switch --create"):
        branch = "<branch>"
        parts = command.strip().split()
        if len(parts) >= 3:
            branch = parts[-1]
        return f"{prompt}\nSwitched to a new branch '{branch}'"
    if normalized.startswith("git switch --detach"):
        return f"{prompt}\nHEAD is now at c1 Demo snapshot"
    if normalized.startswith("git switch"):
        branch = "<branch>"
        parts = command.strip().split()
        if len(parts) >= 3:
            branch = parts[-1]
        return f"{prompt}\nSwitched to branch '{branch}'"
    if normalized.startswith("git checkout -b"):
        branch = "<branch>"
        parts = command.strip().split()
        if len(parts) >= 3:
            b_idx = parts.index("-b") if "-b" in parts else -1
            if b_idx >= 0 and b_idx + 1 < len(parts):
                branch = parts[b_idx + 1]
        return f"{prompt}\nSwitched to a new branch '{branch}'"
    if normalized.startswith("git stash list"):
        return f"{prompt}\nstash@{{0}}: WIP on feature/ui: c2 Add styles\nstash@{{1}}: WIP on main: c1 Initial snapshot"
    if normalized.startswith("git stash pop") or normalized.startswith("git stash apply"):
        return f"{prompt}\nOn branch feature/ui\nChanges not staged for commit:\n  modified:   src/app.js\nDropped stash@{{0}}"
    if normalized.startswith("git stash"):
        return f"{prompt}\nSaved working directory and index state WIP on feature/ui: c2 Add styles"
    if normalized.startswith("git push --force-with-lease") or normalized.startswith("git push -f"):
        return f"{prompt}\nTo https://example.test/demo/repository.git\n + c2...c3 feature/ui -> feature/ui (forced update)"
    if normalized.startswith("git push") and "--delete" in normalized:
        return f"{prompt}\nTo https://example.test/demo/repository.git\n - [deleted]         feature/old"
    if normalized.startswith("git push -u") or normalized.startswith("git push --set-upstream"):
        return f"{prompt}\nTo https://example.test/demo/repository.git\n * [new branch]      feature/ui -> feature/ui\nBranch 'feature/ui' set up to track remote branch 'feature/ui' from 'origin'."
    if normalized.startswith("git push"):
        return f"{prompt}\nTo https://example.test/demo/repository.git\n   c1..c2  feature/ui -> feature/ui"
    if normalized.startswith("git pull --rebase"):
        return f"{prompt}\nSuccessfully rebased and updated refs/heads/main."
    if normalized.startswith("git pull"):
        return f"{prompt}\nFrom https://example.test/demo/repository.git\n * branch            main       -> FETCH_HEAD\nUpdating c1..c2\nFast-forward\n README.md | 2 +-"
    if normalized.startswith("git merge --squash"):
        return f"{prompt}\nSquash commit -- not updating HEAD\nAutomatic merge went well; stopped before committing as requested"
    if normalized.startswith("git branch -d") or normalized.startswith("git branch --delete"):
        return f"{prompt}\nDeleted branch feature/ui (was c2)."
    if normalized.startswith("git branch -D"):
        return f"{prompt}\nDeleted branch feature/spike (was c2)."
    if normalized.startswith("git branch -a"):
        return f"{prompt}\n* main\n  feature/ui\n  remotes/origin/main\n  remotes/origin/feature/ui"
    if normalized.startswith("git commit --amend"):
        return f"{prompt}\n[main c3] Corrected snapshot\n Date: Mon May 25 12:00:00 2026 +0800\n 1 file changed, 2 insertions(+)"
    if normalized.startswith("git commit"):
        return f"{prompt}\n[main c2] Demo snapshot\n 1 file changed, 2 insertions(+)"
    if normalized.startswith("git status"):
        return f"{prompt}\nOn branch main\nChanges to be committed:\n  modified:   README.md\n\nUntracked files:\n  notes.txt"
    if normalized.startswith("git log"):
        return f"{prompt}\nc2 Demo snapshot\nc1 Initial project snapshot"
    if normalized.startswith("git diff --check"):
        return f"{prompt}\nsrc/auth.js:1: leftover conflict marker"
    if normalized.startswith(("git diff --ours", "git diff --theirs", "git diff --base")):
        return f"{prompt}\ndiff --git a/src/auth.js b/src/auth.js\n@@ -1 +1 @@\n+resolved side content"
    if normalized.startswith("git diff"):
        return f"{prompt}\ndiff --git a/README.md b/README.md\n+Added practice note"
    if normalized.startswith("git ls-files -u"):
        return f"{prompt}\n100644 BASE 1\tsrc/auth.js\n100644 c1 2\tsrc/auth.js\n100644 c2 3\tsrc/auth.js"
    if normalized.startswith("git remote"):
        return f"{prompt}\norigin  https://example.test/demo/repository.git (fetch)\norigin  https://example.test/demo/repository.git (push)"
    if normalized.startswith("git branch"):
        return f"{prompt}\n* main\n  starter"
    if normalized.startswith("git show"):
        return f"{prompt}\ncommit c2\n\n    Demo snapshot\n\ndiff --git a/README.md b/README.md"
    if normalized.startswith("git check-ignore"):
        return f"{prompt}\n.gitignore:3:*.log\tdebug.log"
    if normalized.startswith("git ls-files"):
        return f"{prompt}\nREADME.md\nsrc/app.py"
    if normalized == ".gitignore":
        return "# .gitignore\nnode_modules/\n*.log\n.env"
    return f"{prompt}\n# output depends on the repository state"


def _sample_directory_for(command: str) -> str:
    if "research" in command:
        return "research-log"
    if "ui-kit" in command:
        return "ui-kit"
    return "demo-project"


def _syntax_title(command: str) -> str:
    if any(token in command for token in ("<path>", "<directory>", "<url>", "<branch>", "<number>", '"message"')):
        return f"Syntax: {command}"
    return command


def _syntax_explanation(command: str, canonical_command: str) -> str:
    note = _placeholder_note(command)
    return (
        f"Use `{command}` only when the authored scenario asks for this exact shape of command. "
        f"This syntax is different from `{canonical_command}` because options, destinations, paths, branch names, depth, or messages change what Git acts on. "
        f"{note}"
    )


def _syntax_how_to_read(command: str) -> list[str]:
    items = [
        "Read the command from left to right: base command first, then options, then the concrete value such as a path, directory, URL, branch, number, or message.",
        "Anything shown inside angle brackets is not typed literally; it is replaced with the value given by the scenario.",
    ]
    normalized = normalize_command_text(command)
    if "--quiet" in normalized or " -q" in f" {normalized}":
        items.append("Quiet commands can succeed with no visible output, so verification must come from status, metadata, or the target state rather than terminal chatter.")
    if "<directory>" in command:
        items.append("The directory argument matters because initializing or cloning the parent folder is a different answer from targeting the named child folder.")
    if "<branch>" in command:
        items.append("The branch option changes which branch name is created or checked out; it is not just decoration.")
    if "<path>" in command:
        items.append("The path limits the operation. A broad command can accidentally stage, restore, or inspect files that the scenario wanted left alone.")
    if "<number>" in command:
        items.append("The number limits history depth or output count, so use the exact amount requested.")
    if '"message"' in command:
        items.append("The message text must match the scenario's required commit message, not the sample word shown here.")
    return _clean_items(items)


def _syntax_when_to_use(command: str) -> list[str]:
    normalized = normalize_command_text(command)
    items = []
    if normalized.startswith("git init"):
        items.append("Use this during repository setup, before any first commit exists unless the task explicitly says you are safely reinitializing.")
    elif normalized.startswith("git clone"):
        items.append("Use this when the required starting point is a remote repository, not a local folder that already exists.")
    elif normalized.startswith("git add"):
        items.append("Use this after inspecting changes and before committing, when the chosen content belongs in the next snapshot.")
    elif normalized.startswith("git commit"):
        items.append("Use this only after the index contains exactly the snapshot that should be saved.")
    elif normalized.startswith("git restore --staged"):
        items.append("Use this when content is staged but should be kept as an unstaged working-tree change.")
    elif normalized.startswith("git restore"):
        items.append("Use this when the scenario says selected working-tree edits should be discarded.")
    elif normalized.startswith("git rm"):
        items.append("Use this when a tracked generated file should stop being tracked but remain on disk.")
    elif normalized == ".gitignore":
        items.append("Use this when the scenario asks you to ignore generated, local, or secret files before staging the ignore rule.")
    else:
        items.append("Use this as an inspection step when the scenario asks you to read repository evidence before acting.")
    items.append("Do not choose it just because it looks familiar; match it to the scenario's exact required values.")
    return _clean_items(items)


def _generic_syntax_section(
    *,
    command: str,
    canonical_command: str,
    effects: list[str],
    boundaries: list[str],
    watch_for: str,
    readiness: list[str],
) -> dict[str, Any]:
    return _section(
        section_id=command_syntax_section_id(command),
        section_type="syntax",
        title=_syntax_title(command),
        command=command,
        content=[
            _paragraph(_syntax_explanation(command, canonical_command)),
            _terminal(_sample_output_for_syntax(command)),
            _bullets("How to read this syntax", _syntax_how_to_read(command)),
            _bullets("When to use this exact command", _syntax_when_to_use(command)),
            _bullets("What changes", effects),
            _bullets("What does not change", boundaries),
            _bullets("Check before/after", readiness or ["Run a diagnostic command after action commands to confirm the repository state matches the scenario."]),
            _warning(watch_for),
        ],
    )

def _clean_items(items: list[str] | None) -> list[str]:
    return [str(item).strip() for item in (items or []) if str(item).strip()]


def _first_sentence(text: str) -> str:
    value = " ".join(str(text).strip().split())
    if not value:
        return ""
    for marker in (". ", "! ", "? "):
        if marker in value:
            return value.split(marker, 1)[0] + marker.strip()
    return value


def _placeholder_note(command: str) -> str:
    if "<path>" in command:
        return "Replace <path> with the exact file or folder named by the scenario. Do not use a placeholder literally."
    if "<directory>" in command:
        return "Replace <directory> with the exact destination folder requested by the scenario."
    if "<url>" in command:
        return "Replace <url> with the exact remote URL from the scenario."
    if "<branch>" in command:
        return "Replace <branch> with the exact branch name requested by the scenario."
    if "<number>" in command:
        return "Replace <number> with the numeric value requested by the scenario."
    if '"message"' in command:
        return "Replace the sample message with the exact commit message required by the scenario."
    return "Choose this syntax only when its option, path, or argument matches the scenario details."


def _verification_items(*, command: str, effects: list[str], boundaries: list[str], readiness: list[str]) -> list[str]:
    items = []
    if effects:
        items.append(f"Expected result: {effects[0]}")
    if readiness:
        items.append(f"Before running it: {readiness[0]}")
    if boundaries:
        items.append(f"Do not expect it to do this: {boundaries[0]}")
    if command.startswith("git status"):
        items.append("Verify the branch line and each path category: staged, unstaged, untracked, and ignored when requested.")
    elif command.startswith("git diff --staged") or command.startswith("git diff --cached"):
        items.append("Verify that the displayed patch is the version already staged for the next commit.")
    elif command.startswith("git diff"):
        items.append("Verify whether you are reading unstaged edits, staged edits, or all tracked edits since HEAD.")
    elif command.startswith("git log"):
        items.append("Verify commit order before choosing a commit id or judging whether history looks correct.")
    elif command.startswith("git add"):
        items.append("Run a status or staged diff afterward to confirm only the intended paths or hunks entered the index.")
    elif command.startswith("git commit"):
        items.append("Run a log or status check afterward to confirm the new or amended snapshot is the intended one.")
    elif command.startswith("git restore"):
        items.append("Run status afterward because restore affects either the working tree or index depending on the flags used.")
    elif command.startswith("git init"):
        items.append("Run status afterward to confirm the folder is now a repository without assuming a commit was created.")
    elif command.startswith("git clone"):
        items.append("Inspect status and remotes afterward to confirm the local copy is clean and connected to origin.")
    elif command == ".gitignore":
        items.append("Pair the ignore rule with status or check-ignore so you can prove the generated path is excluded.")
    return _clean_items(items)


def _state_language(*, command: str, effects: list[str], boundaries: list[str]) -> str:
    if command.startswith(("git status", "git log", "git diff", "git show", "git branch", "git remote", "git reflog", "git check-ignore", "git ls-files")):
        return "This is a reading command in Tower 1. It gives evidence for the next decision, but the repository state should remain unchanged after the preview command runs."
    if command.startswith("git add"):
        return "This command changes the index, which is the staged snapshot prepared for the next commit. It does not create history by itself."
    if command.startswith("git commit"):
        return "This command changes local history by creating or replacing the commit at the current branch tip."
    if command.startswith("git restore --staged"):
        return "This command changes the index by moving selected content out of staging while keeping the working-tree edits available."
    if command.startswith("git restore"):
        return "This command changes working-tree files by replacing local edits with the chosen source version."
    if command.startswith("git rm --cached"):
        return "This command changes the index so Git stops tracking a path while leaving the local file present."
    if command.startswith("git init"):
        return "This command creates repository metadata. It prepares tracking capability, but it does not stage or commit project files."
    if command.startswith("git clone"):
        return "This command creates a local repository from a remote fixture and records the origin relationship."
    if command == ".gitignore":
        return "This content changes ignore behavior for untracked paths. It does not automatically remove files already tracked by Git."
    return _first_sentence(effects[0] if effects else "Use this command only when it matches the scenario state.")


def _rich_syntax_section(
    *,
    section_id: str,
    title: str,
    command: str,
    does: str,
    sample_output: str,
    how_to_read: list[str],
    effects: list[str],
    boundaries: list[str],
    mistake: str,
) -> dict[str, Any]:
    return _section(
        section_id=section_id,
        section_type="syntax",
        title=title,
        command=command,
        content=[
            _paragraph(does),
            _terminal(sample_output),
            _bullets("How to read it", how_to_read),
            _bullets("What changes", effects),
            _bullets("What does not change", boundaries),
            _warning(mistake),
        ],
    )


def _section(
    *,
    section_id: str,
    section_type: str,
    title: str,
    content: list[dict[str, Any]],
    command: str = "",
    token: str = "",
) -> dict[str, Any]:
    section = {
        "id": section_id,
        "type": section_type,
        "title": title,
        "content": content,
    }
    if command:
        section["command"] = command
    if token:
        section["token"] = token
    return section


def _semantic_item_sections(
    *,
    section_type: str,
    prefix: str,
    items: list[dict[str, Any]] | None,
) -> list[dict[str, Any]]:
    sections = []
    for item in items or []:
        token = item.get("token") or item.get("command") or item.get("title") or ""
        title = item.get("title") or token or section_type.replace("_", " ").title()
        body = item.get("body") or item.get("description") or ""
        content = item.get("content")
        if not isinstance(content, list):
            token_label = str(token or title).strip()
            content = []
            if body:
                content.append(_paragraph(body))
            content.extend(
                [
                    _callout(
                        "How to use this in a scenario",
                        f"Look for the exact clue that requires {token_label}. If the scenario does not ask for that behavior, prefer the simpler supported syntax.",
                    ),
                    _bullets(
                        "Decision checklist",
                        _clean_items(
                            [
                                f"Confirm the scenario names or implies {token_label} before using this syntax.",
                                "Keep the rest of the command unchanged unless the scenario gives another required value.",
                                "After running it, inspect the state that this option or argument is supposed to affect.",
                            ]
                        ),
                    ),
                ]
            )
        sections.append(
            _section(
                section_id=item.get("id") or f"{prefix}-{_slug(token or title)}",
                section_type=section_type,
                title=title,
                command=item.get("command") or "",
                token=item.get("token") or "",
                content=content,
            )
        )
    return sections

def _sections(
    *,
    canonical_command: str,
    summary: str,
    syntax: list[str],
    effects: list[str],
    boundaries: list[str],
    watch_for: str,
    readiness: list[str],
    terminal_output: str = "",
    options: list[dict[str, Any]] | None = None,
    arguments: list[dict[str, Any]] | None = None,
    diagram: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    syntax = _clean_items(syntax)
    effects = _clean_items(effects)
    boundaries = _clean_items(boundaries)
    readiness = _clean_items(readiness)
    overview_blocks = [
        _paragraph(summary),
        _callout(
            "Mental model",
            _state_language(command=canonical_command, effects=effects, boundaries=boundaries),
        ),
        *([diagram] if diagram else []),
        _bullets(
            "What to look at before using it",
            readiness
            or [
                "Read the scenario values carefully before choosing command syntax.",
                "Check whether the task is asking you to inspect, stage, commit, initialize, clone, ignore, unstage, or discard.",
            ],
        ),
    ]
    if terminal_output:
        overview_blocks.append(_terminal(terminal_output))
    overview_blocks.append(
        _bullets(
            "How to verify the result",
            _verification_items(
                command=canonical_command,
                effects=effects,
                boundaries=boundaries,
                readiness=readiness,
            ),
        )
    )

    sections = [
        _section(
            section_id="overview",
            section_type="overview",
            title="Overview",
            command=canonical_command,
            content=overview_blocks,
        )
    ]
    for syntax_example in syntax:
        sections.append(
            _generic_syntax_section(
                command=syntax_example,
                canonical_command=canonical_command,
                effects=effects,
                boundaries=boundaries,
                watch_for=watch_for,
                readiness=readiness,
            )
        )
    sections.extend(
        _semantic_item_sections(section_type="option", prefix="option", items=options)
    )
    sections.extend(
        _semantic_item_sections(section_type="argument", prefix="argument", items=arguments)
    )
    sections.extend(
        [
            _section(
                section_id="effects",
                section_type="effect",
                title="Effects and boundaries",
                content=[
                    _paragraph(
                        "Before you run the command in a scored scenario, separate the thing it changes or reports from the things it deliberately leaves alone."
                    ),
                    _bullets("Repository effect", effects),
                    _bullets("What does not change", boundaries),
                    _callout(
                        "State-check habit",
                        "After an action command, inspect the repository again. After a diagnostic command, use the evidence to choose the next action rather than treating the diagnostic output as the solution itself.",
                    ),
                ],
            ),
            _section(
                section_id="mistakes",
                section_type="mistake",
                title="Common beginner mistake",
                content=[
                    _warning(watch_for),
                    _bullets(
                        "Safer habit",
                        _clean_items(
                            [
                                "Read the scenario's exact path, branch, directory, URL, or message before typing.",
                                "Use status, diff, log, or another diagnostic command when you are unsure what state you are changing.",
                                "Prefer narrow command syntax over a broad command when the scenario only asks for one file, one hunk, or one folder.",
                            ]
                        ),
                    ),
                ],
            ),
            _section(
                section_id="practice-notes",
                section_type="practice_note",
                title="Field notes",
                content=[
                    _paragraph(
                        "Use this page as the last check before opening an authored level variant. The preview teaches behavior; the scenario will still require you to apply the exact values from its brief."
                    ),
                    _bullets("Before running it", readiness),
                    _bullets(
                        "While solving",
                        _clean_items(
                            [
                                "Keep diagnostic commands separate from counted action commands.",
                                "Do not guess from memory when the scenario gives concrete file names or messages.",
                                "When the state is not what you expected, inspect first instead of piling on more action commands.",
                            ]
                        ),
                    ),
                ],
            ),
        ]
    )
    return sections

def pages_from_command_sections(sections: list[dict[str, Any]]) -> list[dict[str, Any]]:
    pages = []
    for index, section in enumerate(sections, start=1):
        if not isinstance(section, dict):
            continue
        page = {
            "id": section.get("id") or f"section-{index}",
            "title": section.get("title") or f"Section {index}",
            "heading": section.get("title") or f"Section {index}",
            "blocks": section.get("content") or [],
            "section_type": section.get("type") or "overview",
        }
        if section.get("command"):
            page["eyebrow"] = section["command"]
        elif section.get("token"):
            page["eyebrow"] = section["token"]
        pages.append(page)
    return pages


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
    base_command: str = "",
    options: list[dict[str, Any]] | None = None,
    arguments: list[dict[str, Any]] | None = None,
    authored_sections: list[dict[str, Any]] | None = None,
    diagram: dict[str, Any] | None = None,
) -> dict[str, Any]:
    sections = authored_sections or _sections(
        canonical_command=canonical_command,
        summary=summary,
        syntax=syntax,
        effects=effects,
        boundaries=boundaries,
        watch_for=watch_for,
        readiness=readiness,
        terminal_output=terminal_output,
        options=options,
        arguments=arguments,
        diagram=diagram,
    )
    return {
        "key": key,
        "base_command": base_command or base_command_for_command(canonical_command),
        "display_name": display_name,
        "canonical_command": canonical_command,
        "aliases": aliases,
        "summary": summary,
        "tags": tags,
        "sections": sections,
        "pages": pages_from_command_sections(sections),
    }


def tome_pages(sections: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Build a tome's renderable pages from authored sections.

    Tomes (general lessons) are authored with the same section/block vocabulary
    as command library entries, so the Storey Book reader renders both."""
    return pages_from_command_sections(sections)


# ── Authored library entries ─────────────────────────────────────────────────
# The command library is seeded content: entries are authored here and persisted
# to the ``LibraryEntry`` model by ``python manage.py seed_command_library``.
# Each dict maps 1:1 to the arguments of ``_content`` above. Copy the ``git init``
# entry as a template when authoring a new command.
LIBRARY_ENTRIES: list[dict[str, Any]] = [
    {
        # Stable identifier for the entry (kebab-case). Also the seed lookup key.
        "key": "git-init",
        # Human label shown in the book's command rail.
        "display_name": "git init",
        # The canonical, fully-written form the content is authored against.
        "canonical_command": "git init",
        # Base command used for grouping (defaults from canonical when omitted).
        "base_command": "git init",
        # Other accepted spellings/forms for this command.
        "aliases": ["git init <directory>", "git init -b <branch>", "git init -q"],
        # One-paragraph summary shown at the top of the command.
        "summary": "git init creates Git metadata for a folder so future snapshots can be tracked there.",
        # Free-form tags (diagnostic/action/…); surfaced to the book payload.
        "tags": ["action", "setup"],
        # Authored syntax examples; each becomes a syntax page.
        "syntax": [
            "git init",
            "git init <directory>",
            "git init -b <branch>",
            "git init --quiet",
        ],
        "effects": ["Creates the repository metadata directory for the folder."],
        "boundaries": ["It does not stage or commit any existing project files."],
        "watch_for": "Running it inside a folder that is already a repository.",
        "readiness": ["Confirm you are in the intended folder before initializing."],
        "terminal_output": "Initialized empty Git repository in /path/.git/",
        # ── Sub-navigation: options & arguments ──────────────────────────────
        # Each option/argument becomes its own page AND a sub-nav item in the
        # Storey Book (e.g. git init → -q / --quiet, -b / --initial-branch).
        "options": [
            {
                "token": "-b / --initial-branch",
                "title": "Initial branch name",
                "body": "Names the first branch instead of accepting the default branch name.",
            },
            {
                "token": "-q / --quiet",
                "title": "Quiet init",
                "body": "Suppresses the confirmation message while still creating the repository.",
            },
        ],
        "arguments": [
            {
                "token": "<directory>",
                "title": "Destination directory",
                "body": "Initializes the named folder instead of the current working directory.",
            },
        ],
        # ── Authored diagram (optional) ──────────────────────────────────────
        # Rendered as neon SVG in the book. kind="flow" | "dag".
        "diagram": _diagram(
            kind="flow",
            title="What init sets up",
            caption="git init creates the .git metadata folder; your files stay untracked until you stage and commit them.",
            nodes=[
                {"id": "folder", "label": "Project folder", "accent": "muted"},
                {"id": "repo", "label": ".git metadata", "accent": "cyan"},
            ],
            edges=[{"from": "folder", "to": "repo", "label": "git init"}],
        ),
    },
    # TODO(authoring): add the remaining commands registered across the storeys
    # here, one dict per command, following the template above.
]
