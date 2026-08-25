"""Frostbound Citadel Chapter 2: Choose the Integration form drills."""

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


DRILLS = [
    q(
        "git-rev-list/revision-set",
        "fc-intro-rev-list-count",
        "Count the commits in a range",
        "Two teams disagree about how far main has moved since the project's first commit. Settle it with a number: count the commits reachable from main but not from the first commit (its id is in Copy details).",
        "Count the commits in the range between the first commit and main.",
        build_drill_variants(
            "fc-intro-rev-list-count",
            build_broken_form_state,
            ["git rev-list --count {p}0..main"],
            build_read_evaluation(["git rev-list --count {p}0..main"]),
            details=["{p}0..main"],
        ),
        checks=[required_command_check("The commit range was counted before integrating.", ["git rev-list --count"])],
        adventure="frost-choose-the-integration-drills",
    ),
    q(
        "git-diff/three-dot",
        "fc-intro-three-dot",
        "Compare a branch from where it started",
        "A review must see the feature/work branch the way its author wrote it: compared against the point where it split from main, not against today's main. Use the three-dot comparison between main and feature/work.",
        "Compare feature/work against main starting from their common ancestor.",
        build_drill_variants(
            "fc-intro-three-dot",
            build_clean_form_state,
            ["git diff main...feature/work"],
            build_read_evaluation(["git diff main...feature/work"]),
        ),
        checks=[required_command_check("The branch was compared from its starting point.", ["git diff main...feature/work"])],
        details=["main...feature/work"],
        adventure="frost-choose-the-integration-drills",
    ),
    q(
        "git-merge/no-ff-advanced",
        "fc-intro-merge-no-ff",
        "Merge with a visible merge commit",
        "Team policy says every integration must stay visible in history. Merge the branch feature/work into main so an explicit merge commit records the join, even though a fast-forward would be possible.",
        "Merge feature/work into main with an explicit merge commit.",
        build_drill_variants(
            "fc-intro-merge-no-ff",
            build_clean_form_state,
            ["git merge --no-ff feature/work"],
            build_requirement_evaluation({}, ["git merge --no-ff"], rules=[{"type": "commit_count_equals", "count": 6}]),
        ),
        checks=[
            {
                "label": "An explicit merge commit records the integration.",
                "requirement": {"rules": [{"type": "commit_count_equals", "count": 6}]},
            }
        ],
        details=["feature/work"],
        adventure="frost-choose-the-integration-drills",
        workflow=True,
    ),
    q(
        "git-merge/squash-advanced",
        "fc-intro-merge-squash",
        "Squash a branch into one staged change",
        "The feature/work branch is full of noisy work-in-progress commits, and only its end result should enter review. Squash the branch into a single staged change without committing yet.",
        "Squash-merge feature/work so its combined change is staged, ready for one commit.",
        build_drill_variants(
            "fc-intro-merge-squash",
            build_clean_form_state,
            ["git merge --squash feature/work"],
            build_requirement_evaluation({}, ["git merge --squash"], rules=[{"type": "staging_not_empty"}]),
        ),
        checks=[
            {
                "label": "The combined change is staged as one unit.",
                "requirement": {"rules": [{"type": "staging_not_empty"}]},
            }
        ],
        details=["feature/work"],
        adventure="frost-choose-the-integration-drills",
        workflow=True,
    ),
]

WORKFLOWS = [
    q(
        "git-merge/no-ff-advanced",
        "fc-apply-reviewed-join",
        "Review the branch, then merge visibly",
        "Before feature/work is admitted into main, read its changes from where it branched off, then merge it with an explicit merge commit and confirm the join in the history.",
        "Compare from the branch point, merge with an explicit merge commit, then verify.",
        build_drill_variants(
            "fc-apply-reviewed-join",
            build_clean_form_state,
            ["git diff main...feature/work", "git merge --no-ff feature/work", STATUS_COMMAND, GRAPH_COMMAND],
            build_requirement_evaluation(
                {},
                ["git diff main...feature/work", "git merge --no-ff", "git status", "git log"],
                rules=[{"type": "commit_count_equals", "count": 6}],
            ),
        ),
        checks=[
            required_command_check("The branch was reviewed from its starting point.", ["git diff main...feature/work"]),
            {
                "label": "An explicit merge commit records the join.",
                "requirement": {"rules": [{"type": "commit_count_equals", "count": 6}]},
            },
            required_command_check("The resulting history was verified.", ["git log"]),
        ],
        details=["feature/work"],
        command_forms=["git-diff/three-dot", *CORE_FORM_TAGS],
        adventure="frost-choose-the-integration-workflows",
        workflow=True,
        max_counted_commands=8,
    ),
    q(
        "git-merge/no-ff-advanced",
        "fc-apply-counted-join",
        "Count the range, then merge visibly",
        "The reviewer wants numbers first: count how many commits main holds beyond the first commit (see Copy details), then merge feature/work with a visible merge commit and verify.",
        "Count the range, merge with an explicit merge commit, then verify the history.",
        build_drill_variants(
            "fc-apply-counted-join",
            build_clean_form_state,
            ["git rev-list --count {p}0..main", "git merge --no-ff feature/work", STATUS_COMMAND, GRAPH_COMMAND],
            build_requirement_evaluation(
                {},
                ["git rev-list --count", "git merge --no-ff", "git status", "git log"],
                rules=[{"type": "commit_count_equals", "count": 6}],
            ),
            details=["{p}0..main", "feature/work"],
        ),
        checks=[
            required_command_check("The commit range was counted first.", ["git rev-list --count"]),
            {
                "label": "An explicit merge commit records the join.",
                "requirement": {"rules": [{"type": "commit_count_equals", "count": 6}]},
            },
        ],
        command_forms=["git-rev-list/revision-set", *CORE_FORM_TAGS],
        adventure="frost-choose-the-integration-workflows",
        workflow=True,
        max_counted_commands=8,
    ),
    q(
        "git-merge/squash-advanced",
        "fc-apply-reviewed-squash",
        "Review, then squash to one change",
        "The team wants feature/work's result without its noisy commit history. Read the three-dot comparison first, then squash the branch into one staged change and check what is pending.",
        "Compare from the branch point, squash the branch, then verify the staged result.",
        build_drill_variants(
            "fc-apply-reviewed-squash",
            build_clean_form_state,
            ["git diff main...feature/work", "git merge --squash feature/work", STATUS_COMMAND, GRAPH_COMMAND],
            build_requirement_evaluation(
                {},
                ["git diff main...feature/work", "git merge --squash", "git status", "git log"],
                rules=[{"type": "staging_not_empty"}],
            ),
        ),
        checks=[
            required_command_check("The branch was reviewed from its starting point.", ["git diff main...feature/work"]),
            {
                "label": "The combined change is staged as one unit.",
                "requirement": {"rules": [{"type": "staging_not_empty"}]},
            },
        ],
        details=["feature/work"],
        command_forms=["git-diff/three-dot", *CORE_FORM_TAGS],
        adventure="frost-choose-the-integration-workflows",
        workflow=True,
        max_counted_commands=8,
    ),
    q(
        "git-merge/squash-advanced",
        "fc-apply-counted-squash",
        "Count, then squash deliberately",
        "Numbers first, shape second: count the commits main holds beyond the first commit (see Copy details), then stage feature/work's entire result as one squashed change and check the pending state.",
        "Count the range, squash feature/work, then verify the staged result.",
        build_drill_variants(
            "fc-apply-counted-squash",
            build_clean_form_state,
            ["git rev-list --count {p}0..main", "git merge --squash feature/work", STATUS_COMMAND, GRAPH_COMMAND],
            build_requirement_evaluation(
                {},
                ["git rev-list --count", "git merge --squash", "git status", "git log"],
                rules=[{"type": "staging_not_empty"}],
            ),
            details=["{p}0..main", "feature/work"],
        ),
        checks=[
            required_command_check("The commit range was counted first.", ["git rev-list --count"]),
            {
                "label": "The combined change is staged as one unit.",
                "requirement": {"rules": [{"type": "staging_not_empty"}]},
            },
        ],
        command_forms=["git-rev-list/revision-set", *CORE_FORM_TAGS],
        adventure="frost-choose-the-integration-workflows",
        workflow=True,
        max_counted_commands=8,
    ),
]

