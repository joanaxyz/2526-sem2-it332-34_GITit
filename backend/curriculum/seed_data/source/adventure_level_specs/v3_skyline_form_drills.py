"""Neon Backstreets (skyline) form drills: solo intros + applied waves.

Same tiered-law structure as the Frostbound drills: every playable skyline
command form gets a solo intro wave at its first use in play order, plus
applied waves until it reaches at least three distinct waves. Chapter incident
levels provide the remaining appearances for each chapter's diagnostic form.

Story briefs are plain language and name every literal the learner must type;
per-variant values are surfaced as bare Copy details the brief points at.
"""

from __future__ import annotations

from .common import ev, q, v
from .v3_advanced_workflows import _state
from .v3_frost_form_drills import (
    CORE_TAGS,
    GRAPH,
    STATUS,
    _broken,
    _clean,
    _dv,
    _read_eval,
    _req,
    _required_check,
)


# ---------------------------------------------------------------------------
# Chapter 1 - skyline-revision-language
# ---------------------------------------------------------------------------

REVISION_DRILLS = [
    q(
        "git-rev-parse/revision",
        "sr-intro-rev-parse",
        "Resolve a revision to a commit id",
        "A deployment report references HEAD~1 and the on-call engineer needs the actual commit id behind that expression before anything else happens.",
        "Resolve the revision expression HEAD~1 to its commit id.",
        _dv("sr-intro-rev-parse", _clean, ["git rev-parse HEAD~1"], _read_eval(["git rev-parse HEAD~1"])),
        checks=[_required_check("The revision expression was resolved.", ["git rev-parse"])],
        details=["HEAD~1"],
        adventure="skyline-revision-language-drills",
    ),
    q(
        "git-rev-parse/toplevel",
        "sr-intro-rev-parse-toplevel",
        "Locate the repository root",
        "A build script must run from the repository root, but the current shell could be anywhere inside the project. Print the repository's top-level directory.",
        "Print the repository's top-level directory.",
        _dv(
            "sr-intro-rev-parse-toplevel",
            _clean,
            ["git rev-parse --show-toplevel"],
            _read_eval(["git rev-parse --show-toplevel"]),
        ),
        checks=[_required_check("The repository root was located.", ["git rev-parse --show-toplevel"])],
        adventure="skyline-revision-language-drills",
    ),
]

REVISION_WORKFLOWS = [
    q(
        "git-rev-parse/toplevel",
        "sr-apply-root-then-resolve",
        "Locate the root, then resolve the revision",
        "Before wiring up the automation, print the repository root, then resolve HEAD~1 so the script can pin the exact commit it operates on.",
        "Print the repository root, resolve HEAD~1, then verify the state.",
        _dv(
            "sr-apply-root-then-resolve",
            _clean,
            ["git rev-parse --show-toplevel", "git rev-parse HEAD~1", STATUS, GRAPH],
            _read_eval(["git rev-parse --show-toplevel", "git rev-parse HEAD~1", "git status", "git log"]),
        ),
        checks=[
            _required_check("The root and the revision were both resolved.", ["git rev-parse --show-toplevel", "git rev-parse"]),
        ],
        details=["HEAD~1"],
        command_forms=["git-rev-parse/revision", *CORE_TAGS],
        adventure="skyline-revision-language-workflows",
        workflow=True,
        max_counted_commands=8,
    ),
    q(
        "git-rev-parse/toplevel",
        "sr-apply-audit-coordinates",
        "Pin the audit coordinates",
        "An incident audit needs two facts recorded together: where this repository lives on disk and which commit id the expression main resolves to. Produce both.",
        "Print the repository root and resolve main to its commit id, then verify.",
        _dv(
            "sr-apply-audit-coordinates",
            _clean,
            ["git rev-parse --show-toplevel", "git rev-parse main", STATUS, GRAPH],
            _read_eval(["git rev-parse --show-toplevel", "git rev-parse main", "git status", "git log"]),
        ),
        checks=[
            _required_check("Both audit coordinates were produced.", ["git rev-parse --show-toplevel", "git rev-parse"]),
        ],
        details=["main"],
        command_forms=["git-rev-parse/revision", *CORE_TAGS],
        adventure="skyline-revision-language-workflows",
        workflow=True,
        max_counted_commands=8,
    ),
]


# ---------------------------------------------------------------------------
# Chapter 2 - skyline-hidden-history
# ---------------------------------------------------------------------------

HIDDEN_DRILLS = [
    q(
        "git-blame/path",
        "sh-intro-blame",
        "Find who last changed each line",
        "A wrong setting shipped inside src/app.ts and the investigation starts with one question: which commit last touched each line of that file?",
        "Show line-by-line authorship for src/app.ts.",
        _dv("sh-intro-blame", _clean, ["git blame src/app.ts"], _read_eval(["git blame src/app.ts"])),
        checks=[_required_check("Line authorship was traced.", ["git blame"])],
        details=["src/app.ts"],
        adventure="skyline-hidden-history-drills",
    ),
    q(
        "git-grep/pattern",
        "sh-intro-grep",
        "Search the tracked content",
        "Somewhere in the tracked files the word stable still appears, and the report needs to know exactly where. Search the repository content for it.",
        "Search tracked content for the word stable.",
        _dv("sh-intro-grep", _clean, ["git grep stable"], _read_eval(["git grep stable"])),
        checks=[_required_check("The tracked content was searched.", ["git grep"])],
        details=["stable"],
        adventure="skyline-hidden-history-drills",
    ),
    q(
        "git-show/path-at-revision",
        "sh-intro-show-path",
        "Read a file as it was in an old commit",
        "The investigation needs the exact content src/app.ts had in an earlier commit (its id is in Copy details), without checking anything out.",
        "Print the old commit's version of src/app.ts.",
        _dv(
            "sh-intro-show-path",
            _clean,
            ["git show {p}1:src/app.ts"],
            _read_eval(["git show {p}1:src/app.ts"]),
            details=["{p}1:src/app.ts"],
        ),
        checks=[_required_check("The historical file content was read.", ["git show"])],
        adventure="skyline-hidden-history-drills",
    ),
]

HIDDEN_WORKFLOWS = [
    q(
        "git-grep/pattern",
        "sh-apply-search-then-blame",
        "Search first, then trace the line",
        "Find where the word stable appears in tracked content, then trace line authorship of src/app.ts to see which commit put it there.",
        "Search for stable, trace authorship of src/app.ts, then verify.",
        _dv(
            "sh-apply-search-then-blame",
            _clean,
            ["git grep stable", "git blame src/app.ts", STATUS, GRAPH],
            _read_eval(["git grep stable", "git blame", "git status", "git log"]),
        ),
        checks=[
            _required_check("The content was searched and the line traced.", ["git grep", "git blame"]),
        ],
        details=["stable", "src/app.ts"],
        command_forms=["git-blame/path", *CORE_TAGS],
        adventure="skyline-hidden-history-workflows",
        workflow=True,
        max_counted_commands=8,
    ),
    q(
        "git-show/path-at-revision",
        "sh-apply-compare-versions",
        "Read the old version, then the evidence trail",
        "Print the version of src/app.ts from the earlier commit in Copy details, then trace the file's line authorship so old content and current blame line up in the report.",
        "Read the old file content, trace authorship, then verify.",
        _dv(
            "sh-apply-compare-versions",
            _clean,
            ["git show {p}1:src/app.ts", "git blame src/app.ts", STATUS, GRAPH],
            _read_eval(["git show {p}1:src/app.ts", "git blame", "git status", "git log"]),
            details=["{p}1:src/app.ts"],
        ),
        checks=[
            _required_check("The old content and current authorship were both read.", ["git show", "git blame"]),
        ],
        command_forms=["git-blame/path", *CORE_TAGS],
        adventure="skyline-hidden-history-workflows",
        workflow=True,
        max_counted_commands=8,
    ),
    q(
        "git-grep/pattern",
        "sh-apply-search-the-snapshot",
        "Search today, then read the old snapshot",
        "Search the tracked content for stable, then print the older version of src/app.ts (commit id in Copy details) to see whether the word was already there.",
        "Search for stable, read the old file version, then verify.",
        _dv(
            "sh-apply-search-the-snapshot",
            _clean,
            ["git grep stable", "git show {p}1:src/app.ts", STATUS, GRAPH],
            _read_eval(["git grep stable", "git show {p}1:src/app.ts", "git status", "git log"]),
            details=["stable", "{p}1:src/app.ts"],
        ),
        checks=[
            _required_check("Today's content and the old snapshot were both read.", ["git grep", "git show"]),
        ],
        command_forms=["git-show/path-at-revision", *CORE_TAGS],
        adventure="skyline-hidden-history-workflows",
        workflow=True,
        max_counted_commands=8,
    ),
]


# ---------------------------------------------------------------------------
# Chapter 4 - skyline-repeated-conflict
# ---------------------------------------------------------------------------

REPEATED_DRILLS = [
    q(
        "git-rerere/status",
        "sc-intro-rerere-status",
        "List the recorded conflict paths",
        "This repository records conflict resolutions for reuse. Before the next integration, list which paths currently have recorded conflict state.",
        "List the paths with recorded conflict resolutions.",
        _dv("sc-intro-rerere-status", _clean, ["git rerere status"], _read_eval(["git rerere status"])),
        checks=[_required_check("The recorded conflict paths were listed.", ["git rerere status"])],
        adventure="skyline-repeated-conflict-drills",
    ),
    q(
        "git-rerere/diff",
        "sc-intro-rerere-diff",
        "Inspect the recorded resolutions",
        "A recorded resolution will be replayed automatically on the next matching conflict. Inspect what the recorded resolution actually changes before trusting it.",
        "Show the recorded conflict resolutions.",
        _dv("sc-intro-rerere-diff", _clean, ["git rerere diff"], _read_eval(["git rerere diff"])),
        checks=[_required_check("The recorded resolutions were inspected.", ["git rerere diff"])],
        adventure="skyline-repeated-conflict-drills",
    ),
]

REPEATED_WORKFLOWS = [
    q(
        "git-rerere/diff",
        "sc-apply-audit-recorded",
        "Audit the recorded resolution",
        "Before the next merge window, list the recorded conflict paths, then inspect what the recorded resolution changes. Nothing may be modified.",
        "List recorded paths, inspect the resolutions, then verify.",
        _dv(
            "sc-apply-audit-recorded",
            _clean,
            ["git rerere status", "git rerere diff", STATUS, GRAPH],
            _read_eval(["git rerere status", "git rerere diff", "git status", "git log"]),
        ),
        checks=[
            _required_check("The recorded state was audited.", ["git rerere status", "git rerere diff"]),
        ],
        command_forms=["git-rerere/status", *CORE_TAGS],
        adventure="skyline-repeated-conflict-workflows",
        workflow=True,
        max_counted_commands=8,
    ),
    q(
        "git-rerere/diff",
        "sc-apply-preflight-check",
        "Pre-flight the conflict memory",
        "A repeated integration is scheduled for tonight. Inspect the recorded resolutions and the repository state so the automation's behavior is predictable.",
        "Inspect the recorded resolutions and the current state.",
        _dv(
            "sc-apply-preflight-check",
            _clean,
            ["git rerere diff", "git rerere status", STATUS, GRAPH],
            _read_eval(["git rerere diff", "git rerere status", "git status", "git log"]),
        ),
        checks=[
            _required_check("The conflict memory was pre-flighted.", ["git rerere diff", "git rerere status"]),
        ],
        command_forms=["git-rerere/status", *CORE_TAGS],
        adventure="skyline-repeated-conflict-workflows",
        workflow=True,
        max_counted_commands=8,
    ),
]


# ---------------------------------------------------------------------------
# Chapter 5 - skyline-many-realities
# ---------------------------------------------------------------------------

REALITIES_DRILLS = [
    q(
        "git-worktree/list",
        "sm-intro-worktree-list",
        "List the attached worktrees",
        "This repository has more than one working directory attached to it, and a branch can only be checked out in one of them. List every attached worktree before touching any branch.",
        "List all worktrees attached to this repository.",
        _dv("sm-intro-worktree-list", _clean, ["git worktree list"], _read_eval(["git worktree list"])),
        checks=[_required_check("The attached worktrees were listed.", ["git worktree list"])],
        adventure="skyline-many-realities-drills",
    ),
    q(
        "git-sparse-checkout/list",
        "sm-intro-sparse-list",
        "List the sparse checkout paths",
        "Files look missing in this working directory because a sparse checkout limits which paths are materialized. List the sparse paths to see what is intentionally present.",
        "List the paths included in the sparse checkout.",
        _dv("sm-intro-sparse-list", _clean, ["git sparse-checkout list"], _read_eval(["git sparse-checkout list"])),
        checks=[_required_check("The sparse paths were listed.", ["git sparse-checkout list"])],
        adventure="skyline-many-realities-drills",
    ),
    q(
        "git-submodule/status",
        "sm-intro-submodule-status",
        "Check the submodule state",
        "This project embeds another repository as a submodule, pinned to a specific commit. Check the submodule's current state before any dependency work starts.",
        "Show the status of the project's submodules.",
        _dv("sm-intro-submodule-status", _clean, ["git submodule status"], _read_eval(["git submodule status"])),
        checks=[_required_check("The submodule state was checked.", ["git submodule status"])],
        adventure="skyline-many-realities-drills",
    ),
]

REALITIES_WORKFLOWS = [
    q(
        "git-sparse-checkout/list",
        "sm-apply-map-the-workspace",
        "Map the whole workspace setup",
        "A new teammate cannot find files that should exist. Map the setup for them: list the worktrees, then the sparse paths, so it is clear where everything actually lives.",
        "List the worktrees and the sparse paths, then verify.",
        _dv(
            "sm-apply-map-the-workspace",
            _clean,
            ["git worktree list", "git sparse-checkout list", STATUS, GRAPH],
            _read_eval(["git worktree list", "git sparse-checkout list", "git status", "git log"]),
        ),
        checks=[
            _required_check("The workspace setup was mapped.", ["git worktree list", "git sparse-checkout list"]),
        ],
        command_forms=["git-worktree/list", *CORE_TAGS],
        adventure="skyline-many-realities-workflows",
        workflow=True,
        max_counted_commands=8,
    ),
    q(
        "git-submodule/status",
        "sm-apply-dependency-audit",
        "Audit the dependency pins",
        "The release checklist requires proof of where every dependency stands: check the submodule status and list the worktrees so the audit shows the full picture.",
        "Check submodule status and list worktrees, then verify.",
        _dv(
            "sm-apply-dependency-audit",
            _clean,
            ["git submodule status", "git worktree list", STATUS, GRAPH],
            _read_eval(["git submodule status", "git worktree list", "git status", "git log"]),
        ),
        checks=[
            _required_check("The dependency pins were audited.", ["git submodule status", "git worktree list"]),
        ],
        command_forms=["git-worktree/list", *CORE_TAGS],
        adventure="skyline-many-realities-workflows",
        workflow=True,
        max_counted_commands=8,
    ),
    q(
        "git-sparse-checkout/list",
        "sm-apply-explain-missing-files",
        "Explain the missing files",
        "A bug report claims files vanished. Show they are excluded by the sparse checkout, and confirm the submodule pin is untouched, so the report can be closed with evidence.",
        "List sparse paths and submodule status, then verify.",
        _dv(
            "sm-apply-explain-missing-files",
            _clean,
            ["git sparse-checkout list", "git submodule status", STATUS, GRAPH],
            _read_eval(["git sparse-checkout list", "git submodule status", "git status", "git log"]),
        ),
        checks=[
            _required_check("The exclusions and pins were both read.", ["git sparse-checkout list", "git submodule status"]),
        ],
        command_forms=["git-submodule/status", *CORE_TAGS],
        adventure="skyline-many-realities-workflows",
        workflow=True,
        max_counted_commands=8,
    ),
    q(
        "git-submodule/status",
        "sm-apply-floor-check",
        "Run the morning floor check",
        "Every morning the on-call engineer verifies the multi-workspace setup: worktrees, sparse paths, and submodule pins, in that order. Run the full check.",
        "List worktrees, sparse paths, and submodule status, then verify.",
        _dv(
            "sm-apply-floor-check",
            _clean,
            ["git worktree list", "git sparse-checkout list", "git submodule status", STATUS, GRAPH],
            _read_eval(["git worktree list", "git sparse-checkout list", "git submodule status", "git status", "git log"]),
        ),
        checks=[
            _required_check(
                "The full setup was checked.",
                ["git worktree list", "git sparse-checkout list", "git submodule status"],
            ),
        ],
        command_forms=["git-worktree/list", "git-sparse-checkout/list", *CORE_TAGS],
        adventure="skyline-many-realities-workflows",
        workflow=True,
        max_counted_commands=8,
    ),
]


# ---------------------------------------------------------------------------
# Chapter 6 - skyline-enchant-behavior
# ---------------------------------------------------------------------------

ENCHANT_DRILLS = [
    q(
        "git-config/get",
        "se-intro-config-get",
        "Read one configuration value",
        "Automation behaves differently on this machine and the first suspect is identity configuration. Read the single value of user.name to see what Git is actually using.",
        "Read the configured value of user.name.",
        _dv("se-intro-config-get", _clean, ["git config --get user.name"], _read_eval(["git config --get user.name"])),
        checks=[_required_check("The configuration value was read.", ["git config --get"])],
        details=["user.name"],
        adventure="skyline-enchant-behavior-drills",
    ),
]

ENCHANT_WORKFLOWS: list = []


# ---------------------------------------------------------------------------
# Chapter 7 - skyline-guard-the-archive
# ---------------------------------------------------------------------------

GUARD_DRILLS = [
    q(
        "git-verify-commit/commit",
        "sg-intro-verify-commit",
        "Verify a commit's signature",
        "A release-critical commit claims to be signed by the release bot. Verify the signature of the commit in Copy details before the deployment trusts it.",
        "Verify the commit's cryptographic signature.",
        _dv(
            "sg-intro-verify-commit",
            _clean,
            ["git verify-commit {p}1"],
            _read_eval(["git verify-commit {p}1"]),
            details=["{p}1"],
        ),
        checks=[_required_check("The commit signature was verified.", ["git verify-commit"])],
        adventure="skyline-guard-the-archive-drills",
    ),
]

GUARD_WORKFLOWS: list = []


# ---------------------------------------------------------------------------
# Chapter 8 - skyline-restore-maintain
# ---------------------------------------------------------------------------

RESTORE_DRILLS = [
    q(
        "git-fsck/full",
        "sx-intro-fsck",
        "Run a full integrity check",
        "After a crashed sync, the object store's health is in question. Run a full integrity check to surface any dangling or unreachable objects.",
        "Run a full repository integrity check.",
        _dv("sx-intro-fsck", _clean, ["git fsck --full"], _read_eval(["git fsck --full"])),
        checks=[_required_check("The integrity check was run.", ["git fsck --full"])],
        adventure="skyline-restore-maintain-drills",
    ),
    q(
        "git-count-objects/verbose-human",
        "sx-intro-count-objects",
        "Measure the object store",
        "Disk usage on this machine keeps climbing. Measure the repository's loose and packed object storage in human-readable form.",
        "Show verbose, human-readable object storage counts.",
        _dv("sx-intro-count-objects", _clean, ["git count-objects -vH"], _read_eval(["git count-objects -vH"])),
        checks=[_required_check("The object storage was measured.", ["git count-objects -vH"])],
        adventure="skyline-restore-maintain-drills",
    ),
    q(
        "git-reset/reflog-recovery",
        "sx-intro-reflog-recovery",
        "Recover the known-good state",
        "The branch tip is broken, but the reflog shows the last good commit (its id is in Copy details). Move main back to that known-good state, discarding the broken one.",
        "Hard-reset main to the known-good commit found in the reflog.",
        _dv(
            "sx-intro-reflog-recovery",
            _broken,
            ["git reset --hard {p}1"],
            _req({}, ["git reset --hard"], rules=[{"type": "branch_points_to", "branch": "main", "commit": "{p}1"}]),
            details=["{p}1"],
        ),
        checks=[_required_check("The branch was recovered to the known-good commit.", ["git reset --hard"])],
        adventure="skyline-restore-maintain-drills",
        workflow=True,
    ),
    q(
        "git-reflog/show-ref",
        "sx-intro-reflog-show",
        "Read one ref's movement history",
        "Before any recovery decision, read the movement history of the main ref so the last good position can be identified from evidence, not memory.",
        "Show the reflog for the main ref.",
        _dv("sx-intro-reflog-show", _broken, ["git reflog show main"], _read_eval(["git reflog show main"])),
        checks=[_required_check("The ref's movement history was read.", ["git reflog show"])],
        details=["main"],
        adventure="skyline-restore-maintain-drills",
    ),
]

RESTORE_WORKFLOWS = [
    q(
        "git-reset/reflog-recovery",
        "sx-apply-evidence-then-recover",
        "Read the reflog, then recover",
        "Read main's movement history, identify the last good commit (its id is in Copy details), then move main back to it and confirm the recovery.",
        "Read the reflog, hard-reset to the known-good commit, then verify.",
        _dv(
            "sx-apply-evidence-then-recover",
            _broken,
            ["git reflog show main", "git reset --hard {p}1", STATUS, GRAPH],
            _req(
                {},
                ["git reflog show", "git reset --hard", "git status", "git log"],
                rules=[{"type": "branch_points_to", "branch": "main", "commit": "{p}1"}],
            ),
            details=["{p}1"],
        ),
        checks=[
            _required_check("The movement history was read first.", ["git reflog show"]),
            _required_check("The branch was recovered to the known-good commit.", ["git reset --hard"]),
        ],
        command_forms=["git-reflog/show-ref", *CORE_TAGS],
        adventure="skyline-restore-maintain-workflows",
        workflow=True,
        max_counted_commands=8,
    ),
    q(
        "git-count-objects/verbose-human",
        "sx-apply-health-report",
        "Produce the storage health report",
        "The weekly health report pairs an integrity check with storage numbers. Run the full check, then measure the object store, changing nothing.",
        "Run the integrity check and measure storage, then verify.",
        _dv(
            "sx-apply-health-report",
            _clean,
            ["git fsck --full", "git count-objects -vH", STATUS, GRAPH],
            _read_eval(["git fsck --full", "git count-objects -vH", "git status", "git log"]),
        ),
        checks=[
            _required_check("The health report reads were produced.", ["git fsck --full", "git count-objects -vH"]),
        ],
        command_forms=["git-fsck/full", *CORE_TAGS],
        adventure="skyline-restore-maintain-workflows",
        workflow=True,
        max_counted_commands=8,
    ),
    q(
        "git-reset/reflog-recovery",
        "sx-apply-check-then-recover",
        "Check integrity, then recover the branch",
        "Confirm the object store is intact with a full check, then move main back to the known-good commit from Copy details and verify the result.",
        "Run the integrity check, hard-reset to the known-good commit, then verify.",
        _dv(
            "sx-apply-check-then-recover",
            _broken,
            ["git fsck --full", "git reset --hard {p}1", STATUS, GRAPH],
            _req(
                {},
                ["git fsck --full", "git reset --hard", "git status", "git log"],
                rules=[{"type": "branch_points_to", "branch": "main", "commit": "{p}1"}],
            ),
            details=["{p}1"],
        ),
        checks=[
            _required_check("Integrity was confirmed before recovery.", ["git fsck --full"]),
            _required_check("The branch was recovered to the known-good commit.", ["git reset --hard"]),
        ],
        command_forms=["git-fsck/full", *CORE_TAGS],
        adventure="skyline-restore-maintain-workflows",
        workflow=True,
        max_counted_commands=8,
    ),
    q(
        "git-reflog/show-ref",
        "sx-apply-movement-audit",
        "Audit the ref movement",
        "The audit wants main's movement history next to the storage numbers. Read the reflog for main, then measure the object store, changing nothing.",
        "Read main's reflog and measure storage, then verify.",
        _dv(
            "sx-apply-movement-audit",
            _broken,
            ["git reflog show main", "git count-objects -vH", STATUS, GRAPH],
            _read_eval(["git reflog show", "git count-objects -vH", "git status", "git log"]),
        ),
        checks=[
            _required_check("The movement and storage reads were produced.", ["git reflog show", "git count-objects -vH"]),
        ],
        details=["main"],
        command_forms=["git-count-objects/verbose-human", *CORE_TAGS],
        adventure="skyline-restore-maintain-workflows",
        workflow=True,
        max_counted_commands=8,
    ),
]


# ---------------------------------------------------------------------------
# Chapter 9 - skyline-serve-the-city
# ---------------------------------------------------------------------------

SERVE_DRILLS = [
    q(
        "git-for-each-ref/all",
        "ss-intro-for-each-ref",
        "Enumerate every ref, formatted",
        "The sync service advertises refs to other machines. Enumerate every ref this repository holds so the served set can be reviewed before anything syncs.",
        "Enumerate all refs in the repository.",
        _dv("ss-intro-for-each-ref", _clean, ["git for-each-ref"], _read_eval(["git for-each-ref"])),
        checks=[_required_check("The complete ref set was enumerated.", ["git for-each-ref"])],
        adventure="skyline-serve-the-city-drills",
    ),
]

SERVE_WORKFLOWS: list = []


# ---------------------------------------------------------------------------
# Chapter 10 - skyline-migrate-the-grid
# ---------------------------------------------------------------------------

MIGRATE_DRILLS = [
    q(
        "git-cat-file/type",
        "sq-intro-cat-file-type",
        "Check what kind of object an id names",
        "After the migration, an id from the old system (see Copy details) must be proven to name a commit and not something else. Check the object's type.",
        "Print the object type of the id in Copy details.",
        _dv(
            "sq-intro-cat-file-type",
            _clean,
            ["git cat-file -t {p}1"],
            _read_eval(["git cat-file -t {p}1"]),
            details=["{p}1"],
        ),
        checks=[_required_check("The object type was checked.", ["git cat-file -t"])],
        adventure="skyline-migrate-the-grid-drills",
    ),
    q(
        "git-ls-tree/tree",
        "sq-intro-ls-tree",
        "List what a commit's tree contains",
        "Migration sign-off requires proof that the file layout survived. List the tree of the commit in Copy details to see exactly which entries it stores.",
        "List the tree entries of the commit in Copy details.",
        _dv(
            "sq-intro-ls-tree",
            _clean,
            ["git ls-tree {p}1"],
            _read_eval(["git ls-tree {p}1"]),
            details=["{p}1"],
        ),
        checks=[_required_check("The tree entries were listed.", ["git ls-tree"])],
        adventure="skyline-migrate-the-grid-drills",
    ),
]

MIGRATE_WORKFLOWS = [
    q(
        "git-ls-tree/tree",
        "sq-apply-verify-migrated-commit",
        "Verify one migrated commit end to end",
        "Prove the migrated commit in Copy details is intact: confirm the id names a commit, then list its tree to confirm the file layout survived.",
        "Check the object type, list its tree, then verify.",
        _dv(
            "sq-apply-verify-migrated-commit",
            _clean,
            ["git cat-file -t {p}1", "git ls-tree {p}1", STATUS, GRAPH],
            _read_eval(["git cat-file -t", "git ls-tree", "git status", "git log"]),
            details=["{p}1"],
        ),
        checks=[
            _required_check("The commit was verified type-first.", ["git cat-file -t", "git ls-tree"]),
        ],
        command_forms=["git-cat-file/type", *CORE_TAGS],
        adventure="skyline-migrate-the-grid-workflows",
        workflow=True,
        max_counted_commands=8,
    ),
    q(
        "git-ls-tree/tree",
        "sq-apply-layout-comparison",
        "Compare two commits' layouts",
        "The sign-off compares the file layout of two migrated commits (both ids in Copy details). List both trees back to back, changing nothing.",
        "List the trees of both commits, then verify.",
        _dv(
            "sq-apply-layout-comparison",
            _clean,
            ["git ls-tree {p}0", "git ls-tree {p}1", STATUS, GRAPH],
            _read_eval(["git ls-tree", "git status", "git log"]),
            details=["{p}0", "{p}1"],
        ),
        checks=[
            _required_check("Both layouts were listed.", ["git ls-tree"]),
        ],
        command_forms=CORE_TAGS,
        adventure="skyline-migrate-the-grid-workflows",
        workflow=True,
        max_counted_commands=8,
    ),
]


# ---------------------------------------------------------------------------
# Chapter 11 - skyline-git-machinery
# ---------------------------------------------------------------------------

MACHINERY_DRILLS = [
    q(
        "git-symbolic-ref/head",
        "sy-intro-symbolic-ref",
        "Read what HEAD points to",
        "The visible branch name is only a label. Read HEAD's symbolic target to see exactly which ref the repository considers current.",
        "Print the ref that HEAD symbolically points to.",
        _dv("sy-intro-symbolic-ref", _clean, ["git symbolic-ref HEAD"], _read_eval(["git symbolic-ref HEAD"])),
        checks=[_required_check("HEAD's symbolic target was read.", ["git symbolic-ref"])],
        details=["HEAD"],
        adventure="skyline-git-machinery-drills",
    ),
    q(
        "git-cat-file/pretty",
        "sy-intro-cat-file-pretty",
        "Decode a raw object",
        "To explain what a commit really is, decode the raw object behind the id in Copy details and read its stored fields directly.",
        "Pretty-print the object with the id in Copy details.",
        _dv(
            "sy-intro-cat-file-pretty",
            _clean,
            ["git cat-file -p {p}1"],
            _read_eval(["git cat-file -p {p}1"]),
            details=["{p}1"],
        ),
        checks=[_required_check("The raw object was decoded.", ["git cat-file -p"])],
        adventure="skyline-git-machinery-drills",
    ),
]

MACHINERY_WORKFLOWS = [
    q(
        "git-cat-file/pretty",
        "sy-apply-follow-the-chain",
        "Follow HEAD down to its object",
        "Walk the chain once, end to end: read HEAD's symbolic ref, then decode the commit object it ultimately points to (id in Copy details).",
        "Read HEAD's target, decode the commit object, then verify.",
        _dv(
            "sy-apply-follow-the-chain",
            _clean,
            ["git symbolic-ref HEAD", "git cat-file -p {p}1", STATUS, GRAPH],
            _read_eval(["git symbolic-ref", "git cat-file -p", "git status", "git log"]),
            details=["{p}1"],
        ),
        checks=[
            _required_check("The chain was followed from HEAD to the object.", ["git symbolic-ref", "git cat-file -p"]),
        ],
        command_forms=["git-symbolic-ref/head", *CORE_TAGS],
        adventure="skyline-git-machinery-workflows",
        workflow=True,
        max_counted_commands=8,
    ),
    q(
        "git-cat-file/pretty",
        "sy-apply-decode-and-type",
        "Decode the object and prove its type",
        "For the archive record, prove the id in Copy details names a commit, then decode its content so the record shows both the type and the stored fields.",
        "Check the object's type, decode it, then verify.",
        _dv(
            "sy-apply-decode-and-type",
            _clean,
            ["git cat-file -t {p}1", "git cat-file -p {p}1", STATUS, GRAPH],
            _read_eval(["git cat-file -t", "git cat-file -p", "git status", "git log"]),
            details=["{p}1"],
        ),
        checks=[
            _required_check("The object was typed and decoded.", ["git cat-file -t", "git cat-file -p"]),
        ],
        command_forms=["git-cat-file/type", *CORE_TAGS],
        adventure="skyline-git-machinery-workflows",
        workflow=True,
        max_counted_commands=8,
    ),
]


LEVELS = [
    *REVISION_DRILLS,
    *REVISION_WORKFLOWS,
    *HIDDEN_DRILLS,
    *HIDDEN_WORKFLOWS,
    *REPEATED_DRILLS,
    *REPEATED_WORKFLOWS,
    *REALITIES_DRILLS,
    *REALITIES_WORKFLOWS,
    *ENCHANT_DRILLS,
    *ENCHANT_WORKFLOWS,
    *GUARD_DRILLS,
    *GUARD_WORKFLOWS,
    *RESTORE_DRILLS,
    *RESTORE_WORKFLOWS,
    *SERVE_DRILLS,
    *SERVE_WORKFLOWS,
    *MIGRATE_DRILLS,
    *MIGRATE_WORKFLOWS,
    *MACHINERY_DRILLS,
    *MACHINERY_WORKFLOWS,
]

__all__ = ["LEVELS"]
