"""Frostbound Citadel Chapter 1: Temper the Commit form drills."""

from __future__ import annotations

from ..common import q
from ..form_drill_support import (
    CORE_FORM_TAGS,
    GRAPH_COMMAND,
    STATUS_COMMAND,
    build_broken_form_state,
    build_clean_form_state,
    build_drill_variants,
    build_read_evaluation,
    build_requirement_evaluation,
    required_command_check,
)
from ._fixtures import (
    _broken_dirty,
    _dirty,
    _meta,
    _staged,
)


DRILLS = [
    q(
        "git-diff/stat-advanced",
        "ft-intro-diff-stat",
        "Measure the pending change",
        "A teammate left an unstaged edit in src/app.ts and the reviewer wants to know how big it is before it goes anywhere.",
        "Show a per-file summary of how much the working tree has changed.",
        build_drill_variants("ft-intro-diff-stat", _dirty, ["git diff --stat"], build_read_evaluation(["git diff --stat"])),
        checks=[required_command_check("The change size was measured before staging.", ["git diff --stat"])],
        details=["src/app.ts"],
        adventure="frost-temper-the-commit-drills",
    ),
    q(
        "git-diff/check-whitespace",
        "ft-intro-diff-check",
        "Check the change for whitespace errors",
        "The editor that produced the pending src/app.ts change is known to add trailing whitespace. The reviewer will reject the change unless it is checked first.",
        "Check the working-tree changes for whitespace errors.",
        build_drill_variants("ft-intro-diff-check", _dirty, ["git diff --check"], build_read_evaluation(["git diff --check"])),
        checks=[required_command_check("The change was checked for whitespace errors.", ["git diff --check"])],
        details=["src/app.ts"],
        adventure="frost-temper-the-commit-drills",
    ),
    q(
        "git-add/patch-advanced",
        "ft-intro-add-patch",
        "Stage the change hunk by hunk",
        "Only part of the pending edit to src/app.ts was approved in review. Stage the file hunk by hunk so you choose exactly what goes into the next commit.",
        "Stage src/app.ts using hunk-level staging.",
        build_drill_variants(
            "ft-intro-add-patch",
            _dirty,
            ["git add -p src/app.ts"],
            build_requirement_evaluation({}, ["git add -p"], rules=[{"type": "staging_not_empty"}]),
        ),
        checks=[
            {
                "label": "The approved hunks are staged for the next commit.",
                "requirement": {"rules": [{"type": "staging_not_empty"}]},
            }
        ],
        details=["src/app.ts"],
        adventure="frost-temper-the-commit-drills",
        workflow=True,
    ),
    q(
        "git-add/tracked-only-advanced",
        "ft-intro-add-update",
        "Stage tracked edits only",
        "The working tree mixes an approved edit to the tracked file src/app.ts with scratch files that must stay out of history. Stage only what is already tracked.",
        "Stage every tracked edit without adding any untracked file.",
        build_drill_variants(
            "ft-intro-add-update",
            _dirty,
            ["git add -u"],
            build_requirement_evaluation({}, ["git add -u"], rules=[{"type": "staging_not_empty"}]),
        ),
        checks=[
            {
                "label": "Tracked edits are staged for the next commit.",
                "requirement": {"rules": [{"type": "staging_not_empty"}]},
            }
        ],
        adventure="frost-temper-the-commit-drills",
        workflow=True,
    ),
    q(
        "git-commit/amend-advanced",
        "ft-intro-amend",
        "Rewrite the unpublished tip commit",
        "The latest commit has not been pushed yet: it is missing the staged release notes and its message is a placeholder. Rewrite it in place using the commit message 'Temper the relay tip'.",
        "Amend the latest commit so it includes the staged work and carries the message 'Temper the relay tip'.",
        build_drill_variants(
            "ft-intro-amend",
            _staged,
            ["git commit --amend -m 'Temper the relay tip'"],
            build_requirement_evaluation(
                {
                    "latest_commit": {"branch": "main", "message_contains": ["Temper the relay tip"]},
                    "staging_empty": True,
                },
                ["git commit --amend"],
            ),
        ),
        checks=[
            {
                "label": "The tip commit now carries the requested message.",
                "requirement": {
                    "latest_commit": {"branch": "main", "message_contains": ["Temper the relay tip"]}
                },
            }
        ],
        details=["Temper the relay tip"],
        adventure="frost-temper-the-commit-drills",
        workflow=True,
    ),
    q(
        "git-commit/amend-no-edit-advanced",
        "ft-intro-amend-no-edit",
        "Fold staged work into the tip commit",
        "The staged file src/notes.md belongs to the commit already at the tip, and that commit's message is already correct. Fold the staged work in without changing the message.",
        "Amend the tip commit with the staged content while keeping its existing message.",
        build_drill_variants(
            "ft-intro-amend-no-edit",
            _staged,
            ["git commit --amend --no-edit"],
            build_requirement_evaluation(
                {
                    "latest_commit": {"branch": "main", "contains_paths": ["src/notes.md"]},
                    "staging_empty": True,
                },
                ["git commit --amend --no-edit"],
            ),
        ),
        checks=[
            {
                "label": "The staged file is folded into the existing tip commit.",
                "requirement": {"latest_commit": {"branch": "main", "contains_paths": ["src/notes.md"]}},
            }
        ],
        details=["src/notes.md"],
        adventure="frost-temper-the-commit-drills",
        workflow=True,
    ),
    q(
        "git-reset/soft",
        "ft-intro-reset-soft",
        "Step the branch back, keep the work",
        "The commit at the tip of main broke the deployment, but its changes are still needed for rework. Move main back to the last good commit (its id is in Copy details) while keeping the changes.",
        "Soft-reset main to the last good commit so the work stays available for restaging.",
        build_drill_variants(
            "ft-intro-reset-soft",
            build_broken_form_state,
            ["git reset --soft {p}1"],
            build_requirement_evaluation({}, ["git reset --soft"], rules=[{"type": "branch_points_to", "branch": "main", "commit": "{p}1"}]),
            details=["{p}1"],
        ),
        checks=[required_command_check("The branch stepped back with the work preserved.", ["git reset --soft"])],
        adventure="frost-temper-the-commit-drills",
        workflow=True,
    ),
    q(
        "git-reset/mixed",
        "ft-intro-reset-mixed",
        "Step back and unstage everything",
        "The broken tip commit needs to be rebuilt from scratch, starting from an unstaged state. Move main back to the last good commit (see Copy details) and leave the changes unstaged.",
        "Mixed-reset main to the last good commit.",
        build_drill_variants(
            "ft-intro-reset-mixed",
            build_broken_form_state,
            ["git reset --mixed {p}1"],
            build_requirement_evaluation({}, ["git reset --mixed"], rules=[{"type": "branch_points_to", "branch": "main", "commit": "{p}1"}]),
            details=["{p}1"],
        ),
        checks=[required_command_check("The branch stepped back with nothing staged.", ["git reset --mixed"])],
        adventure="frost-temper-the-commit-drills",
        workflow=True,
    ),
    q(
        "git-reset/hard-advanced",
        "ft-intro-reset-hard",
        "Discard the broken state completely",
        "Both the broken tip commit and the local edits on top of it have been rejected. Nothing local is worth keeping: move main back to the last good commit (see Copy details) and discard everything else.",
        "Hard-reset main to the last good commit, discarding local edits.",
        build_drill_variants(
            "ft-intro-reset-hard",
            _broken_dirty,
            ["git reset --hard {p}1"],
            build_requirement_evaluation(
                {"working_tree_clean": True},
                ["git reset --hard"],
                rules=[{"type": "branch_points_to", "branch": "main", "commit": "{p}1"}],
            ),
            details=["{p}1"],
        ),
        checks=[
            {
                "label": "The workspace is clean at the last good commit.",
                "requirement": {"working_tree_clean": True},
            }
        ],
        adventure="frost-temper-the-commit-drills",
        workflow=True,
    ),
    q(
        "git-restore/source-advanced",
        "ft-intro-restore-source",
        "Bring back one file from an old commit",
        "Today's src/app.ts is suspected of being wrong. Copy the version from the first commit (its id is in Copy details) into the working tree so the two versions can be compared. No branch should move.",
        "Restore src/app.ts from the old commit into the working tree.",
        build_drill_variants(
            "ft-intro-restore-source",
            build_clean_form_state,
            ["git restore --source {p}0 src/app.ts"],
            build_requirement_evaluation({}, ["git restore --source"], rules=[{"type": "working_tree_dirty"}]),
            details=["{p}0", "src/app.ts"],
        ),
        checks=[
            {
                "label": "The old version of the file is in the working tree.",
                "requirement": {"rules": [{"type": "working_tree_dirty"}]},
            }
        ],
        adventure="frost-temper-the-commit-drills",
        workflow=True,
    ),
    q(
        "git-tag/lightweight-advanced",
        "ft-intro-tag-checkpoint",
        "Tag the known-good commit",
        "Before any history rewriting starts, the team wants the current trusted commit to have a name so later work can be compared against it. Create a lightweight tag called relay-checkpoint at the current commit.",
        "Create the lightweight tag relay-checkpoint at HEAD.",
        build_drill_variants(
            "ft-intro-tag-checkpoint",
            build_clean_form_state,
            ["git tag relay-checkpoint"],
            build_requirement_evaluation({}, ["git tag"], rules=[_meta("last_tag_created", "relay-checkpoint")]),
        ),
        checks=[
            {
                "label": "The checkpoint tag exists at the trusted commit.",
                "requirement": {"rules": [_meta("last_tag_created", "relay-checkpoint")]},
            }
        ],
        details=["relay-checkpoint"],
        adventure="frost-temper-the-commit-drills",
        workflow=True,
    ),
]

WORKFLOWS = [
    q(
        "git-add/patch-advanced",
        "ft-apply-measured-staging",
        "Measure, then stage precisely",
        "A mixed edit to src/app.ts is waiting. Measure how big it is, stage only the approved hunks, then check the repository state to confirm the split.",
        "Measure the change, stage src/app.ts hunk by hunk, then verify with status and log.",
        build_drill_variants(
            "ft-apply-measured-staging",
            _dirty,
            ["git diff --stat", "git add -p src/app.ts", STATUS_COMMAND, GRAPH_COMMAND],
            build_requirement_evaluation({}, ["git diff --stat", "git add -p", "git status", "git log"], rules=[{"type": "staging_not_empty"}]),
        ),
        checks=[
            required_command_check("The change was measured before staging.", ["git diff --stat"]),
            {
                "label": "The approved hunks are staged.",
                "requirement": {"rules": [{"type": "staging_not_empty"}]},
            },
            required_command_check("The resulting state was verified.", ["git status", "git log"]),
        ],
        details=["src/app.ts"],
        command_forms=["git-diff/stat-advanced", *CORE_FORM_TAGS],
        adventure="frost-temper-the-commit-workflows",
        workflow=True,
        max_counted_commands=8,
    ),
    q(
        "git-add/patch-advanced",
        "ft-apply-guarded-staging",
        "Check whitespace, then stage",
        "The pending src/app.ts edit came from an editor that mangles whitespace. Prove the change is clean, then stage it hunk by hunk and verify the state.",
        "Check for whitespace errors, stage src/app.ts hunk by hunk, then verify.",
        build_drill_variants(
            "ft-apply-guarded-staging",
            _dirty,
            ["git diff --check", "git add -p src/app.ts", STATUS_COMMAND, GRAPH_COMMAND],
            build_requirement_evaluation({}, ["git diff --check", "git add -p", "git status", "git log"], rules=[{"type": "staging_not_empty"}]),
        ),
        checks=[
            required_command_check("The change was checked for whitespace errors.", ["git diff --check"]),
            {
                "label": "The clean hunks are staged.",
                "requirement": {"rules": [{"type": "staging_not_empty"}]},
            },
            required_command_check("The resulting state was verified.", ["git status", "git log"]),
        ],
        details=["src/app.ts"],
        command_forms=["git-diff/check-whitespace", *CORE_FORM_TAGS],
        adventure="frost-temper-the-commit-workflows",
        workflow=True,
        max_counted_commands=8,
    ),
    q(
        "git-add/tracked-only-advanced",
        "ft-apply-tracked-sweep",
        "Measure, then stage tracked edits",
        "Every tracked edit in the working tree is approved; nothing untracked is. Measure the pending work, stage the tracked edits only, and confirm the result.",
        "Measure the change, stage tracked edits only, then verify with status and log.",
        build_drill_variants(
            "ft-apply-tracked-sweep",
            _dirty,
            ["git diff --stat", "git add -u", STATUS_COMMAND, GRAPH_COMMAND],
            build_requirement_evaluation({}, ["git diff --stat", "git add -u", "git status", "git log"], rules=[{"type": "staging_not_empty"}]),
        ),
        checks=[
            required_command_check("The pending work was measured.", ["git diff --stat"]),
            {
                "label": "Tracked edits are staged; untracked files are not.",
                "requirement": {"rules": [{"type": "staging_not_empty"}]},
            },
            required_command_check("The resulting state was verified.", ["git status", "git log"]),
        ],
        command_forms=["git-diff/stat-advanced", *CORE_FORM_TAGS],
        adventure="frost-temper-the-commit-workflows",
        workflow=True,
        max_counted_commands=8,
    ),
    q(
        "git-commit/amend-advanced",
        "ft-apply-fold-and-rename",
        "Fold the fix into the tip commit",
        "A reviewed fix to src/app.ts belongs inside the unpublished tip commit, which also needs its real message. Check the change, stage the tracked edit, then rewrite the tip using the commit message 'Fold the field fix into the tip'.",
        "Check whitespace, stage tracked edits, then amend the tip with the message 'Fold the field fix into the tip'.",
        build_drill_variants(
            "ft-apply-fold-and-rename",
            _dirty,
            ["git diff --check", "git add -u", "git commit --amend -m 'Fold the field fix into the tip'", STATUS_COMMAND, GRAPH_COMMAND],
            build_requirement_evaluation(
                {
                    "latest_commit": {"branch": "main", "message_contains": ["Fold the field fix into the tip"]},
                    "working_tree_clean": True,
                    "staging_empty": True,
                },
                ["git diff --check", "git add -u", "git commit --amend", "git status", "git log"],
            ),
        ),
        checks=[
            required_command_check("The change was checked before staging.", ["git diff --check"]),
            {
                "label": "The tip commit carries the fix and the requested message.",
                "requirement": {
                    "latest_commit": {"branch": "main", "message_contains": ["Fold the field fix into the tip"]}
                },
            },
            required_command_check("The resulting history was verified.", ["git log"]),
        ],
        details=["Fold the field fix into the tip"],
        command_forms=["git-add/tracked-only-advanced", "git-diff/check-whitespace", *CORE_FORM_TAGS],
        adventure="frost-temper-the-commit-workflows",
        workflow=True,
        max_counted_commands=8,
    ),
    q(
        "git-commit/amend-advanced",
        "ft-apply-clarify-tip",
        "Absorb staged notes and fix the message",
        "The tip commit has a placeholder message and the release notes are still only staged. Rewrite the tip so it absorbs the staged notes and carries the commit message 'Clarify the relay tip'.",
        "Amend the tip with the staged notes and the message 'Clarify the relay tip', then verify.",
        build_drill_variants(
            "ft-apply-clarify-tip",
            _staged,
            ["git diff --stat", "git commit --amend -m 'Clarify the relay tip'", STATUS_COMMAND, GRAPH_COMMAND],
            build_requirement_evaluation(
                {
                    "latest_commit": {"branch": "main", "message_contains": ["Clarify the relay tip"]},
                    "staging_empty": True,
                },
                ["git diff --stat", "git commit --amend", "git status", "git log"],
            ),
        ),
        checks=[
            {
                "label": "The tip commit carries the requested message.",
                "requirement": {"latest_commit": {"branch": "main", "message_contains": ["Clarify the relay tip"]}},
            },
            required_command_check("The resulting history was verified.", ["git log"]),
        ],
        details=["Clarify the relay tip"],
        command_forms=["git-diff/stat-advanced", *CORE_FORM_TAGS],
        adventure="frost-temper-the-commit-workflows",
        workflow=True,
        max_counted_commands=8,
    ),
    q(
        "git-commit/amend-no-edit-advanced",
        "ft-apply-silent-fold",
        "Fold hunks in, keep the message",
        "The reviewed hunks of src/app.ts belong to the tip commit, whose message is already approved. Stage the hunks, then fold them in without changing the message.",
        "Stage src/app.ts hunk by hunk, amend without editing the message, then verify.",
        build_drill_variants(
            "ft-apply-silent-fold",
            _dirty,
            ["git add -p src/app.ts", "git commit --amend --no-edit", STATUS_COMMAND, GRAPH_COMMAND],
            build_requirement_evaluation(
                {"staging_empty": True},
                ["git add -p", "git commit --amend --no-edit", "git status", "git log"],
            ),
        ),
        checks=[
            required_command_check(
                "The staged hunks were folded into the tip without renaming it.",
                ["git add -p", "git commit --amend --no-edit"],
            ),
            required_command_check("The resulting history was verified.", ["git log"]),
        ],
        details=["src/app.ts"],
        command_forms=["git-add/patch-advanced", *CORE_FORM_TAGS],
        adventure="frost-temper-the-commit-workflows",
        workflow=True,
        max_counted_commands=8,
    ),
    q(
        "git-commit/amend-no-edit-advanced",
        "ft-apply-checked-fold",
        "Check, then fold without renaming",
        "Staged notes in src/notes.md must join the tip commit unchanged. Check the pending state first, then fold the staged work in while keeping the approved message.",
        "Check whitespace, amend without editing the message, then verify the history.",
        build_drill_variants(
            "ft-apply-checked-fold",
            _staged,
            ["git diff --check", "git commit --amend --no-edit", STATUS_COMMAND, GRAPH_COMMAND],
            build_requirement_evaluation(
                {
                    "latest_commit": {"branch": "main", "contains_paths": ["src/notes.md"]},
                    "staging_empty": True,
                },
                ["git diff --check", "git commit --amend --no-edit", "git status", "git log"],
            ),
        ),
        checks=[
            {
                "label": "The staged notes are folded into the existing tip.",
                "requirement": {"latest_commit": {"branch": "main", "contains_paths": ["src/notes.md"]}},
            },
            required_command_check("The resulting history was verified.", ["git log"]),
        ],
        details=["src/notes.md"],
        command_forms=["git-diff/check-whitespace", *CORE_FORM_TAGS],
        adventure="frost-temper-the-commit-workflows",
        workflow=True,
        max_counted_commands=8,
    ),
    q(
        "git-reset/soft",
        "ft-apply-soft-retreat",
        "Step back softly from the bad tip",
        "The broken commit at the tip still holds valuable changes. Measure the state, move main back to the last good commit (see Copy details) while keeping the work, then verify.",
        "Measure the state, soft-reset main to the last good commit, then verify.",
        build_drill_variants(
            "ft-apply-soft-retreat",
            build_broken_form_state,
            ["git diff --stat", "git reset --soft {p}1", STATUS_COMMAND, GRAPH_COMMAND],
            build_requirement_evaluation({}, ["git diff --stat", "git reset --soft", "git status", "git log"], rules=[{"type": "branch_points_to", "branch": "main", "commit": "{p}1"}]),
            details=["{p}1"],
        ),
        checks=[
            required_command_check("The branch stepped back with the work preserved.", ["git reset --soft"]),
            required_command_check("The resulting state was verified.", ["git status", "git log"]),
        ],
        command_forms=["git-diff/stat-advanced", *CORE_FORM_TAGS],
        adventure="frost-temper-the-commit-workflows",
        workflow=True,
        max_counted_commands=8,
    ),
    q(
        "git-reset/soft",
        "ft-apply-layered-retreat",
        "Step back in two layers",
        "First step back softly to the last good commit to inspect what the broken tip held, then release the snapshot from staging by stepping back to the first commit with a mixed reset. Both commit ids are in Copy details.",
        "Soft-reset to the last good commit, then mixed-reset to the first commit, then verify.",
        build_drill_variants(
            "ft-apply-layered-retreat",
            build_broken_form_state,
            ["git reset --soft {p}1", "git reset --mixed {p}0", STATUS_COMMAND, GRAPH_COMMAND],
            build_requirement_evaluation({}, ["git reset --soft", "git reset --mixed", "git status", "git log"], rules=[{"type": "branch_points_to", "branch": "main", "commit": "{p}0"}]),
            details=["{p}1", "{p}0"],
        ),
        checks=[
            required_command_check("The branch stepped back in two deliberate layers.", ["git reset --soft", "git reset --mixed"]),
            required_command_check("The resulting state was verified.", ["git status", "git log"]),
        ],
        command_forms=["git-reset/mixed", *CORE_FORM_TAGS],
        adventure="frost-temper-the-commit-workflows",
        workflow=True,
        max_counted_commands=8,
    ),
    q(
        "git-reset/mixed",
        "ft-apply-mixed-rework",
        "Unstage the broken commit for rework",
        "The broken tip commit needs a fresh file-selection pass. Measure it, move main back to the last good commit (see Copy details) with a mixed reset, then check what is left to restage.",
        "Measure the change, mixed-reset main to the last good commit, then verify.",
        build_drill_variants(
            "ft-apply-mixed-rework",
            build_broken_form_state,
            ["git diff --stat", "git reset --mixed {p}1", STATUS_COMMAND, GRAPH_COMMAND],
            build_requirement_evaluation({}, ["git diff --stat", "git reset --mixed", "git status", "git log"], rules=[{"type": "branch_points_to", "branch": "main", "commit": "{p}1"}]),
            details=["{p}1"],
        ),
        checks=[
            required_command_check("The commit was unstaged for rework.", ["git reset --mixed"]),
            required_command_check("The resulting state was verified.", ["git status", "git log"]),
        ],
        command_forms=["git-diff/stat-advanced", *CORE_FORM_TAGS],
        adventure="frost-temper-the-commit-workflows",
        workflow=True,
        max_counted_commands=8,
    ),
    q(
        "git-reset/hard-advanced",
        "ft-apply-condemned-floor",
        "Discard the rejected work entirely",
        "Review rejected both the tip commit and every local edit on top of it. Check what would be lost, then hard-reset main to the last good commit (see Copy details) and confirm the workspace is clean.",
        "Check the pending edits, hard-reset to the last good commit, then verify a clean state.",
        build_drill_variants(
            "ft-apply-condemned-floor",
            _broken_dirty,
            ["git diff --check", "git reset --hard {p}1", STATUS_COMMAND, GRAPH_COMMAND],
            build_requirement_evaluation(
                {"working_tree_clean": True},
                ["git diff --check", "git reset --hard", "git status", "git log"],
                rules=[{"type": "branch_points_to", "branch": "main", "commit": "{p}1"}],
            ),
            details=["{p}1"],
        ),
        checks=[
            {
                "label": "The workspace is clean at the last good commit.",
                "requirement": {"working_tree_clean": True},
            },
            required_command_check("The resulting state was verified.", ["git status", "git log"]),
        ],
        command_forms=["git-diff/check-whitespace", *CORE_FORM_TAGS],
        adventure="frost-temper-the-commit-workflows",
        workflow=True,
        max_counted_commands=8,
    ),
    q(
        "git-restore/source-advanced",
        "ft-apply-recover-then-compare",
        "Reset hard, then recover one file",
        "After discarding the rejected work, one file is still needed from the first commit for comparison. Hard-reset to the last good commit, then restore src/app.ts from the first commit. Both ids are in Copy details.",
        "Hard-reset to the last good commit, restore src/app.ts from the first commit, then verify.",
        build_drill_variants(
            "ft-apply-recover-then-compare",
            _broken_dirty,
            ["git reset --hard {p}1", "git restore --source {p}0 src/app.ts", STATUS_COMMAND, GRAPH_COMMAND],
            build_requirement_evaluation(
                {},
                ["git reset --hard", "git restore --source", "git status", "git log"],
                rules=[
                    {"type": "branch_points_to", "branch": "main", "commit": "{p}1"},
                    {"type": "working_tree_dirty"},
                ],
            ),
            details=["{p}1", "{p}0", "src/app.ts"],
        ),
        checks=[
            required_command_check("The workspace was reset, then one file recovered.", ["git reset --hard", "git restore --source"]),
            required_command_check("The resulting state was verified.", ["git status", "git log"]),
        ],
        command_forms=["git-reset/hard-advanced", *CORE_FORM_TAGS],
        adventure="frost-temper-the-commit-workflows",
        workflow=True,
        max_counted_commands=8,
    ),
    q(
        "git-restore/source-advanced",
        "ft-apply-foundation-audit",
        "Compare today's file with the original",
        "The team suspects src/app.ts has drifted from its original version. Restore the copy from the first commit (see Copy details) into the working tree, then measure exactly how different today's file is.",
        "Restore src/app.ts from the first commit, then measure the difference.",
        build_drill_variants(
            "ft-apply-foundation-audit",
            build_clean_form_state,
            ["git restore --source {p}0 src/app.ts", "git diff --stat", STATUS_COMMAND, GRAPH_COMMAND],
            build_requirement_evaluation({}, ["git restore --source", "git diff --stat", "git status", "git log"], rules=[{"type": "working_tree_dirty"}]),
            details=["{p}0", "src/app.ts"],
        ),
        checks=[
            {
                "label": "The original version is in the working tree for comparison.",
                "requirement": {"rules": [{"type": "working_tree_dirty"}]},
            },
            required_command_check("The difference was measured.", ["git diff --stat"]),
        ],
        command_forms=["git-diff/stat-advanced", *CORE_FORM_TAGS],
        adventure="frost-temper-the-commit-workflows",
        workflow=True,
        max_counted_commands=8,
    ),
]

