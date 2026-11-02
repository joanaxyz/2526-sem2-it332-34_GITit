"""Human-authored command-to-adventure routing.

This is one of the first small pieces moved out of the monolithic seed modules:
it is hand-authored curriculum structure, not generated target output.
"""

ADVENTURE_BY_COMMAND = {
    # One adventure per chapter (1:1): the adventure is just the chapter's run +
    # mastery carrier; learners see a flat list of levels. Ch1 reauthor pulls the
    # commit loop + reading + identity into Chapter 1 so a learner can actually use
    # Git by its end - all under the single "repository-foundations" adventure.
    "git-init": "repository-foundations",
    "git-clone": "repository-foundations",
    "git-status": "repository-foundations",
    "git-config": "repository-foundations",
    "git-log": "repository-foundations",
    "git-show": "repository-foundations",
    "git-diff": "stage-with-intent",
    "git-add": "stage-with-intent",
    "git-commit": "seal-the-snapshot",
    "git-rm": "untrack-and-undo-edits",
    "git-restore": "untrack-and-undo-edits",
    "git-check-ignore": "repository-foundations",
    "git-switch": "create-and-move",
    "git-branch": "create-and-move",
    "git-checkout": "create-and-move",
    "git-merge": "integrate-branches",
    "git-merge-base": "integrate-branches",
    "git-checkout-conflict": "resolve-conflicts",
    "git-diff-conflict": "resolve-conflicts",
    "git-ls-files": "resolve-conflicts",
    "git-mergetool": "manage-the-merge",
    "git-reset": "step-back-safely",
    "git-revert": "reverse-and-recover",
    "git-reflog": "reverse-and-recover",
    "git-stash": "shelve-work",
    "git-cherry-pick": "transplant-commits",
    "git-remote": "connect-and-inspect",
    "git-fetch": "connect-and-inspect",
    "git-pull": "integrate-upstream",
    "git-push": "publish-work",
}

ADVENTURE_BY_USAGE = {
    "git-switch/detach": "detach-and-clean",
    "git-branch/delete": "detach-and-clean",
    "git-branch/delete-force": "detach-and-clean",
    "git-branch/verbose": "detach-and-clean",
    "git-merge/abort": "manage-the-merge",
    "git-merge/continue": "manage-the-merge",
    # Ch1 reauthor: these specific usages move into Chapter 1 (the core save loop
    # and reading work) even though add/commit/diff also appear in Chapter 2.
    "git-add/file": "repository-foundations",
    "git-add/dot": "repository-foundations",
    "git-commit/message": "repository-foundations",
    "git-diff/working": "repository-foundations",
    "git-diff/staged": "repository-foundations",
}


def adventure_for_usage(usage: str) -> str:
    if usage in ADVENTURE_BY_USAGE:
        return ADVENTURE_BY_USAGE[usage]
    return ADVENTURE_BY_COMMAND.get(usage.split("/", 1)[0], "found-a-repository")
