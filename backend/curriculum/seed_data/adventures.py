# content-architecture-hardening (Phase 4): multi-wave level plans.
#
# By default the seed authors one AdventureLevel per scenario (1 command, 1
# monster). A wave plan REPLACES that 1:1 layout for the named adventure with
# authored multi-wave levels: each level bundles several scenarios into waves
# (one monster per slot), and a scenario may be re-referenced by a later level so
# the runtime serves it as a different variant (per-scenario LRU). Mastery then
# Records authored repetition for Git command practice - a command is mastered only after every slot that
# exercises it is solved.
#
# `waves` is a list of waves; each wave is a list of scenario slugs (the q()
# slugs authored in adventure_levels.py). Adventures without a plan keep the 1:1
# layout. Chapter 1's "found-a-repository" is the reference.
from curriculum.seed_data.blueprint_overlay import BLUEPRINT_ADVENTURE_LEVELS


def _waves(*scenario_slugs: str) -> list[list[str]]:
    """One monster per wave: each scenario slug becomes its own single-slot wave."""
    return [[slug] for slug in scenario_slugs]


ADVENTURE_WAVE_PLANS = {
    # --- Chapter 1: creating-inspecting-repositories ---------------------------
    # One adventure per chapter (1:1): all Chapter 1 levels flat under a single
    # adventure, in concept order (found -> save -> read -> identity). The learner
    # sees a flat list of ~11 levels; the adventure is just the run/mastery carrier.
    "repository-foundations": [
        {
            "slug": "start-a-repository",
            "title": "Start a Repository",
            "waves": _waves(
                "init-current-folder",
                "init-named-folder",
                "init-with-initial-branch",
            ),
        },
        {
            "slug": "copy-a-project",
            "title": "Copy a Project",
            "waves": _waves(
                "clone-default-folder",
                "clone-into-named-folder",
                "clone-specific-branch",
                "clone-shallow-history",
            ),
        },
        {
            "slug": "see-what-changed",
            "title": "See What Changed",
            "waves": _waves(
                "inspect-status",
                "inspect-short-status",
                "inspect-porcelain-status",
                "inspect-ignored-status",
            ),
        },
        {
            "slug": "stage-and-commit",
            "title": "Stage and Commit",
            "waves": _waves("stage-one-file", "commit-staged-snapshot"),
        },
        {
            "slug": "a-second-snapshot",
            "title": "A Second Snapshot",
            "waves": [
                ["stage-visible-folder-work"],
                # Spiral re-entry: commit again as a fresh situation, so the commit
                # move must be solved twice to master (served as a new variant).
                ["commit-staged-snapshot"],
            ],
        },
        {
            "slug": "walk-the-log",
            "title": "Walk the Log",
            "waves": _waves(
                "inspect-compact-history",
                "inspect-graph-history",
                "inspect-limited-history",
            ),
        },
        {
            "slug": "look-closer",
            "title": "Look Closer",
            "waves": _waves("inspect-log-patch", "inspect-log-stat"),
        },
        {
            "slug": "inspect-a-commit",
            "title": "Inspect a Commit",
            "waves": _waves(
                "inspect-named-commit",
                "inspect-head-commit",
                "inspect-commit-paths",
            ),
        },
        {
            "slug": "compare-work",
            "title": "Compare Work",
            "waves": _waves("inspect-working-diff", "inspect-staged-diff"),
        },
        {
            "slug": "set-your-identity",
            "title": "Set Your Identity",
            "waves": _waves(
                "set-global-user-name",
                "set-global-user-email",
                "list-effective-config",
            ),
        },
        {
            "slug": "aliases-and-ignores",
            "title": "Aliases and Ignores",
            "waves": _waves("set-global-alias", "explain-ignore-rule"),
        },
    ],
    # --- Chapter 2: tracking-changes-snapshots ---------------------------------
    # Ch1 reauthor moved the basic diff/stage-one/commit-message/check-ignore
    # scenarios into Chapter 1; Chapter 2 keeps the precision + undo + amend work.
    "stage-with-intent": [
        {
            "slug": "stage-with-precision",
            "title": "Stage with Precision",
            "waves": _waves(
                "inspect-changed-paths",
                "stage-selected-hunks",
                "stage-tracked-updates",
                "stage-all-changes",
            ),
        },
    ],
    "seal-the-snapshot": [
        {
            "slug": "commit-your-work",
            "title": "Commit Your Work",
            "waves": _waves("commit-tracked-changes-directly"),
        },
        {
            "slug": "amend-the-last-commit",
            "title": "Amend the Last Commit",
            "waves": _waves("amend-latest-commit-message", "amend-without-editing-message"),
        },
    ],
    "untrack-and-undo-edits": [
        {
            "slug": "undo-staged-and-working",
            "title": "Undo Staged and Working Edits",
            "waves": _waves("unstage-one-file", "discard-working-file-change"),
        },
        {
            "slug": "stop-tracking-files",
            "title": "Stop Tracking Files",
            "waves": _waves(
                "remove-tracked-file",
                "stop-tracking-local-file",
                "stop-tracking-directory",
            ),
        },
    ],
    # --- Chapter 3: branching-switching ----------------------------------------
    "create-and-move": [
        {
            "slug": "see-and-make-branches",
            "title": "See and Make Branches",
            "waves": _waves(
                "list-local-branches",
                "create-branch-pointer",
                "create-branch-at-start-point",
            ),
        },
        {
            "slug": "move-between-branches",
            "title": "Move Between Branches",
            "waves": _waves(
                "switch-existing-branch",
                "create-and-switch-branch",
                "legacy-create-and-switch",
            ),
        },
    ],
    "detach-and-clean": [
        {
            "slug": "inspect-branches",
            "title": "Inspect Branches",
            "waves": _waves("inspect-branch-tips", "inspect-detached-commit"),
        },
        {
            "slug": "clean-up-branches",
            "title": "Clean Up Branches",
            "waves": _waves("delete-merged-branch", "force-delete-branch-pointer"),
        },
    ],
    # --- Chapter 4: merging-conflicts ------------------------------------------
    "integrate-branches": [
        {
            "slug": "merge-branches",
            "title": "Merge Branches",
            "waves": _waves(
                "find-merge-base",
                "merge-fast-forward-branch",
                "merge-with-merge-commit",
                "squash-merge-branch",
            ),
        },
    ],
    "resolve-conflicts": [
        {
            "slug": "inspect-the-conflict",
            "title": "Inspect the Conflict",
            "waves": _waves(
                "inspect-our-conflict-side",
                "inspect-their-conflict-side",
                "inspect-base-conflict-side",
                "list-unmerged-index-entries",
            ),
        },
        {
            "slug": "choose-a-side",
            "title": "Choose a Side",
            "waves": _waves("choose-our-conflict-side", "choose-their-conflict-side"),
        },
    ],
    "manage-the-merge": [
        {
            "slug": "drive-the-merge",
            "title": "Drive the Merge",
            "waves": _waves(
                "launch-merge-tool",
                "continue-resolved-merge",
                "abort-conflicted-merge",
            ),
        },
    ],
    # --- Chapter 5: undoing-recovery -------------------------------------------
    "step-back-safely": [
        {
            "slug": "reset-hard",
            "title": "Reset Hard",
            "waves": _waves("reset-hard-one-parent", "reset-hard-specific-commit"),
        },
    ],
    "reverse-and-recover": [
        {
            "slug": "reverse-shared-work",
            "title": "Reverse and Recover",
            "waves": _waves(
                "revert-shared-commit",
                "revert-with-generated-message",
                "inspect-reflog-for-recovery",
            ),
        },
    ],
    # --- Chapter 6: temporary-work-patches -------------------------------------
    "shelve-work": [
        {
            "slug": "stash-and-restore",
            "title": "Stash and Restore",
            "waves": _waves("stash-local-work", "list-stashed-work", "pop-top-stash"),
        },
        {
            "slug": "manage-the-stash",
            "title": "Manage the Stash",
            "waves": _waves("apply-top-stash", "drop-top-stash"),
        },
    ],
    "transplant-commits": [
        {
            "slug": "cherry-pick-commits",
            "title": "Cherry-pick Commits",
            "waves": _waves(
                "cherry-pick-one-commit",
                "cherry-pick-without-commit",
                "abort-cherry-pick",
            ),
        },
    ],
    # --- Chapter 7: remotes-collaboration --------------------------------------
    "connect-and-inspect": [
        {
            "slug": "inspect-remotes",
            "title": "Inspect Remotes",
            "waves": _waves("list-remote-names", "inspect-remote-urls"),
        },
        {
            "slug": "fetch-updates",
            "title": "Fetch Updates",
            "waves": _waves("fetch-origin-updates", "fetch-and-prune-stale-refs"),
        },
    ],
    "integrate-upstream": [
        {
            "slug": "pull-upstream",
            "title": "Pull Upstream Work",
            "waves": _waves("pull-fast-forward-update", "pull-with-rebase"),
        },
    ],
    "publish-work": [
        {
            "slug": "publish-branches",
            "title": "Publish Branches",
            "waves": _waves("push-and-set-upstream", "push-current-branch"),
        },
        {
            "slug": "rewrite-and-remove",
            "title": "Rewrite and Remove",
            "waves": _waves("force-with-lease-after-rewrite", "delete-remote-branch"),
        },
    ],
    # --- Advanced stories: command onboarding is a wave, not a payout ---------
    #
    # Frostbound and Neon still introduce each advanced form in one focused
    # command (the intro-first mastery law depends on that), but those micro
    # encounters are grouped into 2-4 wave field operations. A single syntax
    # check must never masquerade as a complete adventure level.
    "frost-temper-the-commit-drills": [
        {
            "slug": "audit-and-stage-the-patch",
            "title": "Audit and Stage the Patch",
            "waves": _waves(
                "ft-intro-diff-stat",
                "ft-intro-diff-check",
                "ft-intro-add-patch",
                "ft-intro-add-update",
            ),
        },
        {
            "slug": "rewrite-the-tip",
            "title": "Rewrite the Tip",
            "waves": _waves("ft-intro-amend", "ft-intro-amend-no-edit"),
        },
        {
            "slug": "step-back-with-intent",
            "title": "Step Back with Intent",
            "waves": _waves(
                "ft-intro-reset-soft",
                "ft-intro-reset-mixed",
                "ft-intro-reset-hard",
            ),
        },
        {
            "slug": "restore-and-mark-known-good",
            "title": "Restore and Mark Known-Good",
            "waves": _waves("ft-intro-restore-source", "ft-intro-tag-checkpoint"),
        },
    ],
    "frost-choose-the-integration-drills": [
        {
            "slug": "compare-and-choose-the-integration",
            "title": "Compare and Choose the Integration",
            "waves": _waves(
                "fc-intro-rev-list-count",
                "fc-intro-three-dot",
                "fc-intro-merge-no-ff",
                "fc-intro-merge-squash",
            ),
        },
    ],
    "frost-survive-the-conflict-drills": [
        {
            "slug": "map-the-conflict",
            "title": "Map the Conflict",
            "waves": _waves(
                "fs-intro-merge-tree",
                "fs-intro-ls-files-u",
                "fs-intro-diff-base",
            ),
        },
        {
            "slug": "compare-both-sides",
            "title": "Compare Both Sides",
            "waves": _waves("fs-intro-diff-ours", "fs-intro-diff-theirs"),
        },
        {
            "slug": "resolve-or-retreat",
            "title": "Resolve or Retreat",
            "waves": _waves(
                "fs-intro-checkout-ours",
                "fs-intro-checkout-theirs",
                "fs-intro-merge-abort",
                "fs-intro-merge-continue",
            ),
        },
    ],
    "frost-move-the-patch-drills": [
        {
            "slug": "inspect-and-shelve-the-patch",
            "title": "Inspect and Shelve the Patch",
            "waves": _waves(
                "fm-intro-range-diff",
                "fm-intro-stash-push",
                "fm-intro-stash-show",
            ),
        },
        {
            "slug": "recover-or-retreat",
            "title": "Recover or Retreat",
            "waves": _waves(
                "fm-intro-stash-apply",
                "fm-intro-stash-pop",
                "fm-intro-stash-drop",
                "fm-intro-cherry-abort",
            ),
        },
    ],
    "frost-reforge-the-branch-drills": [
        {
            "slug": "rebase-or-stand-down",
            "title": "Rebase or Stand Down",
            "waves": _waves("fr-intro-rebase", "fr-intro-rebase-abort"),
        },
    ],
    "frost-govern-the-remote-drills": [
        {
            "slug": "inspect-and-refresh-remotes",
            "title": "Inspect and Refresh Remotes",
            "waves": _waves(
                "fg-intro-branch-vv",
                "fg-intro-fetch-all",
                "fg-intro-fetch-prune",
            ),
        },
        {
            "slug": "integrate-under-guard",
            "title": "Integrate Under Guard",
            "waves": _waves("fg-intro-pull-ff-only", "fg-intro-pull-rebase"),
        },
        {
            "slug": "publish-with-guardrails",
            "title": "Publish with Guardrails",
            "waves": _waves(
                "fg-intro-push-lease",
                "fg-intro-push-delete",
                "fg-intro-set-url",
            ),
        },
    ],
    "frost-deliver-the-release-drills": [
        {
            "slug": "read-the-release-history",
            "title": "Read the Release History",
            "waves": _waves(
                "fd-intro-shortlog",
                "fd-intro-shortlog-numbered",
                "fd-intro-describe",
            ),
        },
        {
            "slug": "mark-and-publish-the-release",
            "title": "Mark and Publish the Release",
            "waves": _waves(
                "fd-intro-tag-annotated",
                "fd-intro-tag-delete",
                "fd-intro-push-tags",
            ),
        },
    ],
    "frost-hunt-the-regression-drills": [
        {
            "slug": "run-and-preserve-the-search",
            "title": "Run and Preserve the Search",
            "waves": _waves("fh-intro-bisect-run", "fh-intro-bisect-log"),
        },
    ],
    "frost-publish-the-core-drills": [
        {
            "slug": "verify-the-release-record",
            "title": "Verify the Release Record",
            "waves": _waves("fp-intro-verify-tag", "fp-intro-show-ref"),
        },
    ],
    "skyline-revision-language-drills": [
        {
            "slug": "locate-and-resolve",
            "title": "Locate and Resolve",
            "waves": _waves("sr-intro-rev-parse", "sr-intro-rev-parse-toplevel"),
        },
    ],
    "skyline-hidden-history-drills": [
        {
            "slug": "search-the-hidden-history",
            "title": "Search the Hidden History",
            "waves": _waves("sh-intro-blame", "sh-intro-grep", "sh-intro-show-path"),
        },
    ],
    "skyline-repeated-conflict-drills": [
        {
            "slug": "read-the-resolution-memory",
            "title": "Read the Resolution Memory",
            "waves": _waves("sc-intro-rerere-status", "sc-intro-rerere-diff"),
        },
    ],
    "skyline-many-realities-drills": [
        {
            "slug": "map-the-parallel-workspaces",
            "title": "Map the Parallel Workspaces",
            "waves": _waves(
                "sm-intro-worktree-list",
                "sm-intro-sparse-list",
                "sm-intro-submodule-status",
            ),
        },
    ],
    "skyline-enchant-behavior-drills": [
        {
            "slug": "audit-the-effective-behavior",
            "title": "Audit the Effective Behavior",
            "waves": _waves("se-intro-config-get", "se-apply-config-audit"),
        },
    ],
    "skyline-guard-the-archive-drills": [
        {
            "slug": "inspect-and-verify-the-commit",
            "title": "Inspect and Verify the Commit",
            "waves": _waves("sg-intro-verify-commit", "sg-apply-inspect-and-verify"),
        },
    ],
    "skyline-restore-maintain-drills": [
        {
            "slug": "measure-and-recover-the-store",
            "title": "Measure and Recover the Store",
            "waves": _waves(
                "sx-intro-fsck",
                "sx-intro-count-objects",
                "sx-intro-reflog-show",
                "sx-intro-reflog-recovery",
            ),
        },
    ],
    "skyline-serve-the-city-drills": [
        {
            "slug": "audit-the-served-ref-set",
            "title": "Audit the Served Ref Set",
            "waves": _waves("ss-intro-for-each-ref", "ss-apply-audit-served-refs"),
        },
    ],
    "skyline-migrate-the-grid-drills": [
        {
            "slug": "inspect-the-migrated-objects",
            "title": "Inspect the Migrated Objects",
            "waves": _waves("sq-intro-cat-file-type", "sq-intro-ls-tree"),
        },
    ],
    "skyline-git-machinery-drills": [
        {
            "slug": "trace-head-to-the-object",
            "title": "Trace HEAD to the Object",
            "waves": _waves("sy-intro-symbolic-ref", "sy-intro-cat-file-pretty"),
        },
    ],
}

ADVENTURE_WAVE_PLANS.update(BLUEPRINT_ADVENTURE_LEVELS)


ADVENTURE_SOURCES = {
    "creating-inspecting-repositories": [
        {
            "slug": "repository-foundations",
            "title": "Repository Foundations",
        },
    ],
    "tracking-changes-snapshots": [
        {
            "slug": "stage-with-intent",
            "title": "Stage with Intent",
        },
        {
            "slug": "seal-the-snapshot",
            "title": "Seal the Snapshot",
        },
        {
            "slug": "untrack-and-undo-edits",
            "title": "Untrack and Undo Edits",
        },
    ],
    "branching-switching": [
        {
            "slug": "create-and-move",
            "title": "Create and Move",
        },
        {
            "slug": "detach-and-clean",
            "title": "Detach and Clean",
        },
    ],
    "merging-conflicts": [
        {
            "slug": "integrate-branches",
            "title": "Integrate Branches",
        },
        {
            "slug": "resolve-conflicts",
            "title": "Resolve Conflicts",
        },
        {
            "slug": "manage-the-merge",
            "title": "Manage the Merge",
        },
    ],
    "undoing-recovery": [
        {
            "slug": "step-back-safely",
            "title": "Step Back Safely",
        },
        {
            "slug": "reverse-and-recover",
            "title": "Reverse and Recover",
        },
    ],
    "temporary-work-patches": [
        {
            "slug": "shelve-work",
            "title": "Shelve Work",
        },
        {
            "slug": "transplant-commits",
            "title": "Transplant Commits",
        },
    ],
    "remotes-collaboration": [
        {
            "slug": "connect-and-inspect",
            "title": "Connect and Inspect",
        },
        {
            "slug": "integrate-upstream",
            "title": "Integrate Upstream",
        },
        {
            "slug": "publish-work",
            "title": "Publish Work",
        },
    ],
}


# Curriculum v3 story incidents. Advanced chapters use two multi-step incident
# levels each; the final Arcane chapter uses complete beginner handoff workflows.
_V3_INCIDENT_CHAPTERS = [
    "frost-temper-the-commit",
    "frost-choose-the-integration",
    "frost-survive-the-conflict",
    "frost-move-the-patch",
    "frost-reforge-the-branch",
    "frost-govern-the-remote",
    "frost-deliver-the-release",
    "frost-hunt-the-regression",
    "frost-publish-the-core",
    "skyline-revision-language",
    "skyline-hidden-history",
    "skyline-first-broken-commit",
    "skyline-repeated-conflict",
    "skyline-many-realities",
    "skyline-enchant-behavior",
    "skyline-guard-the-archive",
    "skyline-restore-maintain",
    "skyline-serve-the-city",
    "skyline-migrate-the-grid",
    "skyline-git-machinery",
    "skyline-command-laboratory",
]

ADVENTURE_SOURCES["guild-archive-handoff"] = [
    {
        "slug": "guild-archive-handoff-workflows",
        "title": "Guild Handoff Workflows",
    }
]

ADVENTURE_SOURCES.update(
    {
        chapter_slug: [
            {
                "slug": f"{chapter_slug}-drills",
                "title": "Field Training",
            },
            {
                "slug": f"{chapter_slug}-workflows",
                "title": "Applied Workflows",
            },
            {
                "slug": f"{chapter_slug}-incidents",
                "title": "Repository Incidents",
            },
        ]
        for chapter_slug in _V3_INCIDENT_CHAPTERS
    }
)
