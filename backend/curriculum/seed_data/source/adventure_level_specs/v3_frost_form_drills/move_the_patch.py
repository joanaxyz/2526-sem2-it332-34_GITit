"""Frostbound Citadel Chapter 4: Move the Patch form drills."""

from __future__ import annotations

from ..common import q
from ..form_drill_support import (
    CORE_FORM_TAGS,
    GRAPH_COMMAND,
    STATUS_COMMAND,
    build_clean_form_state,
    build_drill_variants,
    build_read_evaluation,
    build_requirement_evaluation,
    required_command_check,
)
from ._fixtures import (
    _cherry_conflict,
    _meta,
    _stashed,
    _work,
)


DRILLS = [
    q(
        "git-range-diff/series",
        "fm-intro-range-diff",
        "Compare two versions of a patch series",
        "An older candidate branch and the current feature/work branch both claim to contain the same fix. Compare the two patch series (the exact ranges are in Copy details) to see how the fix evolved.",
        "Compare the old series against the current branch's series.",
        build_drill_variants(
            "fm-intro-range-diff",
            build_clean_form_state,
            ["git range-diff {p}0..old/series {p}0..feature/work"],
            build_read_evaluation(["git range-diff {p}0..old/series {p}0..feature/work"]),
            details=["{p}0..old/series", "{p}0..feature/work"],
        ),
        checks=[required_command_check("The two patch series were compared.", ["git range-diff"])],
        adventure="frost-move-the-patch-drills",
    ),
    q(
        "git-stash/push-untracked-message",
        "fm-intro-stash-push",
        "Shelve unfinished work, untracked included",
        "An urgent task interrupts your unfinished work, which includes a brand-new untracked file. Stash everything — tracked and untracked — using the stash message 'Shelve relay draft'.",
        "Stash the local work, including untracked files, with the message 'Shelve relay draft'.",
        build_drill_variants(
            "fm-intro-stash-push",
            _work,
            ["git stash push -u -m 'Shelve relay draft'"],
            build_requirement_evaluation({}, ["git stash push -u"], rules=[_meta("last_stash_action", "push")]),
        ),
        checks=[
            {
                "label": "The draft is stashed with untracked work included.",
                "requirement": {"rules": [_meta("last_stash_action", "push")]},
            }
        ],
        details=["Shelve relay draft"],
        adventure="frost-move-the-patch-drills",
        workflow=True,
    ),
    q(
        "git-stash/show-patch",
        "fm-intro-stash-show",
        "Look inside a stash entry",
        "There is a stash entry called 'hotfix draft' and nobody remembers exactly what it holds. Inspect the entry stash@{0} before it is restored anywhere.",
        "Show the contents of the stash entry stash@{0}.",
        build_drill_variants(
            "fm-intro-stash-show",
            _stashed,
            ["git stash show stash@{0}"],
            build_read_evaluation(["git stash show stash@{0}"]),
        ),
        checks=[required_command_check("The stash entry was inspected before restoring.", ["git stash show"])],
        details=["stash@{0}"],
        adventure="frost-move-the-patch-drills",
    ),
    q(
        "git-stash/apply-indexed",
        "fm-intro-stash-apply",
        "Restore stashed work, keep the copy",
        "The stashed hotfix is needed again, but the stash copy must survive in case this attempt fails. Apply the entry stash@{0} without removing it from the stash.",
        "Apply the stash entry stash@{0} while keeping it on the stash list.",
        build_drill_variants(
            "fm-intro-stash-apply",
            _stashed,
            ["git stash apply stash@{0}"],
            build_requirement_evaluation({}, ["git stash apply"], rules=[_meta("last_stash_action", "apply")]),
        ),
        checks=[
            {
                "label": "The stashed work is restored and the stash copy kept.",
                "requirement": {"rules": [_meta("last_stash_action", "apply")]},
            }
        ],
        details=["stash@{0}"],
        adventure="frost-move-the-patch-drills",
        workflow=True,
    ),
    q(
        "git-stash/pop-indexed",
        "fm-intro-stash-pop",
        "Restore stashed work and remove the entry",
        "The interruption is over for good. Restore the stashed hotfix and remove the entry from the stash in one step, using stash@{0}.",
        "Pop the stash entry stash@{0} back into the working tree.",
        build_drill_variants(
            "fm-intro-stash-pop",
            _stashed,
            ["git stash pop stash@{0}"],
            build_requirement_evaluation({}, ["git stash pop"], rules=[_meta("last_stash_action", "pop")]),
        ),
        checks=[
            {
                "label": "The stashed work is restored and the entry removed.",
                "requirement": {"rules": [_meta("last_stash_action", "pop")]},
            }
        ],
        details=["stash@{0}"],
        adventure="frost-move-the-patch-drills",
        workflow=True,
    ),
    q(
        "git-stash/drop-indexed",
        "fm-intro-stash-drop",
        "Delete a stale stash entry",
        "The stashed draft was replaced by a better fix that already landed. Drop the stale entry stash@{0} so nobody restores it by mistake.",
        "Drop the stash entry stash@{0}.",
        build_drill_variants(
            "fm-intro-stash-drop",
            _stashed,
            ["git stash drop stash@{0}"],
            build_requirement_evaluation({}, ["git stash drop"], rules=[_meta("last_stash_action", "drop")]),
        ),
        checks=[
            {
                "label": "The stale entry is gone from the stash.",
                "requirement": {"rules": [_meta("last_stash_action", "drop")]},
            }
        ],
        details=["stash@{0}"],
        adventure="frost-move-the-patch-drills",
        workflow=True,
    ),
    q(
        "git-cherry-pick/abort-advanced",
        "fm-intro-cherry-abort",
        "Back out of a stuck cherry-pick",
        "A cherry-pick stopped halfway and the half-applied change sitting in staging is wrong for this branch. Abort the cherry-pick and return the branch to its original state.",
        "Abort the in-progress cherry-pick cleanly.",
        build_drill_variants(
            "fm-intro-cherry-abort",
            _cherry_conflict,
            ["git cherry-pick --abort"],
            build_requirement_evaluation(
                {"working_tree_clean": True, "staging_empty": True},
                ["git cherry-pick --abort"],
                rules=[_meta("last_cherry_pick_aborted", True)],
            ),
        ),
        checks=[
            {
                "label": "The cherry-pick is gone and the workspace is clean.",
                "requirement": {"staging_empty": True, "working_tree_clean": True},
            }
        ],
        adventure="frost-move-the-patch-drills",
        workflow=True,
    ),
]

WORKFLOWS = [
    q(
        "git-stash/push-untracked-message",
        "fm-apply-shelve-and-inspect",
        "Stash the work, then check the entry",
        "Stash the interrupted work — untracked file included — using the message 'Shelve probe wiring', then inspect the new entry to confirm it holds everything.",
        "Stash with the message 'Shelve probe wiring', inspect stash@{0}, then verify.",
        build_drill_variants(
            "fm-apply-shelve-and-inspect",
            _work,
            ["git stash push -u -m 'Shelve probe wiring'", "git stash show stash@{0}", STATUS_COMMAND, GRAPH_COMMAND],
            build_requirement_evaluation(
                {},
                ["git stash push -u", "git stash show", "git status", "git log"],
                rules=[_meta("last_stash_action", "push")],
            ),
        ),
        checks=[
            {
                "label": "The work is stashed with untracked files included.",
                "requirement": {"rules": [_meta("last_stash_action", "push")]},
            },
            required_command_check("The new stash entry was inspected.", ["git stash show"]),
        ],
        details=["Shelve probe wiring", "stash@{0}"],
        command_forms=["git-stash/show-patch", *CORE_FORM_TAGS],
        adventure="frost-move-the-patch-workflows",
        workflow=True,
        max_counted_commands=8,
    ),
    q(
        "git-stash/apply-indexed",
        "fm-apply-inspect-then-apply",
        "Check the entry, then restore carefully",
        "Before the stashed hotfix goes back into the working tree, inspect the entry stash@{0}, apply it while keeping the stash copy, and confirm the restore landed.",
        "Inspect stash@{0}, apply it keeping the copy, then verify the state.",
        build_drill_variants(
            "fm-apply-inspect-then-apply",
            _stashed,
            ["git stash show stash@{0}", "git stash apply stash@{0}", STATUS_COMMAND, GRAPH_COMMAND],
            build_requirement_evaluation(
                {},
                ["git stash show", "git stash apply", "git status", "git log"],
                rules=[_meta("last_stash_action", "apply")],
            ),
        ),
        checks=[
            required_command_check("The entry was inspected before restoring.", ["git stash show"]),
            {
                "label": "The work is restored with the stash copy kept.",
                "requirement": {"rules": [_meta("last_stash_action", "apply")]},
            },
        ],
        details=["stash@{0}"],
        command_forms=["git-stash/show-patch", *CORE_FORM_TAGS],
        adventure="frost-move-the-patch-workflows",
        workflow=True,
        max_counted_commands=8,
    ),
    q(
        "git-stash/pop-indexed",
        "fm-apply-park-and-pop",
        "Park the work, then take it back",
        "Park the in-progress work on the stash using the message 'Park the relay sweep', then take it straight back with a pop once the interruption clears. Confirm the stash is empty again.",
        "Stash with the message 'Park the relay sweep', pop stash@{0}, then verify.",
        build_drill_variants(
            "fm-apply-park-and-pop",
            _work,
            ["git stash push -u -m 'Park the relay sweep'", "git stash pop stash@{0}", STATUS_COMMAND, GRAPH_COMMAND],
            build_requirement_evaluation(
                {},
                ["git stash push -u", "git stash pop", "git status", "git log"],
                rules=[_meta("last_stash_action", "pop")],
            ),
        ),
        checks=[
            required_command_check("The work was parked on the stash.", ["git stash push -u"]),
            {
                "label": "The work is back and the stash entry is gone.",
                "requirement": {"rules": [_meta("last_stash_action", "pop")]},
            },
        ],
        details=["Park the relay sweep", "stash@{0}"],
        command_forms=["git-stash/push-untracked-message", *CORE_FORM_TAGS],
        adventure="frost-move-the-patch-workflows",
        workflow=True,
        max_counted_commands=8,
    ),
    q(
        "git-stash/drop-indexed",
        "fm-apply-audit-then-drop",
        "Check the entry one last time, then delete it",
        "The stash entry stash@{0} is believed stale. Inspect it one last time, drop it, and confirm the working tree was never touched.",
        "Inspect stash@{0}, drop it, then verify the state.",
        build_drill_variants(
            "fm-apply-audit-then-drop",
            _stashed,
            ["git stash show stash@{0}", "git stash drop stash@{0}", STATUS_COMMAND, GRAPH_COMMAND],
            build_requirement_evaluation(
                {},
                ["git stash show", "git stash drop", "git status", "git log"],
                rules=[_meta("last_stash_action", "drop")],
            ),
        ),
        checks=[
            required_command_check("The entry was checked before deleting.", ["git stash show"]),
            {
                "label": "The stale entry is gone from the stash.",
                "requirement": {"rules": [_meta("last_stash_action", "drop")]},
            },
        ],
        details=["stash@{0}"],
        command_forms=["git-stash/show-patch", *CORE_FORM_TAGS],
        adventure="frost-move-the-patch-workflows",
        workflow=True,
        max_counted_commands=8,
    ),
    q(
        "git-stash/apply-indexed",
        "fm-apply-restore-then-clear",
        "Restore the work, then clear the entry",
        "Apply the stashed hotfix from stash@{0} while keeping the copy, confirm the restore landed, then remove the now-redundant entry from the stash.",
        "Apply stash@{0}, then drop the stash copy, then verify the state.",
        build_drill_variants(
            "fm-apply-restore-then-clear",
            _stashed,
            ["git stash apply stash@{0}", "git stash drop stash@{0}", STATUS_COMMAND, GRAPH_COMMAND],
            build_requirement_evaluation(
                {},
                ["git stash apply", "git stash drop", "git status", "git log"],
                rules=[_meta("last_stash_action", "drop")],
            ),
        ),
        checks=[
            required_command_check("The work was restored before clearing the stash.", ["git stash apply"]),
            {
                "label": "The redundant stash entry is gone.",
                "requirement": {"rules": [_meta("last_stash_action", "drop")]},
            },
        ],
        details=["stash@{0}"],
        command_forms=["git-stash/drop-indexed", *CORE_FORM_TAGS],
        adventure="frost-move-the-patch-workflows",
        workflow=True,
        max_counted_commands=8,
    ),
    q(
        "git-stash/pop-indexed",
        "fm-apply-inspect-then-pop",
        "Confirm the entry, then pop it",
        "The interruption is over. Inspect the stash entry stash@{0} to confirm it is the right one, then pop it back into the working tree and verify the restore.",
        "Inspect stash@{0}, pop it, then verify the state.",
        build_drill_variants(
            "fm-apply-inspect-then-pop",
            _stashed,
            ["git stash show stash@{0}", "git stash pop stash@{0}", STATUS_COMMAND, GRAPH_COMMAND],
            build_requirement_evaluation(
                {},
                ["git stash show", "git stash pop", "git status", "git log"],
                rules=[_meta("last_stash_action", "pop")],
            ),
        ),
        checks=[
            required_command_check("The entry was confirmed before popping.", ["git stash show"]),
            {
                "label": "The work is restored and the entry removed.",
                "requirement": {"rules": [_meta("last_stash_action", "pop")]},
            },
        ],
        details=["stash@{0}"],
        command_forms=["git-stash/show-patch", *CORE_FORM_TAGS],
        adventure="frost-move-the-patch-workflows",
        workflow=True,
        max_counted_commands=8,
    ),
    q(
        "git-cherry-pick/abort-advanced",
        "fm-apply-inspect-then-back-out",
        "Confirm the damage, then back out",
        "Check what the stuck cherry-pick left in staging, then abort it and read the history to prove the branch returned to its original tip.",
        "Check the state, abort the cherry-pick, then verify the history.",
        build_drill_variants(
            "fm-apply-inspect-then-back-out",
            _cherry_conflict,
            [STATUS_COMMAND, "git cherry-pick --abort", GRAPH_COMMAND],
            build_requirement_evaluation(
                {"working_tree_clean": True, "staging_empty": True},
                ["git status", "git cherry-pick --abort", "git log"],
                rules=[_meta("last_cherry_pick_aborted", True)],
            ),
        ),
        checks=[
            {
                "label": "The cherry-pick is gone and the workspace is clean.",
                "requirement": {"staging_empty": True, "working_tree_clean": True},
            },
            required_command_check("The recovered history was verified.", ["git log"]),
        ],
        command_forms=CORE_FORM_TAGS,
        adventure="frost-move-the-patch-workflows",
        workflow=True,
        max_counted_commands=8,
    ),
    q(
        "git-cherry-pick/abort-advanced",
        "fm-apply-abort-under-orders",
        "Abort the cherry-pick immediately",
        "The transplant was called off mid-flight. Abort the cherry-pick right away, then check the workspace and history so the rollback can be reported.",
        "Abort the cherry-pick, then verify the workspace and history.",
        build_drill_variants(
            "fm-apply-abort-under-orders",
            _cherry_conflict,
            ["git cherry-pick --abort", STATUS_COMMAND, GRAPH_COMMAND],
            build_requirement_evaluation(
                {"working_tree_clean": True, "staging_empty": True},
                ["git cherry-pick --abort", "git status", "git log"],
                rules=[_meta("last_cherry_pick_aborted", True)],
            ),
        ),
        checks=[
            {
                "label": "The cherry-pick is gone and the workspace is clean.",
                "requirement": {"staging_empty": True, "working_tree_clean": True},
            },
            required_command_check("The rollback was verified.", ["git status", "git log"]),
        ],
        command_forms=CORE_FORM_TAGS,
        adventure="frost-move-the-patch-workflows",
        workflow=True,
        max_counted_commands=8,
    ),
]

