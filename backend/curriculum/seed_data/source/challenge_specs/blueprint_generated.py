"""Blueprint-generated challenge scenarios."""

from __future__ import annotations

from .helpers import *  # noqa: F403

_BP_CHAPTER_COPY = {
    1: {
        "summary": "Build a repository whose first history is intentional, inspectable, and free of generated noise.",
        "narrative": "Repository foundations are the point where a project becomes auditable instead of just a folder of files.",
        "scene": "A teammate has handed you a starter project right before the first review.",
        "focus": "initialization, cloning, inspection, identity, ignore rules, and the first clean commits",
        "target": "a clean initialized or cloned repository with only the intended project files in history",
        "risk": "A careless first commit teaches the project to trust noise as if it were source.",
    },
    2: {
        "summary": "Shape the index so each commit contains the right work and leaves the rest behind.",
        "narrative": "Clean snapshots come from choosing what enters the index, repairing mistakes, and committing with restraint.",
        "scene": "A feature patch arrived with finished work, scratch notes, and a few index mistakes tangled together.",
        "focus": "selective staging, restore, rm, cached removal, amend, and commit discipline",
        "target": "one or more clean commits whose tree matches the selected work and leaves local drafts local",
        "risk": "A broad add or rushed amend can turn scratch work into permanent history.",
    },
    3: {
        "summary": "Create, move, inspect, and clean branch pointers without losing useful work.",
        "narrative": "Branching is pointer management under pressure: know where HEAD is, name useful work, and delete only what is safe.",
        "scene": "The release lead needs the branch map cleaned up before more work is based on it.",
        "focus": "branch creation, switching, detached inspection, branch cleanup, and graph reading",
        "target": "the requested branch or cleanup state with HEAD on the intended ref",
        "risk": "The wrong pointer move can hide work or leave the player on the wrong line of history.",
    },
    4: {
        "summary": "Integrate branches and resolve conflicts by reading the graph and the conflicted index.",
        "narrative": "Merging is not a single command; it is a graph decision followed by careful conflict evidence when histories overlap.",
        "scene": "Two teammates finished overlapping branch work and need a reliable integration.",
        "focus": "merge shape, merge-base, abort, conflict inspection, side selection, and merge continuation",
        "target": "an integrated history with conflicts resolved or a deliberate abort that restores the pre-merge state",
        "risk": "Guessing during a conflict can commit the wrong side while the graph looks successful.",
    },
    5: {
        "summary": "Recover from bad history moves using the right private or shared undo strategy.",
        "narrative": "Recovery work starts by deciding whether to move a private ref or add a public correcting commit.",
        "scene": "A mistaken change has landed in history and the team needs the repair to match how public that history is.",
        "focus": "reflog reading, hard reset, backup branches, revert, and recovery choice",
        "target": "a repaired branch tip or a new revert commit with the intended tree",
        "risk": "Resetting shared work erases the evidence teammates need; reverting private work leaves avoidable clutter.",
    },
    6: {
        "summary": "Shelve, restore, and transplant work without mixing unrelated changes.",
        "narrative": "Temporary work and patch movement let useful changes travel without dragging the whole branch with them.",
        "scene": "An urgent fix needs to move while unfinished local work is still sitting in the workspace.",
        "focus": "stash, stash restore, cherry-pick, no-commit picks, abort, and follow-up commits",
        "target": "the selected patch or restored WIP committed on the intended branch",
        "risk": "A rushed stash or pick can either lose local work or commit more history than the task asked for.",
    },
    7: {
        "summary": "Coordinate local and remote refs through fetch, pull, push, cleanup, and safe rewrite publication.",
        "narrative": "Remote collaboration is ref negotiation: inspect before integrating, publish deliberately, and use leases for rewrites.",
        "scene": "The remote has changed while local work still needs to be published safely.",
        "focus": "remote inspection, fetch, prune, pull, pull --rebase, push, upstreams, force-with-lease, and remote deletion",
        "target": "local and remote refs aligned with the requested collaboration outcome",
        "risk": "Publishing without checking remote state can overwrite or expose the wrong work.",
    },
}

_BP_DIFFICULTY_COPY = {
    "easy": {
        "before": "one small repository mismatch and no competing local work",
        "task": "make the smallest valid graph, ref, index, or remote change",
    },
    "medium": {
        "before": "enough history, refs, or workspace state that you need to inspect before acting",
        "task": "combine the chapter move with earlier inspection and cleanup habits",
    },
    "hard": {
        "before": "multiple plausible paths, extra context refs or notes, and very little scaffolding",
        "task": "choose the full command sequence from repository state alone",
    },
}

def _bp_trial_copy(chapter: int, difficulty: str) -> dict[str, str]:
    chapter_copy = _BP_CHAPTER_COPY[chapter]
    difficulty_copy = _BP_DIFFICULTY_COPY[difficulty]
    return {
        "story": chapter_copy["scene"],
        "task": f"{difficulty_copy['task'].capitalize()} using {chapter_copy['focus']}.",
        "before": difficulty_copy["before"],
        "after": chapter_copy["target"],
        "current": "",
        "risk": chapter_copy["risk"],
        "concept": chapter_copy["focus"],
    }

def _bp_variant_entry(case_id: str, label: str, spec: dict[str, Any]) -> dict[str, Any]:
    return variant(
        case_id,
        label,
        story=spec["story"],
        task=spec["task"],
        before=spec["before"],
        after=spec["after"],
        current=spec.get("current"),
        risk=spec.get("risk"),
        initial=spec["initial"],
        solution=spec["solution"],
        workspace_files=spec.get("workspace_files"),
        evaluation=_contract(
            spec["state_requirements"],
            required=spec.get("required"),
            graph={"from": spec["before"], "to": spec["after"]},
            concepts=spec.get("concepts"),
        ),
    )

def _bp_trial(chapter: int, difficulty: str, uses: list[str], variant_a: dict[str, Any], variant_b: dict[str, Any]) -> dict[str, Any]:
    case_id = f"ch{chapter}-challenge-{difficulty}"
    wrapper = _bp_trial_copy(chapter, difficulty)
    max_len = max(len(variant_a["solution"]), len(variant_b["solution"]))
    return level(
        difficulty,
        story=wrapper["story"],
        task=wrapper["task"],
        before=wrapper["before"],
        after=wrapper["after"],
        current=wrapper["current"],
        risk=wrapper["risk"],
        uses_adventure_levels=uses,
        min_counted_commands=1,
        max_counted_commands=max(6, max_len + 3),
        variants=[
            _bp_variant_entry(case_id, f"Chapter {chapter} {difficulty.title()} A", variant_a),
            _bp_variant_entry(f"{case_id}-alt", f"Chapter {chapter} {difficulty.title()} B", variant_b),
        ],
    )

def _blueprint_challenges() -> list[dict[str, Any]]:
    specs = []
    for module, slug, title, _trial_ids in BLUEPRINT_CHALLENGE_SPECS:
        chapter = int(slug[2])
        if chapter == 1:
            trials = [
                _bp_trial(
                    1,
                    "easy",
                    ["ch1-adv-init-current-folder", "ch1-adv-stage-one-file", "ch1-adv-commit-staged-snapshot"],
                    {
                        "story": "A brand-new CLI tool folder has a README and a starter script, but no repository yet.",
                        "task": "Turn the folder into a repository and make one clean commit containing both starter files.",
                        "before": "an empty folder with README.md and src/cli.py, no Git metadata",
                        "after": "main -> c0 containing both files; working tree and index clean",
                        "initial": uninitialized({"README.md": "A small CLI tool.\n", "src/cli.py": "def main():\n    pass\n"}),
                        "solution": ["git init", "git status", "git add .", "git commit -m 'Initial commit'"],
                        "required": ["git init", "git add", "git commit"],
                        "state_requirements": {
                            "repository_initialized": True,
                            "latest_commit": {"branch": "main", "contains_paths": ["README.md", "src/cli.py"], "message_contains": ["Initial commit"]},
                            "working_tree_clean": True,
                            "staging_empty": True,
                        },
                        "concepts": ["git init", "git add", "git commit"],
                    },
                    {
                        "story": "A brand-new documentation site folder has a README and a starter index page, but no repository yet.",
                        "task": "Turn the folder into a repository and make one clean commit containing both starter files.",
                        "before": "an empty folder with README.md and docs/index.md, no Git metadata",
                        "after": "main -> c0 containing both files; working tree and index clean",
                        "initial": uninitialized({"README.md": "A small documentation site.\n", "docs/index.md": "# Welcome\n"}),
                        "solution": ["git init", "git status", "git add .", "git commit -m 'Initial commit'"],
                        "required": ["git init", "git add", "git commit"],
                        "state_requirements": {
                            "repository_initialized": True,
                            "latest_commit": {"branch": "main", "contains_paths": ["README.md", "docs/index.md"], "message_contains": ["Initial commit"]},
                            "working_tree_clean": True,
                            "staging_empty": True,
                        },
                        "concepts": ["git init", "git add", "git commit"],
                    },
                ),
                _bp_trial(
                    1,
                    "medium",
                    ["ch1-adv-init-first-branch", "ch1-adv-set-user-name", "ch1-adv-set-user-email", "ch1-adv-write-ignore-rule"],
                    {
                        "story": "A Python app's source and tests both need saving, but a noisy build.log must never enter history.",
                        "task": "Initialize on main, confirm your identity, verify the noise is ignored, then save the app and its tests as two separate commits.",
                        "before": "uninitialized folder with app.py, tests/test_app.py, an untracked .gitignore, and ignored build.log",
                        "after": "main -> c0(app.py) -> c1(tests/test_app.py); build.log never committed",
                        "initial": uninitialized({
                            "app.py": "print('run')\n",
                            "tests/test_app.py": "def test_ok():\n    assert True\n",
                            ".gitignore": {"status": "untracked", "content": "*.log\n"},
                            "build.log": {"status": "ignored", "content": "noise\n"},
                        }),
                        "solution": [
                            "git init -b main",
                            "git config --global user.name Reviewer",
                            "git config --global user.email reviewer@example.test",
                            "git status --ignored",
                            "git add .gitignore app.py",
                            "git commit -m 'Add app'",
                            "git add tests/test_app.py",
                            "git commit -m 'Add tests'",
                        ],
                        "required": ["git init", "git config --global user.name", "git config --global user.email", "git status --ignored", "git commit"],
                        "state_requirements": {
                            "repository_initialized": True,
                            "head_branch": "main",
                            "latest_commit": {"branch": "main", "contains_paths": ["tests/test_app.py"], "message_contains": ["Add tests"]},
                            "staging_empty": True,
                            "rules": [
                                {"type": "commit_count_equals", "count": 2},
                                {"type": "commit_tree_excludes", "commit": "c1", "paths": ["build.log"]},
                            ],
                        },
                        "concepts": ["git init -b", "git config --global", "git status --ignored", "git add", "git commit"],
                    },
                    {
                        "story": "A web widget's source and tests both need saving, but a noisy widget.log must never enter history.",
                        "task": "Initialize on main, confirm your identity, verify the noise is ignored, then save the widget and its tests as two separate commits.",
                        "before": "uninitialized folder with widget.js, tests/test_widget.js, an untracked .gitignore, and ignored widget.log",
                        "after": "main -> c0(widget.js) -> c1(tests/test_widget.js); widget.log never committed",
                        "initial": uninitialized({
                            "widget.js": "export function render() {}\n",
                            "tests/test_widget.js": "test('renders', () => {})\n",
                            ".gitignore": {"status": "untracked", "content": "*.log\n"},
                            "widget.log": {"status": "ignored", "content": "noise\n"},
                        }),
                        "solution": [
                            "git init -b main",
                            "git config --global user.name Reviewer",
                            "git config --global user.email reviewer@example.test",
                            "git status --ignored",
                            "git add .gitignore widget.js",
                            "git commit -m 'Add widget'",
                            "git add tests/test_widget.js",
                            "git commit -m 'Add widget tests'",
                        ],
                        "required": ["git init", "git config --global user.name", "git config --global user.email", "git status --ignored", "git commit"],
                        "state_requirements": {
                            "repository_initialized": True,
                            "head_branch": "main",
                            "latest_commit": {"branch": "main", "contains_paths": ["tests/test_widget.js"], "message_contains": ["Add widget tests"]},
                            "staging_empty": True,
                            "rules": [
                                {"type": "commit_count_equals", "count": 2},
                                {"type": "commit_tree_excludes", "commit": "c1", "paths": ["widget.log"]},
                            ],
                        },
                        "concepts": ["git init -b", "git config --global", "git status --ignored", "git add", "git commit"],
                    },
                ),
                _bp_trial(
                    1,
                    "hard",
                    ["ch1-adv-clone-specific-branch", "ch1-adv-compact-and-script-status", "ch1-adv-graph-history", "ch1-adv-show-commit"],
                    {
                        "story": "A teammate's release repository keeps its pending fix on a hotfix branch, not the default branch.",
                        "task": "Clone that exact branch and confirm precisely what it contains before trusting it.",
                        "before": "remote with main and hotfix branches; hotfix has one commit main does not",
                        "after": "hotfix branch cloned locally; its pending-fix commit inspected and confirmed",
                        "initial": uninitialized({}, remote_fixtures={
                            "branches": {"origin/main": "r1", "origin/hotfix": "r2"},
                            "default_branch": "origin/main",
                            "commits": [
                                commit("r1", "Base release", [], {"README.md": "release v1\n"}),
                                commit("r2", "Prep hotfix branch", ["r1"], {"README.md": "release v1\n", "hotfix.md": "pending fix\n"}),
                            ],
                        }),
                        "solution": [
                            "git clone -b hotfix https://example.test/team/app.git",
                            "git status -s",
                            "git log --oneline --graph --all",
                            "git show --name-only r2",
                        ],
                        "required": ["git clone -b", "git status -s", "git log", "git show --name-only"],
                        "state_requirements": {
                            "repository_initialized": True,
                            "head_branch": "hotfix",
                            "latest_commit": {"branch": "hotfix", "contains_paths": ["hotfix.md"], "message_contains": ["Prep hotfix branch"]},
                            "staging_empty": True,
                            "working_tree_clean": True,
                            "rules": [{"type": "commit_count_equals", "count": 2}],
                        },
                        "concepts": ["git clone -b", "git status -s", "git log --graph --all", "git show --name-only"],
                    },
                    {
                        "story": "A teammate's project keeps its pending release notes on a release-docs branch, not the default branch.",
                        "task": "Clone that exact branch and confirm precisely what it contains before trusting it.",
                        "before": "remote with main and release-docs branches; release-docs has one commit main does not",
                        "after": "release-docs branch cloned locally; its pending-notes commit inspected and confirmed",
                        "initial": uninitialized({}, remote_fixtures={
                            "branches": {"origin/main": "r1", "origin/release-docs": "r2"},
                            "default_branch": "origin/main",
                            "commits": [
                                commit("r1", "Base project", [], {"README.md": "project v1\n"}),
                                commit("r2", "Prep release docs branch", ["r1"], {"README.md": "project v1\n", "RELEASE.md": "pending notes\n"}),
                            ],
                        }),
                        "solution": [
                            "git clone -b release-docs https://example.test/team/app.git",
                            "git status -s",
                            "git log --oneline --graph --all",
                            "git show --name-only r2",
                        ],
                        "required": ["git clone -b", "git status -s", "git log", "git show --name-only"],
                        "state_requirements": {
                            "repository_initialized": True,
                            "head_branch": "release-docs",
                            "latest_commit": {"branch": "release-docs", "contains_paths": ["RELEASE.md"], "message_contains": ["Prep release docs branch"]},
                            "staging_empty": True,
                            "working_tree_clean": True,
                            "rules": [{"type": "commit_count_equals", "count": 2}],
                        },
                        "concepts": ["git clone -b", "git status -s", "git log --graph --all", "git show --name-only"],
                    },
                ),
            ]
        elif chapter == 2:
            trials = [
                _bp_trial(
                    2,
                    "easy",
                    ["ch2-adv-changed-paths-only", "ch2-adv-repair-before-commit"],
                    {
                        "story": "A UI copy fix, a stray debug edit, and an untracked scratch file are all sitting in the same worktree.",
                        "task": "Inspect the changes, discard the debug edit, and commit only the real UI copy fix.",
                        "before": "main -> c0; src/app.py has a real fix, src/debug.py has a debug edit, scratch.txt is untracked",
                        "after": "main -> c1 with only the UI copy fix; debug edit discarded; scratch.txt still untracked",
                        "initial": repo(
                            commits=[commit("c0", "Initial", [], {"README.md": "base\n", "src/app.py": "v1\n", "src/debug.py": "prod\n"})],
                            working_tree={
                                "src/app.py": {"status": "modified", "content": "v1 fixed copy\n"},
                                "src/debug.py": {"status": "modified", "content": "debug=True\n"},
                                "scratch.txt": {"status": "untracked", "content": "local notes\n"},
                            },
                        ),
                        "solution": ["git status", "git diff --name-only", "git restore src/debug.py", "git add src/app.py", "git commit -m 'Fix UI copy'"],
                        "required": ["git status", "git diff --name-only", "git restore", "git add", "git commit"],
                        "state_requirements": {
                            "latest_commit": {"branch": "main", "contains_paths": ["src/app.py"], "excludes_paths": ["src/debug.py"], "message_contains": ["Fix UI copy"]},
                            "staging_empty": True,
                            "rules": [{"type": "working_tree_clean_except", "paths": ["scratch.txt"]}],
                        },
                        "concepts": ["git status", "git diff --name-only", "git restore", "git add", "git commit"],
                    },
                    {
                        "story": "A config typo fix, a stray debug-logging edit, and an untracked notes file are all sitting in the same worktree.",
                        "task": "Inspect the changes, discard the debug edit, and commit only the real config typo fix.",
                        "before": "main -> c0; config.yaml has a real fix, logging.py has a debug edit, notes.tmp is untracked",
                        "after": "main -> c1 with only the config typo fix; debug edit discarded; notes.tmp still untracked",
                        "initial": repo(
                            commits=[commit("c0", "Initial", [], {"README.md": "base\n", "config.yaml": "port: 8080\n", "logging.py": "level=INFO\n"})],
                            working_tree={
                                "config.yaml": {"status": "modified", "content": "port: 8081\n"},
                                "logging.py": {"status": "modified", "content": "level=DEBUG\n"},
                                "notes.tmp": {"status": "untracked", "content": "scratch\n"},
                            },
                        ),
                        "solution": ["git status", "git diff --name-only", "git restore logging.py", "git add config.yaml", "git commit -m 'Fix config typo'"],
                        "required": ["git status", "git diff --name-only", "git restore", "git add", "git commit"],
                        "state_requirements": {
                            "latest_commit": {"branch": "main", "contains_paths": ["config.yaml"], "excludes_paths": ["logging.py"], "message_contains": ["Fix config typo"]},
                            "staging_empty": True,
                            "rules": [{"type": "working_tree_clean_except", "paths": ["notes.tmp"]}],
                        },
                        "concepts": ["git status", "git diff --name-only", "git restore", "git add", "git commit"],
                    },
                ),
                _bp_trial(
                    2,
                    "medium",
                    ["ch2-adv-untrack-generated-directory", "ch2-adv-amend-message-or-content"],
                    {
                        "story": "The latest commit accidentally tracked a generated bundle and forgot a real source file.",
                        "task": "Untrack the generated file, add the forgotten one, and repair the commit in place.",
                        "before": "main -> c1(app+bundle); dist/bundle.js tracked by mistake, src/utils.py still untracked",
                        "after": "main -> amended c1 with src/utils.py and .gitignore; dist/bundle.js no longer tracked",
                        "initial": repo(
                            commits=[
                                commit("c0", "Initial", [], {"README.md": "base\n"}),
                                commit("c1", "Add feature", ["c0"], {"README.md": "base\n", "src/feature.py": "v1\n", "dist/bundle.js": "built\n"}),
                            ],
                            branches={"main": "c1"},
                            working_tree={
                                "src/utils.py": {"status": "untracked", "content": "def helper():\n    pass\n"},
                                ".gitignore": {"status": "untracked", "content": "dist/\n"},
                            },
                        ),
                        "solution": ["git rm --cached dist/bundle.js", "git add .gitignore src/utils.py", "git commit --amend --no-edit", "git status"],
                        "required": ["git rm --cached", "git add", "git commit --amend"],
                        "state_requirements": {
                            "latest_commit": {"branch": "main", "contains_paths": ["src/utils.py", ".gitignore"], "excludes_paths": ["dist/bundle.js"]},
                            "staging_empty": True,
                            "rules": [{"type": "branch_tip_replaces_commit", "branch": "main", "old": "c1"}],
                        },
                        "concepts": ["git rm --cached", "git add", "git commit --amend --no-edit"],
                    },
                    {
                        "story": "The latest commit accidentally tracked a local settings file and forgot a real source file.",
                        "task": "Untrack the local settings file, add the forgotten one, and repair the commit in place.",
                        "before": "main -> c1(settings); local.settings.json tracked by mistake, src/settings_view.py still untracked",
                        "after": "main -> amended c1 with src/settings_view.py and .gitignore; local.settings.json no longer tracked",
                        "initial": repo(
                            commits=[
                                commit("c0", "Initial", [], {"README.md": "base\n"}),
                                commit("c1", "Add settings screen", ["c0"], {"README.md": "base\n", "src/settings.py": "v1\n", "local.settings.json": "{\"secret\": true}\n"}),
                            ],
                            branches={"main": "c1"},
                            working_tree={
                                "src/settings_view.py": {"status": "untracked", "content": "class View:\n    pass\n"},
                                ".gitignore": {"status": "untracked", "content": "local.settings.json\n"},
                            },
                        ),
                        "solution": ["git rm --cached local.settings.json", "git add .gitignore src/settings_view.py", "git commit --amend --no-edit", "git status"],
                        "required": ["git rm --cached", "git add", "git commit --amend"],
                        "state_requirements": {
                            "latest_commit": {"branch": "main", "contains_paths": ["src/settings_view.py", ".gitignore"], "excludes_paths": ["local.settings.json"]},
                            "staging_empty": True,
                            "rules": [{"type": "branch_tip_replaces_commit", "branch": "main", "old": "c1"}],
                        },
                        "concepts": ["git rm --cached", "git add", "git commit --amend --no-edit"],
                    },
                ),
                _bp_trial(
                    2,
                    "hard",
                    ["ch2-adv-cleanup-repo-workflow", "ch2-adv-shape-two-snapshots", "ch2-adv-repair-before-commit"],
                    {
                        "story": "A web app's workspace has a half-finished feature, an obsolete helper, a generated build directory tracked by mistake, and a leftover debug hunk all mixed together.",
                        "task": "Split this mess into two clean commits: the real feature first, then the cleanup and documentation, discarding the debug leftovers.",
                        "before": "main -> c0; mixed additions, a tracked deletion, a tracked generated dir, and a partial hunk in src/app.py",
                        "after": "main -> c0 -> c1(feature) -> c2(cleanup+docs); old_helper.py and dist/ removed from history; debug hunk discarded",
                        "initial": repo(
                            commits=[commit("c0", "Initial", [], {"README.md": "base\n", "src/app.py": "v1\n", "old_helper.py": "legacy\n", "dist/bundle.js": "built\n"})],
                            working_tree={
                                "src/app.py": {"status": "modified", "hunks": ["feature", "debug"]},
                                "docs/guide.md": {"status": "untracked", "content": "Guide\n"},
                                ".gitignore": {"status": "untracked", "content": "dist/\n"},
                            },
                            partial_hunks={"src/app.py": {"target_hunks": ["feature"], "leftover_hunks": ["debug"]}},
                        ),
                        "solution": [
                            "git add -p src/app.py",
                            "git commit -m 'Add feature'",
                            "git rm old_helper.py",
                            "git rm -r --cached dist",
                            "git add .gitignore docs/guide.md",
                            "git commit -m 'Clean up and document'",
                            "git restore src/app.py",
                        ],
                        "required": ["git add -p", "git commit", "git rm", "git rm -r --cached"],
                        "state_requirements": {
                            "latest_commit": {"branch": "main", "contains_paths": [".gitignore", "docs/guide.md"], "message_contains": ["Clean up and document"]},
                            "staging_empty": True,
                            "rules": [
                                {"type": "commit_count_equals", "count": 3},
                                {"type": "tracked_path_removed_from_commit_tree", "path": "old_helper.py"},
                                {"type": "tracked_path_removed_from_commit_tree", "path": "dist/bundle.js"},
                                {"type": "working_tree_clean_except", "paths": ["dist/bundle.js"]},
                            ],
                        },
                        "concepts": ["git add -p", "git commit", "git rm", "git rm -r --cached", "git restore"],
                    },
                    {
                        "story": "A data pipeline's workspace has a half-finished stage, a legacy transform, a generated build directory tracked by mistake, and a leftover debug hunk all mixed together.",
                        "task": "Split this mess into two clean commits: the real pipeline stage first, then the cleanup and documentation, discarding the debug leftovers.",
                        "before": "main -> c0; mixed additions, a tracked deletion, a tracked generated dir, and a partial hunk in src/pipeline.py",
                        "after": "main -> c0 -> c1(stage) -> c2(cleanup+docs); legacy_transform.py and build/ removed from history; debug hunk discarded",
                        "initial": repo(
                            commits=[commit("c0", "Initial", [], {"README.md": "base\n", "src/pipeline.py": "v1\n", "legacy_transform.py": "legacy\n", "build/output.csv": "built\n"})],
                            working_tree={
                                "src/pipeline.py": {"status": "modified", "hunks": ["feature", "debug"]},
                                "docs/pipeline.md": {"status": "untracked", "content": "Guide\n"},
                                ".gitignore": {"status": "untracked", "content": "build/\n"},
                            },
                            partial_hunks={"src/pipeline.py": {"target_hunks": ["feature"], "leftover_hunks": ["debug"]}},
                        ),
                        "solution": [
                            "git add -p src/pipeline.py",
                            "git commit -m 'Add pipeline stage'",
                            "git rm legacy_transform.py",
                            "git rm -r --cached build",
                            "git add .gitignore docs/pipeline.md",
                            "git commit -m 'Clean up pipeline'",
                            "git restore src/pipeline.py",
                        ],
                        "required": ["git add -p", "git commit", "git rm", "git rm -r --cached"],
                        "state_requirements": {
                            "latest_commit": {"branch": "main", "contains_paths": [".gitignore", "docs/pipeline.md"], "message_contains": ["Clean up pipeline"]},
                            "staging_empty": True,
                            "rules": [
                                {"type": "commit_count_equals", "count": 3},
                                {"type": "working_tree_clean_except", "paths": ["build/output.csv"]},
                                {"type": "tracked_path_removed_from_commit_tree", "path": "legacy_transform.py"},
                                {"type": "tracked_path_removed_from_commit_tree", "path": "build/output.csv"},
                            ],
                        },
                        "concepts": ["git add -p", "git commit", "git rm", "git rm -r --cached", "git restore"],
                    },
                ),
            ]
        elif chapter == 3:
            trials = [
                _bp_trial(
                    3,
                    "easy",
                    ["ch3-adv-switch-create"],
                    {
                        "story": "A new UI feature needs its own branch before any commit happens.",
                        "task": "Create and switch to feature/ui in one move, then commit the new work there.",
                        "before": "main -> c0; src/ui.py untracked",
                        "after": "main -> c0 unchanged; feature/ui -> c1",
                        "initial": repo(commits=[commit("c0", "Initial", [], {"README.md": "base\n"})], branches={"main": "c0"}, working_tree={"src/ui.py": {"status": "untracked", "content": "class UI:\n    pass\n"}}),
                        "solution": ["git switch -c feature/ui", "git add src/ui.py", "git commit -m 'Add UI feature'", "git log --oneline --graph"],
                        "required": ["git switch -c", "git add", "git commit", "git log"],
                        "state_requirements": {
                            "head_branch": "feature/ui",
                            "latest_commit": {"branch": "feature/ui", "contains_paths": ["src/ui.py"], "message_contains": ["Add UI feature"]},
                            "working_tree_clean": True,
                            "staging_empty": True,
                            "rules": [{"type": "branch_points_to", "branch": "main", "commit": "c0"}],
                        },
                        "concepts": ["git switch -c", "git add", "git commit", "git log --graph"],
                    },
                    {
                        "story": "A new docs feature needs its own branch before any commit happens.",
                        "task": "Create and switch to feature/docs in one move, then commit the new work there.",
                        "before": "main -> c0; docs/index.md untracked",
                        "after": "main -> c0 unchanged; feature/docs -> c1",
                        "initial": repo(commits=[commit("c0", "Initial", [], {"README.md": "base\n"})], branches={"main": "c0"}, working_tree={"docs/index.md": {"status": "untracked", "content": "# Docs\n"}}),
                        "solution": ["git switch -c feature/docs", "git add docs/index.md", "git commit -m 'Add docs feature'", "git log --oneline --graph"],
                        "required": ["git switch -c", "git add", "git commit", "git log"],
                        "state_requirements": {
                            "head_branch": "feature/docs",
                            "latest_commit": {"branch": "feature/docs", "contains_paths": ["docs/index.md"], "message_contains": ["Add docs feature"]},
                            "working_tree_clean": True,
                            "staging_empty": True,
                            "rules": [{"type": "branch_points_to", "branch": "main", "commit": "c0"}],
                        },
                        "concepts": ["git switch -c", "git add", "git commit", "git log --graph"],
                    },
                ),
                _bp_trial(
                    3,
                    "medium",
                    ["ch3-adv-branch-from-release", "ch3-adv-create-branch-at-start"],
                    {
                        "story": "An urgent release patch must build on last week's release cut, not on today's ongoing work.",
                        "task": "Branch a hotfix from that older release commit, switch to it, and commit the patch there.",
                        "before": "main -> c0 -> c1(release cut) -> c2(ongoing work)",
                        "after": "hotfix branches from c1 and advances by one commit; main unchanged at c2",
                        "initial": repo(
                            commits=[
                                commit("c0", "Initial", [], {"README.md": "base\n"}),
                                commit("c1", "Release cut", ["c0"], {"README.md": "release\n"}),
                                commit("c2", "Ongoing work", ["c1"], {"README.md": "release\n", "src/app.py": "v2\n"}),
                            ],
                            branches={"main": "c2"},
                            working_tree={"hotfix.md": {"status": "untracked", "content": "urgent fix notes\n"}},
                        ),
                        "solution": ["git branch hotfix c1", "git switch hotfix", "git add hotfix.md", "git commit -m 'Patch release'", "git branch -v"],
                        "required": ["git branch", "git switch", "git commit", "git branch -v"],
                        "state_requirements": {
                            "head_branch": "hotfix",
                            "latest_commit": {"branch": "hotfix", "contains_paths": ["hotfix.md"], "message_contains": ["Patch release"]},
                            "rules": [
                                {"type": "branch_points_to", "branch": "main", "commit": "c2"},
                                {"type": "commit_parent_equals", "branch": "hotfix", "parent_equals": "c1"},
                            ],
                        },
                        "concepts": ["git branch <name> <start-point>", "git switch", "git commit", "git branch -v"],
                    },
                    {
                        "story": "An urgent support patch must build on last week's release cut, not on today's ongoing work.",
                        "task": "Branch a support fix from that older release commit, switch to it, and commit the patch there.",
                        "before": "main -> c0 -> c1(release cut) -> c2(ongoing work)",
                        "after": "support branches from c1 and advances by one commit; main unchanged at c2",
                        "initial": repo(
                            commits=[
                                commit("c0", "Initial", [], {"README.md": "base\n"}),
                                commit("c1", "Release cut", ["c0"], {"README.md": "release\n"}),
                                commit("c2", "Ongoing work", ["c1"], {"README.md": "release\n", "src/app.py": "v2\n"}),
                            ],
                            branches={"main": "c2"},
                            working_tree={"support-fix.md": {"status": "untracked", "content": "urgent support notes\n"}},
                        ),
                        "solution": ["git branch support c1", "git switch support", "git add support-fix.md", "git commit -m 'Patch support'", "git branch -v"],
                        "required": ["git branch", "git switch", "git commit", "git branch -v"],
                        "state_requirements": {
                            "head_branch": "support",
                            "latest_commit": {"branch": "support", "contains_paths": ["support-fix.md"], "message_contains": ["Patch support"]},
                            "rules": [
                                {"type": "branch_points_to", "branch": "main", "commit": "c2"},
                                {"type": "commit_parent_equals", "branch": "support", "parent_equals": "c1"},
                            ],
                        },
                        "concepts": ["git branch <name> <start-point>", "git switch", "git commit", "git branch -v"],
                    },
                ),
                _bp_trial(
                    3,
                    "hard",
                    ["ch3-adv-recover-detached-work", "ch3-adv-delete-merged-branch", "ch3-adv-force-delete-scratch-branch"],
                    {
                        "story": "A promising docs idea only exists as an orphaned commit, while two disposable branch pointers still clutter the graph.",
                        "task": "Inspect the orphaned commit directly, rescue and finish it on a real branch, then remove both disposable pointers.",
                        "before": "main -> c2; old(merged, disposable) and scratch(unmerged, disposable) branches; c1 reachable only by id",
                        "after": "docs-rescue anchors the finished rescued work; old and scratch removed; main unchanged",
                        "initial": repo(
                            commits=[
                                commit("c0", "Initial", [], {"README.md": "base\n"}),
                                commit("c1", "Draft docs idea", ["c0"], {"README.md": "base\n", "draft.md": "idea\n"}),
                                commit("c2", "Continue main", ["c0"], {"README.md": "base v2\n"}),
                                commit("c3", "Abandoned experiment", ["c0"], {"README.md": "base\n", "experiment.md": "trial\n"}),
                            ],
                            branches={"main": "c2", "old": "c0", "scratch": "c3"},
                        ),
                        "solution": [
                            "git switch --detach c1",
                            "git add finalized.md",
                            "git commit -m 'Finalize rescued docs'",
                            "git branch docs-rescue HEAD",
                            "git switch docs-rescue",
                            "git branch -d old",
                            "git branch -D scratch",
                        ],
                        "workspace_files": [{"after_command_index": 0, "path": "finalized.md", "content": "Docs finalized from rescued idea\n"}],
                        "required": ["git switch --detach", "git commit", "git branch", "git switch", "git branch -d", "git branch -D"],
                        "state_requirements": {
                            "head_branch": "docs-rescue",
                            "latest_commit": {"branch": "docs-rescue", "contains_paths": ["finalized.md"], "message_contains": ["Finalize rescued docs"]},
                            "rules": [
                                {"type": "branch_points_to", "branch": "main", "commit": "c2"},
                                {"type": "branch_absent", "branch": "old"},
                                {"type": "branch_absent", "branch": "scratch"},
                            ],
                        },
                        "concepts": ["git switch --detach", "git commit", "git branch <name> <commit>", "git switch", "git branch -d", "git branch -D"],
                    },
                    {
                        "story": "A promising fix only exists as an orphaned commit, while two disposable branch pointers still clutter the graph.",
                        "task": "Inspect the orphaned commit directly, rescue and finish it on a real branch, then remove both disposable pointers.",
                        "before": "main -> c2; old(merged, disposable) and scratch(unmerged, disposable) branches; c1 reachable only by id",
                        "after": "fix-rescue anchors the finished rescued work; old and scratch removed; main unchanged",
                        "initial": repo(
                            commits=[
                                commit("c0", "Initial", [], {"README.md": "base\n"}),
                                commit("c1", "Draft urgent fix", ["c0"], {"README.md": "base\n", "hotfix_draft.md": "idea\n"}),
                                commit("c2", "Continue main", ["c0"], {"README.md": "base v2\n"}),
                                commit("c3", "Abandoned experiment", ["c0"], {"README.md": "base\n", "experiment.md": "trial\n"}),
                            ],
                            branches={"main": "c2", "old": "c0", "scratch": "c3"},
                        ),
                        "solution": [
                            "git switch --detach c1",
                            "git add verified_fix.md",
                            "git commit -m 'Finalize rescued fix'",
                            "git branch fix-rescue HEAD",
                            "git switch fix-rescue",
                            "git branch -d old",
                            "git branch -D scratch",
                        ],
                        "workspace_files": [{"after_command_index": 0, "path": "verified_fix.md", "content": "Fix finalized from rescued idea\n"}],
                        "required": ["git switch --detach", "git commit", "git branch", "git switch", "git branch -d", "git branch -D"],
                        "state_requirements": {
                            "head_branch": "fix-rescue",
                            "latest_commit": {"branch": "fix-rescue", "contains_paths": ["verified_fix.md"], "message_contains": ["Finalize rescued fix"]},
                            "rules": [
                                {"type": "branch_points_to", "branch": "main", "commit": "c2"},
                                {"type": "branch_absent", "branch": "old"},
                                {"type": "branch_absent", "branch": "scratch"},
                            ],
                        },
                        "concepts": ["git switch --detach", "git commit", "git branch <name> <commit>", "git switch", "git branch -d", "git branch -D"],
                    },
                ),
            ]
        elif chapter == 4:
            trials = [
                _bp_trial(
                    4,
                    "easy",
                    ["ch4-adv-merge-fast-forward"],
                    {
                        "story": "A docs feature is complete and main has not moved since it branched off.",
                        "task": "Verify there is no divergence, then bring main forward to the feature tip.",
                        "before": "main behind feature/docs; no divergence",
                        "after": "main -> feature/docs tip via fast-forward",
                        "initial": repo(commits=[commit("c0", "Initial", [], {"README.md": "base\n"}), commit("c1", "Add docs", ["c0"], {"README.md": "base\n", "docs/guide.md": "guide\n"})], branches={"main": "c0", "feature/docs": "c1"}),
                        "solution": ["git log --oneline --graph --all", "git status", "git merge feature/docs"],
                        "required": ["git log", "git status", "git merge"],
                        "state_requirements": {"working_tree_clean": True, "rules": [{"type": "branch_points_to", "branch": "main", "commit": "c1"}]},
                        "concepts": ["git log --graph --all", "git status", "git merge"],
                    },
                    {
                        "story": "A style feature is complete and main has not moved since it branched off.",
                        "task": "Verify there is no divergence, then bring main forward to the feature tip.",
                        "before": "main behind feature/style; no divergence",
                        "after": "main -> feature/style tip via fast-forward",
                        "initial": repo(commits=[commit("c0", "Initial", [], {"README.md": "base\n"}), commit("c1", "Add styles", ["c0"], {"README.md": "base\n", "src/styles.css": "body {}\n"})], branches={"main": "c0", "feature/style": "c1"}),
                        "solution": ["git log --oneline --graph --all", "git status", "git merge feature/style"],
                        "required": ["git log", "git status", "git merge"],
                        "state_requirements": {"working_tree_clean": True, "rules": [{"type": "branch_points_to", "branch": "main", "commit": "c1"}]},
                        "concepts": ["git log --graph --all", "git status", "git merge"],
                    },
                ),
                _bp_trial(
                    4,
                    "medium",
                    ["ch4-adv-merge-no-ff", "ch4-adv-merge-squash"],
                    {
                        "story": "A plugin branch's history is worth preserving exactly as it happened.",
                        "task": "Confirm the shared ancestor, then merge with an explicit merge commit that keeps both histories visible.",
                        "before": "main and feature/plugin diverged from c0",
                        "after": "main -> merge commit with two parents; feature/plugin history preserved",
                        "initial": repo(
                            commits=[
                                commit("c0", "Initial", [], {"README.md": "base\n"}),
                                commit("c1", "Main work", ["c0"], {"README.md": "main v2\n"}),
                                commit("c2", "Plugin work", ["c0"], {"README.md": "base\n", "plugin.py": "hook()\n"}),
                            ],
                            branches={"main": "c1", "feature/plugin": "c2"},
                        ),
                        "solution": ["git merge-base main feature/plugin", "git merge --no-ff feature/plugin"],
                        "required": ["git merge-base", "git merge --no-ff"],
                        "state_requirements": {"latest_commit": {"branch": "main"}, "rules": [{"type": "commit_parent_count_equals", "count": 2}]},
                        "concepts": ["git merge-base", "git merge --no-ff"],
                    },
                    {
                        "story": "An experimental branch's individual commits are not worth keeping - only the finished result matters.",
                        "task": "Confirm the shared ancestor, squash the branch into one clean commit, then discard the disposable pointer.",
                        "before": "main and feature/experiment diverged from c0",
                        "after": "main -> single squashed commit; feature/experiment branch removed",
                        "initial": repo(
                            commits=[
                                commit("c0", "Initial", [], {"README.md": "base\n"}),
                                commit("c1", "Main work", ["c0"], {"README.md": "main v2\n"}),
                                commit("c2", "Experiment work", ["c0"], {"README.md": "base\n", "experiment.py": "trial()\n"}),
                            ],
                            branches={"main": "c1", "feature/experiment": "c2"},
                        ),
                        "solution": ["git merge-base main feature/experiment", "git merge --squash feature/experiment", "git commit -m 'Squash experimental feature'", "git branch -D feature/experiment"],
                        "required": ["git merge-base", "git merge --squash", "git commit", "git branch -D"],
                        "state_requirements": {
                            "latest_commit": {"branch": "main", "contains_paths": ["experiment.py"], "message_contains": ["Squash experimental feature"]},
                            "staging_empty": True,
                            "rules": [{"type": "commit_is_not_merge"}, {"type": "branch_absent", "branch": "feature/experiment"}],
                        },
                        "concepts": ["git merge-base", "git merge --squash", "git commit", "git branch -D"],
                    },
                ),
                _bp_trial(
                    4,
                    "hard",
                    ["ch4-adv-manual-mixed-resolution", "ch4-adv-take-theirs", "ch4-adv-take-ours"],
                    {
                        "story": "main and feature/routes both changed the same routing table from a shared base, and only evidence can tell you which side is right.",
                        "task": "Find the common ancestor, inspect every side of the conflict, then keep the incoming routing table and finish the merge.",
                        "before": "main and feature/routes both edit src/routes.py from a shared base",
                        "after": "main -> merge commit with feature/routes' routing table kept; conflict fully resolved",
                        "initial": repo(
                            commits=[
                                commit("c0", "Base routes", [], {"src/routes.py": "routes = {}\n"}),
                                commit("c1", "Main adds /health", ["c0"], {"src/routes.py": "routes = {'/health': 1}\n"}),
                                commit("c2", "Feature adds /status", ["c0"], {"src/routes.py": "routes = {'/status': 1}\n"}),
                            ],
                            branches={"main": "c1", "feature/routes": "c2"},
                        ),
                        "solution": [
                            "git merge-base main feature/routes",
                            "git merge feature/routes",
                            "git ls-files -u",
                            "git diff --base src/routes.py",
                            "git diff --ours src/routes.py",
                            "git diff --theirs src/routes.py",
                            "git checkout --theirs src/routes.py",
                            "git add src/routes.py",
                            "git merge --continue",
                        ],
                        "required": ["git merge-base", "git merge", "git ls-files -u", "git diff --base", "git checkout --theirs", "git add", "git merge --continue"],
                        "state_requirements": {
                            "conflict_free": True,
                            "latest_commit": {"branch": "main", "contains_paths": ["src/routes.py"]},
                            "rules": [
                                {"type": "commit_parent_count_equals", "count": 2},
                                {"type": "operation_metadata_equals", "key": "last_checkout_conflict_side", "value": "theirs"},
                            ],
                        },
                        "concepts": ["git merge-base", "git merge", "git ls-files -u", "git diff --base/--ours/--theirs", "git checkout --theirs", "git merge --continue"],
                    },
                    {
                        "story": "main and feature/config both tuned the same timeout value from a shared base, and only evidence can tell you which side is right.",
                        "task": "Find the common ancestor, inspect every side of the conflict, then keep main's own timeout value and finish the merge.",
                        "before": "main and feature/config both edit src/config.py from a shared base",
                        "after": "main -> merge commit with main's own timeout value kept; conflict fully resolved",
                        "initial": repo(
                            commits=[
                                commit("c0", "Base config", [], {"src/config.py": "timeout = 1000\n"}),
                                commit("c1", "Main tunes timeout", ["c0"], {"src/config.py": "timeout = 5000\n"}),
                                commit("c2", "Feature tunes timeout", ["c0"], {"src/config.py": "timeout = 2500\n"}),
                            ],
                            branches={"main": "c1", "feature/config": "c2"},
                        ),
                        "solution": [
                            "git merge-base main feature/config",
                            "git merge feature/config",
                            "git ls-files -u",
                            "git diff --base src/config.py",
                            "git diff --ours src/config.py",
                            "git diff --theirs src/config.py",
                            "git checkout --ours src/config.py",
                            "git add src/config.py",
                            "git merge --continue",
                        ],
                        "required": ["git merge-base", "git merge", "git ls-files -u", "git diff --base", "git checkout --ours", "git add", "git merge --continue"],
                        "state_requirements": {
                            "conflict_free": True,
                            "latest_commit": {"branch": "main", "contains_paths": ["src/config.py"]},
                            "rules": [
                                {"type": "commit_parent_count_equals", "count": 2},
                                {"type": "operation_metadata_equals", "key": "last_checkout_conflict_side", "value": "ours"},
                            ],
                        },
                        "concepts": ["git merge-base", "git merge", "git ls-files -u", "git diff --base/--ours/--theirs", "git checkout --ours", "git merge --continue"],
                    },
                ),
            ]
        elif chapter == 5:
            trials = [
                _bp_trial(
                    5,
                    "easy",
                    ["ch5-adv-reset-hard-parent"],
                    {
                        "story": "A private branch's latest commit is nothing but a leftover debug print, never shared with anyone.",
                        "task": "Confirm what the bad commit contains, then drop it and return to the last good commit.",
                        "before": "main -> c1(good) -> c2(bad debug commit), private/unshared",
                        "after": "main -> c1; bad commit unreachable",
                        "initial": repo(
                            commits=[
                                commit("c0", "Initial", [], {"README.md": "base\n"}),
                                commit("c1", "Good work", ["c0"], {"README.md": "base\n", "src/app.py": "v1\n"}),
                                commit("c2", "Leftover debug print", ["c1"], {"README.md": "base\n", "src/app.py": "v1\nprint('debug')\n"}),
                            ],
                            branches={"main": "c2"},
                        ),
                        "solution": ["git log --oneline", "git show c2", "git reset --hard HEAD~1"],
                        "required": ["git log", "git show", "git reset --hard"],
                        "state_requirements": {"working_tree_clean": True, "rules": [{"type": "branch_points_to", "branch": "main", "commit": "c1"}]},
                        "concepts": ["git log", "git show", "git reset --hard"],
                    },
                    {
                        "story": "A private branch's latest commit accidentally includes generated build output, never shared with anyone.",
                        "task": "Confirm what the bad commit contains, then drop it and return to the last good commit.",
                        "before": "main -> c1(good) -> c2(bad generated commit), private/unshared",
                        "after": "main -> c1; bad commit unreachable",
                        "initial": repo(
                            commits=[
                                commit("c0", "Initial", [], {"README.md": "base\n"}),
                                commit("c1", "Good work", ["c0"], {"README.md": "base\n", "src/app.py": "v1\n"}),
                                commit("c2", "Accidentally committed generated output", ["c1"], {"README.md": "base\n", "src/app.py": "v1\n", "dist/build.js": "generated\n"}),
                            ],
                            branches={"main": "c2"},
                        ),
                        "solution": ["git log --oneline", "git show c2", "git reset --hard HEAD~1"],
                        "required": ["git log", "git show", "git reset --hard"],
                        "state_requirements": {"working_tree_clean": True, "rules": [{"type": "branch_points_to", "branch": "main", "commit": "c1"}]},
                        "concepts": ["git log", "git show", "git reset --hard"],
                    },
                ),
                _bp_trial(
                    5,
                    "medium",
                    ["ch5-adv-revert-no-edit"],
                    {
                        "story": "A bad config change already shipped to everyone on main and must stay auditable.",
                        "task": "Confirm what shipped, then undo it with a new commit instead of rewriting history.",
                        "before": "main -> c0 -> c1(bad shared config change)",
                        "after": "main advances with a revert commit; c1 stays in history",
                        "initial": repo(commits=[commit("c0", "Initial", [], {"README.md": "base\n"}), commit("c1", "Ship config change", ["c0"], {"README.md": "base\n", "config.yaml": "debug: true\n"})], branches={"main": "c1"}),
                        "solution": ["git log --oneline", "git show c1", "git revert --no-edit c1"],
                        "required": ["git log", "git show", "git revert"],
                        "state_requirements": {"rules": [{"type": "new_revert_commit_exists"}, {"type": "revert_preserves_history", "commit": "c1", "branch": "main"}]},
                        "concepts": ["git log", "git show", "git revert --no-edit"],
                    },
                    {
                        "story": "A bad UI copy change already shipped to everyone on main and must stay auditable.",
                        "task": "Confirm what shipped, then undo it with a new commit instead of rewriting history.",
                        "before": "main -> c0 -> c1(bad shared copy change)",
                        "after": "main advances with a revert commit; c1 stays in history",
                        "initial": repo(commits=[commit("c0", "Initial", [], {"README.md": "base\n"}), commit("c1", "Ship incorrect UI copy", ["c0"], {"README.md": "base\n", "src/copy.py": "text = 'Wrong message'\n"})], branches={"main": "c1"}),
                        "solution": ["git log --oneline", "git show c1", "git revert --no-edit c1"],
                        "required": ["git log", "git show", "git revert"],
                        "state_requirements": {"rules": [{"type": "new_revert_commit_exists"}, {"type": "revert_preserves_history", "commit": "c1", "branch": "main"}]},
                        "concepts": ["git log", "git show", "git revert --no-edit"],
                    },
                ),
                _bp_trial(
                    5,
                    "hard",
                    ["ch5-adv-recover-lost-tip", "ch5-adv-choose-reset-or-revert"],
                    {
                        "story": "An accidental reset dropped a genuinely useful release note, and a further bad commit landed on main afterward.",
                        "task": "Find the lost work in the reflog and anchor it, then undo the later shared mistake without rewriting main.",
                        "before": "main reset away from c2(lost); a further bad shared commit c3 landed on main",
                        "after": "lost work anchored on recovered; main gets a revert commit undoing c3",
                        "initial": repo(
                            commits=[
                                commit("c0", "Initial", [], {"README.md": "base\n"}),
                                commit("c1", "Release prep", ["c0"], {"README.md": "release\n"}),
                                commit("c2", "Important release note", ["c1"], {"README.md": "release\n", "RELEASE_NOTES.md": "notes\n"}),
                                commit("c3", "Ship bad analytics", ["c1"], {"README.md": "release\n", "analytics.py": "track_bad()\n"}),
                            ],
                            branches={"main": "c3"},
                            reflog=[
                                {"ref": "HEAD@{0}", "target": "c3", "message": "commit: Ship bad analytics"},
                                {"ref": "HEAD@{1}", "target": "c1", "message": "reset: moving to c1"},
                                {"ref": "HEAD@{2}", "target": "c2", "message": "commit: Important release note"},
                            ],
                        ),
                        "solution": ["git reflog", "git branch recovered c2", "git revert --no-edit c3"],
                        "required": ["git reflog", "git branch", "git revert"],
                        "state_requirements": {
                            "rules": [
                                {"type": "branch_points_to", "branch": "recovered", "commit": "c2"},
                                {"type": "new_revert_commit_exists"},
                                {"type": "revert_preserves_history", "commit": "c3", "branch": "main"},
                            ]
                        },
                        "concepts": ["git reflog", "git branch <name> <sha>", "git revert"],
                    },
                    {
                        "story": "An accidental reset dropped genuinely useful hotfix documentation, and a further bad commit landed on main afterward.",
                        "task": "Find the lost work in the reflog and anchor it, then undo the later shared mistake without rewriting main.",
                        "before": "main reset away from c2(lost); a further bad shared commit c3 landed on main",
                        "after": "lost work anchored on recovered; main gets a revert commit undoing c3",
                        "initial": repo(
                            commits=[
                                commit("c0", "Initial", [], {"README.md": "base\n"}),
                                commit("c1", "Hotfix prep", ["c0"], {"README.md": "hotfix\n"}),
                                commit("c2", "Important hotfix documentation", ["c1"], {"README.md": "hotfix\n", "HOTFIX_NOTES.md": "notes\n"}),
                                commit("c3", "Ship bad telemetry", ["c1"], {"README.md": "hotfix\n", "telemetry.py": "track_bad()\n"}),
                            ],
                            branches={"main": "c3"},
                            reflog=[
                                {"ref": "HEAD@{0}", "target": "c3", "message": "commit: Ship bad telemetry"},
                                {"ref": "HEAD@{1}", "target": "c1", "message": "reset: moving to c1"},
                                {"ref": "HEAD@{2}", "target": "c2", "message": "commit: Important hotfix documentation"},
                            ],
                        ),
                        "solution": ["git reflog", "git branch recovered c2", "git revert --no-edit c3"],
                        "required": ["git reflog", "git branch", "git revert"],
                        "state_requirements": {
                            "rules": [
                                {"type": "branch_points_to", "branch": "recovered", "commit": "c2"},
                                {"type": "new_revert_commit_exists"},
                                {"type": "revert_preserves_history", "commit": "c3", "branch": "main"},
                            ]
                        },
                        "concepts": ["git reflog", "git branch <name> <sha>", "git revert"],
                    },
                ),
            ]
        elif chapter == 6:
            trials = [
                _bp_trial(
                    6,
                    "easy",
                    ["ch6-adv-stash-restore-commit"],
                    {
                        "story": "Unfinished local work on main can't follow you onto hotfix/docs for an urgent doc fix.",
                        "task": "Shelve the local work, land the urgent fix on the hotfix branch, then come back and restore your own work.",
                        "before": "feature work uncommitted on main; hotfix/docs branch needs a doc fix",
                        "after": "hotfix/docs advances with the fix; main's WIP restored after popping the stash",
                        "initial": repo(commits=[commit("c0", "Initial", [], {"README.md": "base\n"})], branches={"main": "c0", "hotfix/docs": "c0"}, working_tree={"src/app.py": {"status": "untracked", "content": "work in progress\n"}}),
                        "solution": ["git status", "git stash", "git switch hotfix/docs", "git add DOCS.md", "git commit -m 'Add urgent doc fix'", "git switch main", "git stash pop"],
                        "workspace_files": [{"after_command_index": 2, "path": "DOCS.md", "content": "Urgent doc fix\n"}],
                        "required": ["git status", "git stash", "git switch", "git commit", "git stash pop"],
                        "state_requirements": {
                            "head_branch": "main",
                            "latest_commit": {"branch": "hotfix/docs", "contains_paths": ["DOCS.md"], "message_contains": ["Add urgent doc fix"]},
                            "rules": [{"type": "working_tree_contains", "path": "src/app.py"}],
                        },
                        "concepts": ["git status", "git stash", "git switch", "git commit", "git stash pop"],
                    },
                    {
                        "story": "Unfinished local work on main can't follow you onto hotfix/bugfix for an urgent bug fix.",
                        "task": "Shelve the local work, land the urgent fix on the hotfix branch, then come back and restore your own work.",
                        "before": "feature work uncommitted on main; hotfix/bugfix branch needs a bug fix",
                        "after": "hotfix/bugfix advances with the fix; main's WIP restored after popping the stash",
                        "initial": repo(commits=[commit("c0", "Initial", [], {"README.md": "base\n"})], branches={"main": "c0", "hotfix/bugfix": "c0"}, working_tree={"src/feature.py": {"status": "untracked", "content": "work in progress\n"}}),
                        "solution": ["git status", "git stash", "git switch hotfix/bugfix", "git add BUGFIX.md", "git commit -m 'Add urgent bugfix'", "git switch main", "git stash pop"],
                        "workspace_files": [{"after_command_index": 2, "path": "BUGFIX.md", "content": "Urgent bugfix\n"}],
                        "required": ["git status", "git stash", "git switch", "git commit", "git stash pop"],
                        "state_requirements": {
                            "head_branch": "main",
                            "latest_commit": {"branch": "hotfix/bugfix", "contains_paths": ["BUGFIX.md"], "message_contains": ["Add urgent bugfix"]},
                            "rules": [{"type": "working_tree_contains", "path": "src/feature.py"}],
                        },
                        "concepts": ["git status", "git stash", "git switch", "git commit", "git stash pop"],
                    },
                ),
                _bp_trial(
                    6,
                    "medium",
                    ["ch6-adv-cherry-pick-one"],
                    {
                        "story": "A security fix exists on the development branch, and the release branch needs exactly that fix and nothing else.",
                        "task": "Confirm which commit is the fix, then transplant only that commit onto the release branch.",
                        "before": "release branch lacks a security fix that exists on development",
                        "after": "release advances by the cherry-picked fix only; unrelated dev commits absent",
                        "initial": repo(
                            commits=[
                                commit("c0", "Initial", [], {"README.md": "base\n"}),
                                commit("c1", "Release cut", ["c0"], {"README.md": "base\n"}),
                                commit("c2", "Fix XSS vulnerability", ["c1"], {"README.md": "base\n", "src/security.py": "escape(x)\n"}),
                                commit("c3", "Unrelated dev work", ["c2"], {"README.md": "base\n", "src/security.py": "escape(x)\n", "src/dev.py": "wip\n"}),
                            ],
                            branches={"main": "c1", "development": "c3"},
                        ),
                        "solution": ["git log --oneline --graph --all", "git show c2", "git switch main", "git cherry-pick c2"],
                        "required": ["git log", "git show", "git switch", "git cherry-pick"],
                        "state_requirements": {
                            "latest_commit": {"branch": "main", "contains_paths": ["src/security.py"], "excludes_paths": ["src/dev.py"]},
                            "rules": [{"type": "cherry_pick_created_new_commit", "source": "c2"}, {"type": "cherry_pick_copied_changes_from", "source": "c2"}],
                        },
                        "concepts": ["git log --graph --all", "git show", "git switch", "git cherry-pick"],
                    },
                    {
                        "story": "A typo fix exists on the development branch, and the release branch needs exactly that fix and nothing else.",
                        "task": "Confirm which commit is the fix, then transplant only that commit onto the release branch.",
                        "before": "release branch lacks a typo fix that exists on development",
                        "after": "release advances by the cherry-picked fix only; unrelated dev commits absent",
                        "initial": repo(
                            commits=[
                                commit("c0", "Initial", [], {"README.md": "base\n"}),
                                commit("c1", "Release cut", ["c0"], {"README.md": "base\n"}),
                                commit("c2", "Fix typo in error message", ["c1"], {"README.md": "base\n", "src/errors.py": "msg = 'Not found'\n"}),
                                commit("c3", "Unrelated refactor", ["c2"], {"README.md": "base\n", "src/errors.py": "msg = 'Not found'\n", "src/refactor.py": "wip\n"}),
                            ],
                            branches={"main": "c1", "development": "c3"},
                        ),
                        "solution": ["git log --oneline --graph --all", "git show c2", "git switch main", "git cherry-pick c2"],
                        "required": ["git log", "git show", "git switch", "git cherry-pick"],
                        "state_requirements": {
                            "latest_commit": {"branch": "main", "contains_paths": ["src/errors.py"], "excludes_paths": ["src/refactor.py"]},
                            "rules": [{"type": "cherry_pick_created_new_commit", "source": "c2"}, {"type": "cherry_pick_copied_changes_from", "source": "c2"}],
                        },
                        "concepts": ["git log --graph --all", "git show", "git switch", "git cherry-pick"],
                    },
                ),
                _bp_trial(
                    6,
                    "hard",
                    ["ch6-adv-abort-then-pick-right-commit", "ch6-adv-stash-and-pick"],
                    {
                        "story": "A cherry-pick of the wrong release candidate is stuck mid-way, and the real fix is still waiting on develop.",
                        "task": "Abort the wrong pick, bring in the correct fix unstaged so you can adapt it, then commit the adapted result.",
                        "before": "main mid-cherry-pick of the wrong candidate c2; correct fix c3 available on develop",
                        "after": "wrong pick aborted; correct fix adapted and committed on main",
                        "initial": repo(
                            commits=[
                                commit("c0", "Initial", [], {"README.md": "base\n"}),
                                commit("c1", "Release cut", ["c0"], {"README.md": "release\n"}),
                                commit("c2", "Wrong candidate fix", ["c1"], {"README.md": "release\nwrong\n"}),
                                commit("c3", "Correct fix for release", ["c1"], {"README.md": "release\n", "src/patch.py": "fix()\n"}),
                            ],
                            branches={"main": "c1", "develop": "c3"},
                            cherry_pick_in_progress=True,
                            cherry_pick_original_head="c1",
                        ),
                        "solution": ["git cherry-pick --abort", "git cherry-pick --no-commit c3", "git add src/patch.py", "git commit -m 'Adapt release fix'"],
                        "required": ["git cherry-pick --abort", "git cherry-pick --no-commit", "git add", "git commit"],
                        "state_requirements": {
                            "latest_commit": {"branch": "main", "contains_paths": ["src/patch.py"], "message_contains": ["Adapt release fix"]},
                            "staging_empty": True,
                            "rules": [{"type": "operation_metadata_equals", "key": "last_cherry_pick_aborted", "value": True}],
                        },
                        "concepts": ["git cherry-pick --abort", "git cherry-pick --no-commit", "git add", "git commit"],
                    },
                    {
                        "story": "A cherry-pick of the wrong doc candidate is stuck mid-way, and the real backport is still waiting on develop.",
                        "task": "Abort the wrong pick, bring in the correct backport unstaged so you can adapt it, then commit the adapted result.",
                        "before": "main mid-cherry-pick of the wrong candidate c2; correct backport c3 available on develop",
                        "after": "wrong pick aborted; correct backport adapted and committed on main",
                        "initial": repo(
                            commits=[
                                commit("c0", "Initial", [], {"README.md": "base\n"}),
                                commit("c1", "Release cut", ["c0"], {"README.md": "release\n"}),
                                commit("c2", "Wrong doc candidate", ["c1"], {"README.md": "release\nwrong\n"}),
                                commit("c3", "Correct doc backport", ["c1"], {"README.md": "release\n", "docs/backport.md": "notes\n"}),
                            ],
                            branches={"main": "c1", "develop": "c3"},
                            cherry_pick_in_progress=True,
                            cherry_pick_original_head="c1",
                        ),
                        "solution": ["git cherry-pick --abort", "git cherry-pick --no-commit c3", "git add docs/backport.md", "git commit -m 'Adapt doc backport'"],
                        "required": ["git cherry-pick --abort", "git cherry-pick --no-commit", "git add", "git commit"],
                        "state_requirements": {
                            "latest_commit": {"branch": "main", "contains_paths": ["docs/backport.md"], "message_contains": ["Adapt doc backport"]},
                            "staging_empty": True,
                            "rules": [{"type": "operation_metadata_equals", "key": "last_cherry_pick_aborted", "value": True}],
                        },
                        "concepts": ["git cherry-pick --abort", "git cherry-pick --no-commit", "git add", "git commit"],
                    },
                ),
            ]
        else:
            trials = [
                _bp_trial(
                    7,
                    "easy",
                    ["ch7-adv-push-set-upstream"],
                    {
                        "story": "A docs feature only exists locally so far, cloned fresh from origin/main.",
                        "task": "Branch off, commit the docs feature, and publish it to origin with tracking set up.",
                        "before": "local repo cloned from origin/main only",
                        "after": "origin/feature/docs exists at the local feature tip; main unchanged",
                        "initial": uninitialized({}, remote_fixtures={"branches": {"origin/main": "r0"}, "default_branch": "origin/main", "commits": [commit("r0", "Initial project", [], {"README.md": "base\n"})]}),
                        "solution": ["git clone https://example.test/team/app.git", "git remote -v", "git switch -c feature/docs", "git add docs/guide.md", "git commit -m 'Add docs feature'", "git push -u origin feature/docs"],
                        "workspace_files": [{"after_command_index": 2, "path": "docs/guide.md", "content": "Guide\n"}],
                        "required": ["git clone", "git switch -c", "git commit", "git push -u"],
                        "state_requirements": {
                            "head_branch": "feature/docs",
                            "latest_commit": {"branch": "feature/docs", "contains_paths": ["docs/guide.md"], "message_contains": ["Add docs feature"]},
                            "rules": [
                                {"type": "remote_branch_matches_local", "remote_branch": "origin/feature/docs", "branch": "feature/docs"},
                                {"type": "upstream_tracking_set", "branch": "feature/docs"},
                                {"type": "branch_points_to", "branch": "main", "commit": "r0"},
                            ],
                        },
                        "concepts": ["git clone", "git switch -c", "git commit", "git push -u"],
                    },
                    {
                        "story": "A test feature only exists locally so far, cloned fresh from origin/main.",
                        "task": "Branch off, commit the test feature, and publish it to origin with tracking set up.",
                        "before": "local repo cloned from origin/main only",
                        "after": "origin/feature/test exists at the local feature tip; main unchanged",
                        "initial": uninitialized({}, remote_fixtures={"branches": {"origin/main": "r0"}, "default_branch": "origin/main", "commits": [commit("r0", "Initial project", [], {"README.md": "base\n"})]}),
                        "solution": ["git clone https://example.test/team/app.git", "git remote -v", "git switch -c feature/test", "git add tests/test_app.py", "git commit -m 'Add test feature'", "git push -u origin feature/test"],
                        "workspace_files": [{"after_command_index": 2, "path": "tests/test_app.py", "content": "def test_ok():\n    assert True\n"}],
                        "required": ["git clone", "git switch -c", "git commit", "git push -u"],
                        "state_requirements": {
                            "head_branch": "feature/test",
                            "latest_commit": {"branch": "feature/test", "contains_paths": ["tests/test_app.py"], "message_contains": ["Add test feature"]},
                            "rules": [
                                {"type": "remote_branch_matches_local", "remote_branch": "origin/feature/test", "branch": "feature/test"},
                                {"type": "upstream_tracking_set", "branch": "feature/test"},
                                {"type": "branch_points_to", "branch": "main", "commit": "r0"},
                            ],
                        },
                        "concepts": ["git clone", "git switch -c", "git commit", "git push -u"],
                    },
                ),
                _bp_trial(
                    7,
                    "medium",
                    ["ch7-adv-pull-default", "ch7-adv-sync-diverged-work"],
                    {
                        "story": "A teammate published a changelog on origin/main while an unrelated local note was still unpublished.",
                        "task": "Fetch to see what changed, integrate it, then publish the combined result.",
                        "before": "origin/main advanced with a teammate commit; local main has one unpublished commit",
                        "after": "local integrates upstream via pull; origin/main advances to match the integrated local tip",
                        "initial": repo(
                            commits=[
                                commit("c0", "Initial", [], {"README.md": "base\n"}),
                                commit("c1", "Local note", ["c0"], {"README.md": "base\n", "notes.md": "local\n"}),
                                commit("r1", "Teammate adds changelog", ["c0"], {"README.md": "base\n", "CHANGELOG.md": "v1\n"}),
                            ],
                            branches={"main": "c1"},
                            remotes={"origin": "https://example.test/team/app.git"},
                            remote_branches={"origin/main": "c0"},
                            upstream_tracking={"main": "origin/main"},
                            remote_updates={"origin/main": "r1"},
                        ),
                        "solution": ["git fetch origin", "git log --oneline --graph --all", "git pull", "git push"],
                        "required": ["git fetch", "git log", "git pull", "git push"],
                        "state_requirements": {
                            "latest_commit": {"branch": "main", "contains_paths": ["notes.md", "CHANGELOG.md"]},
                            "working_tree_clean": True,
                            "rules": [{"type": "remote_branch_matches_local", "remote_branch": "origin/main", "branch": "main"}],
                        },
                        "concepts": ["git fetch", "git log --graph --all", "git pull", "git push"],
                    },
                    {
                        "story": "Team policy requires a linear history, and a teammate published updates on origin/main while a local draft was still unpublished.",
                        "task": "Fetch to see what changed, replay your local work on top with a rebase, then publish the result.",
                        "before": "origin/main advanced with a teammate commit; local main has one unpublished commit",
                        "after": "local commit is rebased onto the teammate's work; origin/main advances to match",
                        "initial": repo(
                            commits=[
                                commit("c0", "Initial", [], {"README.md": "base\n"}),
                                commit("c1", "Local draft", ["c0"], {"README.md": "base\n", "draft.md": "local\n"}),
                                commit("r1", "Teammate adds updates", ["c0"], {"README.md": "base\n", "UPDATES.md": "v1\n"}),
                            ],
                            branches={"main": "c1"},
                            remotes={"origin": "https://example.test/team/app.git"},
                            remote_branches={"origin/main": "c0"},
                            upstream_tracking={"main": "origin/main"},
                            remote_updates={"origin/main": "r1"},
                        ),
                        "solution": ["git fetch origin", "git log --oneline --graph --all", "git pull --rebase", "git push"],
                        "required": ["git fetch", "git log", "git pull --rebase", "git push"],
                        "state_requirements": {
                            "latest_commit": {"branch": "main", "contains_paths": ["draft.md"], "message_contains": ["Local draft"]},
                            "working_tree_clean": True,
                            "rules": [
                                {"type": "commit_parent_equals", "branch": "main", "parent_equals": "r1"},
                                {"type": "operation_metadata_equals", "key": "pull_strategy", "value": "rebase"},
                                {"type": "remote_branch_matches_local", "remote_branch": "origin/main", "branch": "main"},
                            ],
                        },
                        "concepts": ["git fetch", "git log --graph --all", "git pull --rebase", "git push"],
                    },
                ),
                _bp_trial(
                    7,
                    "hard",
                    ["ch7-adv-rewrite-and-lease", "ch7-adv-fetch-prune"],
                    {
                        "story": "A teammate's hotfix landed on origin/main while a local release note sat unpublished, and a stale remote branch is still cluttering the remote.",
                        "task": "Sync safely: replay your note on top of the hotfix, correct its message, publish only under a lease, and remove the stale branch.",
                        "before": "origin/main has a teammate hotfix; local has an unpublished release note; a stale remote branch still exists",
                        "after": "local note rebased onto the hotfix, corrected, published under lease; stale branch removed",
                        "initial": repo(
                            commits=[
                                commit("c0", "Initial", [], {"README.md": "base\n"}),
                                commit("c1", "Release note", ["c0"], {"README.md": "base\n", "notes.md": "draft\n"}),
                                commit("r2", "Teammate hotfix", ["c0"], {"README.md": "base\n", "hotfix.md": "urgent\n"}),
                            ],
                            branches={"main": "c1"},
                            remotes={"origin": "https://example.test/team/app.git"},
                            remote_branches={"origin/main": "c0", "origin/old-feature": "c0"},
                            upstream_tracking={"main": "origin/main"},
                            remote_updates={"origin/main": "r2"},
                            remote_stale_branches=["old-feature"],
                        ),
                        "solution": ["git fetch --prune", "git log --oneline --graph --all", "git pull --rebase", "git commit --amend -m 'Correct release note'", "git push --force-with-lease", "git push origin --delete old-feature"],
                        "required": ["git fetch --prune", "git pull --rebase", "git commit --amend", "git push --force-with-lease", "git push"],
                        "state_requirements": {
                            "latest_commit": {"branch": "main", "contains_paths": ["notes.md"], "message_contains": ["Correct release note"]},
                            "rules": [
                                {"type": "remote_branch_absent", "remote_branch": "origin/old-feature"},
                                {"type": "commit_parent_equals", "branch": "main", "parent_equals": "r2"},
                                {"type": "commit_tree_contains", "branch": "main", "paths": ["hotfix.md"]},
                                {"type": "operation_metadata_equals", "key": "force_with_lease", "value": True},
                                {"type": "remote_branch_matches_local", "remote_branch": "origin/main", "branch": "main"},
                            ],
                        },
                        "concepts": ["git fetch --prune", "git pull --rebase", "git commit --amend", "git push --force-with-lease", "git push origin --delete"],
                    },
                    {
                        "story": "A teammate's hotfix landed on origin/main while a local summary sat unpublished, and a stale remote branch is still cluttering the remote.",
                        "task": "Sync safely: replay your summary on top of the hotfix, correct its message, publish only under a lease, and remove the stale branch.",
                        "before": "origin/main has a teammate hotfix; local has an unpublished summary; a stale remote branch still exists",
                        "after": "local summary rebased onto the hotfix, corrected, published under lease; stale branch removed",
                        "initial": repo(
                            commits=[
                                commit("c0", "Initial", [], {"README.md": "base\n"}),
                                commit("c1", "Summary note", ["c0"], {"README.md": "base\n", "summary.md": "draft\n"}),
                                commit("r2", "Teammate hotfix", ["c0"], {"README.md": "base\n", "patch.md": "urgent\n"}),
                            ],
                            branches={"main": "c1"},
                            remotes={"origin": "https://example.test/team/app.git"},
                            remote_branches={"origin/main": "c0", "origin/old-draft": "c0"},
                            upstream_tracking={"main": "origin/main"},
                            remote_updates={"origin/main": "r2"},
                            remote_stale_branches=["old-draft"],
                        ),
                        "solution": ["git fetch --prune", "git log --oneline --graph --all", "git pull --rebase", "git commit --amend -m 'Correct summary note'", "git push --force-with-lease", "git push origin --delete old-draft"],
                        "required": ["git fetch --prune", "git pull --rebase", "git commit --amend", "git push --force-with-lease", "git push"],
                        "state_requirements": {
                            "latest_commit": {"branch": "main", "contains_paths": ["summary.md"], "message_contains": ["Correct summary note"]},
                            "rules": [
                                {"type": "remote_branch_absent", "remote_branch": "origin/old-draft"},
                                {"type": "commit_parent_equals", "branch": "main", "parent_equals": "r2"},
                                {"type": "commit_tree_contains", "branch": "main", "paths": ["patch.md"]},
                                {"type": "operation_metadata_equals", "key": "force_with_lease", "value": True},
                                {"type": "remote_branch_matches_local", "remote_branch": "origin/main", "branch": "main"},
                            ],
                        },
                        "concepts": ["git fetch --prune", "git pull --rebase", "git commit --amend", "git push --force-with-lease", "git push origin --delete"],
                    },
                ),
            ]
        copy_spec = _BP_CHAPTER_COPY[chapter]
        specs.append(challenge(module, slug, title, copy_spec["summary"], copy_spec["narrative"], trials))
    return specs

CHALLENGES = _blueprint_challenges()
