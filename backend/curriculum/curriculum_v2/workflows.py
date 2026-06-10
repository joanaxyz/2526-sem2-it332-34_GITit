from curriculum.curriculum_v2.drills import EMPTY_FOLDER_STATE, REPO_WITH_WORKING_CHANGE

WORKFLOW_SCENARIOS = [

    {
        "module": "creating-inspecting-repositories",
        "slug": "wake-the-repository",
        "title": "Wake the Repository",
        "summary": "Turn a plain folder into a tracked project base.",
        "narrative": "A project folder exists, but it has no repository metadata yet.",
        "command_topics": ["git init"],
        "levels": [
            {
                "difficulty": "easy",
                "required_successful_attempts": 1,
                "min_counted_commands": 1,
                "max_counted_commands": 3,
                "scenario_context": {
                    "schema_version": 3,
                    "story": "You opened a project folder called field-notes. It has files, but no repository metadata.",
                    "task": "Turn this folder into a repository."
                },
                "variants": [
                    {
                        "case_id": "easy-wake-current-folder",
                        "slug_template": "easy-wake-current-folder",
                        "label_template": "Current folder",
                        "initial_state_template": EMPTY_FOLDER_STATE,
                        "solution_commands_template": ["git init"],
                        "evaluation_spec_template": {
                            "state_requirements": {"repository_initialized": True},
                            "process_requirements": {"required_commands": ["git init"]},
                            "completion_policy": {"mode": "rules"}
                        }
                    }
                ]
            },
            {
                "difficulty": "medium",
                "required_successful_attempts": 1,
                "min_counted_commands": 1,
                "max_counted_commands": 2,
                "scenario_context": {
                    "schema_version": 3,
                    "story": "A starter file is already present. Your job is only to create repository metadata.",
                    "task": "Make this folder ready for tracking."
                },
                "variants": [
                    {
                        "case_id": "medium-wake-with-notes",
                        "slug_template": "medium-wake-with-notes",
                        "label_template": "Starter notes",
                        "initial_state_template": {
                            **EMPTY_FOLDER_STATE,
                            "working_tree": {"README.md": "Project notes", "plan.md": "First sprint"}
                        },
                        "solution_commands_template": ["git init"],
                        "evaluation_spec_template": {
                            "state_requirements": {
                                "repository_initialized": True,
                                "working_tree_contains": ["README.md", "plan.md"]
                            },
                            "process_requirements": {"required_commands": ["git init"]},
                            "completion_policy": {"mode": "rules"}
                        }
                    }
                ]
            },
            {
                "difficulty": "hard",
                "required_successful_attempts": 1,
                "min_counted_commands": 1,
                "max_counted_commands": 1,
                "scenario_context": {
                    "schema_version": 3,
                    "story": "This folder is still outside repository control.",
                    "task": "Reach the required repository state."
                },
                "variants": [
                    {
                        "case_id": "hard-wake-basecamp",
                        "slug_template": "hard-wake-basecamp",
                        "label_template": "Basecamp",
                        "initial_state_template": EMPTY_FOLDER_STATE,
                        "solution_commands_template": ["git init"],
                        "evaluation_spec_template": {
                            "state_requirements": {"repository_initialized": True},
                            "process_requirements": {"required_commands": ["git init"]},
                            "completion_policy": {"mode": "rules"}
                        }
                    }
                ]
            }
        ]
    },
    {
        "module": "creating-inspecting-repositories",
        "slug": "scout-the-worktree",
        "title": "Scout the Worktree",
        "summary": "Read what changed without touching files.",
        "narrative": "A teammate asks for a quick state check before anyone stages work.",
        "command_topics": ["git status"],
        "levels": [
            {
                "difficulty": "easy",
                "required_successful_attempts": 1,
                "min_counted_commands": 0,
                "max_counted_commands": 2,
                "scenario_context": {
                    "schema_version": 3,
                    "story": "app.py has a working-directory change.",
                    "task": "Inspect what changed without modifying the repository."
                },
                "variants": [
                    {
                        "case_id": "easy-scout-working-change",
                        "slug_template": "easy-scout-working-change",
                        "label_template": "Working change",
                        "initial_state_template": REPO_WITH_WORKING_CHANGE,
                        "solution_commands_template": ["git status"],
                        "evaluation_spec_template": {
                            "state_requirements": {"repository_state_unchanged": True},
                            "process_requirements": {"required_commands": ["git status"]},
                            "completion_policy": {"mode": "rules"}
                        }
                    }
                ]
            },
            {
                "difficulty": "medium",
                "required_successful_attempts": 1,
                "min_counted_commands": 0,
                "max_counted_commands": 1,
                "scenario_context": {
                    "schema_version": 3,
                    "story": "The workspace may contain work that is not ready to save.",
                    "task": "Read the repository state only."
                },
                "variants": [
                    {
                        "case_id": "medium-scout-before-stage",
                        "slug_template": "medium-scout-before-stage",
                        "label_template": "Before staging",
                        "initial_state_template": REPO_WITH_WORKING_CHANGE,
                        "solution_commands_template": ["git status"],
                        "evaluation_spec_template": {
                            "state_requirements": {"repository_state_unchanged": True},
                            "process_requirements": {"required_commands": ["git status"]},
                            "completion_policy": {"mode": "rules"}
                        }
                    }
                ]
            },
            {
                "difficulty": "hard",
                "required_successful_attempts": 1,
                "min_counted_commands": 0,
                "max_counted_commands": 1,
                "scenario_context": {
                    "schema_version": 3,
                    "story": "You need information, not a snapshot.",
                    "task": "Observe the repository and keep the state unchanged."
                },
                "variants": [
                    {
                        "case_id": "hard-scout-no-touch",
                        "slug_template": "hard-scout-no-touch",
                        "label_template": "No touch",
                        "initial_state_template": REPO_WITH_WORKING_CHANGE,
                        "solution_commands_template": ["git status"],
                        "evaluation_spec_template": {
                            "state_requirements": {"repository_state_unchanged": True},
                            "process_requirements": {"required_commands": ["git status"]},
                            "completion_policy": {"mode": "rules"}
                        }
                    }
                ]
            }
        ]
    },
    {
        "module": "creating-inspecting-repositories",
        "slug": "basecamp-sweep",
        "title": "Basecamp Sweep",
        "summary": "Create the repository, then verify its first signal.",
        "narrative": "A fresh project needs to become a repository before the first inspection makes sense.",
        "command_topics": ["git init", "git status"],
        "levels": [
            {
                "difficulty": "easy",
                "required_successful_attempts": 1,
                "min_counted_commands": 1,
                "max_counted_commands": 3,
                "scenario_context": {
                    "schema_version": 3,
                    "story": "You are standing in a plain project folder.",
                    "task": "Make it a repository, then check its state."
                },
                "variants": [
                    {
                        "case_id": "easy-basecamp-init-check",
                        "slug_template": "easy-basecamp-init-check",
                        "label_template": "Init and check",
                        "initial_state_template": EMPTY_FOLDER_STATE,
                        "solution_commands_template": ["git init", "git status"],
                        "evaluation_spec_template": {
                            "state_requirements": {"repository_initialized": True},
                            "process_requirements": {"required_commands": ["git init", "git status"]},
                            "completion_policy": {"mode": "rules"}
                        }
                    }
                ]
            },
            {
                "difficulty": "medium",
                "required_successful_attempts": 1,
                "min_counted_commands": 1,
                "max_counted_commands": 2,
                "scenario_context": {
                    "schema_version": 3,
                    "story": "A plain folder contains starter documentation.",
                    "task": "Reach the initialized-and-checked state."
                },
                "variants": [
                    {
                        "case_id": "medium-basecamp-ready-check",
                        "slug_template": "medium-basecamp-ready-check",
                        "label_template": "Ready check",
                        "initial_state_template": EMPTY_FOLDER_STATE,
                        "solution_commands_template": ["git init", "git status"],
                        "evaluation_spec_template": {
                            "state_requirements": {"repository_initialized": True},
                            "process_requirements": {"required_commands": ["git init", "git status"]},
                            "completion_policy": {"mode": "rules"}
                        }
                    }
                ]
            },
            {
                "difficulty": "hard",
                "required_successful_attempts": 1,
                "min_counted_commands": 1,
                "max_counted_commands": 2,
                "scenario_context": {
                    "schema_version": 3,
                    "story": "The folder is not yet a repository.",
                    "task": "Set it up and confirm the resulting state."
                },
                "variants": [
                    {
                        "case_id": "hard-basecamp-tight-check",
                        "slug_template": "hard-basecamp-tight-check",
                        "label_template": "Tight check",
                        "initial_state_template": EMPTY_FOLDER_STATE,
                        "solution_commands_template": ["git init", "git status"],
                        "evaluation_spec_template": {
                            "state_requirements": {"repository_initialized": True},
                            "process_requirements": {"required_commands": ["git init", "git status"]},
                            "completion_policy": {"mode": "rules"}
                        }
                    }
                ]
            }
        ]
    },
    {
        "module": "branching-switching",
        "slug": "stage-commit-switch",
        "title": "Stage, Commit, Then Switch Branches",
        "summary": "Combine staging, committing, and branch switching in one practical flow.",
        "narrative": "You finished one small change on main and need to preserve it before switching to a feature branch.",
        "command_topics": ["git add", "git commit", "git switch"],
        "levels": [
            {
                "difficulty": "easy",
                "required_successful_attempts": 2,
                "min_counted_commands": 3,
                "max_counted_commands": 6,
                "scenario_context": {
                    "schema_version": 3,
                    "story": "app.py is ready to save before you move to the docs-refresh branch.",
                    "task": "Stage app.py, create the required commit, then switch branches.",
                    "details": [
                        {"label": "File to commit", "value": "app.py"},
                        {"label": "Required commit message", "value": "Update greeting"},
                        {"label": "Final branch", "value": "docs-refresh"},
                    ],
                },
                "variants": [
                    {
                        "case_id": "easy-app-switch",
                        "slug_template": "easy-app-switch",
                        "label_template": "App update",
                        "initial_state_template": {
                            **REPO_WITH_WORKING_CHANGE,
                            "branches": {"main": "c0", "docs-refresh": "c0"},
                        },
                        "solution_commands_template": [
                            "git add app.py",
                            'git commit -m "Update greeting"',
                            "git switch docs-refresh",
                        ],
                        "evaluation_spec_template": {
                            "state_requirements": {
                                "head_branch": "docs-refresh",
                                "latest_commit": {
                                    "branch": "main",
                                    "message_contains": ["Update greeting"],
                                    "contains_paths": ["app.py"],
                                },
                                "staging_empty": True,
                            },
                            "completion_policy": {"mode": "rules"},
                        },
                    }
                ],
            },
            {
                "difficulty": "medium",
                "required_successful_attempts": 2,
                "min_counted_commands": 3,
                "max_counted_commands": 5,
                "scenario_context": {
                    "schema_version": 3,
                    "story": "The app.py change belongs in a snapshot before you move branches.",
                    "task": "Commit app.py, then switch branches.",
                    "details": [
                        {"label": "Required commit message", "value": "Update greeting"},
                        {"label": "Final branch", "value": "docs-refresh"},
                    ],
                },
                "variants": [
                    {
                        "case_id": "medium-selective-switch",
                        "slug_template": "medium-selective-switch",
                        "label_template": "Selective commit",
                        "initial_state_template": {
                            **REPO_WITH_WORKING_CHANGE,
                            "branches": {"main": "c0", "docs-refresh": "c0"},
                            "working_tree": {"app.py": "print('hello world')\n"},
                        },
                        "solution_commands_template": [
                            "git add app.py",
                            'git commit -m "Update greeting"',
                            "git switch docs-refresh",
                        ],
                        "evaluation_spec_template": {
                            "state_requirements": {
                                "head_branch": "docs-refresh",
                                "latest_commit": {
                                    "branch": "main",
                                    "message_contains": ["Update greeting"],
                                    "contains_paths": ["app.py"],
                                },
                            },
                            "completion_policy": {"mode": "rules"},
                        },
                    }
                ],
            },
            {
                "difficulty": "hard",
                "required_successful_attempts": 1,
                "min_counted_commands": 3,
                "max_counted_commands": 4,
                "scenario_context": {
                    "schema_version": 3,
                    "story": "You need a clean branch handoff after a selective commit.",
                    "task": "Reach the requested final repository state.",
                    "details": [
                        {"label": "Required commit message", "value": "Update greeting"},
                        {"label": "Final branch", "value": "docs-refresh"},
                    ],
                },
                "variants": [
                    {
                        "case_id": "hard-selective-switch",
                        "slug_template": "hard-selective-switch",
                        "label_template": "Minimal guidance",
                        "initial_state_template": {
                            **REPO_WITH_WORKING_CHANGE,
                            "branches": {"main": "c0", "docs-refresh": "c0"},
                            "working_tree": {"app.py": "print('hello world')\n"},
                        },
                        "solution_commands_template": [
                            "git add app.py",
                            'git commit -m "Update greeting"',
                            "git switch docs-refresh",
                        ],
                        "evaluation_spec_template": {
                            "state_requirements": {
                                "head_branch": "docs-refresh",
                                "latest_commit": {
                                    "branch": "main",
                                    "message_contains": ["Update greeting"],
                                    "contains_paths": ["app.py"],
                                },
                            },
                            "completion_policy": {"mode": "rules"},
                        },
                    }
                ],
            },
        ],
    }
]
