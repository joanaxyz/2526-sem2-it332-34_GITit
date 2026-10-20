"""Module 1 wave scenarios: repository foundations (levels 1.1-1.6)."""

from __future__ import annotations

from typing import Any

from curriculum.seed_data.source.scenario_fixtures.shapes import (
    amended,
    commit,
    hunks,
    modified,
    remote_fixture,
    repo,
    tip,
    untracked,
)


def _init_nested(*, root: str, branch: str, siblings: list[str]) -> dict[str, Any]:
    """A workspace of several projects; only ``root`` becomes a repository."""
    files = {f"{root}/README.md": f"{root}-readme", f"{root}/app.py": f"{root}-app"}
    files.update({f"{sibling}/README.md": f"{sibling}-readme" for sibling in siblings})
    return {
        "initial_state": repo(
            initialized=False,
            working_tree={path: untracked(content) for path, content in files.items()},
        ),
        "state_requirements": {
            "repository_initialized": True,
            "repository_root": root,
            "head_branch": branch,
            "staging_empty": True,
            "working_tree_contains": sorted(files),
            "rules": [{"type": "commit_count_equals", "count": 0}],
        },
    }


def _shallow_clone(
    *, url: str, project: str, destination: str, depth: int, messages: list[str]
) -> dict[str, Any]:
    commits: list[dict] = []
    tree: dict[str, str] = {}
    for index, message in enumerate(messages, start=1):
        tree = {**tree, f"{project}/part-{index}.md": f"{project}-part-{index}"}
        parents = [f"r{index - 1}"] if index > 1 else []
        commits.append(commit(f"r{index}", message, parents, dict(tree)))
    tip_id = commits[-1]["id"]
    return {
        "initial_state": repo(
            initialized=False,
            remote_fixtures=remote_fixture(url, commits, tip_id),
        ),
        "state_requirements": {
            "repository_initialized": True,
            "head_branch": "main",
            "remote_exists": ["origin"],
            "remote_url_matches": {"origin": url},
            "remote_branch_points_to": {"origin/main": tip_id},
            "branch_points_to": {"main": tip_id},
            "working_tree_clean": True,
            "rules": [
                {"type": "commit_count_equals", "count": depth},
            ],
            "repository_root": destination,
        },
    }


def _first_snapshot(*, files: dict[str, str], private: str, message: str) -> dict[str, Any]:
    return {
        "initial_state": repo(
            initialized=False,
            working_tree={
                **{path: untracked(content) for path, content in files.items()},
                private: untracked(f"{private}-private"),
            },
        ),
        "state_requirements": {
            "repository_initialized": True,
            "head_branch": "main",
            "staging_empty": True,
            "latest_commit": {
                "branch": "main",
                "message_contains": [message],
                "contains_paths": sorted(files),
                "excludes_paths": [private],
            },
            "working_tree_contains": [private],
            "rules": [
                {"type": "commit_count_equals", "count": 1},
                tip("main", message_equals=message, tree_excludes=[private]),
            ],
        },
    }


def _hunk_plus_file(
    *,
    path: str,
    fix: str,
    leftover: str,
    extra_path: str,
    extra: Any,
    extra_committed: str | None,
    message: str,
) -> dict[str, Any]:
    tree = {"README.md": "readme-v1", path: f"{path}-v1"}
    if extra_committed is not None:
        tree[extra_path] = extra_committed
    return {
        "initial_state": repo(
            commits=[commit("c1", "Initial project snapshot", [], tree)],
            branches={"main": "c1"},
            working_tree={path: hunks(fix, leftover), extra_path: extra},
            partial_hunks={path: {"target_hunks": [fix], "leftover_hunks": [leftover]}},
        ),
        "state_requirements": {
            "head_branch": "main",
            "staging_empty": True,
            "latest_commit": {
                "branch": "main",
                "message_contains": [message],
                "contains_paths": [path, extra_path],
            },
            "rules": [
                {"type": "commit_count_equals", "count": 2},
                tip(
                    "main",
                    message_equals=message,
                    changes_include_tokens=[fix],
                    changes_exclude_tokens=[leftover],
                ),
                {"type": "partial_hunks_left_in_working_tree", "paths": {path: [leftover]}},
            ],
        },
    }


def _split_commits(
    *, path: str, first: tuple[str, str], second: tuple[str, str]
) -> dict[str, Any]:
    (first_hunk, first_message), (second_hunk, second_message) = first, second
    return {
        "initial_state": repo(
            commits=[
                commit(
                    "c1",
                    "Initial project snapshot",
                    [],
                    {"README.md": "readme-v1", path: f"{path}-v1"},
                )
            ],
            branches={"main": "c1"},
            working_tree={path: hunks(first_hunk, second_hunk)},
            partial_hunks={path: {"target_hunks": [first_hunk], "leftover_hunks": [second_hunk]}},
        ),
        "state_requirements": {
            "head_branch": "main",
            "staging_empty": True,
            "working_tree_clean": True,
            "rules": [
                {"type": "commit_count_on_branch_equals", "branch": "main", "count": 3},
                tip(
                    "main~1",
                    message_equals=first_message,
                    changes_include_tokens=[first_hunk],
                    changes_exclude_tokens=[second_hunk],
                ),
                # The second commit's file carries both hunks, as in Git; the
                # split itself is proven by main~1 excluding the second hunk.
                tip("main", message_equals=second_message, changes_include_tokens=[second_hunk]),
            ],
        },
    }


def _hunk_into_last(*, path: str, missing: str, leftover: str, message: str) -> dict[str, Any]:
    base = {"README.md": "readme-v1", path: f"{path}-v1"}
    return {
        "initial_state": repo(
            commits=[
                commit("c1", "Initial project snapshot", [], base),
                commit("c2", message, ["c1"], {**base, path: f"{path}-v2"}),
            ],
            branches={"main": "c2"},
            working_tree={path: hunks(missing, leftover)},
            partial_hunks={path: {"target_hunks": [missing], "leftover_hunks": [leftover]}},
        ),
        "state_requirements": {
            "head_branch": "main",
            "staging_empty": True,
            "rules": [
                {"type": "commit_count_on_branch_equals", "branch": "main", "count": 2},
                tip(
                    "main",
                    message_equals=message,
                    changes_include_tokens=[missing],
                    changes_exclude_tokens=[leftover],
                ),
                {"type": "partial_hunks_left_in_working_tree", "paths": {path: [leftover]}},
                *amended("c2"),
            ],
        },
    }


def _reword_then_commit(
    *,
    committed: str,
    vague: str,
    reworded: str,
    new_path: str,
    new_message: str,
) -> dict[str, Any]:
    base = {"README.md": "readme-v1"}
    return {
        "initial_state": repo(
            commits=[
                commit("c1", "Initial project snapshot", [], base),
                commit("c2", vague, ["c1"], {**base, committed: f"{committed}-v1"}),
            ],
            branches={"main": "c2"},
            working_tree={new_path: untracked(f"{new_path}-draft")},
        ),
        "state_requirements": {
            "head_branch": "main",
            "staging_empty": True,
            "working_tree_clean": True,
            "rules": [
                {"type": "commit_count_on_branch_equals", "branch": "main", "count": 3},
                tip(
                    "main~1",
                    message_equals=reworded,
                    changes_include=[committed],
                    tree_excludes=[new_path],
                ),
                tip("main", message_equals=new_message, changes_include=[new_path]),
                {"type": "branch_history_excludes", "branch": "main", "commits": ["c2"]},
            ],
        },
    }


def _discard_theme() -> dict[str, Any]:
    tree = {"README.md": "readme-v1", "styles/theme.css": "theme-v1", "index.html": "index-v1"}
    return {
        "initial_state": repo(
            commits=[commit("c1", "Initial project snapshot", [], tree)],
            branches={"main": "c1"},
            working_tree={"styles/theme.css": modified("theme-neon-experiment")},
        ),
        "state_requirements": {
            "head_branch": "main",
            "branch_points_to": {"main": "c1"},
            "staging_empty": True,
            "working_tree_clean": True,
            "rules": [{"type": "commit_count_equals", "count": 1}],
        },
    }


def _unstage_then_commit(*, fix_path: str, keep_path: str, message: str) -> dict[str, Any]:
    tree = {"README.md": "readme-v1", fix_path: f"{fix_path}-v1", keep_path: f"{keep_path}-v1"}
    keep_edit = f"{keep_path}-draft-v2"
    return {
        "initial_state": repo(
            commits=[commit("c1", "Initial project snapshot", [], tree)],
            branches={"main": "c1"},
            staging={fix_path: f"{fix_path}-fixed-v2", keep_path: keep_edit},
        ),
        "state_requirements": {
            "head_branch": "main",
            "staging_empty": True,
            "latest_commit": {
                "branch": "main",
                "message_contains": [message],
                "contains_paths": [fix_path],
                "excludes_paths": [keep_path],
            },
            "working_tree_contains": [keep_path],
            "rules": [
                {"type": "commit_count_equals", "count": 2},
                tip("main", message_equals=message),
                {"type": "working_tree_contains_tokens", "paths": {keep_path: [keep_edit]}},
            ],
        },
    }


def _capstone(
    *,
    staged_note: str,
    stray: str,
    path: str,
    fix: str,
    leftover: str,
    message: str,
) -> dict[str, Any]:
    tree = {"README.md": "readme-v1", path: f"{path}-v1", stray: f"{stray}-v1"}
    return {
        "initial_state": repo(
            commits=[commit("c1", "Initial project snapshot", [], tree)],
            branches={"main": "c1"},
            staging={staged_note: f"{staged_note}-draft"},
            working_tree={stray: modified(f"{stray}-stray-edit"), path: hunks(fix, leftover)},
            partial_hunks={path: {"target_hunks": [fix], "leftover_hunks": [leftover]}},
        ),
        "state_requirements": {
            "head_branch": "main",
            "staging_empty": True,
            "working_tree_contains": [staged_note, path],
            "working_tree_absent": [stray],
            "rules": [
                {"type": "commit_count_equals", "count": 2},
                tip(
                    "main",
                    message_equals=message,
                    changes_include_tokens=[fix],
                    changes_exclude_tokens=[leftover],
                    changes_exclude=[staged_note, stray],
                ),
                {"type": "partial_hunks_left_in_working_tree", "paths": {path: [leftover]}},
            ],
        },
    }


def _init_workspace(
    *, root: str, branch: str, files: dict[str, str], inside: bool = False
) -> dict[str, Any]:
    """``root`` becomes a repository; ``files`` (inside it when ``inside``) stay untracked."""
    rules: list[dict[str, Any]] = [{"type": "commit_count_equals", "count": 0}]
    if inside:
        rules += [
            {"type": "working_tree_matches_exact_paths", "paths": sorted(files)},
            {"type": "working_tree_contains_tokens", "tokens": sorted(files.values())},
        ]
    return {
        "initial_state": repo(
            initialized=False,
            working_tree={path: untracked(content) for path, content in files.items()},
        ),
        "state_requirements": {
            "repository_initialized": True,
            "repository_root": root,
            "head_branch": branch,
            "staging_empty": True,
            "working_tree_contains": sorted(files),
            "rules": rules,
        },
    }


def _clone(
    *, url: str, project: str, messages: list[str], branch: str = "main", root: str | None = None
) -> dict[str, Any]:
    """A remote whose ``main`` holds ``messages``; a ``branch`` other than main adds one commit."""
    commits: list[dict] = []
    tree: dict[str, str] = {"README.md": f"# {project}\n"}
    for index, message in enumerate(messages, start=1):
        tree = {**tree, f"docs/part-{index}.md": f"{project}-part-{index}"}
        commits.append(
            commit(f"r{index}", message, [f"r{index - 1}"] if index > 1 else [], dict(tree))
        )
    branches = {"origin/main": commits[-1]["id"]}
    if branch != "main":
        branch_tip = f"r{len(commits) + 1}"
        commits.append(
            commit(
                branch_tip,
                f"Start the {branch} branch",
                [commits[-1]["id"]],
                {**tree, f"{branch}.md": f"{project}-{branch}"},
            )
        )
        branches[f"origin/{branch}"] = branch_tip
    tip_id = branches[f"origin/{branch}"]
    fixtures = remote_fixture(url, commits, branches["origin/main"])
    fixtures["branches"] = branches
    requirements: dict[str, Any] = {
        "repository_initialized": True,
        "head_branch": branch,
        "remote_exists": ["origin"],
        "remote_branch_exists": [f"origin/{branch}"],
        "remote_branch_points_to": {f"origin/{branch}": tip_id},
        "branch_points_to": {branch: tip_id},
        "staging_empty": True,
        "working_tree_clean": True,
        "rules": [],
    }
    if root:
        requirements["repository_root"] = root
    return {
        "initial_state": repo(initialized=False, remote_fixtures=fixtures),
        "state_requirements": requirements,
    }


FIXTURES: dict[str, dict[str, Any]] = {
    # 1.1 Initializing Repositories
    "init-easy-plain-notes": _init_workspace(
        root=".", branch="main", files={"notes.md": "Planning notes\n"}, inside=True
    ),
    "init-easy-plain-recipes": _init_workspace(
        root=".", branch="main", files={"recipes.md": "Family recipes\n"}, inside=True
    ),
    "init-easy-new-folder-among-files": _init_workspace(
        root="site-assets", branch="main", files={"design/logo.svg": "<svg>logo</svg>\n"}
    ),
    "init-medium-existing-sketches": _init_workspace(
        root="sketches",
        branch="main",
        files={"sketches/ideas.md": "Sketch ideas\n", "sketches/palette.txt": "teal,amber\n"},
        inside=True,
    ),
    "init-hard-nested-service": _init_nested(
        root="services/billing-api", branch="trunk", siblings=["services/search-api", "docs"]
    ),
    "init-hard-nested-course": _init_nested(
        root="courses/git-basics", branch="main", siblings=["courses/sql-basics", "templates"]
    ),
    # 1.2 Cloning Repositories
    "clone-easy-style-guide": _clone(
        url="https://example.test/design/style-guide.git",
        project="style-guide",
        messages=["Create the style guide", "Add colour tokens"],
    ),
    "clone-easy-branch-folder-handbook": _clone(
        url="https://example.test/docs/handbook.git",
        project="handbook",
        messages=["Create the team handbook", "Add onboarding chapter"],
        branch="draft",
        root="handbook-draft",
    ),
    "clone-medium-shallow-icons": _shallow_clone(
        url="https://example.test/design/icon-set.git",
        project="icons",
        destination="icon-set",
        depth=1,
        messages=["Create the icon set", "Add navigation icons", "Add status icons"],
    ),
    "clone-hard-shallow-ssh-audit": _shallow_clone(
        url="git@example.test:security/audit-rules.git",
        project="rules",
        destination="rules-review",
        depth=2,
        messages=[
            "Create audit rules",
            "Add password policy rule",
            "Add token rotation rule",
            "Add session timeout rule",
        ],
    ),
    # 1.3 Staging and Committing
    "commit-medium-three-file-release": {
        "initial_state": repo(
            commits=[
                commit(
                    "c1",
                    "Release 1.1",
                    [],
                    {
                        "README.md": "readme-v1",
                        "setup.py": "setup-1.1",
                        "src/version.py": "version-1.1",
                    },
                )
            ],
            branches={"main": "c1"},
            working_tree={
                "CHANGELOG.md": untracked("changelog-1.2"),
                "setup.py": modified("setup-1.2"),
                "src/version.py": modified("version-1.2"),
            },
        ),
        "state_requirements": {
            "head_branch": "main",
            "staging_empty": True,
            "latest_commit": {
                "branch": "main",
                "message_contains": ["Prepare 1.2 release"],
                "contains_paths": ["CHANGELOG.md", "setup.py", "src/version.py"],
            },
            "rules": [
                {"type": "commit_count_equals", "count": 2},
                tip(
                    "main",
                    message_equals="Prepare 1.2 release",
                    tree_contains={
                        "CHANGELOG.md": "changelog-1.2",
                        "setup.py": "setup-1.2",
                        "src/version.py": "version-1.2",
                    },
                ),
            ],
        },
    },
    "commit-medium-new-project-portfolio": _first_snapshot(
        files={"index.html": "portfolio-home-v1", "styles.css": "portfolio-styles-v1"},
        private="notes.txt",
        message="Initial portfolio",
    ),
    "commit-medium-new-project-recipes": _first_snapshot(
        files={"recipes.md": "recipes-v1", "shopping.md": "shopping-v1"},
        private="draft.txt",
        message="Start recipe notes",
    ),
    # 1.4 Partial Staging
    "partial-medium-hunk-plus-test": _hunk_plus_file(
        path="src/cart.py",
        fix="cart-rounding-fix-hunk",
        leftover="cart-debug-print-hunk",
        extra_path="tests/test_cart.py",
        extra=untracked("test-cart-rounding-v1"),
        extra_committed=None,
        message="Fix cart total rounding",
    ),
    "partial-medium-hunk-plus-doc": _hunk_plus_file(
        path="src/export.py",
        fix="export-quoting-fix-hunk",
        leftover="export-experimental-flag-hunk",
        extra_path="docs/export.md",
        extra=modified("export-docs-quoting-v2"),
        extra_committed="export-docs-v1",
        message="Fix CSV quoting",
    ),
    "partial-hard-split-two-commits-api": _split_commits(
        path="src/api.py",
        first=("api-expiry-fix-hunk", "Fix token expiry check"),
        second=("api-logging-tidy-hunk", "Tidy API logging"),
    ),
    "partial-hard-split-two-commits-ui": _split_commits(
        path="src/menu.js",
        first=("menu-focus-trap-fix-hunk", "Fix menu focus trap"),
        second=("menu-helper-rename-hunk", "Rename menu helpers"),
    ),
    # 1.5 Amending Commits
    "amend-medium-hunk-into-last-checkout": _hunk_into_last(
        path="src/checkout.py",
        missing="checkout-total-guard-hunk",
        leftover="checkout-debug-hunk",
        message="Validate checkout totals",
    ),
    "amend-medium-hunk-into-last-search": _hunk_into_last(
        path="src/search.py",
        missing="search-exact-rank-hunk",
        leftover="search-logging-hunk",
        message="Rank exact matches first",
    ),
    "amend-hard-fix-message-then-commit-api": _reword_then_commit(
        committed="src/limiter.py",
        vague="stuff",
        reworded="Add rate limiter",
        new_path="docs/limits.md",
        new_message="Document rate limits",
    ),
    "amend-hard-fix-message-then-commit-docs": _reword_then_commit(
        committed="docs/install.md",
        vague="wip",
        reworded="Document install steps",
        new_path="docs/faq.md",
        new_message="Add install FAQ",
    ),
    # 1.6 Unstaging and Discarding
    "restore-easy-discard-theme": _discard_theme(),
    "restore-medium-unstage-then-commit-login": _unstage_then_commit(
        fix_path="src/login.py", keep_path="notes/todo.md", message="Fix login redirect"
    ),
    "restore-medium-unstage-then-commit-cart": _unstage_then_commit(
        fix_path="src/cart_badge.js",
        keep_path="scratch/ideas.txt",
        message="Fix cart badge count",
    ),
    "restore-hard-capstone-report": _capstone(
        staged_note="debug.log",
        stray="tmp/output.txt",
        path="src/report.py",
        fix="report-totals-fix-hunk",
        leftover="report-experiment-hunk",
        message="Fix report totals",
    ),
    "restore-hard-capstone-invoice": _capstone(
        staged_note="notes/invoice-ideas.md",
        stray="build/invoice.html",
        path="src/invoice.py",
        fix="invoice-due-date-fix-hunk",
        leftover="invoice-refactor-hunk",
        message="Fix invoice due date",
    ),
}
