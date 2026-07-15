"""Authored command-library source data.

The assembly helpers stay in :mod:`curriculum.library`; this module contains the
large hand-authored dictionaries so the runtime library module remains readable.
"""
from __future__ import annotations

from collections.abc import Callable
from typing import Any

DiagramFactory = Callable[..., dict[str, Any]]


def authored_library_entries(diagram_factory: DiagramFactory) -> list[dict[str, Any]]:
    """Return the hand-authored command library entries.

    The diagram factory is injected to keep this data module free of rendering or
    block-construction logic while preserving the exact existing payload shape.
    """
    return [
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
        # Free-form tags (diagnostic/action/); surfaced to the book payload.
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
        # -- Sub-navigation: options & arguments ------------------------------
        # Each option/argument becomes its own page AND a sub-nav item in the
        # Chapter Book (e.g. git init -> -q / --quiet, -b / --initial-branch).
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
        # -- Authored diagram (optional) --------------------------------------
        # Rendered as neon SVG in the book. kind="flow" | "dag".
        "diagram": diagram_factory(
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
]


SEMANTIC_SECTION_COPY: dict[str, dict[str, str]] = {
    "option-s-short": {
        "token": "-s / --short",
        "title": "Short status",
        "body": "Shows status in compact two-column form. Use it when the scenario wants quick path categories rather than full prose.",
    },
    "option-porcelain": {
        "token": "--porcelain",
        "title": "Script-stable status",
        "body": "Prints status in a stable format designed for tools and careful parsing.",
    },
    "option-sb": {
        "token": "-sb",
        "title": "Short status with branch",
        "body": "Adds branch and upstream information to compact status output.",
    },
    "option-ignored": {
        "token": "--ignored",
        "title": "Include ignored paths",
        "body": "Lists ignored files so you can prove an ignore rule is hiding the intended path.",
    },
    "option-oneline": {
        "token": "--oneline",
        "title": "Compact commits",
        "body": "Shows each commit on one line, useful when the graph shape matters more than full patch detail.",
    },
    "option-graph": {
        "token": "--graph",
        "title": "Graph history",
        "body": "Draws branch and merge shape in the log output so divergence is visible.",
    },
    "option-all": {
        "token": "--all",
        "title": "All refs",
        "body": "Includes every local and remote-tracking ref instead of only the current branch history.",
    },
    "option-count": {
        "token": "-n / --max-count",
        "title": "Limit output",
        "body": "Limits history output to the requested number of commits.",
    },
    "option-staged-cached": {
        "token": "--staged / --cached",
        "title": "Compare staged content",
        "body": "Compares the index to HEAD so you can inspect the snapshot that would be committed.",
    },
    "option-head": {
        "token": "HEAD",
        "title": "Compare against HEAD",
        "body": "Uses the current commit as the comparison point for working and staged changes.",
    },
    "option-name-only": {
        "token": "--name-only",
        "title": "Path list only",
        "body": "Shows changed path names without the full patch.",
    },
    "option-conflict-sides": {
        "token": "--ours / --theirs / --base",
        "title": "Conflict stages",
        "body": "Reads the current branch side, incoming side, or common ancestor side of a conflicted path.",
    },
    "option-v": {
        "token": "-v",
        "title": "Verbose detail",
        "body": "Adds the extra detail this command can reveal, such as matching ignore rules or branch tip commits.",
    },
    "option-a-all": {
        "token": "-a / --all",
        "title": "All tracked paths",
        "body": "Broadens the command to all tracked changes. Use it only when every tracked update belongs in the scenario.",
    },
    "option-d-delete": {
        "token": "-d / -D",
        "title": "Delete branch",
        "body": "Deletes a branch name. The force form removes the pointer even when Git would normally protect it.",
    },
    "option-c-create": {
        "token": "-c / --create",
        "title": "Create while switching",
        "body": "Creates a new branch and moves HEAD there in one command.",
    },
    "option-detach": {
        "token": "--detach",
        "title": "Detach HEAD",
        "body": "Moves HEAD directly to a commit for inspection without attaching it to a branch name.",
    },
    "option-b-create": {
        "token": "-b",
        "title": "Legacy create branch",
        "body": "Creates a branch while using the older checkout command spelling.",
    },
    "option-pop": {
        "token": "pop",
        "title": "Restore and remove stash",
        "body": "Applies the top stash and drops it when the restore succeeds.",
    },
    "option-apply": {
        "token": "apply",
        "title": "Restore and keep stash",
        "body": "Applies stash contents while leaving the stash entry available.",
    },
    "option-drop": {
        "token": "drop",
        "title": "Delete stash entry",
        "body": "Removes a stash entry without applying it.",
    },
    "option-list": {
        "token": "list",
        "title": "List stashes",
        "body": "Shows saved stash entries before choosing one to restore or drop.",
    },
    "option-u-upstream": {
        "token": "-u / --set-upstream",
        "title": "Set upstream",
        "body": "Publishes the branch and records the remote branch future push and pull should use.",
    },
    "option-force-with-lease": {
        "token": "--force-with-lease",
        "title": "Protected force push",
        "body": "Updates a remote ref only if it still points where your local repository last saw it.",
    },
    "option-delete": {
        "token": "--delete",
        "title": "Delete remote branch",
        "body": "Removes a branch name from the remote repository.",
    },
    "option-rebase": {
        "token": "--rebase",
        "title": "Pull with rebase",
        "body": "Fetches upstream work and replays local commits on top instead of creating a merge commit.",
    },
    "option-squash": {
        "token": "--squash",
        "title": "Squash merge",
        "body": "Stages the combined changes from another branch without creating a merge commit yet.",
    },
    "option-v-verbose": {
        "token": "-v",
        "title": "Show remote URLs",
        "body": "Lists each remote with its fetch and push URLs.",
    },
    "option-b-initial-branch": {
        "token": "-b / --initial-branch",
        "title": "Initial branch name",
        "body": "Names the first branch in a newly initialized repository.",
    },
    "option-q-quiet": {
        "token": "-q / --quiet",
        "title": "Quiet output",
        "body": "Suppresses routine success output. Verify by inspecting state afterward.",
    },
    "option-b-branch": {
        "token": "-b / --branch",
        "title": "Clone a branch",
        "body": "Checks out the named remote branch after cloning.",
    },
    "option-depth": {
        "token": "--depth",
        "title": "Shallow history",
        "body": "Copies only the requested amount of recent history from the remote.",
    },
    "option-u-update": {
        "token": "-u / --update",
        "title": "Tracked updates only",
        "body": "Stages tracked modifications and deletions while leaving untracked files alone.",
    },
    "option-p-patch": {
        "token": "-p / --patch",
        "title": "Patch selection",
        "body": "Lets you choose individual hunks instead of staging an entire file.",
    },
    "option-cached": {
        "token": "--cached",
        "title": "Index only",
        "body": "Removes a path from Git's index while keeping the local file or directory.",
    },
    "option-m-message": {
        "token": "-m / --message",
        "title": "Commit message",
        "body": "Supplies the commit message directly in the command.",
    },
    "option-amend": {
        "token": "--amend",
        "title": "Replace latest commit",
        "body": "Replaces the current branch tip with a new commit built from the staged snapshot.",
    },
    "option-no-edit": {
        "token": "--no-edit",
        "title": "Keep generated message",
        "body": "Reuses the existing message for an amend or the generated message for a revert.",
    },
    "option-staged": {
        "token": "--staged",
        "title": "Operate on the index",
        "body": "Targets staged content instead of the working-tree file.",
    },
    "option-abort": {
        "token": "--abort",
        "title": "Abort operation",
        "body": "Backs out an in-progress merge or cherry-pick and returns to the pre-operation state.",
    },
    "option-continue": {
        "token": "--continue",
        "title": "Continue operation",
        "body": "Completes an operation after conflicts have been resolved and staged.",
    },
    "option-ours": {
        "token": "--ours",
        "title": "Current branch side",
        "body": "Chooses or inspects the current branch version of a conflicted path.",
    },
    "option-theirs": {
        "token": "--theirs",
        "title": "Incoming side",
        "body": "Chooses or inspects the incoming branch version of a conflicted path.",
    },
    "option-tool": {
        "token": "--tool",
        "title": "Choose merge tool",
        "body": "Selects which configured merge tool to launch.",
    },
    "option-global": {
        "token": "--global",
        "title": "Global config scope",
        "body": "Writes or reads the user-wide Git configuration instead of only the current repository.",
    },
    "option-prune": {
        "token": "--prune",
        "title": "Prune stale refs",
        "body": "Removes remote-tracking branches that no longer exist on the remote.",
    },
    "option-no-commit": {
        "token": "--no-commit",
        "title": "Stage without committing",
        "body": "Applies the patch from another commit to the index and working tree without creating a commit.",
    },
    "option-unmerged": {
        "token": "-u / --unmerged",
        "title": "Unmerged index entries",
        "body": "Shows the index stages for paths currently involved in a merge conflict.",
    },
    "argument-path": {
        "token": "<path>",
        "title": "Path argument",
        "body": "Limits the command to the exact file or directory named by the scenario.",
    },
    "argument-commit": {
        "token": "<commit>",
        "title": "Commit argument",
        "body": "Names the commit object the command should inspect, revert, reset to, or copy from.",
    },
    "argument-branch": {
        "token": "<branch>",
        "title": "Branch argument",
        "body": "Names the branch pointer or remote branch involved in the action.",
    },
    "argument-start-point": {
        "token": "<start-point>",
        "title": "Start point",
        "body": "Chooses the commit where a new branch should begin.",
    },
    "argument-remote": {
        "token": "<remote>",
        "title": "Remote argument",
        "body": "Names the configured remote, such as origin.",
    },
    "argument-directory": {
        "token": "<directory>",
        "title": "Directory argument",
        "body": "Names the folder the command should create, initialize, or target.",
    },
    "argument-url": {
        "token": "<url>",
        "title": "Remote URL",
        "body": "Names the source repository to clone from.",
    },
    "argument-number": {
        "token": "<number>",
        "title": "Numeric value",
        "body": "Provides the requested count, such as clone depth or log length.",
    },
    "argument-key": {
        "token": "<key>",
        "title": "Configuration key",
        "body": "Names the Git configuration setting being read or written.",
    },
    "argument-value": {
        "token": "<value>",
        "title": "Configuration value",
        "body": "Provides the value stored for a Git configuration key.",
    },
}


COMMAND_EFFECTS: dict[str, tuple[list[str], list[str], str, list[str]]] = {
    "git clone": (
        ["Creates a local repository from a remote fixture and records origin metadata."],
        ["It does not edit the remote repository or create new commits."],
        "Cloning the wrong branch, depth, or destination folder.",
        ["Confirm the requested URL, branch, depth, and destination folder before cloning."],
    ),
    "git status": (
        ["Reports branch, index, working-tree, untracked, ignored, or conflict state."],
        ["It does not change files, staging, commits, branches, or remotes."],
        "Treating a diagnostic command as if it fixed the repository state.",
        ["Read the branch line and every path category before deciding the next action."],
    ),
    "git config": (
        ["Reads or writes Git configuration such as user identity or merge-tool preferences."],
        ["It does not stage files, create commits, or repair repository history."],
        "Setting a global value when the scenario only asked you to inspect configuration.",
        ["Check whether the scenario asks for global configuration, local configuration, or inspection only."],
    ),
    "git log": (
        ["Shows commit history and graph shape for the selected refs."],
        ["It does not move HEAD or branch pointers."],
        "Reading only the current branch when the scenario needs all refs.",
        ["Choose the history view that exposes the commits or branches named in the scenario."],
    ),
    "git show": (
        ["Shows details for HEAD or a named commit/object."],
        ["It does not check out or apply the inspected commit."],
        "Inspecting the wrong commit because the ref was not read from the scenario.",
        ["Identify the exact commit or ref you need before showing it."],
    ),
    "git diff": (
        ["Compares working, staged, committed, or conflict-stage content."],
        ["It does not stage, discard, or resolve the compared changes."],
        "Comparing the wrong side of the index or conflict.",
        ["Decide whether you need working, staged, HEAD, ours, theirs, or base before running the diff."],
    ),
    "git add": (
        ["Copies selected working-tree content into the index for the next commit."],
        ["It does not create a commit or publish work."],
        "Staging broad paths when only one file or hunk belongs in the snapshot.",
        ["Inspect status or diff so the index receives exactly the intended content."],
    ),
    "git commit": (
        ["Creates or replaces a local commit from the staged snapshot."],
        ["It does not automatically include unstaged or untracked files unless the chosen syntax says so."],
        "Committing before checking what is staged.",
        ["Inspect the staged diff and choose a message that matches the scenario."],
    ),
    "git rm": (
        ["Stages tracked paths for removal, or removes them only from the index when cached."],
        ["The cached form keeps the local file or directory on disk."],
        "Deleting local files when the task only asked Git to stop tracking them.",
        ["Check whether the file should disappear locally or only from the next commit."],
    ),
    "git check-ignore": (
        ["Explains which ignore rule matches a path."],
        ["It does not add, remove, or edit ignore rules."],
        "Assuming ignored means previously tracked files are no longer tracked.",
        ["Use it after status suggests a generated path is hidden."],
    ),
    ".gitignore": (
        ["Defines ignore patterns for untracked generated, local, or secret files."],
        ["It does not automatically untrack files that are already committed."],
        "Writing a broad ignore rule or expecting it to remove already tracked files.",
        ["Check whether the path is untracked, and verify the rule with status or git check-ignore."],
    ),
    "git restore": (
        ["Restores working-tree files or unstages content depending on flags."],
        ["It does not create an undo commit."],
        "Discarding work that should only have been unstaged.",
        ["Confirm whether the scenario wants to change the working tree, the index, or both."],
    ),
    "git branch": (
        ["Lists, creates, or deletes branch pointers."],
        ["It does not switch HEAD unless another command does that."],
        "Creating a branch but forgetting you are still on the old branch.",
        ["Read HEAD and the requested branch name before changing branch pointers."],
    ),
    "git switch": (
        ["Moves HEAD to another branch, optionally creating the branch first."],
        ["It does not merge histories or publish the branch."],
        "Switching while local changes would be carried into the wrong task.",
        ["Inspect status before moving to another branch."],
    ),
    "git checkout": (
        ["Creates and switches branches in legacy form, or selects a conflict side during resolution."],
        ["It does not replace modern switch/restore for everyday branch and file work in this track."],
        "Using checkout's broad behavior when the focused modern command would be clearer.",
        ["Use checkout only when the scenario specifically asks for its branch-creation or conflict-side form."],
    ),
    "git merge": (
        ["Integrates another branch, manages a conflicted merge, or stages a squash merge."],
        ["It does not publish the result to a remote by itself."],
        "Merging from the wrong current branch.",
        ["Confirm your current branch and the incoming branch before merging."],
    ),
    "git merge-base": (
        ["Prints the best common ancestor between refs."],
        ["It does not merge, switch, or edit commits."],
        "Confusing the ancestor commit with the merge result.",
        ["Identify the two refs whose divergence point matters."],
    ),
    "git ls-files": (
        ["Lists index entries, including unmerged conflict stages."],
        ["It does not resolve conflicts or edit files."],
        "Reading unmerged entries but forgetting a separate resolution step is still required.",
        ["Use it when the conflict state is unclear from status alone."],
    ),
    "git mergetool": (
        ["Launches a configured merge tool for conflicted files."],
        ["It does not guarantee the conflict is resolved until the result is saved and staged."],
        "Opening a tool before understanding which paths are conflicted.",
        ["Inspect unmerged paths and configured tool expectations first."],
    ),
    "git reset": (
        ["Moves the current branch and can reset index and working tree to a target commit."],
        ["It should not be used casually on shared history."],
        "Using hard reset when a shared-history revert would be safer.",
        ["Confirm the target commit and whether local changes should be discarded."],
    ),
    "git revert": (
        ["Creates a new commit that undoes an earlier commit."],
        ["It does not delete the original commit from history."],
        "Using reset to fix shared history when revert is the safer operation.",
        ["Identify the exact bad commit and whether history is already shared."],
    ),
    "git reflog": (
        ["Shows recent HEAD movements for recovery."],
        ["It does not recover anything until another command uses the discovered commit."],
        "Waiting until entries expire instead of acting once the lost commit is found.",
        ["Use it after a reset, amend, or detached-HEAD move made a commit hard to find."],
    ),
    "git stash": (
        ["Shelves local changes and can list, restore, or drop stash entries."],
        ["It is not permanent project history."],
        "Treating a stash as a substitute for a commit that must be preserved.",
        ["Check status and choose apply or pop based on whether the stash should remain."],
    ),
    "git cherry-pick": (
        ["Copies the patch from an existing commit onto the current branch."],
        ["It does not move the source branch."],
        "Picking from the wrong commit or forgetting conflicts are possible.",
        ["Confirm the current branch and source commit before applying the patch."],
    ),
    "git remote": (
        ["Lists configured remotes and their fetch/push URLs."],
        ["It does not contact the remote or update tracking refs."],
        "Assuming a remote name proves the local branch is up to date.",
        ["Inspect remote names before fetch, pull, or push decisions."],
    ),
    "git fetch": (
        ["Updates remote-tracking refs from a remote."],
        ["It does not merge or rebase into the current branch."],
        "Expecting local files to change after fetch alone.",
        ["Know which remote should be refreshed and whether stale refs should be pruned."],
    ),
    "git pull": (
        ["Fetches upstream work and integrates it into the current branch."],
        ["It does not publish local commits."],
        "Pulling before checking whether the branch has the intended upstream.",
        ["Inspect branch and upstream state before pulling."],
    ),
    "git push": (
        ["Publishes local commits, sets upstreams, force-updates with lease, or deletes remote branches."],
        ["It does not pull missing remote work first."],
        "Pushing or force-pushing without checking the remote branch state.",
        ["Confirm remote, branch, upstream, and whether lease protection is required."],
    ),
}
