"""Playable fieldwork for Frostbound Citadel and Neon Backstreets.

The complete chapter books remain broader than this first playable tranche.  Each
chapter receives three detailed, two-variant field exercises.  Stateful commands
use the established simulator; expert inspection commands use deterministic,
backend-recognized diagnostic execution.
"""

from __future__ import annotations

import copy

from .common import *  # noqa: F403


def _history(*, branch: str = "main", tip: str = "c3") -> dict:
    commits = [
        commit("c0", "Create service shell", [], {"README.md": "service", "src/app.ts": "export const mode = 'base'\n"}),
        commit("c1", "Add request validation", ["c0"], {"README.md": "service", "src/app.ts": "export const mode = 'validated'\n"}),
        commit("c2", "Add metrics endpoint", ["c1"], {"README.md": "service", "src/app.ts": "export const mode = 'metrics'\n", "src/metrics.ts": "export const enabled = true\n"}),
        commit("c3", "Prepare deployment", ["c2"], {"README.md": "deploy", "src/app.ts": "export const mode = 'production'\n", "src/metrics.ts": "export const enabled = true\n"}),
    ]
    return repo(commits=commits, branches={branch: tip}, head=branch)


def _history_alt(*, branch: str = "trunk", tip: str = "d3") -> dict:
    commits = [
        commit("d0", "Create dashboard shell", [], {"README.md": "dashboard", "web/main.ts": "const stage = 'base'\n"}),
        commit("d1", "Add navigation", ["d0"], {"README.md": "dashboard", "web/main.ts": "const stage = 'nav'\n"}),
        commit("d2", "Add accessibility pass", ["d1"], {"README.md": "dashboard", "web/main.ts": "const stage = 'accessible'\n"}),
        commit("d3", "Prepare release candidate", ["d2"], {"README.md": "release", "web/main.ts": "const stage = 'candidate'\n"}),
    ]
    return repo(commits=commits, branches={branch: tip}, head=branch)


def _diag(
    *,
    usage: str,
    adventure: str,
    slug: str,
    title: str,
    story: str,
    task: str,
    command_a: str,
    command_b: str,
    state_a: dict | None = None,
    state_b: dict | None = None,
    required: str | None = None,
    details_a: list[dict] | None = None,
    details_b: list[dict] | None = None,
) -> dict:
    required_command = required or " ".join(command_a.split()[:2])
    return q(
        usage,
        slug,
        title,
        story,
        task,
        [
            v(
                f"{slug}-a",
                "Primary repository",
                copy.deepcopy(state_a or _history()),
                [command_a],
                ev({}, required=[required_command]),
                details=details_a,
            ),
            v(
                f"{slug}-b",
                "Alternate repository",
                copy.deepcopy(state_b or _history_alt()),
                [command_b],
                ev({}, required=[required_command]),
                details=details_b,
            ),
        ],
        checks=[
            {
                "label": "The requested repository evidence was inspected.",
                "requirement": {"required_commands": [required_command]},
            }
        ],
        min_counted_commands=0,
        max_counted_commands=1,
        adventure=adventure,
        workflow=True,
    )


def _move(
    *,
    usage: str,
    adventure: str,
    slug: str,
    title: str,
    story: str,
    task: str,
    command_a: str,
    command_b: str,
    state_a: dict,
    state_b: dict,
    required: str | None = None,
    details_a: list[dict] | None = None,
    details_b: list[dict] | None = None,
) -> dict:
    required_command = required or " ".join(command_a.split()[:2])
    return q(
        usage,
        slug,
        title,
        story,
        task,
        [
            v(
                f"{slug}-a",
                "Primary repository",
                copy.deepcopy(state_a),
                [command_a],
                ev({}, required=[required_command]),
                details=details_a,
            ),
            v(
                f"{slug}-b",
                "Alternate repository",
                copy.deepcopy(state_b),
                [command_b],
                ev({}, required=[required_command]),
                details=details_b,
            ),
        ],
        checks=[
            {
                "label": "The repository was moved into the requested safe state.",
                "requirement": {"required_commands": [required_command]},
            }
        ],
        min_counted_commands=1,
        max_counted_commands=1,
        adventure=adventure,
        workflow=True,
    )


def _merge_repo(*, main_tip: str, feature_tip: str, prefix: str = "c") -> dict:
    root = f"{prefix}0"
    main = f"{prefix}1"
    feature = f"{prefix}2"
    commits = [
        commit(root, "Shared foundation", [], {"src/app.ts": "base\n"}),
        commit(main, "Mainline hardening", [root], {"src/app.ts": "main\n"}),
        commit(feature, "Feature delivery", [root], {"src/app.ts": "base\n", "src/feature.ts": "ready\n"}),
    ]
    return repo(commits=commits, branches={"main": main_tip, "feature/delivery": feature_tip})


def _conflict_repo(*, prefix: str = "c") -> dict:
    root, main, feature = f"{prefix}0", f"{prefix}1", f"{prefix}2"
    commits = [
        commit(root, "Shared timeout", [], {"src/config.ts": "timeout=1000\n"}),
        commit(main, "Main timeout", [root], {"src/config.ts": "timeout=5000\n"}),
        commit(feature, "Feature timeout", [root], {"src/config.ts": "timeout=2500\n"}),
    ]
    return repo(
        commits=commits,
        branches={"main": main, "feature/timeout": feature},
        working_tree={"src/config.ts": {"status": "conflicted", "content": "<<<<<<< HEAD\ntimeout=5000\n=======\ntimeout=2500\n>>>>>>> feature/timeout"}},
        conflicts=["src/config.ts"],
        conflict_details={"src/config.ts": {"base": "timeout=1000", "ours": "timeout=5000", "theirs": "timeout=2500", "merge_branch": "feature/timeout"}},
        merge_parent=feature,
        merge_abort_state=repo(commits=commits, branches={"main": main, "feature/timeout": feature}),
    )


# Frostbound Citadel ---------------------------------------------------------

_frost_reset_a = _history()
_frost_reset_b = _history_alt()

_frost_merge_a = _merge_repo(main_tip="c1", feature_tip="c2")
_frost_merge_b = _merge_repo(main_tip="m1", feature_tip="m2", prefix="m")

_frost_stash_a = _history()
_frost_stash_a["working_tree"] = {"src/notes.ts": {"status": "untracked", "content": "draft\n"}}
_frost_stash_b = _history_alt()
_frost_stash_b["working_tree"] = {"web/experiment.ts": {"status": "untracked", "content": "trial\n"}}

_frost_rebase_a = _merge_repo(main_tip="c1", feature_tip="c2")
_frost_rebase_a["head"] = {"type": "branch", "name": "feature/delivery"}
_frost_rebase_b = _merge_repo(main_tip="m1", feature_tip="m2", prefix="m")
_frost_rebase_b["head"] = {"type": "branch", "name": "feature/delivery"}

_frost_remote_a = _history()
_frost_remote_a.update({
    "remotes": {"origin": "https://example.test/ice/service.git"},
    "remote_branches": {"origin/main": "c2", "origin/obsolete": "c1"},
    "upstream_tracking": {"main": "origin/main"},
    "remote_updates": {"origin/main": "c3", "origin/obsolete": None},
})
_frost_remote_b = _history_alt()
_frost_remote_b.update({
    "remotes": {"origin": "https://example.test/ice/dashboard.git"},
    "remote_branches": {"origin/trunk": "d2", "origin/retired": "d1"},
    "upstream_tracking": {"trunk": "origin/trunk"},
    "remote_updates": {"origin/trunk": "d3", "origin/retired": None},
})

_frost_release_a = _history()
_frost_release_b = _history_alt()

LEVELS = [
    _diag(
        usage="git-diff/stat-advanced",
        adventure="frost-temper-the-commit-fieldwork",
        slug="frost-read-change-shape",
        title="Read the Shape of a Change",
        story="A repair convoy arrives with a broad set of edits, but the forge cannot accept a snapshot until its scope is understood.",
        task="Inspect the change summary before deciding how the work should be divided.",
        command_a="git diff --stat",
        command_b="git diff --stat",
        state_a={**_history(), "working_tree": {"src/app.ts": "candidate\n", "docs/runbook.md": "deploy\n"}},
        state_b={**_history_alt(), "working_tree": {"web/main.ts": "candidate\n", "docs/review.md": "review\n"}},
        required="git diff --stat",
    ),
    _diag(
        usage="git-diff/check-whitespace",
        adventure="frost-temper-the-commit-fieldwork",
        slug="frost-check-patch-hygiene",
        title="Check Patch Hygiene",
        story="The frozen gate rejects malformed patches; invisible whitespace damage must be detected before the snapshot is rewritten.",
        task="Run the whitespace safety inspection on the pending work.",
        command_a="git diff --check",
        command_b="git diff --check",
        state_a={**_history(), "working_tree": {"src/app.ts": "const ready = true;   \n"}},
        state_b={**_history_alt(), "working_tree": {"web/main.ts": "const ready = true;\t\n"}},
        required="git diff --check",
    ),
    _move(
        usage="git-reset/soft",
        adventure="frost-temper-the-commit-fieldwork",
        slug="frost-reopen-last-snapshot",
        title="Reopen the Last Snapshot",
        story="The latest local snapshot contains the right files but the wrong boundary. Its changes must remain staged while the branch pointer steps back.",
        task="Move the current branch to the previous commit without discarding or unstaging the snapshot's changes.",
        command_a="git reset --soft c2",
        command_b="git reset --soft d2",
        state_a=_frost_reset_a,
        state_b=_frost_reset_b,
        required="git reset --soft",
        details_a=[{"label": "Target commit", "value": "c2"}],
        details_b=[{"label": "Target commit", "value": "d2"}],
    ),
    _move(
        usage="git-merge/no-ff-advanced",
        adventure="frost-choose-the-integration-fieldwork",
        slug="frost-preserve-integration-checkpoint",
        title="Preserve an Integration Checkpoint",
        story="The delivery branch is ready, and the expedition needs an explicit historical checkpoint even though a simpler topology is possible.",
        task="Integrate the delivery branch while preserving a merge commit.",
        command_a="git merge --no-ff feature/delivery",
        command_b="git merge --no-ff feature/delivery",
        state_a=_frost_merge_a,
        state_b=_frost_merge_b,
        required="git merge --no-ff",
        details_a=[{"label": "Branch", "value": "feature/delivery"}],
        details_b=[{"label": "Branch", "value": "feature/delivery"}],
    ),
    _move(
        usage="git-merge/squash-advanced",
        adventure="frost-choose-the-integration-fieldwork",
        slug="frost-compress-delivery-series",
        title="Compress a Delivery Series",
        story="A noisy prototype branch must be reviewed as one staged change rather than merged with all of its temporary checkpoints.",
        task="Squash the delivery branch into the index without creating a merge commit.",
        command_a="git merge --squash feature/delivery",
        command_b="git merge --squash feature/delivery",
        state_a=_frost_merge_a,
        state_b=_frost_merge_b,
        required="git merge --squash",
        details_a=[{"label": "Branch", "value": "feature/delivery"}],
        details_b=[{"label": "Branch", "value": "feature/delivery"}],
    ),
    _diag(
        usage="git-range-diff/series",
        adventure="frost-choose-the-integration-fieldwork",
        slug="frost-compare-rewritten-series",
        title="Compare Rewritten Patch Series",
        story="Two editions of the same expedition plan have different commit identifiers after review. The meaningful patch changes must be compared, not merely the graph tips.",
        task="Compare the old and revised patch series.",
        command_a="git range-diff main..feature/delivery main..feature/revised",
        command_b="git range-diff trunk..feature/delivery trunk..feature/revised",
        state_a=repo(
            commits=[
                commit("c0", "base", [], {"a": "0"}), commit("c1", "main", ["c0"], {"a": "1"}),
                commit("c2", "feature one", ["c1"], {"a": "1", "b": "1"}), commit("c3", "feature two", ["c2"], {"a": "1", "b": "2"}),
                commit("c4", "feature one revised", ["c1"], {"a": "1", "b": "1"}), commit("c5", "feature two revised", ["c4"], {"a": "1", "b": "3"}),
            ],
            branches={"main": "c1", "feature/delivery": "c3", "feature/revised": "c5"},
        ),
        state_b=repo(
            commits=[
                commit("d0", "base", [], {"a": "0"}), commit("d1", "trunk", ["d0"], {"a": "1"}),
                commit("d2", "feature one", ["d1"], {"a": "1", "b": "1"}), commit("d3", "feature two", ["d2"], {"a": "1", "b": "2"}),
                commit("d4", "feature one revised", ["d1"], {"a": "1", "b": "1"}), commit("d5", "feature two revised", ["d4"], {"a": "1", "b": "3"}),
            ],
            branches={"trunk": "d1", "feature/delivery": "d3", "feature/revised": "d5"},
            head="trunk",
        ),
        required="git range-diff",
    ),
    _diag(
        usage="git-ls-files/unmerged-advanced",
        adventure="frost-survive-the-conflict-fieldwork",
        slug="frost-inspect-conflict-stages",
        title="Inspect Conflict Stages",
        story="A blizzard-interrupted integration left several index stages for the same path. The crew must identify the unresolved entries before choosing a resolution.",
        task="Inspect the unmerged index entries.",
        command_a="git ls-files -u",
        command_b="git ls-files -u",
        state_a=_conflict_repo(),
        state_b=_conflict_repo(prefix="m"),
        required="git ls-files -u",
    ),
    _diag(
        usage="git-diff-conflict/ours-advanced",
        adventure="frost-survive-the-conflict-fieldwork",
        slug="frost-read-our-conflict-change",
        title="Read Our Side of the Conflict",
        story="The current branch changed the same configuration line as the incoming branch. Before accepting either side, the mainline contribution must be isolated and reviewed.",
        task="Inspect the current branch's conflict-side diff for the affected path.",
        command_a="git diff --ours src/config.ts",
        command_b="git diff --ours src/config.ts",
        state_a=_conflict_repo(),
        state_b=_conflict_repo(prefix="m"),
        required="git diff --ours",
        details_a=[{"label": "Conflicted path", "value": "src/config.ts"}],
        details_b=[{"label": "Conflicted path", "value": "src/config.ts"}],
    ),
    _move(
        usage="git-merge/abort-advanced",
        adventure="frost-survive-the-conflict-fieldwork",
        slug="frost-abort-unsafe-integration",
        title="Abort an Unsafe Integration",
        story="The conflict cannot be resolved with the information available at the outpost. The repository must return to its clean pre-merge position without improvised edits.",
        task="Cancel the in-progress merge and restore the pre-merge state.",
        command_a="git merge --abort",
        command_b="git merge --abort",
        state_a=_conflict_repo(),
        state_b=_conflict_repo(prefix="m"),
        required="git merge --abort",
    ),
    _diag(
        usage="git-stash/show-patch",
        adventure="frost-move-the-patch-fieldwork",
        slug="frost-inspect-shelved-patch",
        title="Inspect a Shelved Patch",
        story="A previous expedition left work in the stash. Its patch must be reviewed before any files are restored into the current checkout.",
        task="Inspect the latest stashed patch without applying it.",
        command_a="git stash show -p",
        command_b="git stash show -p",
        state_a={**_history(), "stash_stack": [{"working_tree": {"src/app.ts": "draft"}, "staging": {}, "message": "WIP service"}]},
        state_b={**_history_alt(), "stash_stack": [{"working_tree": {"web/main.ts": "draft"}, "staging": {}, "message": "WIP dashboard"}]},
        required="git stash show",
    ),
    _move(
        usage="git-stash/push-untracked-message",
        adventure="frost-move-the-patch-fieldwork",
        slug="frost-shelve-untracked-expedition",
        title="Shelve an Untracked Expedition",
        story="Urgent repairs require a clean checkout, but the current experiment includes new files that ordinary stash behavior would leave behind.",
        task="Stash tracked and untracked work together with a descriptive message.",
        command_a="git stash push -u -m 'shelve ice probe'",
        command_b="git stash push -u -m 'shelve sensor trial'",
        state_a=_frost_stash_a,
        state_b=_frost_stash_b,
        required="git stash push",
    ),
    _move(
        usage="git-cherry-pick/abort-advanced",
        adventure="frost-move-the-patch-fieldwork",
        slug="frost-abort-patch-transplant",
        title="Abort a Patch Transplant",
        story="A transplanted commit stopped on an incompatible change. Continuing would mix unrelated repairs, so the operation must be rolled back cleanly.",
        task="Abort the in-progress cherry-pick and return to the original branch tip.",
        command_a="git cherry-pick --abort",
        command_b="git cherry-pick --abort",
        state_a={**_history(), "cherry_pick_in_progress": True, "cherry_pick_original_head": "c3", "conflicts": ["src/app.ts"], "working_tree": {"src/app.ts": {"status": "conflicted", "content": "markers"}}},
        state_b={**_history_alt(), "cherry_pick_in_progress": True, "cherry_pick_original_head": "d3", "conflicts": ["web/main.ts"], "working_tree": {"web/main.ts": {"status": "conflicted", "content": "markers"}}},
        required="git cherry-pick --abort",
    ),
    _move(
        usage="git-rebase/branch",
        adventure="frost-reforge-the-branch-fieldwork",
        slug="frost-replay-delivery-on-main",
        title="Replay Delivery on the New Mainline",
        story="The mainline advanced while the delivery branch was under review. The branch's focused patch must be replayed onto the new base before publication.",
        task="Rebase the current delivery branch onto main.",
        command_a="git rebase main",
        command_b="git rebase main",
        state_a=_frost_rebase_a,
        state_b=_frost_rebase_b,
        required="git rebase",
    ),
    _diag(
        usage="git-range-diff/series",
        adventure="frost-reforge-the-branch-fieldwork",
        slug="frost-audit-rebase-result",
        title="Audit a Rebased Series",
        story="After history has been rewritten, the team needs evidence that the intended patch sequence survived and only the requested revision changed.",
        task="Compare the pre-review and post-review patch series.",
        command_a="git range-diff main..feature/delivery main..feature/revised",
        command_b="git range-diff trunk..feature/delivery trunk..feature/revised",
        state_a=copy.deepcopy(repo(
            commits=[commit("c0", "base", [], {"a": "0"}), commit("c1", "main", ["c0"], {"a": "1"}), commit("c2", "old", ["c1"], {"a": "1", "b": "1"}), commit("c3", "new", ["c1"], {"a": "1", "b": "2"})],
            branches={"main": "c1", "feature/delivery": "c2", "feature/revised": "c3"},
        )),
        state_b=copy.deepcopy(repo(
            commits=[commit("d0", "base", [], {"a": "0"}), commit("d1", "trunk", ["d0"], {"a": "1"}), commit("d2", "old", ["d1"], {"a": "1", "b": "1"}), commit("d3", "new", ["d1"], {"a": "1", "b": "2"})],
            branches={"trunk": "d1", "feature/delivery": "d2", "feature/revised": "d3"}, head="trunk",
        )),
        required="git range-diff",
    ),
    _move(
        usage="git-rebase/branch",
        adventure="frost-reforge-the-branch-fieldwork",
        slug="frost-replay-hotfix-on-main",
        title="Replay a Hotfix on the New Base",
        story="A second branch carries a small emergency repair but was created from an outdated checkpoint. It must be moved without merging the obsolete base.",
        task="Rebase the current repair branch onto main.",
        command_a="git rebase main",
        command_b="git rebase main",
        state_a=_frost_rebase_a,
        state_b=_frost_rebase_b,
        required="git rebase",
    ),
    _diag(
        usage="git-branch/tracking",
        adventure="frost-govern-the-remote-fieldwork",
        slug="frost-audit-tracking-relationships",
        title="Audit Tracking Relationships",
        story="Several branches cross the frozen relay, and a mistaken upstream would publish work to the wrong expedition line.",
        task="Inspect verbose branch tracking information before synchronizing.",
        command_a="git branch -vv",
        command_b="git branch -vv",
        state_a=_frost_remote_a,
        state_b=_frost_remote_b,
        required="git branch -vv",
    ),
    _move(
        usage="git-fetch/prune-advanced",
        adventure="frost-govern-the-remote-fieldwork",
        slug="frost-refresh-and-prune-relay",
        title="Refresh and Prune the Relay",
        story="The remote relay contains a new mainline tip and a branch that has been retired. Local remote-tracking refs must reflect both facts.",
        task="Fetch remote updates and prune deleted remote-tracking branches.",
        command_a="git fetch --prune",
        command_b="git fetch --prune",
        state_a=_frost_remote_a,
        state_b=_frost_remote_b,
        required="git fetch --prune",
    ),
    _move(
        usage="git-remote/set-url-advanced",
        adventure="frost-govern-the-remote-fieldwork",
        slug="frost-repoint-origin-relay",
        title="Repoint the Origin Relay",
        story="The expedition migrated to a new relay endpoint. Existing branch and tracking state must remain while only the remote URL changes.",
        task="Update origin to the replacement repository URL.",
        command_a="git remote set-url origin https://example.test/ice/service-v2.git",
        command_b="git remote set-url origin https://example.test/ice/dashboard-v2.git",
        state_a=_frost_remote_a,
        state_b=_frost_remote_b,
        required="git remote set-url",
        details_a=[{"label": "New URL", "value": "https://example.test/ice/service-v2.git"}],
        details_b=[{"label": "New URL", "value": "https://example.test/ice/dashboard-v2.git"}],
    ),
    _diag(
        usage="git-shortlog/numbered",
        adventure="frost-deliver-the-release-fieldwork",
        slug="frost-summarize-contributors",
        title="Summarize Release Contributors",
        story="The summit observatory requires a concise contributor ledger before the release can be announced across the citadel.",
        task="Produce a numbered contributor summary for the current history.",
        command_a="git shortlog -sn main",
        command_b="git shortlog -sn trunk",
        state_a=_frost_release_a,
        state_b=_frost_release_b,
        required="git shortlog",
    ),
    _move(
        usage="git-tag/annotated-advanced",
        adventure="frost-deliver-the-release-fieldwork",
        slug="frost-mark-annotated-release",
        title="Mark an Annotated Release",
        story="The final build needs a durable release marker carrying human context, not merely a lightweight pointer.",
        task="Create the annotated release tag with the supplied message.",
        command_a="git tag -a v2.0.0 -m 'Frostbound release'",
        command_b="git tag -a v3.1.0 -m 'Citadel release'",
        state_a=_frost_release_a,
        state_b=_frost_release_b,
        required="git tag -a",
        details_a=[{"label": "Tag", "value": "v2.0.0"}],
        details_b=[{"label": "Tag", "value": "v3.1.0"}],
    ),
    _diag(
        usage="git-describe/tags",
        adventure="frost-deliver-the-release-fieldwork",
        slug="frost-describe-build-position",
        title="Describe the Build Position",
        story="A deployment artifact was built after the last marked release. The team needs a human-readable name that explains its distance from that tag.",
        task="Describe the current commit relative to the nearest tag.",
        command_a="git describe --tags",
        command_b="git describe --tags",
        state_a={**_frost_release_a, "tags": {"v1.9.0": "c2"}},
        state_b={**_frost_release_b, "tags": {"v3.0.0": "d2"}},
        required="git describe",
    ),
]


# Neon Backstreets ----------------------------------------------------------

_sky_forensics_a = _history()
_sky_forensics_b = _history_alt()
_sky_forensics_a["operation_metadata"] = {
    "bisect_good": "c0", "bisect_bad": "c3", "first_bad_commit": "c2",
    "rerere_paths": ["src/app.ts"], "rerere_before": "mode=legacy", "rerere_after": "mode=safe",
    "worktrees": [
        {"path": "/workspace/repository", "commit": "c3", "branch": "main"},
        {"path": "/workspace/hotfix", "commit": "c2", "branch": "hotfix/metrics"},
    ],
    "sparse_paths": ["src", "docs/runbooks"],
    "submodules": [{"path": "vendor/ui", "commit": "a1b2c3d", "describe": "heads/stable"}],
    "signatures": {"c3": {"signer": "Skyline Release Bot"}, "v2.0.0": {"signer": "Skyline Release Bot"}},
}
_sky_forensics_a["tags"] = {"v2.0.0": {"target": "c3", "annotated": True}}
_sky_forensics_a["config"] = {"user.name": "Contributor A", "core.autocrlf": "input", "alias.audit": "log --graph --all"}
_sky_forensics_a["reflog"] = [{"ref": "HEAD@{0}", "target": "c3", "message": "release"}, {"ref": "HEAD@{1}", "target": "c2", "message": "metrics"}]

_sky_forensics_b["operation_metadata"] = {
    "bisect_good": "d0", "bisect_bad": "d3", "first_bad_commit": "d2",
    "rerere_paths": ["web/main.ts"], "rerere_before": "layout=old", "rerere_after": "layout=accessible",
    "worktrees": [
        {"path": "/workspace/dashboard", "commit": "d3", "branch": "trunk"},
        {"path": "/workspace/accessibility", "commit": "d2", "branch": "audit/accessibility"},
    ],
    "sparse_paths": ["web", "docs/accessibility"],
    "submodules": [{"path": "vendor/charts", "commit": "d4e5f6a", "describe": "heads/main"}],
    "signatures": {"d3": {"signer": "Nexus Release Bot"}, "v3.1.0": {"signer": "Nexus Release Bot"}},
}
_sky_forensics_b["tags"] = {"v3.1.0": {"target": "d3", "annotated": True}}
_sky_forensics_b["config"] = {"user.name": "Contributor B", "core.autocrlf": "false", "alias.audit": "log --first-parent"}
_sky_forensics_b["reflog"] = [{"ref": "HEAD@{0}", "target": "d3", "message": "candidate"}, {"ref": "HEAD@{1}", "target": "d2", "message": "accessibility"}]

LEVELS += [
    _diag(
        usage="git-rev-parse/revision", adventure="skyline-revision-language-fieldwork",
        slug="skyline-resolve-head-parent", title="Resolve a Relative Revision",
        story="A deployment manifest names a commit relative to the current tip. The exact object identifier must be resolved before an automated job consumes it.",
        task="Resolve the parent of the current commit.", command_a="git rev-parse HEAD^", command_b="git rev-parse HEAD^",
        state_a=_sky_forensics_a, state_b=_sky_forensics_b, required="git rev-parse",
    ),
    _diag(
        usage="git-rev-parse/revision", adventure="skyline-revision-language-fieldwork",
        slug="skyline-resolve-branch-tip", title="Resolve a Branch Tip",
        story="Two services exchange branch names, but the release controller needs immutable commit identifiers for reproducible execution.",
        task="Resolve the active branch name to its commit identifier.", command_a="git rev-parse main", command_b="git rev-parse trunk",
        state_a=_sky_forensics_a, state_b=_sky_forensics_b, required="git rev-parse",
    ),
    _diag(
        usage="git-rev-parse/toplevel", adventure="skyline-revision-language-fieldwork",
        slug="skyline-locate-repository-root", title="Locate the Repository Root",
        story="A tool was launched from deep inside a modern monorepo. It must locate the canonical repository root before reading shared configuration.",
        task="Print the top-level repository directory.", command_a="git rev-parse --show-toplevel", command_b="git rev-parse --show-toplevel",
        state_a=_sky_forensics_a, state_b=_sky_forensics_b, required="git rev-parse --show-toplevel",
    ),
    _diag(
        usage="git-blame/path", adventure="skyline-hidden-history-fieldwork",
        slug="skyline-trace-line-ownership", title="Trace Line Ownership",
        story="A production setting changed without a clear ticket. Line-level provenance can identify the commit that last shaped the current file.",
        task="Trace the current file line by line to its last-changing commit.", command_a="git blame src/app.ts", command_b="git blame web/main.ts",
        state_a=_sky_forensics_a, state_b=_sky_forensics_b, required="git blame",
        details_a=[{"label": "Path", "value": "src/app.ts"}], details_b=[{"label": "Path", "value": "web/main.ts"}],
    ),
    _diag(
        usage="git-grep/pattern", adventure="skyline-hidden-history-fieldwork",
        slug="skyline-search-tracked-content", title="Search Tracked Content",
        story="An obsolete mode name may still exist somewhere in the tracked tree. The investigation must search repository content rather than the filesystem indiscriminately.",
        task="Search tracked content for the supplied mode token.", command_a="git grep production HEAD", command_b="git grep candidate HEAD",
        state_a=_sky_forensics_a, state_b=_sky_forensics_b, required="git grep",
        details_a=[{"label": "Pattern", "value": "production"}], details_b=[{"label": "Pattern", "value": "candidate"}],
    ),
    _diag(
        usage="git-blame/path", adventure="skyline-hidden-history-fieldwork",
        slug="skyline-audit-readme-provenance", title="Audit Documentation Provenance",
        story="Release documentation and implementation disagree. Before editing either source, the team needs to know which snapshot last established the current wording.",
        task="Trace the release documentation lines to their source commit.", command_a="git blame README.md", command_b="git blame README.md",
        state_a=_sky_forensics_a, state_b=_sky_forensics_b, required="git blame",
    ),
    _diag(
        usage="git-bisect/run", adventure="skyline-first-broken-commit-fieldwork",
        slug="skyline-run-automated-bisect", title="Run an Automated Bisect",
        story="A regression hides somewhere between the known-good foundation and the failing release. A deterministic test can classify each candidate commit automatically.",
        task="Run the authored test across the bisect range and identify the first bad commit.", command_a="git bisect run test-service", command_b="git bisect run test-dashboard",
        state_a=_sky_forensics_a, state_b=_sky_forensics_b, required="git bisect run",
    ),
    _diag(
        usage="git-bisect/log", adventure="skyline-first-broken-commit-fieldwork",
        slug="skyline-record-bisect-evidence", title="Record Bisect Evidence",
        story="The regression has been isolated, but the incident report needs the good boundary, bad boundary, and final culprit recorded for review.",
        task="Inspect the bisect decision log.", command_a="git bisect log", command_b="git bisect log",
        state_a=_sky_forensics_a, state_b=_sky_forensics_b, required="git bisect log",
    ),
    _diag(
        usage="git-bisect/run", adventure="skyline-first-broken-commit-fieldwork",
        slug="skyline-confirm-first-bad-change", title="Confirm the First Bad Change",
        story="A second service shows the same symptom under a different test harness. The search must be rerun from its independently authored boundaries.",
        task="Run the appropriate automated test and report the first bad commit.", command_a="git bisect run verify-metrics", command_b="git bisect run verify-accessibility",
        state_a=_sky_forensics_a, state_b=_sky_forensics_b, required="git bisect run",
    ),
    _diag(
        usage="git-merge-tree/branches", adventure="skyline-repeated-conflict-fieldwork",
        slug="skyline-preview-virtual-merge", title="Preview a Virtual Merge",
        story="Two teams are approaching the same integration window. The city controller needs a merge forecast without changing either checkout or index.",
        task="Preview the merge result between the selected branches.", command_a="git merge-tree main main", command_b="git merge-tree trunk trunk",
        state_a=_sky_forensics_a, state_b=_sky_forensics_b, required="git merge-tree",
    ),
    _diag(
        usage="git-rerere/status", adventure="skyline-repeated-conflict-fieldwork",
        slug="skyline-inspect-recorded-conflicts", title="Inspect Recorded Conflict Paths",
        story="The same integration collision has appeared across several release trains. The team must see which paths already have reusable resolution records.",
        task="List paths tracked by the recorded-resolution cache.", command_a="git rerere status", command_b="git rerere status",
        state_a=_sky_forensics_a, state_b=_sky_forensics_b, required="git rerere status",
    ),
    _diag(
        usage="git-rerere/diff", adventure="skyline-repeated-conflict-fieldwork",
        slug="skyline-review-recorded-resolution", title="Review a Recorded Resolution",
        story="Automation can replay a previous decision, but the exact before-and-after resolution must be audited before it is trusted again.",
        task="Inspect the recorded resolution diff.", command_a="git rerere diff", command_b="git rerere diff",
        state_a=_sky_forensics_a, state_b=_sky_forensics_b, required="git rerere diff",
    ),
    _diag(
        usage="git-worktree/list", adventure="skyline-many-realities-fieldwork",
        slug="skyline-inventory-worktrees", title="Inventory Parallel Worktrees",
        story="Hotfix, release, and audit work happen in parallel directories attached to one object database. Their paths, branches, and tips must be inventoried before cleanup.",
        task="List all attached worktrees.", command_a="git worktree list", command_b="git worktree list",
        state_a=_sky_forensics_a, state_b=_sky_forensics_b, required="git worktree list",
    ),
    _diag(
        usage="git-sparse-checkout/list", adventure="skyline-many-realities-fieldwork",
        slug="skyline-inspect-sparse-boundary", title="Inspect the Sparse Boundary",
        story="A large monorepo checkout intentionally exposes only selected districts. The active sparse paths must be confirmed before a missing directory is treated as data loss.",
        task="List the paths included by sparse checkout.", command_a="git sparse-checkout list", command_b="git sparse-checkout list",
        state_a=_sky_forensics_a, state_b=_sky_forensics_b, required="git sparse-checkout list",
    ),
    _diag(
        usage="git-submodule/status", adventure="skyline-many-realities-fieldwork",
        slug="skyline-audit-submodule-pins", title="Audit Submodule Pins",
        story="The application depends on separately versioned components. Each nested repository must be checked against the exact commit recorded by the superproject.",
        task="Inspect current submodule paths and pinned commits.", command_a="git submodule status", command_b="git submodule status",
        state_a=_sky_forensics_a, state_b=_sky_forensics_b, required="git submodule status",
    ),
    _diag(
        usage="git-config/get", adventure="skyline-enchant-behavior-fieldwork",
        slug="skyline-read-effective-author", title="Read Effective Author Configuration",
        story="An automated commit used an unexpected identity. Before changing configuration, the effective value visible to this repository must be read precisely.",
        task="Read the effective user.name value.", command_a="git config --get user.name", command_b="git config --get user.name",
        state_a=_sky_forensics_a, state_b=_sky_forensics_b, required="git config --get",
    ),
    _diag(
        usage="git-config/get", adventure="skyline-enchant-behavior-fieldwork",
        slug="skyline-read-line-ending-policy", title="Read the Line-Ending Policy",
        story="A cross-platform diff contains suspicious whole-file changes. The repository's effective line-ending behavior must be confirmed before anyone rewrites files.",
        task="Read the effective core.autocrlf value.", command_a="git config --get core.autocrlf", command_b="git config --get core.autocrlf",
        state_a=_sky_forensics_a, state_b=_sky_forensics_b, required="git config --get",
    ),
    _diag(
        usage="git-config/get", adventure="skyline-enchant-behavior-fieldwork",
        slug="skyline-read-audit-alias", title="Read a Shared Audit Alias",
        story="A team command is documented as an alias, but local behavior differs between services. The exact expansion must be inspected before standardization.",
        task="Read the alias.audit configuration value.", command_a="git config --get alias.audit", command_b="git config --get alias.audit",
        state_a=_sky_forensics_a, state_b=_sky_forensics_b, required="git config --get",
    ),
    _diag(
        usage="git-verify-commit/commit", adventure="skyline-guard-the-archive-fieldwork",
        slug="skyline-verify-release-commit", title="Verify a Release Commit",
        story="The deployment gate accepts only a release commit whose authored signature verifies against the trusted keyring.",
        task="Verify the signature attached to the release commit.", command_a="git verify-commit c3", command_b="git verify-commit d3",
        state_a=_sky_forensics_a, state_b=_sky_forensics_b, required="git verify-commit",
        details_a=[{"label": "Commit", "value": "c3"}], details_b=[{"label": "Commit", "value": "d3"}],
    ),
    _diag(
        usage="git-verify-tag/tag", adventure="skyline-guard-the-archive-fieldwork",
        slug="skyline-verify-release-tag", title="Verify a Release Tag",
        story="A release tag arrived from the signing pipeline. Its annotated object and signer must be verified before the artifact is promoted.",
        task="Verify the signature attached to the release tag.", command_a="git verify-tag v2.0.0", command_b="git verify-tag v3.1.0",
        state_a=_sky_forensics_a, state_b=_sky_forensics_b, required="git verify-tag",
        details_a=[{"label": "Tag", "value": "v2.0.0"}], details_b=[{"label": "Tag", "value": "v3.1.0"}],
    ),
    _diag(
        usage="git-verify-commit/commit", adventure="skyline-guard-the-archive-fieldwork",
        slug="skyline-audit-trusted-snapshot", title="Audit a Trusted Snapshot",
        story="A protected environment references an immutable snapshot directly rather than through a branch. Its signature must be validated before execution.",
        task="Verify the trusted snapshot commit.", command_a="git verify-commit HEAD", command_b="git verify-commit HEAD",
        state_a=_sky_forensics_a, state_b=_sky_forensics_b, required="git verify-commit",
    ),
    _diag(
        usage="git-fsck/full", adventure="skyline-restore-maintain-fieldwork",
        slug="skyline-check-object-connectivity", title="Check Object Connectivity",
        story="A storage incident may have interrupted object transfer. The repository needs a full connectivity and validity check before recovery actions begin.",
        task="Run the full repository integrity inspection.", command_a="git fsck --full", command_b="git fsck --full",
        state_a=_sky_forensics_a, state_b=_sky_forensics_b, required="git fsck --full",
    ),
    _diag(
        usage="git-count-objects/verbose-human", adventure="skyline-restore-maintain-fieldwork",
        slug="skyline-measure-object-storage", title="Measure Object Storage",
        story="Repository operations are slowing as loose objects accumulate. The maintenance team needs a human-readable storage inventory before selecting a cleanup strategy.",
        task="Inspect loose and packed object counts and sizes.", command_a="git count-objects -vH", command_b="git count-objects -vH",
        state_a=_sky_forensics_a, state_b=_sky_forensics_b, required="git count-objects",
    ),
    _diag(
        usage="git-reflog/show-ref", adventure="skyline-restore-maintain-fieldwork",
        slug="skyline-inspect-branch-recovery-log", title="Inspect a Branch Recovery Log",
        story="A branch pointer moved during emergency repair. The local reference log preserves its recent positions and must be read before resetting anything.",
        task="Inspect the reflog for the active branch.", command_a="git reflog show main", command_b="git reflog show trunk",
        state_a=_sky_forensics_a, state_b=_sky_forensics_b, required="git reflog",
    ),
    _diag(
        usage="git-cat-file/type", adventure="skyline-git-machinery-fieldwork",
        slug="skyline-identify-object-type", title="Identify an Object Type",
        story="A low-level maintenance script received an object identifier without context. The object type must be determined before choosing a decoder.",
        task="Inspect the type of the selected object.", command_a="git cat-file -t HEAD", command_b="git cat-file -t HEAD",
        state_a=_sky_forensics_a, state_b=_sky_forensics_b, required="git cat-file -t",
    ),
    _diag(
        usage="git-ls-tree/tree", adventure="skyline-git-machinery-fieldwork",
        slug="skyline-inspect-tree-entries", title="Inspect Tree Entries",
        story="A commit points to a tree snapshot that must be audited without checking it out. The stored paths and blob identities need direct inspection.",
        task="List the entries in the selected revision's tree.", command_a="git ls-tree HEAD", command_b="git ls-tree HEAD",
        state_a=_sky_forensics_a, state_b=_sky_forensics_b, required="git ls-tree",
    ),
    _diag(
        usage="git-show-ref/all", adventure="skyline-git-machinery-fieldwork",
        slug="skyline-inventory-reference-store", title="Inventory the Reference Store",
        story="The data center coordinates branches, tags, and remote-tracking refs through the reference namespace. Every live pointer must be inventoried with its object identifier.",
        task="List all known references and their targets.", command_a="git show-ref", command_b="git show-ref",
        state_a=_sky_forensics_a, state_b=_sky_forensics_b, required="git show-ref",
    ),
]
