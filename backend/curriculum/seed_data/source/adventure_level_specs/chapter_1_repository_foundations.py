"""Chapter 1 authored adventure levels."""

from __future__ import annotations

from .common import *  # noqa: F403

LEVELS = [
    # Chapter 1 - Repository Foundations
    q(
        "git-init/current-directory",
        "init-current-folder",
        "Onboard an existing project folder",
        "A capstone folder already has starter files, but it has no repository metadata yet.",
        "Turn the current folder into a repository, then save its files as the first commit.",
        [
            v(
                "init-current-capstone",
                "Capstone folder",
                uninitialized({"README.md": "Capstone notes", "src/app.py": "print('hi')\n"}),
                ["git init", "git add .", "git commit -m 'Initial commit'"],
                ev(
                    {
                        "repository_initialized": True,
                        "latest_commit": {
                            "branch": "main",
                            "contains_paths": ["README.md", "src/app.py"],
                            "message_contains": ["Initial commit"],
                        },
                        "working_tree_clean": True,
                    },
                    required=["git init", "git commit"],
                ),
            ),
            v(
                "init-current-docs",
                "Docs folder",
                uninitialized({"README.md": "Docs", "guide.md": "Draft"}),
                ["git init", "git add .", "git commit -m 'Initial commit'"],
                ev(
                    {
                        "repository_initialized": True,
                        "latest_commit": {
                            "branch": "main",
                            "contains_paths": ["README.md", "guide.md"],
                            "message_contains": ["Initial commit"],
                        },
                        "working_tree_clean": True,
                    },
                    required=["git init", "git commit"],
                ),
            ),
        ],
        checks=[
            {
                "label": "The folder is now a Git repository.",
                "requirement": {"repository_initialized": True},
            },
            {
                "label": "Your files are saved in the first commit.",
                "requirement": {"min_commits_on_branch": {"main": 1}},
            },
            {
                "label": "Nothing is left uncommitted.",
                "requirement": {"working_tree_clean": True},
            },
        ],
        workflow=True,
    ),
    q(
        "git-init/named-directory",
        "init-named-folder",
        "Initialize a new named folder",
        "A new exercise needs its own repository instead of reusing the current workspace.",
        "Create repository metadata for the requested folder name.",
        [
            v(
                "init-named-invoice",
                "Invoice project",
                uninitialized({}),
                ["git init invoice-tracker"],
                ev(
                    {
                        "repository_initialized": True,
                        "rules": [meta_equals("last_init_directory", "invoice-tracker")],
                    },
                    required=["git init"],
                ),
                details=[{"label": "Folder name", "value": "invoice-tracker"}],
            ),
            v(
                "init-named-qa",
                "QA results",
                uninitialized({}),
                ["git init qa-results"],
                ev(
                    {
                        "repository_initialized": True,
                        "rules": [meta_equals("last_init_directory", "qa-results")],
                    },
                    required=["git init"],
                ),
                details=[{"label": "Folder name", "value": "qa-results"}],
            ),
        ],
        checks=[
            {
                "label": "A named repository folder was created.",
                "requirement": {
                    "rules": [
                        {
                            "type": "operation_metadata_not_equals",
                            "key": "last_init_directory",
                            "value": None,
                        }
                    ]
                },
            }
        ],
        prerequisites=["init-current-folder"],
        workflow=True,
    ),
    q(
        "git-init/initial-branch",
        "init-with-initial-branch",
        "Start on a required first branch",
        "A team standard requires the first branch to use a specific name from the beginning.",
        "Initialize the folder with the requested first branch name, then save the first commit.",
        [
            v(
                "init-branch-trunk",
                "Trunk standard",
                uninitialized({"README.md": "Portal"}),
                ["git init -b trunk", "git add .", "git commit -m 'Initial commit'"],
                ev(
                    {
                        "repository_initialized": True,
                        "head_branch": "trunk",
                        "latest_commit": {
                            "branch": "trunk",
                            "contains_paths": ["README.md"],
                            "message_contains": ["Initial commit"],
                        },
                        "working_tree_clean": True,
                        "rules": [meta_equals("last_init_initial_branch", "trunk")],
                    },
                    required=["git init", "git commit"],
                ),
                details=[{"label": "First branch name", "value": "trunk"}],
            ),
            v(
                "init-branch-mainline",
                "Mainline standard",
                uninitialized({"README.md": "SDK"}),
                ["git init --initial-branch mainline", "git add .", "git commit -m 'Initial commit'"],
                ev(
                    {
                        "repository_initialized": True,
                        "head_branch": "mainline",
                        "latest_commit": {
                            "branch": "mainline",
                            "contains_paths": ["README.md"],
                            "message_contains": ["Initial commit"],
                        },
                        "working_tree_clean": True,
                        "rules": [meta_equals("last_init_initial_branch", "mainline")],
                    },
                    required=["git init", "git commit"],
                ),
                details=[{"label": "First branch name", "value": "mainline"}],
            ),
        ],
        checks=[
            {
                "label": "The repository started on the required first branch.",
                "requirement": {
                    "repository_initialized": True,
                    "rules": [
                        {
                            "type": "operation_metadata_not_equals",
                            "key": "last_init_initial_branch",
                            "value": "main",
                        }
                    ],
                },
            },
            {
                "label": "The first commit is saved.",
                "requirement": {"rules": [{"type": "commit_count_equals", "count": 1}]},
            },
            {
                "label": "Nothing is left uncommitted.",
                "requirement": {"working_tree_clean": True},
            },
        ],
        prerequisites=["init-current-folder"],
        workflow=True,
    ),
    q(
        "git-clone/named-folder",
        "clone-into-named-folder",
        "Clone into a chosen folder and check it",
        "A training repository must be copied locally using the folder name given by the instructor.",
        "Clone into the requested destination folder, then confirm the copy with status and history.",
        [
            v(
                "clone-named-level",
                "Level lab",
                uninitialized({}, remote_fixtures=REMOTE_FIXTURE_MAIN),
                [
                    "git clone https://example.test/cit/level.git level-lab",
                    "git status",
                    "git log --oneline",
                ],
                ev(
                    {
                        "repository_initialized": True,
                        "remote_exists": ["origin"],
                        "upstream_tracking_set": ["main"],
                        "rules": [meta_equals("last_clone_destination", "level-lab")],
                    },
                    required=["git clone"],
                ),
                details=[
                    {"label": "Repository URL", "value": "https://example.test/cit/level.git"},
                    {"label": "Destination folder", "value": "level-lab"},
                ],
            ),
            v(
                "clone-named-api",
                "API lab",
                uninitialized({}, remote_fixtures=REMOTE_FIXTURE_MAIN),
                [
                    "git clone https://example.test/cit/api.git api-lab",
                    "git status",
                    "git log --oneline",
                ],
                ev(
                    {
                        "repository_initialized": True,
                        "remote_exists": ["origin"],
                        "upstream_tracking_set": ["main"],
                        "rules": [meta_equals("last_clone_destination", "api-lab")],
                    },
                    required=["git clone"],
                ),
                details=[
                    {"label": "Repository URL", "value": "https://example.test/cit/api.git"},
                    {"label": "Destination folder", "value": "api-lab"},
                ],
            ),
        ],
        checks=[
            {
                "label": "The project is cloned locally.",
                "requirement": {"repository_initialized": True},
            },
            {
                "label": "It is connected to the origin remote.",
                "requirement": {"remote_exists": ["origin"]},
            },
        ],
        prerequisites=["init-current-folder"],
        workflow=True,
    ),
    q(
        "git-clone/branch",
        "clone-specific-branch",
        "Clone a specific branch",
        "A lab keeps its starter content on a specific branch, so the clone must land directly on that branch.",
        "Clone the repository so it checks out the requested branch immediately, then confirm it.",
        [
            v(
                "clone-branch-starter",
                "Starter branch",
                uninitialized({}, remote_fixtures=REMOTE_FIXTURE_STARTER),
                [
                    "git clone -b starter https://example.test/cit/lab.git lab",
                    "git status",
                    "git log --oneline",
                ],
                ev(
                    {
                        "repository_initialized": True,
                        "head_branch": "starter",
                        "upstream_tracking": {"starter": "origin/starter"},
                        "rules": [meta_equals("last_clone_branch", "starter")],
                    },
                    required=["git clone"],
                ),
                details=[
                    {"label": "Repository URL", "value": "https://example.test/cit/lab.git"},
                    {"label": "Branch to clone", "value": "starter"},
                    {"label": "Destination folder", "value": "lab"},
                ],
            ),
            v(
                "clone-branch-main",
                "Explicit main",
                uninitialized({}, remote_fixtures=REMOTE_FIXTURE_STARTER),
                [
                    "git clone --branch main https://example.test/cit/lab.git lab-main",
                    "git status",
                    "git log --oneline",
                ],
                ev(
                    {
                        "repository_initialized": True,
                        "head_branch": "main",
                        "upstream_tracking": {"main": "origin/main"},
                        "rules": [meta_equals("last_clone_branch", "main")],
                    },
                    required=["git clone"],
                ),
                details=[
                    {"label": "Repository URL", "value": "https://example.test/cit/lab.git"},
                    {"label": "Branch to clone", "value": "main"},
                    {"label": "Destination folder", "value": "lab-main"},
                ],
            ),
        ],
        checks=[
            {
                "label": "The requested branch is cloned locally.",
                "requirement": {"repository_initialized": True},
            },
            {
                "label": "It is connected to the origin remote.",
                "requirement": {"remote_exists": ["origin"]},
            },
        ],
        prerequisites=["clone-into-named-folder"],
        workflow=True,
    ),
    q(
        "git-clone/depth",
        "clone-shallow-history",
        "Clone only the latest history slice",
        "A large repository is needed only for a short review, so old history should not be copied.",
        "Create a shallow local clone.",
        [
            v(
                "clone-depth-portal",
                "Portal review",
                uninitialized({}, remote_fixtures=REMOTE_FIXTURE_HISTORY),
                ["git clone --depth 1 https://example.test/cit/portal.git", "git log --oneline"],
                ev(
                    {
                        "repository_initialized": True,
                        "rules": [
                            meta_equals("last_clone_shallow", True),
                            meta_equals("last_clone_depth", 1),
                            {"type": "commit_count_equals", "count": 1},
                        ],
                    },
                    required=["git clone"],
                ),
                details=[
                    {"label": "Repository URL", "value": "https://example.test/cit/portal.git"},
                    {"label": "History depth", "value": "1"},
                ],
            ),
            v(
                "clone-depth-docs",
                "Docs review",
                uninitialized({}, remote_fixtures=REMOTE_FIXTURE_HISTORY),
                ["git clone --depth 2 https://example.test/cit/docs.git docs", "git log --oneline"],
                ev(
                    {
                        "repository_initialized": True,
                        "rules": [
                            meta_equals("last_clone_shallow", True),
                            meta_equals("last_clone_depth", 2),
                            {"type": "commit_count_equals", "count": 2},
                        ],
                    },
                    required=["git clone"],
                ),
                details=[
                    {"label": "Repository URL", "value": "https://example.test/cit/docs.git"},
                    {"label": "History depth", "value": "2"},
                    {"label": "Destination folder", "value": "docs"},
                ],
            ),
        ],
        checks=[
            {
                "label": "A shallow clone was created.",
                "requirement": {"rules": [meta_equals("last_clone_shallow", True)]},
            },
            {
                "label": "The project is cloned locally.",
                "requirement": {"repository_initialized": True},
            },
        ],
        prerequisites=["clone-into-named-folder"],
        workflow=True,
    ),
    q(
        "git-status/plain",
        "inspect-status",
        "Read status, then save the work",
        "Before saving, you need to see exactly what changed and what is still untracked.",
        "Read the repository status, then stage and commit the reviewed work.",
        [
            v(
                "status-working-change",
                "Triage and save",
                repo(
                    commits=BASE,
                    working_tree={
                        "src/app.py": "print('hello world')\n",
                        "notes.txt": {"status": "untracked", "content": "todo"},
                    },
                ),
                ["git status", "git add .", "git commit -m 'Save reviewed work'"],
                ev(
                    {
                        "latest_commit": {
                            "branch": "main",
                            "contains_paths": ["src/app.py", "notes.txt"],
                            "message_contains": ["Save reviewed work"],
                        },
                        "working_tree_clean": True,
                    },
                    required=["git status", "git commit"],
                ),
            ),
            v(
                "status-staged-change",
                "Confirm and save",
                repo(
                    commits=BASE,
                    working_tree={
                        "README.md": "updated",
                        "docs/log.md": {"status": "untracked", "content": "v1"},
                    },
                ),
                ["git status", "git add .", "git commit -m 'Update docs'"],
                ev(
                    {
                        "latest_commit": {
                            "branch": "main",
                            "contains_paths": ["README.md", "docs/log.md"],
                            "message_contains": ["Update docs"],
                        },
                        "working_tree_clean": True,
                    },
                    required=["git status", "git commit"],
                ),
            ),
        ],
        checks=[
            {
                "label": "Everything you reviewed is committed.",
                "requirement": {"working_tree_clean": True},
            },
            {
                "label": "A new snapshot was saved.",
                "requirement": {"min_commits_on_branch": {"main": 2}},
            },
        ],
        prerequisites=["init-current-folder"],
        min_counted_commands=1,
        max_counted_commands=4,
        workflow=True,
    ),
    q(
        "git-status/ignored",
        "inspect-ignored-status",
        "Confirm what is ignored, then save the code",
        "A build artifact is intentionally ignored; confirm it stays hidden before saving real work.",
        "Use ignored-aware status to check the artifact is hidden, then commit only the real change.",
        [
            v(
                "status-ignored-dist",
                "Ignore build output, save code",
                repo(
                    commits=BASE,
                    working_tree={
                        "dist/app.js": {"status": "ignored", "content": "bundle"},
                        "src/app.py": "print('release')\n",
                    },
                ),
                ["git status --ignored", "git add src/app.py", "git commit -m 'Ship release code'"],
                ev(
                    {
                        "latest_commit": {
                            "branch": "main",
                            "contains_paths": ["src/app.py"],
                            "excludes_paths": ["dist/app.js"],
                            "message_contains": ["Ship release code"],
                        },
                        "working_tree_contains": ["dist/app.js"],
                    },
                    required=["git status --ignored", "git commit"],
                ),
            ),
            v(
                "status-ignored-env",
                "Ignore secrets, save notes",
                repo(
                    commits=BASE,
                    working_tree={
                        ".env": {"status": "ignored", "content": "SECRET=1"},
                        "README.md": "Setup steps",
                    },
                ),
                ["git status --ignored", "git add README.md", "git commit -m 'Document setup'"],
                ev(
                    {
                        "latest_commit": {
                            "branch": "main",
                            "contains_paths": ["README.md"],
                            "excludes_paths": [".env"],
                            "message_contains": ["Document setup"],
                        },
                        "working_tree_contains": [".env"],
                    },
                    required=["git status --ignored", "git commit"],
                ),
            ),
        ],
        checks=[
            {
                "label": "Your real change is saved in a new commit.",
                "requirement": {"min_commits_on_branch": {"main": 2}},
            },
        ],
        prerequisites=["inspect-status"],
        min_counted_commands=1,
        max_counted_commands=4,
        workflow=True,
    ),
    q(
        "git-log/oneline",
        "inspect-compact-history",
        "Survey the recent work, then log a handoff note",
        "You are taking over a feature mid-flight. Survey what has already been done - at a few levels of detail - before adding your own handoff note.",
        "Read the history compactly, limit it to the latest entries, summarize what each commit changed, then commit your handoff note.",
        [
            v(
                "history-handoff-portal",
                "Portal handoff",
                repo(
                    commits=THREE_COMMITS,
                    branches={"main": "c2"},
                    working_tree={
                        "HANDOFF.md": {"status": "untracked", "content": "Picking up after the login work.\n"}
                    },
                ),
                [
                    "git log --oneline",
                    "git log -n 2",
                    "git log --stat",
                    "git add HANDOFF.md",
                    "git commit -m 'Add handoff notes'",
                ],
                ev(
                    {
                        "latest_commit": {
                            "branch": "main",
                            "contains_paths": ["HANDOFF.md"],
                            "message_contains": ["handoff"],
                        },
                        "working_tree_clean": True,
                    },
                    required=["git log --oneline", "git commit"],
                ),
            ),
            v(
                "history-handoff-docs",
                "Docs handoff",
                repo(
                    commits=THREE_COMMITS,
                    branches={"main": "c2"},
                    working_tree={
                        "HANDOFF.md": {"status": "untracked", "content": "Continuing the docs refresh.\n"}
                    },
                ),
                [
                    "git log --oneline",
                    "git log -n 3",
                    "git log --stat",
                    "git add HANDOFF.md",
                    "git commit -m 'Add handoff summary'",
                ],
                ev(
                    {
                        "latest_commit": {
                            "branch": "main",
                            "contains_paths": ["HANDOFF.md"],
                            "message_contains": ["handoff"],
                        },
                        "working_tree_clean": True,
                    },
                    required=["git log --oneline", "git commit"],
                ),
            ),
        ],
        checks=[
            {
                "label": "Your handoff note is part of the project history now.",
                "requirement": {"min_commits_on_branch": {"main": 4}},
            },
            {
                "label": "Nothing is left uncommitted.",
                "requirement": {"working_tree_clean": True},
            },
        ],
        prerequisites=["inspect-status"],
        min_counted_commands=1,
        max_counted_commands=6,
        workflow=True,
    ),
    q(
        "git-log/graph-all",
        "inspect-graph-history",
        "Map the branch shape, then record your review",
        "Two lines of work exist side by side. Map the full branch graph and read the detailed changes before recording what you found.",
        "View the whole-history graph across all branches, read the per-commit patches, then commit your review note.",
        [
            v(
                "history-graph-feature",
                "Feature branch graph",
                repo(
                    commits=THREE_COMMITS
                    + [
                        commit(
                            "c3", "Draft profile", ["c1"], {**BASE_TREE, "src/profile.py": "draft"}
                        )
                    ],
                    branches={"main": "c2", "feature/profile": "c3"},
                    working_tree={
                        "REVIEW.md": {"status": "untracked", "content": "Reviewed main vs feature/profile.\n"}
                    },
                ),
                [
                    "git log --oneline --graph --all",
                    "git log -p",
                    "git add REVIEW.md",
                    "git commit -m 'Record branch review'",
                ],
                ev(
                    {
                        "latest_commit": {
                            "branch": "main",
                            "contains_paths": ["REVIEW.md"],
                            "message_contains": ["review"],
                        },
                        "working_tree_clean": True,
                    },
                    required=["git log --oneline --graph --all", "git commit"],
                ),
            ),
            v(
                "history-graph-hotfix",
                "Hotfix branch graph",
                repo(
                    commits=THREE_COMMITS
                    + [commit("c4", "Patch copy", ["c1"], {**BASE_TREE, "README.md": "patched"})],
                    branches={"main": "c2", "hotfix/copy": "c4"},
                    working_tree={
                        "REVIEW.md": {"status": "untracked", "content": "Reviewed main vs hotfix/copy.\n"}
                    },
                ),
                [
                    "git log --oneline --graph --all",
                    "git log -p",
                    "git add REVIEW.md",
                    "git commit -m 'Record hotfix review'",
                ],
                ev(
                    {
                        "latest_commit": {
                            "branch": "main",
                            "contains_paths": ["REVIEW.md"],
                            "message_contains": ["review"],
                        },
                        "working_tree_clean": True,
                    },
                    required=["git log --oneline --graph --all", "git commit"],
                ),
            ),
        ],
        checks=[
            {
                "label": "Your review note is saved on main.",
                "requirement": {"min_commits_on_branch": {"main": 4}},
            },
            {
                "label": "Nothing is left uncommitted.",
                "requirement": {"working_tree_clean": True},
            },
        ],
        prerequisites=["inspect-compact-history"],
        min_counted_commands=1,
        max_counted_commands=6,
        workflow=True,
    ),
    q(
        "git-show/commit",
        "inspect-named-commit",
        "Inspect specific commits, then file a report",
        "A review references particular commits. Inspect exactly what they changed - the full diff, the touched files, and the current tip - before filing your report.",
        "Inspect a named commit in full, list just the files another commit touched, read the current tip, then commit your report.",
        [
            v(
                "history-report-login",
                "Login report",
                repo(
                    commits=THREE_COMMITS,
                    branches={"main": "c2"},
                    working_tree={
                        "AUDIT.md": {"status": "untracked", "content": "Audited c1 and c2.\n"}
                    },
                ),
                [
                    "git show c1",
                    "git show --name-only c2",
                    "git show",
                    "git add AUDIT.md",
                    "git commit -m 'File audit report'",
                ],
                ev(
                    {
                        "latest_commit": {
                            "branch": "main",
                            "contains_paths": ["AUDIT.md"],
                            "message_contains": ["audit"],
                        },
                        "working_tree_clean": True,
                    },
                    required=["git show c1", "git commit"],
                ),
                details=[
                    {"label": "Show full diff for", "value": "c1"},
                    {"label": "List touched files for", "value": "c2"},
                ],
            ),
            v(
                "history-report-shell",
                "Shell report",
                repo(
                    commits=THREE_COMMITS,
                    branches={"main": "c2"},
                    working_tree={
                        "AUDIT.md": {"status": "untracked", "content": "Audited the app shell commits.\n"}
                    },
                ),
                [
                    "git show c0",
                    "git show --name-only c1",
                    "git show",
                    "git add AUDIT.md",
                    "git commit -m 'File shell audit'",
                ],
                ev(
                    {
                        "latest_commit": {
                            "branch": "main",
                            "contains_paths": ["AUDIT.md"],
                            "message_contains": ["audit"],
                        },
                        "working_tree_clean": True,
                    },
                    required=["git show c0", "git commit"],
                ),
                details=[
                    {"label": "Show full diff for", "value": "c0"},
                    {"label": "List touched files for", "value": "c1"},
                ],
            ),
        ],
        checks=[
            {
                "label": "Your audit report is saved in a new commit.",
                "requirement": {"min_commits_on_branch": {"main": 4}},
            },
            {
                "label": "Nothing is left uncommitted.",
                "requirement": {"working_tree_clean": True},
            },
        ],
        prerequisites=["inspect-compact-history"],
        min_counted_commands=1,
        max_counted_commands=6,
        workflow=True,
    ),
]
