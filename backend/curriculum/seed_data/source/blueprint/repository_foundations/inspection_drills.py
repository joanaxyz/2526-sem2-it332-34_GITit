"""Repository Foundations levels for inspection drills."""

from __future__ import annotations

from ..helpers import _wave

LEVELS = [
        {
            "slug": "inspection-drills",
            "title": "Inspection Drills",
            "waves": [
                _wave(
                    "ch1-adv-porcelain-staged",
                    "git-status/porcelain",
                    "Script check mid-snapshot",
                    ["git status --porcelain"],
                    state="staged",
                    story=(
                        "A release script runs while a README.md change is already staged and "
                        "waiting. Read the workspace in the stable script-friendly form to see how "
                        "a half-built snapshot reports itself, and touch nothing."
                    ),
                    evaluation={
                        "staging_not_empty": True,
                        "rules": [
                            {"type": "staging_contains", "path": "README.md"},
                            {"type": "commit_count_equals", "count": 1},
                        ],
                    },
                    checks=[
                        {
                            "label": "The half-built snapshot was read in script-stable form.",
                            "requirement": {"required_commands": ["git status --porcelain"]},
                        },
                    ],
                ),
                _wave(
                    "ch1-adv-identity-fresh-machine",
                    "git-config/global-user-name",
                    "Set up a fresh machine",
                    [
                        "git config --global user.name 'Learner C'",
                        "git config --global user.email learner-c@example.test",
                        "git config --list",
                    ],
                    required=["git config --global user.name", "git config --global user.email", "git config --list"],
                    forms=["git-config/global-user-email", "git-config/list"],
                    state="clean",
                    story=(
                        "A loaner laptop has no idea who you are, and nothing should be authored "
                        "from it until it does. Record both halves of the identity shown below, "
                        "then list the effective settings to confirm the machine is ready."
                    ),
                    details=[
                        {"label": "Author name", "value": "Learner C"},
                        {"label": "Author email", "value": "learner-c@example.test"},
                    ],
                    evaluation={
                        "rules": [
                            {
                                "type": "operation_metadata_equals",
                                "key": "last_config_key",
                                "value": "user.email",
                            },
                            {
                                "type": "operation_metadata_equals",
                                "key": "last_config_scope",
                                "value": "global",
                            },
                        ]
                    },
                    checks=[
                        {
                            "label": "Both halves of the identity are recorded globally.",
                            "requirement": {
                                "rules": [
                                    {
                                        "type": "operation_metadata_equals",
                                        "key": "last_config_key",
                                        "value": "user.email",
                                    }
                                ]
                            },
                        },
                        {
                            "label": "The effective settings were listed to confirm readiness.",
                            "requirement": {"required_commands": ["git config --list"]},
                        },
                    ],
                ),
                _wave(
                    "ch1-adv-alias-shortlog",
                    "git-config/alias",
                    "Create a history shortcut",
                    ["git config --global alias.lg log", "git config --list"],
                    required=["git config --global alias.lg", "git config --list"],
                    forms=["git-config/list"],
                    state="clean",
                    story=(
                        "You read project history more than any other output, so it deserves its "
                        "own shortcut. Record a global shortcut named lg for the history command, "
                        "then list the settings to confirm it stuck."
                    ),
                    details=[
                        {"label": "Alias name", "value": "lg"},
                        {"label": "Expands to", "value": "log"},
                    ],
                    evaluation={
                        "rules": [
                            {
                                "type": "operation_metadata_equals",
                                "key": "last_config_key",
                                "value": "alias.lg",
                            }
                        ]
                    },
                    checks=[
                        {
                            "label": "A global lg shortcut is recorded in your configuration.",
                            "requirement": {
                                "rules": [
                                    {
                                        "type": "operation_metadata_equals",
                                        "key": "last_config_key",
                                        "value": "alias.lg",
                                    }
                                ]
                            },
                        },
                        {
                            "label": "The recorded shortcut was confirmed in the listed settings.",
                            "requirement": {"required_commands": ["git config --list"]},
                        },
                    ],
                ),
                _wave(
                    "ch1-adv-show-second-commit",
                    "git-show/commit",
                    "Describe the latest change",
                    ["git show c1", "git add CHANGELOG.md", "git commit -m 'Describe latest change'"],
                    required=["git show", "git add", "git commit"],
                    forms=["git-add/file", "git-commit/message"],
                    state="show-note",
                    story=(
                        "The changelog draft needs an accurate description of the most recent "
                        "snapshot, referenced by its exact name. Open that named snapshot, read "
                        "what it changed, then save the finished changelog entry."
                    ),
                    details=[
                        {"label": "Commit to inspect", "value": "c1"},
                        {"label": "Commit message", "value": "Describe latest change"},
                    ],
                    evaluation={
                        "latest_commit": {
                            "branch": "main",
                            "contains_paths": ["CHANGELOG.md"],
                            "message_contains": ["Describe latest change"],
                        },
                        "staging_empty": True,
                        "working_tree_clean": True,
                        "rules": [{"type": "commit_count_equals", "count": 3}],
                    },
                    checks=[
                        {
                            "label": "The named snapshot was opened and read first.",
                            "requirement": {"required_commands": ["git show"]},
                        },
                        {
                            "label": "The changelog entry is committed on main.",
                            "requirement": {
                                "latest_commit": {
                                    "branch": "main",
                                    "contains_paths": ["CHANGELOG.md"],
                                    "message_contains": ["Describe latest change"],
                                }
                            },
                        },
                    ],
                ),
                _wave(
                    "ch1-adv-patch-review-note",
                    "git-log/patch",
                    "Patch review, then a note",
                    ["git log -p", "git add REVIEW.md", "git commit -m 'Record patch review'"],
                    required=["git log -p", "git add", "git commit"],
                    forms=["git-add/file", "git-commit/message"],
                    state="history-note",
                    story=(
                        "A review note, REVIEW.md, should summarize every line this project's "
                        "history has changed so far. Walk the history with full patch text to "
                        "gather the facts, then save the finished note as the next snapshot."
                    ),
                    details=[{"label": "Commit message", "value": "Record patch review"}],
                    evaluation={
                        "latest_commit": {
                            "branch": "main",
                            "contains_paths": ["REVIEW.md"],
                            "message_contains": ["Record patch review"],
                        },
                        "staging_empty": True,
                        "working_tree_clean": True,
                        "rules": [{"type": "commit_count_equals", "count": 3}],
                    },
                    checks=[
                        {
                            "label": "History was walked with full patch detail first.",
                            "requirement": {"required_commands": ["git log -p"]},
                        },
                        {
                            "label": "The review note is committed on main.",
                            "requirement": {
                                "latest_commit": {
                                    "branch": "main",
                                    "contains_paths": ["REVIEW.md"],
                                    "message_contains": ["Record patch review"],
                                }
                            },
                        },
                    ],
                ),
                _wave(
                    "ch1-adv-name-only-audit",
                    "git-show/name-only",
                    "Path audit, then a note",
                    [
                        "git show --name-only c0",
                        "git add AUDIT.md",
                        "git commit -m 'List first commit paths'",
                    ],
                    required=["git show --name-only", "git add", "git commit"],
                    forms=["git-add/file", "git-commit/message"],
                    state="audit-note",
                    story=(
                        "The audit sheet's last blank is the list of paths the project's very first "
                        "snapshot touched. Read exactly that list from the named snapshot, complete "
                        "AUDIT.md, and save it."
                    ),
                    details=[
                        {"label": "Commit to inspect", "value": "c0"},
                        {"label": "Commit message", "value": "List first commit paths"},
                    ],
                    evaluation={
                        "latest_commit": {
                            "branch": "main",
                            "contains_paths": ["AUDIT.md"],
                            "message_contains": ["List first commit paths"],
                        },
                        "staging_empty": True,
                        "working_tree_clean": True,
                        "rules": [{"type": "commit_count_equals", "count": 4}],
                    },
                    checks=[
                        {
                            "label": "Only the touched paths were read from the named snapshot.",
                            "requirement": {"required_commands": ["git show --name-only"]},
                        },
                        {
                            "label": "The completed audit note is committed on main.",
                            "requirement": {
                                "latest_commit": {
                                    "branch": "main",
                                    "contains_paths": ["AUDIT.md"],
                                    "message_contains": ["List first commit paths"],
                                }
                            },
                        },
                    ],
                ),
            ],
        },
    ]
