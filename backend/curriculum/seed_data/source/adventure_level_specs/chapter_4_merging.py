"""Chapter 4 authored adventure levels."""

from __future__ import annotations

from .common import *  # noqa: F403

MERGE_BASE = [
    commit("c0", "Initial project", [], {"README.md": "base", "src/app.py": "base"}),
    commit("c1", "Update main shell", ["c0"], {"README.md": "base", "src/app.py": "main shell"}),
    commit(
        "c2",
        "Add profile feature",
        ["c0"],
        {"README.md": "base", "src/app.py": "base", "src/profile.py": "profile"},
    ),
]

CONFLICT_COMMITS = [
    commit("c0", "Initial project", [], {"src/auth.js": "timeout=1000", "README.md": "base"}),
    commit(
        "c1",
        "Increase timeout on main",
        ["c0"],
        {"src/auth.js": "timeout=5000", "README.md": "base"},
    ),
    commit(
        "c2",
        "Tune timeout on feature",
        ["c0"],
        {"src/auth.js": "timeout=2500", "README.md": "base"},
    ),
]

CONFLICT_STATE = repo(
    commits=CONFLICT_COMMITS,
    branches={"main": "c1", "feature/auth-timeout": "c2"},
    conflict_on_merge=True,
    conflict_files=["src/auth.js"],
)

PRECONFLICT = repo(
    commits=CONFLICT_COMMITS,
    branches={"main": "c1", "feature/auth-timeout": "c2"},
    working_tree={
        "src/auth.js": {
            "status": "conflicted",
            "content": "<<<<<<< HEAD\ntimeout=5000\n=======\ntimeout=2500\n>>>>>>> feature/auth-timeout",
        }
    },
    conflicts=["src/auth.js"],
    merge_parent="c2",
    conflict_details={
        "src/auth.js": {
            "base": "timeout=1000",
            "ours": "timeout=5000",
            "theirs": "timeout=2500",
            "merge_branch": "feature/auth-timeout",
        }
    },
)

RESOLVED_MERGE = repo(
    commits=CONFLICT_COMMITS,
    branches={"main": "c1", "feature/auth-timeout": "c2"},
    staging={"src/auth.js": {"status": "modified", "content": "timeout=2500"}},
    conflicts=[],
    merge_parent="c2",
    conflict_details={},
    operation_metadata={"last_merge_branch": "feature/auth-timeout"},
)

LEVELS = [
    # Chapter 4 - Merging and Conflict Resolution
    q(
        "git-merge/branch",
        "merge-fast-forward-branch",
        "Merge a branch that can fast-forward",
        "A feature branch is ahead of main and main has not moved since it split.",
        "Integrate the feature branch into the current branch cleanly.",
        [
            v(
                "merge-ff-profile",
                "Profile feature",
                repo(commits=MERGE_BASE, branches={"main": "c0", "feature/profile": "c2"}),
                ["git merge feature/profile"],
                ev(
                    {
                        "branches_equal": [["main", "feature/profile"]],
                        "rules": [meta_equals("last_merge_fast_forward", True)],
                    },
                    required=["git merge"],
                ),
                details=[{"label": "Branch to merge", "value": "feature/profile"}],
            ),
            v(
                "merge-ff-maincopy",
                "Copy feature",
                repo(
                    commits=[
                        commit("c0", "Initial", [], {"README.md": "base"}),
                        commit("c3", "Improve copy", ["c0"], {"README.md": "better"}),
                    ],
                    branches={"main": "c0", "feature/copy": "c3"},
                ),
                ["git merge feature/copy"],
                ev(
                    {
                        "branches_equal": [["main", "feature/copy"]],
                        "rules": [meta_equals("last_merge_fast_forward", True)],
                    },
                    required=["git merge"],
                ),
                details=[{"label": "Branch to merge", "value": "feature/copy"}],
            ),
        ],
        checks=[
            {
                "label": "The branch was fast-forward merged into the current branch.",
                "requirement": {"rules": [meta_equals("last_merge_fast_forward", True)]},
            }
        ],
        workflow=True,
    ),
    q(
        "git-merge/no-ff",
        "merge-with-merge-commit",
        "Force a merge commit",
        "The branch can technically fast-forward, but the team wants a visible merge checkpoint.",
        "Integrate the branch while preserving a merge commit in history.",
        [
            v(
                "merge-noff-profile",
                "Profile merge checkpoint",
                repo(commits=MERGE_BASE, branches={"main": "c0", "feature/profile": "c2"}),
                ["git merge --no-ff feature/profile"],
                ev(
                    {
                        "rules": [
                            {"type": "commit_is_merge", "branch": "main"},
                            meta_equals("last_merge_no_ff", True),
                        ]
                    },
                    required=["git merge --no-ff"],
                ),
                details=[{"label": "Branch to merge", "value": "feature/profile"}],
            ),
            v(
                "merge-noff-copy",
                "Copy merge checkpoint",
                repo(
                    commits=[
                        commit("c0", "Initial", [], {"README.md": "base"}),
                        commit("c3", "Improve copy", ["c0"], {"README.md": "better"}),
                    ],
                    branches={"main": "c0", "feature/copy": "c3"},
                ),
                ["git merge --no-ff feature/copy"],
                ev(
                    {
                        "rules": [
                            {"type": "commit_is_merge", "branch": "main"},
                            meta_equals("last_merge_no_ff", True),
                        ]
                    },
                    required=["git merge --no-ff"],
                ),
                details=[{"label": "Branch to merge", "value": "feature/copy"}],
            ),
        ],
        checks=[
            {
                "label": "The latest commit on main is a merge commit.",
                "requirement": {"rules": [{"type": "commit_is_merge", "branch": "main"}]},
            }
        ],
        prerequisites=["merge-fast-forward-branch"],
        workflow=True,
    ),
    q(
        "git-merge/abort",
        "abort-conflicted-merge",
        "Abort a conflicted merge",
        "A merge produced conflicts, and the safest decision is to return to the clean pre-merge state.",
        "Cancel the in-progress merge.",
        [
            v(
                "merge-abort-auth",
                "Abort auth conflict",
                PRECONFLICT,
                ["git merge --abort"],
                ev(
                    {
                        "conflict_free": True,
                        "working_tree_clean": True,
                        "staging_empty": True,
                        "rules": [meta_equals("last_merge_aborted", True)],
                    },
                    required=["git merge --abort"],
                ),
            ),
            v(
                "merge-abort-copy",
                "Abort copy conflict",
                {
                    **copy.deepcopy(PRECONFLICT),
                    "conflicts": ["README.md"],
                    "working_tree": {"README.md": {"status": "conflicted", "content": "markers"}},
                    "conflict_details": {"README.md": {"ours": "main", "theirs": "feature"}},
                },
                ["git merge --abort"],
                ev(
                    {
                        "conflict_free": True,
                        "working_tree_clean": True,
                        "staging_empty": True,
                        "rules": [meta_equals("last_merge_aborted", True)],
                    },
                    required=["git merge --abort"],
                ),
            ),
        ],
        checks=[
            {
                "label": "No conflict or staged merge work remains.",
                "requirement": {
                    "conflict_free": True,
                    "working_tree_clean": True,
                    "staging_empty": True,
                },
            }
        ],
        prerequisites=["merge-fast-forward-branch"],
        workflow=True,
    ),
    q(
        "git-checkout-conflict/ours",
        "choose-our-conflict-side",
        "Choose our side of a conflict",
        "A conflicted file should keep the current branch version before the resolution is staged.",
        "Replace the conflicted file with the current branch side.",
        [
            v(
                "checkout-ours-auth",
                "Keep main timeout",
                PRECONFLICT,
                ["git checkout --ours src/auth.js"],
                ev(
                    {
                        "conflicts_contain_paths": ["src/auth.js"],
                        "working_tree_contains": ["src/auth.js"],
                        "rules": [
                            {
                                "type": "working_tree_contains_tokens",
                                "path": "src/auth.js",
                                "tokens": ["timeout=5000"],
                            }
                        ],
                    },
                    required=["git checkout --ours"],
                ),
            ),
            v(
                "checkout-ours-copy",
                "Keep main copy",
                {
                    **copy.deepcopy(PRECONFLICT),
                    "conflict_details": {
                        "src/auth.js": {"ours": "MAIN COPY", "theirs": "FEATURE COPY"}
                    },
                    "working_tree": {"src/auth.js": {"status": "conflicted", "content": "markers"}},
                },
                ["git checkout --ours src/auth.js"],
                ev(
                    {
                        "conflicts_contain_paths": ["src/auth.js"],
                        "rules": [
                            {
                                "type": "working_tree_contains_tokens",
                                "path": "src/auth.js",
                                "tokens": ["MAIN COPY"],
                            }
                        ],
                    },
                    required=["git checkout --ours"],
                ),
            ),
        ],
        checks=[
            {
                "label": "The conflicted file now holds the current branch side.",
                "requirement": {"rules": [meta_equals("last_checkout_conflict_side", "ours")]},
            }
        ],
        prerequisites=["merge-fast-forward-branch"],
        workflow=True,
    ),
    q(
        "git-checkout-conflict/theirs",
        "choose-their-conflict-side",
        "Choose their side of a conflict",
        "A conflicted file should take the incoming branch version before the resolution is staged.",
        "Replace the conflicted file with the incoming branch side.",
        [
            v(
                "checkout-theirs-auth",
                "Take feature timeout",
                PRECONFLICT,
                ["git checkout --theirs src/auth.js"],
                ev(
                    {
                        "conflicts_contain_paths": ["src/auth.js"],
                        "working_tree_contains": ["src/auth.js"],
                        "rules": [
                            {
                                "type": "working_tree_contains_tokens",
                                "path": "src/auth.js",
                                "tokens": ["timeout=2500"],
                            }
                        ],
                    },
                    required=["git checkout --theirs"],
                ),
            ),
            v(
                "checkout-theirs-copy",
                "Take feature copy",
                {
                    **copy.deepcopy(PRECONFLICT),
                    "conflict_details": {
                        "src/auth.js": {"ours": "MAIN COPY", "theirs": "FEATURE COPY"}
                    },
                    "working_tree": {"src/auth.js": {"status": "conflicted", "content": "markers"}},
                },
                ["git checkout --theirs src/auth.js"],
                ev(
                    {
                        "conflicts_contain_paths": ["src/auth.js"],
                        "rules": [
                            {
                                "type": "working_tree_contains_tokens",
                                "path": "src/auth.js",
                                "tokens": ["FEATURE COPY"],
                            }
                        ],
                    },
                    required=["git checkout --theirs"],
                ),
            ),
        ],
        checks=[
            {
                "label": "The conflicted file now holds the incoming branch side.",
                "requirement": {"rules": [meta_equals("last_checkout_conflict_side", "theirs")]},
            }
        ],
        prerequisites=["merge-fast-forward-branch"],
        workflow=True,
    ),
    q(
        "git-merge/continue",
        "continue-resolved-merge",
        "Finish a resolved merge",
        "The conflict has already been resolved and staged, so the merge can now be completed.",
        "Finish the in-progress merge.",
        [
            v(
                "merge-continue-auth",
                "Continue auth merge",
                RESOLVED_MERGE,
                ["git merge --continue"],
                ev(
                    {
                        "conflict_free": True,
                        "staging_empty": True,
                        "rules": [{"type": "commit_is_merge", "branch": "main"}],
                    },
                    required=["git merge --continue"],
                ),
            ),
            v(
                "merge-continue-copy",
                "Continue copy merge",
                {
                    **copy.deepcopy(RESOLVED_MERGE),
                    "staging": {"README.md": {"status": "modified", "content": "resolved"}},
                },
                ["git merge --continue"],
                ev(
                    {
                        "conflict_free": True,
                        "staging_empty": True,
                        "rules": [{"type": "commit_is_merge", "branch": "main"}],
                    },
                    required=["git merge --continue"],
                ),
            ),
        ],
        checks=[
            {
                "label": "The merge is complete and no staged conflict work remains.",
                "requirement": {
                    "conflict_free": True,
                    "staging_empty": True,
                    "rules": [{"type": "commit_is_merge", "branch": "main"}],
                },
            }
        ],
        prerequisites=["choose-our-conflict-side", "choose-their-conflict-side"],
        workflow=True,
    ),
]
