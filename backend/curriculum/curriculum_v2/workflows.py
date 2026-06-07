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
                "narrative": "Prepare the folder so the simulator recognizes it as a repository.",
                "task_prompt": "Initialize the current project folder.",
                "required_successful_attempts": 1,
                "min_counted_commands": 1,
                "max_counted_commands": 3,
                "student_context": {
                    "schema_version": 2,
                    "brief": {
                        "story": "You opened a project folder called field-notes. It has files, but no repository metadata.",
                        "task": "Turn this folder into a repository."
                    },
                    "repository": {"current_state": ["README.md exists in a plain folder.", "No commits exist yet."]},
                    "objective": {"outcome": "The current folder should become a repository."}
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
                "narrative": "Prepare a folder that already contains starter notes and keep the workspace untouched.",
                "task_prompt": "Initialize the project folder without editing files.",
                "required_successful_attempts": 1,
                "min_counted_commands": 1,
                "max_counted_commands": 2,
                "student_context": {
                    "schema_version": 2,
                    "brief": {
                        "story": "A starter file is already present. Your job is only to create repository metadata.",
                        "task": "Make this folder ready for tracking."
                    },
                    "repository": {"current_state": ["README.md exists.", "The folder is not a repository yet."]},
                    "objective": {"outcome": "The folder should be initialized, with files still in place."}
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
                "narrative": "Reach the same final state with minimal guidance.",
                "task_prompt": "Prepare the folder for version control.",
                "required_successful_attempts": 1,
                "min_counted_commands": 1,
                "max_counted_commands": 1,
                "student_context": {
                    "schema_version": 2,
                    "brief": {
                        "story": "This folder is still outside repository control.",
                        "task": "Reach the required repository state."
                    },
                    "repository": {"current_state": ["A plain project folder contains README.md."]},
                    "objective": {"outcome": "The folder should be recognized as a repository."}
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
                "narrative": "Inspect the current state and leave everything as-is.",
                "task_prompt": "Inspect the repository state.",
                "required_successful_attempts": 1,
                "min_counted_commands": 0,
                "max_counted_commands": 2,
                "student_context": {
                    "schema_version": 2,
                    "brief": {
                        "story": "app.py has a working-directory change.",
                        "task": "Inspect what changed without modifying the repository."
                    },
                    "repository": {"current_state": ["main has one unstaged change.", "Nothing is staged."]},
                    "objective": {"outcome": "The repository should be unchanged after inspection."}
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
                "narrative": "Inspect the state before deciding what belongs in the next snapshot.",
                "task_prompt": "Check the repository state without changing it.",
                "required_successful_attempts": 1,
                "min_counted_commands": 0,
                "max_counted_commands": 1,
                "student_context": {
                    "schema_version": 2,
                    "brief": {
                        "story": "The workspace may contain work that is not ready to save.",
                        "task": "Read the repository state only."
                    },
                    "repository": {"current_state": ["app.py is modified in the working directory."]},
                    "objective": {"outcome": "The repository should remain exactly as it started."}
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
                "narrative": "Reach the observation goal with no state changes.",
                "task_prompt": "Inspect the current repository.",
                "required_successful_attempts": 1,
                "min_counted_commands": 0,
                "max_counted_commands": 1,
                "student_context": {
                    "schema_version": 2,
                    "brief": {
                        "story": "You need information, not a snapshot.",
                        "task": "Observe the repository and keep the state unchanged."
                    },
                    "repository": {"current_state": ["main has an unstaged file change."]},
                    "objective": {"outcome": "The starting repository state should still match the final state."}
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
                "narrative": "Prepare the folder and verify the state afterward.",
                "task_prompt": "Initialize the folder, then inspect it.",
                "required_successful_attempts": 1,
                "min_counted_commands": 1,
                "max_counted_commands": 3,
                "student_context": {
                    "schema_version": 2,
                    "brief": {
                        "story": "You are standing in a plain project folder.",
                        "task": "Make it a repository, then check its state."
                    },
                    "repository": {"current_state": ["README.md exists.", "No repository metadata exists yet."]},
                    "objective": {"outcome": "The folder should become a repository and be inspected once."}
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
                "narrative": "Prepare the project and confirm what the repository reports.",
                "task_prompt": "Initialize and inspect the folder.",
                "required_successful_attempts": 1,
                "min_counted_commands": 1,
                "max_counted_commands": 2,
                "student_context": {
                    "schema_version": 2,
                    "brief": {
                        "story": "A plain folder contains starter documentation.",
                        "task": "Reach the initialized-and-checked state."
                    },
                    "repository": {"current_state": ["The folder contains README.md but is not initialized."]},
                    "objective": {"outcome": "The folder should be initialized, and one inspection should have happened."}
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
                "narrative": "Complete the setup and inspection route with a tight command budget.",
                "task_prompt": "Reach the requested setup state.",
                "required_successful_attempts": 1,
                "min_counted_commands": 1,
                "max_counted_commands": 2,
                "student_context": {
                    "schema_version": 2,
                    "brief": {
                        "story": "The folder is not yet a repository.",
                        "task": "Set it up and confirm the resulting state."
                    },
                    "repository": {"current_state": ["README.md exists in a plain folder."]},
                    "objective": {"outcome": "The folder should be initialized, with one state inspection completed."}
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
                "narrative": "Stage the ready file, commit it with the requested message text, then switch to docs-refresh.",
                "task_prompt": "Save app.py on main and move to docs-refresh.",
                "required_successful_attempts": 2,
                "min_counted_commands": 3,
                "max_counted_commands": 6,
                "student_context": {
                    "schema_version": 2,
                    "brief": {
                        "story": "app.py is ready to save before you move to the docs-refresh branch.",
                        "task": "Stage app.py, create the required commit, then switch branches.",
                    },
                    "repository": {"current_state": ["app.py is modified on main.", "docs-refresh already exists."]},
                    "objective": {
                        "outcome": "main should contain the new app.py commit and HEAD should end on docs-refresh.",
                        "required_details": [
                            {"label": "File to commit", "value": "app.py"},
                            {"label": "Required message text", "value": "Update greeting"},
                            {"label": "Final branch", "value": "docs-refresh"},
                        ],
                    },
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
                "narrative": "Commit the requested file before switching branches.",
                "task_prompt": "Save app.py, then switch to docs-refresh.",
                "required_successful_attempts": 2,
                "min_counted_commands": 3,
                "max_counted_commands": 5,
                "student_context": {
                    "schema_version": 2,
                    "brief": {
                        "story": "The app.py change belongs in a snapshot before you move branches.",
                        "task": "Commit app.py, then switch branches.",
                    },
                    "repository": {"current_state": ["app.py is modified on main."]},
                    "objective": {
                        "outcome": "main should gain an app.py commit and HEAD should end on docs-refresh.",
                        "required_details": [
                            {"label": "File to commit", "value": "app.py"},
                            {"label": "Final branch", "value": "docs-refresh"},
                        ],
                    },
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
                "narrative": "Reach the final repository state with minimal feedback.",
                "task_prompt": "Commit app.py on main and finish on docs-refresh.",
                "required_successful_attempts": 1,
                "min_counted_commands": 3,
                "max_counted_commands": 4,
                "student_context": {
                    "schema_version": 2,
                    "brief": {
                        "story": "You need a clean branch handoff after a selective commit.",
                        "task": "Reach the requested final repository state.",
                    },
                    "repository": {"current_state": ["app.py is modified on main."]},
                    "objective": {
                        "outcome": "Save app.py on main and end on docs-refresh.",
                        "required_details": [
                            {"label": "Final branch", "value": "docs-refresh"},
                            {"label": "Committed file", "value": "app.py"},
                        ],
                    },
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
