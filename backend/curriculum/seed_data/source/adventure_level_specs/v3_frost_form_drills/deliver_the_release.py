"""Frostbound Citadel Chapter 7: Deliver the Release form drills."""

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
    _meta,
    _meta_set,
)


DRILLS = [
    q(
        "git-shortlog/summary",
        "fd-intro-shortlog",
        "Summarize commits by author",
        "The release record must say who did the work. Produce the commit summary grouped by author.",
        "Summarize the commit history grouped by author.",
        build_drill_variants("fd-intro-shortlog", build_clean_form_state, ["git shortlog"], build_read_evaluation(["git shortlog"])),
        checks=[required_command_check("Contributors were summarized for the record.", ["git shortlog"])],
        adventure="frost-deliver-the-release-drills",
    ),
    q(
        "git-shortlog/numbered",
        "fd-intro-shortlog-numbered",
        "Count commits per author",
        "The release board wants numbers, not prose: produce the per-author commit counts, sorted by how many commits each person made.",
        "Produce numbered, sorted per-author commit counts.",
        build_drill_variants("fd-intro-shortlog-numbered", build_clean_form_state, ["git shortlog -sn"], build_read_evaluation(["git shortlog -sn"])),
        checks=[required_command_check("Per-author commit counts were produced.", ["git shortlog -sn"])],
        adventure="frost-deliver-the-release-drills",
    ),
    q(
        "git-describe/tags",
        "fd-intro-describe",
        "Name the current commit from its tags",
        "Every build that ships needs a human-readable name derived from the nearest release tag. Produce that name for the current commit.",
        "Describe HEAD relative to the nearest reachable tag.",
        build_drill_variants("fd-intro-describe", build_clean_form_state, ["git describe --tags"], build_read_evaluation(["git describe --tags"])),
        checks=[required_command_check("The commit was named from its tags.", ["git describe --tags"])],
        adventure="frost-deliver-the-release-drills",
    ),
    q(
        "git-tag/annotated-advanced",
        "fd-intro-tag-annotated",
        "Create an annotated release tag",
        "The reviewed commit becomes a release candidate today. Create an annotated tag named v1.1 with the message 'Heat core release candidate' so the release has a durable name and description.",
        "Create the annotated tag v1.1 with the message 'Heat core release candidate'.",
        build_drill_variants(
            "fd-intro-tag-annotated",
            build_clean_form_state,
            ["git tag -a v1.1 -m 'Heat core release candidate'"],
            build_requirement_evaluation({}, ["git tag -a"], rules=[_meta("last_tag_created", "v1.1")]),
        ),
        checks=[
            {
                "label": "The annotated release tag exists.",
                "requirement": {"rules": [_meta("last_tag_created", "v1.1")]},
            }
        ],
        details=["v1.1", "Heat core release candidate"],
        adventure="frost-deliver-the-release-drills",
        workflow=True,
    ),
    q(
        "git-tag/delete-advanced",
        "fd-intro-tag-delete",
        "Delete an outdated tag",
        "The old v1.0 tag now points at superseded work and keeps confusing people. Delete the local tag v1.0.",
        "Delete the outdated local tag v1.0.",
        build_drill_variants(
            "fd-intro-tag-delete",
            build_clean_form_state,
            ["git tag -d v1.0"],
            build_requirement_evaluation({}, ["git tag -d"], rules=[_meta_set("last_tags_deleted")]),
        ),
        checks=[
            {
                "label": "The outdated tag is gone.",
                "requirement": {"rules": [_meta_set("last_tags_deleted")]},
            }
        ],
        details=["v1.0"],
        adventure="frost-deliver-the-release-drills",
        workflow=True,
    ),
    q(
        "git-push/all-tags",
        "fd-intro-push-tags",
        "Publish all tags",
        "Downstream consumers synchronize on tags, not branches. Push every local tag to origin so the release markers are visible everywhere.",
        "Push all local tags to the origin remote.",
        build_drill_variants(
            "fd-intro-push-tags",
            build_clean_form_state,
            ["git push --tags"],
            build_requirement_evaluation({}, ["git push --tags"], rules=[_meta("last_push_tags", True)]),
        ),
        checks=[
            {
                "label": "The tags were published.",
                "requirement": {"rules": [_meta("last_push_tags", True)]},
            }
        ],
        adventure="frost-deliver-the-release-drills",
        workflow=True,
    ),
]

WORKFLOWS = [
    q(
        "git-tag/annotated-advanced",
        "fd-apply-name-then-mark",
        "Check the current name, then tag",
        "Find the commit's current tag-derived name, then create the annotated tag v1.1 with the message 'Signed relay candidate' and verify the new marker.",
        "Describe the tip, create the annotated tag v1.1, then verify.",
        build_drill_variants(
            "fd-apply-name-then-mark",
            build_clean_form_state,
            ["git describe --tags", "git tag -a v1.1 -m 'Signed relay candidate'", STATUS_COMMAND, GRAPH_COMMAND],
            build_requirement_evaluation(
                {},
                ["git describe --tags", "git tag -a", "git status", "git log"],
                rules=[_meta("last_tag_created", "v1.1")],
            ),
        ),
        checks=[
            required_command_check("The current tag-derived name was checked first.", ["git describe --tags"]),
            {
                "label": "The annotated release tag exists.",
                "requirement": {"rules": [_meta("last_tag_created", "v1.1")]},
            },
        ],
        details=["v1.1", "Signed relay candidate"],
        command_forms=["git-describe/tags", *CORE_FORM_TAGS],
        adventure="frost-deliver-the-release-workflows",
        workflow=True,
        max_counted_commands=8,
    ),
    q(
        "git-push/all-tags",
        "fd-apply-mark-then-broadcast",
        "Tag the hotfix, then publish the tags",
        "Create the annotated tag v1.2 with the message 'Relay hotfix marker', then push all tags so every consumer picks the new marker up together. Verify afterward.",
        "Create the annotated tag v1.2, push all tags, then verify.",
        build_drill_variants(
            "fd-apply-mark-then-broadcast",
            build_clean_form_state,
            ["git tag -a v1.2 -m 'Relay hotfix marker'", "git push --tags", STATUS_COMMAND, GRAPH_COMMAND],
            build_requirement_evaluation(
                {},
                ["git tag -a", "git push --tags", "git status", "git log"],
                rules=[_meta("last_push_tags", True)],
            ),
        ),
        checks=[
            {
                "label": "The hotfix tag exists.",
                "requirement": {"rules": [_meta("last_tag_created", "v1.2")]},
            },
            {
                "label": "The tags were published.",
                "requirement": {"rules": [_meta("last_push_tags", True)]},
            },
        ],
        details=["v1.2", "Relay hotfix marker"],
        command_forms=["git-tag/annotated-advanced", *CORE_FORM_TAGS],
        adventure="frost-deliver-the-release-workflows",
        workflow=True,
        max_counted_commands=8,
    ),
    q(
        "git-tag/delete-advanced",
        "fd-apply-credit-then-retire",
        "Credit the authors, then delete the tag",
        "Produce the author summary for the release record, then delete the superseded tag v1.0 and check the remaining state.",
        "Summarize authors, delete the tag v1.0, then verify.",
        build_drill_variants(
            "fd-apply-credit-then-retire",
            build_clean_form_state,
            ["git shortlog", "git tag -d v1.0", STATUS_COMMAND, GRAPH_COMMAND],
            build_requirement_evaluation(
                {},
                ["git shortlog", "git tag -d", "git status", "git log"],
                rules=[_meta_set("last_tags_deleted")],
            ),
        ),
        checks=[
            required_command_check("Authors were credited first.", ["git shortlog"]),
            {
                "label": "The superseded tag is gone.",
                "requirement": {"rules": [_meta_set("last_tags_deleted")]},
            },
        ],
        details=["v1.0"],
        command_forms=["git-shortlog/summary", *CORE_FORM_TAGS],
        adventure="frost-deliver-the-release-workflows",
        workflow=True,
        max_counted_commands=8,
    ),
    q(
        "git-tag/delete-advanced",
        "fd-apply-rename-the-marker",
        "Check the name, then delete the stale tag",
        "The v1.0 tag must give way to a corrected one. Check the tip's tag-derived name, delete the stale tag v1.0, and confirm the removal registered.",
        "Describe the tip, delete the tag v1.0, then verify.",
        build_drill_variants(
            "fd-apply-rename-the-marker",
            build_clean_form_state,
            ["git describe --tags", "git tag -d v1.0", STATUS_COMMAND, GRAPH_COMMAND],
            build_requirement_evaluation(
                {},
                ["git describe --tags", "git tag -d", "git status", "git log"],
                rules=[_meta_set("last_tags_deleted")],
            ),
        ),
        checks=[
            required_command_check("The tip's name was checked before deleting.", ["git describe --tags"]),
            {
                "label": "The stale tag is gone.",
                "requirement": {"rules": [_meta_set("last_tags_deleted")]},
            },
        ],
        details=["v1.0"],
        command_forms=["git-describe/tags", *CORE_FORM_TAGS],
        adventure="frost-deliver-the-release-workflows",
        workflow=True,
        max_counted_commands=8,
    ),
    q(
        "git-push/all-tags",
        "fd-apply-credit-then-broadcast",
        "Count contributions, then publish the tags",
        "Produce the per-author commit counts for the release record, then push all tags to origin and confirm the publication registered.",
        "Count contributions, push all tags, then verify.",
        build_drill_variants(
            "fd-apply-credit-then-broadcast",
            build_clean_form_state,
            ["git shortlog -sn", "git push --tags", STATUS_COMMAND, GRAPH_COMMAND],
            build_requirement_evaluation(
                {},
                ["git shortlog -sn", "git push --tags", "git status", "git log"],
                rules=[_meta("last_push_tags", True)],
            ),
        ),
        checks=[
            required_command_check("Contribution counts were produced first.", ["git shortlog -sn"]),
            {
                "label": "The tags were published.",
                "requirement": {"rules": [_meta("last_push_tags", True)]},
            },
        ],
        command_forms=["git-shortlog/numbered", *CORE_FORM_TAGS],
        adventure="frost-deliver-the-release-workflows",
        workflow=True,
        max_counted_commands=8,
    ),
    q(
        "git-shortlog/summary",
        "fd-apply-release-ledger",
        "Assemble the release record",
        "The release record pairs the author summary with the build's tag-derived name. Produce both reads back to back; nothing in the repository may change.",
        "Summarize authors and describe the tip for the record.",
        build_drill_variants(
            "fd-apply-release-ledger",
            build_clean_form_state,
            ["git shortlog", "git describe --tags", STATUS_COMMAND, GRAPH_COMMAND],
            build_read_evaluation(["git shortlog", "git describe --tags", "git status", "git log"]),
        ),
        checks=[
            required_command_check("Both record reads were produced.", ["git shortlog", "git describe --tags"]),
        ],
        command_forms=["git-describe/tags", *CORE_FORM_TAGS],
        adventure="frost-deliver-the-release-workflows",
        workflow=True,
        max_counted_commands=8,
    ),
]

