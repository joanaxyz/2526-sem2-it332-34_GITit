"""Module 2 wave scenarios: branching and collaboration (levels 2.1-2.9)."""

from __future__ import annotations

from typing import Any

from curriculum.seed_data.source.scenario_fixtures.shapes import (
    clean,
    commit,
    matches_origin,
    modified,
    origin,
    points_to,
    repo,
    tip,
    untracked,
)

BASE = {"README.md": "readme-v1"}


def _stash_entry(path: str, content: str, message: str) -> dict[str, Any]:
    return {"working_tree": {path: modified(content)}, "staging": {}, "conflicts": [], "message": message}


# ---------------------------------------------------------------------------
# 2.1 Creating and Switching Branches
# ---------------------------------------------------------------------------


def _back_to_main(*, branch: str, path: str, message: str) -> dict[str, Any]:
    return {
        "initial_state": repo(
            commits=[
                commit("c1", "Project baseline", [], BASE),
                commit("c2", message, ["c1"], {**BASE, path: f"{path}-v1"}),
            ],
            branches={"main": "c1", branch: "c2"},
            head=branch,
        ),
        "state_requirements": clean("main", points_to("main", "c1"), points_to(branch, "c2")),
    }


def _detached_save_and_return() -> dict[str, Any]:
    base = {**BASE, "src/search.py": "search-v1"}
    state = repo(
        commits=[
            commit("c1", "Project baseline", [], base),
            commit("c2", "Cache search results", ["c1"], {**base, "src/cache.py": "cache-v1"}),
            commit(
                "c3", "Spike: trigram search index", ["c1"], {**base, "src/search.py": "search-trigram"}
            ),
        ],
        branches={"main": "c1", "develop": "c2"},
    )
    state["head"] = {"type": "detached", "target": "c3"}
    return {
        "initial_state": state,
        "state_requirements": clean(
            "develop",
            points_to("archive/spike-results", "c3"),
            points_to("develop", "c2"),
            points_to("main", "c1"),
        ),
    }


# ---------------------------------------------------------------------------
# 2.2 Branch Naming Conventions
# ---------------------------------------------------------------------------


def _delete_merged(*, branch: str, path: str, message: str) -> dict[str, Any]:
    return {
        "initial_state": repo(
            commits=[
                commit("c1", "Project baseline", [], BASE),
                commit("c2", message, ["c1"], {**BASE, path: f"{path}-v2"}),
            ],
            branches={"main": "c2", branch: "c2"},
        ),
        "state_requirements": clean("main", points_to("main", "c2"), branch_absent=[branch]),
    }


def _named_branch_commit(
    *, path: str, fix: str, stray: str, branch: str, message: str
) -> dict[str, Any]:
    base = {**BASE, path: f"{path}-v1", stray: f"{stray}-v1"}
    return {
        "initial_state": repo(
            commits=[commit("c1", "Project baseline", [], base)],
            branches={"main": "c1"},
            working_tree={path: modified(fix), stray: modified(f"{stray}-stray-edit")},
        ),
        "state_requirements": clean(
            branch,
            points_to("main", "c1"),
            {"type": "commit_count_on_branch_equals", "branch": branch, "count": 2},
            tip(branch, message_equals=message, tree_contains={path: fix, stray: f"{stray}-v1"}),
        ),
    }


# ---------------------------------------------------------------------------
# 2.3 Stashing Work in Progress
# ---------------------------------------------------------------------------


def _pop_one(*, branch: str, path: str, wip: str, message: str) -> dict[str, Any]:
    base = {**BASE, path: f"{path}-v1"}
    return {
        "initial_state": repo(
            commits=[
                commit("c1", "Project baseline", [], base),
                commit("c2", message, ["c1"], {**base, path: f"{path}-v2"}),
            ],
            branches={"main": "c1", branch: "c2"},
            head=branch,
            stash_stack=[_stash_entry(path, wip, f"WIP on {branch}: c2 {message}")],
        ),
        "state_requirements": {
            "head_branch": branch,
            "staging_empty": True,
            "branch_points_to": {branch: "c2"},
            "working_tree_contains": [path],
            "rules": [
                {"type": "working_tree_contains_tokens", "paths": {path: [wip]}},
                {"type": "stash_stack_empty"},
            ],
        },
    }


def _two_stashes() -> dict[str, Any]:
    branch = "feature/reports"
    real, chart = "src/reports.py", "src/chart.js"
    base = {**BASE, real: "reports-v1", chart: "chart-v1"}
    return {
        "initial_state": repo(
            commits=[
                commit("c1", "Project baseline", [], base),
                commit("c2", "Start monthly reports", ["c1"], {**base, real: "reports-v2"}),
            ],
            branches={"main": "c1", branch: "c2"},
            head=branch,
            # stash@{1} is the real work; stash@{0} (last) is the abandoned experiment.
            stash_stack=[
                _stash_entry(real, "reports-monthly-totals", f"WIP on {branch}: monthly totals"),
                _stash_entry(chart, "chart-neon-experiment", f"WIP on {branch}: neon chart colours"),
            ],
        ),
        "state_requirements": {
            "head_branch": branch,
            "staging_empty": True,
            "working_tree_contains": [real],
            "rules": [
                {"type": "working_tree_contains_tokens", "paths": {real: ["reports-monthly-totals"]}},
                {"type": "working_tree_excludes_tokens", "paths": {chart: ["chart-neon-experiment"]}},
                {"type": "stash_stack_empty"},
            ],
        },
    }


def _cancelled_experiment() -> dict[str, Any]:
    path = "src/layout.py"
    base = {**BASE, path: "layout-v1"}
    return {
        "initial_state": repo(
            commits=[
                commit("c1", "Project baseline", [], base),
                commit("c2", "Cut release 3.0", ["c1"], {**base, "CHANGELOG.md": "release-3.0"}),
                commit("c3", "Start the layout experiment", ["c1"], {**base, path: "layout-v2"}),
            ],
            branches={"main": "c1", "release/v3": "c2", "feature/experiment": "c3"},
            head="feature/experiment",
            working_tree={path: modified("layout-grid-wip")},
        ),
        "state_requirements": clean(
            "feature/experiment",
            {"type": "stash_stack_empty"},
            points_to("feature/experiment", "c3"),
            points_to("release/v3", "c2"),
        ),
    }


# ---------------------------------------------------------------------------
# 2.4 Pushing to a Remote
# ---------------------------------------------------------------------------


def _branch_commit_publish(*, name: str, path: str, branch: str, message: str) -> dict[str, Any]:
    return {
        "initial_state": repo(
            commits=[commit("c1", "Project baseline", [], BASE)],
            branches={"main": "c1"},
            working_tree={path: untracked(f"{path}-v1")},
            **origin(name, branches={"origin/main": "c1"}, tracking={"main": "origin/main"}),
        ),
        "state_requirements": clean(
            branch,
            points_to("main", "c1"),
            tip(branch, message_equals=message, parent_equals="c1", tree_contains={path: f"{path}-v1"}),
            matches_origin(branch),
            upstream_tracking={branch: f"origin/{branch}"},
        ),
    }


def _amend_then_lease(
    *, name: str, branch: str, path: str, wrong: str, right: str
) -> dict[str, Any]:
    return {
        "initial_state": repo(
            commits=[
                commit("c1", "Project baseline", [], BASE),
                commit("c2", wrong, ["c1"], {**BASE, path: f"{path}-v1"}),
            ],
            branches={"main": "c1", branch: "c2"},
            head=branch,
            **origin(
                name,
                branches={"origin/main": "c1", f"origin/{branch}": "c2"},
                tracking={branch: f"origin/{branch}"},
            ),
        ),
        "state_requirements": clean(
            branch,
            tip(branch, message_equals=right, parent_equals="c1", tree_contains={path: f"{path}-v1"}),
            {"type": "operation_metadata_equals", "key": "last_amend_replaced_commit", "value": "c2"},
            matches_origin(branch),
            {"type": "operation_metadata_equals", "key": "force_with_lease", "value": True},
        ),
    }


# ---------------------------------------------------------------------------
# 2.5 Fetching and Pulling from a Remote
# ---------------------------------------------------------------------------


def _update_then_branch(*, name: str, branch: str, path: str, teammate: str) -> dict[str, Any]:
    base = {**BASE, path: f"{path}-v1"}
    return {
        "initial_state": repo(
            commits=[
                commit("c1", "Project baseline", [], base),
                commit("c2", teammate, ["c1"], {**base, path: f"{path}-v2"}),
            ],
            branches={"main": "c1"},
            **origin(
                name,
                branches={"origin/main": "c1"},
                updates={"origin/main": "c2"},
                tracking={"main": "origin/main"},
            ),
        ),
        "state_requirements": clean(
            branch,
            points_to(branch, "c2"),
            points_to("main", "c2"),
            remote_branch_points_to={"origin/main": "c2"},
        ),
    }


def _stash_pull_pop(*, name: str, branch: str, path: str, wip: str, teammate: str) -> dict[str, Any]:
    base = {**BASE, path: f"{path}-v1"}
    return {
        "initial_state": repo(
            commits=[
                commit("c1", "Project baseline", [], base),
                commit("c2", teammate, ["c1"], {**base, path: f"{path}-v2"}),
            ],
            branches={branch: "c1"},
            head=branch,
            working_tree={path: modified(wip)},
            **origin(
                name,
                branches={f"origin/{branch}": "c1"},
                updates={f"origin/{branch}": "c2"},
                tracking={branch: f"origin/{branch}"},
            ),
        ),
        "state_requirements": {
            "head_branch": branch,
            "staging_empty": True,
            "branch_points_to": {branch: "c2"},
            "remote_branch_points_to": {f"origin/{branch}": "c2"},
            "working_tree_contains": [path],
            "rules": [
                {"type": "working_tree_contains_tokens", "paths": {path: [wip]}},
                {"type": "stash_stack_empty"},
            ],
        },
    }


# ---------------------------------------------------------------------------
# 2.6 Reconciling Diverged Local and Remote Histories
# ---------------------------------------------------------------------------


def _commit_then_reconcile(
    *, name: str, branch: str, keep: str, scratch: str, teammate_path: str, message: str
) -> dict[str, Any]:
    base = {**BASE, scratch: f"{scratch}-v1"}
    return {
        "initial_state": repo(
            commits=[
                commit("c1", "Project baseline", [], base),
                commit("c2", "Add contributor guide", ["c1"], {**base, teammate_path: "guide-v1"}),
            ],
            branches={branch: "c1"},
            head=branch,
            staging={keep: f"{keep}-v1", scratch: f"{scratch}-draft-2"},
            **origin(
                name,
                branches={f"origin/{branch}": "c1"},
                updates={f"origin/{branch}": "c2"},
                tracking={branch: f"origin/{branch}"},
            ),
        ),
        "state_requirements": {
            "head_branch": branch,
            "staging_empty": True,
            "working_tree_contains": [scratch],
            "rules": [
                tip(
                    branch,
                    is_merge=True,
                    tree_contains={
                        keep: f"{keep}-v1",
                        teammate_path: "guide-v1",
                        scratch: f"{scratch}-v1",
                    },
                ),
                tip(f"{branch}~1", message_equals=message, parent_equals="c1"),
                {"type": "working_tree_contains_tokens", "paths": {scratch: [f"{scratch}-draft-2"]}},
                matches_origin(branch),
            ],
        },
    }


# ---------------------------------------------------------------------------
# 2.7 Completing Branch Merges
# ---------------------------------------------------------------------------


def _commit_then_land(*, branch: str, target: str, path: str, message: str) -> dict[str, Any]:
    return {
        "initial_state": repo(
            commits=[
                commit("c1", "Project baseline", [], BASE),
                commit("c2", f"Start {path}", ["c1"], {**BASE, path: f"{path}-draft"}),
            ],
            branches={target: "c1", branch: "c2"},
            head=branch,
            working_tree={path: modified(f"{path}-v1")},
        ),
        "state_requirements": clean(
            target,
            tip(target, is_merge=True, parent_equals="c1", tree_contains={path: f"{path}-v1"}),
            tip(branch, message_equals=message, parent_equals="c2", tree_contains={path: f"{path}-v1"}),
        ),
    }


def _land_publish_tidy(
    *, name: str, branch: str, target: str, path: str, message: str
) -> dict[str, Any]:
    return {
        "initial_state": repo(
            commits=[
                commit("c1", "Project baseline", [], BASE),
                commit("c2", message, ["c1"], {**BASE, path: f"{path}-v1"}),
            ],
            branches={target: "c1", branch: "c2"},
            head=branch,
            **origin(name, branches={f"origin/{target}": "c1"}, tracking={target: f"origin/{target}"}),
        ),
        "state_requirements": clean(
            target,
            tip(target, is_merge=True, tree_contains={path: f"{path}-v1"}),
            matches_origin(target),
            branch_absent=[branch],
        ),
    }


# ---------------------------------------------------------------------------
# 2.8 Squash Merging
# ---------------------------------------------------------------------------


def _wip_branch(path: str, drafts: int) -> list[dict]:
    commits = [commit("c1", "Project baseline", [], BASE)]
    for index in range(2, drafts + 2):
        content = f"{path}-v1" if index == drafts + 1 else f"{path}-draft-{index - 1}"
        commits.append(commit(f"c{index}", f"WIP {index - 1}", [f"c{index - 1}"], {**BASE, path: content}))
    return commits


def _squash_publish(
    *, name: str, branch: str, target: str, path: str, message: str, drafts: int
) -> dict[str, Any]:
    return {
        "initial_state": repo(
            commits=_wip_branch(path, drafts),
            branches={target: "c1", branch: f"c{drafts + 1}"},
            head=target,
            **origin(name, branches={f"origin/{target}": "c1"}, tracking={target: f"origin/{target}"}),
        ),
        "state_requirements": clean(
            target,
            tip(target, message_equals=message, parent_equals="c1", tree_contains={path: f"{path}-v1"}),
            {"type": "commit_count_on_branch_equals", "branch": target, "count": 2},
            matches_origin(target),
        ),
    }


def _switch_squash_cleanup(*, branch: str, target: str, path: str, message: str) -> dict[str, Any]:
    return {
        "initial_state": repo(
            commits=_wip_branch(path, 3), branches={target: "c1", branch: "c4"}, head=branch
        ),
        "state_requirements": clean(
            target,
            tip(target, message_equals=message, parent_equals="c1", tree_contains={path: f"{path}-v1"}),
            {"type": "commit_count_on_branch_equals", "branch": target, "count": 2},
            branch_absent=[branch],
        ),
    }


# ---------------------------------------------------------------------------
# 2.9 Deleting and Recovering Remote Branches
# ---------------------------------------------------------------------------


def _land_and_retire_remote(*, name: str, branch: str, path: str, message: str) -> dict[str, Any]:
    return {
        "initial_state": repo(
            commits=[
                commit("c1", "Project baseline", [], BASE),
                commit("c2", message, ["c1"], {**BASE, path: f"{path}-v1"}),
            ],
            branches={"main": "c1", branch: "c2"},
            **origin(
                name,
                branches={"origin/main": "c1", f"origin/{branch}": "c2"},
                tracking={"main": "origin/main", branch: f"origin/{branch}"},
            ),
        ),
        "state_requirements": clean(
            "main",
            tip("main", is_merge=True, tree_contains={path: f"{path}-v1"}),
            matches_origin("main"),
            remote_branch_absent=[f"origin/{branch}"],
            branch_exists=[branch],
        ),
    }


def _capstone(*, name: str, branch: str, path: str, stale: str) -> dict[str, Any]:
    return {
        "initial_state": repo(
            commits=[
                commit("c1", "Project baseline", [], BASE),
                commit("c2", f"Draft {path}", ["c1"], {**BASE, path: f"{path}-draft"}),
                commit("c3", f"Finish {path}", ["c2"], {**BASE, path: f"{path}-v1"}),
                commit("c4", f"Start {stale}", ["c1"], {**BASE, "src/banner.js": "banner-old"}),
            ],
            branches={"main": "c1"},
            **origin(
                name,
                branches={"origin/main": "c1", f"origin/{branch}": "c2", f"origin/{stale}": "c4"},
                updates={f"origin/{branch}": "c3"},
                tracking={"main": "origin/main"},
                stale=[f"origin/{stale}"],
            ),
        ),
        "state_requirements": clean(
            "main",
            tip("main", is_merge=True, tree_contains={path: f"{path}-v1"}),
            matches_origin("main"),
            remote_branch_absent=[f"origin/{branch}", f"origin/{stale}"],
        ),
    }


FIXTURES: dict[str, dict[str, Any]] = {
    # 2.1
    "switch-easy-back-to-main-docs": _back_to_main(
        branch="feature/docs-refresh", path="docs/index.md", message="Refresh the docs landing page"
    ),
    "switch-easy-back-to-main-api": _back_to_main(
        branch="feature/api-keys", path="src/api_keys.py", message="Add API key model"
    ),
    "switch-hard-detached-save-and-return": _detached_save_and_return(),
    # 2.2
    "bn-easy-delete-merged-typo": _delete_merged(
        branch="fix/readme-typo", path="README.md", message="Fix typo in README"
    ),
    "bn-easy-delete-merged-spike": _delete_merged(
        branch="spike/old-search", path="src/search.py", message="Keep the old search ranking"
    ),
    "bn-hard-named-branch-commit-parser": _named_branch_commit(
        path="src/parser.py",
        fix="parser-unicode-identifiers",
        stray="debug.log",
        branch="fix/parser-unicode",
        message="Handle unicode identifiers",
    ),
    "bn-hard-named-branch-commit-billing": _named_branch_commit(
        path="src/billing.py",
        fix="billing-round-totals",
        stray="tmp/billing-dump.txt",
        branch="PROJ-733/invoice-rounding",
        message="Round invoice totals",
    ),
    # 2.3
    "stash-easy-pop-search": _pop_one(
        branch="feature/search", path="src/search.py", wip="search-ranking-wip", message="Start search page"
    ),
    "stash-easy-pop-profile": _pop_one(
        branch="feature/profile", path="src/profile.py", wip="profile-avatar-wip", message="Start profile page"
    ),
    "stash-hard-two-stashes-reports": _two_stashes(),
    "stash-hard-cancelled-experiment": _cancelled_experiment(),
    # 2.4
    "push-medium-branch-commit-publish-search": _branch_commit_publish(
        name="shop-web", path="src/filters.js", branch="feature/search-filters", message="Add search filters"
    ),
    "push-medium-branch-commit-publish-invoices": _branch_commit_publish(
        name="billing-api",
        path="src/invoice_pdf.py",
        branch="feature/invoice-pdf",
        message="Add invoice PDF export",
    ),
    "push-hard-amend-then-lease-api": _amend_then_lease(
        name="api-client",
        branch="feature/api-retry",
        path="src/client.py",
        wrong="Fix stuff",
        right="Add retry to API client",
    ),
    "push-hard-amend-then-lease-docs": _amend_then_lease(
        name="handbook",
        branch="docs/sso",
        path="docs/sso.md",
        wrong="docs",
        right="Document SSO setup",
    ),
    # 2.5
    "pull-medium-update-then-branch-ui": _update_then_branch(
        name="shop-web", branch="feature/dark-mode", path="src/theme.css", teammate="Tidy theme colours"
    ),
    "pull-medium-update-then-branch-api": _update_then_branch(
        name="billing-api", branch="feature/webhooks", path="src/events.py", teammate="Add event registry"
    ),
    "pull-hard-stash-pull-pop-docs": _stash_pull_pop(
        name="handbook",
        branch="main",
        path="docs/guide.md",
        wip="guide-install-section-wip",
        teammate="Fix typos in the guide intro",
    ),
    "pull-hard-stash-pull-pop-app": _stash_pull_pop(
        name="ticketing-app",
        branch="develop",
        path="src/app.py",
        wip="app-timeout-setting-wip",
        teammate="Add logging setup to app",
    ),
    # 2.6
    "rec-medium-commit-then-reconcile-docs": _commit_then_reconcile(
        name="handbook",
        branch="main",
        keep="docs/setup.md",
        scratch="notes/draft.md",
        teammate_path="CONTRIBUTING.md",
        message="Document local setup",
    ),
    "rec-medium-commit-then-reconcile-api": _commit_then_reconcile(
        name="billing-api",
        branch="develop",
        keep="src/health.py",
        scratch="scratch/payload.json",
        teammate_path="docs/contributing.md",
        message="Add health check",
    ),
    # 2.7
    "merge-medium-commit-switch-noff-reports": _commit_then_land(
        branch="feature/reports", target="main", path="src/reports.py", message="Add monthly report"
    ),
    "merge-medium-commit-switch-noff-auth": _commit_then_land(
        branch="feature/mfa", target="develop", path="src/mfa.py", message="Add MFA prompt"
    ),
    "merge-hard-land-publish-tidy-search": _land_publish_tidy(
        name="shop-web",
        branch="feature/search",
        target="main",
        path="src/search.js",
        message="Add search page",
    ),
    "merge-hard-land-publish-tidy-billing": _land_publish_tidy(
        name="billing-api",
        branch="hotfix/billing-rounding",
        target="release/v2",
        path="src/rounding.py",
        message="Round billing totals half up",
    ),
    # 2.8
    "squash-medium-squash-publish-onboarding": _squash_publish(
        name="shop-web",
        branch="feature/onboarding",
        target="main",
        path="src/onboarding.js",
        message="Add onboarding flow",
        drafts=4,
    ),
    "squash-medium-squash-publish-export": _squash_publish(
        name="billing-api",
        branch="feature/export-csv",
        target="develop",
        path="src/export_csv.py",
        message="Add CSV export",
        drafts=3,
    ),
    "squash-hard-switch-squash-cleanup-cli": _switch_squash_cleanup(
        branch="feature/cli-colors", target="main", path="src/colors.py", message="Add CLI colors"
    ),
    "squash-hard-switch-squash-cleanup-ui": _switch_squash_cleanup(
        branch="feature/toast-ui", target="develop", path="src/toast.js", message="Add toast notifications"
    ),
    # 2.9
    "rb-medium-land-and-retire-search": _land_and_retire_remote(
        name="shop-web", branch="feature/search", path="src/search.js", message="Add search page"
    ),
    "rb-medium-land-and-retire-billing": _land_and_retire_remote(
        name="billing-api", branch="feature/billing", path="src/billing.py", message="Add billing summary"
    ),
    "rb-hard-capstone-release-notes": _capstone(
        name="handbook",
        branch="feature/release-notes",
        path="docs/release-notes.md",
        stale="feature/old-banner",
    ),
    "rb-hard-capstone-payments": _capstone(
        name="shop-web",
        branch="feature/payments-v2",
        path="src/payments.js",
        stale="feature/legacy-checkout",
    ),
}
