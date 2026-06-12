"""Authored v2 adventure quest curriculum.

The goal of this file is not to dump command trivia. Each quest teaches one Git
move in the smallest realistic situation where that move matters. Challenges in
``challenges.py`` combine these moves into full workday-style scenarios.
"""

from __future__ import annotations

import copy

from curriculum.curriculum_v2.spec_helpers import commit, ev, meta_equals, repo, uninitialized


def _command_from_usage(usage: str) -> str:
    """Return the command family a quest is meant to train.

    Objective checks are shared by every variant of a quest, so they must stay
    variant-safe. Specific files, branches, and commit IDs belong in the
    per-variant evaluation_spec; the checklist only verifies the intended Git
    move was used.
    """
    family = usage.split("/", 1)[0]
    if usage.startswith(("git-checkout/create-and-switch", "git-checkout/legacy-create")):
        return "git switch"
    if usage.startswith("git-checkout/"):
        return "git checkout"
    command_map = {
        "git-cherry-pick": "git cherry-pick",
        "git-ls-files": "git ls-files",
        "git-merge-base": "git merge-base",
        "git-rev-list": "git rev-list",
    }
    if family in command_map:
        return command_map[family]
    if family.startswith("git-"):
        return "git " + family[4:]
    return family.replace("-", " ")


def _variant_safe_checks(usage: str, checks: list[dict] | None) -> list[dict]:
    command = _command_from_usage(usage)
    first_label = None
    for check in checks or []:
        label = str(check.get("label", "")).strip()
        if label:
            first_label = label
            break
    return [
        {
            "label": first_label or f"Use {command} for the requested Git move.",
            "requirement": {"required_commands": [command]},
        }
    ]


def v(case_id: str, label: str, initial: dict, solution: list[str], evaluation: dict, *, hints: list[str] | None = None) -> dict:
    return {
        "case_id": case_id,
        "slug_template": case_id,
        "label_template": label,
        "initial_state_template": initial,
        "solution_commands_template": solution,
        "evaluation_spec_template": evaluation,
        "hint_set_template": hints or [],
        "scaffold_policy_template": {"hints": "progressive", "answer": "never"},
    }


def q(
    usage: str,
    slug: str,
    title: str,
    story: str,
    task: str,
    variants: list[dict],
    *,
    checks: list[dict],
    prerequisites: list[str] | None = None,
    required_successful_attempts: int = 2,
    min_counted_commands: int = 1,
    max_counted_commands: int = 4,
    details: list[dict] | None = None,
    constraints: list[str] | None = None,
) -> dict:
    return {
        "usage": usage,
        "slug": slug,
        "title": title,
        "required_successful_attempts": required_successful_attempts,
        "min_counted_commands": min_counted_commands,
        "max_counted_commands": max_counted_commands,
        "scenario_context": {
            "schema_version": 3,
            "story": story,
            "task": task,
            "details": details or [],
            "constraints": constraints or [],
        },
        "objective_checks": _variant_safe_checks(usage, checks),
        "prerequisites": prerequisites or [],
        "variants": variants,
    }


BASE_TREE = {
    "README.md": "Project notes",
    "src/app.py": "print('hello')\n",
}
BASE = [commit("c0", "Initial project", [], BASE_TREE)]
TWO_COMMITS = [
    commit("c0", "Initial project", [], {"README.md": "Project notes"}),
    commit("c1", "Add app shell", ["c0"], BASE_TREE),
]
THREE_COMMITS = [
    *TWO_COMMITS,
    commit("c2", "Add login copy", ["c1"], {**BASE_TREE, "src/login.py": "title='Login'\n"}),
]

REMOTE_FIXTURE_MAIN = {
    "branches": {"origin/main": "r2"},
    "default_branch": "origin/main",
    "commits": [
        commit("r1", "Create remote starter", [], {"README.md": "remote v1"}),
        commit("r2", "Add starter app", ["r1"], {"README.md": "remote v1", "src/app.py": "remote app"}),
    ],
}

REMOTE_FIXTURE_STARTER = {
    "branches": {"origin/main": "r10", "origin/starter": "r11"},
    "default_branch": "origin/main",
    "commits": [
        commit("r10", "Create lab base", [], {"README.md": "base"}),
        commit("r11", "Prepare starter branch", ["r10"], {"README.md": "base", "starter.md": "exercise"}),
    ],
}

REMOTE_FIXTURE_HISTORY = {
    "branches": {"origin/main": "r22"},
    "default_branch": "origin/main",
    "commits": [
        commit("r20", "Create portal", [], {"README.md": "v1"}),
        commit("r21", "Add page", ["r20"], {"README.md": "v1", "page.md": "v1"}),
        commit("r22", "Polish page", ["r21"], {"README.md": "v2", "page.md": "v2"}),
    ],
}

ADVENTURE_QUESTS = [
    # Storey 1 â€” Repository Foundations
    q(
        "git-init/current-directory",
        "init-current-folder",
        "Initialize an existing project folder",
        "A capstone folder already has starter files, but it has no repository metadata yet.",
        "Turn the current folder into a repository without staging or saving files yet.",
        [
            v("init-current-capstone", "Capstone folder", uninitialized({"README.md": "Capstone notes", "src/app.py": "print('hi')\n"}), ["git init"], ev({"repository_initialized": True}, required=["git init"])),
            v("init-current-docs", "Docs folder", uninitialized({"README.md": "Docs", "guide.md": "Draft"}), ["git init"], ev({"repository_initialized": True}, required=["git init"])),
        ],
        checks=[{"label": "The folder is now a repository.", "requirement": {"repository_initialized": True}}],
    ),
    q(
        "git-init/named-directory",
        "init-named-folder",
        "Initialize a new named folder",
        "A new exercise needs its own repository instead of reusing the current workspace.",
        "Create repository metadata for the requested folder name.",
        [
            v("init-named-invoice", "Invoice project", uninitialized({}), ["git init invoice-tracker"], ev({"repository_initialized": True, "rules": [meta_equals("last_init_directory", "invoice-tracker")]}, required=["git init"])),
            v("init-named-qa", "QA results", uninitialized({}), ["git init qa-results"], ev({"repository_initialized": True, "rules": [meta_equals("last_init_directory", "qa-results")]}, required=["git init"])),
        ],
        checks=[{"label": "A named folder was initialized.", "requirement": {"rules": [{"type": "operation_metadata_not_equals", "key": "last_init_directory", "value": None}]}}],
        prerequisites=["init-current-folder"],
    ),
    q(
        "git-init/initial-branch",
        "init-with-initial-branch",
        "Choose the first branch name",
        "A team standard requires the first branch to use a specific name from the beginning.",
        "Initialize the folder with the requested first branch name.",
        [
            v("init-branch-trunk", "Trunk standard", uninitialized({"README.md": "Portal"}), ["git init -b trunk"], ev({"repository_initialized": True, "head_branch": "trunk", "rules": [meta_equals("last_init_initial_branch", "trunk")]}, required=["git init"])),
            v("init-branch-mainline", "Mainline standard", uninitialized({"README.md": "SDK"}), ["git init --initial-branch mainline"], ev({"repository_initialized": True, "head_branch": "mainline", "rules": [meta_equals("last_init_initial_branch", "mainline")]}, required=["git init"])),
        ],
        checks=[{"label": "HEAD starts on the requested first branch.", "requirement": {"rules": [{"type": "operation_metadata_not_equals", "key": "last_init_initial_branch", "value": "main"}]}}],
        prerequisites=["init-current-folder"],
    ),
    q(
        "git-clone/named-folder",
        "clone-into-named-folder",
        "Clone into a chosen folder",
        "A training repository must be copied locally using the folder name given by the instructor.",
        "Create a local clone in the requested destination folder.",
        [
            v("clone-named-tower", "Tower lab", uninitialized({}, remote_fixtures=REMOTE_FIXTURE_MAIN), ["git clone https://example.test/cit/tower.git tower-lab"], ev({"repository_initialized": True, "remote_exists": ["origin"], "upstream_tracking_set": ["main"], "rules": [meta_equals("last_clone_destination", "tower-lab")]}, required=["git clone"])),
            v("clone-named-api", "API lab", uninitialized({}, remote_fixtures=REMOTE_FIXTURE_MAIN), ["git clone https://example.test/cit/api.git api-lab"], ev({"repository_initialized": True, "remote_exists": ["origin"], "upstream_tracking_set": ["main"], "rules": [meta_equals("last_clone_destination", "api-lab")]}, required=["git clone"])),
        ],
        checks=[{"label": "The clone has an origin remote and local main branch.", "requirement": {"remote_exists": ["origin"], "upstream_tracking_set": ["main"]}}],
        prerequisites=["init-current-folder"],
    ),
    q(
        "git-clone/branch",
        "clone-specific-branch",
        "Clone a specific branch",
        "A lab has separate starter content that is not on the default branch.",
        "Clone the repository and check out the starter branch immediately.",
        [
            v("clone-branch-starter", "Starter branch", uninitialized({}, remote_fixtures=REMOTE_FIXTURE_STARTER), ["git clone -b starter https://example.test/cit/lab.git lab"], ev({"repository_initialized": True, "head_branch": "starter", "upstream_tracking": {"starter": "origin/starter"}, "rules": [meta_equals("last_clone_branch", "starter")]}, required=["git clone"])),
            v("clone-branch-main", "Explicit main", uninitialized({}, remote_fixtures=REMOTE_FIXTURE_STARTER), ["git clone --branch main https://example.test/cit/lab.git lab-main"], ev({"repository_initialized": True, "head_branch": "main", "upstream_tracking": {"main": "origin/main"}, "rules": [meta_equals("last_clone_branch", "main")]}, required=["git clone"])),
        ],
        checks=[{"label": "The local branch tracks the chosen remote branch.", "requirement": {"upstream_tracking_set": ["starter"]}}],
        prerequisites=["clone-into-named-folder"],
    ),
    q(
        "git-clone/depth",
        "clone-shallow-history",
        "Clone only the latest history slice",
        "A large repository is needed only for a short review, so old history should not be copied.",
        "Create a shallow local clone.",
        [
            v("clone-depth-portal", "Portal review", uninitialized({}, remote_fixtures=REMOTE_FIXTURE_HISTORY), ["git clone --depth 1 https://example.test/cit/portal.git"], ev({"repository_initialized": True, "rules": [meta_equals("last_clone_shallow", True), meta_equals("last_clone_depth", 1), {"type": "commit_count_equals", "count": 1}]}, required=["git clone"])),
            v("clone-depth-docs", "Docs review", uninitialized({}, remote_fixtures=REMOTE_FIXTURE_HISTORY), ["git clone --depth 2 https://example.test/cit/docs.git docs"], ev({"repository_initialized": True, "rules": [meta_equals("last_clone_shallow", True), meta_equals("last_clone_depth", 2), {"type": "commit_count_equals", "count": 2}]}, required=["git clone"])),
        ],
        checks=[{"label": "The clone is marked as shallow.", "requirement": {"rules": [meta_equals("last_clone_shallow", True)]}}],
        prerequisites=["clone-into-named-folder"],
    ),
    q(
        "git-status/plain",
        "inspect-status",
        "Inspect current repository state",
        "Before staging anything, you need to know what is changed and what is still untouched.",
        "Inspect the repository without changing it.",
        [
            v("status-working-change", "Working change", repo(commits=BASE, working_tree={"src/app.py": "print('hello world')\n"}), ["git status"], ev({"repository_state_unchanged": True}, required=["git status"])),
            v("status-staged-change", "Staged change", repo(commits=BASE, staging={"src/app.py": "print('hello world')\n"}), ["git status"], ev({"repository_state_unchanged": True}, required=["git status"])),
        ],
        checks=[{"label": "Repository state was inspected without mutation.", "requirement": {"repository_state_unchanged": True, "required_commands": ["git status"]}}],
        prerequisites=["init-current-folder"],
        min_counted_commands=0,
        max_counted_commands=2,
    ),
    q(
        "git-status/ignored",
        "inspect-ignored-status",
        "Inspect ignored files too",
        "A build artifact may be intentionally ignored, but you need to confirm it is being hidden from normal tracking.",
        "Inspect repository state including ignored files.",
        [
            v("status-ignored-dist", "Ignored build output", repo(commits=BASE, working_tree={"dist/app.js": {"status": "ignored", "content": "bundle"}}), ["git status --ignored"], ev({"repository_state_unchanged": True}, required=["git status --ignored"])),
            v("status-ignored-env", "Ignored env file", repo(commits=BASE, working_tree={".env": {"status": "ignored", "content": "SECRET=1"}}), ["git status --ignored"], ev({"repository_state_unchanged": True}, required=["git status --ignored"])),
        ],
        checks=[{"label": "Ignored paths were included without changing state.", "requirement": {"repository_state_unchanged": True, "required_commands": ["git status --ignored"]}}],
        prerequisites=["inspect-status"],
        min_counted_commands=0,
        max_counted_commands=2,
    ),
    q(
        "git-log/oneline",
        "inspect-compact-history",
        "Inspect compact history",
        "A teammate asks which commits are already on the branch before you start work.",
        "Read the branch history in a compact form without changing the repository.",
        [
            v("log-oneline-two", "Two commits", repo(commits=TWO_COMMITS, branches={"main": "c1"}), ["git log --oneline"], ev({"repository_state_unchanged": True}, required=["git log --oneline"])),
            v("log-oneline-three", "Three commits", repo(commits=THREE_COMMITS, branches={"main": "c2"}), ["git log --oneline"], ev({"repository_state_unchanged": True}, required=["git log --oneline"])),
        ],
        checks=[{"label": "History was inspected without mutation.", "requirement": {"repository_state_unchanged": True, "required_commands": ["git log --oneline"]}}],
        prerequisites=["inspect-status"],
        min_counted_commands=0,
        max_counted_commands=2,
    ),
    q(
        "git-log/graph-all",
        "inspect-graph-history",
        "Inspect graph history across refs",
        "Two branches exist, and you need to see their shape before deciding how to integrate them.",
        "Inspect all visible branch history as a graph without changing state.",
        [
            v("log-graph-feature", "Feature branch graph", repo(commits=THREE_COMMITS + [commit("c3", "Draft profile", ["c1"], {**BASE_TREE, "src/profile.py": "draft"})], branches={"main": "c2", "feature/profile": "c3"}), ["git log --oneline --graph --all"], ev({"repository_state_unchanged": True}, required=["git log --oneline --graph --all"])),
            v("log-graph-hotfix", "Hotfix branch graph", repo(commits=THREE_COMMITS + [commit("c4", "Patch copy", ["c1"], {**BASE_TREE, "README.md": "patched"})], branches={"main": "c2", "hotfix/copy": "c4"}), ["git log --oneline --graph --all"], ev({"repository_state_unchanged": True}, required=["git log --oneline --graph --all"])),
        ],
        checks=[{"label": "All refs were inspected without mutation.", "requirement": {"repository_state_unchanged": True, "required_commands": ["git log --oneline --graph --all"]}}],
        prerequisites=["inspect-compact-history"],
        min_counted_commands=0,
        max_counted_commands=2,
    ),
    q(
        "git-show/commit",
        "inspect-named-commit",
        "Inspect a named commit",
        "A short commit id appears in a review comment, and you need to inspect it before acting.",
        "Inspect the named commit without modifying repository state.",
        [
            v("show-commit-c1", "App shell commit", repo(commits=TWO_COMMITS, branches={"main": "c1"}), ["git show c1"], ev({"repository_state_unchanged": True}, required=["git show c1"])),
            v("show-commit-c2", "Login copy commit", repo(commits=THREE_COMMITS, branches={"main": "c2"}), ["git show c2"], ev({"repository_state_unchanged": True}, required=["git show c2"])),
        ],
        checks=[{"label": "The named commit was inspected without mutation.", "requirement": {"repository_state_unchanged": True}}],
        prerequisites=["inspect-compact-history"],
        min_counted_commands=0,
        max_counted_commands=2,
    ),
]

ADVENTURE_QUESTS += [
    # Storey 2 â€” Tracking Changes and Snapshots
    q(
        "git-diff/working",
        "inspect-working-diff",
        "Compare unstaged work",
        "You have edited a file, but you need to review the actual content difference before staging it.",
        "Inspect the unstaged difference without changing repository state.",
        [
            v("diff-working-app", "App edit", repo(commits=BASE, working_tree={"src/app.py": "print('hello tower')\n"}), ["git diff"], ev({"repository_state_unchanged": True}, required=["git diff"])),
            v("diff-working-readme", "Readme edit", repo(commits=BASE, working_tree={"README.md": "Updated project notes"}), ["git diff"], ev({"repository_state_unchanged": True}, required=["git diff"])),
        ],
        checks=[{"label": "Unstaged work was inspected without mutation.", "requirement": {"repository_state_unchanged": True, "required_commands": ["git diff"]}}],
        min_counted_commands=0,
        max_counted_commands=2,
    ),
    q(
        "git-add/file",
        "stage-one-file",
        "Stage only one ready file",
        "Several files are changed, but only one file belongs in the next snapshot.",
        "Move only the requested file into the staging area.",
        [
            v("stage-file-app", "Stage app", repo(commits=BASE, working_tree={"src/app.py": "print('ready')\n", "README.md": "draft notes"}), ["git add src/app.py"], ev({"staging_contains": ["src/app.py"], "working_tree_contains": ["README.md"]}, required=["git add"])),
            v("stage-file-readme", "Stage readme", repo(commits=BASE, working_tree={"README.md": "ready notes", "src/app.py": "debug print"}), ["git add README.md"], ev({"staging_contains": ["README.md"], "working_tree_contains": ["src/app.py"]}, required=["git add"])),
        ],
        checks=[{"label": "Only the requested file is staged.", "requirement": {"staging_contains": ["src/app.py"]}}],
        prerequisites=["inspect-working-diff"],
    ),
    q(
        "git-add/dot",
        "stage-visible-folder-work",
        "Stage all visible folder changes",
        "A small docs update is complete and every visible changed file belongs together.",
        "Move the visible working changes into the staging area.",
        [
            v("stage-dot-docs", "Docs batch", repo(commits=BASE, working_tree={"README.md": "new intro", "docs/guide.md": {"status": "untracked", "content": "Guide"}}), ["git add ."], ev({"staging_contains": ["README.md", "docs/guide.md"], "working_tree_clean": True}, required=["git add"])),
            v("stage-dot-ui", "UI batch", repo(commits=BASE, working_tree={"src/app.py": "print('ui')\n", "src/theme.css": {"status": "untracked", "content": "body{}"}}), ["git add ."], ev({"staging_contains": ["src/app.py", "src/theme.css"], "working_tree_clean": True}, required=["git add"])),
        ],
        checks=[{"label": "Visible working changes moved to staging.", "requirement": {"working_tree_clean": True}}],
        prerequisites=["stage-one-file"],
    ),
    q(
        "git-add/all",
        "stage-all-changes",
        "Stage every tracked and untracked change",
        "A cleanup commit should include all adds, edits, and removals that are currently visible.",
        "Prepare every working-tree change for the next snapshot.",
        [
            v("stage-all-cleanup", "Cleanup batch", repo(commits=BASE, working_tree={"src/app.py": "print('clean')\n", "tmp.log": {"status": "untracked", "content": "log"}}), ["git add -A"], ev({"staging_contains": ["src/app.py", "tmp.log"], "working_tree_clean": True}, required=["git add"])),
            v("stage-all-assets", "Asset batch", repo(commits=BASE, working_tree={"README.md": "new", "assets/logo.svg": {"status": "untracked", "content": "svg"}}), ["git add --all"], ev({"staging_contains": ["README.md", "assets/logo.svg"], "working_tree_clean": True}, required=["git add"])),
        ],
        checks=[{"label": "All working changes are staged.", "requirement": {"working_tree_clean": True}}],
        prerequisites=["stage-visible-folder-work"],
    ),
    q(
        "git-add/patch",
        "stage-selected-hunks",
        "Stage selected hunks only",
        "One file has a useful fix and an unrelated draft hunk. Only the useful hunk belongs in the next snapshot.",
        "Stage the selected hunk while leaving the unrelated hunk in the working tree.",
        [
            v("patch-login-hunk", "Login hunk", repo(commits=BASE, working_tree={"src/app.py": {"status": "modified", "hunks": ["login validation", "debug draft"]}}, partial_hunks={"src/app.py": {"target_hunks": ["login validation"], "leftover_hunks": ["debug draft"]}}), ["git add -p src/app.py"], ev({"rules": [{"type": "staging_contains_tokens", "path": "src/app.py", "tokens": ["login validation"]}, {"type": "working_tree_contains_tokens", "path": "src/app.py", "tokens": ["debug draft"]}]}, required=["git add -p"])),
            v("patch-copy-hunk", "Copy hunk", repo(commits=BASE, working_tree={"README.md": {"status": "modified", "hunks": ["clear install steps", "future roadmap"]}}, partial_hunks={"README.md": {"target_hunks": ["clear install steps"], "leftover_hunks": ["future roadmap"]}}), ["git add --patch README.md"], ev({"rules": [{"type": "staging_contains_tokens", "path": "README.md", "tokens": ["clear install steps"]}, {"type": "working_tree_contains_tokens", "path": "README.md", "tokens": ["future roadmap"]}]}, required=["git add --patch"])),
        ],
        checks=[{"label": "The selected hunk is staged, while leftover work remains unstaged.", "requirement": {"rules": [{"type": "staging_contains_tokens", "path": "src/app.py", "tokens": ["login validation"]}]}}],
        prerequisites=["stage-one-file"],
    ),
    q(
        "git-diff/staged",
        "inspect-staged-diff",
        "Review staged content",
        "A file is already prepared for the next snapshot, but you need to verify the staged content before saving it.",
        "Inspect the staged difference without changing repository state.",
        [
            v("diff-staged-app", "Staged app", repo(commits=BASE, staging={"src/app.py": "print('ready')\n"}), ["git diff --staged"], ev({"repository_state_unchanged": True}, required=["git diff --staged"])),
            v("diff-staged-readme", "Staged readme", repo(commits=BASE, staging={"README.md": "ready notes"}), ["git diff --cached"], ev({"repository_state_unchanged": True}, required=["git diff --cached"])),
        ],
        checks=[{"label": "Staged content was inspected without mutation.", "requirement": {"repository_state_unchanged": True}}],
        prerequisites=["stage-one-file"],
        min_counted_commands=0,
        max_counted_commands=2,
    ),
    q(
        "git-commit/message",
        "commit-staged-snapshot",
        "Commit the staged snapshot",
        "The right changes are already staged and need to become a clear local checkpoint.",
        "Save the staged snapshot with the required message.",
        [
            v("commit-login-copy", "Login copy", repo(commits=BASE, staging={"src/app.py": "print('login copy')\n"}), ["git commit -m 'Update login copy'"], ev({"latest_commit": {"branch": "main", "contains_paths": ["src/app.py"], "message_contains": ["Update login copy"]}, "staging_empty": True}, required=["git commit"])),
            v("commit-readme-setup", "Readme setup", repo(commits=BASE, staging={"README.md": "Install steps"}), ["git commit -m 'Update setup notes'"], ev({"latest_commit": {"branch": "main", "contains_paths": ["README.md"], "message_contains": ["Update setup notes"]}, "staging_empty": True}, required=["git commit"])),
        ],
        checks=[{"label": "A new commit exists and the staging area is empty.", "requirement": {"staging_empty": True, "min_commits_on_branch": {"main": 2}}}],
        prerequisites=["stage-one-file", "inspect-staged-diff"],
    ),
    q(
        "git-commit/all-message",
        "commit-tracked-changes-directly",
        "Commit tracked edits directly",
        "Only tracked files should be saved; a new scratch file must remain untracked.",
        "Save the tracked edits in one checkpoint while leaving scratch work alone.",
        [
            v("commit-all-app", "Tracked app edit", repo(commits=BASE, working_tree={"src/app.py": "print('tracked')\n", "scratch.txt": {"status": "untracked", "content": "notes"}}), ["git commit -a -m 'Update tracked app'"], ev({"latest_commit": {"branch": "main", "contains_paths": ["src/app.py"], "excludes_paths": ["scratch.txt"], "message_contains": ["Update tracked app"]}, "working_tree_contains": ["scratch.txt"]}, required=["git commit"])),
            v("commit-all-readme", "Tracked readme edit", repo(commits=BASE, working_tree={"README.md": "tracked notes", "idea.md": {"status": "untracked", "content": "later"}}), ["git commit -a -m 'Update tracked notes'"], ev({"latest_commit": {"branch": "main", "contains_paths": ["README.md"], "excludes_paths": ["idea.md"], "message_contains": ["Update tracked notes"]}, "working_tree_contains": ["idea.md"]}, required=["git commit"])),
        ],
        checks=[{"label": "Tracked edits are committed and untracked scratch remains outside history.", "requirement": {"working_tree_contains": ["scratch.txt"]}}],
        prerequisites=["commit-staged-snapshot"],
    ),
    q(
        "git-restore/staged-file",
        "unstage-one-file",
        "Move a staged file back out of staging",
        "A file was staged too early and needs more review before it belongs in the next snapshot.",
        "Remove the requested file from staging while keeping its work in the working tree.",
        [
            v("unstage-app", "Unstage app", repo(commits=BASE, staging={"src/app.py": "print('draft')\n"}), ["git restore --staged src/app.py"], ev({"working_tree_contains": ["src/app.py"], "rules": [{"type": "staging_excludes", "paths": ["src/app.py"]}]}, required=["git restore"])),
            v("unstage-readme", "Unstage readme", repo(commits=BASE, staging={"README.md": "draft"}), ["git restore --staged README.md"], ev({"working_tree_contains": ["README.md"], "rules": [{"type": "staging_excludes", "paths": ["README.md"]}]}, required=["git restore"])),
        ],
        checks=[{"label": "The file is no longer staged and its work remains local.", "requirement": {"working_tree_contains": ["src/app.py"]}}],
        prerequisites=["stage-one-file"],
    ),
    q(
        "git-restore/working-file",
        "discard-working-file-change",
        "Discard an unwanted working-tree change",
        "A debug edit should be thrown away, not saved or staged.",
        "Restore the requested file back to the committed version.",
        [
            v("restore-app-debug", "Discard app debug", repo(commits=BASE, working_tree={"src/app.py": "print('debug')\n"}), ["git restore src/app.py"], ev({"working_tree_clean": True, "staging_empty": True}, required=["git restore"])),
            v("restore-readme-draft", "Discard readme draft", repo(commits=BASE, working_tree={"README.md": "bad draft"}), ["git restore README.md"], ev({"working_tree_clean": True, "staging_empty": True}, required=["git restore"])),
        ],
        checks=[{"label": "The unwanted working change is gone.", "requirement": {"working_tree_clean": True}}],
        prerequisites=["inspect-working-diff"],
    ),
    q(
        "git-rm/tracked-file",
        "remove-tracked-file",
        "Remove a tracked file from the next commit",
        "A tracked debug file should disappear from the project history going forward.",
        "Stage the removal of the requested tracked file.",
        [
            v("rm-debug-log", "Remove debug log", repo(commits=[commit("c0", "Initial project", [], {**BASE_TREE, "debug.log": "trace"})], branches={"main": "c0"}), ["git rm debug.log"], ev({"working_tree_absent": ["debug.log"], "staging_contains": ["debug.log"]}, required=["git rm"])),
            v("rm-old-report", "Remove old report", repo(commits=[commit("c0", "Initial project", [], {**BASE_TREE, "reports/old.txt": "old"})], branches={"main": "c0"}), ["git rm reports/old.txt"], ev({"working_tree_absent": ["reports/old.txt"], "staging_contains": ["reports/old.txt"]}, required=["git rm"])),
        ],
        checks=[{"label": "Removal is staged and the file is gone from the working tree.", "requirement": {"working_tree_absent": ["debug.log"], "staging_contains": ["debug.log"]}}],
        prerequisites=["commit-staged-snapshot"],
    ),
    q(
        "git-rm/cached",
        "stop-tracking-local-file",
        "Stop tracking a file but keep it locally",
        "A local configuration file was accidentally tracked and should stay on disk but leave future commits.",
        "Stage the file for removal from tracking while preserving the local copy.",
        [
            v("rm-cached-env", "Keep local env", repo(commits=[commit("c0", "Track env", [], {**BASE_TREE, ".env": "SECRET=1"})], branches={"main": "c0"}), ["git rm --cached .env"], ev({"staging_contains": [".env"], "working_tree_contains": [".env"], "rules": [meta_equals("last_rm_cached_paths", [".env"])]}, required=["git rm --cached"])),
            v("rm-cached-local", "Keep local settings", repo(commits=[commit("c0", "Track settings", [], {**BASE_TREE, "local.json": "{}"})], branches={"main": "c0"}), ["git rm --cached local.json"], ev({"staging_contains": ["local.json"], "working_tree_contains": ["local.json"], "rules": [meta_equals("last_rm_cached_paths", ["local.json"])]}, required=["git rm --cached"])),
        ],
        checks=[{"label": "The file is staged for untracking but still exists locally.", "requirement": {"staging_contains": [".env"], "working_tree_contains": [".env"]}}],
        prerequisites=["remove-tracked-file"],
    ),
]

BRANCH_BASE = [
    commit("c0", "Initial project", [], {"README.md": "base"}),
    commit("c1", "Add app shell", ["c0"], {"README.md": "base", "src/app.py": "v1"}),
    commit("c2", "Add dashboard", ["c1"], {"README.md": "base", "src/app.py": "v1", "src/dashboard.py": "v1"}),
]

ADVENTURE_QUESTS += [
    # Storey 3 â€” Branch Navigation
    q(
        "git-branch/list",
        "list-local-branches",
        "List local branches",
        "Before switching work streams, you need to see which local branch names already exist.",
        "Inspect local branch names without changing repository state.",
        [
            v("branch-list-feature", "Feature branches", repo(commits=BRANCH_BASE, branches={"main": "c2", "feature/login": "c2"}), ["git branch"], ev({"repository_state_unchanged": True}, required=["git branch"])),
            v("branch-list-hotfix", "Hotfix branches", repo(commits=BRANCH_BASE, branches={"main": "c2", "hotfix/copy": "c1"}), ["git branch"], ev({"repository_state_unchanged": True}, required=["git branch"])),
        ],
        checks=[{"label": "Branches were inspected without mutation.", "requirement": {"repository_state_unchanged": True, "required_commands": ["git branch"]}}],
        min_counted_commands=0,
        max_counted_commands=2,
    ),
    q(
        "git-branch/create",
        "create-branch-pointer",
        "Create a branch without switching",
        "A teammate needs a branch pointer prepared, but you should keep working on the current branch for now.",
        "Create the requested branch while leaving HEAD where it is.",
        [
            v("branch-create-profile", "Profile branch", repo(commits=BRANCH_BASE, branches={"main": "c2"}), ["git branch feature/profile"], ev({"branch_exists": ["feature/profile"], "head_branch": "main", "branch_points_to": {"feature/profile": "c2"}}, required=["git branch"])),
            v("branch-create-docs", "Docs branch", repo(commits=BRANCH_BASE, branches={"main": "c2"}), ["git branch docs-refresh"], ev({"branch_exists": ["docs-refresh"], "head_branch": "main", "branch_points_to": {"docs-refresh": "c2"}}, required=["git branch"])),
        ],
        checks=[{"label": "The new branch exists and HEAD did not move.", "requirement": {"branch_exists": ["feature/profile"], "head_branch": "main"}}],
        prerequisites=["list-local-branches"],
    ),
    q(
        "git-branch/create-at-start",
        "create-branch-at-start-point",
        "Create a branch at an older start point",
        "A hotfix needs to start from a stable commit instead of the latest work on main.",
        "Create the requested branch pointer at the specified existing commit.",
        [
            v("branch-start-c1", "Hotfix from c1", repo(commits=BRANCH_BASE, branches={"main": "c2"}), ["git branch hotfix/login c1"], ev({"branch_exists": ["hotfix/login"], "branch_points_to": {"hotfix/login": "c1"}, "head_branch": "main"}, required=["git branch"])),
            v("branch-start-c0", "Archive from c0", repo(commits=BRANCH_BASE, branches={"main": "c2"}), ["git branch archive/base c0"], ev({"branch_exists": ["archive/base"], "branch_points_to": {"archive/base": "c0"}, "head_branch": "main"}, required=["git branch"])),
        ],
        checks=[{"label": "The new branch points to the requested older commit.", "requirement": {"branch_points_to": {"hotfix/login": "c1"}}}],
        prerequisites=["create-branch-pointer"],
    ),
    q(
        "git-switch/existing",
        "switch-existing-branch",
        "Switch to an existing branch",
        "The next task belongs on a branch that already exists locally.",
        "Move HEAD to the requested branch without creating a new one.",
        [
            v("switch-docs", "Docs handoff", repo(commits=BRANCH_BASE, branches={"main": "c2", "docs-refresh": "c2"}), ["git switch docs-refresh"], ev({"head_branch": "docs-refresh", "staging_empty": True}, required=["git switch"])),
            v("switch-feature", "Feature handoff", repo(commits=BRANCH_BASE, branches={"main": "c2", "feature/profile": "c2"}), ["git switch feature/profile"], ev({"head_branch": "feature/profile", "staging_empty": True}, required=["git switch"])),
        ],
        checks=[{"label": "HEAD is on the requested existing branch.", "requirement": {"head_branch": "docs-refresh"}}],
        prerequisites=["list-local-branches"],
    ),
    q(
        "git-switch/create",
        "create-and-switch-branch",
        "Create a branch and switch to it",
        "A new task starts now, so the branch should be created and checked out immediately.",
        "Create the requested branch and move HEAD onto it.",
        [
            v("switch-create-auth", "Auth branch", repo(commits=BRANCH_BASE, branches={"main": "c2"}), ["git switch -c feature/auth"], ev({"branch_exists": ["feature/auth"], "head_branch": "feature/auth"}, required=["git switch -c"])),
            v("switch-create-ui", "UI branch", repo(commits=BRANCH_BASE, branches={"main": "c2"}), ["git switch --create feature/ui-polish"], ev({"branch_exists": ["feature/ui-polish"], "head_branch": "feature/ui-polish"}, required=["git switch --create"])),
        ],
        checks=[{"label": "The new branch exists and HEAD is on it.", "requirement": {"branch_exists": ["feature/auth"], "head_branch": "feature/auth"}}],
        prerequisites=["create-branch-pointer"],
    ),
    q(
        "git-checkout/legacy-create",
        "legacy-create-and-switch",
        "Use legacy create-and-switch spelling",
        "An older team note uses the legacy branch command form, and you need to recognize the equivalent operation.",
        "Create the requested branch and move HEAD onto it using the legacy spelling.",
        [
            v("checkout-create-legacy", "Legacy branch", repo(commits=BRANCH_BASE, branches={"main": "c2"}), ["git checkout -b feature/legacy-ui"], ev({"branch_exists": ["feature/legacy-ui"], "head_branch": "feature/legacy-ui"}, required=["git checkout -b"])),
            v("checkout-create-hotfix", "Legacy hotfix", repo(commits=BRANCH_BASE, branches={"main": "c2"}), ["git checkout -b hotfix/navbar c1"], ev({"branch_exists": ["hotfix/navbar"], "head_branch": "hotfix/navbar", "branch_points_to": {"hotfix/navbar": "c1"}}, required=["git checkout -b"])),
        ],
        checks=[{"label": "The branch was created and checked out.", "requirement": {"head_branch": "feature/legacy-ui"}}],
        prerequisites=["create-and-switch-branch"],
    ),
    q(
        "git-switch/detach",
        "inspect-detached-commit",
        "Detach HEAD at a commit for inspection",
        "You need to inspect an older snapshot without moving any branch pointer.",
        "Move HEAD directly to the requested commit while keeping branch pointers unchanged.",
        [
            v("switch-detach-c1", "Inspect c1", repo(commits=BRANCH_BASE, branches={"main": "c2"}), ["git switch --detach c1"], ev({"rules": [{"type": "head_detached_at", "commit": "c1"}], "branch_points_to": {"main": "c2"}}, required=["git switch --detach"])),
            v("switch-detach-c0", "Inspect c0", repo(commits=BRANCH_BASE, branches={"main": "c2"}), ["git switch --detach c0"], ev({"rules": [{"type": "head_detached_at", "commit": "c0"}], "branch_points_to": {"main": "c2"}}, required=["git switch --detach"])),
        ],
        checks=[{"label": "HEAD is detached at the requested commit and main did not move.", "requirement": {"rules": [{"type": "head_detached_at", "commit": "c1"}], "branch_points_to": {"main": "c2"}}}],
        prerequisites=["switch-existing-branch"],
    ),
    q(
        "git-branch/delete",
        "delete-merged-branch",
        "Delete a safe local branch pointer",
        "A branch has already been integrated, so keeping the old local pointer creates clutter.",
        "Remove the requested local branch pointer while staying on the current branch.",
        [
            v("branch-delete-docs", "Delete docs branch", repo(commits=BRANCH_BASE, branches={"main": "c2", "docs-refresh": "c1"}), ["git branch -d docs-refresh"], ev({"branch_absent": ["docs-refresh"], "head_branch": "main"}, required=["git branch -d"])),
            v("branch-delete-old", "Delete old branch", repo(commits=BRANCH_BASE, branches={"main": "c2", "old/navbar": "c1"}), ["git branch --delete old/navbar"], ev({"branch_absent": ["old/navbar"], "head_branch": "main"}, required=["git branch --delete"])),
        ],
        checks=[{"label": "The branch pointer is gone and HEAD stayed put.", "requirement": {"branch_absent": ["docs-refresh"], "head_branch": "main"}}],
        prerequisites=["switch-existing-branch"],
    ),
]

MERGE_BASE = [
    commit("c0", "Initial project", [], {"README.md": "base", "src/app.py": "base"}),
    commit("c1", "Update main shell", ["c0"], {"README.md": "base", "src/app.py": "main shell"}),
    commit("c2", "Add profile feature", ["c0"], {"README.md": "base", "src/app.py": "base", "src/profile.py": "profile"}),
]
CONFLICT_COMMITS = [
    commit("c0", "Initial project", [], {"src/auth.js": "timeout=1000", "README.md": "base"}),
    commit("c1", "Increase timeout on main", ["c0"], {"src/auth.js": "timeout=5000", "README.md": "base"}),
    commit("c2", "Tune timeout on feature", ["c0"], {"src/auth.js": "timeout=2500", "README.md": "base"}),
]
CONFLICT_STATE = repo(
    commits=CONFLICT_COMMITS,
    branches={"main": "c1", "feature/auth-timeout": "c2"},
    conflict_on_merge=True,
    conflict_files=["src/auth.js"],
)
PRECONFLICT = repo(
    commits=CONFLICT_COMMITS,
    branches={"main": "c1", "feature/auth-timeout": "c2"},
    working_tree={"src/auth.js": {"status": "conflicted", "content": "<<<<<<< HEAD\ntimeout=5000\n=======\ntimeout=2500\n>>>>>>> feature/auth-timeout"}},
    conflicts=["src/auth.js"],
    merge_parent="c2",
    conflict_details={"src/auth.js": {"base": "timeout=1000", "ours": "timeout=5000", "theirs": "timeout=2500", "merge_branch": "feature/auth-timeout"}},
)
RESOLVED_MERGE = repo(
    commits=CONFLICT_COMMITS,
    branches={"main": "c1", "feature/auth-timeout": "c2"},
    staging={"src/auth.js": {"status": "modified", "content": "timeout=2500"}},
    conflicts=[],
    merge_parent="c2",
    conflict_details={},
    operation_metadata={"last_merge_branch": "feature/auth-timeout"},
)

ADVENTURE_QUESTS += [
    # Storey 4 â€” Merging and Conflict Resolution
    q(
        "git-merge/branch",
        "merge-fast-forward-branch",
        "Merge a branch that can fast-forward",
        "A feature branch is ahead of main and main has not moved since it split.",
        "Integrate the feature branch into the current branch cleanly.",
        [
            v("merge-ff-profile", "Profile feature", repo(commits=MERGE_BASE, branches={"main": "c0", "feature/profile": "c2"}), ["git merge feature/profile"], ev({"branches_equal": [["main", "feature/profile"]], "rules": [meta_equals("last_merge_fast_forward", True)]}, required=["git merge"])),
            v("merge-ff-maincopy", "Copy feature", repo(commits=[commit("c0", "Initial", [], {"README.md": "base"}), commit("c3", "Improve copy", ["c0"], {"README.md": "better"})], branches={"main": "c0", "feature/copy": "c3"}), ["git merge feature/copy"], ev({"branches_equal": [["main", "feature/copy"]], "rules": [meta_equals("last_merge_fast_forward", True)]}, required=["git merge"])),
        ],
        checks=[{"label": "The current branch now matches the feature branch.", "requirement": {"branches_equal": [["main", "feature/profile"]]}}],
    ),
    q(
        "git-merge/no-ff",
        "merge-with-merge-commit",
        "Force a merge commit",
        "The branch can technically fast-forward, but the team wants a visible merge checkpoint.",
        "Integrate the branch while preserving a merge commit in history.",
        [
            v("merge-noff-profile", "Profile merge checkpoint", repo(commits=MERGE_BASE, branches={"main": "c0", "feature/profile": "c2"}), ["git merge --no-ff feature/profile"], ev({"rules": [{"type": "commit_is_merge", "branch": "main"}, meta_equals("last_merge_no_ff", True)]}, required=["git merge --no-ff"])),
            v("merge-noff-copy", "Copy merge checkpoint", repo(commits=[commit("c0", "Initial", [], {"README.md": "base"}), commit("c3", "Improve copy", ["c0"], {"README.md": "better"})], branches={"main": "c0", "feature/copy": "c3"}), ["git merge --no-ff feature/copy"], ev({"rules": [{"type": "commit_is_merge", "branch": "main"}, meta_equals("last_merge_no_ff", True)]}, required=["git merge --no-ff"])),
        ],
        checks=[{"label": "The latest commit on main is a merge commit.", "requirement": {"rules": [{"type": "commit_is_merge", "branch": "main"}]}}],
        prerequisites=["merge-fast-forward-branch"],
    ),
    q(
        "git-merge/abort",
        "abort-conflicted-merge",
        "Abort a conflicted merge",
        "A merge produced conflicts, and the safest decision is to return to the clean pre-merge state.",
        "Cancel the in-progress merge.",
        [
            v("merge-abort-auth", "Abort auth conflict", PRECONFLICT, ["git merge --abort"], ev({"conflict_free": True, "working_tree_clean": True, "staging_empty": True, "rules": [meta_equals("last_merge_aborted", True)]}, required=["git merge --abort"])),
            v("merge-abort-copy", "Abort copy conflict", {**copy.deepcopy(PRECONFLICT), "conflicts": ["README.md"], "working_tree": {"README.md": {"status": "conflicted", "content": "markers"}}, "conflict_details": {"README.md": {"ours": "main", "theirs": "feature"}}}, ["git merge --abort"], ev({"conflict_free": True, "working_tree_clean": True, "staging_empty": True, "rules": [meta_equals("last_merge_aborted", True)]}, required=["git merge --abort"])),
        ],
        checks=[{"label": "No conflict or staged merge work remains.", "requirement": {"conflict_free": True, "working_tree_clean": True, "staging_empty": True}}],
        prerequisites=["merge-fast-forward-branch"],
    ),
    q(
        "git-checkout/ours",
        "choose-our-conflict-side",
        "Choose our side of a conflict",
        "A conflicted file should keep the current branch version before the resolution is staged.",
        "Replace the conflicted file with the current branch side.",
        [
            v("checkout-ours-auth", "Keep main timeout", PRECONFLICT, ["git checkout --ours src/auth.js"], ev({"conflicts_contain_paths": ["src/auth.js"], "working_tree_contains": ["src/auth.js"], "rules": [{"type": "working_tree_contains_tokens", "path": "src/auth.js", "tokens": ["timeout=5000"]}]}, required=["git checkout --ours"])),
            v("checkout-ours-copy", "Keep main copy", {**copy.deepcopy(PRECONFLICT), "conflict_details": {"src/auth.js": {"ours": "MAIN COPY", "theirs": "FEATURE COPY"}}, "working_tree": {"src/auth.js": {"status": "conflicted", "content": "markers"}}}, ["git checkout --ours src/auth.js"], ev({"conflicts_contain_paths": ["src/auth.js"], "rules": [{"type": "working_tree_contains_tokens", "path": "src/auth.js", "tokens": ["MAIN COPY"]}]}, required=["git checkout --ours"])),
        ],
        checks=[{"label": "The conflicted file now contains the current branch side.", "requirement": {"rules": [{"type": "working_tree_contains_tokens", "path": "src/auth.js", "tokens": ["timeout=5000"]}]}}],
        prerequisites=["merge-fast-forward-branch"],
    ),
    q(
        "git-checkout/theirs",
        "choose-their-conflict-side",
        "Choose their side of a conflict",
        "A conflicted file should take the incoming branch version before the resolution is staged.",
        "Replace the conflicted file with the incoming branch side.",
        [
            v("checkout-theirs-auth", "Take feature timeout", PRECONFLICT, ["git checkout --theirs src/auth.js"], ev({"conflicts_contain_paths": ["src/auth.js"], "working_tree_contains": ["src/auth.js"], "rules": [{"type": "working_tree_contains_tokens", "path": "src/auth.js", "tokens": ["timeout=2500"]}]}, required=["git checkout --theirs"])),
            v("checkout-theirs-copy", "Take feature copy", {**copy.deepcopy(PRECONFLICT), "conflict_details": {"src/auth.js": {"ours": "MAIN COPY", "theirs": "FEATURE COPY"}}, "working_tree": {"src/auth.js": {"status": "conflicted", "content": "markers"}}}, ["git checkout --theirs src/auth.js"], ev({"conflicts_contain_paths": ["src/auth.js"], "rules": [{"type": "working_tree_contains_tokens", "path": "src/auth.js", "tokens": ["FEATURE COPY"]}]}, required=["git checkout --theirs"])),
        ],
        checks=[{"label": "The conflicted file now contains the incoming branch side.", "requirement": {"rules": [{"type": "working_tree_contains_tokens", "path": "src/auth.js", "tokens": ["timeout=2500"]}]}}],
        prerequisites=["merge-fast-forward-branch"],
    ),
    q(
        "git-merge/continue",
        "continue-resolved-merge",
        "Finish a resolved merge",
        "The conflict has already been resolved and staged, so the merge can now be completed.",
        "Finish the in-progress merge.",
        [
            v("merge-continue-auth", "Continue auth merge", RESOLVED_MERGE, ["git merge --continue"], ev({"conflict_free": True, "staging_empty": True, "rules": [{"type": "commit_is_merge", "branch": "main"}]}, required=["git merge --continue"])),
            v("merge-continue-copy", "Continue copy merge", {**copy.deepcopy(RESOLVED_MERGE), "staging": {"README.md": {"status": "modified", "content": "resolved"}}}, ["git merge --continue"], ev({"conflict_free": True, "staging_empty": True, "rules": [{"type": "commit_is_merge", "branch": "main"}]}, required=["git merge --continue"])),
        ],
        checks=[{"label": "The merge is complete and no staged conflict work remains.", "requirement": {"conflict_free": True, "staging_empty": True, "rules": [{"type": "commit_is_merge", "branch": "main"}]}}],
        prerequisites=["choose-our-conflict-side", "choose-their-conflict-side"],
    ),
]

RECOVERY_COMMITS = [
    commit("c0", "Initial project", [], {"README.md": "base", "src/app.py": "v1"}),
    commit("c1", "Add login form", ["c0"], {"README.md": "base", "src/app.py": "v1", "src/login.py": "login"}),
    commit("c2", "Add broken analytics", ["c1"], {"README.md": "base", "src/app.py": "v1", "src/login.py": "login", "src/analytics.py": "broken"}),
]

ADVENTURE_QUESTS += [
    # Storey 5 â€” Undoing and Recovery
    q(
        "git-commit/amend",
        "amend-latest-commit-message",
        "Amend the latest local commit",
        "The latest local commit has the right content but the message is unclear and has not been shared yet.",
        "Replace the latest commit with a clearer message.",
        [
            v("amend-message-copy", "Fix message", repo(commits=[commit("c0", "Initial project", [], BASE_TREE), commit("c1", "wip", ["c0"], {**BASE_TREE, "README.md": "Better intro"})], branches={"main": "c1"}), ["git commit --amend -m 'Update onboarding copy'"], ev({"rules": [{"type": "commit_replaced_by_amend"}, {"type": "latest_commit_message_contains", "branch": "main", "text": "Update onboarding copy"}]}, required=["git commit --amend"])),
            v("amend-message-docs", "Fix docs message", repo(commits=[commit("c0", "Initial project", [], BASE_TREE), commit("c1", "docs", ["c0"], {**BASE_TREE, "docs/guide.md": "Guide"})], branches={"main": "c1"}), ["git commit --amend -m 'Add setup guide'"], ev({"rules": [{"type": "commit_replaced_by_amend"}, {"type": "latest_commit_message_contains", "branch": "main", "text": "Add setup guide"}]}, required=["git commit --amend"])),
        ],
        checks=[{"label": "The latest local commit was replaced.", "requirement": {"rules": [{"type": "commit_replaced_by_amend"}]}}],
    ),
    q(
        "git-reset/hard-head",
        "reset-hard-one-parent",
        "Move back one commit and clean files",
        "The latest local commit is disposable and should be removed with its file changes.",
        "Move the current branch back one parent and clean the working tree.",
        [
            v("reset-head-analytics", "Drop analytics", repo(commits=RECOVERY_COMMITS, branches={"main": "c2"}, working_tree={"scratch.txt": {"status": "untracked", "content": "tmp"}}, staging={"README.md": "staged draft"}), ["git reset --hard HEAD~1"], ev({"rules": [{"type": "branch_moved_to", "branch": "main", "commit": "c1"}], "working_tree_clean": True, "staging_empty": True}, required=["git reset --hard"])),
            v("reset-head-login", "Drop login", repo(commits=RECOVERY_COMMITS[:2], branches={"main": "c1"}, working_tree={"notes.txt": {"status": "untracked", "content": "tmp"}}), ["git reset --hard HEAD~1"], ev({"rules": [{"type": "branch_moved_to", "branch": "main", "commit": "c0"}], "working_tree_clean": True, "staging_empty": True}, required=["git reset --hard"])),
        ],
        checks=[{"label": "The branch moved backward and local dirt is gone.", "requirement": {"working_tree_clean": True, "staging_empty": True, "rules": [meta_equals("last_reset_mode", "hard")]}}],
        prerequisites=["amend-latest-commit-message"],
    ),
    q(
        "git-reset/hard",
        "reset-hard-specific-commit",
        "Reset hard to a named commit",
        "A local branch should return to a specific known-good checkpoint.",
        "Move the branch to the requested commit and clean local changes.",
        [
            v("reset-hard-c0", "Back to base", repo(commits=RECOVERY_COMMITS, branches={"main": "c2"}, working_tree={"src/app.py": "local debug"}), ["git reset --hard c0"], ev({"rules": [{"type": "branch_moved_to", "branch": "main", "commit": "c0"}], "working_tree_clean": True, "staging_empty": True}, required=["git reset --hard"])),
            v("reset-hard-c1", "Back to login", repo(commits=RECOVERY_COMMITS, branches={"main": "c2"}, staging={"README.md": "staged"}), ["git reset --hard c1"], ev({"rules": [{"type": "branch_moved_to", "branch": "main", "commit": "c1"}], "working_tree_clean": True, "staging_empty": True}, required=["git reset --hard"])),
        ],
        checks=[{"label": "The branch now points at the named checkpoint and local changes are clean.", "requirement": {"working_tree_clean": True, "staging_empty": True, "rules": [meta_equals("last_reset_mode", "hard")]}}],
        prerequisites=["reset-hard-one-parent"],
    ),
    q(
        "git-revert/one-commit",
        "revert-shared-commit",
        "Revert a shared commit safely",
        "A bad commit may already be visible to others, so history should be preserved while undoing its effect.",
        "Create a new commit that reverses the requested earlier commit.",
        [
            v("revert-analytics", "Revert analytics", repo(commits=RECOVERY_COMMITS, branches={"main": "c2"}), ["git revert c2"], ev({"rules": [{"type": "new_revert_commit_exists"}, {"type": "revert_preserves_history", "branch": "main", "commit": "c2"}], "min_commits_on_branch": {"main": 4}}, required=["git revert"])),
            v("revert-login", "Revert login", repo(commits=RECOVERY_COMMITS, branches={"main": "c2"}), ["git revert c1"], ev({"rules": [{"type": "new_revert_commit_exists"}, {"type": "revert_preserves_history", "branch": "main", "commit": "c1"}], "min_commits_on_branch": {"main": 4}}, required=["git revert"])),
        ],
        checks=[{"label": "A new revert commit exists and the old commit remains in history.", "requirement": {"rules": [{"type": "new_revert_commit_exists"}]}}],
        prerequisites=["reset-hard-specific-commit"],
    ),
    q(
        "git-revert/no-edit",
        "revert-with-generated-message",
        "Revert using the generated message",
        "A quick rollback should use the standard generated revert message so the reason stays traceable.",
        "Create the revert commit using the generated message.",
        [
            v("revert-noedit-analytics", "Generated analytics revert", repo(commits=RECOVERY_COMMITS, branches={"main": "c2"}), ["git revert --no-edit c2"], ev({"rules": [{"type": "new_revert_commit_exists"}, meta_equals("last_revert_no_edit", True)]}, required=["git revert --no-edit"])),
            v("revert-noedit-login", "Generated login revert", repo(commits=RECOVERY_COMMITS, branches={"main": "c2"}), ["git revert --no-edit c1"], ev({"rules": [{"type": "new_revert_commit_exists"}, meta_equals("last_revert_no_edit", True)]}, required=["git revert --no-edit"])),
        ],
        checks=[{"label": "The generated revert path was used.", "requirement": {"rules": [meta_equals("last_revert_no_edit", True)]}}],
        prerequisites=["revert-shared-commit"],
    ),
    q(
        "git-reflog/head",
        "inspect-reflog-for-recovery",
        "Inspect recent HEAD movements",
        "A branch moved unexpectedly, and the fastest clue is the local movement log.",
        "Inspect recent HEAD movements without changing repository state.",
        [
            v("reflog-after-reset", "After reset", repo(commits=RECOVERY_COMMITS, branches={"main": "c1"}, reflog=[{"ref": "HEAD@{0}", "target": "c2", "message": "commit"}, {"ref": "HEAD@{1}", "target": "c1", "message": "reset: moving to HEAD~1"}]), ["git reflog"], ev({"repository_state_unchanged": True}, required=["git reflog"])),
            v("reflog-after-amend", "After amend", repo(commits=RECOVERY_COMMITS, branches={"main": "c2"}, reflog=[{"ref": "HEAD@{0}", "target": "c1", "message": "commit --amend: replaced c1"}]), ["git reflog"], ev({"repository_state_unchanged": True}, required=["git reflog"])),
        ],
        checks=[{"label": "Reflog was inspected without mutation.", "requirement": {"repository_state_unchanged": True, "required_commands": ["git reflog"]}}],
        prerequisites=["reset-hard-one-parent"],
        min_counted_commands=0,
        max_counted_commands=2,
    ),
]

STASH_REPO = repo(commits=BRANCH_BASE, branches={"main": "c2", "hotfix/navbar": "c1"}, working_tree={"src/app.py": "work in progress", "notes.md": {"status": "untracked", "content": "idea"}})
STASHED_REPO = repo(commits=BRANCH_BASE, branches={"main": "c2"}, stash_stack=[{"message": "WIP on main: c2 Add dashboard", "working_tree": {"src/app.py": "work in progress"}, "staging": {}, "head_commit": "c2"}])
CHERRY_REPO = repo(
    commits=[
        commit("c0", "Initial project", [], {"README.md": "base", "src/app.py": "v1"}),
        commit("c1", "Add docs", ["c0"], {"README.md": "base", "src/app.py": "v1", "docs/guide.md": "guide"}),
        commit("c2", "Patch auth guard", ["c0"], {"README.md": "base", "src/app.py": "v1", "src/auth.py": "guard"}),
    ],
    branches={"main": "c1", "hotfix/auth-guard": "c2"},
)

ADVENTURE_QUESTS += [
    # Storey 6 â€” Temporary Work and Patch Movement
    q(
        "git-stash/push",
        "stash-local-work",
        "Shelve unfinished local work",
        "You need to leave your current branch, but unfinished edits would block the switch.",
        "Shelve the local work and leave the working tree clean.",
        [
            v("stash-app-wip", "App WIP", STASH_REPO, ["git stash"], ev({"working_tree_clean": True, "staging_empty": True, "rules": [{"type": "stash_top_contains", "paths": ["src/app.py", "notes.md"]}]}, required=["git stash"])),
            v("stash-readme-wip", "Readme WIP", repo(commits=BRANCH_BASE, branches={"main": "c2"}, working_tree={"README.md": "draft"}), ["git stash push"], ev({"working_tree_clean": True, "staging_empty": True, "rules": [{"type": "stash_top_contains", "paths": ["README.md"]}]}, required=["git stash"])),
        ],
        checks=[{"label": "Working tree is clean and the shelved work is on top of the stash.", "requirement": {"working_tree_clean": True, "staging_empty": True}}],
    ),
    q(
        "git-stash/list",
        "list-stashed-work",
        "List saved stashes",
        "There may be saved work from earlier; inspect it before applying anything.",
        "Inspect the saved stash entries without changing repository state.",
        [
            v("stash-list-one", "One stash", STASHED_REPO, ["git stash list"], ev({"repository_state_unchanged": True}, required=["git stash list"])),
            v("stash-list-two", "Two stashes", repo(commits=BRANCH_BASE, branches={"main": "c2"}, stash_stack=[{"message": "WIP one", "working_tree": {"a": "1"}, "staging": {}, "head_commit": "c2"}, {"message": "WIP two", "working_tree": {"b": "2"}, "staging": {}, "head_commit": "c2"}]), ["git stash list"], ev({"repository_state_unchanged": True}, required=["git stash list"])),
        ],
        checks=[{"label": "Stash entries were inspected without mutation.", "requirement": {"repository_state_unchanged": True}}],
        prerequisites=["stash-local-work"],
        min_counted_commands=0,
        max_counted_commands=2,
    ),
    q(
        "git-stash/pop",
        "pop-top-stash",
        "Restore and remove the top stash",
        "You are back on the right branch and want the most recent shelved work restored, not kept twice.",
        "Restore the top saved work and remove that stash entry.",
        [
            v("stash-pop-app", "Pop app work", STASHED_REPO, ["git stash pop"], ev({"working_tree_contains": ["src/app.py"], "stash_stack_empty": True, "rules": [{"type": "stash_pop_restored_paths", "paths": ["src/app.py"]}]}, required=["git stash pop"])),
            v("stash-pop-readme", "Pop readme work", repo(commits=BRANCH_BASE, branches={"main": "c2"}, stash_stack=[{"message": "WIP readme", "working_tree": {"README.md": "draft"}, "staging": {}, "head_commit": "c2"}]), ["git stash pop"], ev({"working_tree_contains": ["README.md"], "stash_stack_empty": True, "rules": [{"type": "stash_pop_restored_paths", "paths": ["README.md"]}]}, required=["git stash pop"])),
        ],
        checks=[{"label": "Saved work returned and the stash stack is empty.", "requirement": {"stash_stack_empty": True}}],
        prerequisites=["list-stashed-work"],
    ),
    q(
        "git-stash/apply",
        "apply-top-stash",
        "Restore a stash but keep it saved",
        "You want to try the saved work again while keeping the stash as a backup.",
        "Restore the top saved work without deleting the stash entry.",
        [
            v("stash-apply-app", "Apply app work", STASHED_REPO, ["git stash apply"], ev({"working_tree_contains": ["src/app.py"], "rules": [{"type": "stash_top_contains", "paths": ["src/app.py"]}]}, required=["git stash apply"])),
            v("stash-apply-readme", "Apply readme work", repo(commits=BRANCH_BASE, branches={"main": "c2"}, stash_stack=[{"message": "WIP readme", "working_tree": {"README.md": "draft"}, "staging": {}, "head_commit": "c2"}]), ["git stash apply"], ev({"working_tree_contains": ["README.md"], "rules": [{"type": "stash_top_contains", "paths": ["README.md"]}]}, required=["git stash apply"])),
        ],
        checks=[{"label": "Saved work returned and the stash still exists.", "requirement": {"required_commands": ["git stash apply"]}}],
        prerequisites=["list-stashed-work"],
    ),
    q(
        "git-stash/drop",
        "drop-top-stash",
        "Delete the top stash entry",
        "An old stash is no longer needed and should not be accidentally applied later.",
        "Remove the top stash entry.",
        [
            v("stash-drop-app", "Drop app stash", STASHED_REPO, ["git stash drop"], ev({"stash_stack_empty": True, "rules": [meta_equals("last_stash_operation", "drop")]}, required=["git stash drop"])),
            v("stash-drop-readme", "Drop readme stash", repo(commits=BRANCH_BASE, branches={"main": "c2"}, stash_stack=[{"message": "WIP readme", "working_tree": {"README.md": "draft"}, "staging": {}, "head_commit": "c2"}]), ["git stash drop"], ev({"stash_stack_empty": True, "rules": [meta_equals("last_stash_operation", "drop")]}, required=["git stash drop"])),
        ],
        checks=[{"label": "The top stash entry is gone.", "requirement": {"stash_stack_empty": True}}],
        prerequisites=["list-stashed-work"],
    ),
    q(
        "git-cherry-pick/one-commit",
        "cherry-pick-one-commit",
        "Copy one commit onto the current branch",
        "A useful fix exists on another branch, but the rest of that branch is not ready.",
        "Apply only the requested commit onto the current branch.",
        [
            v("pick-auth-guard", "Auth guard fix", CHERRY_REPO, ["git cherry-pick c2"], ev({"rules": [{"type": "cherry_pick_created_new_commit", "source": "c2"}, {"type": "cherry_pick_copied_changes_from", "source": "c2"}]}, required=["git cherry-pick"])),
            v("pick-docs", "Docs copy", repo(commits=[commit("c0", "Initial", [], {"README.md": "base"}), commit("c1", "Main work", ["c0"], {"README.md": "base", "src/app.py": "v1"}), commit("c2", "Add guide", ["c0"], {"README.md": "base", "docs/guide.md": "guide"})], branches={"main": "c1", "docs/guide": "c2"}), ["git cherry-pick c2"], ev({"rules": [{"type": "cherry_pick_created_new_commit", "source": "c2"}, {"type": "cherry_pick_copied_changes_from", "source": "c2"}]}, required=["git cherry-pick"])),
        ],
        checks=[{"label": "A new commit copied the requested source changes.", "requirement": {"rules": [{"type": "cherry_pick_created_new_commit", "source": "c2"}]}}],
        prerequisites=["stash-local-work"],
    ),
    q(
        "git-cherry-pick/no-commit",
        "cherry-pick-without-commit",
        "Stage a picked commit without committing",
        "You need the changes from another commit, but you want to inspect them before saving a new checkpoint.",
        "Apply the requested commit into staging without creating a commit yet.",
        [
            v("pick-n-auth", "Stage auth guard", CHERRY_REPO, ["git cherry-pick --no-commit c2"], ev({"staging_contains": ["src/auth.py"], "rules": [meta_equals("last_cherry_pick_no_commit", True)]}, required=["git cherry-pick --no-commit"])),
            v("pick-n-docs", "Stage guide", repo(commits=[commit("c0", "Initial", [], {"README.md": "base"}), commit("c1", "Main work", ["c0"], {"README.md": "base", "src/app.py": "v1"}), commit("c2", "Add guide", ["c0"], {"README.md": "base", "docs/guide.md": "guide"})], branches={"main": "c1", "docs/guide": "c2"}), ["git cherry-pick -n c2"], ev({"staging_contains": ["docs/guide.md"], "rules": [meta_equals("last_cherry_pick_no_commit", True)]}, required=["git cherry-pick -n"])),
        ],
        checks=[{"label": "Picked changes are staged and no commit was created automatically.", "requirement": {"rules": [meta_equals("last_cherry_pick_no_commit", True)]}}],
        prerequisites=["cherry-pick-one-commit"],
    ),
]

REMOTE_LOCAL = repo(
    commits=[
        commit("c0", "Initial project", [], {"README.md": "base"}),
        commit("c1", "Local main work", ["c0"], {"README.md": "base", "src/app.py": "local"}),
        commit("r2", "Remote update", ["c1"], {"README.md": "remote update", "src/app.py": "local"}),
    ],
    branches={"main": "c1"},
    remotes={"origin": "https://example.test/team/app.git"},
    remote_branches={"origin/main": "c1"},
    remote_updates={"origin/main": "r2"},
    upstream_tracking={"main": "origin/main"},
)
PUSH_REPO = repo(
    commits=[commit("c0", "Initial project", [], {"README.md": "base"}), commit("c1", "Add feature", ["c0"], {"README.md": "base", "src/feature.py": "feature"})],
    branches={"main": "c0", "feature/payment": "c1"},
    head="feature/payment",
    remotes={"origin": "https://example.test/team/app.git"},
    remote_branches={"origin/main": "c0"},
)

ADVENTURE_QUESTS += [
    # Storey 7 â€” Remotes and Collaboration
    q(
        "git-remote/verbose",
        "inspect-remote-urls",
        "Inspect remote URLs",
        "Before fetching or pushing, confirm which remote endpoint the repository is connected to.",
        "Inspect configured remote URLs without changing repository state.",
        [
            v("remote-v-origin", "Origin remote", repo(commits=BASE, remotes={"origin": "https://example.test/team/app.git"}), ["git remote -v"], ev({"repository_state_unchanged": True}, required=["git remote -v"])),
            v("remote-v-upstream", "Upstream remote", repo(commits=BASE, remotes={"origin": "https://example.test/fork/app.git", "upstream": "https://example.test/team/app.git"}), ["git remote -v"], ev({"repository_state_unchanged": True}, required=["git remote -v"])),
        ],
        checks=[{"label": "Remote URLs were inspected without mutation.", "requirement": {"repository_state_unchanged": True, "required_commands": ["git remote -v"]}}],
        min_counted_commands=0,
        max_counted_commands=2,
    ),
    q(
        "git-fetch/origin",
        "fetch-origin-updates",
        "Fetch remote updates safely",
        "The remote may have new work, but you do not want to move your local branch yet.",
        "Update remote-tracking information while leaving the local branch where it is.",
        [
            v("fetch-origin-main", "Fetch main", REMOTE_LOCAL, ["git fetch origin"], ev({"remote_branch_exists": ["origin/main"], "rules": [{"type": "fetch_updated_remote_tracking_without_moving_local", "branch": "main"}]}, required=["git fetch"])),
            v("fetch-default-main", "Fetch default", REMOTE_LOCAL, ["git fetch"], ev({"remote_branch_exists": ["origin/main"], "rules": [{"type": "fetch_updated_remote_tracking_without_moving_local", "branch": "main"}]}, required=["git fetch"])),
        ],
        checks=[{"label": "Remote tracking updated and the local branch stayed still.", "requirement": {"remote_tracking_updated": True}}],
        prerequisites=["inspect-remote-urls"],
    ),
    q(
        "git-fetch/prune",
        "fetch-and-prune-stale-refs",
        "Fetch and prune stale remote refs",
        "A deleted remote branch is still showing locally and should be cleaned from remote-tracking refs.",
        "Update remote-tracking information and remove stale refs.",
        [
            v("fetch-prune-old", "Prune old feature", repo(commits=BASE, remotes={"origin": "https://example.test/team/app.git"}, remote_branches={"origin/main": "c0", "origin/old-feature": "c0"}, remote_stale_branches=["old-feature"]), ["git fetch --prune"], ev({"remote_branch_absent": ["origin/old-feature"], "remote_tracking_updated": True}, required=["git fetch --prune"])),
            v("fetch-prune-bug", "Prune bugfix", repo(commits=BASE, remotes={"origin": "https://example.test/team/app.git"}, remote_branches={"origin/main": "c0", "origin/bugfix/old": "c0"}, remote_stale_branches=["origin/bugfix/old"]), ["git fetch -p origin"], ev({"remote_branch_absent": ["origin/bugfix/old"], "remote_tracking_updated": True}, required=["git fetch -p"])),
        ],
        checks=[{"label": "The stale remote-tracking branch is gone.", "requirement": {"remote_tracking_updated": True}}],
        prerequisites=["fetch-origin-updates"],
    ),
    q(
        "git-pull/default",
        "pull-fast-forward-update",
        "Pull upstream work into the current branch",
        "Remote main has a new commit, and your local main can fast-forward cleanly.",
        "Integrate the upstream update into the current branch.",
        [
            v("pull-main-update", "Pull main update", REMOTE_LOCAL, ["git pull"], ev({"rules": [{"type": "pull_moved_local_to_upstream", "branch": "main", "upstream": "origin/main"}], "remote_tracking_updated": True}, required=["git pull"])),
            v("pull-origin-main", "Pull explicit main", REMOTE_LOCAL, ["git pull origin main"], ev({"rules": [{"type": "pull_moved_local_to_upstream", "branch": "main", "upstream": "origin/main"}], "remote_tracking_updated": True}, required=["git pull"])),
        ],
        checks=[{"label": "The local branch now matches its upstream.", "requirement": {"rules": [{"type": "pull_moved_local_to_upstream", "branch": "main", "upstream": "origin/main"}]}}],
        prerequisites=["fetch-origin-updates"],
    ),
    q(
        "git-pull/rebase",
        "pull-with-rebase",
        "Pull with rebase",
        "Your local branch has work while the remote has advanced; the team wants a linear replay on top of upstream.",
        "Integrate upstream using rebase mode.",
        [
            v("pull-rebase-main", "Rebase local work", repo(commits=[commit("c0", "Initial", [], {"README.md": "base"}), commit("c1", "Remote setup", ["c0"], {"README.md": "remote"}), commit("c2", "Local note", ["c0"], {"README.md": "base", "notes.md": "local"})], branches={"main": "c2"}, remotes={"origin": "https://example.test/team/app.git"}, remote_branches={"origin/main": "c1"}, upstream_tracking={"main": "origin/main"}), ["git pull --rebase"], ev({"rules": [meta_equals("pull_strategy", "rebase"), meta_equals("pull_rebased_onto", "c1")], "remote_tracking_updated": True}, required=["git pull --rebase"])),
            v("pull-rebase-explicit", "Rebase explicit", repo(commits=[commit("c0", "Initial", [], {"README.md": "base"}), commit("c1", "Remote setup", ["c0"], {"README.md": "remote"}), commit("c2", "Local note", ["c0"], {"README.md": "base", "notes.md": "local"})], branches={"main": "c2"}, remotes={"origin": "https://example.test/team/app.git"}, remote_branches={"origin/main": "c1"}, upstream_tracking={"main": "origin/main"}), ["git pull --rebase origin main"], ev({"rules": [meta_equals("pull_strategy", "rebase"), meta_equals("pull_rebased_onto", "c1")], "remote_tracking_updated": True}, required=["git pull --rebase"])),
        ],
        checks=[{"label": "The pull used rebase mode.", "requirement": {"rules": [meta_equals("pull_strategy", "rebase")]}}],
        prerequisites=["pull-fast-forward-update"],
    ),
    q(
        "git-push/upstream",
        "push-and-set-upstream",
        "Publish a new branch and set upstream",
        "A local feature branch is ready for review, and future pushes should know its upstream.",
        "Publish the branch to origin and set tracking.",
        [
            v("push-u-payment", "Publish payment branch", PUSH_REPO, ["git push -u origin feature/payment"], ev({"upstream_tracking": {"feature/payment": "origin/feature/payment"}, "rules": [{"type": "push_moved_remote_to_local_tip", "branch": "feature/payment", "remote_branch": "origin/feature/payment"}]}, required=["git push -u"])),
            v("push-u-profile", "Publish profile branch", repo(commits=PUSH_REPO["commits"], branches={"main": "c0", "feature/profile": "c1"}, head="feature/profile", remotes={"origin": "https://example.test/team/app.git"}, remote_branches={"origin/main": "c0"}), ["git push --set-upstream origin feature/profile"], ev({"upstream_tracking": {"feature/profile": "origin/feature/profile"}, "rules": [{"type": "push_moved_remote_to_local_tip", "branch": "feature/profile", "remote_branch": "origin/feature/profile"}]}, required=["git push --set-upstream"])),
        ],
        checks=[{"label": "The remote branch matches local work and upstream tracking is set.", "requirement": {"required_commands": ["git push"]}}],
        prerequisites=["inspect-remote-urls"],
    ),
    q(
        "git-push/current",
        "push-current-branch",
        "Push a tracked branch",
        "The branch already tracks a remote branch, so the new local commit can be published directly.",
        "Publish the current branch to its remote counterpart.",
        [
            v("push-current-main", "Push main", repo(commits=PUSH_REPO["commits"], branches={"main": "c1"}, remotes={"origin": "https://example.test/team/app.git"}, remote_branches={"origin/main": "c0"}, upstream_tracking={"main": "origin/main"}), ["git push"], ev({"rules": [{"type": "push_moved_remote_to_local_tip", "branch": "main", "remote_branch": "origin/main"}]}, required=["git push"])),
            v("push-current-feature", "Push feature", {**copy.deepcopy(PUSH_REPO), "upstream_tracking": {"feature/payment": "origin/feature/payment"}, "remote_branches": {"origin/main": "c0", "origin/feature/payment": "c0"}}, ["git push"], ev({"rules": [{"type": "push_moved_remote_to_local_tip", "branch": "feature/payment", "remote_branch": "origin/feature/payment"}]}, required=["git push"])),
        ],
        checks=[{"label": "The remote branch now points to the local tip.", "requirement": {"required_commands": ["git push"]}}],
        prerequisites=["push-and-set-upstream"],
    ),
    q(
        "git-push/force-with-lease",
        "force-with-lease-after-rewrite",
        "Force safely after local rewrite",
        "A local branch was intentionally rewritten, and the safer force mode should update the remote.",
        "Publish the rewritten local tip with lease protection.",
        [
            v("push-lease-feature", "Lease feature", {**copy.deepcopy(PUSH_REPO), "remote_branches": {"origin/main": "c0", "origin/feature/payment": "old1"}, "upstream_tracking": {"feature/payment": "origin/feature/payment"}}, ["git push --force-with-lease"], ev({"rules": [meta_equals("force_push_with_lease", True), {"type": "push_moved_remote_to_local_tip", "branch": "feature/payment", "remote_branch": "origin/feature/payment"}]}, required=["git push --force-with-lease"])),
            v("push-lease-main", "Lease main", repo(commits=PUSH_REPO["commits"], branches={"main": "c1"}, remotes={"origin": "https://example.test/team/app.git"}, remote_branches={"origin/main": "old1"}, upstream_tracking={"main": "origin/main"}), ["git push --force-with-lease origin main"], ev({"rules": [meta_equals("force_push_with_lease", True), {"type": "push_moved_remote_to_local_tip", "branch": "main", "remote_branch": "origin/main"}]}, required=["git push --force-with-lease"])),
        ],
        checks=[{"label": "The push used lease-protected force mode.", "requirement": {"rules": [meta_equals("force_push_with_lease", True)]}}],
        prerequisites=["push-current-branch"],
    ),
    q(
        "git-push/delete",
        "delete-remote-branch",
        "Delete a remote branch",
        "A review branch was merged and should be removed from the remote list.",
        "Delete the requested branch from origin.",
        [
            v("push-del-payment", "Delete payment remote", repo(commits=PUSH_REPO["commits"], branches={"main": "c1"}, remotes={"origin": "https://example.test/team/app.git"}, remote_branches={"origin/main": "c1", "origin/feature/payment": "c1"}), ["git push origin --delete feature/payment"], ev({"remote_branch_absent": ["origin/feature/payment"], "rules": [meta_equals("remote_branch_deleted", "feature/payment")]}, required=["git push"])),
            v("push-del-profile", "Delete profile remote", repo(commits=PUSH_REPO["commits"], branches={"main": "c1"}, remotes={"origin": "https://example.test/team/app.git"}, remote_branches={"origin/main": "c1", "origin/feature/profile": "c1"}), ["git push origin --delete feature/profile"], ev({"remote_branch_absent": ["origin/feature/profile"], "rules": [meta_equals("remote_branch_deleted", "feature/profile")]}, required=["git push"])),
        ],
        checks=[{"label": "The requested remote branch is gone.", "requirement": {"required_commands": ["git push"]}}],
        prerequisites=["push-and-set-upstream"],
    ),
]
