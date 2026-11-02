"""Frostbound Citadel Chapter 5: Reforge the Branch form drills."""

from __future__ import annotations

from ..common import q
from ..form_drill_support import (
    CORE_FORM_TAGS,
    GRAPH_COMMAND,
    STATUS_COMMAND,
    build_drill_variants,
    build_requirement_evaluation,
    required_command_check,
)
from ._fixtures import (
    _meta,
    _rebase_paused,
    _rebase_ready,
)


DRILLS = [
    q(
        "git-rebase/branch",
        "fr-intro-rebase",
        "Rebase the branch onto today's main",
        "The branch feature/work was started from an old commit, and main has moved on since. You are on feature/work: replay its commits onto today's main so review sees one straight line of history.",
        "Rebase the current branch feature/work onto main.",
        build_drill_variants(
            "fr-intro-rebase",
            _rebase_ready,
            ["git rebase main"],
            build_requirement_evaluation({}, ["git rebase"], rules=[_meta("last_rebase_target", "main")]),
        ),
        checks=[
            {
                "label": "The branch was replayed onto today's main.",
                "requirement": {"rules": [_meta("last_rebase_target", "main")]},
            }
        ],
        details=["feature/work", "main"],
        adventure="frost-reforge-the-branch-drills",
        workflow=True,
    ),
    q(
        "git-rebase/abort",
        "fr-intro-rebase-abort",
        "Abort a rebase that went wrong",
        "A rebase stopped midway and the team no longer trusts the plan. Abort it and put the branch back exactly where it was before the rebase started.",
        "Abort the in-progress rebase safely.",
        build_drill_variants(
            "fr-intro-rebase-abort",
            _rebase_paused,
            ["git rebase --abort"],
            build_requirement_evaluation({}, ["git rebase --abort"], rules=[_meta("last_rebase_aborted", True)]),
        ),
        checks=[
            {
                "label": "The branch returned to its pre-rebase state.",
                "requirement": {"rules": [_meta("last_rebase_aborted", True)]},
            }
        ],
        adventure="frost-reforge-the-branch-drills",
        workflow=True,
    ),
]

WORKFLOWS = [
    q(
        "git-rebase/branch",
        "fr-apply-rebase-and-compare",
        "Rebase, then prove nothing was lost",
        "Replay feature/work onto main, then compare the earlier candidate series against the rewritten branch (the ranges are in Copy details) to prove the patches kept their meaning.",
        "Rebase onto main, compare the patch series, then verify the history.",
        build_drill_variants(
            "fr-apply-rebase-and-compare",
            _rebase_ready,
            ["git rebase main", "git range-diff {p}0..old/series {p}0..feature/work", STATUS_COMMAND, GRAPH_COMMAND],
            build_requirement_evaluation(
                {},
                ["git rebase", "git range-diff", "git status", "git log"],
                rules=[_meta("last_rebase_target", "main")],
            ),
            details=["{p}0..old/series", "{p}0..feature/work"],
        ),
        checks=[
            {
                "label": "The branch was replayed onto today's main.",
                "requirement": {"rules": [_meta("last_rebase_target", "main")]},
            },
            required_command_check("The rewrite was checked with a series comparison.", ["git range-diff"]),
        ],
        command_forms=["git-range-diff/series", *CORE_FORM_TAGS],
        adventure="frost-reforge-the-branch-workflows",
        workflow=True,
        max_counted_commands=8,
    ),
    q(
        "git-rebase/branch",
        "fr-apply-survey-then-rebase",
        "Read the history, then rebase",
        "Read the commit graph before touching anything, replay feature/work onto main, then read the graph again so the before and after can be compared.",
        "Read the graph, rebase onto main, then verify the new shape.",
        build_drill_variants(
            "fr-apply-survey-then-rebase",
            _rebase_ready,
            [GRAPH_COMMAND, "git rebase main", STATUS_COMMAND, GRAPH_COMMAND],
            build_requirement_evaluation(
                {},
                ["git log", "git rebase", "git status"],
                rules=[
                    _meta("last_rebase_target", "main"),
                    {
                        "type": "required_command_sequence",
                        "commands": ["git status", "git log"],
                    },
                ],
            ),
        ),
        checks=[
            {
                "label": "The branch was replayed onto today's main.",
                "requirement": {"rules": [_meta("last_rebase_target", "main")]},
            },
            {
                "label": "The new shape was verified after the rebase.",
                "requirement": {
                    "required_commands": ["git status", "git log"],
                    "rules": [
                        {
                            "type": "required_command_sequence",
                            "commands": ["git status", "git log"],
                        }
                    ],
                },
            },
        ],
        details=["main"],
        command_forms=CORE_FORM_TAGS,
        adventure="frost-reforge-the-branch-workflows",
        workflow=True,
        max_counted_commands=8,
    ),
    q(
        "git-rebase/abort",
        "fr-apply-compare-then-abort",
        "Compare the series, then call it off",
        "In the middle of the rebase, compare the old candidate series against the current branch (ranges in Copy details). The comparison shows the rewrite is drifting, so abort it and confirm the branch returned to its pre-rebase state.",
        "Compare the series, abort the rebase, then verify the state.",
        build_drill_variants(
            "fr-apply-compare-then-abort",
            _rebase_paused,
            ["git range-diff {p}0..old/series {p}0..feature/work", "git rebase --abort", STATUS_COMMAND, GRAPH_COMMAND],
            build_requirement_evaluation(
                {},
                ["git range-diff", "git rebase --abort", "git status", "git log"],
                rules=[_meta("last_rebase_aborted", True)],
            ),
            details=["{p}0..old/series", "{p}0..feature/work"],
        ),
        checks=[
            required_command_check("The drift was measured before deciding.", ["git range-diff"]),
            {
                "label": "The branch returned to its pre-rebase state.",
                "requirement": {"rules": [_meta("last_rebase_aborted", True)]},
            },
        ],
        command_forms=["git-range-diff/series", *CORE_FORM_TAGS],
        adventure="frost-reforge-the-branch-workflows",
        workflow=True,
        max_counted_commands=8,
    ),
    q(
        "git-rebase/abort",
        "fr-apply-stand-down-rewrite",
        "Abort the rebase and report",
        "The rewrite window was cancelled. Abort the paused rebase immediately, then check the workspace and history so the rollback can be reported.",
        "Abort the rebase, then verify the workspace and history.",
        build_drill_variants(
            "fr-apply-stand-down-rewrite",
            _rebase_paused,
            ["git rebase --abort", STATUS_COMMAND, GRAPH_COMMAND],
            build_requirement_evaluation(
                {},
                ["git rebase --abort", "git status", "git log"],
                rules=[_meta("last_rebase_aborted", True)],
            ),
        ),
        checks=[
            {
                "label": "The branch returned to its pre-rebase state.",
                "requirement": {"rules": [_meta("last_rebase_aborted", True)]},
            },
            required_command_check("The rollback was verified.", ["git status", "git log"]),
        ],
        command_forms=CORE_FORM_TAGS,
        adventure="frost-reforge-the-branch-workflows",
        workflow=True,
        max_counted_commands=8,
    ),
]

