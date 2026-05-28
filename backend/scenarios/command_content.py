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


def command_content_key_for_command(command: str) -> str:
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
    key = command_content_key_for_command(syntax or command)
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
        return "This is a reading command in Module 1. It gives evidence for the next decision, but the repository state should remain unchanged after the preview command runs."
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
                title="Practice notes",
                content=[
                    _paragraph(
                        "Use this page as the last check before opening an authored practice variant. The preview teaches behavior; the scenario will still require you to apply the exact values from its brief."
                    ),
                    _bullets("Before running it", readiness),
                    _bullets(
                        "During practice",
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


def _git_log_sections() -> list[dict[str, Any]]:
    return [
        _section(
            section_id="overview",
            section_type="overview",
            title="Overview",
            command="git log",
            content=[
                _paragraph(
                    "git log reads commit history. The simulator supports the base history view, "
                    "a compact one-line view, a graph view across all refs, and simple count limits."
                ),
                _callout(
                    "Mental model",
                    "This is a reading command in Module 1. It gives evidence for the next decision, "
                    "but the repository state should remain unchanged after the preview command runs.",
                ),
                _bullets(
                    "What to look at before using it",
                    [
                        "Identify the specific history question the scenario asks: message, commit order, branch tips, or count.",
                        "Decide whether you need the full log, one-line compact view, graph across all refs, or a limited count.",
                        "Note any commit id the scenario requires so you can verify it appears in the output.",
                    ],
                ),
                _terminal(
                    "commit c2\nAuthor: Demo User\n\n    Add profile validation\n\ncommit c1\nAuthor: Demo User\n\n    Add baseline feature"
                ),
                _bullets(
                    "How to verify the result",
                    [
                        "Expected result: Reports commit history without changing HEAD, branches, staging, or working-tree files.",
                        "Before running it: Identify which log syntax the scenario asks for (base, --oneline, --graph --all, or -n <number>).",
                        "Verify commit order before choosing a commit id or judging whether history looks correct.",
                        "Do not expect it to do this: stage, commit, switch branches, discard edits, or fetch remote data.",
                    ],
                ),
            ],
        ),
        _rich_syntax_section(
            section_id=command_syntax_section_id("git log"),
            title="Reading History",
            command="git log",
            does=(
                "git log shows commit history from the current HEAD. Use it when you need commit "
                "messages, authorship-style context, parent order, or the newest commit before choosing an action."
            ),
            sample_output="commit c2\nAuthor: Demo User\n\n    Add profile validation\n\ncommit c1\nAuthor: Demo User\n\n    Add baseline feature",
            how_to_read=[
                "The top commit is the newest commit reachable from the current HEAD.",
                "The commit id, such as c2, is the name you can pass to supported diagnostic commands like git show.",
                "The indented message is the human explanation of that snapshot.",
            ],
            effects=["No repository state changes. It only reads commit history."],
            boundaries=[
                "It does not show unstaged file edits.",
                "It does not stage, commit, switch branches, or rewrite history.",
            ],
            mistake="Reading the newest message as proof that the working tree is clean. Pair history checks with git status when files may have changed.",
        ),
        _rich_syntax_section(
            section_id=command_syntax_section_id("git log --oneline"),
            title="Compact History",
            command="git log --oneline",
            does=(
                "git log --oneline compresses each commit into one row. It is the fastest way to "
                "scan commit order and messages when the full commit body is more detail than you need."
            ),
            sample_output="c2 Add profile validation\nc1 Add baseline feature",
            how_to_read=[
                "Each line starts with a short commit id followed by the commit message.",
                "Rows are still newest first.",
                "Use this view to answer questions like what changed most recently or whether the expected message exists.",
            ],
            effects=["No repository state changes. It only changes how history is displayed."],
            boundaries=[
                "It does not hide commits; it hides extra detail from each commit row.",
                "It does not tell you whether files are staged or unstaged.",
            ],
            mistake="Copying a short id from the wrong line because the output is compact. Read the message beside the id before using it.",
        ),
        _rich_syntax_section(
            section_id=command_syntax_section_id("git log --oneline --graph --all"),
            title="Visual Branch History",
            command="git log --oneline --graph --all",
            does=(
                "git log --oneline --graph --all shows compact history with branch shape. In the simulator, "
                "this is the teaching syntax for seeing more than the current branch path."
            ),
            sample_output="* c3 (feature) Draft profile copy\n| * c2 (main) Add profile validation\n|/\n* c1 Add baseline feature",
            how_to_read=[
                "Asterisks mark commits, while lines show how branch paths relate.",
                "Labels in parentheses show branch tips or known refs when the simulator can display them.",
                "--all matters when the task asks about branch tips beyond the current branch.",
            ],
            effects=["No repository state changes. It only draws history with branch context."],
            boundaries=[
                "It does not merge branches or move branch tips.",
                "It does not fetch remote history; it only shows refs already present in simulator state.",
            ],
            mistake="Assuming graph lines changed the repository. They are visual output only; choose an action command separately if the task asks for a change.",
        ),
        _rich_syntax_section(
            section_id=command_syntax_section_id("git log -n <number>"),
            title="Limit History by Count",
            command="git log -n <number>",
            does=(
                "git log -n <number> shows only the newest number of commits requested by the scenario. "
                "Use it when the task asks for a short recent history window instead of the full log."
            ),
            sample_output="c3 Finalize profile card\nc2 Add profile validation",
            how_to_read=[
                "Replace <number> with the exact count named by the scenario.",
                "The output is still newest first; it is only shorter than the full log.",
                "If the scenario asks for two recent commits, showing more commits is unnecessary evidence.",
            ],
            effects=["No repository state changes. It only limits how many history rows are printed."],
            boundaries=[
                "It does not delete older commits.",
                "It does not change which branch HEAD points to.",
            ],
            mistake="Typing the word <number> literally or using a count different from the scenario requirement.",
        ),
        _rich_syntax_section(
            section_id=command_syntax_section_id("git log --max-count=<number>"),
            title="Limit History with --max-count",
            command="git log --max-count=<number>",
            does=(
                "git log --max-count=<number> is the long-option version of limiting history output. "
                "It is useful when the preview or scenario emphasizes the named option rather than the short -n syntax."
            ),
            sample_output="c3 Finalize profile card\nc2 Add profile validation",
            how_to_read=[
                "The value after = is the maximum number of commits to display.",
                "The commits themselves are unchanged; only the printed list is limited.",
                "Use this syntax when the scenario specifically names --max-count or asks for the long option syntax.",
            ],
            effects=["No repository state changes. It only limits displayed history."],
            boundaries=[
                "It does not squash, hide, or remove commits from the repository.",
                "It does not inspect working-tree or staged changes.",
            ],
            mistake="Confusing limited output with limited history. Older commits still exist even if this syntax does not print them.",
        ),
        _section(
            section_id="option-oneline",
            section_type="option",
            title="Option: --oneline",
            token="--oneline",
            content=[
                _paragraph(
                    "--oneline keeps the history order but prints each commit as a short id plus message. "
                    "Use it for quick scanning before choosing a commit to inspect."
                ),
                _bullets(
                    "Good for",
                    [
                        "Finding the newest commit message.",
                        "Comparing a short sequence of recent commits.",
                        "Copying a commit id for a follow-up git show command.",
                    ],
                ),
            ],
        ),
        _section(
            section_id="option-graph",
            section_type="option",
            title="Option: --graph",
            token="--graph",
            content=[
                _paragraph(
                    "--graph adds visual branch lines to log output. It is most useful with --oneline "
                    "because the compact rows leave room for the branch drawing."
                ),
                _warning(
                    "Do not treat graph marks as commands. The marks only explain relationships between commits."
                ),
            ],
        ),
        _section(
            section_id="option-all",
            section_type="option",
            title="Option: --all",
            token="--all",
            content=[
                _paragraph(
                    "--all asks the simulator to include all known refs in the log traversal, not only the "
                    "current branch path. Use it when a scenario asks about another branch tip."
                ),
                _bullets(
                    "Boundaries",
                    [
                        "It does not contact a remote.",
                        "It does not create, delete, or switch branches.",
                    ],
                ),
            ],
        ),
        _section(
            section_id="option-count",
            section_type="option",
            title="Option: -n / --max-count",
            token="-n / --max-count",
            content=[
                _paragraph(
                    "-n and --max-count limit how many commits the simulator prints. Use them when a task asks for only the most recent entries."
                ),
                _bullets(
                    "Accepted syntax",
                    ["git log -n <number>", "git log --max-count=<number>"],
                ),
            ],
        ),
        _section(
            section_id="effects",
            section_type="effect",
            title="Effects and boundaries",
            content=[
                _bullets(
                    "Repository effect",
                    ["Reports commit history, commit ids, messages, and branch shape only."],
                ),
                _bullets(
                    "What does not change",
                    [
                        "HEAD stays where it is.",
                        "Branches, commits, staged files, and working-tree files are unchanged.",
                        "No remote data is fetched.",
                    ],
                ),
            ],
        ),
        _section(
            section_id="mistakes",
            section_type="mistake",
            title="Common Mistakes",
            content=[
                _warning(
                    "Using git log as a cleanliness check. History output tells you what has been committed, not what is currently staged or edited."
                ),
                _bullets(
                    "Watch for",
                    [
                        "Reading only the first oneline row when the task asks about branch shape.",
                        "Forgetting --all when the relevant commit is on another known ref.",
                        "Assuming --graph performs a branch operation instead of drawing output.",
                    ],
                ),
            ],
        ),
        _section(
            section_id="practice-notes",
            section_type="practice_note",
            title="Practice notes",
            content=[
                _paragraph(
                    "Use history output as evidence, not as the final action. In an authored scenario, read the newest commit, branch labels, and graph shape first, then decide whether a separate action command is needed."
                ),
                _bullets(
                    "Before relying on log output",
                    [
                        "Check whether the scenario asks about the current branch only or every known ref.",
                        "Pair log with git status when working-tree or staged changes may matter.",
                        "Copy commit ids only after confirming the message beside the id is the one you mean.",
                    ],
                ),
            ],
        ),
    ]


GIT_COMMAND_CONTENT_LIBRARY: list[dict[str, Any]] = [
    _content(
        key="git-status",
        display_name="git status",
        canonical_command="git status",
        aliases=[
            "git status -s",
            "git status --short",
            "git status --porcelain",
            "git status -sb",
            "git status --ignored",
        ],
        summary=(
            "git status reports the current branch, staged changes, unstaged changes, "
            "and untracked files without changing repository state."
        ),
        tags=["diagnostic", "working-tree", "index"],
        syntax=[
            "git status",
            "git status -s",
            "git status --short",
            "git status --porcelain",
            "git status -sb",
            "git status --ignored",
        ],
        effects=["Reports repository state only."],
        boundaries=["It does not stage, commit, discard, or rewrite files."],
        watch_for="Treating status output as a fix instead of evidence.",
        readiness=["Name the branch, staged paths, unstaged paths, and untracked paths."],
        terminal_output="On branch main\nChanges to be committed:\n  modified: demo.txt",
        options=[
            {
                "token": "-s / --short",
                "title": "Short status",
                "body": "Shows the same repository state in compact two-column status lines.",
            },
            {
                "token": "--porcelain",
                "title": "Porcelain status",
                "body": "Uses the simulator's short status output for stable machine-readable status practice.",
            },
            {
                "token": "-sb",
                "title": "Short status with branch",
                "body": "Adds the current branch header to compact status output.",
            },
            {
                "token": "--ignored",
                "title": "Show ignored files",
                "body": "Includes ignored working-tree paths so .gitignore scenarios can verify generated files are excluded.",
            },
        ],
    ),
    _content(
        key="git-log",
        display_name="git log",
        canonical_command="git log",
        aliases=[
            "git log --oneline",
            "git log --oneline --graph --all",
            "git log -n <number>",
            "git log --max-count=<number>",
        ],
        summary=(
            "git log reads commit history. Formatting flags change how the history is "
            "shown, not the commits themselves."
        ),
        tags=["diagnostic", "history"],
        syntax=[
            "git log",
            "git log --oneline",
            "git log --oneline --graph --all",
            "git log -n <number>",
            "git log --max-count=<number>",
        ],
        effects=["Reports commit history and branch shape only."],
        boundaries=["It does not move HEAD, create commits, or edit files."],
        watch_for="Reading only the newest line when the task asks for branch or graph context.",
        readiness=["Identify the latest commit, message, and relevant branch tips."],
        authored_sections=_git_log_sections(),
    ),
    _content(
        key="git-diff",
        display_name="git diff",
        canonical_command="git diff",
        aliases=[
            "git diff <path>",
            "git diff --staged",
            "git diff --cached",
            "git diff HEAD",
            "git diff --name-only",
            "git diff --ours <path>",
            "git diff --theirs <path>",
            "git diff --base <path>",
            "git diff --check",
        ],
        summary="git diff shows working-tree, staged, range, or conflict-side changes before you act.",
        tags=["diagnostic", "working-tree", "diff", "conflict-resolution"],
        syntax=[
            "git diff",
            "git diff <path>",
            "git diff --staged",
            "git diff --cached",
            "git diff --staged <path>",
            "git diff --cached <path>",
            "git diff HEAD",
            "git diff --name-only",
            "git diff --staged --name-only",
            "git diff --ours <path>",
            "git diff --theirs <path>",
            "git diff --base <path>",
            "git diff --check",
            "git diff --check <path>",
        ],
        effects=["Reports content differences or conflict-marker warnings only."],
        boundaries=["It does not resolve, stage, commit, or discard changes."],
        watch_for="Assuming plain git diff includes staged changes or both sides of a conflict.",
        readiness=["Use it before staging when you need to inspect working-tree edits, staged content, or conflict sides."],
        options=[
            {
                "token": "--staged / --cached",
                "title": "Staged diff",
                "body": "Shows what is already in the index for the next commit instead of unstaged working-tree edits.",
            },
            {
                "token": "HEAD",
                "title": "All changes since HEAD",
                "body": "Shows the combined staged and unstaged tracked changes since the latest commit.",
            },
            {
                "token": "--name-only",
                "title": "Path names only",
                "body": "Prints only changed paths for quick beginner-friendly diagnostics.",
            },
            {
                "id": "option-conflict-sides",
                "token": "--ours / --theirs / --base",
                "title": "Conflict side diff",
                "body": "Shows the current branch side, incoming branch side, or common base for a conflicted path.",
            },
            {
                "id": "option-check",
                "token": "--check",
                "title": "Conflict marker check",
                "body": "Reports leftover conflict marker lines so you can catch unresolved files before staging.",
            },
        ],
        arguments=[
            {
                "token": "<path>",
                "title": "Path filter",
                "body": "Limits the diff output to a path the simulator knows about.",
            },
        ],
    ),
    _content(
        key="git-diff-staged",
        display_name="git diff --staged",
        canonical_command="git diff --staged",
        base_command="git diff",
        aliases=[
            "git diff --cached",
            "git diff --staged <path>",
            "git diff --cached <path>",
            "git diff --staged --name-only",
        ],
        summary="git diff --staged shows what is already in the index for the next commit.",
        tags=["diagnostic", "index", "diff"],
        syntax=[
            "git diff --staged",
            "git diff --cached",
            "git diff --staged <path>",
            "git diff --cached <path>",
            "git diff --staged --name-only",
        ],
        effects=["Reports staged content changes only."],
        boundaries=["It does not include unstaged working-tree edits."],
        watch_for="Checking only plain diff and missing what is already staged.",
        readiness=["Compare staged diff with status before committing."],
        options=[
            {
                "token": "--staged / --cached",
                "title": "Read the index",
                "body": "Switches diff from unstaged working-tree changes to the staged snapshot.",
            },
        ],
    ),
    _content(
        key="git-show",
        display_name="git show",
        canonical_command="git show",
        aliases=["git show <commit>", "git show --name-only"],
        summary="git show displays details for the current or named Git object, usually a commit.",
        tags=["diagnostic", "history", "object"],
        syntax=["git show", "git show <commit>", "git show --name-only"],
        effects=["Reports commit metadata and patch details only."],
        boundaries=["It does not change branches, files, or the index."],
        watch_for="Inspecting the wrong commit when the task names a specific revision.",
        readiness=["Confirm whether you need HEAD or a named commit."],
        arguments=[
            {
                "token": "<commit>",
                "title": "Object to inspect",
                "body": "The simulator accepts at most one object name; omitting it means HEAD.",
            },
        ],
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
        options=[
            {
                "token": "-v",
                "title": "Verbose branch list",
                "body": "Adds commit-tip detail to the branch listing.",
            },
        ],
    ),
    _content(
        key="git-remote-v",
        display_name="git remote -v",
        canonical_command="git remote -v",
        base_command="git remote",
        aliases=["git remote"],
        summary="git remote -v lists configured remote names and their fetch/push URLs.",
        tags=["diagnostic", "remotes"],
        syntax=["git remote", "git remote -v"],
        effects=["Reports configured remote relationships only."],
        boundaries=["Remote listing does not contact the remote or change remote-tracking branches."],
        watch_for="Assuming a remote listing proves local history is up to date.",
        readiness=["Confirm the remote name and URL before clone or remote-related work."],
        options=[
            {
                "token": "-v / --verbose",
                "title": "Verbose remote list",
                "body": "Shows fetch and push URLs for each configured remote.",
            },
        ],
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
        key="git-check-ignore",
        display_name="git check-ignore -v",
        canonical_command="git check-ignore -v <path>",
        base_command="git check-ignore",
        aliases=[],
        summary="git check-ignore -v explains which .gitignore rule matched an ignored path.",
        tags=["diagnostic", "ignore"],
        syntax=["git check-ignore -v <path>"],
        effects=["Reports ignore-rule evidence only."],
        boundaries=["It does not edit .gitignore, stage files, or untrack anything."],
        watch_for="Using it on a path that is not ignored and assuming silence means success.",
        readiness=["Use it after adding ignore rules when a scenario asks you to verify a generated path."],
        options=[
            {
                "token": "-v",
                "title": "Verbose rule source",
                "body": "Shows the simulated .gitignore source and matching rule token for the path.",
            },
        ],
        arguments=[
            {
                "token": "<path>",
                "title": "Ignored path",
                "body": "Names one generated or local path to check.",
            },
        ],
    ),
    _content(
        key="git-ls-files",
        display_name="git ls-files",
        canonical_command="git ls-files",
        aliases=["git ls-files -u", "git ls-files --unmerged"],
        summary="git ls-files lists tracked paths; -u shows unmerged conflict stages.",
        tags=["diagnostic", "index", "conflict-resolution"],
        syntax=["git ls-files", "git ls-files -u", "git ls-files --unmerged"],
        effects=["Reports tracked paths or unmerged index stages only."],
        boundaries=["It does not include ignored untracked files, stage new files, or resolve conflicts."],
        watch_for="Confusing tracked file lists with conflict-stage evidence. Use -u when you need unmerged paths.",
        readiness=["Use it when you need to confirm whether a generated path is tracked or which paths are unmerged."],
        options=[
            {
                "id": "option-unmerged",
                "token": "-u / --unmerged",
                "title": "Unmerged index stages",
                "body": "Lists the base, current, and incoming stages for each conflicted path.",
            },
        ],
    ),
    _content(
        key="git-init",
        display_name="git init",
        canonical_command="git init",
        aliases=[
            "git init <directory>",
            "git init -b <branch>",
            "git init --initial-branch <branch>",
            "git init --initial-branch=<branch>",
            "git init -b <branch> <directory>",
            "git init --initial-branch=<branch> <directory>",
            "git init -q",
            "git init --quiet",
            "git init --quiet <directory>",
        ],
        summary=(
            "git init creates Git metadata for a folder so future snapshots can be "
            "tracked there."
        ),
        tags=["action", "repository-setup"],
        syntax=[
            "git init",
            "git init <directory>",
            "git init -b <branch>",
            "git init --initial-branch <branch>",
            "git init --initial-branch=<branch>",
            "git init -b <branch> <directory>",
            "git init --initial-branch=<branch> <directory>",
            "git init -q",
            "git init --quiet",
            "git init --quiet <directory>",
            "git init -q -b <branch> <directory>",
            "git init --quiet --initial-branch=<branch> <directory>",
        ],
        effects=["Creates simulator Git metadata at the current or named directory; safe reinitialization preserves existing repository state."],
        boundaries=["It does not stage files, create commits, or rewrite file contents."],
        watch_for="Initializing the parent folder when the scenario names a child directory.",
        readiness=["Check whether the task names the current folder or a destination folder."],
        options=[
            {
                "token": "-b / --initial-branch",
                "title": "Initial branch name",
                "body": "Sets the first branch name in simulator state instead of using main.",
            },
            {
                "token": "-q / --quiet",
                "title": "Quiet init",
                "body": "Suppresses extra initialization chatter while still creating the simulator repository state.",
            },
        ],
        arguments=[
            {
                "token": "<directory>",
                "title": "Destination directory",
                "body": "Records that the repository was initialized in a named directory.",
            },
        ],
    ),
    _content(
        key="git-clone",
        display_name="git clone",
        canonical_command="git clone <url>",
        aliases=[
            "git clone <url> <directory>",
            "git clone -b <branch> <url>",
            "git clone --branch <branch> <url>",
            "git clone --depth <number> <url>",
        ],
        summary=(
            "git clone creates a local working copy from a remote repository and sets "
            "up the origin and upstream relationship."
        ),
        tags=["action", "remote", "repository-setup"],
        syntax=[
            "git clone <url>",
            "git clone <url> <directory>",
            "git clone -b <branch> <url>",
            "git clone --branch <branch> <url>",
            "git clone -b <branch> <url> <directory>",
            "git clone --branch <branch> <url> <directory>",
            "git clone --depth <number> <url>",
            "git clone --depth <number> <url> <directory>",
            "git clone --depth <number> -b <branch> <url> <directory>",
            "git clone --depth <number> --branch <branch> <url> <directory>",
        ],
        effects=[
            "Creates a local repository, configures origin, checks out the selected branch, and leaves the working tree clean.",
            "Records an origin remote URL and an origin/<branch> remote-tracking branch for the checked-out branch.",
        ],
        boundaries=[
            "It does not modify the remote repository.",
            "Module 1 does not support advanced clone options such as --bare, --mirror, submodules, filters, or templates.",
        ],
        watch_for="Use the exact destination, branch, and depth requested by the scenario.",
        readiness=[
            "Confirm whether the URL is HTTPS or SSH, whether a custom destination is named, and whether the branch or depth is specified.",
        ],
        options=[
            {
                "token": "-b / --branch",
                "title": "Selected branch",
                "body": "Checks out the named remote branch instead of the default branch and tracks origin/<branch>.",
            },
            {
                "token": "--depth",
                "title": "Shallow history",
                "body": "Uses a positive number to limit visible cloned history, such as --depth 1 for only the tip commit.",
            },
        ],
        arguments=[
            {
                "token": "<url>",
                "title": "Remote URL",
                "body": "Required. HTTPS URLs and SSH-style URLs are both recorded as the origin URL for the local copy.",
            },
            {
                "token": "<directory>",
                "title": "Destination folder",
                "body": "Optional. If omitted, Module 1 infers the folder name from the repository URL.",
            },
            {
                "token": "<branch>",
                "title": "Branch name",
                "body": "Names a branch that must exist in the simulated remote fixture.",
            },
            {
                "token": "<number>",
                "title": "Depth",
                "body": "Must be a positive integer. Module 1 uses it to mark the clone as shallow.",
            },
        ],
    ),
    _content(
        key="git-add",
        display_name="git add",
        canonical_command="git add <path>",
        aliases=["git add .", "git add -A", "git add --all", "git add -u", "git add --update"],
        summary="git add copies selected working-tree changes into the staging area.",
        tags=["action", "index", "staging"],
        syntax=[
            "git add <path>",
            "git add <path> <path>",
            "git add <directory>/",
            "git add .",
            "git add -A",
            "git add --all",
            "git add -u",
            "git add --update",
            "git add -p <path>",
            "git add --patch <path>",
        ],
        effects=["Moves selected path changes from the working tree into the index."],
        boundaries=["It does not create a commit or remove the edits from your files."],
        watch_for="Staging every file when only one path belongs in the next commit.",
        readiness=["Use status and diff to confirm the path before staging."],
        options=[
            {
                "token": "-A / --all",
                "title": "Stage all changes",
                "body": "Stages tracked and untracked changes selected by the simulator path rules.",
            },
            {
                "token": "-u / --update",
                "title": "Stage tracked changes only",
                "body": "Stages modifications and deletions to tracked files without adding new untracked files.",
            },
            {
                "token": "-p / --patch",
                "title": "Patch staging",
                "body": "Stages authored partial hunks instead of the whole selected file.",
            },
        ],
        arguments=[
            {
                "token": "<path>",
                "title": "Pathspec",
                "body": "Selects one or more paths for staging; use it instead of staging unrelated files.",
            },
        ],
    ),
    _content(
        key="git-add-p",
        display_name="git add -p",
        canonical_command="git add -p",
        base_command="git add",
        aliases=["git add -p <path>", "git add --patch <path>"],
        summary="git add -p lets you stage selected hunks instead of an entire file.",
        tags=["action", "index", "partial-staging"],
        syntax=["git add -p", "git add -p <path>", "git add --patch <path>"],
        effects=["Moves selected hunks from the working tree into the index."],
        boundaries=["It leaves unselected hunks in the working tree."],
        watch_for="Accepting unrelated hunks because they happen to be in the same file.",
        readiness=["Read each hunk and match it to the scenario's requested change."],
        options=[
            {
                "token": "-p / --patch",
                "title": "Patch staging",
                "body": "Uses the simulator's authored hunk data to stage only selected changes.",
            },
        ],
        arguments=[
            {
                "token": "<path>",
                "title": "Optional path",
                "body": "Limits patch staging to a path; when omitted, the simulator uses available authored hunks.",
            },
        ],
    ),
    _content(
        key="git-rm-cached",
        display_name="git rm --cached",
        canonical_command="git rm --cached <path>",
        base_command="git rm",
        aliases=[],
        summary="git rm --cached removes a path from the index while leaving the local file present.",
        tags=["action", "index", "ignore"],
        syntax=["git rm --cached <path>", "git rm -r --cached <directory>"],
        effects=["Stages removal of the tracked path from future commits."],
        boundaries=["It does not delete the local working-tree file."],
        watch_for="Using a removal command that deletes a local file you meant to keep.",
        readiness=["Use it with ignore rules when a generated file is already tracked."],
        options=[
            {
                "token": "--cached",
                "title": "Keep the local file",
                "body": "Removes the path from the index while preserving it in the working tree as ignored content.",
            },
        ],
        arguments=[
            {
                "token": "<path>",
                "title": "Path to remove",
                "body": "Names the tracked, staged, or working-tree path affected by git rm.",
            },
        ],
    ),
    _content(
        key="git-commit",
        display_name="git commit",
        canonical_command='git commit -m "message"',
        aliases=[
            'git commit --message "message"',
            'git commit -am "message"',
            'git commit -a -m "message"',
        ],
        summary="git commit saves the staged snapshot and advances the current branch tip.",
        tags=["action", "history", "snapshot"],
        syntax=[
            'git commit -m "message"',
            'git commit --message "message"',
            'git commit -am "message"',
            'git commit -a -m "message"',
            "git commit --amend",
            'git commit --amend -m "message"',
            "git commit --amend --no-edit",
        ],
        effects=["Creates a new commit from the index and moves the current branch to it."],
        boundaries=["It does not include unstaged changes or ignored files."],
        watch_for="Committing before checking exactly what is staged.",
        readiness=["Confirm staged paths and the required message before committing."],
        options=[
            {
                "token": "-m / --message",
                "title": "Commit message",
                "body": "Supplies the commit message accepted by the simulator.",
            },
            {
                "token": "-a / --all",
                "title": "Stage tracked changes before committing",
                "body": "Stages modifications to tracked files, then creates the commit.",
            },
            {
                "token": "--amend",
                "title": "Amend latest commit",
                "body": "Replaces the latest local commit instead of creating a new follow-up commit.",
            },
        ],
    ),
    _content(
        key="git-commit-amend",
        display_name="git commit --amend",
        canonical_command="git commit --amend",
        base_command="git commit",
        aliases=['git commit --amend -m "message"', "git commit --amend --no-edit"],
        summary=(
            "git commit --amend replaces the latest local commit with a corrected "
            "commit instead of adding a follow-up commit."
        ),
        tags=["action", "history", "rewrite"],
        syntax=["git commit --amend", 'git commit --amend -m "message"', "git commit --amend --no-edit"],
        effects=["Replaces the latest local commit with a new commit object."],
        boundaries=["It should not be used to rewrite shared history in these local-only scenarios."],
        watch_for="Creating a second commit instead of repairing the latest one.",
        readiness=["Confirm the commit is local and the staged content/message are correct."],
        options=[
            {
                "token": "--amend",
                "title": "Replace latest commit",
                "body": "Creates a replacement commit and records the replaced commit in simulator metadata.",
            },
            {
                "token": "--no-edit",
                "title": "Keep the old message",
                "body": "Accepted only with --amend; keeps the existing commit message when staged content changes.",
            },
            {
                "token": "-m / --message",
                "title": "New amend message",
                "body": "Supplies the message for the replacement commit.",
            },
        ],
    ),
    _content(
        key="git-restore",
        display_name="git restore",
        canonical_command="git restore <path>",
        aliases=["git restore <path> <path>", "git restore ."],
        summary="git restore discards selected working-tree changes by restoring paths from the index or HEAD.",
        tags=["action", "working-tree", "discard"],
        syntax=["git restore <path>", "git restore <path> <path>", "git restore ."],
        effects=["Replaces selected working-tree paths with the chosen source version."],
        boundaries=["It does not affect unrelated paths."],
        watch_for="Restoring the wrong path and losing edits you meant to keep.",
        readiness=["Separate paths to discard from paths to keep before running it."],
        arguments=[
            {
                "token": "<path>",
                "title": "Path to restore",
                "body": "Required. Names the working-tree path whose local changes should be discarded.",
            },
        ],
    ),
    _content(
        key="git-restore-staged",
        display_name="git restore --staged",
        canonical_command="git restore --staged <path>",
        base_command="git restore",
        aliases=["git restore --staged <path> <path>", "git restore --staged ."],
        summary="git restore --staged moves selected changes out of the staging area.",
        tags=["action", "index", "unstage"],
        syntax=[
            "git restore --staged <path>",
            "git restore --staged <path> <path>",
            "git restore --staged .",
        ],
        effects=["Updates the index so selected changes are no longer staged."],
        boundaries=["It does not discard the working-tree file content."],
        watch_for="Leaving off --staged and discarding work instead of unstaging it.",
        readiness=["Use status after unstaging to verify the path moved back to unstaged."],
        options=[
            {
                "token": "--staged",
                "title": "Unstage instead of discard",
                "body": "Moves selected staged content back to the working tree.",
            },
        ],
        arguments=[
            {
                "token": "<path>",
                "title": "Path to unstage",
                "body": "Required. Names the staged path to move out of the index.",
            },
        ],
    ),
    _content(
        key="git-merge",
        display_name="git merge",
        canonical_command="git merge <branch>",
        aliases=["git merge --abort", "git merge --continue"],
        summary="git merge integrates another branch into the current branch and may pause for conflict resolution.",
        tags=["action", "merge", "conflict-resolution"],
        syntax=["git merge <branch>", "git merge --abort", "git merge --continue"],
        effects=[
            "Starts a merge, records conflict state when files overlap, aborts an in-progress merge, or completes a resolved merge.",
        ],
        boundaries=[
            "It does not choose conflict content for you. Resolve conflicted files before continuing.",
        ],
        watch_for="Running another merge while unmerged files are still present.",
        readiness=[
            "Confirm the current branch, the incoming branch, and whether any conflict files are already unresolved.",
        ],
        options=[
            {
                "id": "option-abort",
                "token": "--abort",
                "title": "Cancel the merge",
                "body": "Restores the pre-merge state when the current conflict should not be completed.",
            },
            {
                "id": "option-continue",
                "token": "--continue",
                "title": "Complete resolved merge",
                "body": "Creates the merge commit after conflicted files have been resolved and staged.",
            },
        ],
        arguments=[
            {
                "token": "<branch>",
                "title": "Incoming branch",
                "body": "Names the local or remote-tracking branch to integrate into the current branch.",
            },
        ],
    ),
    _content(
        key="git-checkout-conflict-side",
        display_name="git checkout --ours/--theirs",
        canonical_command="git checkout --ours <path>",
        aliases=["git checkout --theirs <path>"],
        summary="git checkout --ours or --theirs copies one side of an unresolved conflict into the working tree.",
        tags=["action", "merge", "conflict-resolution"],
        syntax=["git checkout --ours <path>", "git checkout --theirs <path>"],
        effects=[
            "Replaces the conflicted working-tree file with either the current branch side or the incoming branch side.",
        ],
        boundaries=[
            "This simulator supports only --ours/--theirs for conflicted paths, not general branch checkout.",
            "It does not stage the file; the conflict remains unmerged until the path is added.",
        ],
        watch_for="Using the wrong side for the scenario goal before staging the resolved file.",
        readiness=["Confirm whether the goal asks for the current branch version or the incoming branch version."],
        options=[
            {
                "id": "option-ours",
                "token": "--ours",
                "title": "Current branch side",
                "body": "Uses the HEAD/current branch version of the conflicted file.",
            },
            {
                "id": "option-theirs",
                "token": "--theirs",
                "title": "Incoming branch side",
                "body": "Uses the incoming branch version of the conflicted file.",
            },
        ],
        arguments=[
            {
                "token": "<path>",
                "title": "Conflict path",
                "body": "Required. Names a file currently listed as unmerged.",
            },
        ],
    ),
    _content(
        key="git-mergetool",
        display_name="git mergetool",
        canonical_command="git mergetool",
        aliases=["git mergetool --tool <tool>"],
        summary="git mergetool opens the configured merge tool workflow for unresolved conflict paths.",
        tags=["action", "merge", "conflict-resolution"],
        syntax=["git mergetool", "git mergetool --tool <tool>", "git mergetool <path>"],
        effects=["Records that the merge tool was launched and opens the workspace conflict editor for selected paths."],
        boundaries=[
            "It only works when a merge conflict is in progress.",
            "It does not choose or stage the resolved file content for you.",
        ],
        watch_for="Running mergetool before a merge has produced unmerged files.",
        readiness=["Confirm the conflict path and merge tool requested by the scenario."],
        options=[
            {
                "id": "option-tool",
                "token": "--tool",
                "title": "Tool selection",
                "body": "Uses the named simulated merge tool for this run instead of relying only on stored config.",
            },
        ],
        arguments=[
            {
                "token": "<path>",
                "title": "Conflict path",
                "body": "Limits the merge tool run to one conflicted path.",
            },
        ],
    ),
    _content(
        key="git-config",
        display_name="git config",
        canonical_command="git config --global <key> <value>",
        aliases=["git config --global merge.tool <tool>"],
        summary="git config stores a simulator setting such as the merge tool name.",
        tags=["action", "configuration", "conflict-resolution"],
        syntax=["git config --global <key> <value>", "git config --global merge.tool <tool>"],
        effects=["Records the requested global config value in simulator metadata."],
        boundaries=["It does not launch a merge tool or change file content by itself."],
        watch_for="Configuring the tool but forgetting to run git mergetool during the conflict.",
        readiness=["Use the exact key and value requested by the scenario."],
        options=[
            {
                "id": "option-global",
                "token": "--global",
                "title": "Global setting",
                "body": "Stores the setting in the simulator's global config scope.",
            },
        ],
        arguments=[
            {"token": "<key>", "title": "Config key", "body": "Names the setting, such as merge.tool."},
            {"token": "<value>", "title": "Config value", "body": "Names the value to store, such as vscode or vimdiff."},
        ],
    ),
    _content(
        key="git-fetch",
        display_name="git fetch",
        canonical_command="git fetch",
        aliases=["git fetch <remote>"],
        summary="git fetch updates remote-tracking refs without moving the current local branch.",
        tags=["action", "remote", "diagnostic-setup", "conflict-prevention"],
        syntax=["git fetch", "git fetch <remote>"],
        effects=["Updates simulated remote-tracking branches and materializes fetched commits."],
        boundaries=["It does not merge, cherry-pick, or move the current branch tip."],
        watch_for="Assuming fetch has integrated the remote branch into your current branch.",
        readiness=["Compare local and remote-tracking branches after fetching when a scenario asks for prevention checks."],
        arguments=[
            {
                "token": "<remote>",
                "title": "Remote name",
                "body": "Names the remote to fetch; origin is used when omitted.",
            },
        ],
    ),
    _content(
        key="git-cherry-pick",
        display_name="git cherry-pick",
        canonical_command="git cherry-pick <commit>",
        aliases=["git cherry-pick --no-commit <commit>", "git cherry-pick --abort"],
        summary="git cherry-pick copies one selected commit onto the current branch.",
        tags=["action", "history", "backport"],
        syntax=["git cherry-pick <commit>", "git cherry-pick --no-commit <commit>", "git cherry-pick --abort"],
        effects=["Creates a new commit from the selected commit or stages its changes for review."],
        boundaries=["It does not merge the entire source branch history."],
        watch_for="Cherry-picking the branch tip when the scenario asks for one specific commit.",
        readiness=["Use log or show to confirm the selected commit before applying it."],
        options=[
            {
                "id": "option-no-commit",
                "token": "--no-commit / -n",
                "title": "Stage without committing",
                "body": "Applies the selected commit's changes to the index without creating the new commit yet.",
            },
            {
                "id": "option-abort",
                "token": "--abort",
                "title": "Cancel cherry-pick",
                "body": "Returns the branch to its original tip for an in-progress cherry-pick.",
            },
        ],
        arguments=[
            {
                "token": "<commit>",
                "title": "Source commit",
                "body": "Names the commit whose changes should be copied.",
            },
        ],
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
    # ── Module 2 command content ──────────────────────────────────────────────
    _content(
        key="git-switch",
        display_name="git switch",
        canonical_command="git switch <branch>",
        aliases=["git switch -c <branch>", "git switch --detach <commit>"],
        summary=(
            "git switch moves HEAD to a named branch. "
            "With -c it creates the branch first. "
            "With --detach it moves HEAD off any branch pointer."
        ),
        tags=["action", "branching", "navigation"],
        syntax=["git switch <branch>", "git switch -c <branch>", "git switch --detach <commit>"],
        effects=["Moves HEAD to the target branch or detached commit."],
        boundaries=["It does not commit, merge, or rewrite history."],
        watch_for="Forgetting -c when the branch does not exist yet.",
        readiness=["Use git branch to confirm the target branch exists before switching."],
        terminal_output="Switched to branch 'feature/auth'",
        options=[
            {
                "token": "-c / --create",
                "title": "Create and switch",
                "body": "Creates a new branch at the current HEAD (or an optional start point) and immediately switches to it.",
            },
            {
                "token": "--detach",
                "title": "Detach HEAD",
                "body": "Moves HEAD directly to the named commit without attaching it to a branch.",
            },
        ],
        arguments=[
            {
                "token": "<branch>",
                "title": "Branch name",
                "body": "The name of the branch to switch to, or create when -c is used.",
            },
        ],
    ),
    _content(
        key="git-checkout-b",
        display_name="git checkout -b",
        canonical_command="git checkout -b <branch>",
        aliases=["git checkout -b <branch> <start-point>"],
        summary=(
            "git checkout -b creates a new branch and checks it out in one step. "
            "An optional start point sets the commit the branch begins at."
        ),
        tags=["action", "branching", "legacy"],
        syntax=["git checkout -b <branch>", "git checkout -b <branch> <start-point>"],
        effects=["Creates the named branch and moves HEAD to it."],
        boundaries=["It does not commit or merge."],
        watch_for="Omitting the start point when the branch must begin at a specific older commit.",
        readiness=["Prefer git switch -c in modern workflows; git checkout -b is the legacy equivalent."],
        terminal_output="Switched to a new branch 'feature/auth'",
        options=[
            {
                "token": "-b",
                "title": "Create and checkout",
                "body": "Creates a new branch and immediately checks it out, equivalent to git branch then git checkout.",
            },
        ],
        arguments=[
            {
                "token": "<branch>",
                "title": "New branch name",
                "body": "The name of the branch to create.",
            },
            {
                "token": "<start-point>",
                "title": "Branch start point",
                "body": "Commit id or branch tip to begin the new branch from. Defaults to HEAD when omitted.",
            },
        ],
    ),
    _content(
        key="git-stash",
        display_name="git stash",
        canonical_command="git stash",
        aliases=["git stash pop", "git stash apply", "git stash drop", "git stash list"],
        summary=(
            "git stash saves uncommitted working-tree and index changes to a temporary stack "
            "so you can switch context and restore the work later."
        ),
        tags=["action", "working-tree", "context-switch"],
        syntax=["git stash", "git stash pop", "git stash apply", "git stash drop", "git stash list"],
        effects=["Stash saves changes; pop or apply restores them; drop discards one entry."],
        boundaries=["Stash does not create a permanent commit or push to any remote."],
        watch_for="Using stash pop when apply is safer because stash pop removes the entry even if conflicts occur.",
        readiness=["Check git stash list to verify the entry exists before pop or apply."],
        terminal_output="Saved working directory and index state WIP on feature/ui: c2 Add styles",
        options=[
            {
                "token": "pop",
                "title": "Restore and remove",
                "body": "Applies the most recent stash entry and removes it from the stack.",
            },
            {
                "token": "apply",
                "title": "Restore without removing",
                "body": "Applies a stash entry to the working tree but keeps it on the stack.",
            },
            {
                "token": "drop",
                "title": "Remove without restoring",
                "body": "Deletes one stash entry without applying it.",
            },
            {
                "token": "list",
                "title": "Show all stash entries",
                "body": "Lists all entries in the stash stack with their indices.",
            },
        ],
    ),
    _content(
        key="git-push",
        display_name="git push",
        canonical_command="git push",
        aliases=[
            "git push -u <remote> <branch>",
            "git push <remote> <branch>",
            "git push --force-with-lease <remote> <branch>",
            "git push <remote> --delete <branch>",
        ],
        summary=(
            "git push uploads local commits to a remote repository. "
            "-u sets upstream tracking. "
            "--force-with-lease safely overwrites the remote after a rebase."
        ),
        tags=["action", "remote", "collaboration"],
        syntax=[
            "git push",
            "git push -u <remote> <branch>",
            "git push <remote> <branch>",
            "git push --force-with-lease <remote> <branch>",
            "git push <remote> --delete <branch>",
        ],
        effects=["Moves the remote branch pointer forward (or deletes it)."],
        boundaries=["It does not merge, rebase, or create local commits."],
        watch_for="Using --force instead of --force-with-lease, which can overwrite a teammate's push.",
        readiness=["Confirm the local branch is ahead of the remote before pushing."],
        terminal_output="To https://example.test/demo/repository.git\n * [new branch]      feature/auth -> feature/auth",
        options=[
            {
                "token": "-u / --set-upstream",
                "title": "Set upstream tracking",
                "body": "Links the local branch to the remote branch so future git push and git pull can omit the remote and branch names.",
            },
            {
                "token": "--force-with-lease",
                "title": "Safe force push",
                "body": "Overwrites the remote branch only if it matches what you last fetched, preventing accidental overwrites of a teammate's commits.",
            },
            {
                "token": "--delete",
                "title": "Delete remote branch",
                "body": "Removes the named branch from the remote repository.",
            },
        ],
        arguments=[
            {
                "token": "<remote>",
                "title": "Remote name",
                "body": "The remote to push to; origin is used when omitted.",
            },
            {
                "token": "<branch>",
                "title": "Branch name",
                "body": "The local branch to push; HEAD's branch is used when omitted.",
            },
        ],
    ),
    _content(
        key="git-pull",
        display_name="git pull",
        canonical_command="git pull",
        aliases=["git pull --rebase", "git pull <remote> <branch>"],
        summary=(
            "git pull fetches from the remote and integrates changes into the current branch. "
            "--rebase replays local commits on top of the fetched tip instead of creating a merge commit."
        ),
        tags=["action", "remote", "collaboration"],
        syntax=["git pull", "git pull --rebase", "git pull <remote> <branch>"],
        effects=["Advances the local branch to include remote commits."],
        boundaries=["It does not push or create new remote branches."],
        watch_for="Forgetting --rebase when the team policy requires a linear history.",
        readiness=["Run git fetch and inspect remote branches before deciding to pull or rebase."],
        terminal_output="From https://example.test/demo/repository.git\n * branch  main -> FETCH_HEAD\nUpdating c1..c2\nFast-forward",
        options=[
            {
                "token": "--rebase",
                "title": "Rebase instead of merge",
                "body": "Replays local commits on top of the fetched remote tip, keeping a linear history.",
            },
        ],
        arguments=[
            {
                "token": "<remote>",
                "title": "Remote name",
                "body": "Overrides the default remote; origin is used when omitted.",
            },
            {
                "token": "<branch>",
                "title": "Remote branch",
                "body": "The remote branch to pull from; the tracked upstream is used when omitted.",
            },
        ],
    ),
    _content(
        key="git-merge-squash",
        display_name="git merge --squash",
        canonical_command="git merge --squash <branch>",
        aliases=[],
        summary=(
            "git merge --squash collapses all commits from the source branch into staged changes "
            "on the target branch without creating a merge commit. "
            "A separate git commit then lands the work as a single snapshot."
        ),
        tags=["action", "merging", "history"],
        syntax=["git merge --squash <branch>"],
        effects=["Stages all changes from the source branch as a single diff ready to commit."],
        boundaries=["It does not create a commit or merge-commit on its own."],
        watch_for="Forgetting to run git commit after the squash; the changes stay staged but no commit is recorded.",
        readiness=["Confirm the target branch is clean before squashing so you can isolate the incoming changes."],
        terminal_output="Squash commit -- not updating HEAD\nAutomatic merge went well; stopped before committing as requested",
        options=[
            {
                "token": "--squash",
                "title": "Squash into staged changes",
                "body": "Combines all commits from the source branch into staged working-tree edits; must be followed by git commit.",
            },
        ],
        arguments=[
            {
                "token": "<branch>",
                "title": "Source branch",
                "body": "The branch whose commits are squashed into the current branch's index.",
            },
        ],
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
                "base_command": item["base_command"],
                "display_name": item["display_name"],
                "canonical_command": item["canonical_command"],
                "aliases": item["aliases"],
                "summary": item["summary"],
                "tags": item["tags"],
                "sections": item["sections"],
                "pages": item["pages"],
                "is_active": True,
                "version": 1,
                "sort_order": sort_order,
            },
        )
    return len(active_keys)
