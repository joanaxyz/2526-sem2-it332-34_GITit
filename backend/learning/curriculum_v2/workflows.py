from learning.curriculum_v2.drills import REPO_WITH_WORKING_CHANGE

WORKFLOW_SCENARIOS = [
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
