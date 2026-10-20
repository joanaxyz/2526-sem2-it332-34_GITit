"""Module 3 wave scenarios: conflict resolution (levels 3.1-3.3)."""

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


def _conflicted(path: str, ours: str, theirs: str, label: str) -> dict[str, Any]:
    return {
        "status": "conflicted",
        "content": f"<<<<<<< HEAD\n{ours}\n=======\n{theirs}\n>>>>>>> {label}\n",
    }


def _stopped_merge(
    commits: list[dict], branches: dict[str, str], *, branch: str, target: str, path: str
) -> dict[str, Any]:
    """main stopped mid-merge of ``branch`` (tip ``target``) on a conflict in ``path``."""
    trees = {item["id"]: item["tree"] for item in commits}
    before = repo(commits=commits, branches=branches)
    ours, theirs = trees[branches["main"]][path], trees[target][path]
    stopped = repo(
        commits=commits,
        branches=branches,
        merge_parent=target,
        merge_abort_state=before,
        conflict_details={
            path: {
                "base": trees["c0"][path],
                "ours": ours,
                "theirs": theirs,
                "merge_branch": branch,
            }
        },
        working_tree={path: _conflicted(path, ours, theirs, branch)},
        operation_metadata={
            "last_merge_branch": branch,
            "last_merge_target": target,
            "last_merge_conflicted": True,
        },
    )
    stopped["conflicts"] = [path]
    return stopped


def _stopped_pick(
    commits: list[dict],
    branches: dict[str, str],
    *,
    head: str,
    source: str,
    path: str,
    staged: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """``head`` stopped mid-cherry-pick of ``source`` on a conflict in ``path``."""
    trees = {item["id"]: item["tree"] for item in commits}
    parents = {item["id"]: item["parents"] for item in commits}
    ours, theirs = trees[branches[head]][path], trees[source][path]
    state = repo(
        commits=commits,
        branches=branches,
        head=head,
        staging=staged or {},
        cherry_pick_in_progress=True,
        cherry_pick_original_head=branches[head],
        cherry_pick_source=source,
        conflict_details={
            path: {"base": trees[parents[source][0]][path], "ours": ours, "theirs": theirs}
        },
        working_tree={path: _conflicted(path, ours, theirs, source)},
        operation_metadata={
            "last_cherry_pick_source": source,
            "last_cherry_pick_conflicted": True,
            "last_cherry_pick_conflict_paths": [path],
        },
    )
    state["conflicts"] = [path]
    return state


# ---------------------------------------------------------------------------
# 3.1 Resolving Merge Conflicts Manually
# ---------------------------------------------------------------------------


def _abort_wrong_merge(*, branch: str, path: str, ours: str, theirs: str) -> dict[str, Any]:
    commits = [
        commit("c0", "Common base", [], {"README.md": "readme-v1", path: f"{path} base"}),
        commit("c1", "Main update", ["c0"], {"README.md": "readme-v1", path: ours}),
        commit("c2", f"Update {branch}", ["c0"], {"README.md": "readme-v1", path: theirs}),
    ]
    branches = {"main": "c1", branch: "c2"}
    return {
        "initial_state": _stopped_merge(commits, branches, branch=branch, target="c2", path=path),
        "state_requirements": clean(
            "main",
            points_to("main", "c1"),
            points_to(branch, "c2"),
            conflict_free=True,
        ),
    }


def _pull_conflict(
    *, name: str, branch: str, path: str, base: str, ours: str, theirs: str, resolved: str
) -> dict[str, Any]:
    commits = [
        commit("c0", "Common base", [], {"README.md": "readme-v1", path: base}),
        commit("c1", f"Update {path} locally", ["c0"], {"README.md": "readme-v1", path: ours}),
        commit("c2", f"Update {path} on origin", ["c0"], {"README.md": "readme-v1", path: theirs}),
    ]
    remote = f"origin/{branch}"
    return {
        "initial_state": repo(
            commits=commits,
            branches={branch: "c1"},
            head=branch,
            **origin(
                name,
                branches={remote: "c0"},
                updates={remote: "c2"},
                tracking={branch: remote},
            ),
        ),
        "state_requirements": clean(
            branch,
            {"type": "commit_is_merge", "branch": branch},
            {"type": "commit_has_parent", "branch": branch, "parent": "c2"},
            {"type": "commit_tree_contains", "branch": branch, "tree": {path: resolved}},
            matches_origin(branch),
            conflict_free=True,
        ),
    }


def _abort_then_redo() -> dict[str, Any]:
    path = "src/payments.py"
    commits = [
        commit("c0", "Common base", [], {path: "FEE = 0.03"}),
        commit("c1", "Main fee update", ["c0"], {path: "FEE = 0.025"}),
        commit("c2", "Payments v1 fee", ["c0"], {path: "FEE = 0.04"}),
        commit("c3", "Payments v2 fee and cap", ["c0"], {path: "FEE = 0.03\nCAP = 500"}),
    ]
    branches = {"main": "c1", "feature/payments-v1": "c2", "feature/payments-v2": "c3"}
    return {
        "initial_state": _stopped_merge(
            commits, branches, branch="feature/payments-v1", target="c2", path=path
        ),
        "state_requirements": clean(
            "main",
            {"type": "commit_is_merge", "branch": "main"},
            {"type": "commit_has_parent", "branch": "main", "parent": "c3"},
            {"type": "branch_history_excludes", "branch": "main", "commits": ["c2"]},
            {
                "type": "commit_tree_contains",
                "branch": "main",
                "tree": {path: "FEE = 0.025\nCAP = 500"},
            },
            conflict_free=True,
        ),
    }


# ---------------------------------------------------------------------------
# 3.2 Resolving Conflicts Using a Merge Tool
# ---------------------------------------------------------------------------


def _tool_merge(
    *,
    branch: str,
    path: str,
    ours: str,
    theirs: str,
    resolved: str,
    config: dict[str, str],
    configured: dict[str, str] | None = None,
) -> dict[str, Any]:
    commits = [
        commit("c0", "Common base", [], {"README.md": "readme-v1", path: f"{path} base"}),
        commit("c1", "Main update", ["c0"], {"README.md": "readme-v1", path: ours}),
        commit("c2", f"Update {branch}", ["c0"], {"README.md": "readme-v1", path: theirs}),
    ]
    return {
        "initial_state": repo(
            commits=commits,
            branches={"main": "c1", branch: "c2"},
            **({"config": dict(configured)} if configured else {}),
        ),
        "state_requirements": clean(
            "main",
            {"type": "commit_is_merge", "branch": "main"},
            {"type": "commit_has_parent", "branch": "main", "parent": "c2"},
            {"type": "commit_tree_contains", "branch": "main", "tree": {path: resolved}},
            conflict_free=True,
            config=config,
        ),
    }


# ---------------------------------------------------------------------------
# 3.3 Cherry-Picking Commits
# ---------------------------------------------------------------------------


def _trace_source() -> dict[str, Any]:
    fix = "Stop double-charging retries"
    base = {"README.md": "readme-v1", "src/charge.py": "charge-v1", "src/report.py": "report-v1"}
    commits = [
        commit("c0", "Billing baseline", [], base),
        commit("c1", "Main groundwork", ["c0"], {**base, "src/report.py": "report-v2"}),
        commit(
            "c2",
            fix,
            ["c1"],
            {**base, "src/report.py": "report-v2", "src/charge.py": "charge-fixed"},
        ),
        commit("c3", "Prepare release 2.4", ["c0"], {**base, "README.md": "readme-2.4"}),
    ]
    return {
        "initial_state": repo(
            commits=commits, branches={"main": "c2", "release-2.4": "c3"}, head="release-2.4"
        ),
        "state_requirements": clean(
            "release-2.4",
            tip(
                "release-2.4",
                message_contains=[fix, "cherry picked from commit c2"],
                parent_equals="c3",
                tree_contains={"src/charge.py": "charge-fixed", "src/report.py": "report-v1"},
            ),
            points_to("main", "c2"),
        ),
    }


def _conflict_continue() -> dict[str, Any]:
    path, fix = "src/auth.py", "Lock accounts after five failures"
    commits = [
        commit("c0", "Auth baseline", [], {path: "MAX_FAILURES = None"}),
        commit("c1", fix, ["c0"], {path: "MAX_FAILURES = 5"}),
        commit("c2", "Main continues", ["c1"], {path: "MAX_FAILURES = 5", "README.md": "main"}),
        commit(
            "c3",
            "Release 1.9 auth logging",
            ["c0"],
            {path: "MAX_FAILURES = None\nLOG_FAILURES = True"},
        ),
    ]
    return {
        "initial_state": repo(
            commits=commits, branches={"main": "c2", "release-1.9": "c3"}, head="release-1.9"
        ),
        "state_requirements": clean(
            "release-1.9",
            {"type": "cherry_pick_not_in_progress"},
            tip(
                "release-1.9",
                message_contains=[fix],
                parent_equals="c3",
                tree_contains={path: "MAX_FAILURES = 5\nLOG_FAILURES = True"},
            ),
            conflict_free=True,
        ),
    }


def _abort_stopped_pick() -> dict[str, Any]:
    path = "src/cart.py"
    base = {path: "TAX = 0.10", "src/totals.py": "totals-v1"}
    commits = [
        commit("c0", "Cart baseline", [], base),
        commit(
            "c1",
            "Cart tax and totals fix",
            ["c0"],
            {path: "TAX = 0.12", "src/totals.py": "totals-v2"},
        ),
        commit(
            "c2",
            "Main continues",
            ["c1"],
            {path: "TAX = 0.12", "src/totals.py": "totals-v2", "README.md": "main"},
        ),
        commit("c3", "Review build tax", ["c0"], {**base, path: "TAX = 0.08"}),
    ]
    branches = {"main": "c2", "release-review-2": "c3"}
    return {
        "initial_state": _stopped_pick(
            commits,
            branches,
            head="release-review-2",
            source="c1",
            path=path,
            staged={"src/totals.py": {"status": "modified", "content": "totals-v2"}},
        ),
        "state_requirements": clean(
            "release-review-2",
            points_to("release-review-2", "c3"),
            {"type": "cherry_pick_not_in_progress"},
            conflict_free=True,
        ),
    }


def _two_fixes_one_commit(
    *, release: str, picks: tuple[str, str], message: str, paths: tuple[str, str]
) -> dict[str, Any]:
    first, second = paths
    base = {
        "README.md": "readme-v1",
        first: f"{first}-v1",
        second: f"{second}-v1",
        "src/new.py": "new-v1",
    }
    tree = dict(base)
    commits = [commit("c0", "Baseline", [], dict(base))]
    for index in range(1, 5):
        if f"c{index}" == picks[0]:
            tree = {**tree, first: f"{first}-fixed"}
            label = f"Fix {first}"
        elif f"c{index}" == picks[1]:
            tree = {**tree, second: f"{second}-fixed"}
            label = f"Fix {second}"
        else:
            tree = {**tree, "src/new.py": f"new-v{index + 1}"}
            label = f"New feature step {index}"
        commits.append(commit(f"c{index}", label, [f"c{index - 1}"], dict(tree)))
    commits.append(
        commit("c5", f"Prepare {release}", ["c0"], {**base, "README.md": f"readme-{release}"})
    )
    return {
        "initial_state": repo(
            commits=commits, branches={"main": "c4", release: "c5"}, head=release
        ),
        "state_requirements": clean(
            release,
            tip(
                release,
                message_equals=message,
                parent_equals="c5",
                tree_contains={
                    first: f"{first}-fixed",
                    second: f"{second}-fixed",
                    "src/new.py": "new-v1",
                },
            ),
            {"type": "commit_count_on_branch_equals", "branch": release, "count": 3},
        ),
    }


def _two_releases() -> dict[str, Any]:
    path, fix = "src/session.py", "Expire sessions on password change"
    base = {"README.md": "readme-v1", path: "session-v1"}
    commits = [
        commit("c0", "Baseline", [], base),
        commit("c1", "Main groundwork", ["c0"], {**base, "README.md": "readme-main"}),
        commit("c2", "Main docs", ["c1"], {**base, "README.md": "readme-main-2"}),
        commit("c3", fix, ["c2"], {"README.md": "readme-main-2", path: "session-secure"}),
        commit("c4", "Prepare release 2.0", ["c0"], {**base, "README.md": "readme-2.0"}),
        commit("c5", "Prepare release 2.1", ["c0"], {**base, "README.md": "readme-2.1"}),
    ]
    picked = {"message_contains": [fix], "tree_contains": {path: "session-secure"}}
    return {
        "initial_state": repo(
            commits=commits, branches={"main": "c3", "release-2.0": "c4", "release-2.1": "c5"}
        ),
        "state_requirements": clean(
            "release-2.0",
            tip("release-2.1", parent_equals="c5", **picked),
            tip("release-2.0", parent_equals="c4", **picked),
            points_to("main", "c3"),
        ),
    }


def _backport_capstone(
    *, release: str, path: str, wrong: str, right: str, lines: dict[str, str]
) -> dict[str, Any]:
    commits = [
        commit("c0", "Baseline", [], {"README.md": "readme-v1", path: lines["base"]}),
        commit("c1", "Main groundwork", ["c0"], {"README.md": "readme-main", path: lines["base"]}),
        commit("c2", wrong, ["c1"], {"README.md": "readme-main", path: lines["experiment"]}),
        commit(
            "c3", f"Prepare {release}", ["c0"], {"README.md": "readme-v1", path: lines["release"]}
        ),
        commit("c4", right, ["c2"], {"README.md": "readme-main", path: lines["fixed"]}),
    ]
    branches = {"main": "c4", release: "c3"}
    return {
        "initial_state": _stopped_pick(commits, branches, head=release, source="c2", path=path),
        "state_requirements": clean(
            release,
            {"type": "cherry_pick_not_in_progress"},
            tip(
                release,
                message_contains=[right, "cherry picked from commit c4"],
                parent_equals="c3",
                tree_contains={path: lines["resolved"]},
            ),
            {"type": "commit_count_on_branch_equals", "branch": release, "count": 3},
            conflict_free=True,
        ),
    }


FIXTURES: dict[str, dict[str, Any]] = {
    # 3.1
    "manual-easy-abort-wrong-branch": _abort_wrong_merge(
        branch="feature/legacy-theme",
        path="src/theme.css",
        ours="--brand: teal;",
        theirs="--brand: grey;",
    ),
    "manual-easy-abort-too-early": _abort_wrong_merge(
        branch="feature/payments",
        path="src/payments.py",
        ours="CURRENCY = 'PHP'",
        theirs="CURRENCY = 'USD'",
    ),
    "manual-medium-pull-conflict-readme": _pull_conflict(
        name="field-notes",
        branch="main",
        path="README.md",
        base="Run the app with: npm start",
        ours="Run the app with: npm run dev",
        theirs="Run the app with: npm start -- --port 3000",
        resolved="Run the app with: npm run dev -- --port 3000",
    ),
    "manual-medium-pull-conflict-config": _pull_conflict(
        name="ticketing-app",
        branch="develop",
        path="config/app.yml",
        base="timeout: 30\nretries: 1",
        ours="timeout: 45\nretries: 1",
        theirs="timeout: 30\nretries: 3",
        resolved="timeout: 45\nretries: 3",
    ),
    "manual-hard-abort-redo-payments": _abort_then_redo(),
    # 3.2
    "mergetool-medium-configure-tool-billing": _tool_merge(
        branch="feature/billing-copy",
        path="src/billing_copy.txt",
        ours="Your invoice is ready.",
        theirs="Your monthly invoice is attached.",
        resolved="Your monthly invoice is ready.",
        config={"merge.tool": "meld"},
    ),
    "mergetool-hard-no-backup-api": _tool_merge(
        branch="feature/api-v3",
        path="src/api_version.py",
        ours="API_VERSION = '2.4'",
        theirs="API_VERSION = '3.0'",
        resolved="API_VERSION = '3.0'\nLEGACY_VERSION = '2.4'",
        config={"merge.tool": "meld", "mergetool.keepBackup": "false"},
        configured={"merge.tool": "meld"},
    ),
    # 3.3
    "cherry-easy-trace-source-hotfix": _trace_source(),
    "cherry-medium-conflict-continue-auth": _conflict_continue(),
    "cherry-medium-abort-stopped-pick": _abort_stopped_pick(),
    "cherry-medium-two-fixes-one-commit-login": _two_fixes_one_commit(
        release="release-1.2",
        picks=("c2", "c3"),
        message="Backport login fixes",
        paths=("src/login.py", "src/session.py"),
    ),
    "cherry-medium-two-fixes-one-commit-tax": _two_fixes_one_commit(
        release="release-3.1",
        picks=("c1", "c4"),
        message="Backport tax fixes",
        paths=("src/tax.py", "src/invoice_tax.py"),
    ),
    "cherry-hard-two-releases-security": _two_releases(),
    "cherry-hard-backport-capstone-export": _backport_capstone(
        release="release-1.4",
        path="src/export.py",
        wrong="Try a streaming export format",
        right="Escape quotes in CSV export",
        lines={
            "base": "return to_csv(rows)",
            "experiment": "return stream_csv(rows)",
            "release": "return to_csv(rows, header=True)",
            "fixed": "return to_csv(rows, quoting=QUOTE_ALL)",
            "resolved": "return to_csv(rows, header=True, quoting=QUOTE_ALL)",
        },
    ),
    "cherry-hard-backport-capstone-login": _backport_capstone(
        release="release-3.0",
        path="src/login.py",
        wrong="Experiment with passwordless login",
        right="Trim spaces from login emails",
        lines={
            "base": "email = form.email",
            "experiment": "email = magic_link(form.email)",
            "release": "email = form.email.lower()",
            "fixed": "email = form.email.strip()",
            "resolved": "email = form.email.strip().lower()",
        },
    ),
}
