"""Blueprint adventure levels for transplant-commits."""

from __future__ import annotations

from .helpers import _wave

ADVENTURE_LEVELS = [
        {
            "slug": "move-one-commit",
            "title": "Move One Commit",
            "waves": [
                _wave(
                    "ch6-adv-cherry-pick-one",
                    "git-cherry-pick/one-commit",
                    "Cherry-pick one",
                    ["git cherry-pick c2"],
                    state="cherry",
                    story=(
                        "hotfix/auth-guard has exactly one bugfix commit that main also needs, without "
                        "pulling in the rest of that branch's history. Copy just that one commit onto "
                        "main."
                    ),
                    evaluation={
                        "latest_commit": {"branch": "main", "contains_paths": ["src/auth.py"]},
                        "rules": [
                            {"type": "cherry_pick_created_new_commit", "source": "c2"},
                            {"type": "cherry_pick_copied_changes_from", "source": "c2"},
                        ],
                    },
                    checks=[
                        {
                            "label": "The bugfix landed on main as a brand-new commit with the same change.",
                            "requirement": {
                                "latest_commit": {"branch": "main", "contains_paths": ["src/auth.py"]},
                                "rules": [
                                    {"type": "cherry_pick_created_new_commit", "source": "c2"},
                                    {"type": "cherry_pick_copied_changes_from", "source": "c2"},
                                ],
                            },
                        },
                    ],
                ),
                _wave(
                    "ch6-adv-cherry-pick-no-commit",
                    "git-cherry-pick/no-commit",
                    "Cherry-pick no commit",
                    ["git cherry-pick --no-commit c2"],
                    state="cherry",
                    story=(
                        "The auth-guard fix needs to be combined with a local edit before it becomes a "
                        "commit. Bring its changes into the staging area without creating a commit yet."
                    ),
                    evaluation={
                        "staging_not_empty": True,
                        "rules": [
                            {"type": "operation_metadata_equals", "key": "last_cherry_pick_no_commit", "value": True}
                        ],
                    },
                    checks=[
                        {
                            "label": "The fix is staged, ready to combine with local edits, with no commit created yet.",
                            "requirement": {
                                "staging_not_empty": True,
                                "rules": [
                                    {
                                        "type": "operation_metadata_equals",
                                        "key": "last_cherry_pick_no_commit",
                                        "value": True,
                                    }
                                ],
                            },
                        },
                    ],
                ),
                _wave(
                    "ch6-adv-abort-cherry-pick",
                    "git-cherry-pick/abort",
                    "Abort cherry-pick",
                    ["git cherry-pick --abort"],
                    state="cherry-abort",
                    story=(
                        "A cherry-pick was started onto the wrong target and is now stuck mid-way. Back "
                        "all the way out to the state before it began."
                    ),
                    evaluation={
                        "staging_empty": True,
                        "working_tree_clean": True,
                    },
                    checks=[
                        {
                            "label": "The cherry-pick is fully backed out; the repository is clean again.",
                            "requirement": {"staging_empty": True, "working_tree_clean": True},
                        },
                    ],
                ),
            ],
        },
        {
            "slug": "patch-movement-workflows",
            "title": "Patch Movement Workflows",
            "waves": [
                _wave(
                    "ch6-adv-pick-then-adjust",
                    "git-cherry-pick/no-commit",
                    "Pick then adjust",
                    ["git cherry-pick --no-commit c2", "git add src/auth.py", "git commit -m 'Adapt picked fix'"],
                    required=["git cherry-pick --no-commit", "git commit"],
                    forms=["git-add/file", "git-commit/message"],
                    state="cherry",
                    story=(
                        "The auth-guard fix from hotfix/auth-guard needs a small adjustment before it "
                        "fits main. Bring it in unstaged, adapt it, then commit the adapted version as "
                        "a single new commit."
                    ),
                    evaluation={
                        "latest_commit": {
                            "branch": "main",
                            "contains_paths": ["src/auth.py"],
                            "message_contains": ["Adapt picked fix"],
                        },
                        "staging_empty": True,
                    },
                    checks=[
                        {
                            "label": "The fix was copied in unstaged before being adapted.",
                            "requirement": {"required_commands": ["git cherry-pick --no-commit"]},
                        },
                        {
                            "label": "The adapted fix is committed as one new commit on main.",
                            "requirement": {
                                "latest_commit": {
                                    "branch": "main",
                                    "contains_paths": ["src/auth.py"],
                                    "message_contains": ["Adapt picked fix"],
                                }
                            },
                        },
                    ],
                    workspace_files=[
                        {
                            "after_command_index": 1,
                            "path": "src/auth.py",
                            "content": "guard\nadapted=True\n",
                        }
                    ],
                ),
                _wave(
                    "ch6-adv-stash-and-pick",
                    "git-stash/push",
                    "Stash and pick",
                    [
                        "git stash",
                        "git cherry-pick c2",
                        "git stash pop",
                        "git add README.md",
                        "git commit -m 'Restore WIP after pick'",
                    ],
                    required=["git stash", "git cherry-pick", "git stash pop", "git commit"],
                    forms=["git-cherry-pick/one-commit", "git-stash/pop", "git-add/file", "git-commit/message"],
                    state="stash-cherry",
                    story=(
                        "Local WIP is in the way of bringing in a commit from another branch. Shelve "
                        "it, transplant the commit, then restore and commit the WIP so nothing is lost."
                    ),
                    evaluation={
                        "latest_commit": {
                            "branch": "main",
                            "contains_paths": ["README.md"],
                            "message_contains": ["Restore WIP after pick"],
                        },
                        "staging_empty": True,
                        "rules": [
                            {"type": "operation_metadata_equals", "key": "last_cherry_pick_source", "value": "c2"}
                        ],
                    },
                    checks=[
                        {
                            "label": "Local WIP was shelved before the transplant, and the picked commit landed on main.",
                            "requirement": {
                                "rules": [
                                    {
                                        "type": "operation_metadata_equals",
                                        "key": "last_cherry_pick_source",
                                        "value": "c2",
                                    }
                                ]
                            },
                        },
                        {
                            "label": "The restored WIP is committed on main afterward.",
                            "requirement": {
                                "latest_commit": {
                                    "branch": "main",
                                    "contains_paths": ["README.md"],
                                    "message_contains": ["Restore WIP after pick"],
                                }
                            },
                        },
                    ],
                ),
                _wave(
                    "ch6-adv-abort-then-pick-right-commit",
                    "git-cherry-pick/abort",
                    "Abort then pick right commit",
                    ["git cherry-pick --abort", "git cherry-pick c2"],
                    required=["git cherry-pick --abort", "git cherry-pick"],
                    forms=["git-cherry-pick/one-commit"],
                    state="cherry-abort",
                    story=(
                        "The wrong commit was cherry-picked and is now stuck mid-conflict. Back it out "
                        "completely, then bring in the correct patch instead."
                    ),
                    evaluation={
                        "latest_commit": {"branch": "main", "contains_paths": ["src/auth.py"]},
                        "rules": [{"type": "cherry_pick_created_new_commit", "source": "c2"}],
                    },
                    checks=[
                        {
                            "label": "The wrong pick was fully aborted first.",
                            "requirement": {"required_commands": ["git cherry-pick --abort"]},
                        },
                        {
                            "label": "Only the correct patch appears on main afterward.",
                            "requirement": {
                                "latest_commit": {"branch": "main", "contains_paths": ["src/auth.py"]},
                                "rules": [{"type": "cherry_pick_created_new_commit", "source": "c2"}],
                            },
                        },
                    ],
                ),
            ],
        },
        {
            "slug": "transplant-drills",
            "title": "Transplant Drills",
            "waves": [
                _wave(
                    "ch6-adv-pick-then-verify",
                    "git-cherry-pick/one-commit",
                    "Transplant, then read the record",
                    ["git cherry-pick c2", "git log --oneline"],
                    required=["git cherry-pick", "git log"],
                    forms=["git-log/oneline"],
                    state="cherry",
                    story=(
                        "Copy the approved bugfix onto main as its own brand-new commit, then "
                        "read the compact history to confirm the transplant sits on top with "
                        "the same change and a new identity."
                    ),
                    evaluation={
                        "latest_commit": {"branch": "main", "contains_paths": ["src/auth.py"]},
                        "rules": [
                            {"type": "cherry_pick_created_new_commit", "source": "c2"},
                            {"type": "cherry_pick_copied_changes_from", "source": "c2"},
                        ],
                    },
                    checks=[
                        {
                            "label": "The fix landed as a brand-new commit on main.",
                            "requirement": {
                                "rules": [{"type": "cherry_pick_created_new_commit", "source": "c2"}]
                            },
                        },
                        {
                            "label": "The transplant was confirmed in the history.",
                            "requirement": {"required_commands": ["git log"]},
                        },
                    ],
                ),
                _wave(
                    "ch6-adv-pick-after-look",
                    "git-cherry-pick/one-commit",
                    "Open it first, then transplant",
                    ["git show c2", "git cherry-pick c2"],
                    required=["git show", "git cherry-pick"],
                    forms=["git-show/commit"],
                    state="cherry",
                    story=(
                        "Rule of transplants: never copy a commit you have not read. Open the "
                        "candidate commit and read its full change, then copy it onto main."
                    ),
                    details=[{"label": "Commit to transplant", "value": "c2"}],
                    evaluation={
                        "latest_commit": {"branch": "main", "contains_paths": ["src/auth.py"]},
                        "rules": [
                            {"type": "cherry_pick_created_new_commit", "source": "c2"},
                            {"type": "cherry_pick_copied_changes_from", "source": "c2"},
                        ],
                    },
                    checks=[
                        {
                            "label": "The candidate was read before copying.",
                            "requirement": {"required_commands": ["git show"]},
                        },
                        {
                            "label": "The fix landed on main as a new commit.",
                            "requirement": {
                                "rules": [{"type": "cherry_pick_created_new_commit", "source": "c2"}]
                            },
                        },
                    ],
                ),
                _wave(
                    "ch6-adv-no-commit-inspect",
                    "git-cherry-pick/no-commit",
                    "Stage the patch, review, seal",
                    [
                        "git cherry-pick --no-commit c2",
                        "git diff --staged",
                        "git commit -m 'Reviewed transplant'",
                    ],
                    required=["git cherry-pick --no-commit", "git diff --staged", "git commit"],
                    forms=["git-diff/staged", "git-commit/message"],
                    state="cherry",
                    story=(
                        "Bring the fix's changes into staging without committing, read exactly "
                        "what is about to enter history, and only then seal it under the "
                        "provided message."
                    ),
                    details=[{"label": "Commit message", "value": "Reviewed transplant"}],
                    evaluation={
                        "latest_commit": {
                            "branch": "main",
                            "contains_paths": ["src/auth.py"],
                            "message_contains": ["Reviewed transplant"],
                        },
                        "staging_empty": True,
                    },
                    checks=[
                        {
                            "label": "The staged patch was reviewed before sealing.",
                            "requirement": {"required_commands": ["git diff --staged"]},
                        },
                        {
                            "label": "The reviewed transplant is committed on main.",
                            "requirement": {
                                "latest_commit": {
                                    "branch": "main",
                                    "message_contains": ["Reviewed transplant"],
                                }
                            },
                        },
                    ],
                ),
                _wave(
                    "ch6-adv-no-commit-combine",
                    "git-cherry-pick/no-commit",
                    "Combine the patch with local work",
                    [
                        "git cherry-pick --no-commit c2",
                        "git add README.md",
                        "git commit -m 'Fix plus local note'",
                    ],
                    required=["git cherry-pick --no-commit", "git add", "git commit"],
                    forms=["git-add/file", "git-commit/message"],
                    state="stash-cherry",
                    story=(
                        "The incoming fix and your local README note belong in one commit "
                        "together. Stage the fix without committing, add the local note beside "
                        "it, and seal both as a single snapshot."
                    ),
                    details=[{"label": "Commit message", "value": "Fix plus local note"}],
                    evaluation={
                        "latest_commit": {
                            "branch": "main",
                            "contains_paths": ["src/auth.py", "README.md"],
                            "message_contains": ["Fix plus local note"],
                        },
                        "staging_empty": True,
                    },
                    checks=[
                        {
                            "label": "The fix was staged without an automatic commit.",
                            "requirement": {"required_commands": ["git cherry-pick --no-commit"]},
                        },
                        {
                            "label": "The fix and the local note landed together.",
                            "requirement": {
                                "latest_commit": {
                                    "branch": "main",
                                    "contains_paths": ["src/auth.py", "README.md"],
                                    "message_contains": ["Fix plus local note"],
                                }
                            },
                        },
                    ],
                ),
                _wave(
                    "ch6-adv-abort-quickly",
                    "git-cherry-pick/abort",
                    "Read the wreck, back out",
                    ["git status", "git cherry-pick --abort"],
                    required=["git status", "git cherry-pick --abort"],
                    forms=["git-status/plain"],
                    state="cherry-abort",
                    story=(
                        "A transplant stalled halfway and the deadline will not wait. Read the "
                        "state to see what is stuck, then back the whole attempt out cleanly."
                    ),
                    evaluation={
                        "staging_empty": True,
                        "working_tree_clean": True,
                    },
                    checks=[
                        {
                            "label": "The stuck state was read before retreating.",
                            "requirement": {"required_commands": ["git status"]},
                        },
                        {
                            "label": "The transplant is fully backed out.",
                            "requirement": {"staging_empty": True, "working_tree_clean": True},
                        },
                    ],
                ),
                _wave(
                    "ch6-adv-abort-then-report",
                    "git-cherry-pick/abort",
                    "Back out, then read the record",
                    ["git cherry-pick --abort", "git log --oneline"],
                    required=["git cherry-pick --abort", "git log"],
                    forms=["git-log/oneline"],
                    state="cherry-abort",
                    story=(
                        "Back the stuck transplant out entirely, then read the compact history "
                        "to confirm the record shows no trace of the failed attempt."
                    ),
                    evaluation={"staging_empty": True, "working_tree_clean": True},
                    checks=[
                        {
                            "label": "The stuck transplant is fully backed out.",
                            "requirement": {"staging_empty": True, "working_tree_clean": True},
                        },
                        {
                            "label": "The untouched record was confirmed.",
                            "requirement": {"required_commands": ["git log"]},
                        },
                    ],
                ),
            ],
        },
        {
            "slug": "transplant-capstones",
            "title": "Transplant Capstones",
            "waves": [
                _wave(
                    "ch6-adv-abort-and-adjust",
                    "git-cherry-pick/abort",
                    "Abort, then transplant carefully",
                    [
                        "git cherry-pick --abort",
                        "git cherry-pick --no-commit c2",
                        "git add src/auth.py",
                        "git commit -m 'Adapted after abort'",
                    ],
                    required=["git cherry-pick --abort", "git cherry-pick --no-commit", "git add", "git commit"],
                    forms=["git-cherry-pick/no-commit", "git-add/file", "git-commit/message"],
                    state="cherry-abort",
                    story=(
                        "The blunt transplant failed; do it the careful way instead. Back out "
                        "the stuck attempt, bring the changes in without committing, adjust the "
                        "staging, and seal the adapted result."
                    ),
                    details=[{"label": "Commit message", "value": "Adapted after abort"}],
                    evaluation={
                        "latest_commit": {
                            "branch": "main",
                            "contains_paths": ["src/auth.py"],
                            "message_contains": ["Adapted after abort"],
                        },
                        "staging_empty": True,
                        "rules": [
                            {
                                "type": "operation_metadata_equals",
                                "key": "last_cherry_pick_no_commit",
                                "value": True,
                            }
                        ],
                    },
                    checks=[
                        {
                            "label": "The stuck attempt was fully backed out first.",
                            "requirement": {"required_commands": ["git cherry-pick --abort"]},
                        },
                        {
                            "label": "The careful transplant landed as an adapted commit.",
                            "requirement": {
                                "latest_commit": {
                                    "branch": "main",
                                    "message_contains": ["Adapted after abort"],
                                }
                            },
                        },
                    ],
                    workspace_files=[
                        {
                            "after_command_index": 2,
                            "path": "src/auth.py",
                            "content": "guard\nadapted_after_abort=True\n",
                        }
                    ],
                ),
                _wave(
                    "ch6-adv-abort-final-drill",
                    "git-cherry-pick/abort",
                    "Script-check, retreat, confirm",
                    ["git status --porcelain", "git cherry-pick --abort", "git status"],
                    required=["git status --porcelain", "git cherry-pick --abort", "git status"],
                    forms=["git-status/porcelain", "git-status/plain"],
                    state="cherry-abort",
                    story=(
                        "Capture the stuck transplant's state in script-stable form for the "
                        "incident note, back the attempt out completely, and confirm the "
                        "workspace reads clean again."
                    ),
                    evaluation={
                        "staging_empty": True,
                        "working_tree_clean": True,
                        "rules": [
                            {
                                "type": "required_command_sequence",
                                "commands": [
                                    "git status --porcelain",
                                    "git cherry-pick --abort",
                                    "git status",
                                ],
                            }
                        ],
                    },
                    checks=[
                        {
                            "label": "The stuck state was captured before retreating.",
                            "requirement": {"required_commands": ["git status --porcelain"]},
                        },
                        {
                            "label": "The workspace reads clean after the retreat.",
                            "requirement": {"staging_empty": True, "working_tree_clean": True},
                        },
                        {
                            "label": "The clean workspace was confirmed after the cherry-pick was aborted.",
                            "requirement": {
                                "rules": [
                                    {
                                        "type": "required_command_sequence",
                                        "commands": [
                                            "git status --porcelain",
                                            "git cherry-pick --abort",
                                            "git status",
                                        ],
                                    }
                                ]
                            },
                        },
                    ],
                ),
                _wave(
                    "ch6-adv-pick-pair",
                    "git-cherry-pick/one-commit",
                    "Transplant, then open the result",
                    ["git cherry-pick c2", "git show"],
                    required=["git cherry-pick", "git show"],
                    forms=["git-show/head"],
                    state="cherry",
                    story=(
                        "Copy the approved fix onto main, then open the freshly created commit "
                        "and read it - same change as the original, brand-new identity here."
                    ),
                    evaluation={
                        "latest_commit": {"branch": "main", "contains_paths": ["src/auth.py"]},
                        "rules": [
                            {"type": "cherry_pick_created_new_commit", "source": "c2"},
                            {"type": "cherry_pick_copied_changes_from", "source": "c2"},
                        ],
                    },
                    checks=[
                        {
                            "label": "The fix landed as a brand-new commit.",
                            "requirement": {
                                "rules": [{"type": "cherry_pick_created_new_commit", "source": "c2"}]
                            },
                        },
                        {
                            "label": "The fresh transplant was opened and read.",
                            "requirement": {"required_commands": ["git show"]},
                        },
                    ],
                ),
                _wave(
                    "ch6-adv-no-commit-final",
                    "git-cherry-pick/no-commit",
                    "Stage the patch, script-check it",
                    ["git cherry-pick --no-commit c2", "git status --porcelain"],
                    required=["git cherry-pick --no-commit", "git status --porcelain"],
                    forms=["git-status/porcelain"],
                    state="cherry",
                    story=(
                        "Bring the fix's changes into staging without committing, then read "
                        "the script-stable state - exactly what the release automation would "
                        "see with a transplant half-landed."
                    ),
                    evaluation={
                        "staging_not_empty": True,
                        "rules": [
                            {
                                "type": "operation_metadata_equals",
                                "key": "last_cherry_pick_no_commit",
                                "value": True,
                            }
                        ],
                    },
                    checks=[
                        {
                            "label": "The patch waits in staging with no commit created.",
                            "requirement": {
                                "staging_not_empty": True,
                                "rules": [
                                    {
                                        "type": "operation_metadata_equals",
                                        "key": "last_cherry_pick_no_commit",
                                        "value": True,
                                    }
                                ],
                            },
                        },
                        {
                            "label": "The half-landed state was read in script-stable form.",
                            "requirement": {"required_commands": ["git status --porcelain"]},
                        },
                    ],
                ),
            ],
        },
    ]
