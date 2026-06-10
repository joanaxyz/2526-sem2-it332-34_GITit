EMPTY_FOLDER_STATE = {
    "repository_initialized": False,
    "commits": [],
    "branches": {},
    "head": {"type": "branch", "name": "main"},
    "working_tree": {"README.md": "Project notes"},
    "staging": {},
    "conflicts": [],
}

REPO_WITH_WORKING_CHANGE = {
    "repository_initialized": True,
    "commits": [
        {
            "id": "c0",
            "message": "Initial project",
            "parents": [],
            "tree": {"app.py": "print('hello')\n", "README.md": "Project notes"},
            "changes": {"app.py": {"change_type": "added"}, "README.md": {"change_type": "added"}},
            "files": {"app.py": "added", "README.md": "added"},
        }
    ],
    "branches": {"main": "c0"},
    "head": {"type": "branch", "name": "main"},
    "working_tree": {"app.py": "print('hello world')\n"},
    "staging": {},
    "conflicts": [],
}

REPO_WITH_STAGED_CHANGE = {
    **REPO_WITH_WORKING_CHANGE,
    "working_tree": {},
    "staging": {"app.py": "print('hello world')\n"},
}

COMMAND_DRILLS = [
    {
        "usage": "git-init/current-directory",
        "slug": "init-current-folder",
        "title": "Initialize the current folder",
        "required_successful_attempts": 2,
        "min_counted_commands": 1,
        "max_counted_commands": 3,
        "scenario_context": {
            "schema_version": 3,
            "story": "You opened a project folder that has files but no Git repository yet.",
            "task": "Initialize this folder as a Git repository.",
        },
        "objective_checks": [
            {
                "label": "The current folder is a Git repository.",
                "requirement": {"repository_initialized": True},
            },
        ],
        "variants": [
            {
                "case_id": "init-current-readme",
                "slug_template": "init-current-readme",
                "label_template": "Project folder",
                "initial_state_template": EMPTY_FOLDER_STATE,
                "solution_commands_template": ["git init"],
                "evaluation_spec_template": {
                    "state_requirements": {"repository_initialized": True},
                    "process_requirements": {"required_commands": ["git init"]},
                    "completion_policy": {"mode": "rules"},
                },
            }
        ],
    },
    {
        "usage": "git-status/short-status",
        "slug": "read-status",
        "title": "Read repository status",
        "required_successful_attempts": 2,
        "min_counted_commands": 0,
        "max_counted_commands": 2,
        "scenario_context": {
            "schema_version": 3,
            "story": "A teammate asks what is currently changed in the repository.",
            "task": "Inspect repository status without changing anything.",
        },
        "objective_checks": [
            {
                "label": "The repository is unchanged while you inspect it.",
                "requirement": {"repository_state_unchanged": True},
            },
        ],
        "variants": [
            {
                "case_id": "status-working-change",
                "slug_template": "status-working-change",
                "label_template": "Working change",
                "initial_state_template": REPO_WITH_WORKING_CHANGE,
                "solution_commands_template": ["git status"],
                "evaluation_spec_template": {
                    "state_requirements": {"repository_state_unchanged": True},
                    "process_requirements": {"required_commands": ["git status"]},
                    "completion_policy": {"mode": "rules"},
                },
            }
        ],
    },
    {
        "usage": "git-add/file",
        "slug": "stage-one-file",
        "title": "Stage one file",
        "required_successful_attempts": 3,
        "min_counted_commands": 1,
        "max_counted_commands": 3,
        "scenario_context": {
            "schema_version": 3,
            "story": "Only app.py is ready for the next snapshot.",
            "task": "Stage app.py.",
            "details": [{"label": "File to stage", "value": "app.py"}],
        },
        "objective_checks": [
            {
                "label": "app.py is in the staging area.",
                "requirement": {"staging_contains": ["app.py"]},
            },
        ],
        "variants": [
            {
                "case_id": "stage-app-py",
                "slug_template": "stage-app-py",
                "label_template": "Stage app.py",
                "initial_state_template": REPO_WITH_WORKING_CHANGE,
                "solution_commands_template": ["git add app.py"],
                "evaluation_spec_template": {
                    "state_requirements": {"staging_contains": ["app.py"]},
                    "process_requirements": {"required_commands": ["git add"]},
                    "completion_policy": {"mode": "rules"},
                },
            }
        ],
    },
    {
        "usage": "git-commit/message",
        "slug": "commit-staged-file",
        "title": "Commit staged work",
        "required_successful_attempts": 3,
        "min_counted_commands": 1,
        "max_counted_commands": 3,
        "scenario_context": {
            "schema_version": 3,
            "story": "The right file is already staged.",
            "task": "Create the requested commit.",
            "details": [
                {"label": "Required message text", "value": "Update greeting"},
                {"label": "Committed file", "value": "app.py"},
            ],
        },
        "objective_checks": [
            {
                "label": "main has a new commit containing app.py.",
                "requirement": {
                    "latest_commit": {
                        "branch": "main",
                        "contains_paths": ["app.py"],
                        "message_contains": ["Update greeting"],
                    }
                },
            },
            {
                "label": "The staging area is empty afterward.",
                "requirement": {"staging_empty": True},
            },
        ],
        "variants": [
            {
                "case_id": "commit-greeting",
                "slug_template": "commit-greeting",
                "label_template": "Commit greeting update",
                "initial_state_template": REPO_WITH_STAGED_CHANGE,
                "solution_commands_template": ['git commit -m "Update greeting"'],
                "evaluation_spec_template": {
                    "state_requirements": {
                        "latest_commit": {
                            "branch": "main",
                            "message_contains": ["Update greeting"],
                            "contains_paths": ["app.py"],
                        },
                        "staging_empty": True,
                    },
                    "process_requirements": {"required_commands": ["git commit"]},
                    "completion_policy": {"mode": "rules"},
                },
            }
        ],
    },
    {
        "usage": "git-switch/existing",
        "slug": "switch-to-existing-branch",
        "title": "Switch to an existing branch",
        "required_successful_attempts": 2,
        "min_counted_commands": 1,
        "max_counted_commands": 3,
        "scenario_context": {
            "schema_version": 3,
            "story": "Your teammate already created a docs-refresh branch for documentation work.",
            "task": "Move your workspace onto docs-refresh.",
            "details": [{"label": "Final branch", "value": "docs-refresh"}],
        },
        "objective_checks": [
            {
                "label": "HEAD is on the docs-refresh branch.",
                "requirement": {"head_branch": "docs-refresh"},
            },
        ],
        "variants": [
            {
                "case_id": "switch-docs-refresh",
                "slug_template": "switch-docs-refresh",
                "label_template": "Branch handoff",
                "initial_state_template": {
                    "repository_initialized": True,
                    "commits": [
                        {
                            "id": "c0",
                            "message": "Initial project",
                            "parents": [],
                            "tree": {"README.md": "Project notes"},
                            "changes": {"README.md": {"change_type": "added"}},
                            "files": {"README.md": "added"},
                        }
                    ],
                    "branches": {"main": "c0", "docs-refresh": "c0"},
                    "head": {"type": "branch", "name": "main"},
                    "working_tree": {},
                    "staging": {},
                    "conflicts": [],
                },
                "solution_commands_template": ["git switch docs-refresh"],
                "evaluation_spec_template": {
                    "state_requirements": {
                        "head_branch": "docs-refresh",
                        "staging_empty": True,
                    },
                    "process_requirements": {"required_commands": ["git switch"]},
                    "completion_policy": {"mode": "rules"},
                },
            }
        ],
    },
]
