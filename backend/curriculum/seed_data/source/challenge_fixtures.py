"""Shared hand-authored Challenge repository fixtures.

These histories are source data, not generated targets. Keeping them separate
from the scenario list makes the challenge seed module more reviewable.
"""
from __future__ import annotations

from curriculum.seed_data.spec_helpers import commit, repo

# Shared authored histories -------------------------------------------------------------
CLONE_REMOTE = {
    "branches": {"origin/main": "r2", "origin/starter/login": "r3"},
    "default_branch": "origin/main",
    "commits": [
        commit("r0", "Create starter repository", [], {"README.md": "Git-it starter\n"}),
        commit(
            "r1",
            "Add app shell",
            ["r0"],
            {"README.md": "Git-it starter\n", "src/app.py": "print('hello')\n"},
        ),
        commit(
            "r2",
            "Add testing notes",
            ["r1"],
            {
                "README.md": "Git-it starter\n",
                "src/app.py": "print('hello')\n",
                "TESTING.md": "Run pytest\n",
            },
        ),
        commit(
            "r3",
            "Prepare login starter",
            ["r1"],
            {
                "README.md": "Git-it starter\n",
                "src/app.py": "print('hello')\n",
                "src/login.py": "TODO\n",
            },
        ),
    ],
}

SNAPSHOT_BASE = [
    commit(
        "c0", "Initial app shell", [], {"README.md": "Portal\n", "src/app.py": "print('hello')\n"}
    ),
]
SNAPSHOT_WITH_SECRET = [
    commit(
        "c0",
        "Initial app shell",
        [],
        {"README.md": "Portal\n", "src/app.py": "print('hello')\n", ".env": "SECRET=old\n"},
    ),
]

BRANCH_BASE = [
    commit("c0", "Initial portal", [], {"README.md": "Portal\n"}),
    commit(
        "c1", "Add app shell", ["c0"], {"README.md": "Portal\n", "src/app.py": "print('hello')\n"}
    ),
]
BRANCH_LONG = [
    *BRANCH_BASE,
    commit(
        "c2",
        "Add dashboard",
        ["c1"],
        {
            "README.md": "Portal\n",
            "src/app.py": "print('hello')\n",
            "src/dashboard.py": "cards=[]\n",
        },
    ),
]

MERGE_BASE = [
    commit("c0", "Create portal", [], {"README.md": "Portal\n", "src/app.py": "shell\n"}),
    commit(
        "m1",
        "Polish main shell",
        ["c0"],
        {"README.md": "Portal\n", "src/app.py": "shell\n", "docs/release.md": "draft\n"},
    ),
    commit(
        "f1",
        "Add level menu",
        ["c0"],
        {"README.md": "Portal\n", "src/app.py": "shell\n", "src/menu.py": "levels=[]\n"},
    ),
]
CONFLICT_HISTORY = [
    commit("c0", "Create auth config", [], {"src/auth.js": "timeout=3000\nmode='basic'\n"}),
    commit("m1", "Increase main timeout", ["c0"], {"src/auth.js": "timeout=5000\nmode='basic'\n"}),
    commit("f1", "Tune feature timeout", ["c0"], {"src/auth.js": "timeout=2500\nmode='strict'\n"}),
]
PRECONFLICT = repo(
    commits=CONFLICT_HISTORY,
    branches={"main": "m1", "feature/auth-timeout": "f1"},
    working_tree={
        "src/auth.js": {
            "status": "conflicted",
            "content": "<<<<<<< HEAD\ntimeout=5000\nmode='basic'\n=======\ntimeout=2500\nmode='strict'\n>>>>>>> feature/auth-timeout",
        }
    },
    conflicts=["src/auth.js"],
    merge_parent="f1",
    conflict_details={
        "src/auth.js": {
            "base": "timeout=3000\nmode='basic'\n",
            "ours": "timeout=5000\nmode='basic'\n",
            "theirs": "timeout=2500\nmode='strict'\n",
            "merge_branch": "feature/auth-timeout",
        }
    },
    operation_metadata={"last_merge_branch": "feature/auth-timeout"},
)

RECOVERY_HISTORY = [
    commit("c0", "Initial portal", [], {"README.md": "Portal\n"}),
    commit("c1", "Add app shell", ["c0"], {"README.md": "Portal\n", "src/app.py": "shell\n"}),
    commit(
        "c2",
        "Break login route",
        ["c1"],
        {"README.md": "Portal\n", "src/app.py": "shell\n", "src/login.py": "broken=True\n"},
    ),
]

PATCH_HISTORY = [
    commit("c0", "Base project", [], {"README.md": "base\n"}),
    commit("r1", "Prepare release", ["c0"], {"README.md": "base\n", "release.md": "ready\n"}),
    commit(
        "b1", "Fix login crash", ["c0"], {"README.md": "base\n", "src/login.py": "fixed=True\n"}
    ),
    commit(
        "b2",
        "Add noisy experiment",
        ["b1"],
        {"README.md": "base\n", "src/login.py": "fixed=True\n", "experiment.txt": "skip\n"},
    ),
]

REMOTE_BASE = [
    commit("c0", "Create portal", [], {"README.md": "Portal\n"}),
    commit(
        "c1", "Local app shell", ["c0"], {"README.md": "Portal\n", "src/app.py": "local shell\n"}
    ),
]
REMOTE_FIXTURE_AHEAD = {
    "branches": {"origin/main": "r2"},
    "default_branch": "origin/main",
    "commits": [
        commit(
            "r2",
            "Remote review note",
            ["c1"],
            {"README.md": "Portal\n", "src/app.py": "local shell\n", "review.md": "approved\n"},
        ),
    ],
}
REMOTE_DIVERGED = [
    commit("c0", "Create portal", [], {"README.md": "Portal\n"}),
    commit("c1", "Add app shell", ["c0"], {"README.md": "Portal\n", "src/app.py": "local shell\n"}),
    commit(
        "l2",
        "Local release note",
        ["c1"],
        {"README.md": "Portal\n", "src/app.py": "local shell\n", "release.md": "local\n"},
    ),
    commit(
        "r2",
        "Remote review note",
        ["c1"],
        {"README.md": "Portal\n", "src/app.py": "local shell\n", "review.md": "approved\n"},
    ),
]

