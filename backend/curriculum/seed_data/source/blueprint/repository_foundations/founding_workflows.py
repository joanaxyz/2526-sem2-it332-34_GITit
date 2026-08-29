"""Repository Foundations levels for founding workflows."""

from __future__ import annotations

from ..helpers import _wave

LEVELS = [
        {
            "slug": "founding-workflows",
            "title": "Founding Workflows",
            "waves": [
                _wave(
                    "ch1-adv-new-project-identity",
                    "git-init/current-directory",
                    "Found a project with identity",
                    [
                        "git init",
                        "git config --global user.name 'Learner A'",
                        "git config --global user.email learner-a@example.test",
                        "git add .",
                        "git commit -m 'Initial commit'",
                    ],
                    required=["git init", "git config", "git add", "git commit"],
                    forms=[
                        "git-config/global-user-name",
                        "git-config/global-user-email",
                        "git-add/dot",
                        "git-commit/message",
                    ],
                    state="uninitialized",
                    story=(
                        "A brand-new machine, a brand-new project: nothing is tracked and no author "
                        "identity exists yet. Stand the repository up, record the author name and "
                        "email shown below, and land every starter file in a first snapshot that is "
                        "attributed correctly."
                    ),
                    details=[
                        {"label": "Author name", "value": "Learner A"},
                        {"label": "Author email", "value": "learner-a@example.test"},
                        {"label": "Commit message", "value": "Initial commit"},
                    ],
                    evaluation={
                        "repository_initialized": True,
                        "latest_commit": {
                            "branch": "main",
                            "contains_paths": ["README.md", "src/app.py"],
                            "message_contains": ["Initial commit"],
                        },
                        "working_tree_clean": True,
                        "staging_empty": True,
                        "rules": [
                            {
                                "type": "operation_metadata_equals",
                                "key": "last_config_key",
                                "value": "user.email",
                            }
                        ],
                    },
                    checks=[
                        {
                            "label": "The folder is a repository with both identity halves recorded.",
                            "requirement": {
                                "repository_initialized": True,
                                "rules": [
                                    {
                                        "type": "operation_metadata_equals",
                                        "key": "last_config_key",
                                        "value": "user.email",
                                    }
                                ],
                            },
                        },
                        {
                            "label": "Every starter file landed in the first snapshot.",
                            "requirement": {
                                "latest_commit": {
                                    "branch": "main",
                                    "contains_paths": ["README.md", "src/app.py"],
                                    "message_contains": ["Initial commit"],
                                }
                            },
                        },
                        {
                            "label": "Nothing is left staged or unstaged afterward.",
                            "requirement": {"working_tree_clean": True, "staging_empty": True},
                        },
                    ],
                ),
                _wave(
                    "ch1-adv-init-status-save",
                    "git-init/current-directory",
                    "Initialize, inspect, save, verify",
                    [
                        "git init",
                        "git status",
                        "git add .",
                        "git commit -m 'First snapshot'",
                        "git log --oneline",
                    ],
                    required=["git init", "git status", "git add", "git commit", "git log"],
                    forms=["git-status/plain", "git-add/dot", "git-commit/message", "git-log/oneline"],
                    state="uninitialized",
                    story=(
                        "This starter folder is about to become the project of record, and you want "
                        "the full founding routine done properly: create the repository, read what "
                        "it sees, save everything as the first snapshot, and verify it in history."
                    ),
                    details=[{"label": "Commit message", "value": "First snapshot"}],
                    evaluation={
                        "repository_initialized": True,
                        "latest_commit": {
                            "branch": "main",
                            "contains_paths": ["README.md", "src/app.py"],
                            "message_contains": ["First snapshot"],
                        },
                        "working_tree_clean": True,
                        "staging_empty": True,
                        "rules": [{"type": "commit_count_equals", "count": 1}],
                    },
                    checks=[
                        {
                            "label": "The fresh repository state was read before saving.",
                            "requirement": {"required_commands": ["git status"]},
                        },
                        {
                            "label": "Every starter file landed in the first snapshot.",
                            "requirement": {
                                "latest_commit": {
                                    "branch": "main",
                                    "contains_paths": ["README.md", "src/app.py"],
                                    "message_contains": ["First snapshot"],
                                }
                            },
                        },
                        {
                            "label": "The snapshot was verified against history afterward.",
                            "requirement": {"required_commands": ["git log"]},
                        },
                    ],
                ),
                _wave(
                    "ch1-adv-named-project-save",
                    "git-init/named-directory",
                    "Found a studio workspace",
                    [
                        "git init studio",
                        "git status",
                        "git add .",
                        "git commit -m 'Studio setup'",
                    ],
                    required=["git init", "git status", "git add", "git commit"],
                    forms=["git-status/plain", "git-add/dot", "git-commit/message"],
                    state="uninitialized",
                    story=(
                        "The design team's new workspace must live under the exact folder name "
                        "shown below. Create it, read what the fresh repository sees, and save the "
                        "starter files as its first snapshot."
                    ),
                    details=[
                        {"label": "Folder name", "value": "studio"},
                        {"label": "Commit message", "value": "Studio setup"},
                    ],
                    evaluation={
                        "repository_initialized": True,
                        "latest_commit": {
                            "branch": "main",
                            "contains_paths": ["README.md", "src/app.py"],
                            "message_contains": ["Studio setup"],
                        },
                        "working_tree_clean": True,
                        "rules": [
                            {
                                "type": "operation_metadata_equals",
                                "key": "last_init_directory",
                                "value": "studio",
                            }
                        ],
                    },
                    checks=[
                        {
                            "label": "The workspace was created under the requested folder name.",
                            "requirement": {
                                "rules": [
                                    {
                                        "type": "operation_metadata_equals",
                                        "key": "last_init_directory",
                                        "value": "studio",
                                    }
                                ]
                            },
                        },
                        {
                            "label": "The starter files are saved in the first snapshot.",
                            "requirement": {
                                "latest_commit": {
                                    "branch": "main",
                                    "contains_paths": ["README.md", "src/app.py"],
                                    "message_contains": ["Studio setup"],
                                }
                            },
                        },
                    ],
                ),
                _wave(
                    "ch1-adv-review-then-save",
                    "git-diff/working",
                    "Review every angle, then save",
                    [
                        "git status",
                        "git diff",
                        "git add README.md",
                        "git diff --staged",
                        "git commit -m 'Save reviewed work'",
                    ],
                    required=["git status", "git diff", "git add", "git diff --staged", "git commit"],
                    forms=["git-status/plain", "git-add/file", "git-diff/staged", "git-commit/message"],
                    state="mixed",
                    story=(
                        "One tracked edit is ready to ship while a loose scratch file must stay "
                        "local. Read the overall state, review the unstaged lines, stage only the "
                        "real work, re-check what is about to be saved, and then seal the snapshot."
                    ),
                    details=[{"label": "Commit message", "value": "Save reviewed work"}],
                    evaluation={
                        "latest_commit": {
                            "branch": "main",
                            "contains_paths": ["README.md"],
                            "excludes_paths": ["scratch.txt"],
                            "message_contains": ["Save reviewed work"],
                        },
                        "staging_empty": True,
                        "rules": [{"type": "commit_count_equals", "count": 2}],
                    },
                    checks=[
                        {
                            "label": "The work was reviewed before and after staging.",
                            "requirement": {"required_commands": ["git diff", "git diff --staged"]},
                        },
                        {
                            "label": "Only the real edit was committed; the scratch file stayed local.",
                            "requirement": {
                                "latest_commit": {
                                    "branch": "main",
                                    "contains_paths": ["README.md"],
                                    "excludes_paths": ["scratch.txt"],
                                    "message_contains": ["Save reviewed work"],
                                }
                            },
                        },
                    ],
                ),
                _wave(
                    "ch1-adv-two-snapshots",
                    "git-add/file",
                    "Build history in two snapshots",
                    [
                        "git init",
                        "git add README.md",
                        "git commit -m 'Add readme'",
                        "git add .",
                        "git commit -m 'Add source'",
                        "git log --oneline",
                    ],
                    required=["git init", "git add", "git commit", "git log"],
                    forms=[
                        "git-init/current-directory",
                        "git-commit/message",
                        "git-add/dot",
                        "git-log/oneline",
                    ],
                    state="uninitialized",
                    story=(
                        "This new project's history should tell a story: first the introduction, "
                        "then the source. Stand the repository up, save the readme by itself, save "
                        "the remaining work as a second snapshot, and read the history you built."
                    ),
                    details=[
                        {"label": "First message", "value": "Add readme"},
                        {"label": "Second message", "value": "Add source"},
                    ],
                    evaluation={
                        "repository_initialized": True,
                        "latest_commit": {
                            "branch": "main",
                            "contains_paths": ["src/app.py"],
                            "message_contains": ["Add source"],
                        },
                        "working_tree_clean": True,
                        "staging_empty": True,
                        "rules": [{"type": "commit_count_equals", "count": 2}],
                    },
                    checks=[
                        {
                            "label": "History holds exactly two snapshots, in story order.",
                            "requirement": {"rules": [{"type": "commit_count_equals", "count": 2}]},
                        },
                        {
                            "label": "The second snapshot carries the source work.",
                            "requirement": {
                                "latest_commit": {
                                    "branch": "main",
                                    "contains_paths": ["src/app.py"],
                                    "message_contains": ["Add source"],
                                }
                            },
                        },
                        {
                            "label": "The built history was read back afterward.",
                            "requirement": {"required_commands": ["git log"]},
                        },
                    ],
                ),
                _wave(
                    "ch1-adv-ignore-from-scratch",
                    "git-status/ignored",
                    "Adopt ignore rules end to end",
                    [
                        "git status --ignored",
                        "git check-ignore -v build.log",
                        "git add .gitignore src/app.py",
                        "git commit -m 'Adopt ignore rules'",
                    ],
                    required=["git status --ignored", "git check-ignore", "git add", "git commit"],
                    forms=["git-check-ignore/verbose", "git-add/file", "git-commit/message"],
                    state="ignore",
                    story=(
                        "Generated output keeps photobombing this workspace next to real source "
                        "work. Confirm what is being overlooked and why, then commit the rule file "
                        "and the source edit together while the generated file stays out of history."
                    ),
                    details=[{"label": "Commit message", "value": "Adopt ignore rules"}],
                    evaluation={
                        "latest_commit": {
                            "branch": "main",
                            "contains_paths": [".gitignore", "src/app.py"],
                            "excludes_paths": ["build.log"],
                            "message_contains": ["Adopt ignore rules"],
                        },
                        "staging_empty": True,
                        "rules": [{"type": "ignored_paths_present", "paths": ["build.log"]}],
                    },
                    checks=[
                        {
                            "label": "The ignored path and its matching rule were both confirmed.",
                            "requirement": {
                                "required_commands": ["git status --ignored", "git check-ignore"]
                            },
                        },
                        {
                            "label": "The rule and the source edit are committed; the noise is not.",
                            "requirement": {
                                "latest_commit": {
                                    "branch": "main",
                                    "contains_paths": [".gitignore", "src/app.py"],
                                    "excludes_paths": ["build.log"],
                                    "message_contains": ["Adopt ignore rules"],
                                }
                            },
                        },
                    ],
                ),
            ],
        },
    ]
