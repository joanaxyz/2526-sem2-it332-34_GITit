"""Frostbound Citadel Chapter 3: Survive the Conflict form drills."""

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
    _conflict,
    _resolved_merge,
)


def _conflict_read(slug, form, title, story, task, command, label):
    return q(
        form,
        slug,
        title,
        story,
        task,
        build_drill_variants(slug, _conflict, [command], build_read_evaluation([command], count=3)),
        checks=[required_command_check(label, [command])],
        details=["src/relay.conf"],
        adventure="frost-survive-the-conflict-drills",
    )

NO_MARKERS = {
    "type": "working_tree_excludes_tokens",
    "path": "src/relay.conf",
    "tokens": ["<<<<<<<"],
}

DRILLS = [
    q(
        "git-merge-tree/branches",
        "fs-intro-merge-tree",
        "Preview a merge without running it",
        "Two branches are about to be integrated and the team wants to know in advance whether they collide. Preview how main and feature/work would combine, without touching the working tree.",
        "Preview the merge of main and feature/work.",
        build_drill_variants(
            "fs-intro-merge-tree",
            build_clean_form_state,
            ["git merge-tree main feature/work"],
            build_read_evaluation(["git merge-tree main feature/work"]),
        ),
        checks=[required_command_check("The merge was previewed without changing anything.", ["git merge-tree"])],
        details=["main feature/work"],
        adventure="frost-survive-the-conflict-drills",
    ),
    _conflict_read(
        "fs-intro-ls-files-u",
        "git-ls-files/unmerged-advanced",
        "List the conflicted index entries",
        "A merge stopped on src/relay.conf. Before editing anything, list the unmerged index entries to see the base version and both sides laid out as stages.",
        "List the unmerged index entries for the conflicted file.",
        "git ls-files -u",
        "The conflict stages were inspected.",
    ),
    _conflict_read(
        "fs-intro-diff-base",
        "git-diff-conflict/base-advanced",
        "Compare the conflict against the base",
        "To judge both sides of the conflict fairly, first read how the conflicted src/relay.conf differs from the version both branches started from.",
        "Compare the conflicted file against the common ancestor version.",
        "git diff --base src/relay.conf",
        "The conflict was compared against its base.",
    ),
    _conflict_read(
        "fs-intro-diff-ours",
        "git-diff-conflict/ours-advanced",
        "Compare against our side",
        "Your own team's change raised the load setting in src/relay.conf. Read how the conflicted file differs from your side before deciding anything.",
        "Compare the conflicted file against our side.",
        "git diff --ours src/relay.conf",
        "Our side of the conflict was inspected.",
    ),
    _conflict_read(
        "fs-intro-diff-theirs",
        "git-diff-conflict/theirs-advanced",
        "Compare against their side",
        "The other team's change switched src/relay.conf to strict mode. Read how the conflicted file differs from their side before deciding anything.",
        "Compare the conflicted file against their side.",
        "git diff --theirs src/relay.conf",
        "Their side of the conflict was inspected.",
    ),
    q(
        "git-checkout-conflict/ours-advanced",
        "fs-intro-checkout-ours",
        "Resolve by taking our side",
        "The decision is made: the raised load setting must stay, and the other team's change will be re-applied later. Resolve the conflicted src/relay.conf by taking our side.",
        "Resolve the conflicted file by taking our side.",
        build_drill_variants(
            "fs-intro-checkout-ours",
            _conflict,
            ["git checkout --ours src/relay.conf"],
            build_requirement_evaluation({}, ["git checkout --ours"], rules=[NO_MARKERS]),
        ),
        checks=[
            {
                "label": "The conflict markers are gone from the file.",
                "requirement": {"rules": [NO_MARKERS]},
            }
        ],
        details=["src/relay.conf"],
        adventure="frost-survive-the-conflict-drills",
        workflow=True,
    ),
    q(
        "git-checkout-conflict/theirs-advanced",
        "fs-intro-checkout-theirs",
        "Resolve by taking their side",
        "Analysis shows the other team was right about this file. Resolve the conflicted src/relay.conf by taking their side.",
        "Resolve the conflicted file by taking their side.",
        build_drill_variants(
            "fs-intro-checkout-theirs",
            _conflict,
            ["git checkout --theirs src/relay.conf"],
            build_requirement_evaluation({}, ["git checkout --theirs"], rules=[NO_MARKERS]),
        ),
        checks=[
            {
                "label": "The conflict markers are gone from the file.",
                "requirement": {"rules": [NO_MARKERS]},
            }
        ],
        details=["src/relay.conf"],
        adventure="frost-survive-the-conflict-drills",
        workflow=True,
    ),
    q(
        "git-merge/abort-advanced",
        "fs-intro-merge-abort",
        "Abort the conflicted merge",
        "New instructions arrived in the middle of the merge: this integration must not happen today. Abort the conflicted merge and return the workspace to the state it had before the merge started.",
        "Abort the in-progress merge safely.",
        build_drill_variants(
            "fs-intro-merge-abort",
            _conflict,
            ["git merge --abort"],
            build_requirement_evaluation({"working_tree_clean": True}, ["git merge --abort"]),
        ),
        checks=[
            {
                "label": "The workspace returned to its pre-merge state.",
                "requirement": {"working_tree_clean": True},
            }
        ],
        adventure="frost-survive-the-conflict-drills",
        workflow=True,
    ),
    q(
        "git-merge/continue-advanced",
        "fs-intro-merge-continue",
        "Finish the resolved merge",
        "The conflicted file has already been resolved and staged; only the merge commit is missing. Continue the merge so the resolution becomes a commit.",
        "Continue the resolved merge to create the merge commit.",
        build_drill_variants(
            "fs-intro-merge-continue",
            _resolved_merge,
            ["git merge --continue"],
            build_requirement_evaluation(
                {"working_tree_clean": True, "staging_empty": True},
                ["git merge --continue"],
                rules=[{"type": "commit_count_equals", "count": 4}],
            ),
        ),
        checks=[
            {
                "label": "The merge commit completed the resolution.",
                "requirement": {"rules": [{"type": "commit_count_equals", "count": 4}]},
            }
        ],
        adventure="frost-survive-the-conflict-drills",
        workflow=True,
    ),
]

WORKFLOWS = [
    q(
        "git-checkout-conflict/ours-advanced",
        "fs-apply-hold-the-ceiling",
        "Inspect the conflict, then keep our change",
        "Read the unmerged index entries and our side's difference, then resolve src/relay.conf by keeping your team's raised load setting. Check the workspace afterward.",
        "Inspect the stages and our side, take our side, then verify the state.",
        build_drill_variants(
            "fs-apply-hold-the-ceiling",
            _conflict,
            ["git ls-files -u", "git diff --ours src/relay.conf", "git checkout --ours src/relay.conf", STATUS_COMMAND, GRAPH_COMMAND],
            build_requirement_evaluation({}, ["git ls-files -u", "git diff --ours", "git checkout --ours", "git status", "git log"], rules=[NO_MARKERS]),
        ),
        checks=[
            required_command_check("The conflict evidence was read first.", ["git ls-files -u", "git diff --ours"]),
            {
                "label": "The conflict markers are gone from the file.",
                "requirement": {"rules": [NO_MARKERS]},
            },
        ],
        details=["src/relay.conf"],
        command_forms=["git-ls-files/unmerged-advanced", "git-diff-conflict/ours-advanced", *CORE_FORM_TAGS],
        adventure="frost-survive-the-conflict-workflows",
        workflow=True,
        max_counted_commands=8,
    ),
    q(
        "git-checkout-conflict/theirs-advanced",
        "fs-apply-adopt-strict-mode",
        "Inspect the conflict, then adopt their change",
        "Read the unmerged index entries and their side's difference, then resolve src/relay.conf by adopting the other team's strict-mode change. Check the workspace afterward.",
        "Inspect the stages and their side, take their side, then verify the state.",
        build_drill_variants(
            "fs-apply-adopt-strict-mode",
            _conflict,
            ["git ls-files -u", "git diff --theirs src/relay.conf", "git checkout --theirs src/relay.conf", STATUS_COMMAND, GRAPH_COMMAND],
            build_requirement_evaluation({}, ["git ls-files -u", "git diff --theirs", "git checkout --theirs", "git status", "git log"], rules=[NO_MARKERS]),
        ),
        checks=[
            required_command_check("The conflict evidence was read first.", ["git ls-files -u", "git diff --theirs"]),
            {
                "label": "The conflict markers are gone from the file.",
                "requirement": {"rules": [NO_MARKERS]},
            },
        ],
        details=["src/relay.conf"],
        command_forms=["git-ls-files/unmerged-advanced", "git-diff-conflict/theirs-advanced", *CORE_FORM_TAGS],
        adventure="frost-survive-the-conflict-workflows",
        workflow=True,
        max_counted_commands=8,
    ),
    q(
        "git-merge/abort-advanced",
        "fs-apply-abort-after-base-check",
        "Check the base, then abort",
        "Compare the conflict against the common ancestor. The difference is too large to resolve safely under deadline, so abort the merge and confirm the workspace returned to its pre-merge state.",
        "Compare against the base, abort the merge, then verify the clean state.",
        build_drill_variants(
            "fs-apply-abort-after-base-check",
            _conflict,
            ["git diff --base src/relay.conf", "git merge --abort", STATUS_COMMAND, GRAPH_COMMAND],
            build_requirement_evaluation({"working_tree_clean": True}, ["git diff --base", "git merge --abort", "git status", "git log"]),
        ),
        checks=[
            required_command_check("The conflict was compared against its base.", ["git diff --base"]),
            {
                "label": "The workspace returned to its pre-merge state.",
                "requirement": {"working_tree_clean": True},
            },
        ],
        command_forms=["git-diff-conflict/base-advanced", *CORE_FORM_TAGS],
        adventure="frost-survive-the-conflict-workflows",
        workflow=True,
        max_counted_commands=8,
    ),
    q(
        "git-merge/continue-advanced",
        "fs-apply-seal-staged-resolution",
        "Confirm the state, then finish the merge",
        "The resolution is staged and waiting. Confirm the workspace state, continue the merge to create the merge commit, then read the history to prove the join landed.",
        "Verify the staged resolution, continue the merge, then confirm the merge commit.",
        build_drill_variants(
            "fs-apply-seal-staged-resolution",
            _resolved_merge,
            [STATUS_COMMAND, "git merge --continue", GRAPH_COMMAND],
            build_requirement_evaluation(
                {"working_tree_clean": True, "staging_empty": True},
                ["git status", "git merge --continue", "git log"],
                rules=[{"type": "commit_count_equals", "count": 4}],
            ),
        ),
        checks=[
            {
                "label": "The merge commit completed the resolution.",
                "requirement": {"rules": [{"type": "commit_count_equals", "count": 4}]},
            },
            required_command_check("The resulting history was verified.", ["git log"]),
        ],
        command_forms=CORE_FORM_TAGS,
        adventure="frost-survive-the-conflict-workflows",
        workflow=True,
        max_counted_commands=8,
    ),
    q(
        "git-merge/continue-advanced",
        "fs-apply-full-resolution",
        "Resolve, stage, and finish",
        "Run the complete resolution: take our side of src/relay.conf, stage the resolved file, and continue the merge so the join enters history. Verify afterward.",
        "Take our side, stage the resolution, continue the merge, then verify.",
        build_drill_variants(
            "fs-apply-full-resolution",
            _conflict,
            ["git checkout --ours src/relay.conf", "git add src/relay.conf", "git merge --continue", STATUS_COMMAND, GRAPH_COMMAND],
            build_requirement_evaluation(
                {"working_tree_clean": True, "staging_empty": True},
                ["git checkout --ours", "git add", "git merge --continue", "git status", "git log"],
                rules=[{"type": "commit_count_equals", "count": 4}],
            ),
        ),
        checks=[
            required_command_check("The conflict was resolved and staged.", ["git checkout --ours", "git add"]),
            {
                "label": "The merge commit completed the resolution.",
                "requirement": {"rules": [{"type": "commit_count_equals", "count": 4}]},
            },
        ],
        details=["src/relay.conf"],
        command_forms=["git-checkout-conflict/ours-advanced", "git-add/file", *CORE_FORM_TAGS],
        adventure="frost-survive-the-conflict-workflows",
        workflow=True,
        max_counted_commands=8,
    ),
    q(
        "git-merge/abort-advanced",
        "fs-apply-stand-down",
        "Start resolving, then stand down",
        "Read the unmerged entries and provisionally take their side — then the integration is called off entirely. Abort the merge and confirm the workspace returned to its pre-merge state.",
        "Inspect the stages, take their side, then abort the merge and verify.",
        build_drill_variants(
            "fs-apply-stand-down",
            _conflict,
            ["git ls-files -u", "git checkout --theirs src/relay.conf", "git merge --abort", STATUS_COMMAND, GRAPH_COMMAND],
            build_requirement_evaluation(
                {"working_tree_clean": True},
                ["git ls-files -u", "git checkout --theirs", "git merge --abort", "git status", "git log"],
            ),
        ),
        checks=[
            required_command_check("The conflict evidence was read first.", ["git ls-files -u"]),
            {
                "label": "The workspace returned to its pre-merge state.",
                "requirement": {"working_tree_clean": True},
            },
        ],
        command_forms=["git-ls-files/unmerged-advanced", "git-checkout-conflict/theirs-advanced", *CORE_FORM_TAGS],
        adventure="frost-survive-the-conflict-workflows",
        workflow=True,
        max_counted_commands=8,
    ),
    q(
        "git-diff-conflict/base-advanced",
        "fs-apply-triangulate-base",
        "Read the conflict from base and their side",
        "Before deciding, read the conflict from two angles: how it differs from the common ancestor, and how it differs from the other team's version. Nothing may change yet.",
        "Read the base and their-side comparisons for the conflicted file.",
        build_drill_variants(
            "fs-apply-triangulate-base",
            _conflict,
            ["git diff --base src/relay.conf", "git diff --theirs src/relay.conf", STATUS_COMMAND, GRAPH_COMMAND],
            build_read_evaluation(["git diff --base", "git diff --theirs", "git status", "git log"], count=3),
        ),
        checks=[
            required_command_check(
                "The conflict was read from base and their side.",
                ["git diff --base", "git diff --theirs"],
            ),
        ],
        details=["src/relay.conf"],
        command_forms=["git-diff-conflict/theirs-advanced", *CORE_FORM_TAGS],
        adventure="frost-survive-the-conflict-workflows",
        workflow=True,
        max_counted_commands=8,
    ),
    q(
        "git-diff-conflict/ours-advanced",
        "fs-apply-compare-both-sides",
        "Weigh both sides of the conflict",
        "Weigh your team's raised load setting against the other team's strict mode by reading both comparisons back to back. Nothing may change until the decision is recorded.",
        "Read the our-side and their-side comparisons for the conflicted file.",
        build_drill_variants(
            "fs-apply-compare-both-sides",
            _conflict,
            ["git diff --ours src/relay.conf", "git diff --theirs src/relay.conf", STATUS_COMMAND, GRAPH_COMMAND],
            build_read_evaluation(["git diff --ours", "git diff --theirs", "git status", "git log"], count=3),
        ),
        checks=[
            required_command_check(
                "Both sides of the conflict were weighed.",
                ["git diff --ours", "git diff --theirs"],
            ),
        ],
        details=["src/relay.conf"],
        command_forms=["git-diff-conflict/theirs-advanced", *CORE_FORM_TAGS],
        adventure="frost-survive-the-conflict-workflows",
        workflow=True,
        max_counted_commands=8,
    ),
]

