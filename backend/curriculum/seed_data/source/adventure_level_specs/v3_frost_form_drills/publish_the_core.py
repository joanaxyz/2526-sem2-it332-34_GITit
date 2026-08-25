"""Frostbound Citadel Chapter 9: Publish the Core form drills."""

from __future__ import annotations

from ..common import q
from ..form_drill_support import (
    CORE_FORM_TAGS,
    GRAPH_COMMAND,
    STATUS_COMMAND,
    build_clean_form_state,
    build_drill_variants,
    build_read_evaluation,
    required_command_check,
)


DRILLS = [
    q(
        "git-verify-tag/tag",
        "fp-intro-verify-tag",
        "Verify a release tag's signature",
        "Before the restored release ships, the v1.0 tag's signature must be checked against the trusted release keys. Verify the tag v1.0.",
        "Verify the release tag's signature.",
        build_drill_variants("fp-intro-verify-tag", build_clean_form_state, ["git verify-tag v1.0"], build_read_evaluation(["git verify-tag v1.0"])),
        checks=[required_command_check("The release signature was verified.", ["git verify-tag"])],
        details=["v1.0"],
        adventure="frost-publish-the-core-drills",
    ),
    q(
        "git-show-ref/all",
        "fp-intro-show-ref",
        "List every ref and its target",
        "The final handoff has to list every ref this repository exposes. Read the complete ref list with the commit each ref points to.",
        "List every ref and the object it points to.",
        build_drill_variants("fp-intro-show-ref", build_clean_form_state, ["git show-ref"], build_read_evaluation(["git show-ref"])),
        checks=[required_command_check("The complete ref list was read.", ["git show-ref"])],
        adventure="frost-publish-the-core-drills",
    ),
]

WORKFLOWS = [
    q(
        "git-show-ref/all",
        "fp-apply-verify-then-audit",
        "Verify the tag, then list the refs",
        "Verify the release tag v1.0's signature, then read the complete ref list so the publication can be signed off.",
        "Verify the tag, list the refs, then verify the state.",
        build_drill_variants(
            "fp-apply-verify-then-audit",
            build_clean_form_state,
            ["git verify-tag v1.0", "git show-ref", STATUS_COMMAND, GRAPH_COMMAND],
            build_read_evaluation(["git verify-tag", "git show-ref", "git status", "git log"]),
        ),
        checks=[
            required_command_check("The release signature was verified first.", ["git verify-tag"]),
            required_command_check("The complete ref list was read.", ["git show-ref"]),
        ],
        details=["v1.0"],
        command_forms=["git-verify-tag/tag", *CORE_FORM_TAGS],
        adventure="frost-publish-the-core-workflows",
        workflow=True,
        max_counted_commands=8,
    ),
    q(
        "git-show-ref/all",
        "fp-apply-audit-then-verify",
        "List the refs, then prove the tag",
        "Read the ref list to see what the repository exposes, then prove the release tag v1.0's signature before anyone trusts it.",
        "List the refs, verify the tag, then verify the state.",
        build_drill_variants(
            "fp-apply-audit-then-verify",
            build_clean_form_state,
            ["git show-ref", "git verify-tag v1.0", STATUS_COMMAND, GRAPH_COMMAND],
            build_read_evaluation(["git show-ref", "git verify-tag", "git status", "git log"]),
        ),
        checks=[
            required_command_check("The ref list was read first.", ["git show-ref"]),
            required_command_check("The release signature was proven.", ["git verify-tag"]),
        ],
        details=["v1.0"],
        command_forms=["git-verify-tag/tag", *CORE_FORM_TAGS],
        adventure="frost-publish-the-core-workflows",
        workflow=True,
        max_counted_commands=8,
    ),
]

