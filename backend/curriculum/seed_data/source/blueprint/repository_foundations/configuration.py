"""Repository Foundations levels for configuration."""

from __future__ import annotations

from ..helpers import _wave

LEVELS = [
        {
            "slug": "configure-identity-and-aliases",
            "title": "Configure Identity and Aliases",
            "waves": [
                _wave(
                    "ch1-adv-set-user-name",
                    "git-config/global-user-name",
                    "Set user name",
                    ["git config --global user.name 'Learner A'"],
                    state="clean",
                    story=(
                        "This machine has never had a Git identity configured. Before anything gets "
                        "authored here, set the global author name so every future commit is "
                        "attributed correctly."
                    ),
                    evaluation={
                        "rules": [
                            {"type": "operation_metadata_equals", "key": "last_config_key", "value": "user.name"},
                            {"type": "operation_metadata_equals", "key": "last_config_scope", "value": "global"},
                        ]
                    },
                    checks=[
                        {
                            "label": "The global author name is saved in your config.",
                            "requirement": {
                                "rules": [
                                    {"type": "operation_metadata_equals", "key": "last_config_key", "value": "user.name"},
                                    {"type": "operation_metadata_equals", "key": "last_config_scope", "value": "global"},
                                ]
                            },
                        }
                    ],
                ),
                _wave(
                    "ch1-adv-set-user-email",
                    "git-config/global-user-email",
                    "Set user email",
                    ["git config --global user.email learner-a@example.test"],
                    state="clean",
                    story=(
                        "Author name is set, but the email half of this machine's identity is still "
                        "missing. Set the global author email to complete it."
                    ),
                    evaluation={
                        "rules": [
                            {"type": "operation_metadata_equals", "key": "last_config_key", "value": "user.email"},
                            {"type": "operation_metadata_equals", "key": "last_config_scope", "value": "global"},
                        ]
                    },
                    checks=[
                        {
                            "label": "The global author email is saved in your config.",
                            "requirement": {
                                "rules": [
                                    {"type": "operation_metadata_equals", "key": "last_config_key", "value": "user.email"},
                                    {"type": "operation_metadata_equals", "key": "last_config_scope", "value": "global"},
                                ]
                            },
                        }
                    ],
                ),
                _wave(
                    "ch1-adv-config-list-intro",
                    "git-config/list",
                    "List effective settings",
                    ["git config --list"],
                    state="clean",
                    story=(
                        "Before this machine authors anything, you want to see every setting Git "
                        "will actually apply here: identity, shortcuts, all of it. Read the full "
                        "effective configuration without changing a single value."
                    ),
                    evaluation={
                        "repository_initialized": True,
                        "staging_empty": True,
                        "rules": [{"type": "commit_count_equals", "count": 1}],
                    },
                    checks=[
                        {
                            "label": "The effective configuration was listed and read.",
                            "requirement": {"required_commands": ["git config --list"]},
                        },
                    ],
                ),
                _wave(
                    "ch1-adv-alias-intro",
                    "git-config/alias",
                    "Create a status shortcut",
                    ["git config --global alias.st status"],
                    state="clean",
                    story=(
                        "You check the workspace state constantly, and the full spelling is slowing "
                        "you down. Record a global shortcut named st that expands to the state-"
                        "reading command."
                    ),
                    details=[
                        {"label": "Alias name", "value": "st"},
                        {"label": "Expands to", "value": "status"},
                    ],
                    evaluation={
                        "rules": [
                            {
                                "type": "operation_metadata_equals",
                                "key": "last_config_key",
                                "value": "alias.st",
                            }
                        ]
                    },
                    checks=[
                        {
                            "label": "A global st shortcut is recorded in your configuration.",
                            "requirement": {
                                "rules": [
                                    {
                                        "type": "operation_metadata_equals",
                                        "key": "last_config_key",
                                        "value": "alias.st",
                                    }
                                ]
                            },
                        }
                    ],
                ),
                _wave(
                    "ch1-adv-list-config",
                    "git-config/list",
                    "List config",
                    ["git config --list", "git add README.md", "git commit -m 'Save verified identity'"],
                    required=["git config --list", "git commit"],
                    forms=["git-add/file", "git-commit/message"],
                    state="dirty",
                    story=(
                        "Before this next commit goes out under your name, verify the effective "
                        "configuration actually has the identity you expect, then save the pending "
                        "README edit."
                    ),
                    evaluation={
                        "latest_commit": {
                            "branch": "main",
                            "contains_paths": ["README.md"],
                            "message_contains": ["Save verified identity"],
                        },
                        "staging_empty": True,
                        "working_tree_clean": True,
                    },
                    checks=[
                        {
                            "label": "The effective configuration was listed and checked before committing.",
                            "requirement": {"required_commands": ["git config --list"]},
                        },
                        {
                            "label": "The verified change is committed on main.",
                            "requirement": {
                                "latest_commit": {
                                    "branch": "main",
                                    "contains_paths": ["README.md"],
                                    "message_contains": ["Save verified identity"],
                                }
                            },
                        },
                    ],
                ),
                _wave(
                    "ch1-adv-create-alias",
                    "git-config/alias",
                    "Create alias",
                    [
                        "git config --global alias.st status",
                        "git config --list",
                        "git add README.md",
                        "git commit -m 'Save alias setup'",
                    ],
                    required=["git config --global alias.st", "git config --list", "git commit"],
                    forms=["git-config/list", "git-add/file", "git-commit/message"],
                    state="dirty",
                    story=(
                        "Typing the full status command all day is getting old. Create a global "
                        "alias.st shortcut for it, confirm it is recorded, and then use the normal "
                        "save loop to commit the pending README edit."
                    ),
                    evaluation={
                        "latest_commit": {
                            "branch": "main",
                            "contains_paths": ["README.md"],
                            "message_contains": ["Save alias setup"],
                        },
                        "staging_empty": True,
                        "working_tree_clean": True,
                        "rules": [
                            {"type": "operation_metadata_equals", "key": "last_config_key", "value": "alias.st"},
                        ],
                    },
                    checks=[
                        {
                            "label": "A global alias.st shortcut is recorded and verified in config.",
                            "requirement": {
                                "rules": [
                                    {"type": "operation_metadata_equals", "key": "last_config_key", "value": "alias.st"},
                                ]
                            },
                        },
                        {
                            "label": "The repository is clean after the normal save loop runs.",
                            "requirement": {"staging_empty": True, "working_tree_clean": True},
                        },
                    ],
                ),
            ],
        },
        {
            "slug": "ignore-noise",
            "title": "Ignore Noise",
            "waves": [
                _wave(
                    "ch1-adv-status-ignored-intro",
                    "git-status/ignored",
                    "See what Git ignores",
                    ["git status --ignored"],
                    state="ignore",
                    story=(
                        "This workspace holds real source work, a rule file, and a generated log "
                        "that should never enter history. Read the state with ignored entries "
                        "included so you can see exactly what Git is deliberately overlooking."
                    ),
                    evaluation={
                        "staging_empty": True,
                        "rules": [{"type": "ignored_paths_present", "paths": ["build.log"]}],
                    },
                    checks=[
                        {
                            "label": "The state was read with ignored entries included.",
                            "requirement": {"required_commands": ["git status --ignored"]},
                        },
                    ],
                ),
                _wave(
                    "ch1-adv-check-ignore-intro",
                    "git-check-ignore/verbose",
                    "Trace an ignore rule",
                    ["git check-ignore -v build.log"],
                    state="ignore",
                    story=(
                        "A teammate asks why build.log never shows up as trackable work. Trace "
                        "exactly which rule file and pattern claim that path, so you can answer "
                        "with evidence instead of a guess."
                    ),
                    details=[{"label": "Path to trace", "value": "build.log"}],
                    evaluation={
                        "staging_empty": True,
                        "rules": [{"type": "ignored_paths_present", "paths": ["build.log"]}],
                    },
                    checks=[
                        {
                            "label": "The matching rule was traced for the ignored path.",
                            "requirement": {"required_commands": ["git check-ignore"]},
                        },
                    ],
                ),
                _wave(
                    "ch1-adv-write-ignore-rule",
                    "git-status/ignored",
                    "Write ignore rule",
                    ["git status --ignored", "git add .gitignore src/app.py", "git commit -m 'Ignore build output'"],
                    required=["git status --ignored", "git add", "git commit"],
                    forms=["git-add/file", "git-commit/message"],
                    state="ignore",
                    story=(
                        "A generated build.log sits beside a real source edit in src/app.py, and a new "
                        ".gitignore rule already exists to keep build output out. Confirm the ignored "
                        "file with status --ignored, then commit only the ignore rule and the source "
                        "edit."
                    ),
                    evaluation={
                        "latest_commit": {
                            "branch": "main",
                            "contains_paths": [".gitignore", "src/app.py"],
                            "excludes_paths": ["build.log"],
                            "message_contains": ["Ignore build output"],
                        },
                        "staging_empty": True,
                        "working_tree_clean": True,
                        "rules": [{"type": "ignored_paths_present", "paths": ["build.log"]}],
                    },
                    checks=[
                        {
                            "label": "The build output was confirmed as ignored noise, not real work.",
                            "requirement": {"required_commands": ["git status --ignored"]},
                        },
                        {
                            "label": "The ignore rule and the source edit are committed together.",
                            "requirement": {
                                "latest_commit": {
                                    "branch": "main",
                                    "contains_paths": [".gitignore", "src/app.py"],
                                    "message_contains": ["Ignore build output"],
                                }
                            },
                        },
                    ],
                ),
                _wave(
                    "ch1-adv-explain-ignore-rule",
                    "git-check-ignore/verbose",
                    "Explain ignore rule",
                    ["git check-ignore -v build.log", "git add src/app.py", "git commit -m 'Save source without build log'"],
                    required=["git check-ignore -v", "git commit"],
                    forms=["git-add/file", "git-commit/message"],
                    state="ignore",
                    story=(
                        "A teammate asks exactly which rule is keeping build.log out of history. Trace "
                        "the matching .gitignore pattern with check-ignore -v, then save the real "
                        "source edit without dragging the generated file along."
                    ),
                    evaluation={
                        "latest_commit": {
                            "branch": "main",
                            "contains_paths": ["src/app.py"],
                            "excludes_paths": ["build.log", ".gitignore"],
                            "message_contains": ["Save source without build log"],
                        },
                        "staging_empty": True,
                    },
                    checks=[
                        {
                            "label": "The matching ignore rule was traced with check-ignore -v.",
                            "requirement": {"required_commands": ["git check-ignore -v"]},
                        },
                        {
                            "label": "Only the source edit is committed; the generated file is not.",
                            "requirement": {
                                "latest_commit": {
                                    "branch": "main",
                                    "contains_paths": ["src/app.py"],
                                    "excludes_paths": ["build.log"],
                                    "message_contains": ["Save source without build log"],
                                }
                            },
                        },
                    ],
                ),
            ],
        },
    ]
