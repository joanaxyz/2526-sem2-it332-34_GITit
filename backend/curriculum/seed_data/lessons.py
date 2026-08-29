"""Authored chapter lessons that open in the Chapter Book.

A lesson is not a command. It teaches an idea (mental models, platform rules,
workflow philosophy) with the same section/block vocabulary the command
library uses, so the book reader renders both. Unlike adventures and
challenges, lessons are not a repeating per-chapter pattern - each one is
authored onto a specific chapter (the frozen ``"module"`` key = chapter slug).

Pages are built at import time through ``lesson_pages`` so the seed persists
ready-to-render pages, exactly like seeded command library entries.
"""

from __future__ import annotations

from curriculum.library import _bullets, _callout, _diagram, _paragraph, _warning, lesson_pages

LESSONS = [
    {
        "module": "creating-inspecting-repositories",
        "slug": "how-git-thinks",
        "title": "How Git Thinks",
        "summary": (
            "The four places your work lives - working directory, staging area, "
            "commit history, and HEAD - and how every Git command moves changes between them."
        ),
        "pages": lesson_pages(
            [
                {
                    "id": "overview",
                    "title": "The four places",
                    "type": "overview",
                    "content": [
                        _paragraph(
                            "Every Git command you will ever run moves information between four "
                            "places. Once you can name them, no command is mysterious - each one "
                            "is just an arrow between two of these places."
                        ),
                        _bullets(
                            "The places",
                            [
                                "Working directory - the files you actually edit.",
                                "Staging area - the snapshot you are assembling for the next commit.",
                                "Commit history - permanent snapshots, linked into a graph.",
                                "HEAD - the marker for where you are standing in that graph.",
                            ],
                        ),
                        _diagram(
                            kind="flow",
                            title="Where work flows",
                            caption="add moves edits into staging; commit seals staging into history; HEAD points at where you stand.",
                            nodes=[
                                {"id": "wd", "label": "Working directory", "accent": "muted"},
                                {"id": "staging", "label": "Staging area", "accent": "cyan"},
                                {"id": "history", "label": "Commit history", "accent": "cyan"},
                            ],
                            edges=[
                                {"from": "wd", "to": "staging", "label": "git add"},
                                {"from": "staging", "to": "history", "label": "git commit"},
                            ],
                        ),
                    ],
                },
                {
                    "id": "snapshots-not-diffs",
                    "title": "Snapshots, not saves",
                    "type": "concept",
                    "content": [
                        _paragraph(
                            "A commit is not a 'save' of one file - it is a snapshot of the whole "
                            "project at one moment, plus a link to the snapshot that came before it. "
                            "That chain of links is the commit graph you see in the repository diagrams."
                        ),
                        _callout(
                            "Why the graph matters",
                            "Branches and merges are nothing more than names pointing at commits in "
                            "this graph. When a scenario asks you to 'move a branch' or 'undo a "
                            "commit', you are really moving pointers and adding snapshots.",
                        ),
                        _warning(
                            "Editing a file changes only the working directory. Until you stage and "
                            "commit, Git's history does not know your change exists."
                        ),
                    ],
                },
                {
                    "id": "reading-before-acting",
                    "title": "Read the state before acting",
                    "type": "practice-notes",
                    "content": [
                        _paragraph(
                            "Every level starts the same way: look at the repository "
                            "diagram and status signals first, then decide which arrow you need. "
                            "The answer is always a repository state, never a memorized command string."
                        ),
                        _bullets(
                            "Before every command, ask",
                            [
                                "Where is the change I care about right now - working directory, staging, or history?",
                                "Where does it need to end up?",
                                "Which command moves work between exactly those two places?",
                            ],
                        ),
                    ],
                },
            ]
        ),
    },
]


def _simple_lesson(module: str, slug: str, title: str, summary: str, body: str) -> dict:
    return {
        "module": module,
        "slug": slug,
        "title": title,
        "summary": summary,
        "pages": lesson_pages(
            [
                {
                    "id": "overview",
                    "title": title,
                    "type": "concept",
                    "content": [_paragraph(body)],
                }
            ]
        ),
    }


LESSONS += [
    _simple_lesson(
        "creating-inspecting-repositories",
        "anatomy-of-a-git-command",
        "Anatomy of a Git Command",
        "How to read `git <verb> [options] [arguments]` without guessing.",
        "A Git command starts with `git`, then a verb such as `status`, `add`, or `commit`. Options change behavior; arguments name the thing the command acts on. Angle-bracket words in lessons are placeholders, not text to type literally.",
    ),
    _simple_lesson(
        "creating-inspecting-repositories",
        "what-a-repository-is",
        "What a Repository Is",
        "The hidden `.git` directory, tracked files, untracked files, and repository metadata.",
        "A repository is a working folder plus Git metadata. The working folder is where you edit files. The `.git` directory stores commits, refs, configuration, and the index that powers staging.",
    ),
    _simple_lesson(
        "creating-inspecting-repositories",
        "moving-into-your-project",
        "Moving Into Your Project",
        "Using `cd` to step into a repository before you run Git.",
        "Git always acts on the repository in your current folder. `cd <folder>` is a shell command - not a Git command - that moves you between folders. It sets the stage: after `git init <name>` or `git clone <url> <folder>` creates a project folder, you `cd` into it before running Git there. In these lessons `cd` is accepted and changes nothing on its own; it simply marks that you have stepped into the project so the Git commands that follow read naturally.",
    ),
    _simple_lesson(
        "creating-inspecting-repositories",
        "reading-a-commit-graph",
        "Reading a Commit Graph",
        "How commits, parents, branches, and HEAD fit together.",
        "A commit graph is a chain of snapshots. Each commit points to its parent commit. Branches are names pointing at commits, and HEAD tells you which branch or commit you are standing on.",
    ),
    _simple_lesson(
        "tracking-changes-snapshots",
        "staging-area-draft",
        "The Staging Area Is a Draft",
        "Why `git add` prepares a commit instead of saving one.",
        "The staging area is the draft of your next commit. You can add one file, all tracked updates, or selected hunks, then inspect that draft before `git commit` turns it into history.",
    ),
    _simple_lesson(
        "tracking-changes-snapshots",
        "good-commit-anatomy",
        "Anatomy of a Good Commit",
        "Atomic snapshots, readable messages, and clean history.",
        "A good commit answers one question: what changed and why does it belong together? Keep unrelated edits out, use a direct message, and prefer several focused commits over one tangled checkpoint.",
    ),
    _simple_lesson(
        "tracking-changes-snapshots",
        "ignore-rules",
        "Ignore Rules and What Not to Track",
        "How `.gitignore` keeps generated and secret files out of history.",
        "Ignore rules are for files Git should not offer to track, such as build outputs and local secrets. If a file is already tracked, ignoring it is not enough; remove it from the index with `git rm --cached`.",
    ),
    _simple_lesson(
        "branching-switching",
        "branches-are-labels",
        "Branches Are Labels",
        "A branch is a movable name pointing at a commit.",
        "Creating a branch does not copy the project. It creates a name that points at a commit. New commits move the current branch label forward.",
    ),
    _simple_lesson(
        "branching-switching",
        "detached-head",
        "HEAD and Detached HEAD",
        "What changes when HEAD points directly at a commit.",
        "When HEAD is attached, it points through a branch name. When detached, it points directly at a commit. Detached HEAD is useful for inspection, but new commits there need a branch if you want to keep them.",
    ),
    _simple_lesson(
        "branching-switching",
        "switch-vs-checkout",
        "Switch vs Checkout",
        "Why modern Git uses `switch` for branch movement.",
        "`git switch` is the focused branch-navigation command. `git checkout` is older and can do many jobs, which is why the curriculum teaches checkout only where its legacy or conflict-side forms still matter.",
    ),
    _simple_lesson(
        "merging-conflicts",
        "fast-forward-vs-merge-commit",
        "Fast-Forward vs Merge Commit",
        "Two ways a branch can integrate another branch.",
        "A fast-forward moves the current branch label to a descendant commit. A merge commit creates a new commit with two parents when histories diverged or when you ask Git to preserve the join.",
    ),
    _simple_lesson(
        "merging-conflicts",
        "anatomy-of-a-conflict",
        "Anatomy of a Conflict",
        "Conflict markers, ours, theirs, and base.",
        "A conflict means Git could not combine edits automatically. Ours is the current branch side, theirs is the incoming side, and base is the common ancestor version.",
    ),
    _simple_lesson(
        "merging-conflicts",
        "resolve-abort-or-side",
        "Resolve, Abort, or Take a Side",
        "The three safe decisions during a conflicted merge.",
        "When a merge conflicts, choose deliberately: edit and stage a resolved file, abort to return to the pre-merge state, or take one side when the other side should be discarded.",
    ),
    _simple_lesson(
        "undoing-recovery",
        "restore-reset-revert",
        "Restore vs Reset vs Revert",
        "Choose an undo command by what should happen to history.",
        "`restore` changes files, `reset` moves a branch and can rewrite local history, and `revert` adds a new commit that undoes an older commit without deleting shared history.",
    ),
    _simple_lesson(
        "undoing-recovery",
        "reflog-safety-net",
        "Reflog Is Your Safety Net",
        "How recent HEAD movements help recovery.",
        "The reflog records where HEAD has recently been. If a reset or amend made a commit hard to find, reflog can show the commit id so you can recover it.",
    ),
    _simple_lesson(
        "undoing-recovery",
        "rewriting-shared-history",
        "Rewriting Shared History Is Dangerous",
        "Why local cleanup and shared cleanup use different commands.",
        "Changing commits that only live on your machine can be useful. Changing commits other people have based work on creates confusion, so shared mistakes are usually fixed with revert.",
    ),
    _simple_lesson(
        "temporary-work-patches",
        "shelving-with-stash",
        "Shelving Work with Stash",
        "How stash stores work outside the commit graph.",
        "Stash is a temporary shelf for local changes. It is useful before switching tasks, but it is not a replacement for a commit you need to keep permanently.",
    ),
    _simple_lesson(
        "temporary-work-patches",
        "transplanting-commit",
        "Transplanting a Commit",
        "Why cherry-pick copies a patch instead of merging a branch.",
        "Cherry-pick reads the changes from one commit and applies them to your current branch as a new commit. The source branch does not move.",
    ),
    _simple_lesson(
        "temporary-work-patches",
        "pop-vs-apply",
        "Pop vs Apply",
        "Restore a stash while deciding whether to keep the stash entry.",
        "`git stash apply` restores the saved changes and keeps the stash. `git stash pop` restores the changes and removes that stash entry when it succeeds.",
    ),
    _simple_lesson(
        "remotes-collaboration",
        "remotes-tracking-upstream",
        "Remotes, Tracking Branches, and Upstream",
        "How local branches relate to remote-tracking refs.",
        "A remote is a named connection to another repository. Remote-tracking branches such as `origin/main` are your last fetched view of that remote. Upstream config tells pull and push which remote branch a local branch follows.",
    ),
    _simple_lesson(
        "remotes-collaboration",
        "fetch-vs-pull",
        "Fetch vs Pull",
        "Update your view of the remote separately from integrating it.",
        "`git fetch` updates remote-tracking refs without moving your local branch. `git pull` fetches and then integrates upstream into the current branch.",
    ),
    _simple_lesson(
        "remotes-collaboration",
        "everyday-collaboration-loop",
        "The Everyday Collaboration Loop",
        "Inspect, fetch, integrate, work, and publish.",
        "A reliable collaboration loop is: inspect current state, fetch remote refs, integrate upstream when needed, make focused commits, then push the branch you intend to share.",
    ),
    _simple_lesson(
        "remotes-collaboration",
        "force-with-lease",
        "Force with Lease vs Force",
        "Why lease protection matters after rewriting local history.",
        "`--force-with-lease` refuses to overwrite remote work you have not seen. It is the safer force option when you intentionally rewrote local history and need to update a remote branch.",
    ),
]

from curriculum.seed_data.advanced_lessons import ADVANCED_LESSONS  # noqa: E402

LESSONS.extend(ADVANCED_LESSONS)
