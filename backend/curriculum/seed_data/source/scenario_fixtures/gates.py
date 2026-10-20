"""Challenge Gate scenarios: one workflow per module trial (PLAN.md §14).

Each module's gate has an Easy, a Medium and a Hard trial with two variants.
A trial combines several of the module's commands in the order a real task
needs them; the Hard trial adds one trap the module taught.
"""

from __future__ import annotations

from typing import Any

from curriculum.seed_data.source.scenario_fixtures.module_1 import _first_snapshot
from curriculum.seed_data.source.scenario_fixtures.shapes import (
    ORIGIN,
    amended,
    clean,
    commit,
    hunks,
    modified,
    origin,
    repo,
    tip,
    untracked,
)

# ---------------------------------------------------------------------------
# Module 1 - Local Repository Foundations
# ---------------------------------------------------------------------------


def _complete_last_commit(
    *, path: str, hunk: str, debug: str, missing: str, staged_note: str, message: str
) -> dict[str, Any]:
    base = {"README.md": "readme-v1", path: f"{path}-v1"}
    return {
        "initial_state": repo(
            commits=[
                commit("c1", "Initial project snapshot", [], base),
                commit("c2", message, ["c1"], {**base, path: f"{path}-v2"}),
            ],
            branches={"main": "c2"},
            staging={staged_note: f"{staged_note}-draft"},
            working_tree={path: hunks(hunk, debug), missing: untracked(f"{missing}-v1")},
            partial_hunks={path: {"target_hunks": [hunk], "leftover_hunks": [debug]}},
        ),
        "state_requirements": {
            "head_branch": "main",
            "staging_empty": True,
            "working_tree_contains": [staged_note, path],
            "rules": [
                {"type": "commit_count_on_branch_equals", "branch": "main", "count": 2},
                tip(
                    "main",
                    message_equals=message,
                    changes_include=[path, missing],
                    changes_include_tokens=[hunk],
                    changes_exclude_tokens=[debug],
                    changes_exclude=[staged_note],
                ),
                {"type": "partial_hunks_left_in_working_tree", "paths": {path: [debug]}},
                *amended("c2"),
            ],
        },
    }


def _reword_then_commit_fix(
    *,
    typo: str,
    reworded: str,
    path: str,
    fix: str,
    debug: str,
    doc: str,
    staged_log: str,
    stray: str,
    message: str,
) -> dict[str, Any]:
    base = {"README.md": "readme-v1", stray: f"{stray}-v1"}
    return {
        "initial_state": repo(
            commits=[
                commit("c1", "Initial project snapshot", [], base),
                commit("c2", typo, ["c1"], {**base, path: f"{path}-v1"}),
            ],
            branches={"main": "c2"},
            staging={staged_log: f"{staged_log}-output"},
            working_tree={
                stray: modified(f"{stray}-stray-edit"),
                path: hunks(fix, debug),
                doc: untracked(f"{doc}-v1"),
            },
            partial_hunks={path: {"target_hunks": [fix], "leftover_hunks": [debug]}},
        ),
        "state_requirements": {
            "head_branch": "main",
            "staging_empty": True,
            "working_tree_contains": [staged_log, path],
            "working_tree_absent": [stray],
            "rules": [
                {"type": "commit_count_on_branch_equals", "branch": "main", "count": 3},
                tip("main~1", message_equals=reworded, changes_exclude=[staged_log, doc]),
                tip(
                    "main",
                    message_equals=message,
                    changes_include=[doc],
                    changes_include_tokens=[fix],
                    changes_exclude_tokens=[debug],
                    changes_exclude=[staged_log, stray],
                ),
                {
                    "type": "operation_metadata_equals",
                    "key": "last_amend_replaced_commit",
                    "value": "c2",
                },
                {"type": "partial_hunks_left_in_working_tree", "paths": {path: [debug]}},
            ],
        },
    }


# ---------------------------------------------------------------------------
# Module 2 - Branching and Collaboration
# ---------------------------------------------------------------------------


def _fresh_branch_from_main(*, name: str, old: str, new: str, teammate: str) -> dict[str, Any]:
    base = {"README.md": "readme-v1", "src/app.py": "app-v1"}
    commits = [
        commit("c1", "Project baseline", [], base),
        commit("c2", f"Finish {old}", ["c1"], {**base, f"src/{old}.py": f"{old}-v1"}),
        commit("c3", teammate, ["c1"], {**base, "src/app.py": "app-v2"}),
    ]
    return {
        "initial_state": repo(
            commits=commits,
            branches={"main": "c1", f"feature/{old}": "c2"},
            head=f"feature/{old}",
            **origin(
                name,
                branches={"origin/main": "c1", f"origin/feature/{old}": "c2"},
                updates={"origin/main": "c3"},
                tracking={"main": "origin/main", f"feature/{old}": f"origin/feature/{old}"},
            ),
        ),
        "state_requirements": clean(
            f"feature/{new}",
            {"type": "branch_points_to", "branch": f"feature/{new}", "commit": "c3"},
            {"type": "branch_points_to", "branch": "main", "commit": "c3"},
            {"type": "branch_points_to", "branch": f"feature/{old}", "commit": "c2"},
            remote_branch_points_to={"origin/main": "c3"},
        ),
    }


def _stash_and_sync(*, name: str, branch: str, path: str, wip: str) -> dict[str, Any]:
    base = {"README.md": "readme-v1", "src/app.py": "app-v1", path: f"{path}-v0"}
    commits = [
        commit("c1", "Project baseline", [], base),
        commit("c2", f"Start {branch}", ["c1"], {**base, path: f"{path}-v1"}),
        commit("c3", "Patch login timeout", ["c1"], {**base, "src/app.py": "app-v2"}),
    ]
    return {
        "initial_state": repo(
            commits=commits,
            branches={"main": "c1", f"feature/{branch}": "c2"},
            head=f"feature/{branch}",
            working_tree={path: modified(wip)},
            **origin(
                name,
                branches={"origin/main": "c1"},
                updates={"origin/main": "c3"},
                tracking={"main": "origin/main"},
            ),
        ),
        "state_requirements": {
            "head_branch": f"feature/{branch}",
            "staging_empty": True,
            "branch_points_to": {"main": "c3", f"feature/{branch}": "c2"},
            "remote_branch_points_to": {"origin/main": "c3"},
            "working_tree_contains": [path],
            "rules": [
                {"type": "working_tree_contains_tokens", "paths": {path: [wip]}},
                {"type": "stash_stack_empty"},
            ],
        },
    }


def _land_and_retire(*, name: str, branch: str, path: str, message: str) -> dict[str, Any]:
    base = {"README.md": "readme-v1", "CHANGELOG.md": "changelog-v1"}
    commits = [
        commit("c1", "Project baseline", [], base),
        commit("c2", f"Start {branch}", ["c1"], {**base, path: f"{path}-draft"}),
        commit("c3", f"Finish {branch}", ["c2"], {**base, path: f"{path}-v1"}),
        commit("c4", "Update changelog", ["c1"], {**base, "CHANGELOG.md": "changelog-v2"}),
    ]
    feature = f"feature/{branch}"
    return {
        "initial_state": repo(
            commits=commits,
            branches={"main": "c1", feature: "c3"},
            head=feature,
            **origin(
                name,
                branches={"origin/main": "c1", f"origin/{feature}": "c3"},
                updates={"origin/main": "c4"},
                tracking={"main": "origin/main", feature: f"origin/{feature}"},
            ),
        ),
        "state_requirements": clean(
            "main",
            tip(
                "main",
                message_equals=message,
                is_not_merge=True,
                tree_contains={path: f"{path}-v1", "CHANGELOG.md": "changelog-v2"},
            ),
            {"type": "commit_count_on_branch_equals", "branch": "main", "count": 3},
            {"type": "remote_branch_matches_local", "remote_branch": "origin/main", "branch": "main"},
            {"type": "branch_absent", "branch": feature},
            {"type": "remote_branch_absent", "remote_branch": f"origin/{feature}"},
        ),
    }


# ---------------------------------------------------------------------------
# Module 3 - Conflict Resolution
# ---------------------------------------------------------------------------


def _merge_and_resolve(*, branch: str, path: str, resolved: str) -> dict[str, Any]:
    commits = [
        commit("c0", "Common base", [], {path: f"{path} base"}),
        commit("c1", "Main update", ["c0"], {path: f"{path} main"}),
        commit("c2", f"Update {branch}", ["c0"], {path: f"{path} feature"}),
    ]
    return {
        "initial_state": repo(commits=commits, branches={"main": "c1", f"feature/{branch}": "c2"}),
        "state_requirements": clean(
            "main",
            {"type": "commit_is_merge", "branch": "main"},
            {"type": "commit_has_parent", "branch": "main", "parent": "c2"},
            {"type": "commit_tree_contains", "branch": "main", "tree": {path: resolved}},
            conflict_free=True,
        ),
    }


def _backport_with_origin(*, release: str, path: str, fix: str, resolved: str) -> dict[str, Any]:
    commits = [
        commit("c0", "Common base", [], {path: f"{path} base", "README.md": "readme"}),
        commit("c1", f"Prepare {release}", ["c0"], {path: f"{path} release", "README.md": "readme"}),
        commit("c2", "Main groundwork", ["c0"], {path: f"{path} main", "README.md": "readme"}),
        commit("c3", fix, ["c2"], {path: f"{path} fixed", "README.md": "readme"}),
    ]
    return {
        "initial_state": repo(commits=commits, branches={"main": "c3", release: "c1"}),
        "state_requirements": clean(
            release,
            {"type": "cherry_pick_not_in_progress"},
            {"type": "commit_count_on_branch_equals", "branch": release, "count": 3},
            tip(
                release,
                message_contains=[fix, "cherry picked from commit c3"],
                tree_contains={path: resolved},
            ),
            {"type": "branch_points_to", "branch": "main", "commit": "c3"},
            conflict_free=True,
        ),
    }


def _abort_then_tool_merge(*, wrong: str, right: str, path: str, resolved: str) -> dict[str, Any]:
    base = {path: f"{path} base"}
    ours = {path: f"{path} main"}
    commits = [
        commit("c0", "Common base", [], base),
        commit("c1", "Main update", ["c0"], ours),
        commit("c2", f"Update {wrong}", ["c0"], {path: f"{path} {wrong}"}),
        commit("c3", f"Update {right}", ["c0"], {path: f"{path} {right}"}),
    ]
    branches = {"main": "c1", f"feature/{wrong}": "c2", f"feature/{right}": "c3"}
    before_merge = repo(commits=commits, branches=branches)
    stopped = repo(
        commits=commits,
        branches=branches,
        merge_parent="c2",
        merge_abort_state=before_merge,
        conflict_details={
            path: {
                "base": base[path],
                "ours": ours[path],
                "theirs": f"{path} {wrong}",
                "merge_branch": f"feature/{wrong}",
            }
        },
        working_tree={
            path: {
                "status": "conflicted",
                "content": (
                    f"<<<<<<< HEAD\n{ours[path]}\n=======\n{path} {wrong}\n"
                    f">>>>>>> feature/{wrong}\n"
                ),
            }
        },
        operation_metadata={
            "last_merge_branch": f"feature/{wrong}",
            "last_merge_target": "c2",
            "last_merge_conflicted": True,
        },
    )
    stopped["conflicts"] = [path]
    return {
        "initial_state": stopped,
        "state_requirements": clean(
            "main",
            {"type": "commit_is_merge", "branch": "main"},
            {"type": "commit_has_parent", "branch": "main", "parent": "c3"},
            {"type": "branch_history_excludes", "branch": "main", "commits": ["c2"]},
            {"type": "commit_tree_contains", "branch": "main", "tree": {path: resolved}},
            {"type": "operation_metadata_equals", "key": "last_mergetool_tool", "value": "meld"},
            conflict_free=True,
        ),
    }


# ---------------------------------------------------------------------------
# Module 4 - Advanced Recovery and History
# ---------------------------------------------------------------------------


def _recover_lost_work(*, branch: str, path: str, fix: str) -> dict[str, Any]:
    commits = [
        commit("c0", "Reset position", [], {path: "baseline"}),
        commit("c1", f"Start {branch}", ["c0"], {path: "groundwork"}),
        commit("c2", f"Continue {branch}", ["c1"], {path: "continued"}),
        commit("c3", fix, ["c2"], {path: f"{fix} done"}),
        commit("c4", "Abandoned experiment", ["c2"], {path: "abandoned experiment"}),
    ]
    return {
        "initial_state": repo(
            commits=commits,
            branches={"main": "c0"},
            reflog=[
                {"ref": "main", "commit": "c4", "action": "checkout"},
                {"ref": "main", "commit": "c3", "action": "commit"},
                {"ref": "main", "commit": "c0", "action": "reset: moving to HEAD~3"},
            ],
        ),
        "state_requirements": clean(
            f"recovery/{branch}",
            {"type": "branch_points_to", "branch": f"recovery/{branch}", "commit": "c3"},
            {"type": "branch_points_to", "branch": "main", "commit": "c0"},
            {"type": "required_command_sequence", "commands": ["git reflog", "git show c3"]},
        ),
    }


def _drop_local_revert_published(*, name: str, path: str, bug: str, local: str) -> dict[str, Any]:
    base = {"README.md": "readme-v1", path: f"{path}-v1"}
    commits = [
        commit("c1", "Project baseline", [], base),
        commit("c2", bug, ["c1"], {**base, path: f"{path}-broken"}),
        commit("c3", local, ["c2"], {**base, path: f"{path}-broken", "docs/notes.md": "experiment"}),
    ]
    return {
        "initial_state": repo(
            commits=commits,
            branches={"main": "c3"},
            remotes={"origin": ORIGIN.format(name=name)},
            remote_branches={"origin/main": "c2"},
            upstream_tracking={"main": "origin/main"},
        ),
        "state_requirements": clean(
            "main",
            {"type": "branch_history_contains", "branch": "main", "commits": ["c2"]},
            {"type": "branch_history_excludes", "branch": "main", "commits": ["c3"]},
            {"type": "commit_tree_contains", "branch": "main", "tree": {path: f"{path}-v1"}},
            {"type": "commit_tree_excludes", "branch": "main", "paths": ["docs/notes.md"]},
            {"type": "commit_count_on_branch_equals", "branch": "main", "count": 3},
            {"type": "remote_branch_matches_local", "remote_branch": "origin/main", "branch": "main"},
        ),
    }


def _move_branch_onto_main(*, name: str, branch: str, path: str) -> dict[str, Any]:
    feature = f"feature/{branch}"
    base = {"README.md": "readme", "src/app.py": "app base"}
    release_tree = {**base, "src/app.py": "app release fix"}
    main_tree = {**base, "src/app.py": "app main"}
    commits = [
        commit("c0", "Project baseline", [], base),
        commit("c1", "Release 1.0 fixes", ["c0"], release_tree),
        commit("c2", "Main work", ["c0"], main_tree),
        commit("c3", f"Add {branch}", ["c1"], {**release_tree, path: f"{path} v1"}),
        commit("c4", f"Polish {branch}", ["c3"], {**release_tree, path: f"{path} v2"}),
    ]
    remote = {
        "remotes": {"origin": ORIGIN.format(name=name)},
        "remote_branches": {"origin/main": "c2", f"origin/{feature}": "c4"},
        "upstream_tracking": {"main": "origin/main", feature: f"origin/{feature}"},
    }
    original = repo(
        commits=commits,
        branches={"main": "c2", "release/1.0": "c1", feature: "c4"},
        head=feature,
        **remote,
    )
    stopped = repo(
        commits=commits,
        branches={"main": "c2", "release/1.0": "c1", feature: "c2"},
        head=feature,
        working_tree={
            "src/app.py": {
                "status": "conflicted",
                "content": "<<<<<<< HEAD\napp main\n=======\napp release fix\n>>>>>>> c1\n",
            }
        },
        rebase_state={
            "abort_state": original,
            "current_source": "c1",
            "remaining": ["c3", "c4"],
            "applied": [],
            "branch": feature,
        },
        **remote,
    )
    stopped["conflicts"] = ["src/app.py"]
    return {
        "initial_state": stopped,
        "state_requirements": clean(
            feature,
            {"type": "rebase_not_in_progress"},
            {"type": "branch_history_contains", "branch": feature, "commits": ["c2"]},
            {"type": "branch_history_excludes", "branch": feature, "commits": ["c1"]},
            {"type": "commit_count_on_branch_equals", "branch": feature, "count": 4},
            {
                "type": "commit_tree_contains",
                "branch": feature,
                "tree": {path: f"{path} v2", "src/app.py": "app main"},
            },
            {"type": "remote_branch_matches_local", "remote_branch": f"origin/{feature}", "branch": feature},
            {"type": "operation_metadata_equals", "key": "force_with_lease", "value": True},
            conflict_free=True,
        ),
    }


FIXTURES: dict[str, dict[str, Any]] = {
    # Module 1 gate
    "gate1-easy-first-snapshot-field-log": _first_snapshot(
        files={"notes.md": "field-notes-v1", "readings.csv": "readings-v1"},
        private="scratch.txt",
        message="Start field log",
    ),
    "gate1-easy-first-snapshot-quiz": _first_snapshot(
        files={"index.html": "quiz-home-v1", "quiz.js": "quiz-logic-v1"},
        private="todo.txt",
        message="Start quiz app",
    ),
    "gate1-medium-complete-last-commit-search": _complete_last_commit(
        path="src/search.py",
        hunk="search-ranking-hunk",
        debug="search-debug-hunk",
        missing="templates/search.html",
        staged_note="notes.txt",
        message="Add search page",
    ),
    "gate1-medium-complete-last-commit-upload": _complete_last_commit(
        path="src/upload.py",
        hunk="upload-size-limit-hunk",
        debug="upload-debug-hunk",
        missing="docs/upload.md",
        staged_note="scratch.md",
        message="Add file upload",
    ),
    "gate1-hard-reword-then-commit-export": _reword_then_commit_fix(
        typo="Add expor",
        reworded="Add export",
        path="src/export.py",
        fix="export-header-fix-hunk",
        debug="export-debug-hunk",
        doc="docs/export.md",
        staged_log="tmp/run.log",
        stray="cache/report.json",
        message="Fix export headers",
    ),
    "gate1-hard-reword-then-commit-billing": _reword_then_commit_fix(
        typo="Add biling",
        reworded="Add billing",
        path="src/billing.py",
        fix="billing-tax-fix-hunk",
        debug="billing-debug-hunk",
        doc="docs/billing.md",
        staged_log="logs/billing.log",
        stray="cache/invoices.json",
        message="Fix billing tax",
    ),
    # Module 2 gate
    "gate2-easy-fresh-branch-search": _fresh_branch_from_main(
        name="shop", old="cart", new="search-filters", teammate="Fix cart total"
    ),
    "gate2-easy-fresh-branch-invoices": _fresh_branch_from_main(
        name="billing", old="reports", new="invoice-pdf", teammate="Fix tax rounding"
    ),
    "gate2-medium-stash-and-sync-reports": _stash_and_sync(
        name="analytics", branch="reports", path="src/reports.py", wip="reports-wip-chart"
    ),
    "gate2-medium-stash-and-sync-profile": _stash_and_sync(
        name="accounts", branch="profile", path="src/profile.py", wip="profile-wip-avatar"
    ),
    "gate2-hard-land-and-retire-filters": _land_and_retire(
        name="catalog", branch="filters", path="src/filters.js", message="Add search filters"
    ),
    "gate2-hard-land-and-retire-export": _land_and_retire(
        name="ledger", branch="export", path="src/export.py", message="Add CSV export"
    ),
    # Module 3 gate
    "gate3-easy-merge-and-resolve-banner": _merge_and_resolve(
        branch="banner", path="src/banner.html", resolved="<p>Welcome back, team!</p>"
    ),
    "gate3-easy-merge-and-resolve-footer": _merge_and_resolve(
        branch="footer", path="src/footer.html", resolved="<footer>Contact support</footer>"
    ),
    "gate3-medium-backport-tax": _backport_with_origin(
        release="release/2.1",
        path="src/tax.py",
        fix="Round tax per line",
        resolved="ROUND_PER_LINE = True",
    ),
    "gate3-medium-backport-locale": _backport_with_origin(
        release="release/3.0",
        path="src/locale.py",
        fix="Fix date format for fil-PH",
        resolved="DATE_FORMAT = 'MM/DD/YYYY'",
    ),
    "gate3-hard-abort-then-tool-merge-pricing": _abort_then_tool_merge(
        wrong="old-pricing",
        right="pricing-v2",
        path="src/prices.py",
        resolved="PRICE_TIERS = ['basic', 'pro']",
    ),
    "gate3-hard-abort-then-tool-merge-copy": _abort_then_tool_merge(
        wrong="draft-copy",
        right="checkout-copy",
        path="src/checkout.js",
        resolved="const label = 'Place order'",
    ),
    # Module 4 gate
    "gate4-easy-recover-search-fix": _recover_lost_work(
        branch="search", path="src/search.py", fix="Fix borrower search"
    ),
    "gate4-easy-recover-receipt-fix": _recover_lost_work(
        branch="receipts", path="src/receipts.py", fix="Fix receipt totals"
    ),
    "gate4-medium-drop-local-revert-published-banner": _drop_local_revert_published(
        name="storefront", path="src/banner.py", bug="Add discount banner", local="Try banner animation"
    ),
    "gate4-medium-drop-local-revert-published-alerts": _drop_local_revert_published(
        name="monitor", path="src/alerts.py", bug="Page on every warning", local="Experiment with alert sounds"
    ),
    "gate4-hard-move-branch-onto-main-receipts": _move_branch_onto_main(
        name="pos", branch="receipts", path="src/receipts.py"
    ),
    "gate4-hard-move-branch-onto-main-coupons": _move_branch_onto_main(
        name="promo", branch="coupons", path="src/coupons.py"
    ),
}
