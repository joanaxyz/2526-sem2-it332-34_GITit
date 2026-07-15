from __future__ import annotations

from .library_commands import (
    COMMAND_KEY_ALWAYS_INCLUDED_SECTION_IDS,
    command_syntax_section_id,
    library_key_for_command,
    normalize_command_text,
)


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






