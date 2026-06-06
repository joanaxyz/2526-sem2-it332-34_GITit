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
        "summary": "Create Git metadata for the folder you are already in.",
        "required_successful_attempts": 2,
        "min_counted_commands": 1,
        "max_counted_commands": 3,
        "student_context": {
            "schema_version": 2,
            "brief": {
                "story": "You opened a project folder that has files but no Git repository yet.",
                "task": "Initialize this folder as a Git repository.",
            },
            "repository": {"current_state": ["The folder is not a Git repository yet."]},
            "objective": {"outcome": "The current folder should be initialized as a Git repository."},
        },
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
        "summary": "Use status to inspect staged and unstaged work without changing the repository.",
        "required_successful_attempts": 2,
        "min_counted_commands": 0,
        "max_counted_commands": 2,
        "student_context": {
            "schema_version": 2,
            "brief": {
                "story": "A teammate asks what is currently changed in the repository.",
                "task": "Inspect repository status without changing anything.",
            },
            "repository": {"current_state": ["app.py has an unstaged working-directory change."]},
            "objective": {"outcome": "The repository state should be unchanged after inspection."},
        },
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
        "summary": "Stage a single requested path and leave unrelated work alone.",
        "required_successful_attempts": 3,
        "min_counted_commands": 1,
        "max_counted_commands": 3,
        "student_context": {
            "schema_version": 2,
            "brief": {
                "story": "Only app.py is ready for the next snapshot.",
                "task": "Stage app.py.",
            },
            "repository": {"current_state": ["app.py is modified in the working directory."]},
            "objective": {
                "outcome": "app.py should be in the staging area.",
                "required_details": [{"label": "File to stage", "value": "app.py"}],
            },
        },
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
        "summary": "Create a snapshot from the staging area with the requested message text.",
        "required_successful_attempts": 3,
        "min_counted_commands": 1,
        "max_counted_commands": 3,
        "student_context": {
            "schema_version": 2,
            "brief": {
                "story": "The right file is already staged.",
                "task": "Create the requested commit.",
            },
            "repository": {"current_state": ["app.py is staged."]},
            "objective": {
                "outcome": "The main branch should gain a commit for app.py.",
                "required_details": [
                    {"label": "Required message text", "value": "Update greeting"},
                    {"label": "Committed file", "value": "app.py"},
                ],
            },
        },
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
]
