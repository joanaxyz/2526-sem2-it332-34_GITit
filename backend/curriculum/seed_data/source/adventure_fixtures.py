"""Shared hand-authored Adventure repository fixtures.

These constants are source data reused across adventure waves.
"""
from __future__ import annotations

from curriculum.seed_data.spec_helpers import commit

BASE_TREE = {
    "README.md": "Project notes",
    "src/app.py": "print('hello')\n",
}
BASE = [commit("c0", "Initial project", [], BASE_TREE)]
TWO_COMMITS = [
    commit("c0", "Initial project", [], {"README.md": "Project notes"}),
    commit("c1", "Add app shell", ["c0"], BASE_TREE),
]
THREE_COMMITS = [
    *TWO_COMMITS,
    commit("c2", "Add login copy", ["c1"], {**BASE_TREE, "src/login.py": "title='Login'\n"}),
]

REMOTE_FIXTURE_MAIN = {
    "branches": {"origin/main": "r2"},
    "default_branch": "origin/main",
    "commits": [
        commit("r1", "Create remote starter", [], {"README.md": "remote v1"}),
        commit(
            "r2", "Add starter app", ["r1"], {"README.md": "remote v1", "src/app.py": "remote app"}
        ),
    ],
}

REMOTE_FIXTURE_STARTER = {
    "branches": {"origin/main": "r10", "origin/starter": "r11"},
    "default_branch": "origin/main",
    "commits": [
        commit("r10", "Create lab base", [], {"README.md": "base"}),
        commit(
            "r11",
            "Prepare starter branch",
            ["r10"],
            {"README.md": "base", "starter.md": "exercise"},
        ),
    ],
}

REMOTE_FIXTURE_HISTORY = {
    "branches": {"origin/main": "r22"},
    "default_branch": "origin/main",
    "commits": [
        commit("r20", "Create portal", [], {"README.md": "v1"}),
        commit("r21", "Add page", ["r20"], {"README.md": "v1", "page.md": "v1"}),
        commit("r22", "Polish page", ["r21"], {"README.md": "v2", "page.md": "v2"}),
    ],
}
