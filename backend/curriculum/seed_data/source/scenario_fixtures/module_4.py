"""Module 4 wave scenarios: advanced recovery and history (levels 4.1-4.3)."""

from __future__ import annotations

from typing import Any

from curriculum.seed_data.source.scenario_fixtures.shapes import (
    clean,
    commit,
    matches_origin,
    origin,
    points_to,
    repo,
    tip,
)

def _chain(specs: list[tuple[str, str, str | None, dict[str, str]]]) -> list[dict]:
    """Commits from (id, message, parent, changed files): each tree builds on its parent's."""
    trees: dict[str, dict[str, str]] = {}
    commits = []
    for commit_id, message, parent, changes in specs:
        tree = {**(trees[parent] if parent else {}), **changes}
        trees[commit_id] = tree
        commits.append(commit(commit_id, message, [parent] if parent else [], tree))
    return commits


def _conflicted(ours: str, theirs: str, label: str) -> dict[str, Any]:
    return {
        "status": "conflicted",
        "content": f"<<<<<<< HEAD\n{ours}\n=======\n{theirs}\n>>>>>>> {label}\n",
    }


def _stopped_rebase(
    commits: list[dict],
    branches: dict[str, str],
    *,
    branch: str,
    onto: str,
    source: str,
    remaining: list[str],
    path: str,
    **extra: Any,
) -> dict[str, Any]:
    """``branch`` mid-rebase onto ``onto``, stopped replaying ``source`` on ``path``."""
    trees = {item["id"]: item["tree"] for item in commits}
    parents = {item["id"]: item["parents"] for item in commits}
    original = repo(commits=commits, branches=branches, head=branch, **extra)
    ours, theirs = trees[onto][path], trees[source][path]
    stopped = repo(
        commits=commits,
        branches={**branches, branch: onto},
        head=branch,
        conflict_details={
            path: {"base": trees[parents[source][0]][path], "ours": ours, "theirs": theirs}
        },
        working_tree={path: _conflicted(ours, theirs, source)},
        rebase_state={
            "abort_state": original,
            "current_source": source,
            "remaining": remaining,
            "applied": [],
            "branch": branch,
            "target": onto,
        },
        **extra,
    )
    stopped["conflicts"] = [path]
    return stopped


def _reverted(commit_id: str, branch: str, message: str) -> list[dict[str, Any]]:
    return [
        {"type": "new_revert_commit_exists"},
        {"type": "latest_commit_message_contains", "branch": branch, "text": f'Revert "{message}"'},
        {"type": "revert_preserves_history", "commit": commit_id, "branch": branch},
    ]


# ---------------------------------------------------------------------------
# 4.1 Recovering from Hard Resets
# ---------------------------------------------------------------------------


def _recover_and_publish(
    *, name: str, path: str, branch: str, steps: list[tuple[str, str]], reset_to: str
) -> dict[str, Any]:
    specs: list[tuple[str, str, str | None, dict[str, str]]] = [
        ("c0", "Project baseline", None, {"README.md": "readme-v1", path: f"{path}-v1"})
    ]
    for index, (message, content) in enumerate(steps, start=1):
        specs.append((f"c{index}", message, f"c{index - 1}", {path: content}))
    commits = _chain(specs)
    lost = commits[-1]["id"]
    return {
        "initial_state": repo(
            commits=commits,
            branches={"main": reset_to},
            reflog=[
                {"ref": "main", "commit": lost, "action": f"commit: {commits[-1]['message']}"},
                {"ref": "main", "commit": reset_to, "action": f"reset: moving to {reset_to}"},
            ],
            **origin(name, branches={"origin/main": reset_to}, tracking={"main": "origin/main"}),
        ),
        "state_requirements": clean(
            branch,
            points_to(branch, lost),
            points_to("main", reset_to),
            matches_origin(branch),
            upstream_tracking={branch: f"origin/{branch}"},
        ),
    }


def _recover_then_pick(
    *, path: str, branch: str, groundwork: str, experiment: str, fix: str, fixed: str
) -> dict[str, Any]:
    commits = _chain(
        [
            ("c0", "Project baseline", None, {"README.md": "readme-v1", path: f"{path}-v1"}),
            ("c1", "Prepare the sprint", "c0", {"README.md": "readme-v2"}),
            ("c2", groundwork, "c1", {"src/groundwork.py": "groundwork-draft"}),
            ("c3", experiment, "c2", {"lab/experiment.py": "experiment-v1"}),
            ("c4", fix, "c3", {path: fixed}),
        ]
    )
    return {
        "initial_state": repo(
            commits=commits,
            branches={"main": "c1"},
            reflog=[
                {"ref": "main", "commit": "c4", "action": f"commit: {fix}"},
                {"ref": "main", "commit": "c1", "action": "reset: moving to HEAD~3"},
            ],
        ),
        "state_requirements": clean(
            "main",
            points_to(branch, "c4"),
            tip(
                "main",
                message_contains=[fix],
                parent_equals="c1",
                tree_contains={path: fixed},
                tree_excludes=["lab/experiment.py", "src/groundwork.py"],
            ),
        ),
    }


# ---------------------------------------------------------------------------
# 4.2 Reversing Pushed Commits Safely
# ---------------------------------------------------------------------------


def _pull_then_revert(
    *, name: str, path: str, bad: str, teammate_path: str, teammate: str, bad_id: str
) -> dict[str, Any]:
    specs: list[tuple[str, str, str | None, dict[str, str]]] = [
        ("c0", "Project baseline", None, {"README.md": "readme-v1", path: f"{path}-v1"}),
        ("c1", "Add contributor notes", "c0", {"CONTRIBUTING.md": "contributing-v1"}),
        ("c2", "Tidy project layout", "c1", {"Makefile": "make-v1"}),
    ]
    if bad_id == "c4":
        specs.append(("c3", "Add release checklist", "c2", {"docs/release.md": "release-v1"}))
    specs.append((bad_id, bad, specs[-1][0], {path: f"{path}-broken"}))
    teammate_id = f"c{int(bad_id[1:]) + 1}"
    specs.append((teammate_id, teammate, bad_id, {teammate_path: f"{teammate_path}-v1"}))
    commits = _chain(specs)
    return {
        "initial_state": repo(
            commits=commits,
            branches={"main": bad_id},
            **origin(
                name,
                branches={"origin/main": bad_id},
                updates={"origin/main": teammate_id},
                tracking={"main": "origin/main"},
            ),
        ),
        "state_requirements": clean(
            "main",
            *_reverted(bad_id, "main", bad),
            tip(
                "main",
                parent_equals=teammate_id,
                tree_contains={path: f"{path}-v1", teammate_path: f"{teammate_path}-v1"},
            ),
            matches_origin("main"),
        ),
    }


def _revert_on_release(
    *, name: str, release: str, path: str, bad: str, bad_id: str
) -> dict[str, Any]:
    specs: list[tuple[str, str, str | None, dict[str, str]]] = [
        ("c0", "Project baseline", None, {"README.md": "readme-v1", path: f"{path}-v1"}),
        ("c1", "Start the next version", "c0", {"src/next.py": "next-v1"}),
        ("c2", f"Cut {release}", "c0", {"CHANGELOG.md": "changelog-v1"}),
    ]
    if bad_id == "c4":
        specs.append(("c3", "Fix release build script", "c2", {"build.sh": "build-v2"}))
    specs.append((bad_id, bad, specs[-1][0], {path: f"{path}-broken"}))
    notes_id = f"c{int(bad_id[1:]) + 1}"
    specs.append((notes_id, "Update release notes", bad_id, {"CHANGELOG.md": "changelog-v2"}))
    commits = _chain(specs)
    remote = f"origin/{release}"
    return {
        "initial_state": repo(
            commits=commits,
            branches={"main": "c1", release: notes_id},
            **origin(
                name,
                branches={"origin/main": "c1", remote: notes_id},
                tracking={"main": "origin/main", release: remote},
            ),
        ),
        "state_requirements": clean(
            release,
            *_reverted(bad_id, release, bad),
            tip(
                release,
                parent_equals=notes_id,
                tree_contains={path: f"{path}-v1", "CHANGELOG.md": "changelog-v2"},
            ),
            matches_origin(release),
            points_to("main", "c1"),
        ),
    }


def _amend_then_revert(
    *, name: str, path: str, bad: str, bad_id: str, local_path: str, vague: str, right: str
) -> dict[str, Any]:
    specs: list[tuple[str, str, str | None, dict[str, str]]] = [
        ("c0", "Initial commit", None, {"README.md": "readme-v1", path: f"{path}-v1"}),
        ("c1", "Add product pages", "c0", {"src/products.py": "products-v1"}),
    ]
    if bad_id == "c3":
        specs.append(("c2", "Add tags", "c1", {"src/tags.py": "tags-v1"}))
    specs.append((bad_id, bad, specs[-1][0], {path: f"{path}-broken"}))
    if bad_id == "c2":
        specs.append(("c3", "Add search", "c2", {"src/search.py": "search-v1"}))
    specs.append(("c4", vague, "c3", {local_path: f"{local_path}-v1"}))
    commits = _chain(specs)
    return {
        "initial_state": repo(
            commits=commits,
            branches={"main": "c4"},
            **origin(name, branches={"origin/main": "c3"}, tracking={"main": "origin/main"}),
        ),
        "state_requirements": clean(
            "main",
            *_reverted(bad_id, "main", bad),
            {"type": "branch_history_excludes", "branch": "main", "commits": ["c4"]},
            tip("main~1", message_equals=right, parent_equals="c3", tree_contains={local_path: f"{local_path}-v1"}),
            tip("main", tree_contains={path: f"{path}-v1", local_path: f"{local_path}-v1"}),
            {"type": "branch_history_contains", "branch": "main", "commits": ["c3", bad_id]},
            matches_origin("main"),
        ),
    }


# ---------------------------------------------------------------------------
# 4.3 Completing Rebase Recovery Sequences
# ---------------------------------------------------------------------------


def _rebase_pair(*, branch: str, path: str, base: str, main: str, feature: str, follow_up: str):
    commits = _chain(
        [
            ("c0", "Project baseline", None, {"README.md": "readme-v1", path: base}),
            ("c1", "Main update", "c0", {path: main}),
            ("c2", f"Start {branch}", "c0", {path: feature}),
            ("c3", f"Finish {branch}", "c2", {follow_up: f"{follow_up}-v1"}),
        ]
    )
    return commits, {"main": "c1", branch: "c3"}


def _abort_stopped_rebase(
    *, branch: str, path: str, base: str, main: str, feature: str, follow_up: str
) -> dict[str, Any]:
    commits, branches = _rebase_pair(
        branch=branch, path=path, base=base, main=main, feature=feature, follow_up=follow_up
    )
    return {
        "initial_state": _stopped_rebase(
            commits, branches, branch=branch, onto="c1", source="c2", remaining=["c3"], path=path
        ),
        "state_requirements": clean(
            branch,
            {"type": "rebase_not_in_progress"},
            points_to(branch, "c3"),
            points_to("main", "c1"),
            conflict_free=True,
        ),
    }


def _continue_rebase(
    *,
    branch: str,
    path: str,
    base: str,
    main: str,
    feature: str,
    follow_up: str,
    resolved: str,
    publish: str | None = None,
) -> dict[str, Any]:
    commits, branches = _rebase_pair(
        branch=branch, path=path, base=base, main=main, feature=feature, follow_up=follow_up
    )
    extra = (
        origin(
            publish,
            branches={"origin/main": "c1", f"origin/{branch}": "c3"},
            tracking={"main": "origin/main", branch: f"origin/{branch}"},
        )
        if publish
        else {}
    )
    rules = [
        {"type": "rebase_not_in_progress"},
        {"type": "branch_history_contains", "branch": branch, "commits": ["c1"]},
        {"type": "commit_is_not_merge", "branch": branch},
        {"type": "commit_count_on_branch_equals", "branch": branch, "count": 4},
        {
            "type": "commit_tree_contains",
            "branch": branch,
            "tree": {path: resolved, follow_up: f"{follow_up}-v1"},
        },
    ]
    if publish:
        rules.append(matches_origin(branch))
    return {
        "initial_state": _stopped_rebase(
            commits,
            branches,
            branch=branch,
            onto="c1",
            source="c2",
            remaining=["c3"],
            path=path,
            **extra,
        ),
        "state_requirements": clean(branch, *rules, conflict_free=True),
    }


def _abort_then_onto(*, branch: str, spike: str, path: str) -> dict[str, Any]:
    shared = "src/charts.js"
    commits = _chain(
        [
            ("c0", "Project baseline", None, {"README.md": "readme-v1", shared: "charts-v1"}),
            ("c1", "Upgrade chart defaults", "c0", {shared: "charts-main"}),
            ("c2", f"Spike: {spike}", "c0", {shared: "charts-spike"}),
            ("c3", f"Spike: tune {spike}", "c2", {"src/spike.css": "spike-v1"}),
            ("c4", f"Start {branch}", "c3", {path: f"{path}-v1"}),
            ("c5", f"Finish {branch}", "c4", {path: f"{path}-v2"}),
        ]
    )
    branches = {"main": "c1", f"spike/{spike}": "c3", branch: "c5"}
    return {
        "initial_state": _stopped_rebase(
            commits,
            branches,
            branch=branch,
            onto="c1",
            source="c2",
            remaining=["c3", "c4", "c5"],
            path=shared,
        ),
        "state_requirements": clean(
            branch,
            {"type": "rebase_not_in_progress"},
            {"type": "branch_history_contains", "branch": branch, "commits": ["c1"]},
            {"type": "branch_history_excludes", "branch": branch, "commits": ["c2", "c3"]},
            {"type": "commit_count_on_branch_equals", "branch": branch, "count": 4},
            {
                "type": "commit_tree_contains",
                "branch": branch,
                "tree": {path: f"{path}-v2", shared: "charts-main"},
            },
            {"type": "commit_tree_excludes", "branch": branch, "paths": ["src/spike.css"]},
            points_to(f"spike/{spike}", "c3"),
            conflict_free=True,
        ),
    }


def _reset_rebase_lease(
    *, name: str, branch: str, kept: str, dropped: str, last: str, tip_id: str
) -> dict[str, Any]:
    """The branch was pushed at ``tip_id``; a bad rebase then dropped ``dropped``."""
    rebased_first, rebased_last = ("c4", "c5") if tip_id == "c6" else ("c4", "c6")
    commits = _chain(
        [
            ("c0", "Project baseline", None, {"README.md": "readme-v1", "docs/usage.md": "usage-v1"}),
            ("c1", "Fix typo in usage docs", "c0", {"docs/usage.md": "usage-v2"}),
            ("c2", kept, "c0", {"src/kept.py": "kept-v1"}),
            ("c3", dropped, "c2", {"src/dropped.py": "dropped-v1"}),
            (tip_id, last, "c3", {"src/main.py": "main-v2"}),
            (rebased_first, kept, "c1", {"src/kept.py": "kept-v1"}),
            (rebased_last, last, rebased_first, {"src/main.py": "main-v2"}),
        ]
    )
    remote = f"origin/{branch}"
    return {
        "initial_state": repo(
            commits=commits,
            branches={"main": "c1", branch: rebased_last},
            head=branch,
            reflog=[
                {"ref": branch, "commit": tip_id, "action": f"commit: {last}"},
                {"ref": branch, "commit": rebased_last, "action": f"rebase (finish): refs/heads/{branch} onto c1"},
            ],
            **origin(
                name,
                branches={"origin/main": "c1", remote: tip_id},
                tracking={"main": "origin/main", branch: remote},
            ),
        ),
        "state_requirements": clean(
            branch,
            {"type": "rebase_not_in_progress"},
            {"type": "branch_history_contains", "branch": branch, "commits": ["c1"]},
            {"type": "commit_is_not_merge", "branch": branch},
            {"type": "commit_count_on_branch_equals", "branch": branch, "count": 5},
            {
                "type": "commit_tree_contains",
                "branch": branch,
                "tree": {
                    "src/kept.py": "kept-v1",
                    "src/dropped.py": "dropped-v1",
                    "src/main.py": "main-v2",
                    "docs/usage.md": "usage-v2",
                },
            },
            matches_origin(branch),
            conflict_free=True,
        ),
    }


FIXTURES: dict[str, dict[str, Any]] = {
    # 4.1
    "reflog-medium-recover-and-publish-search": _recover_and_publish(
        name="library-search",
        path="src/search.py",
        branch="recovery/search-fix",
        steps=[
            ("Search groundwork", "search-groundwork"),
            ("Continue search work", "search-continued"),
            ("Add ranking tests", "search-tested"),
            ("Fix borrower search ranking", "search-ranking-fixed"),
        ],
        reset_to="c0",
    ),
    "reflog-medium-recover-and-publish-billing": _recover_and_publish(
        name="billing-api",
        path="src/billing.py",
        branch="recovery/billing",
        steps=[
            ("Billing groundwork", "billing-groundwork"),
            ("Add invoice model", "billing-invoices"),
            ("Add payment terms", "billing-terms"),
            ("Add late fees", "billing-late-fees"),
            ("Finish billing summary", "billing-summary"),
        ],
        reset_to="c2",
    ),
    "reflog-hard-recover-then-pick-auth": _recover_then_pick(
        path="src/auth.py",
        branch="recovery/auth",
        groundwork="Session groundwork",
        experiment="Experiment: magic links",
        fix="Fix auth token expiry",
        fixed="auth-expiry-fixed",
    ),
    "reflog-hard-recover-then-pick-export": _recover_then_pick(
        path="src/export.py",
        branch="recovery/export",
        groundwork="Export groundwork",
        experiment="Debug: dump every row",
        fix="Fix export date format",
        fixed="export-dates-fixed",
    ),
    # 4.2
    "revert-easy-pull-then-revert-docs": _pull_then_revert(
        name="handbook",
        path="docs/conf.py",
        bad="Switch docs theme",
        bad_id="c3",
        teammate_path="docs/faq.md",
        teammate="Add FAQ page",
    ),
    "revert-easy-pull-then-revert-api": _pull_then_revert(
        name="billing-api",
        path="src/routes.py",
        bad="Rename the orders endpoint",
        bad_id="c4",
        teammate_path="src/health.py",
        teammate="Add health endpoint",
    ),
    "revert-medium-release-branch-pricing": _revert_on_release(
        name="shop-web",
        release="release/2.1",
        path="src/pricing.py",
        bad="Round prices to whole pesos",
        bad_id="c4",
    ),
    "revert-medium-release-branch-auth": _revert_on_release(
        name="ticketing-app",
        release="release/1.8",
        path="src/signin.py",
        bad="Require SSO for every account",
        bad_id="c3",
    ),
    "revert-hard-amend-local-revert-pushed-shop": _amend_then_revert(
        name="shop-web",
        path="src/checkout.py",
        bad="Break checkout",
        bad_id="c2",
        local_path="src/order_export.py",
        vague="wip",
        right="Add order export",
    ),
    "revert-hard-amend-local-revert-pushed-blog": _amend_then_revert(
        name="field-notes",
        path="src/rss.py",
        bad="Shorten feed item IDs",
        bad_id="c3",
        local_path="src/feed_rss.py",
        vague="stuff",
        right="Add RSS feed",
    ),
    # 4.3
    "rebase-easy-abort-stopped-docs": _abort_stopped_rebase(
        branch="feature/docs-search",
        path="docs/index.md",
        base="# Handbook",
        main="# Team Handbook",
        feature="# Handbook\nSearch: press /",
        follow_up="docs/search.md",
    ),
    "rebase-easy-continue-config": _continue_rebase(
        branch="feature/config-loader",
        path="config/app.yml",
        base="loader: yaml",
        main="loader: toml",
        feature="loader: yaml\nwatch: true",
        follow_up="docs/config.md",
        resolved="loader: toml\nwatch: true",
    ),
    "rebase-hard-continue-then-lease-search": _continue_rebase(
        branch="feature/search",
        path="src/search.py",
        base="RESULTS = 10",
        main="RESULTS = 20",
        feature="RESULTS = 10\nFUZZY = True",
        follow_up="tests/test_search.py",
        resolved="RESULTS = 20\nFUZZY = True",
        publish="library-search",
    ),
    "rebase-hard-continue-then-lease-billing": _continue_rebase(
        branch="feature/billing",
        path="src/billing.py",
        base="CURRENCY = 'PHP'",
        main="CURRENCY = 'PHP'\nROUNDING = 'half-up'",
        feature="CURRENCY = 'USD'",
        follow_up="docs/billing.md",
        resolved="CURRENCY = 'USD'\nROUNDING = 'half-up'",
        publish="billing-api",
    ),
    "rebase-hard-abort-then-onto-reports": _abort_then_onto(
        branch="feature/reports", spike="charts", path="src/reports.js"
    ),
    "rebase-hard-abort-then-onto-ui": _abort_then_onto(
        branch="feature/table-ui", spike="new-grid", path="src/table.js"
    ),
    "rebase-hard-reset-rebase-lease-cli": _reset_rebase_lease(
        name="cli-tool",
        branch="feature/cli-flags",
        kept="Parse --verbose flag",
        dropped="Parse --quiet flag",
        last="Use flags in main",
        tip_id="c6",
    ),
    "rebase-hard-reset-rebase-lease-api": _reset_rebase_lease(
        name="billing-api",
        branch="feature/rate-limits",
        kept="Add retry budget",
        dropped="Add rate limiter",
        last="Wire limiter into API",
        tip_id="c5",
    ),
}
