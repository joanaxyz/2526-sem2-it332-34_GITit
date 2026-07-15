"""Stateful intermediate and advanced incidents for curriculum v3.

Every incident has four strategy-distinct variants.  The variants share the
chapter diagnostic command, dedicated incident branch, and final DAG
verification, but they require different mutations:

* author a new repair commit from pending work;
* transplant a donor patch without taking its branch history;
* squash-integrate a divergent feature branch;
* revert a bad public commit with an additive correction.

This keeps variant rotation from becoming token substitution while preserving a
single variant-safe objective checklist.
"""

from __future__ import annotations

from dataclasses import dataclass

from .common import commit, ev, q, repo, v


@dataclass(frozen=True)
class ChapterIncident:
    chapter: str
    story_slug: str
    story_title: str
    level_type: str
    diagnostic_usage: str
    diagnostic_commands: tuple[str, str]
    incident_titles: tuple[str, str]
    operational_theme: str


def _base_commits(prefix: str) -> list[dict]:
    return [
        commit(
            f"{prefix}0",
            "Establish shared foundation",
            [],
            {
                "README.md": "Operations repository\n",
                "src/app.ts": "export const mode = 'base'\n",
            },
        ),
        commit(
            f"{prefix}1",
            "Harden the main service",
            [f"{prefix}0"],
            {
                "README.md": "Operations repository\n",
                "src/app.ts": "export const mode = 'stable'\n",
                "src/health.ts": "export const healthy = true\n",
            },
        ),
        commit(
            f"{prefix}2",
            "Introduce the failing deployment",
            [f"{prefix}1"],
            {
                "README.md": "Operations repository\n",
                "src/app.ts": "export const mode = 'unsafe'\n",
                "src/health.ts": "export const healthy = false\n",
            },
        ),
        commit(
            f"{prefix}3",
            "Prepare isolated relay repair",
            [f"{prefix}0"],
            {
                "README.md": "Operations repository\n",
                "src/app.ts": "export const mode = 'base'\n",
                "src/relay.ts": "export const relay = 'repaired'\n",
            },
        ),
        commit(
            f"{prefix}4",
            "Draft earlier patch series",
            [f"{prefix}0"],
            {
                "README.md": "Operations repository\n",
                "src/app.ts": "export const mode = 'candidate-v1'\n",
            },
        ),
    ]


def _metadata(prefix: str) -> dict:
    return {
        "bisect_good": f"{prefix}0",
        "bisect_bad": f"{prefix}2",
        "first_bad_commit": f"{prefix}2",
        "rerere_paths": ["src/app.ts"],
        "rerere_before": "mode = unsafe",
        "rerere_after": "mode = stable",
        "worktrees": [
            {
                "path": "/workspace/repository",
                "commit": f"{prefix}2",
                "branch": "main",
            },
            {
                "path": "/workspace/hotfix",
                "commit": f"{prefix}3",
                "branch": "donor/relay",
            },
        ],
        "sparse_paths": ["src", "docs/runbooks"],
        "submodules": [
            {
                "commit": "a11ce00",
                "path": "vendor/telemetry",
                "describe": "heads/main",
                "initialized": True,
            }
        ],
        "signatures": {
            f"{prefix}1": {"signer": "Release Bot"},
            "v1.0": {"signer": "Release Bot"},
        },
    }


def _state(prefix: str, *, mode: str) -> dict:
    commits = _base_commits(prefix)
    branches = {
        "main": f"{prefix}2" if mode == "revert" else f"{prefix}1",
        "feature/work": f"{prefix}3",
        "donor/patch": f"{prefix}3",
        "old/series": f"{prefix}4",
    }
    state = repo(
        commits=commits,
        branches=branches,
        head="main",
        tags={"v1.0": {"target": f"{prefix}0", "annotated": True, "message": "stable base"}},
        remotes={"origin": "https://example.test/nexus/operations.git"},
        remote_branches={"origin/main": branches["main"]},
        upstream_tracking={"main": "origin/main"},
        config={"user.name": "Repository Marshal", "user.email": "marshal@example.test"},
        operation_metadata=_metadata(prefix),
    )
    if mode == "author":
        state["working_tree"] = {
            "src/repair.ts": {
                "status": "untracked",
                "content": "export const repair = 'verified'\n",
            }
        }
    return state


def _requirements(branch: str, message: str, path: str | None = None) -> dict:
    latest = {"branch": branch, "message_contains": [message]}
    if path:
        latest["contains_paths"] = [path]
    return {
        "head_branch": branch,
        "latest_commit": latest,
        "working_tree_clean": True,
        "staging_empty": True,
        "min_commits_on_branch": {branch: 3},
    }


def _render(command: str, prefix: str) -> str:
    return (
        command.replace("{p}", prefix)
        .replace("{head}", f"{prefix}2")
        .replace("{stable}", f"{prefix}1")
    )


def _required_family(command: str) -> str:
    parts = command.split()
    return " ".join(parts[:2])


def _variants(*, slug: str, diagnostic: str, suffix: str) -> list[dict]:
    rows: list[dict] = []

    branch = f"incident/{suffix}-authored"
    state = _state("a", mode="author")
    rows.append(
        v(
            f"{slug}-author",
            "Author the repair from pending work",
            state,
            [
                _render(diagnostic, "a"),
                "git status",
                f"git switch -c {branch}",
                "git add src/repair.ts",
                "git diff --staged",
                f"git commit -m 'Resolve {suffix} incident'",
                f"git tag {suffix}-authored",
                "git log --oneline --graph --all",
            ],
            ev(
                _requirements(branch, "Resolve", "src/repair.ts"),
                required=[_required_family(_render(diagnostic, "a")), "git switch -c", "git add", "git commit", "git log"],
            ),
            details=[
                branch,
                "src/repair.ts",
                f"Resolve {suffix} incident",
                f"{suffix}-authored",
            ],
        )
    )

    branch = f"incident/{suffix}-transplanted"
    state = _state("b", mode="transplant")
    rows.append(
        v(
            f"{slug}-transplant",
            "Transplant the isolated patch",
            state,
            [
                _render(diagnostic, "b"),
                "git log --oneline --graph --all",
                f"git switch -c {branch} main",
                "git cherry-pick --no-commit b3",
                "git status",
                f"git commit -m 'Transplant {suffix} repair'",
                f"git tag {suffix}-transplanted",
                "git log --oneline --graph --all",
            ],
            ev(
                _requirements(branch, "Transplant", "src/relay.ts"),
                required=[_required_family(_render(diagnostic, "b")), "git switch -c", "git cherry-pick --no-commit", "git commit", "git log"],
            ),
            details=[
                branch,
                "b3",
                f"Transplant {suffix} repair",
                f"{suffix}-transplanted",
            ],
        )
    )

    branch = f"incident/{suffix}-integrated"
    state = _state("c", mode="integrate")
    rows.append(
        v(
            f"{slug}-integrate",
            "Integrate the divergent repair as one reviewed snapshot",
            state,
            [
                _render(diagnostic, "c"),
                "git merge-base main feature/work",
                f"git switch -c {branch} main",
                "git merge --squash feature/work",
                "git status",
                f"git commit -m 'Integrate {suffix} repair'",
                f"git tag {suffix}-integrated",
                "git log --oneline --graph --all",
            ],
            ev(
                _requirements(branch, "Integrate", "src/relay.ts"),
                required=[_required_family(_render(diagnostic, "c")), "git merge-base", "git switch -c", "git merge --squash", "git commit", "git log"],
            ),
            details=[
                branch,
                "feature/work",
                f"Integrate {suffix} repair",
                f"{suffix}-integrated",
            ],
        )
    )

    branch = f"incident/{suffix}-reverted"
    state = _state("d", mode="revert")
    rows.append(
        v(
            f"{slug}-revert",
            "Reverse the shared failure additively",
            state,
            [
                _render(diagnostic, "d"),
                "git log --oneline --graph --all",
                f"git switch -c {branch} main",
                "git revert --no-edit d2",
                f"git tag {suffix}-reverted",
                "git show",
                "git log --oneline --graph --all",
            ],
            ev(
                _requirements(branch, "Revert"),
                required=[_required_family(_render(diagnostic, "d")), "git switch -c", "git revert", "git show", "git log"],
            ),
            details=[
                branch,
                "d2",
                f"{suffix}-reverted",
            ],
        )
    )
    return rows


def _narrative(incident: ChapterIncident, title: str, index: int) -> dict:
    location = "the frozen Citadel" if incident.story_slug == "frostbound-citadel" else "Neon Backstreets"
    return {
        "arrival": f"You arrive at {location} to take ownership of {title.lower()}.",
        "problem_discovery": (
            f"The visible branch tips do not explain the operational failure. {incident.operational_theme}"
        ),
        "repository_evidence": (
            "The repository contains a stable mainline, a divergent repair, an isolated donor patch, "
            "an earlier patch series, and a known bad deployment."
        ),
        "operational_goal": (
            "Use the chapter diagnostic, select a safe strategy, create the incident branch named in "
            "Copy details, produce a corrective commit with the exact message shown there, add the "
            "listed tag, and verify the final graph."
        ),
        "consequence_of_failure": (
            "A plausible-looking but unverified history would either discard another team's work or leave "
            "the failing deployment authoritative."
        ),
        "successful_handoff": (
            f"Incident stream {index} ends with a clean branch, a visible correction, and evidence the next team can audit."
        ),
    }


def _level(incident: ChapterIncident, *, index: int, diagnostic: str) -> dict:
    title = (
        incident.incident_titles[index - 1]
        if index <= len(incident.incident_titles)
        else "Verify the Operational Handoff"
    )
    slug = f"{incident.chapter}-incident-{index}"
    suffix = f"{incident.chapter.replace('_', '-').replace('skyline-', 'sn-').replace('frost-', 'fc-')}-{index}"
    narrative = _narrative(incident, title, index)
    return q(
        incident.diagnostic_usage,
        slug,
        title,
        (
            f"{narrative['arrival']} {narrative['problem_discovery']} "
            f"{narrative['repository_evidence']}"
        ),
        (
            f"{narrative['operational_goal']} {narrative['consequence_of_failure']} "
            f"{narrative['successful_handoff']}"
        ),
        _variants(slug=slug, diagnostic=diagnostic, suffix=suffix),
        checks=[
            {
                "label": "Inspect the chapter-specific evidence before changing history.",
                "requirement": {"required_commands": [_required_family(diagnostic)]},
            },
            {
                "label": "Move the repair onto a dedicated incident branch.",
                "requirement": {"required_commands": ["git switch -c"]},
            },
            {
                "label": "Verify the resulting repository graph before handoff.",
                "requirement": {"required_commands": ["git log"]},
            },
        ],
        min_counted_commands=4,
        max_counted_commands=12 if incident.level_type == "applied_scenario" else 16,
        adventure=f"{incident.chapter}-incidents",
        workflow=True,
        level_type=incident.level_type,
        narrative_brief=narrative,
        # Forms genuinely exercised by EVERY variant of this wave (the four
        # strategies additionally diverge on cherry-pick/squash/revert, which
        # therefore must not be tagged wave-wide).
        command_forms=[
            "git-switch/create",
            "git-tag/lightweight-advanced",
            "git-log/graph-all",
        ],
    )


INCIDENTS = (
    ChapterIncident("frost-temper-the-commit", "frostbound-citadel", "Frostbound Citadel", "applied_scenario", "git-diff/stat-advanced", ("git diff --stat", "git diff --check"), ("Separate the Frozen Patch", "Rebuild the Review Boundary"), "The incoming change set mixes deployable work with review noise."),
    ChapterIncident("frost-choose-the-integration", "frostbound-citadel", "Frostbound Citadel", "applied_scenario", "git-rev-list/revision-set", ("git rev-list --count {p}0..main", "git merge-base main feature/work"), ("Choose the Safe Gate", "Preserve the Integration Record"), "Several integration shapes would produce different review and rollback histories."),
    ChapterIncident("frost-survive-the-conflict", "frostbound-citadel", "Frostbound Citadel", "applied_scenario", "git-merge-tree/branches", ("git merge-tree main feature/work", "git merge-base main feature/work"), ("Forecast the Collision", "Resolve the Shared Rune"), "A clean command exit is not enough; the resulting tree must preserve both teams' intent."),
    ChapterIncident("frost-move-the-patch", "frostbound-citadel", "Frostbound Citadel", "applied_scenario", "git-range-diff/series", ("git range-diff {p}0..old/series {p}0..feature/work", "git show {p}3"), ("Carry the Relay Patch", "Recover the Interrupted Transfer"), "Only the useful patch should move; its unrelated branch history must stay behind."),
    ChapterIncident("frost-reforge-the-branch", "frostbound-citadel", "Frostbound Citadel", "applied_scenario", "git-range-diff/series", ("git range-diff {p}0..old/series {p}0..feature/work", "git log --oneline --graph --all"), ("Reforge the Review Series", "Prove the Rewrite"), "A rewritten branch must preserve patch intent while changing ancestry."),
    ChapterIncident("frost-govern-the-remote", "frostbound-citadel", "Frostbound Citadel", "applied_scenario", "git-branch/tracking", ("git branch -vv", "git remote -v"), ("Read the Signal Towers", "Publish Without Overwriting"), "Local and remote refs disagree, and an unsafe publication could erase a newer report."),
    ChapterIncident("frost-deliver-the-release", "frostbound-citadel", "Frostbound Citadel", "applied_scenario", "git-shortlog/numbered", ("git shortlog -sn", "git describe --tags"), ("Assemble the Release Evidence", "Mark the Candidate"), "The release needs traceable contributors, a human-readable version, and a visible correction."),
    ChapterIncident("frost-hunt-the-regression", "frostbound-citadel", "Frostbound Citadel", "mastery_incident", "git-bisect/run", ("git bisect run test-suite", "git bisect log"), ("Find the First Frozen Failure", "Repair the Located Regression"), "A failing deployment must be narrowed to the first bad commit before the repair is trusted."),
    ChapterIncident("frost-publish-the-core", "frostbound-citadel", "Frostbound Citadel", "mastery_incident", "git-verify-tag/tag", ("git verify-tag v1.0", "git show-ref"), ("Audit the Restored Core", "Publish the Final Heat History"), "The final Citadel history must be inspectable, tagged, and safe to hand to every settlement."),
    ChapterIncident("skyline-revision-language", "neon-backstreets", "Neon Backstreets", "mastery_incident", "git-rev-parse/revision", ("git rev-parse HEAD~1", "git rev-list --count {p}0..main"), ("Resolve the Incident Coordinates", "Name the Exact History Set"), "The district incident cannot be repaired until symbolic revision expressions identify the correct objects."),
    ChapterIncident("skyline-hidden-history", "neon-backstreets", "Neon Backstreets", "mastery_incident", "git-blame/path", ("git blame src/app.ts", "git grep stable"), ("Trace the Changed Line", "Search the Archive for the Fault"), "The visible branch tip hides which change and content path produced the operational behavior."),
    ChapterIncident("skyline-first-broken-commit", "neon-backstreets", "Neon Backstreets", "mastery_incident", "git-bisect/run", ("git bisect run integration-test", "git bisect log"), ("Automate the Regression Search", "Preserve the Bisect Evidence"), "The district needs a repeatable first-bad result rather than a guess based on the latest commit."),
    ChapterIncident("skyline-repeated-conflict", "neon-backstreets", "Neon Backstreets", "mastery_incident", "git-rerere/status", ("git rerere status", "git rerere diff"), ("Inspect the Resolution Memory", "Reuse the Proven Conflict Repair"), "Recurring conflicts should be resolved from recorded evidence without blindly accepting stale content."),
    ChapterIncident("skyline-many-realities", "neon-backstreets", "Neon Backstreets", "mastery_incident", "git-worktree/list", ("git worktree list", "git sparse-checkout list"), ("Map the Parallel Work Floors", "Repair the Reduced Workspace"), "Multiple worktrees and sparse paths hide where a branch is checked out and which files are intentionally absent."),
    ChapterIncident("skyline-enchant-behavior", "neon-backstreets", "Neon Backstreets", "mastery_incident", "git-config/get", ("git config --get user.name", "git config --list"), ("Audit the Effective Configuration", "Correct the Automation Contract"), "Configuration precedence can make identical commands behave differently across machines and worktrees."),
    ChapterIncident("skyline-guard-the-archive", "neon-backstreets", "Neon Backstreets", "mastery_incident", "git-verify-commit/commit", ("git verify-commit {p}1", "git verify-tag v1.0"), ("Verify the Release Identity", "Quarantine the Untrusted Ref"), "A graph can be structurally valid while still being authored or tagged by an untrusted identity."),
    ChapterIncident("skyline-restore-maintain", "neon-backstreets", "Neon Backstreets", "mastery_incident", "git-fsck/full", ("git fsck --full", "git count-objects -vH"), ("Inspect the Object Store", "Recover Before Maintenance"), "Cleanup must not begin until dangling or broken objects have been distinguished from disposable data."),
    # Usage is for-each-ref (taught in this chapter's drills); show-ref stays a
    # frost-taught form and only appears as an untagged supporting read here, so
    # Frostbound completion never depends on skyline waves.
    ChapterIncident("skyline-serve-the-city", "neon-backstreets", "Neon Backstreets", "mastery_incident", "git-for-each-ref/all", ("git for-each-ref", "git show-ref"), ("Audit the Served Refs", "Repair the Synchronization Boundary"), "Repository services must expose the intended refs and no accidental internal branch."),
    ChapterIncident("skyline-migrate-the-grid", "neon-backstreets", "Neon Backstreets", "mastery_incident", "git-cat-file/type", ("git cat-file -t {p}1", "git ls-tree {p}1"), ("Inspect the Migration Objects", "Verify the Imported History"), "A migration is incomplete if refs exist but their object trees or authorship cannot be verified."),
    ChapterIncident("skyline-git-machinery", "neon-backstreets", "Neon Backstreets", "mastery_incident", "git-symbolic-ref/head", ("git symbolic-ref HEAD", "git show-ref"), ("Trace HEAD to Its Ref", "Repair the Visible Reference"), "The visible branch label must be connected to the correct immutable object chain."),
    ChapterIncident("skyline-command-laboratory", "neon-backstreets", "Neon Backstreets", "mastery_incident", "git-for-each-ref/all", ("git for-each-ref", "git rev-parse HEAD"), ("Classify the Remaining Interfaces", "Prove the Final Ref Transition"), "Specialized helpers and plumbing must be classified safely while the scored outcome remains a real ref and DAG change."),
)


LEVELS = [
    _level(incident, index=index, diagnostic=diagnostic)
    for incident in INCIDENTS
    for index, diagnostic in enumerate(
        (*incident.diagnostic_commands, "git log --oneline --graph --all"),
        start=1,
    )
]

__all__ = ["INCIDENTS", "LEVELS"]
