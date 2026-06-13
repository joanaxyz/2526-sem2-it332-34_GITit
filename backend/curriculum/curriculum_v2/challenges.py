"""Scenario-first v2 Git-it Challenge curriculum.

Command Adventure introduces individual Git moves. Git-it Challenge applies only
those already-introduced moves inside believable repository scenarios where the
commit DAG, branch refs, remote refs, or HEAD position visibly changes.

This file intentionally authors Challenge as a curriculum contract, not merely
as "commands the current evaluator happens to know." The simulator/evaluator can
be expanded later, but the seed data already records the intended graph
transition for every scenario.
"""

from __future__ import annotations

from typing import Any

from curriculum.curriculum_v2.spec_helpers import commit, ev, meta_equals, repo, uninitialized

DIFFICULTY_ORDER = {"easy": 1, "medium": 2, "hard": 3}


def _contract(
    state_requirements: dict[str, Any],
    *,
    required: list[str] | None = None,
    forbidden: list[str] | None = None,
    graph: dict[str, Any] | None = None,
    concepts: list[str] | None = None,
    engine_notes: list[str] | None = None,
) -> dict[str, Any]:
    spec = ev(state_requirements, required=required, forbidden=forbidden)
    spec["curriculum_contract"] = {
        "schema_version": 1,
        "challenge_type": "scenario_graph_transition",
        "dag_transition": graph or {},
        "concepts_used": concepts or [],
        "engine_notes": engine_notes or [],
    }
    return spec


def _details(
    before: str, after: str, *, current: str | None = None, risk: str | None = None
) -> list[dict[str, str]]:
    rows = [
        {"label": "Starting diagram", "value": before},
        {"label": "Target diagram", "value": after},
    ]
    if current:
        rows.insert(0, {"label": "Current position", "value": current})
    if risk:
        rows.append({"label": "Why this matters", "value": risk})
    return rows


def _scenario(
    story: str,
    task: str,
    *,
    before: str,
    after: str,
    current: str | None = None,
    risk: str | None = None,
    constraints: list[str] | None = None,
) -> dict[str, Any]:
    return {
        "schema_version": 3,
        "story": story,
        "task": task,
        "details": _details(before, after, current=current, risk=risk),
        "constraints": constraints
        or [
            "Use the repository diagram and status clues before acting.",
            "The final answer is the repository state, not a memorized command string.",
        ],
    }


def variant(
    case_id: str,
    label: str,
    *,
    story: str,
    task: str,
    before: str,
    after: str,
    initial: dict[str, Any],
    solution: list[str],
    evaluation: dict[str, Any],
    current: str | None = None,
    risk: str | None = None,
    workspace_files: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    return {
        "case_id": case_id,
        "slug_template": case_id,
        "label_template": label,
        "initial_state_template": initial,
        "solution_commands_template": solution,
        "solution_workspace_files_template": workspace_files or [],
        "evaluation_spec_template": evaluation,
        "scenario_context_template": _scenario(
            story,
            task,
            before=before,
            after=after,
            current=current,
            risk=risk,
        ),
        "hint_set_template": [],
        "scaffold_policy_template": {
            "hints": "contextual",
            "answer": "never",
            "diagram": "primary",
        },
    }


def level(
    difficulty: str,
    *,
    story: str,
    task: str,
    before: str,
    after: str,
    variants: list[dict[str, Any]],
    uses_adventure_levels: list[str],
    current: str | None = None,
    risk: str | None = None,
    min_counted_commands: int = 1,
    max_counted_commands: int = 8,
    boss: dict[str, Any] | None = None,
) -> dict[str, Any]:
    scenario = _scenario(
        story,
        task,
        before=before,
        after=after,
        current=current,
        risk=risk,
    )
    return {
        "difficulty": difficulty,
        "required_successful_attempts": 1,
        "min_counted_commands": min_counted_commands,
        "max_counted_commands": max_counted_commands,
        "uses_adventure_levels": uses_adventure_levels,
        "scenario_context": scenario,
        # Authored battle boss ({species, hp}); empty = slug-stable default.
        "boss_spec": boss or {},
        "variants": variants,
    }


def challenge(
    module: str,
    slug: str,
    title: str,
    summary: str,
    narrative: str,
    levels: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "module": module,
        "slug": slug,
        "title": title,
        "summary": summary,
        "narrative": narrative,
        "levels": levels,
    }


# Shared authored histories -------------------------------------------------------------
CLONE_REMOTE = {
    "branches": {"origin/main": "r2", "origin/starter/login": "r3"},
    "default_branch": "origin/main",
    "commits": [
        commit("r0", "Create starter repository", [], {"README.md": "Git-it starter\n"}),
        commit(
            "r1",
            "Add app shell",
            ["r0"],
            {"README.md": "Git-it starter\n", "src/app.py": "print('hello')\n"},
        ),
        commit(
            "r2",
            "Add testing notes",
            ["r1"],
            {
                "README.md": "Git-it starter\n",
                "src/app.py": "print('hello')\n",
                "TESTING.md": "Run pytest\n",
            },
        ),
        commit(
            "r3",
            "Prepare login starter",
            ["r1"],
            {
                "README.md": "Git-it starter\n",
                "src/app.py": "print('hello')\n",
                "src/login.py": "TODO\n",
            },
        ),
    ],
}

SNAPSHOT_BASE = [
    commit(
        "c0", "Initial app shell", [], {"README.md": "Portal\n", "src/app.py": "print('hello')\n"}
    ),
]
SNAPSHOT_WITH_SECRET = [
    commit(
        "c0",
        "Initial app shell",
        [],
        {"README.md": "Portal\n", "src/app.py": "print('hello')\n", ".env": "SECRET=old\n"},
    ),
]

BRANCH_BASE = [
    commit("c0", "Initial portal", [], {"README.md": "Portal\n"}),
    commit(
        "c1", "Add app shell", ["c0"], {"README.md": "Portal\n", "src/app.py": "print('hello')\n"}
    ),
]
BRANCH_LONG = [
    *BRANCH_BASE,
    commit(
        "c2",
        "Add dashboard",
        ["c1"],
        {
            "README.md": "Portal\n",
            "src/app.py": "print('hello')\n",
            "src/dashboard.py": "cards=[]\n",
        },
    ),
]

MERGE_BASE = [
    commit("c0", "Create portal", [], {"README.md": "Portal\n", "src/app.py": "shell\n"}),
    commit(
        "m1",
        "Polish main shell",
        ["c0"],
        {"README.md": "Portal\n", "src/app.py": "shell\n", "docs/release.md": "draft\n"},
    ),
    commit(
        "f1",
        "Add level menu",
        ["c0"],
        {"README.md": "Portal\n", "src/app.py": "shell\n", "src/menu.py": "levels=[]\n"},
    ),
]
CONFLICT_HISTORY = [
    commit("c0", "Create auth config", [], {"src/auth.js": "timeout=3000\nmode='basic'\n"}),
    commit("m1", "Increase main timeout", ["c0"], {"src/auth.js": "timeout=5000\nmode='basic'\n"}),
    commit("f1", "Tune feature timeout", ["c0"], {"src/auth.js": "timeout=2500\nmode='strict'\n"}),
]

RECOVERY_HISTORY = [
    commit("c0", "Initial portal", [], {"README.md": "Portal\n"}),
    commit("c1", "Add app shell", ["c0"], {"README.md": "Portal\n", "src/app.py": "shell\n"}),
    commit(
        "c2",
        "Break login route",
        ["c1"],
        {"README.md": "Portal\n", "src/app.py": "shell\n", "src/login.py": "broken=True\n"},
    ),
]

PATCH_HISTORY = [
    commit("c0", "Base project", [], {"README.md": "base\n"}),
    commit("r1", "Prepare release", ["c0"], {"README.md": "base\n", "release.md": "ready\n"}),
    commit(
        "b1", "Fix login crash", ["c0"], {"README.md": "base\n", "src/login.py": "fixed=True\n"}
    ),
    commit(
        "b2",
        "Add noisy experiment",
        ["b1"],
        {"README.md": "base\n", "src/login.py": "fixed=True\n", "experiment.txt": "skip\n"},
    ),
]

REMOTE_BASE = [
    commit("c0", "Create portal", [], {"README.md": "Portal\n"}),
    commit(
        "c1", "Local app shell", ["c0"], {"README.md": "Portal\n", "src/app.py": "local shell\n"}
    ),
]
REMOTE_FIXTURE_AHEAD = {
    "branches": {"origin/main": "r2"},
    "default_branch": "origin/main",
    "commits": [
        commit(
            "r2",
            "Remote review note",
            ["c1"],
            {"README.md": "Portal\n", "src/app.py": "local shell\n", "review.md": "approved\n"},
        ),
    ],
}
REMOTE_DIVERGED = [
    commit("c0", "Create portal", [], {"README.md": "Portal\n"}),
    commit("c1", "Add app shell", ["c0"], {"README.md": "Portal\n", "src/app.py": "local shell\n"}),
    commit(
        "l2",
        "Local release note",
        ["c1"],
        {"README.md": "Portal\n", "src/app.py": "local shell\n", "release.md": "local\n"},
    ),
    commit(
        "r2",
        "Remote review note",
        ["c1"],
        {"README.md": "Portal\n", "src/app.py": "local shell\n", "review.md": "approved\n"},
    ),
]


CHALLENGES = [
    challenge(
        "creating-inspecting-repositories",
        "onboard-existing-repository",
        "Onboard an Existing Repository",
        "Clone the correct starter history so the local diagram matches the team source.",
        "The first Challenge is not about making commits yet. It is about creating a local DAG from an existing remote and reading it before work starts.",
        [
            level(
                "easy",
                story="A teammate sent the starter repository URL for the capstone lab.",
                task="Create a local copy that follows the remote main branch.",
                before="No local repository exists yet.",
                after="Local main points at the same commit as origin/main, with the remote history visible.",
                uses_adventure_levels=[
                    "clone-into-named-folder",
                    "inspect-status",
                    "inspect-graph-history",
                ],
                min_counted_commands=1,
                max_counted_commands=3,
                variants=[
                    variant(
                        "easy-clone-main-history",
                        "Clone main history",
                        story="The lab folder is empty; the team repository already has starter commits.",
                        task="Create a local copy of the main starter history.",
                        before="empty workspace; remote main -> r2",
                        after="main -> r2 and origin/main -> r2",
                        initial=uninitialized(remote_fixtures=CLONE_REMOTE),
                        solution=["git clone https://example.test/git-it/starter.git starter"],
                        evaluation=_contract(
                            {
                                "repository_initialized": True,
                                "head_branch": "main",
                                "branch_points_to": {"main": "r2"},
                                "remote_branch_points_to": {"origin/main": "r2"},
                                "upstream_tracking": {"main": "origin/main"},
                                "rules": [{"type": "commit_exists", "commit": "r2"}],
                                "working_tree_clean": True,
                            },
                            required=["git clone"],
                            graph={
                                "from": "no local DAG",
                                "to": "main and origin/main point to r2",
                            },
                            concepts=["clone", "remote-tracking branch", "HEAD on branch"],
                        ),
                    )
                ],
            ),
            level(
                "medium",
                story="The exercise must start from a non-default remote branch prepared by the instructor.",
                task="Clone the correct branch so the local branch starts at the branch-specific commit.",
                before="No local repository exists yet; origin/main and origin/starter/login point to different commits.",
                after="Local starter/login points at the same commit as origin/starter/login.",
                uses_adventure_levels=["clone-specific-branch", "inspect-graph-history"],
                min_counted_commands=1,
                max_counted_commands=3,
                variants=[
                    variant(
                        "medium-clone-login-starter",
                        "Clone starter branch",
                        story="The instructor says not to start from main; the login branch has the correct starter files.",
                        task="Create a local copy from the login starter branch.",
                        before="origin/main -> r2; origin/starter/login -> r3",
                        after="starter/login -> r3 and origin/starter/login -> r3",
                        initial=uninitialized(remote_fixtures=CLONE_REMOTE),
                        solution=[
                            "git clone -b starter/login https://example.test/git-it/starter.git login-lab"
                        ],
                        evaluation=_contract(
                            {
                                "repository_initialized": True,
                                "head_branch": "starter/login",
                                "branch_points_to": {"starter/login": "r3"},
                                "remote_branch_points_to": {"origin/starter/login": "r3"},
                                "upstream_tracking": {"starter/login": "origin/starter/login"},
                            },
                            required=["git clone -b"],
                            graph={
                                "from": "no local DAG",
                                "to": "starter/login follows origin/starter/login at r3",
                            },
                            concepts=["clone branch", "remote branch selection"],
                        ),
                    )
                ],
            ),
            level(
                "hard",
                story="The repo is large, and the learner only needs the latest visible tip for a quick review.",
                task="Create a shallow local copy of the default branch.",
                before="Remote main has a multi-commit history.",
                after="Local main contains only the shallow tip that matches origin/main.",
                uses_adventure_levels=["clone-shallow-history", "inspect-compact-history"],
                min_counted_commands=1,
                max_counted_commands=3,
                variants=[
                    variant(
                        "hard-clone-shallow-review",
                        "Clone shallow review",
                        story="You only need the newest starter snapshot for a short review, not the whole history.",
                        task="Create a shallow local copy of main.",
                        before="origin/main -> r2 with older parents behind it",
                        after="main -> r2 with shallow local history",
                        initial=uninitialized(remote_fixtures=CLONE_REMOTE),
                        solution=[
                            "git clone --depth 1 https://example.test/git-it/starter.git starter-review"
                        ],
                        evaluation=_contract(
                            {
                                "repository_initialized": True,
                                "head_branch": "main",
                                "branch_points_to": {"main": "r2"},
                                "remote_branch_points_to": {"origin/main": "r2"},
                                "rules": [
                                    {"type": "commit_count_equals", "count": 1},
                                    meta_equals("last_clone_shallow", True),
                                ],
                            },
                            required=["git clone --depth"],
                            graph={
                                "from": "remote history r0 -> r1 -> r2",
                                "to": "local shallow main -> r2",
                            },
                            concepts=["shallow clone", "local copy of remote tip"],
                        ),
                    )
                ],
            ),
        ],
    ),
    challenge(
        "tracking-changes-snapshots",
        "compose-clean-history",
        "Compose Clean History",
        "Turn workspace changes into focused commits while keeping accidental files out of history.",
        "This is the first Challenge that creates new local commits. The learner should see branch tips move because they authored snapshots, not because they guessed commands.",
        [
            level(
                "easy",
                story="A tracked file was edited for the setup page.",
                task="Save that edit as a new commit on main.",
                before="main -> c0; README is modified in the working tree.",
                after="main moves to a new commit containing README.md; workspace is clean.",
                uses_adventure_levels=[
                    "inspect-status",
                    "inspect-working-diff",
                    "stage-one-file",
                    "commit-staged-snapshot",
                ],
                min_counted_commands=2,
                max_counted_commands=5,
                variants=[
                    variant(
                        "easy-commit-readme-edit",
                        "Commit README edit",
                        story="The setup note is ready; it should become the next snapshot.",
                        task="Save the README change as a commit.",
                        before="main -> c0; README.md modified",
                        after="main -> c1 with README.md changed",
                        initial=repo(
                            commits=SNAPSHOT_BASE,
                            working_tree={
                                "README.md": {
                                    "status": "modified",
                                    "content": "Portal\nSetup instructions\n",
                                }
                            },
                        ),
                        solution=["git add README.md", 'git commit -m "Update setup notes"'],
                        evaluation=_contract(
                            {
                                "latest_commit": {
                                    "branch": "main",
                                    "contains_paths": ["README.md"],
                                    "message_contains": ["setup"],
                                },
                                "working_tree_clean": True,
                                "staging_empty": True,
                                "rules": [
                                    {
                                        "type": "commit_parent_count_equals",
                                        "branch": "main",
                                        "count": 1,
                                    }
                                ],
                            },
                            required=["git add", "git commit"],
                            graph={"from": "main -> c0", "to": "main -> new commit after c0"},
                            concepts=["stage selected file", "commit staged snapshot"],
                        ),
                    )
                ],
            ),
            level(
                "medium",
                story="A useful app change and a messy local scratch file are present together in the workspace.",
                task="Commit only the source change and leave the scratch file outside history.",
                before="main -> c0; src/app.py modified; scratch.txt untracked.",
                after="main moves to a source-change commit; scratch.txt remains local only.",
                uses_adventure_levels=[
                    "inspect-status",
                    "inspect-working-diff",
                    "stage-one-file",
                    "commit-staged-snapshot",
                ],
                min_counted_commands=2,
                max_counted_commands=6,
                boss={"species": "slime", "hp": 4},
                variants=[
                    variant(
                        "medium-commit-source-not-scratch",
                        "Commit source only",
                        story="The app change belongs in history; the scratch note does not.",
                        task="Create a focused source commit without capturing the scratch file.",
                        before="main -> c0; app edit plus local scratch file",
                        after="main -> new app commit; scratch.txt remains untracked",
                        initial=repo(
                            commits=SNAPSHOT_BASE,
                            working_tree={
                                "src/app.py": {
                                    "status": "modified",
                                    "content": "print('hello')\nprint('setup')\n",
                                },
                                "scratch.txt": {"status": "untracked", "content": "delete later\n"},
                            },
                        ),
                        solution=["git add src/app.py", 'git commit -m "Update app setup"'],
                        evaluation=_contract(
                            {
                                "latest_commit": {
                                    "branch": "main",
                                    "contains_paths": ["src/app.py"],
                                    "excludes_paths": ["scratch.txt"],
                                    "message_contains": ["setup"],
                                },
                                "working_tree_contains": ["scratch.txt"],
                                "staging_empty": True,
                            },
                            required=["git add", "git commit"],
                            forbidden=["git add .", "git add -A"],
                            graph={
                                "from": "main -> c0 with mixed workspace edits",
                                "to": "main -> focused commit; scratch outside DAG",
                            },
                            concepts=["selective staging", "untracked file exclusion"],
                        ),
                    )
                ],
            ),
            level(
                "hard",
                story="A secret file was accidentally tracked in the previous snapshot, but the local file is still needed for development.",
                task="Remove the secret from the next repository snapshot while preserving it locally.",
                before="main -> c0 contains .env.",
                after="main moves to a commit where .env is no longer tracked, but the local file still exists outside history.",
                uses_adventure_levels=[
                    "stop-tracking-local-file",
                    "commit-staged-snapshot",
                    "inspect-staged-diff",
                ],
                min_counted_commands=2,
                max_counted_commands=6,
                variants=[
                    variant(
                        "hard-stop-tracking-env",
                        "Stop tracking secret",
                        story="The secret should disappear from the committed tree without deleting the developer's local copy.",
                        task="Create a cleanup commit that stops tracking the secret file.",
                        before="main -> c0 includes .env",
                        after="main -> cleanup commit excludes .env; working tree keeps local .env",
                        initial=repo(commits=SNAPSHOT_WITH_SECRET),
                        solution=[
                            "git rm --cached .env",
                            'git commit -m "Stop tracking local env"',
                        ],
                        evaluation=_contract(
                            {
                                "latest_commit": {
                                    "branch": "main",
                                    "contains_paths": [".env"],
                                    "message_contains": ["env"],
                                },
                                "rules": [
                                    {
                                        "type": "tracked_path_removed_from_commit_tree",
                                        "path": ".env",
                                    },
                                    {"type": "ignored_paths_present", "paths": [".env"]},
                                ],
                                "staging_empty": True,
                            },
                            required=["git rm --cached", "git commit"],
                            graph={
                                "from": "main -> c0 with secret in tree",
                                "to": "main -> cleanup commit removing secret from tree",
                            },
                            concepts=["remove from index", "preserve local file", "cleanup commit"],
                        ),
                    )
                ],
            ),
        ],
    ),
    challenge(
        "branching-switching",
        "branch-the-workstream",
        "Branch the Workstream",
        "Move work onto the correct branch so commit history separates tasks instead of tangling them.",
        "Branch Challenges are about visible refs: creating branch pointers, moving HEAD, and making commits where the diagram says they belong.",
        [
            level(
                "easy",
                story="A feature task should not be committed directly on main.",
                task="Create a feature branch and save the new menu file there.",
                before="main -> c1; menu file is untracked.",
                after="feature/menu points to a new commit; main still points to c1.",
                uses_adventure_levels=[
                    "create-and-switch-branch",
                    "stage-one-file",
                    "commit-staged-snapshot",
                ],
                min_counted_commands=3,
                max_counted_commands=7,
                variants=[
                    variant(
                        "easy-feature-branch-commit",
                        "Feature branch commit",
                        story="The menu work is ready, but it belongs on its own branch.",
                        task="Create the feature branch and commit the menu file there.",
                        before="main -> c1; src/menu.py untracked",
                        after="main -> c1; feature/menu -> new commit containing src/menu.py",
                        initial=repo(
                            commits=BRANCH_BASE,
                            branches={"main": "c1"},
                            working_tree={
                                "src/menu.py": {"status": "untracked", "content": "items=[]\n"}
                            },
                        ),
                        solution=[
                            "git switch -c feature/menu",
                            "git add src/menu.py",
                            'git commit -m "Add menu draft"',
                        ],
                        evaluation=_contract(
                            {
                                "head_branch": "feature/menu",
                                "branch_points_to": {"main": "c1"},
                                "latest_commit": {
                                    "branch": "feature/menu",
                                    "contains_paths": ["src/menu.py"],
                                    "message_contains": ["menu"],
                                },
                                "working_tree_clean": True,
                                "staging_empty": True,
                            },
                            required=["git switch -c", "git add", "git commit"],
                            graph={
                                "from": "main -> c1",
                                "to": "main -> c1; feature/menu -> new child commit",
                            },
                            concepts=["create branch", "switch HEAD", "commit on current branch"],
                        ),
                    )
                ],
            ),
            level(
                "medium",
                story="A hotfix must be based on the older release point, not on the newest dashboard work.",
                task="Create the hotfix branch pointer at the correct older commit and check it out.",
                before="main -> c2, but the release point is c1.",
                after="hotfix/login points to c1 while main remains at c2.",
                uses_adventure_levels=[
                    "create-branch-at-start-point",
                    "switch-existing-branch",
                    "inspect-graph-history",
                ],
                min_counted_commands=2,
                max_counted_commands=5,
                variants=[
                    variant(
                        "medium-hotfix-from-release-point",
                        "Hotfix from older commit",
                        story="The dashboard commit is not part of the release line, so the hotfix branch must start from c1.",
                        task="Create the hotfix branch at the release point and move onto it.",
                        before="main -> c2; release point c1",
                        after="main -> c2; hotfix/login -> c1; HEAD on hotfix/login",
                        initial=repo(commits=BRANCH_LONG, branches={"main": "c2"}),
                        solution=["git branch hotfix/login c1", "git switch hotfix/login"],
                        evaluation=_contract(
                            {
                                "head_branch": "hotfix/login",
                                "branch_points_to": {"main": "c2", "hotfix/login": "c1"},
                                "working_tree_clean": True,
                            },
                            required=["git branch", "git switch"],
                            graph={
                                "from": "c0 -> c1 -> c2(main)",
                                "to": "hotfix/login points at c1 while main stays at c2",
                            },
                            concepts=["branch from start point", "switch existing branch"],
                        ),
                    )
                ],
            ),
            level(
                "hard",
                story="A branch pointer is cluttering the graph even though its work is already reachable from main.",
                task="Remove the merged branch pointer without moving main.",
                before="main -> c2; old branch pointer review/menu -> c1, which is already behind main.",
                after="review/menu is gone; main still points to c2.",
                uses_adventure_levels=["delete-merged-branch", "inspect-graph-history"],
                min_counted_commands=1,
                max_counted_commands=4,
                variants=[
                    variant(
                        "hard-delete-merged-review-branch",
                        "Delete merged branch",
                        story="The review branch is already contained in main; keeping it only makes the diagram noisy.",
                        task="Delete the safe merged branch pointer.",
                        before="main -> c2; review/menu -> c1",
                        after="main -> c2; review/menu absent",
                        initial=repo(
                            commits=BRANCH_LONG,
                            branches={"main": "c2", "review/menu": "c1"},
                            head="main",
                        ),
                        solution=["git branch -d review/menu"],
                        evaluation=_contract(
                            {
                                "branch_points_to": {"main": "c2"},
                                "branch_absent": ["review/menu"],
                                "rules": [meta_equals("last_branch_deleted", "review/menu")],
                            },
                            required=["git branch -d"],
                            graph={
                                "from": "main and stale review/menu refs visible",
                                "to": "stale review/menu ref removed",
                            },
                            concepts=["delete merged branch", "ref cleanup"],
                        ),
                    )
                ],
            ),
        ],
    ),
    challenge(
        "merging-conflicts",
        "integrate-diverging-history",
        "Integrate Diverging History",
        "Move branch histories together while preserving the shape of the work.",
        "Merge Challenges make the DAG change in the most visible way: a branch tip moves, a merge commit appears, or a conflict must be resolved before history can continue.",
        [
            level(
                "easy",
                story="Main is behind a completed feature branch and can move forward cleanly.",
                task="Integrate the feature branch by moving main to the feature tip.",
                before="main -> c0; feature/menu -> f1 where c0 is its parent.",
                after="main and feature/menu both point to f1.",
                uses_adventure_levels=["merge-fast-forward-branch", "inspect-graph-history"],
                min_counted_commands=1,
                max_counted_commands=4,
                variants=[
                    variant(
                        "easy-fast-forward-menu",
                        "Fast-forward feature",
                        story="No one added new commits to main after the feature branch started.",
                        task="Bring main forward to the feature tip.",
                        before="main -> c0; feature/menu -> f1",
                        after="main -> f1; feature/menu -> f1",
                        initial=repo(
                            commits=[MERGE_BASE[0], MERGE_BASE[2]],
                            branches={"main": "c0", "feature/menu": "f1"},
                            head="main",
                        ),
                        solution=["git merge feature/menu"],
                        evaluation=_contract(
                            {
                                "branch_points_to": {"main": "f1", "feature/menu": "f1"},
                                "rules": [meta_equals("last_merge_fast_forward", True)],
                                "working_tree_clean": True,
                            },
                            required=["git merge"],
                            graph={
                                "from": "main behind feature/menu",
                                "to": "main fast-forwards to feature/menu",
                            },
                            concepts=["fast-forward merge", "branch pointer movement"],
                        ),
                    )
                ],
            ),
            level(
                "medium",
                story="Both main and the feature branch have useful commits, so history should record the integration point.",
                task="Create a merge commit that connects the two branch histories.",
                before="main -> m1 and feature/menu -> f1 diverge from c0.",
                after="main points to a merge commit with parents m1 and f1.",
                uses_adventure_levels=["merge-with-merge-commit", "inspect-graph-history"],
                min_counted_commands=1,
                max_counted_commands=4,
                variants=[
                    variant(
                        "medium-no-ff-menu-merge",
                        "Merge with integration commit",
                        story="The team wants the diagram to show when the feature branch was integrated.",
                        task="Merge the feature branch with a merge commit.",
                        before="c0 splits into m1(main) and f1(feature/menu)",
                        after="main -> merge commit with parents m1 and f1",
                        initial=repo(
                            commits=MERGE_BASE,
                            branches={"main": "m1", "feature/menu": "f1"},
                            head="main",
                        ),
                        solution=["git merge --no-ff feature/menu"],
                        evaluation=_contract(
                            {
                                "latest_commit": {
                                    "branch": "main",
                                    "contains_paths": ["src/menu.py"],
                                    "message_contains": ["Merge"],
                                },
                                "rules": [
                                    {"type": "commit_is_merge", "branch": "main"},
                                    {"type": "commit_has_parent", "branch": "main", "parent": "m1"},
                                    {"type": "commit_has_parent", "branch": "main", "parent": "f1"},
                                ],
                                "working_tree_clean": True,
                            },
                            required=["git merge --no-ff"],
                            graph={
                                "from": "two diverged branch tips",
                                "to": "new merge commit joins both histories",
                            },
                            concepts=["merge commit", "two-parent history"],
                        ),
                    )
                ],
            ),
            level(
                "hard",
                story="Both branches edited the same auth setting, so integration stops until the conflict is resolved.",
                task="Resolve the conflict and finish the merge so the diagram has a clean merge commit.",
                before="main -> m1 and feature/auth-timeout -> f1 diverge from c0 with conflicting edits.",
                after="main points to a merge commit with both parents and no conflict state.",
                uses_adventure_levels=[
                    "merge-fast-forward-branch",
                    "choose-their-conflict-side",
                    "continue-resolved-merge",
                    "stage-one-file",
                ],
                min_counted_commands=3,
                max_counted_commands=8,
                variants=[
                    variant(
                        "hard-resolve-auth-timeout-conflict",
                        "Resolve timeout conflict",
                        story="The feature branch has the accepted auth behavior, but main also changed the same file.",
                        task="Finish the merge with the accepted auth file content and no remaining conflicts.",
                        before="c0 splits into m1(main) and f1(feature/auth-timeout); src/auth.js conflicts",
                        after="main -> merge commit with parents m1 and f1; src/auth.js resolved",
                        initial=repo(
                            commits=CONFLICT_HISTORY,
                            branches={"main": "m1", "feature/auth-timeout": "f1"},
                            head="main",
                        ),
                        solution=[
                            "git merge feature/auth-timeout",
                            "git add src/auth.js",
                            "git merge --continue",
                        ],
                        workspace_files=[
                            {
                                "after_command_index": 1,
                                "path": "src/auth.js",
                                "content": "timeout=2500\nmode='strict'\n",
                            }
                        ],
                        evaluation=_contract(
                            {
                                "latest_commit": {
                                    "branch": "main",
                                    "contains_paths": ["src/auth.js"],
                                    "message_contains": ["Merge"],
                                },
                                "conflict_free": True,
                                "staging_empty": True,
                                "rules": [
                                    {"type": "commit_is_merge", "branch": "main"},
                                    {"type": "commit_has_parent", "branch": "main", "parent": "m1"},
                                    {"type": "commit_has_parent", "branch": "main", "parent": "f1"},
                                    {
                                        "type": "commit_tree_contains",
                                        "branch": "main",
                                        "tree": {"src/auth.js": "timeout=2500\nmode='strict'\n"},
                                    },
                                ],
                            },
                            required=["git merge", "git add", "git merge --continue"],
                            graph={
                                "from": "diverged branches with conflict",
                                "to": "resolved two-parent merge commit",
                            },
                            concepts=[
                                "conflict resolution",
                                "staging resolved file",
                                "continue merge",
                            ],
                            engine_notes=[
                                "Challenge depends on workspace-file edit support between merge and add."
                            ],
                        ),
                    )
                ],
            ),
        ],
    ),
    challenge(
        "undoing-recovery",
        "recover-history-safely",
        "Recover History Safely",
        "Choose the undo move based on whether history is local, shared, or just wrongly described.",
        "Recovery Challenges must feel like real Git mistakes: the right solution depends on what the diagram says has already been shared.",
        [
            level(
                "easy",
                story="The latest local commit has the right file change but the wrong message, and it has not been shared.",
                task="Replace the latest local commit with a corrected message.",
                before="main -> c1 with an unclear local commit message.",
                after="main points to a replacement commit; the old local commit is recorded as replaced.",
                uses_adventure_levels=["amend-latest-commit-message", "inspect-compact-history"],
                min_counted_commands=1,
                max_counted_commands=4,
                variants=[
                    variant(
                        "easy-amend-local-message",
                        "Amend local message",
                        story="The latest local commit says 'stuff', but the change is actually the login copy.",
                        task="Correct the latest commit message without adding another commit on top.",
                        before="main -> c1 ('stuff')",
                        after="main -> replacement commit with clearer message",
                        initial=repo(
                            commits=[
                                commit("c0", "Initial portal", [], {"README.md": "Portal\n"}),
                                commit(
                                    "c1",
                                    "stuff",
                                    ["c0"],
                                    {"README.md": "Portal\n", "src/login.py": "copy\n"},
                                ),
                            ],
                            branches={"main": "c1"},
                        ),
                        solution=['git commit --amend -m "Add login copy"'],
                        evaluation=_contract(
                            {
                                "latest_commit": {
                                    "branch": "main",
                                    "contains_paths": ["src/login.py"],
                                    "message_contains": ["login"],
                                },
                                "rules": [
                                    {"type": "commit_replaced_by_amend", "old": "c1"},
                                    {
                                        "type": "branch_tip_replaces_commit",
                                        "old": "c1",
                                        "branch": "main",
                                    },
                                    {
                                        "type": "commit_not_followed_by_extra_commit",
                                        "branch": "main",
                                    },
                                ],
                            },
                            required=["git commit --amend"],
                            graph={
                                "from": "main -> c1",
                                "to": "main -> replacement commit, not c1 -> extra commit",
                            },
                            concepts=["amend local commit", "replace tip"],
                        ),
                    )
                ],
            ),
            level(
                "medium",
                story="The latest local commit is wrong and has not been pushed anywhere. Riko, who wrote the broken route, needs it cleaned up.",
                task="Move main back to the last good commit and clean the files.",
                before="main -> c2, but c2 is a bad local commit.",
                after="main points back to c1 with a clean workspace.",
                uses_adventure_levels=["reset-hard-specific-commit", "inspect-reflog-for-recovery"],
                min_counted_commands=1,
                max_counted_commands=4,
                boss={"species": "werewolf", "hp": 4},
                variants=[
                    variant(
                        "medium-reset-local-bad-tip",
                        "Reset bad local tip",
                        story="The broken login route was never shared, so the local branch can move back.",
                        task="Return main to the last good commit.",
                        before="main -> c2 (bad local tip)",
                        after="main -> c1; workspace clean",
                        initial=repo(commits=RECOVERY_HISTORY, branches={"main": "c2"}),
                        solution=["git reset --hard c1"],
                        evaluation=_contract(
                            {
                                "branch_points_to": {"main": "c1"},
                                "working_tree_clean": True,
                                "staging_empty": True,
                                "rules": [
                                    {"type": "branch_moved_to", "branch": "main", "commit": "c1"}
                                ],
                            },
                            required=["git reset --hard"],
                            graph={"from": "main -> c2", "to": "main moved back to c1"},
                            concepts=["local history rewrite", "hard reset"],
                        ),
                    )
                ],
            ),
            level(
                "hard",
                story="The bad commit is already on the shared remote branch, so deleting it would rewrite public history.",
                task="Add a new commit that reverses the bad change while preserving the shared commit in history.",
                before="main and origin/main both point to bad commit c2.",
                after="main points to a new revert commit after c2; c2 remains in the history behind it.",
                uses_adventure_levels=["revert-shared-commit", "inspect-graph-history"],
                min_counted_commands=1,
                max_counted_commands=5,
                variants=[
                    variant(
                        "hard-revert-shared-login-break",
                        "Revert shared breakage",
                        story="The bad login change is shared; the team needs an undo commit, not branch surgery.",
                        task="Reverse the bad commit without deleting it from history.",
                        before="origin/main -> c2 and main -> c2",
                        after="main -> new revert commit whose parent is c2; c2 still exists behind it",
                        initial=repo(
                            commits=RECOVERY_HISTORY,
                            branches={"main": "c2"},
                            remote_branches={"origin/main": "c2"},
                            upstream_tracking={"main": "origin/main"},
                            remotes={"origin": "https://example.test/team/app.git"},
                        ),
                        solution=["git revert c2"],
                        evaluation=_contract(
                            {
                                "latest_commit": {"branch": "main", "message_contains": ["Revert"]},
                                "rules": [
                                    {"type": "new_revert_commit_exists"},
                                    {
                                        "type": "revert_preserves_history",
                                        "branch": "main",
                                        "commit": "c2",
                                    },
                                    {
                                        "type": "commit_parent_equals",
                                        "branch": "main",
                                        "parent": "c2",
                                    },
                                ],
                                "working_tree_clean": True,
                            },
                            required=["git revert"],
                            forbidden=["git reset --hard"],
                            graph={
                                "from": "main/origin-main -> c2",
                                "to": "main -> revert commit after c2; c2 preserved",
                            },
                            concepts=["shared-history undo", "revert commit"],
                        ),
                    )
                ],
            ),
        ],
    ),
    challenge(
        "temporary-work-patches",
        "pause-and-transplant-work",
        "Pause and Transplant Work",
        "Use stash and cherry-pick when normal branch flow would move too much or lose local work.",
        "These scenarios show that not every fix belongs to a full merge. Sometimes the DAG should receive one selected commit, while unfinished workspace edits stay out of the way.",
        [
            level(
                "easy",
                story="You started editing docs on main, but a clean branch switch is needed for a review task.",
                task="Shelve the work-in-progress and switch to the review branch.",
                before="main -> c1 with modified docs; review/menu -> c1 exists.",
                after="HEAD is on review/menu; the docs edit is in the stash, not the working tree.",
                uses_adventure_levels=["stash-local-work", "switch-existing-branch"],
                min_counted_commands=2,
                max_counted_commands=5,
                variants=[
                    variant(
                        "easy-stash-before-review-switch",
                        "Stash before switch",
                        story="The docs edit is unfinished, but you need to inspect the review branch now.",
                        task="Pause the local edit and move to the review branch.",
                        before="main checked out with docs/release.md modified",
                        after="review/menu checked out; stash contains docs/release.md",
                        initial=repo(
                            commits=BRANCH_BASE,
                            branches={"main": "c1", "review/menu": "c1"},
                            head="main",
                            working_tree={
                                "docs/release.md": {"status": "modified", "content": "draft\n"}
                            },
                        ),
                        solution=["git stash", "git switch review/menu"],
                        evaluation=_contract(
                            {
                                "head_branch": "review/menu",
                                "working_tree_clean": True,
                                "rules": [
                                    {
                                        "type": "stash_stack_contains_paths",
                                        "paths": ["docs/release.md"],
                                    }
                                ],
                            },
                            required=["git stash", "git switch"],
                            graph={
                                "from": "HEAD on main with dirty workspace",
                                "to": "HEAD on review/menu; WIP stored outside DAG",
                            },
                            concepts=["stash before switch", "clean branch movement"],
                        ),
                    )
                ],
            ),
            level(
                "medium",
                story="Only the login-crash fix belongs on the release branch; the rest of the bugfix branch is not ready.",
                task="Copy the single fix commit onto release without merging the whole bugfix branch.",
                before="release -> r1; bugfix/login -> b2, with useful fix b1 behind it.",
                after="release points to a new commit copied from b1; b2 is not in release history.",
                uses_adventure_levels=["cherry-pick-one-commit", "inspect-graph-history"],
                min_counted_commands=1,
                max_counted_commands=5,
                variants=[
                    variant(
                        "medium-cherry-pick-login-fix",
                        "Cherry-pick one fix",
                        story="The first bugfix commit is approved; the later experiment must stay off release.",
                        task="Transplant only the approved fix onto release.",
                        before="release -> r1; bugfix/login -> b2 with b1 behind it",
                        after="release -> new commit with b1 changes; release history excludes b2",
                        initial=repo(
                            commits=PATCH_HISTORY,
                            branches={"release": "r1", "bugfix/login": "b2"},
                            head="release",
                        ),
                        solution=["git cherry-pick b1"],
                        evaluation=_contract(
                            {
                                "latest_commit": {
                                    "branch": "release",
                                    "contains_paths": ["src/login.py"],
                                    "message_contains": ["login"],
                                },
                                "rules": [
                                    {
                                        "type": "cherry_pick_created_new_commit",
                                        "source": "b1",
                                        "branch": "release",
                                    },
                                    {
                                        "type": "branch_history_excludes",
                                        "branch": "release",
                                        "commits": ["b2"],
                                    },
                                ],
                            },
                            required=["git cherry-pick"],
                            graph={
                                "from": "release separate from bugfix branch",
                                "to": "release gets a copied fix commit, not bugfix branch history",
                            },
                            concepts=["cherry-pick", "single-commit transplant"],
                        ),
                    )
                ],
            ),
            level(
                "hard",
                story="A release branch has local notes in progress, but an approved hotfix commit must be copied and published cleanly later.",
                task="Shelve the notes, copy the hotfix commit onto release, and leave the release branch clean.",
                before="release -> r1 with notes.txt untracked; bugfix/login has approved commit b1.",
                after="release points to a copied login-fix commit; notes.txt is safely stashed.",
                uses_adventure_levels=[
                    "stash-local-work",
                    "cherry-pick-one-commit",
                    "inspect-status",
                ],
                min_counted_commands=2,
                max_counted_commands=7,
                variants=[
                    variant(
                        "hard-stash-then-pick-release-fix",
                        "Stash then pick fix",
                        story="The release notes are not ready, but the login fix is approved for release.",
                        task="Keep the notes out of the commit and copy the fix onto release.",
                        before="release -> r1; notes.txt untracked; bugfix/login -> b1",
                        after="release -> copied login fix; notes.txt in stash; workspace clean",
                        initial=repo(
                            commits=PATCH_HISTORY[:3],
                            branches={"release": "r1", "bugfix/login": "b1"},
                            head="release",
                            working_tree={
                                "notes.txt": {"status": "untracked", "content": "release draft\n"}
                            },
                        ),
                        solution=["git stash", "git cherry-pick b1"],
                        evaluation=_contract(
                            {
                                "latest_commit": {
                                    "branch": "release",
                                    "contains_paths": ["src/login.py"],
                                    "message_contains": ["login"],
                                },
                                "working_tree_clean": True,
                                "rules": [
                                    {"type": "stash_stack_contains_paths", "paths": ["notes.txt"]},
                                    {
                                        "type": "cherry_pick_created_new_commit",
                                        "source": "b1",
                                        "branch": "release",
                                    },
                                ],
                            },
                            required=["git stash", "git cherry-pick"],
                            graph={
                                "from": "release with dirty workspace and separate bugfix commit",
                                "to": "release advances by copied fix; WIP kept outside DAG",
                            },
                            concepts=["stash WIP", "cherry-pick after cleanup"],
                        ),
                    )
                ],
            ),
        ],
    ),
    challenge(
        "remotes-collaboration",
        "coordinate-with-remote-history",
        "Coordinate with Remote History",
        "Use remote-tracking refs to decide whether to fetch, pull, merge, or publish.",
        "The final storey combines collaboration with the earlier graph skills. The target is not 'use push'; it is 'make local and remote refs tell the right story.'",
        [
            level(
                "easy",
                story="The remote has a new review commit, but local main should not move until the learner decides to integrate it.",
                task="Refresh the remote-tracking branch without moving local main.",
                before="main -> c1; origin/main -> c1 locally, but the remote now has r2.",
                after="origin/main -> r2 while local main still points to c1.",
                uses_adventure_levels=[
                    "fetch-origin-updates",
                    "inspect-remote-urls",
                    "inspect-graph-history",
                ],
                min_counted_commands=1,
                max_counted_commands=4,
                variants=[
                    variant(
                        "easy-fetch-remote-review",
                        "Fetch remote review",
                        story="You need to see what changed on the remote before integrating anything.",
                        task="Update the remote-tracking branch only.",
                        before="main -> c1; origin/main -> c1; remote has r2",
                        after="main -> c1; origin/main -> r2",
                        initial=repo(
                            commits=REMOTE_BASE,
                            branches={"main": "c1"},
                            remote_branches={"origin/main": "c1"},
                            upstream_tracking={"main": "origin/main"},
                            remotes={"origin": "https://example.test/team/app.git"},
                            remote_updates={"origin/main": "r2"},
                            remote_fixtures=REMOTE_FIXTURE_AHEAD,
                        ),
                        solution=["git fetch origin"],
                        evaluation=_contract(
                            {
                                "branch_points_to": {"main": "c1"},
                                "remote_branch_points_to": {"origin/main": "r2"},
                                "rules": [
                                    {
                                        "type": "fetch_updated_remote_tracking_without_moving_local",
                                        "branch": "main",
                                    }
                                ],
                            },
                            required=["git fetch"],
                            graph={
                                "from": "local main and origin/main both c1",
                                "to": "origin/main advances to r2; main stays c1",
                            },
                            concepts=["fetch", "remote-tracking ref", "local branch unchanged"],
                        ),
                    )
                ],
            ),
            level(
                "medium",
                story="The remote update is ready, and local main has no extra commits.",
                task="Bring local main up to its upstream tip.",
                before="main -> c1; origin/main will update to r2.",
                after="main and origin/main both point to r2.",
                uses_adventure_levels=[
                    "pull-fast-forward-update",
                    "fetch-origin-updates",
                    "inspect-graph-history",
                ],
                min_counted_commands=1,
                max_counted_commands=4,
                variants=[
                    variant(
                        "medium-pull-fast-forward-review",
                        "Pull fast-forward review",
                        story="The remote review note can be integrated as a simple forward move.",
                        task="Update local main to match upstream.",
                        before="main -> c1; remote update r2 exists upstream",
                        after="main -> r2 and origin/main -> r2",
                        initial=repo(
                            commits=REMOTE_BASE,
                            branches={"main": "c1"},
                            remote_branches={"origin/main": "c1"},
                            upstream_tracking={"main": "origin/main"},
                            remotes={"origin": "https://example.test/team/app.git"},
                            remote_updates={"origin/main": "r2"},
                            remote_fixtures=REMOTE_FIXTURE_AHEAD,
                        ),
                        solution=["git pull"],
                        evaluation=_contract(
                            {
                                "branch_points_to": {"main": "r2"},
                                "remote_branch_points_to": {"origin/main": "r2"},
                                "rules": [
                                    {
                                        "type": "pull_moved_local_to_upstream",
                                        "branch": "main",
                                        "upstream": "origin/main",
                                    }
                                ],
                                "working_tree_clean": True,
                            },
                            required=["git pull"],
                            graph={
                                "from": "main behind upstream",
                                "to": "main fast-forwards to origin/main",
                            },
                            concepts=["pull", "upstream fast-forward"],
                        ),
                    )
                ],
            ),
            level(
                "hard",
                story="Local main and remote main both advanced from the same base; the release must preserve both histories and publish the result.",
                task="Refresh remote refs, integrate remote main into local main, then publish the merged history.",
                before="main -> l2 and origin/main -> c1 locally; the remote has r2 from the same base c1.",
                after="main points to a merge commit with parents l2 and r2, and origin/main points to that same merge commit.",
                uses_adventure_levels=[
                    "fetch-origin-updates",
                    "merge-with-merge-commit",
                    "push-current-branch",
                    "inspect-graph-history",
                ],
                min_counted_commands=3,
                max_counted_commands=9,
                variants=[
                    variant(
                        "hard-merge-remote-and-publish",
                        "Merge remote and publish",
                        story="Your release note and the remote review note both belong in the final shared branch.",
                        task="Update remote tracking, merge the remote history, and publish the integrated result.",
                        before="main -> l2; origin/main -> c1; remote update r2 exists",
                        after="main -> merge commit with parents l2/r2; origin/main -> same merge commit",
                        initial=repo(
                            commits=REMOTE_DIVERGED,
                            branches={"main": "l2"},
                            remote_branches={"origin/main": "c1"},
                            upstream_tracking={"main": "origin/main"},
                            remotes={"origin": "https://example.test/team/app.git"},
                            remote_updates={"origin/main": "r2"},
                            remote_fixtures={
                                "branches": {"origin/main": "r2"},
                                "default_branch": "origin/main",
                                "commits": [REMOTE_DIVERGED[-1]],
                            },
                        ),
                        solution=["git fetch origin", "git merge origin/main", "git push"],
                        evaluation=_contract(
                            {
                                "remote_branch_matches_local": {"origin/main": "main"},
                                "latest_commit": {
                                    "branch": "main",
                                    "contains_paths": ["review.md"],
                                    "message_contains": ["Merge"],
                                },
                                "rules": [
                                    {"type": "commit_is_merge", "branch": "main"},
                                    {"type": "commit_has_parent", "branch": "main", "parent": "l2"},
                                    {"type": "commit_has_parent", "branch": "main", "parent": "r2"},
                                    {
                                        "type": "push_moved_remote_to_local_tip",
                                        "branch": "main",
                                        "remote_branch": "origin/main",
                                    },
                                ],
                                "working_tree_clean": True,
                            },
                            required=["git fetch", "git merge", "git push"],
                            graph={
                                "from": "local and remote diverged after c1",
                                "to": "published merge commit joins l2 and r2",
                            },
                            concepts=[
                                "fetch before integrate",
                                "merge remote-tracking ref",
                                "publish merged result",
                            ],
                        ),
                    )
                ],
            ),
        ],
    ),
]
