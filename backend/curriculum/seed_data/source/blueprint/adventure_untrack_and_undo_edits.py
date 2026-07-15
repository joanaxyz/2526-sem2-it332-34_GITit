"""Blueprint adventure levels for untrack-and-undo-edits."""

from __future__ import annotations

from .helpers import _wave

ADVENTURE_LEVELS = [
        {
            "slug": "fix-staging-mistakes",
            "title": "Fix Staging Mistakes",
            "waves": [
                _wave(
                    "ch2-adv-unstage-one-file",
                    "git-restore/staged-file",
                    "Unstage one file",
                    ["git restore --staged README.md"],
                    state="staged",
                    story=(
                        "README.md was staged too early, before it was actually ready. Move it back out "
                        "of the staging area without losing the edit - it should still exist as an "
                        "unstaged change afterward."
                    ),
                    evaluation={"staging_empty": True, "working_tree_dirty": True},
                    checks=[
                        {
                            "label": "README.md is no longer staged, but the edit still exists in the working tree.",
                            "requirement": {"staging_empty": True, "working_tree_dirty": True},
                        },
                    ],
                ),
                _wave(
                    "ch2-adv-discard-working-edit",
                    "git-restore/working-file",
                    "Discard working edit",
                    ["git restore README.md"],
                    state="dirty",
                    story=(
                        "A leftover debug edit in README.md needs to disappear completely before real "
                        "work starts. Throw it away and return the file to its last committed content."
                    ),
                    evaluation={"working_tree_clean": True, "staging_empty": True},
                    checks=[
                        {
                            "label": "The debug edit is gone; the file matches the last commit again.",
                            "requirement": {"working_tree_clean": True, "staging_empty": True},
                        },
                    ],
                ),
                _wave(
                    "ch2-adv-repair-before-commit",
                    "git-status/plain",
                    "Repair before commit",
                    [
                        "git status",
                        "git restore --staged scratch.txt",
                        "git restore debug.log",
                        "git add -p src/app.py",
                        "git commit -m 'Commit real fix'",
                    ],
                    required=["git status", "git restore --staged", "git restore", "git add -p", "git commit"],
                    forms=["git-restore/staged-file", "git-restore/working-file", "git-add/patch", "git-commit/message"],
                    state="repair",
                    story=(
                        "The worktree is a genuine mess: scratch.txt was staged by mistake, debug.log is "
                        "an unwanted local edit, and src/app.py mixes a real fix with a leftover debug "
                        "hunk. Inspect the mess, undo both mistakes, and commit only the real fix."
                    ),
                    evaluation={
                        "latest_commit": {
                            "branch": "main",
                            "contains_paths": ["src/app.py"],
                            "message_contains": ["Commit real fix"],
                        },
                        "staging_empty": True,
                    },
                    checks=[
                        {
                            "label": "The mixed worktree was inspected with status before acting.",
                            "requirement": {"required_commands": ["git status"]},
                        },
                        {
                            "label": "The wrongly staged scratch file and the unwanted edit are both undone.",
                            "requirement": {
                                "rules": [
                                    {"type": "staging_excludes", "path": "scratch.txt"},
                                ]
                            },
                        },
                        {
                            "label": "Only the real fix from src/app.py is committed.",
                            "requirement": {
                                "latest_commit": {
                                    "branch": "main",
                                    "contains_paths": ["src/app.py"],
                                    "message_contains": ["Commit real fix"],
                                }
                            },
                        },
                    ],
                ),
                _wave(
                    "ch2-adv-restore-then-redo",
                    "git-restore/staged-file",
                    "Unstage, re-read, discard",
                    ["git restore --staged README.md", "git diff", "git restore README.md"],
                    required=["git restore --staged", "git diff", "git restore"],
                    forms=["git-diff/working", "git-restore/working-file"],
                    state="staged",
                    story=(
                        "Second thoughts about a staged README.md edit: pull it back out of the "
                        "staging area, read it once more as an unstaged change, and conclude it "
                        "was wrong all along - discard it completely."
                    ),
                    evaluation={
                        "working_tree_clean": True,
                        "staging_empty": True,
                        "rules": [{"type": "commit_count_equals", "count": 1}],
                    },
                    checks=[
                        {
                            "label": "The edit was pulled back and re-read before the decision.",
                            "requirement": {"required_commands": ["git restore --staged", "git diff"]},
                        },
                        {
                            "label": "The workspace is fully clean; the edit is gone.",
                            "requirement": {"working_tree_clean": True, "staging_empty": True},
                        },
                    ],
                ),
                _wave(
                    "ch2-adv-porcelain-repair",
                    "git-status/porcelain",
                    "Script-check, then repair",
                    [
                        "git status --porcelain",
                        "git restore --staged scratch.txt",
                        "git restore debug.log",
                        "git add -p src/app.py",
                        "git commit -m 'Keep only the real fix'",
                    ],
                    required=["git status --porcelain", "git restore --staged", "git restore", "git add -p", "git commit"],
                    forms=["git-restore/staged-file", "git-restore/working-file", "git-add/patch", "git-commit/message"],
                    state="repair",
                    story=(
                        "The automation flagged this workspace: junk staged by mistake, an "
                        "unwanted local edit, and one real fix buried in mixed hunks. Read the "
                        "script-stable state, undo both mistakes, and commit only the fix."
                    ),
                    details=[{"label": "Commit message", "value": "Keep only the real fix"}],
                    evaluation={
                        "latest_commit": {
                            "branch": "main",
                            "contains_paths": ["src/app.py"],
                            "excludes_paths": ["scratch.txt", "debug.log"],
                            "message_contains": ["Keep only the real fix"],
                        },
                        "staging_empty": True,
                        "rules": [{"type": "commit_count_equals", "count": 2}],
                    },
                    checks=[
                        {
                            "label": "The mess was read in script-stable form before acting.",
                            "requirement": {"required_commands": ["git status --porcelain"]},
                        },
                        {
                            "label": "Only the real fix is committed; both mistakes are undone.",
                            "requirement": {
                                "latest_commit": {
                                    "branch": "main",
                                    "contains_paths": ["src/app.py"],
                                    "excludes_paths": ["scratch.txt", "debug.log"],
                                    "message_contains": ["Keep only the real fix"],
                                }
                            },
                        },
                    ],
                ),
            ],
        },
        {
            "slug": "remove-or-stop-tracking-files",
            "title": "Remove or Stop Tracking Files",
            "waves": [
                _wave(
                    "ch2-adv-rm-intro",
                    "git-rm/tracked-file",
                    "Stage a file's removal",
                    ["git rm old.txt"],
                    state="tracked-junk",
                    story=(
                        "old.txt has been dead weight in this project for months. Remove it from "
                        "the working tree and stage that removal for the next snapshot - but do "
                        "not create the snapshot yet."
                    ),
                    evaluation={
                        "staging_not_empty": True,
                        "rules": [{"type": "commit_count_equals", "count": 1}],
                    },
                    checks=[
                        {
                            "label": "The file's removal is staged and it is gone from the folder.",
                            "requirement": {"staging_not_empty": True},
                        },
                    ],
                ),
                _wave(
                    "ch2-adv-rm-cached-intro",
                    "git-rm/cached",
                    "Stop tracking, keep the file",
                    ["git rm --cached .env"],
                    state="tracked-junk",
                    story=(
                        ".env holds this machine's local secrets, yet Git is tracking it. Stage "
                        "the instruction that removes it from tracking while the file itself stays "
                        "safely on disk."
                    ),
                    evaluation={
                        "staging_not_empty": True,
                        "rules": [{"type": "commit_count_equals", "count": 1}],
                    },
                    checks=[
                        {
                            "label": "The untracking is staged while the file stays on disk.",
                            "requirement": {"staging_not_empty": True},
                        },
                    ],
                ),
                _wave(
                    "ch2-adv-rm-dir-intro",
                    "git-rm/recursive-cached",
                    "Stop tracking a directory",
                    ["git rm -r --cached dist"],
                    state="tracked-dir",
                    story=(
                        "The whole dist/ build output directory was committed by mistake, and it "
                        "regenerates on every build. Stage the recursive untracking of the entire "
                        "directory, keeping the files on disk."
                    ),
                    evaluation={
                        "staging_not_empty": True,
                        "rules": [{"type": "commit_count_equals", "count": 1}],
                    },
                    checks=[
                        {
                            "label": "The whole directory's untracking is staged recursively.",
                            "requirement": {"staging_not_empty": True},
                        },
                    ],
                ),
                _wave(
                    "ch2-adv-remove-tracked-file",
                    "git-rm/tracked-file",
                    "Remove tracked file",
                    ["git rm old.txt", "git commit -m 'Remove obsolete file'"],
                    required=["git rm", "git commit"],
                    forms=["git-commit/message"],
                    state="tracked-junk",
                    story=(
                        "old.txt is a tracked file nobody needs anymore. Delete it from both the "
                        "working tree and history, and save that removal as its own commit."
                    ),
                    evaluation={
                        "latest_commit": {
                            "branch": "main",
                            "message_contains": ["Remove obsolete file"],
                        },
                        "staging_empty": True,
                        "rules": [{"type": "tracked_path_removed_from_commit_tree", "path": "old.txt"}],
                    },
                    checks=[
                        {
                            "label": "old.txt is removed from the tracked project entirely.",
                            "requirement": {
                                "rules": [{"type": "tracked_path_removed_from_commit_tree", "path": "old.txt"}]
                            },
                        },
                        {
                            "label": "The removal is committed on main by itself.",
                            "requirement": {
                                "latest_commit": {"branch": "main", "message_contains": ["Remove obsolete file"]}
                            },
                        },
                    ],
                ),
                _wave(
                    "ch2-adv-untrack-local-file",
                    "git-rm/cached",
                    "Untrack local file",
                    ["git rm --cached .env", "git commit -m 'Stop tracking local config'"],
                    required=["git rm --cached", "git commit"],
                    forms=["git-commit/message"],
                    state="tracked-junk",
                    story=(
                        ".env holds this machine's local secrets, but it was accidentally committed. "
                        "Stop tracking it in history while leaving the file itself on disk, then save "
                        "that change."
                    ),
                    evaluation={
                        "latest_commit": {
                            "branch": "main",
                            "message_contains": ["Stop tracking local config"],
                        },
                        "staging_empty": True,
                        "rules": [
                            {"type": "tracked_path_removed_from_commit_tree", "path": ".env"},
                            {"type": "ignored_paths_present", "path": ".env", "statuses": ["untracked", "ignored"]},
                        ],
                    },
                    checks=[
                        {
                            "label": ".env is no longer part of the tracked history.",
                            "requirement": {
                                "rules": [{"type": "tracked_path_removed_from_commit_tree", "path": ".env"}]
                            },
                        },
                        {
                            "label": ".env still exists locally on disk, just untracked.",
                            "requirement": {
                                "rules": [
                                    {
                                        "type": "ignored_paths_present",
                                        "path": ".env",
                                        "statuses": ["untracked", "ignored"],
                                    }
                                ]
                            },
                        },
                    ],
                ),
                _wave(
                    "ch2-adv-untrack-generated-directory",
                    "git-rm/recursive-cached",
                    "Untrack generated directory",
                    ["git rm -r --cached dist", "git add .gitignore", "git commit -m 'Stop tracking build output'"],
                    required=["git rm -r --cached", "git commit"],
                    forms=["git-add/file", "git-commit/message"],
                    state="tracked-dir",
                    story=(
                        "The entire dist/ build output directory was tracked by mistake. Stop tracking "
                        "it recursively, add a .gitignore rule so it can never happen again, and commit "
                        "the cleanup."
                    ),
                    evaluation={
                        "latest_commit": {
                            "branch": "main",
                            "contains_paths": [".gitignore"],
                            "message_contains": ["Stop tracking build output"],
                        },
                        "staging_empty": True,
                        "rules": [
                            {"type": "tracked_path_removed_from_commit_tree", "path": "dist/app.js"},
                            {"type": "tracked_path_removed_from_commit_tree", "path": "dist/app.css"},
                        ],
                    },
                    checks=[
                        {
                            "label": "The entire dist/ directory is removed from tracked history.",
                            "requirement": {
                                "rules": [
                                    {"type": "tracked_path_removed_from_commit_tree", "path": "dist/app.js"},
                                    {"type": "tracked_path_removed_from_commit_tree", "path": "dist/app.css"},
                                ]
                            },
                        },
                        {
                            "label": "A committed ignore rule protects it from being tracked again.",
                            "requirement": {
                                "latest_commit": {
                                    "branch": "main",
                                    "contains_paths": [".gitignore"],
                                    "message_contains": ["Stop tracking build output"],
                                }
                            },
                        },
                    ],
                ),
                _wave(
                    "ch2-adv-cleanup-repo-workflow",
                    "git-rm/tracked-file",
                    "Clean tracked junk",
                    ["git rm old.txt", "git rm --cached .env", "git add .gitignore", "git commit -m 'Clean tracked junk'"],
                    required=["git rm", "git rm --cached", "git commit"],
                    forms=["git-rm/cached", "git-add/file", "git-commit/message"],
                    state="tracked-junk",
                    story=(
                        "This repository accidentally tracked two different kinds of junk at once: an "
                        "obsolete old.txt that should disappear entirely, and a local .env that should "
                        "stay on disk but leave history. Clean both in a single commit and add the "
                        "ignore rule that prevents a repeat."
                    ),
                    evaluation={
                        "latest_commit": {
                            "branch": "main",
                            "contains_paths": [".gitignore"],
                            "message_contains": ["Clean tracked junk"],
                        },
                        "staging_empty": True,
                        "rules": [
                            {"type": "tracked_path_removed_from_commit_tree", "path": "old.txt"},
                            {"type": "tracked_path_removed_from_commit_tree", "path": ".env"},
                            {"type": "ignored_paths_present", "path": ".env", "statuses": ["untracked", "ignored"]},
                        ],
                    },
                    checks=[
                        {
                            "label": "old.txt is deleted entirely and .env is untracked but kept on disk.",
                            "requirement": {
                                "rules": [
                                    {"type": "tracked_path_removed_from_commit_tree", "path": "old.txt"},
                                    {"type": "tracked_path_removed_from_commit_tree", "path": ".env"},
                                    {
                                        "type": "ignored_paths_present",
                                        "path": ".env",
                                        "statuses": ["untracked", "ignored"],
                                    },
                                ]
                            },
                        },
                        {
                            "label": "The cleanup and its ignore rule are committed together.",
                            "requirement": {
                                "latest_commit": {
                                    "branch": "main",
                                    "contains_paths": [".gitignore"],
                                    "message_contains": ["Clean tracked junk"],
                                }
                            },
                        },
                    ],
                ),
            ],
        },
        {
            "slug": "verify-the-cleanup",
            "title": "Verify the Cleanup",
            "waves": [
                _wave(
                    "ch2-adv-ignored-after-untrack",
                    "git-rm/cached",
                    "Untrack, protect, prove",
                    [
                        "git rm --cached .env",
                        "git add .gitignore",
                        "git commit -m 'Ignore local config'",
                        "git status --ignored",
                    ],
                    required=["git rm --cached", "git add", "git commit", "git status --ignored"],
                    forms=["git-add/file", "git-commit/message", "git-status/ignored"],
                    state="tracked-junk",
                    story=(
                        "Untrack the local secrets file, commit the protective rule alongside the "
                        "untracking, then read the state with ignored entries included to prove "
                        "the file is now deliberately overlooked."
                    ),
                    details=[{"label": "Commit message", "value": "Ignore local config"}],
                    evaluation={
                        "latest_commit": {
                            "branch": "main",
                            "contains_paths": [".gitignore"],
                            "message_contains": ["Ignore local config"],
                        },
                        "staging_empty": True,
                        "rules": [
                            {"type": "tracked_path_removed_from_commit_tree", "path": ".env"},
                            {"type": "ignored_paths_present", "path": ".env", "statuses": ["untracked", "ignored"]},
                        ],
                    },
                    checks=[
                        {
                            "label": "The secrets file left tracking and the rule is committed.",
                            "requirement": {
                                "latest_commit": {
                                    "branch": "main",
                                    "contains_paths": [".gitignore"],
                                    "message_contains": ["Ignore local config"],
                                },
                                "rules": [
                                    {"type": "tracked_path_removed_from_commit_tree", "path": ".env"}
                                ],
                            },
                        },
                        {
                            "label": "The ignored state was proven with an ignored-inclusive read.",
                            "requirement": {"required_commands": ["git status --ignored"]},
                        },
                    ],
                ),
                _wave(
                    "ch2-adv-explain-env-rule",
                    "git-check-ignore/verbose",
                    "Untrack, then trace the shield",
                    [
                        "git rm --cached .env",
                        "git add .gitignore",
                        "git commit -m 'Stop tracking secrets'",
                        "git status --ignored",
                        "git check-ignore -v .env",
                    ],
                    required=["git rm --cached", "git add", "git commit", "git status --ignored", "git check-ignore"],
                    forms=["git-rm/cached", "git-add/file", "git-commit/message", "git-status/ignored"],
                    state="tracked-junk",
                    story=(
                        "After untracking the secrets file and committing its protective rule, "
                        "answer the follow-up question with evidence: which exact rule now shields "
                        "it? Read the ignored-inclusive state, then trace the matching pattern."
                    ),
                    details=[{"label": "Commit message", "value": "Stop tracking secrets"}],
                    evaluation={
                        "latest_commit": {
                            "branch": "main",
                            "contains_paths": [".gitignore"],
                            "message_contains": ["Stop tracking secrets"],
                        },
                        "staging_empty": True,
                        "rules": [
                            {"type": "tracked_path_removed_from_commit_tree", "path": ".env"},
                            {"type": "ignored_paths_present", "path": ".env", "statuses": ["untracked", "ignored"]},
                        ],
                    },
                    checks=[
                        {
                            "label": "The secrets file left tracking with its rule committed.",
                            "requirement": {
                                "rules": [
                                    {"type": "tracked_path_removed_from_commit_tree", "path": ".env"}
                                ]
                            },
                        },
                        {
                            "label": "The shielding rule was traced with evidence.",
                            "requirement": {"required_commands": ["git check-ignore"]},
                        },
                    ],
                ),
                _wave(
                    "ch2-adv-dir-preview",
                    "git-rm/recursive-cached",
                    "Preview a directory untracking",
                    ["git rm -r --cached dist", "git status --porcelain"],
                    required=["git rm -r --cached", "git status --porcelain"],
                    forms=["git-status/porcelain"],
                    state="tracked-dir",
                    story=(
                        "Before committing anything, see exactly what untracking the build "
                        "directory does to the workspace. Stage the recursive untracking, then "
                        "read the script-stable state a release pipeline would observe."
                    ),
                    evaluation={
                        "staging_not_empty": True,
                        "rules": [{"type": "commit_count_equals", "count": 1}],
                    },
                    checks=[
                        {
                            "label": "The directory untracking is staged for review.",
                            "requirement": {"staging_not_empty": True},
                        },
                        {
                            "label": "The resulting state was read in script-stable form.",
                            "requirement": {"required_commands": ["git status --porcelain"]},
                        },
                    ],
                ),
                _wave(
                    "ch2-adv-dir-cleanup-verify",
                    "git-rm/recursive-cached",
                    "Drop build output, verify twice",
                    [
                        "git rm -r --cached dist",
                        "git add .gitignore",
                        "git commit -m 'Drop build output'",
                        "git status --ignored",
                        "git check-ignore -v dist/app.js",
                    ],
                    required=["git rm -r --cached", "git add", "git commit", "git status --ignored", "git check-ignore"],
                    forms=["git-add/file", "git-commit/message", "git-status/ignored", "git-check-ignore/verbose"],
                    state="tracked-dir",
                    story=(
                        "Finish the build-output cleanup end to end: untrack the directory "
                        "recursively, commit it together with the protective rule, then verify "
                        "the result twice - once in the ignored-inclusive state, once by tracing "
                        "the exact rule that now covers the bundle."
                    ),
                    details=[{"label": "Commit message", "value": "Drop build output"}],
                    evaluation={
                        "latest_commit": {
                            "branch": "main",
                            "contains_paths": [".gitignore"],
                            "message_contains": ["Drop build output"],
                        },
                        "staging_empty": True,
                        "rules": [
                            {"type": "tracked_path_removed_from_commit_tree", "path": "dist/app.js"},
                            {"type": "tracked_path_removed_from_commit_tree", "path": "dist/app.css"},
                        ],
                    },
                    checks=[
                        {
                            "label": "The directory left tracking and the rule is committed.",
                            "requirement": {
                                "rules": [
                                    {"type": "tracked_path_removed_from_commit_tree", "path": "dist/app.js"},
                                    {"type": "tracked_path_removed_from_commit_tree", "path": "dist/app.css"},
                                ]
                            },
                        },
                        {
                            "label": "The cleanup was verified with both reads.",
                            "requirement": {
                                "required_commands": ["git status --ignored", "git check-ignore"]
                            },
                        },
                    ],
                ),
                _wave(
                    "ch2-adv-dir-ignore-explain",
                    "git-rm/recursive-cached",
                    "Untrack artifacts, trace the rule",
                    [
                        "git rm -r --cached dist",
                        "git add .gitignore",
                        "git commit -m 'Ignore build artifacts'",
                        "git check-ignore -v dist/app.css",
                    ],
                    required=["git rm -r --cached", "git add", "git commit", "git check-ignore"],
                    forms=["git-add/file", "git-commit/message", "git-check-ignore/verbose"],
                    state="tracked-dir",
                    story=(
                        "The stylesheet bundle keeps being asked about, so make its status "
                        "undeniable: untrack the generated directory, commit the ignore rule, and "
                        "trace exactly which pattern now claims the stylesheet."
                    ),
                    details=[{"label": "Commit message", "value": "Ignore build artifacts"}],
                    evaluation={
                        "latest_commit": {
                            "branch": "main",
                            "contains_paths": [".gitignore"],
                            "message_contains": ["Ignore build artifacts"],
                        },
                        "staging_empty": True,
                        "rules": [
                            {"type": "tracked_path_removed_from_commit_tree", "path": "dist/app.css"},
                        ],
                    },
                    checks=[
                        {
                            "label": "The artifacts left tracking with their rule committed.",
                            "requirement": {
                                "rules": [
                                    {"type": "tracked_path_removed_from_commit_tree", "path": "dist/app.css"}
                                ]
                            },
                        },
                        {
                            "label": "The claiming pattern was traced for the stylesheet.",
                            "requirement": {"required_commands": ["git check-ignore"]},
                        },
                    ],
                ),
                _wave(
                    "ch2-adv-name-only-cleanup",
                    "git-rm/tracked-file",
                    "Remove, then audit the origin",
                    [
                        "git rm old.txt",
                        "git commit -m 'Drop the obsolete file'",
                        "git show --name-only c0",
                    ],
                    required=["git rm", "git commit", "git show --name-only"],
                    forms=["git-commit/message", "git-show/name-only"],
                    state="tracked-junk",
                    story=(
                        "Remove the obsolete file and commit the removal, then answer the "
                        "reviewer's question: when did that file even arrive? Read the bare path "
                        "list of the very first snapshot to confirm its origin."
                    ),
                    details=[{"label": "Commit message", "value": "Drop the obsolete file"}],
                    evaluation={
                        "latest_commit": {
                            "branch": "main",
                            "message_contains": ["Drop the obsolete file"],
                        },
                        "staging_empty": True,
                        "rules": [{"type": "tracked_path_removed_from_commit_tree", "path": "old.txt"}],
                    },
                    checks=[
                        {
                            "label": "The obsolete file is removed and the removal committed.",
                            "requirement": {
                                "rules": [
                                    {"type": "tracked_path_removed_from_commit_tree", "path": "old.txt"}
                                ]
                            },
                        },
                        {
                            "label": "The file's origin was audited in the first snapshot.",
                            "requirement": {"required_commands": ["git show --name-only"]},
                        },
                    ],
                ),
            ],
        },
        {
            "slug": "undo-drills",
            "title": "Undo Drills",
            "waves": [
                _wave(
                    "ch2-adv-discard-drill",
                    "git-restore/working-file",
                    "Glance, then discard",
                    ["git status -s", "git restore README.md"],
                    required=["git status -s", "git restore"],
                    forms=["git-status/short"],
                    state="dirty",
                    story=(
                        "A stray edit landed in README.md during a demo and nobody wants it. Take "
                        "a compact glance to confirm it is the only change, then return the file "
                        "to its last committed content."
                    ),
                    evaluation={
                        "working_tree_clean": True,
                        "staging_empty": True,
                        "rules": [{"type": "commit_count_equals", "count": 1}],
                    },
                    checks=[
                        {
                            "label": "The stray edit is gone; the workspace matches the last commit.",
                            "requirement": {"working_tree_clean": True, "staging_empty": True},
                        },
                    ],
                ),
                _wave(
                    "ch2-adv-unstage-drill",
                    "git-restore/staged-file",
                    "Script-check, then unstage",
                    ["git status --porcelain", "git restore --staged README.md"],
                    required=["git status --porcelain", "git restore --staged"],
                    forms=["git-status/porcelain"],
                    state="staged",
                    story=(
                        "The release automation refuses to run while anything sits in the staging "
                        "area. Read the script-stable state it saw, then move the premature edit "
                        "back out of staging without losing it."
                    ),
                    evaluation={
                        "staging_empty": True,
                        "working_tree_dirty": True,
                        "rules": [{"type": "commit_count_equals", "count": 1}],
                    },
                    checks=[
                        {
                            "label": "Staging is empty again and the edit survives unstaged.",
                            "requirement": {"staging_empty": True, "working_tree_dirty": True},
                        },
                    ],
                ),
                _wave(
                    "ch2-adv-full-reset-workspace",
                    "git-restore/staged-file",
                    "Hand back a pristine machine",
                    [
                        "git config --global user.name 'Learner D'",
                        "git config --global user.email learner-d@example.test",
                        "git config --list",
                        "git restore --staged README.md",
                        "git restore README.md",
                    ],
                    required=["git config --global user.name", "git config --global user.email", "git config --list", "git restore --staged", "git restore"],
                    forms=["git-config/global-user-name", "git-config/global-user-email", "git-config/list", "git-restore/working-file"],
                    state="staged",
                    story=(
                        "This shared machine goes to the next developer in an hour. Record their "
                        "identity shown below, list the settings to confirm, then clear the "
                        "half-staged experiment so they inherit a pristine workspace."
                    ),
                    details=[
                        {"label": "Author name", "value": "Learner D"},
                        {"label": "Author email", "value": "learner-d@example.test"},
                    ],
                    evaluation={
                        "working_tree_clean": True,
                        "staging_empty": True,
                        "rules": [
                            {
                                "type": "operation_metadata_equals",
                                "key": "last_config_key",
                                "value": "user.email",
                            }
                        ],
                    },
                    checks=[
                        {
                            "label": "The next developer's identity is recorded and confirmed.",
                            "requirement": {
                                "rules": [
                                    {
                                        "type": "operation_metadata_equals",
                                        "key": "last_config_key",
                                        "value": "user.email",
                                    }
                                ],
                                "required_commands": ["git config --list"],
                            },
                        },
                        {
                            "label": "The workspace is pristine: nothing staged, nothing modified.",
                            "requirement": {"working_tree_clean": True, "staging_empty": True},
                        },
                    ],
                ),
                _wave(
                    "ch2-adv-undo-then-update",
                    "git-add/update",
                    "Unstage junk, sweep the real work",
                    [
                        "git restore --staged scratch.txt",
                        "git add -u",
                        "git commit -m 'Stage the right batch'",
                    ],
                    required=["git restore --staged", "git add -u", "git commit"],
                    forms=["git-restore/staged-file", "git-commit/message"],
                    state="repair",
                    story=(
                        "Junk got staged while the real tracked work sat waiting. Pull the junk "
                        "back out of staging, sweep every tracked change in as-is, and commit the "
                        "corrected batch."
                    ),
                    details=[{"label": "Commit message", "value": "Stage the right batch"}],
                    evaluation={
                        "latest_commit": {
                            "branch": "main",
                            "contains_paths": ["src/app.py"],
                            "excludes_paths": ["scratch.txt", "debug.log"],
                            "message_contains": ["Stage the right batch"],
                        },
                        "staging_empty": True,
                        "rules": [{"type": "commit_count_equals", "count": 2}],
                    },
                    checks=[
                        {
                            "label": "The junk left staging before the sweep.",
                            "requirement": {"required_commands": ["git restore --staged"]},
                        },
                        {
                            "label": "The corrected batch is committed without the junk.",
                            "requirement": {
                                "latest_commit": {
                                    "branch": "main",
                                    "contains_paths": ["src/app.py"],
                                    "excludes_paths": ["scratch.txt", "debug.log"],
                                    "message_contains": ["Stage the right batch"],
                                }
                            },
                        },
                    ],
                ),
                _wave(
                    "ch2-adv-remove-verify",
                    "git-rm/tracked-file",
                    "Confirm, then retire a file",
                    [
                        "git status --porcelain",
                        "git rm old.txt",
                        "git commit -m 'Retire the old notes'",
                    ],
                    required=["git status --porcelain", "git rm", "git commit"],
                    forms=["git-status/porcelain", "git-commit/message"],
                    state="tracked-junk",
                    story=(
                        "Before anything is deleted, read the script-stable state to confirm the "
                        "workspace holds no surprises. Then retire the obsolete notes file "
                        "entirely and commit the removal on its own."
                    ),
                    details=[{"label": "Commit message", "value": "Retire the old notes"}],
                    evaluation={
                        "latest_commit": {
                            "branch": "main",
                            "message_contains": ["Retire the old notes"],
                        },
                        "staging_empty": True,
                        "rules": [{"type": "tracked_path_removed_from_commit_tree", "path": "old.txt"}],
                    },
                    checks=[
                        {
                            "label": "The state was confirmed before deleting anything.",
                            "requirement": {"required_commands": ["git status --porcelain"]},
                        },
                        {
                            "label": "The notes file is retired in its own commit.",
                            "requirement": {
                                "rules": [
                                    {"type": "tracked_path_removed_from_commit_tree", "path": "old.txt"}
                                ]
                            },
                        },
                    ],
                ),
                _wave(
                    "ch2-adv-untrack-quick",
                    "git-rm/cached",
                    "Untrack and see the shield",
                    ["git rm --cached .env", "git status --ignored"],
                    required=["git rm --cached", "git status --ignored"],
                    forms=["git-status/ignored"],
                    state="tracked-junk",
                    story=(
                        "The secrets file leaves tracking right now; the protective rule already "
                        "sits in the workspace. Stage the untracking, then read the ignored-"
                        "inclusive state to watch the shield take effect immediately."
                    ),
                    evaluation={
                        "staging_not_empty": True,
                        "rules": [
                            {"type": "ignored_paths_present", "path": ".env", "statuses": ["untracked", "ignored"]},
                        ],
                    },
                    checks=[
                        {
                            "label": "The untracking is staged and the file now reads as shielded.",
                            "requirement": {
                                "staging_not_empty": True,
                                "rules": [
                                    {
                                        "type": "ignored_paths_present",
                                        "path": ".env",
                                        "statuses": ["untracked", "ignored"],
                                    }
                                ],
                            },
                        },
                    ],
                ),
                _wave(
                    "ch2-adv-dir-drill",
                    "git-rm/recursive-cached",
                    "Untrack the regenerating bundle",
                    ["git rm -r --cached dist", "git commit -m 'Untrack generated output'"],
                    required=["git rm -r --cached", "git commit"],
                    forms=["git-commit/message"],
                    state="tracked-dir",
                    story=(
                        "The nightly build regenerated the bundle directory again, and it is "
                        "still tracked from an old mistake. Untrack the whole directory "
                        "recursively and commit that correction by itself."
                    ),
                    details=[{"label": "Commit message", "value": "Untrack generated output"}],
                    evaluation={
                        "latest_commit": {
                            "branch": "main",
                            "message_contains": ["Untrack generated output"],
                        },
                        "staging_empty": True,
                        "rules": [
                            {"type": "tracked_path_removed_from_commit_tree", "path": "dist/app.js"},
                            {"type": "tracked_path_removed_from_commit_tree", "path": "dist/app.css"},
                        ],
                    },
                    checks=[
                        {
                            "label": "The bundle directory left tracking in its own commit.",
                            "requirement": {
                                "rules": [
                                    {"type": "tracked_path_removed_from_commit_tree", "path": "dist/app.js"},
                                    {"type": "tracked_path_removed_from_commit_tree", "path": "dist/app.css"},
                                ]
                            },
                        },
                    ],
                ),
            ],
        },
    ]
