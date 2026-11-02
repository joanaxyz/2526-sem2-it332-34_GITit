"""Chapter plan for the three-story Git-it curriculum v3.

The story is ordered by concept dependency. A Challenge in a chapter may combine
commands from that chapter's Adventure and earlier Adventures,
but it must never introduce a Git problem type before Adventure has taught the
pieces needed to solve it.

Note: across seed_data specs, the frozen authoring key ``"module"`` means
"chapter slug" - it predates the chapter naming and stays frozen so authored
entries never need rewriting.
"""


CHAPTERS = [
    {
        "slug": "creating-inspecting-repositories",
        "story": "arcane-spire",
        "number": 1,
        "title": "Repository Foundations",
        "description": (
            "Start from empty or remote projects, then read branch and commit-history signals "
            "before changing anything."
        ),
        "battle_stage": {"parallax": "chapter-01-foundation-hall"},
    },
    {
        "slug": "tracking-changes-snapshots",
        "story": "arcane-spire",
        "number": 2,
        "title": "Tracking Changes and Snapshots",
        "description": (
            "Use diff, staging, commits, restore, and tracked-file removal to create intentional snapshots."
        ),
        "battle_stage": {"parallax": "chapter-02-scriptorium-library"},
    },
    {
        "slug": "branching-switching",
        "story": "arcane-spire",
        "number": 3,
        "title": "Branch Navigation",
        "description": (
            "Create branch pointers, move HEAD safely, branch from old commits, and clean up merged branches."
        ),
        "battle_stage": {"parallax": "chapter-03-branching-gallery"},
    },
    {
        "slug": "merging-conflicts",
        "story": "arcane-spire",
        "number": 4,
        "title": "Merging and Conflict Resolution",
        "description": (
            "Integrate branch histories, recognize fast-forward versus merge commits, and finish conflicted merges."
        ),
        "battle_stage": {"parallax": "chapter-04-convergence-chamber"},
    },
    {
        "slug": "undoing-recovery",
        "story": "arcane-spire",
        "number": 5,
        "title": "Undoing and Recovery",
        "description": (
            "Choose between restore, amend, reset, revert, and reflog-based recovery based on history safety."
        ),
        "battle_stage": {"parallax": "chapter-05-recovery-vault"},
    },
    {
        "slug": "temporary-work-patches",
        "story": "arcane-spire",
        "number": 6,
        "title": "Temporary Work and Patch Movement",
        "description": (
            "Shelve unfinished work and transplant selected commits without dragging an entire branch history."
        ),
        "battle_stage": {"parallax": "chapter-06-stash-workshop"},
    },
    {
        "slug": "remotes-collaboration",
        "story": "arcane-spire",
        "number": 7,
        "title": "Remotes and Collaboration",
        "description": (
            "Read remote relationships, update remote-tracking refs, pull, publish, and handle collaboration history."
        ),
        "battle_stage": {"parallax": "chapter-07-remote-relay"},
    },
]

# Intermediate and advanced campaigns use story-local chapter numbers. Existing
# slugs remain stable so completion rows, mastery, and authored detail retain identity.
CHAPTERS += [
    {
        "slug": "frost-temper-the-commit",
        "story": "frostbound-citadel",
        "number": 1,
        "title": "Temper the Commit",
        "description": (
            "Shape precise patches, amend local history, split tangled work, and choose reset modes "
            "without losing the changes that still matter."
        ),
        "battle_stage": {"parallax": "frost-01-forge-gate"},
    },
    {
        "slug": "frost-choose-the-integration",
        "story": "frostbound-citadel",
        "number": 2,
        "title": "Choose the Integration",
        "description": (
            "Compare fast-forward, merge-commit, and squash strategies by reading ancestry, divergence, "
            "and first-parent history before integrating a branch."
        ),
        "battle_stage": {"parallax": "frost-02-frozen-bridge"},
    },
    {
        "slug": "frost-survive-the-conflict",
        "story": "frostbound-citadel",
        "number": 3,
        "title": "Survive the Conflict",
        "description": (
            "Inspect unmerged index stages, resolve multi-file conflicts deliberately, use merge tools, "
            "and recover safely when an integration must be aborted."
        ),
        "battle_stage": {"parallax": "frost-03-blizzard-courtyard"},
    },
    {
        "slug": "frost-move-the-patch",
        "story": "frostbound-citadel",
        "number": 4,
        "title": "Move the Patch",
        "description": (
            "Transfer work between branches with advanced stash workflows, cherry-pick transplants, and "
            "targeted reverts while preserving the history and authorship the team needs."
        ),
        "battle_stage": {"parallax": "frost-04-icebound-vault"},
    },
    {
        "slug": "frost-reforge-the-branch",
        "story": "frostbound-citadel",
        "number": 5,
        "title": "Reforge the Branch",
        "description": (
            "Rebase commit series onto the correct base, edit local history interactively, use autosquash, "
            "and compare rewritten patch series before publication."
        ),
        "battle_stage": {"parallax": "frost-05-aurora-anvil"},
    },
    {
        "slug": "frost-govern-the-remote",
        "story": "frostbound-citadel",
        "number": 6,
        "title": "Govern the Remote",
        "description": (
            "Manage upstreams, refspecs, pruning, pull policy, rewritten-history publication, and remote "
            "branch lifecycle without disrupting collaborators."
        ),
        "battle_stage": {"parallax": "frost-06-signal-bastion"},
    },
    {
        "slug": "frost-deliver-the-release",
        "story": "frostbound-citadel",
        "number": 7,
        "title": "Deliver the Release",
        "description": (
            "Build a traceable release with lightweight and annotated tags, contributor summaries from "
            "shortlog, release naming with describe, and deliberate tag publication to the relay stations."
        ),
        "battle_stage": {"parallax": "frost-07-summit-observatory"},
    },
    {
        "slug": "skyline-revision-language",
        "story": "neon-backstreets",
        "number": 1,
        "title": "Speak the Revision Language",
        "description": (
            "Resolve revisions, ancestry expressions, reflog selectors, commit sets, and pathspecs so "
            "complex repository questions can be expressed precisely."
        ),
        "battle_stage": {"parallax": "skyline-01-transit-hub"},
    },
    {
        "slug": "skyline-hidden-history",
        "story": "neon-backstreets",
        "number": 2,
        "title": "Read the Hidden History",
        "description": (
            "Search history by author, message, date, and changed content; trace lines with blame; and "
            "inspect repository-wide content with grep and custom log formats."
        ),
        "battle_stage": {"parallax": "skyline-02-archive-highrise"},
    },
    {
        "slug": "skyline-first-broken-commit",
        "story": "neon-backstreets",
        "number": 3,
        "title": "Hunt the First Broken Commit",
        "description": (
            "Use manual and automated bisect sessions to locate the first bad change, preserve the search "
            "record, and restore the original checkout when the investigation ends."
        ),
        "battle_stage": {"parallax": "skyline-03-debug-lab"},
    },
    {
        "slug": "skyline-repeated-conflict",
        "story": "neon-backstreets",
        "number": 4,
        "title": "Master Repeated Conflict",
        "description": (
            "Record reusable conflict resolutions, choose informative marker styles, inspect virtual merges, "
            "and compare successive patch-series revisions."
        ),
        "battle_stage": {"parallax": "skyline-04-simulation-deck"},
    },
    {
        "slug": "skyline-many-realities",
        "story": "neon-backstreets",
        "number": 5,
        "title": "Work Across Many Realities",
        "description": (
            "Operate multiple worktrees, sparse working directories, partial clones, and submodules for "
            "large repositories and parallel delivery streams."
        ),
        "battle_stage": {"parallax": "skyline-05-multi-level-campus"},
    },
    {
        "slug": "skyline-enchant-behavior",
        "story": "neon-backstreets",
        "number": 6,
        "title": "Configure Git's Behavior",
        "description": (
            "Control configuration scopes, conditional includes, aliases, ignore precedence, attributes, "
            "line endings, hooks, filters, mailmaps, and custom diff or merge drivers."
        ),
        "battle_stage": {"parallax": "skyline-06-automation-district"},
    },
    {
        "slug": "skyline-guard-the-archive",
        "story": "neon-backstreets",
        "number": 7,
        "title": "Guard the Archive",
        "description": (
            "Sign and verify commits and tags, configure credential helpers, enforce safe-directory and "
            "protocol policy, and treat executable repository configuration as a trust boundary."
        ),
        "battle_stage": {"parallax": "skyline-07-security-center"},
    },
    {
        "slug": "skyline-restore-maintain",
        "story": "neon-backstreets",
        "number": 8,
        "title": "Restore and Maintain the Archive",
        "description": (
            "Recover unreachable work through the reflog, audit object health with fsck and count-objects, "
            "and restore known-good states without destroying the evidence a later investigation needs."
        ),
        "battle_stage": {"parallax": "skyline-08-maintenance-core"},
    },
    {
        "slug": "skyline-git-machinery",
        "story": "neon-backstreets",
        "number": 11,
        "title": "Enter Git's Machinery",
        "description": (
            "Read the object database directly: decode blobs, trees, and commits with cat-file, inspect index "
            "entries and tree objects, and follow HEAD's symbolic chain down to the refs it names."
        ),
        "battle_stage": {"parallax": "skyline-09-data-center-roof"},
    },
]

# v3 progression chapters. Existing chapter slugs remain stable; these additions
# complete the beginner/intermediate/advanced narrative without inventing a new
# story-capstone content type. Each story still resolves through its final
# chapter challenge.
CHAPTERS += [
    {
        "slug": "guild-archive-handoff",
        "story": "arcane-spire",
        "number": 8,
        "title": "Complete the Guild Handoff",
        "description": (
            "Combine setup, snapshot, branch, merge, recovery, and remote habits in complete beginner "
            "workflows that leave both the local and Guild histories clean and understandable."
        ),
        "battle_stage": {"parallax": "chapter-08-guild-signal-apex"},
    },
    {
        "slug": "frost-hunt-the-regression",
        "story": "frostbound-citadel",
        "number": 8,
        "title": "Hunt the Frozen Regression",
        "description": (
            "Narrow a failing history with revision ranges, comparison, and automated bisect evidence, "
            "then repair the first bad change without destroying the investigation trail."
        ),
        "battle_stage": {"parallax": "frost-08-avalanche-debug-tunnel"},
    },
    {
        "slug": "frost-publish-the-core",
        "story": "frostbound-citadel",
        "number": 9,
        "title": "Publish the Restored Core",
        "description": (
            "Audit the assembled release, create its final correction, attach traceable refs, and publish "
            "the repaired heat-core history without overwriting a collaborator's newer work."
        ),
        "battle_stage": {"parallax": "frost-09-aurora-release-platform"},
    },
    {
        "slug": "skyline-serve-the-city",
        "story": "neon-backstreets",
        "number": 9,
        "title": "Serve the City's Repositories",
        "description": (
            "Operate the district's synchronization endpoints, audit every advertised ref before it is trusted, "
            "and govern the fetches and pushes that distributed city services are allowed to exchange."
        ),
        "battle_stage": {"parallax": "skyline-09-network-operations-center"},
    },
    {
        "slug": "skyline-migrate-the-grid",
        "story": "neon-backstreets",
        "number": 10,
        "title": "Migrate the Civic Grid",
        "description": (
            "Verify a migrated history end to end: prove that refs, trees, and authorship survived the move "
            "with cat-file, ls-tree, show-ref, and fsck before the district trusts the new archive."
        ),
        "battle_stage": {"parallax": "skyline-10-migration-transit-ring"},
    },
    {
        "slug": "skyline-command-laboratory",
        "story": "neon-backstreets",
        "number": 12,
        "title": "Open the Command Laboratory",
        "description": (
            "Combine every discipline from the campaign in one capstone incident, then land a final ref "
            "change with porcelain commands and prove it correct with rev-parse and for-each-ref."
        ),
        "battle_stage": {"parallax": "skyline-12-command-research-roof"},
    },
]

# Every chapter now has a verified playable fieldwork tranche. The chapter books
# remain broader and continue to mark future engine forms individually.
for _chapter in CHAPTERS[7:]:
    _chapter["is_playable"] = True

# Stable curriculum partitions. Existing gameplay remains the complete Arcane
# Spire ledger; the additive campaigns expose their full authored books while
# command-engine work progresses behind an explicit capability boundary.
ARCANE_SPIRE_CHAPTERS = tuple(
    sorted(
        (chapter for chapter in CHAPTERS if chapter["story"] == "arcane-spire"),
        key=lambda chapter: chapter["number"],
    )
)
FROSTBOUND_CITADEL_CHAPTERS = tuple(
    sorted(
        (chapter for chapter in CHAPTERS if chapter["story"] == "frostbound-citadel"),
        key=lambda chapter: chapter["number"],
    )
)
SKYLINE_NEXUS_CHAPTERS = tuple(
    sorted(
        (chapter for chapter in CHAPTERS if chapter["story"] == "neon-backstreets"),
        key=lambda chapter: chapter["number"],
    )
)
ADVANCED_STORY_CHAPTERS = FROSTBOUND_CITADEL_CHAPTERS + SKYLINE_NEXUS_CHAPTERS
PLAYABLE_CHAPTERS = ARCANE_SPIRE_CHAPTERS + ADVANCED_STORY_CHAPTERS
# The advanced chapter books intentionally exceed the first playable fieldwork
# tranche; this alias remains useful for coverage tests and engine-roadmap UI.
REFERENCE_CHAPTERS = ADVANCED_STORY_CHAPTERS
