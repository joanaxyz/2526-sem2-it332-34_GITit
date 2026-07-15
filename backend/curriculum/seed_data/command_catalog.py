COMMAND_CATALOG = [
    {
        "module": "creating-inspecting-repositories",
        "slug": "git-init",
        "base_command": "git init",
        "title": "git init",
        "summary": "Create Git metadata in the current directory or a named directory.",
        "usages": [
            {"slug": "current-directory", "usage_form": "git init", "label": "Initialize the current folder"},
            {"slug": "named-directory", "usage_form": "git init <directory>", "label": "Initialize a named folder"},
            {"slug": "initial-branch", "usage_form": "git init -b <branch>", "label": "Choose the first branch name"},
        ],
    },
    {
        "module": "creating-inspecting-repositories",
        "slug": "git-clone",
        "base_command": "git clone",
        "title": "git clone",
        "summary": "Create a local repository from a remote URL and optionally choose branch, depth, or folder.",
        "usages": [
            {"slug": "default-folder", "usage_form": "git clone <url>", "label": "Clone into the default folder"},
            {"slug": "named-folder", "usage_form": "git clone <url> <folder>", "label": "Clone into a named folder"},
            {"slug": "branch", "usage_form": "git clone -b <branch> <url>", "label": "Clone a specific branch"},
            {"slug": "depth", "usage_form": "git clone --depth <n> <url>", "label": "Clone shallow history"},
        ],
    },
    {
        "module": "creating-inspecting-repositories",
        "slug": "git-status",
        "base_command": "git status",
        "title": "git status",
        "summary": "Inspect branch, staging, working directory, ignored, and conflict state without mutating the repository.",
        "usages": [
            {"slug": "plain", "usage_form": "git status", "label": "Read repository status"},
            {"slug": "short", "usage_form": "git status -s", "label": "Read compact status"},
            {"slug": "porcelain", "usage_form": "git status --porcelain", "label": "Read script-stable status"},
            {"slug": "ignored", "usage_form": "git status --ignored", "label": "Include ignored files"},
        ],
    },
    {
        "module": "creating-inspecting-repositories",
        "slug": "git-config",
        "base_command": "git config",
        "title": "git config",
        "summary": "Inspect and set Git identity and configuration values.",
        "usages": [
            {"slug": "global-user-name", "usage_form": "git config --global user.name <name>", "label": "Set global author name"},
            {"slug": "global-user-email", "usage_form": "git config --global user.email <email>", "label": "Set global author email"},
            {"slug": "list", "usage_form": "git config --list", "label": "List effective config"},
            {"slug": "alias", "usage_form": "git config --global alias.<name> <command>", "label": "Create a command alias"},
        ],
    },
    {
        "module": "creating-inspecting-repositories",
        "slug": "git-log",
        "base_command": "git log",
        "title": "git log",
        "summary": "Inspect commit history and branch shape.",
        "usages": [
            {"slug": "oneline", "usage_form": "git log --oneline", "label": "Compact history"},
            {"slug": "graph-all", "usage_form": "git log --oneline --graph --all", "label": "Graph all refs"},
            {"slug": "limit", "usage_form": "git log -n <count>", "label": "Limit history output"},
            {"slug": "patch", "usage_form": "git log -p", "label": "History with patches"},
            {"slug": "stat", "usage_form": "git log --stat", "label": "History with a change summary"},
        ],
    },
    {
        "module": "creating-inspecting-repositories",
        "slug": "git-show",
        "base_command": "git show",
        "title": "git show",
        "summary": "Inspect the latest commit or a named object without changing repository state.",
        "usages": [
            {"slug": "head", "usage_form": "git show", "label": "Inspect HEAD"},
            {"slug": "commit", "usage_form": "git show <commit>", "label": "Inspect a named commit"},
            {"slug": "name-only", "usage_form": "git show --name-only <commit>", "label": "Inspect changed paths in a commit"},
        ],
    },
    {
        # One global skill. `module` is the default chapter for its forms; a usage
        # can override it so the basic reading diffs land in Chapter 1 (Read the
        # Graph) while the precision name-only diff lives in Chapter 2.
        "module": "creating-inspecting-repositories",
        "slug": "git-diff",
        "base_command": "git diff",
        "title": "git diff",
        "summary": "Compare working, staged, and committed content before deciding what belongs in the next snapshot.",
        "usages": [
            {"slug": "working", "usage_form": "git diff", "label": "Inspect unstaged changes"},
            {"slug": "staged", "usage_form": "git diff --staged", "label": "Inspect staged changes"},
            {"slug": "name-only", "usage_form": "git diff --name-only", "label": "List changed paths only", "module": "tracking-changes-snapshots"},
        ],
    },
    {
        # The core save loop (stage one file, stage the folder) is Chapter 1;
        # precision staging (-A/-u/-p) overrides into Chapter 2's "shaping" work.
        "module": "creating-inspecting-repositories",
        "slug": "git-add",
        "base_command": "git add",
        "title": "git add",
        "summary": "Copy selected working directory changes into the staging area.",
        "usages": [
            {"slug": "file", "usage_form": "git add <file>", "label": "Stage one file"},
            {"slug": "dot", "usage_form": "git add .", "label": "Stage visible changes below the current folder"},
            {"slug": "all", "usage_form": "git add -A", "label": "Stage all changes", "module": "tracking-changes-snapshots"},
            {"slug": "update", "usage_form": "git add -u", "label": "Stage tracked modifications and deletions", "module": "tracking-changes-snapshots"},
            {"slug": "patch", "usage_form": "git add -p", "label": "Stage selected hunks", "module": "tracking-changes-snapshots"},
        ],
    },
    {
        # Saving the snapshot (commit -m) is Chapter 1; rewriting the last commit
        # (amend) overrides into Chapter 2.
        "module": "creating-inspecting-repositories",
        "slug": "git-commit",
        "base_command": "git commit",
        "title": "git commit",
        "summary": "Create or replace a commit from the staged snapshot.",
        "usages": [
            {"slug": "message", "usage_form": "git commit -m <message>", "label": "Commit with a message"},
            {"slug": "all-message", "usage_form": "git commit -a -m <message>", "label": "Commit tracked changes directly", "module": "tracking-changes-snapshots"},
            {"slug": "amend", "usage_form": "git commit --amend", "label": "Replace the latest local commit", "module": "tracking-changes-snapshots"},
            {"slug": "no-edit", "usage_form": "git commit --amend --no-edit", "label": "Amend without changing the message", "module": "tracking-changes-snapshots"},
        ],
    },
    {
        "module": "tracking-changes-snapshots",
        "slug": "git-rm",
        "base_command": "git rm",
        "title": "git rm",
        "summary": "Remove tracked paths from the index, optionally preserving the local file.",
        "usages": [
            {"slug": "tracked-file", "usage_form": "git rm <file>", "label": "Remove a tracked file"},
            {"slug": "cached", "usage_form": "git rm --cached <file>", "label": "Stop tracking but keep local file"},
            {"slug": "recursive-cached", "usage_form": "git rm -r --cached <directory>", "label": "Stop tracking a directory recursively"},
        ],
    },
    {
        "module": "creating-inspecting-repositories",
        "slug": "git-check-ignore",
        "base_command": "git check-ignore",
        "title": "git check-ignore",
        "summary": "Explain which ignore rule matches a path.",
        "usages": [
            {"slug": "verbose", "usage_form": "git check-ignore -v <path>", "label": "Explain an ignored path"},
        ],
    },
    {
        "module": "tracking-changes-snapshots",
        "slug": "gitignore",
        "base_command": ".gitignore",
        "mastery_trackable": False,
        "title": ".gitignore",
        "summary": "Author ignore rules so generated, local, or secret files stay out of normal staging flow.",
        "usages": [
            {"slug": "rule-file", "usage_form": ".gitignore", "label": "Write ignore rules"},
        ],
    },
    {
        "module": "tracking-changes-snapshots",
        "slug": "git-restore",
        "base_command": "git restore",
        "title": "git restore",
        "summary": "Discard working-tree changes or move staged changes back to the working directory.",
        "usages": [
            {"slug": "working-file", "usage_form": "git restore <file>", "label": "Discard a working-tree change"},
            {"slug": "staged-file", "usage_form": "git restore --staged <file>", "label": "Unstage a file"},
        ],
    },
    {
        "module": "branching-switching",
        "slug": "git-branch",
        "base_command": "git branch",
        "title": "git branch",
        "summary": "Inspect, create, and delete branch pointers while keeping HEAD where it is.",
        "usages": [
            {"slug": "list", "usage_form": "git branch", "label": "List local branches"},
            {"slug": "create", "usage_form": "git branch <name>", "label": "Create a branch pointer"},
            {"slug": "create-at-start", "usage_form": "git branch <name> <start-point>", "label": "Create a branch at a start point"},
            {"slug": "verbose", "usage_form": "git branch -v", "label": "List branches with tip commits"},
            {"slug": "delete", "usage_form": "git branch -d <name>", "label": "Delete a merged branch pointer"},
            {"slug": "delete-force", "usage_form": "git branch -D <name>", "label": "Force-delete an unmerged branch pointer"},
        ],
    },
    {
        "module": "branching-switching",
        "slug": "git-switch",
        "base_command": "git switch",
        "title": "git switch",
        "summary": "Move HEAD to another branch, or create and switch in one safe step.",
        "usages": [
            {"slug": "existing", "usage_form": "git switch <branch>", "label": "Switch to an existing branch"},
            {"slug": "create", "usage_form": "git switch -c <branch>", "label": "Create and switch"},
            {"slug": "detach", "usage_form": "git switch --detach <commit>", "label": "Inspect a commit detached"},
        ],
    },
    {
        "module": "branching-switching",
        "slug": "git-checkout",
        "base_command": "git checkout",
        "title": "git checkout",
        "summary": "Use checkout for legacy branch creation.",
        "usages": [
            {"slug": "legacy-create", "usage_form": "git checkout -b <branch>", "label": "Legacy create-and-switch spelling"},
        ],
    },
    {
        "module": "merging-conflicts",
        "slug": "git-merge",
        "base_command": "git merge",
        "title": "git merge",
        "summary": "Combine another branch into the current branch, or manage an in-progress merge.",
        "usages": [
            {"slug": "branch", "usage_form": "git merge <branch>", "label": "Merge a branch"},
            {"slug": "no-ff", "usage_form": "git merge --no-ff <branch>", "label": "Force a merge commit"},
            {"slug": "squash", "usage_form": "git merge --squash <branch>", "label": "Stage another branch as one snapshot"},
            {"slug": "abort", "usage_form": "git merge --abort", "label": "Abort a conflicted merge"},
            {"slug": "continue", "usage_form": "git merge --continue", "label": "Continue after resolved conflicts"},
        ],
    },
    {
        "module": "merging-conflicts",
        "slug": "git-merge-base",
        "base_command": "git merge-base",
        "title": "git merge-base",
        "summary": "Find the best common ancestor between commits or branches.",
        "usages": [
            {"slug": "two-refs", "usage_form": "git merge-base <ref-a> <ref-b>", "label": "Find a common ancestor"},
        ],
    },
    {
        "module": "merging-conflicts",
        "slug": "git-checkout-conflict",
        "base_command": "git checkout",
        "title": "git checkout conflict sides",
        "summary": "Choose one side of a conflicted file during merge resolution.",
        "usages": [
            {"slug": "ours", "usage_form": "git checkout --ours <file>", "label": "Take our conflict side"},
            {"slug": "theirs", "usage_form": "git checkout --theirs <file>", "label": "Take their conflict side"},
        ],
    },
    {
        "module": "merging-conflicts",
        "slug": "git-diff-conflict",
        "base_command": "git diff",
        "title": "git diff conflict sides",
        "summary": "Compare conflict stages while resolving a merge.",
        "usages": [
            {"slug": "ours", "usage_form": "git diff --ours <file>", "label": "Compare our conflict side"},
            {"slug": "theirs", "usage_form": "git diff --theirs <file>", "label": "Compare their conflict side"},
            {"slug": "base", "usage_form": "git diff --base <file>", "label": "Compare the base conflict stage"},
        ],
    },
    {
        "module": "merging-conflicts",
        "slug": "git-ls-files",
        "base_command": "git ls-files",
        "title": "git ls-files",
        "summary": "Inspect index entries, including unmerged conflict stages.",
        "usages": [
            {"slug": "unmerged", "usage_form": "git ls-files -u", "label": "List unmerged index entries"},
        ],
    },
    {
        "module": "merging-conflicts",
        "slug": "git-mergetool",
        "base_command": "git mergetool",
        "title": "git mergetool",
        "summary": "Launch a configured merge tool for conflicted files.",
        "usages": [
            {"slug": "launch", "usage_form": "git mergetool", "label": "Launch the merge tool"},
        ],
    },
    {
        "module": "undoing-recovery",
        "slug": "git-reset",
        "base_command": "git reset",
        "title": "git reset",
        "summary": "Move the current branch and reset index or working tree to the target commit.",
        "usages": [
            {"slug": "hard", "usage_form": "git reset --hard <commit>", "label": "Move branch and reset files"},
            {"slug": "hard-head", "usage_form": "git reset --hard HEAD~1", "label": "Move back by parent distance"},
        ],
    },
    {
        "module": "undoing-recovery",
        "slug": "git-revert",
        "base_command": "git revert",
        "title": "git revert",
        "summary": "Create a new commit that reverses an older commit without deleting shared history.",
        "usages": [
            {"slug": "one-commit", "usage_form": "git revert <commit>", "label": "Revert one commit"},
            {"slug": "no-edit", "usage_form": "git revert --no-edit <commit>", "label": "Revert with generated message"},
        ],
    },
    {
        "module": "undoing-recovery",
        "slug": "git-reflog",
        "base_command": "git reflog",
        "title": "git reflog",
        "summary": "Inspect recent HEAD movements for recovery clues.",
        "usages": [
            {"slug": "head", "usage_form": "git reflog", "label": "Inspect HEAD movements"},
        ],
    },
    {
        "module": "temporary-work-patches",
        "slug": "git-stash",
        "base_command": "git stash",
        "title": "git stash",
        "summary": "Temporarily shelve local work and restore it later.",
        "usages": [
            {"slug": "push", "usage_form": "git stash", "label": "Shelve local work"},
            {"slug": "list", "usage_form": "git stash list", "label": "List saved stashes"},
            {"slug": "pop", "usage_form": "git stash pop", "label": "Restore and remove the top stash"},
            {"slug": "apply", "usage_form": "git stash apply", "label": "Restore while keeping the stash"},
            {"slug": "drop", "usage_form": "git stash drop", "label": "Delete the top stash"},
        ],
    },
    {
        "module": "temporary-work-patches",
        "slug": "git-cherry-pick",
        "base_command": "git cherry-pick",
        "title": "git cherry-pick",
        "summary": "Apply one existing commit onto the current branch.",
        "usages": [
            {"slug": "one-commit", "usage_form": "git cherry-pick <commit>", "label": "Apply one commit"},
            {"slug": "no-commit", "usage_form": "git cherry-pick --no-commit <commit>", "label": "Stage picked changes without committing"},
            {"slug": "abort", "usage_form": "git cherry-pick --abort", "label": "Abort an in-progress cherry-pick"},
        ],
    },
    {
        "module": "remotes-collaboration",
        "slug": "git-remote",
        "base_command": "git remote",
        "title": "git remote",
        "summary": "Inspect configured remotes and their URLs.",
        "usages": [
            {"slug": "list", "usage_form": "git remote", "label": "List remote names"},
            {"slug": "verbose", "usage_form": "git remote -v", "label": "List remote URLs"},
        ],
    },
    {
        "module": "remotes-collaboration",
        "slug": "git-fetch",
        "base_command": "git fetch",
        "title": "git fetch",
        "summary": "Update remote-tracking branches without changing local work.",
        "usages": [
            {"slug": "origin", "usage_form": "git fetch origin", "label": "Fetch a remote"},
            {"slug": "prune", "usage_form": "git fetch --prune", "label": "Prune stale tracking refs"},
        ],
    },
    {
        "module": "remotes-collaboration",
        "slug": "git-pull",
        "base_command": "git pull",
        "title": "git pull",
        "summary": "Fetch and integrate upstream changes into the current branch.",
        "usages": [
            {"slug": "default", "usage_form": "git pull", "label": "Pull the configured upstream"},
            {"slug": "rebase", "usage_form": "git pull --rebase", "label": "Pull with rebase"},
        ],
    },
    {
        "module": "remotes-collaboration",
        "slug": "git-push",
        "base_command": "git push",
        "title": "git push",
        "summary": "Publish local commits, set upstream tracking, force with lease, or delete remote branches.",
        "usages": [
            {"slug": "upstream", "usage_form": "git push -u origin <branch>", "label": "Push and set upstream"},
            {"slug": "current", "usage_form": "git push", "label": "Push the current branch"},
            {"slug": "force-with-lease", "usage_form": "git push --force-with-lease", "label": "Force safely after rewriting local history"},
            {"slug": "delete", "usage_form": "git push origin --delete <branch>", "label": "Delete a remote branch"},
        ],
    },
]

# Advanced and expert content is additive. Existing Arcane Spire command forms
# keep their original chapter ownership and slugs.
from curriculum.seed_data.advanced_command_catalog import (  # noqa: E402
    COMMAND_FORM_EXTENSIONS,
    NEW_COMMAND_SKILLS,
)

_by_slug = {skill["slug"]: skill for skill in COMMAND_CATALOG}
_missing_base_commands = {
    "git-tag": "git tag",
    "git-rev-list": "git rev-list",
}
for _skill_slug, _forms in COMMAND_FORM_EXTENSIONS.items():
    _skill = _by_slug.get(_skill_slug)
    if _skill is None:
        _base = _missing_base_commands[_skill_slug]
        _skill = {
            "module": _forms[0]["module"],
            "slug": _skill_slug,
            "base_command": _base,
            "title": _base,
            "summary": f"Advanced forms of {_base}.",
            "usages": [],
        }
        COMMAND_CATALOG.append(_skill)
        _by_slug[_skill_slug] = _skill
    _skill["usages"].extend(_forms)
COMMAND_CATALOG.extend(NEW_COMMAND_SKILLS)
