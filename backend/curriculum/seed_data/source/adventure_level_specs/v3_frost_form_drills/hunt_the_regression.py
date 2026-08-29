"""Frostbound Citadel Chapter 8: Hunt the Regression form drills."""

from __future__ import annotations

from ..common import q
from ..form_drill_support import (
    CORE_FORM_TAGS,
    GRAPH_COMMAND,
    STATUS_COMMAND,
    build_broken_form_state,
    build_drill_variants,
    build_read_evaluation,
    required_command_check,
)


DRILLS = [
    q(
        "git-bisect/run",
        "fh-intro-bisect-run",
        "Find the bad commit automatically",
        "Something between the known-good first commit and today's tip broke the deployment. Run the project's test script heat-relay-test under bisect so the first bad commit is found automatically.",
        "Run the test script under an automated bisect session.",
        build_drill_variants(
            "fh-intro-bisect-run",
            build_broken_form_state,
            ["git bisect run heat-relay-test"],
            build_read_evaluation(["git bisect run heat-relay-test"]),
        ),
        checks=[required_command_check("The regression search was automated.", ["git bisect run"])],
        details=["heat-relay-test"],
        adventure="frost-hunt-the-regression-drills",
    ),
    q(
        "git-bisect/log",
        "fh-intro-bisect-log",
        "Read the bisect record",
        "A bisect verdict nobody can audit is worthless. Read the bisect session's log so the search can be attached to the incident report.",
        "Show the bisect session's log.",
        build_drill_variants("fh-intro-bisect-log", build_broken_form_state, ["git bisect log"], build_read_evaluation(["git bisect log"])),
        checks=[required_command_check("The search record was read.", ["git bisect log"])],
        adventure="frost-hunt-the-regression-drills",
    ),
]

WORKFLOWS = [
    q(
        "git-bisect/run",
        "fh-apply-hunt-and-record",
        "Run the search, then keep the record",
        "Run the test script heat-relay-test under bisect, then read the bisect log and the history so the verdict ships with its evidence.",
        "Run the automated bisect, read its log, then verify the history.",
        build_drill_variants(
            "fh-apply-hunt-and-record",
            build_broken_form_state,
            ["git bisect run heat-relay-test", "git bisect log", STATUS_COMMAND, GRAPH_COMMAND],
            build_read_evaluation(["git bisect run", "git bisect log", "git status", "git log"]),
        ),
        checks=[
            required_command_check("The search was automated.", ["git bisect run"]),
            required_command_check("The verdict ships with its record.", ["git bisect log"]),
        ],
        details=["heat-relay-test"],
        command_forms=["git-bisect/log", *CORE_FORM_TAGS],
        adventure="frost-hunt-the-regression-workflows",
        workflow=True,
        max_counted_commands=8,
    ),
    q(
        "git-bisect/run",
        "fh-apply-second-opinion",
        "Confirm with a second test script",
        "A second, independent test script must confirm the verdict. Run relay-freeze-test under bisect and read the record so both searches can be compared.",
        "Run the second automated bisect and read its record.",
        build_drill_variants(
            "fh-apply-second-opinion",
            build_broken_form_state,
            ["git bisect run relay-freeze-test", "git bisect log", STATUS_COMMAND, GRAPH_COMMAND],
            build_read_evaluation(["git bisect run", "git bisect log", "git status", "git log"]),
        ),
        checks=[
            required_command_check("The confirming search was automated.", ["git bisect run"]),
            required_command_check("Its record was read.", ["git bisect log"]),
        ],
        details=["relay-freeze-test"],
        command_forms=["git-bisect/log", *CORE_FORM_TAGS],
        adventure="frost-hunt-the-regression-workflows",
        workflow=True,
        max_counted_commands=8,
    ),
    q(
        "git-bisect/run",
        "fh-apply-survey-then-hunt",
        "Read the history, then run the search",
        "Read the commit graph to understand the search range, run the test script heat-relay-test under bisect, then check the state afterward.",
        "Read the graph, run the automated bisect, then verify.",
        build_drill_variants(
            "fh-apply-survey-then-hunt",
            build_broken_form_state,
            [GRAPH_COMMAND, "git bisect run heat-relay-test", STATUS_COMMAND],
            build_read_evaluation(["git log", "git bisect run", "git status"]),
        ),
        checks=[
            required_command_check("The history was read first.", ["git log"]),
            required_command_check("The search was automated.", ["git bisect run"]),
        ],
        details=["heat-relay-test"],
        command_forms=CORE_FORM_TAGS,
        adventure="frost-hunt-the-regression-workflows",
        workflow=True,
        max_counted_commands=8,
    ),
    q(
        "git-bisect/run",
        "fh-apply-audit-the-hunt",
        "Reproduce yesterday's search",
        "Re-run the automated search that produced yesterday's verdict, then read its record so the audit can compare both runs line by line.",
        "Re-run the automated bisect and read its record for the audit.",
        build_drill_variants(
            "fh-apply-audit-the-hunt",
            build_broken_form_state,
            ["git bisect run heat-relay-test", "git bisect log", GRAPH_COMMAND, STATUS_COMMAND],
            build_read_evaluation(["git bisect run", "git bisect log", "git log", "git status"]),
        ),
        checks=[
            required_command_check("The search was reproduced for the audit.", ["git bisect run"]),
            required_command_check("The audit record was read.", ["git bisect log"]),
        ],
        details=["heat-relay-test"],
        command_forms=["git-bisect/log", *CORE_FORM_TAGS],
        adventure="frost-hunt-the-regression-workflows",
        workflow=True,
        max_counted_commands=8,
    ),
]

