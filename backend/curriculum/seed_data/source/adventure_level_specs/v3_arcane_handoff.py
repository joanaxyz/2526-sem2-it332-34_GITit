"""Final beginner retrieval workflows for the Arcane Spire.

These are not a separate capstone type. They are ordinary adventure levels in
Arcane Chapter 8 and prepare the learner for that chapter's standard challenge.
"""

from __future__ import annotations

from .common import commit, ev, q, repo, v


def _commits(prefix: str) -> list[dict]:
    return [
        commit(
            f"{prefix}0",
            "Awaken the Chronicle",
            [],
            {"README.md": "Arcane Chronicle\n", "src/core.py": "mode = 'base'\n"},
        ),
        commit(
            f"{prefix}1",
            "Restore the signal chamber",
            [f"{prefix}0"],
            {"README.md": "Arcane Chronicle\n", "src/core.py": "mode = 'signal'\n"},
        ),
    ]


def _variant(
    *,
    case_id: str,
    label: str,
    prefix: str,
    branch: str,
    path: str,
    initial: dict,
    solution: list[str],
    message: str,
) -> dict:
    return v(
        case_id,
        label,
        initial,
        solution,
        ev(
            {
                "head_branch": "main",
                "latest_commit": {
                    "branch": "main",
                    "contains_paths": [path],
                    "message_contains": [message],
                },
                "working_tree_clean": True,
                "staging_empty": True,
                "branch_exists": [branch],
                "min_commits_on_branch": {"main": 3},
                "rules": [
                    {
                        "type": "required_command_sequence",
                        "commands": ["git merge", "git log"],
                    }
                ],
            },
            required=["git status", "git switch -c", "git add", "git commit", "git merge", "git log"],
        ),
    )


def _handoff_variants(slug: str, suffix: str) -> list[dict]:
    rows: list[dict] = []

    branch = f"repair/{suffix}-maps"
    path = "maps/northern-route.md"
    initial = repo(
        commits=_commits("h"),
        branches={"main": "h1"},
        head="main",
        working_tree={path: {"status": "untracked", "content": "Northern route restored\n"}},
    )
    rows.append(
        _variant(
            case_id=f"{slug}-branch-forward",
            label="Record the map repair on a branch, then fast-forward it",
            prefix="h",
            branch=branch,
            path=path,
            initial=initial,
            solution=[
                "git status",
                "git log --oneline --graph --all",
                f"git switch -c {branch}",
                f"git add {path}",
                "git commit -m 'Restore route maps'",
                "git switch main",
                f"git merge {branch}",
                "git log --oneline --graph --all",
            ],
            message="Restore route maps",
        )
    )

    branch = f"repair/{suffix}-lens"
    path = "src/lens.py"
    commits = _commits("i") + [
        commit(
            "i2",
            "Document the handoff",
            ["i1"],
            {"README.md": "Arcane Chronicle ready for Guild review\n", "src/core.py": "mode = 'signal'\n"},
        )
    ]
    initial = repo(
        commits=commits,
        branches={"main": "i2"},
        head="main",
        working_tree={path: {"status": "untracked", "content": "alignment = 'corrected'\n"}},
    )
    rows.append(
        _variant(
            case_id=f"{slug}-divergent-merge",
            label="Repair from the earlier stable crystal and preserve the merge",
            prefix="i",
            branch=branch,
            path=path,
            initial=initial,
            solution=[
                "git status",
                "git show i1",
                f"git switch -c {branch} i1",
                f"git add {path}",
                "git commit -m 'Correct signal lens'",
                "git switch main",
                f"git merge --no-ff {branch}",
                "git log --oneline --graph --all",
            ],
            message="Merge",
        )
    )

    branch = f"repair/{suffix}-index"
    path = "src/index.py"
    initial = repo(
        commits=_commits("j"),
        branches={"main": "j1"},
        head="main",
        working_tree={path: {"status": "untracked", "content": "index = 'rebuilt'\n"}},
    )
    rows.append(
        _variant(
            case_id=f"{slug}-squash-handoff",
            label="Review the repair branch and hand it over as one snapshot",
            prefix="j",
            branch=branch,
            path=path,
            initial=initial,
            solution=[
                "git status",
                f"git switch -c {branch}",
                f"git add {path}",
                "git commit -m 'Draft rebuilt index'",
                "git switch main",
                f"git merge --squash {branch}",
                "git commit -m 'Rebuild archive index'",
                "git log --oneline --graph --all",
            ],
            message="Rebuild archive index",
        )
    )

    branch = f"repair/{suffix}-relay"
    path = "src/relay.py"
    initial = repo(
        commits=_commits("k"),
        branches={"main": "k1"},
        head="main",
        working_tree={path: {"status": "untracked", "content": "relay = 'guild-ready'\n"}},
        remotes={"origin": "https://example.test/guild/arcane-spire.git"},
        remote_branches={"origin/main": "k1"},
        upstream_tracking={"main": "origin/main"},
    )
    rows.append(
        _variant(
            case_id=f"{slug}-publish-handoff",
            label="Finish the relay repair and publish the reviewed main branch",
            prefix="k",
            branch=branch,
            path=path,
            initial=initial,
            solution=[
                "git remote -v",
                "git fetch origin",
                "git status",
                f"git switch -c {branch}",
                f"git add {path}",
                "git commit -m 'Prepare Guild relay'",
                "git switch main",
                f"git merge {branch}",
                "git push",
                "git log --oneline --graph --all",
            ],
            message="Prepare Guild relay",
        )
    )
    return rows


def _level(index: int, title: str, story: str, task: str) -> dict:
    slug = f"guild-handoff-workflow-{index}"
    return q(
        "git-status/plain",
        slug,
        title,
        story,
        task,
        _handoff_variants(slug, f"handoff-{index}"),
        checks=[
            {
                "label": "Inspect the repository before choosing a repair path.",
                "requirement": {"required_commands": ["git status"]},
            },
            {
                "label": "Record the repair on a dedicated branch.",
                "requirement": {"required_commands": ["git switch -c", "git commit"]},
            },
            {
                "label": "Integrate the branch into main and verify the DAG.",
                "requirement": {
                    "required_commands": ["git merge", "git log"],
                    "rules": [
                        {
                            "type": "required_command_sequence",
                            "commands": ["git merge", "git log"],
                        }
                    ],
                },
            },
        ],
        min_counted_commands=4,
        max_counted_commands=12,
        adventure="guild-archive-handoff-workflows",
        workflow=True,
        level_type="guided_workflow",
    )


LEVELS = [
    _level(
        1,
        "Prepare the Chronicle for Review",
        "Archivist Mira asks you to complete a late repair while the Guild checks every branch and snapshot in the Chronicle.",
        "Use the repository evidence to isolate the repair, record it cleanly, integrate it into main, and verify the resulting graph.",
    ),
    _level(
        2,
        "Complete the Signal-Chamber Handoff",
        "Warden Cael opens the Guild relay, but the final repository state differs across each review copy.",
        "Choose the correct branch and integration workflow for the selected copy, then leave main clean and auditable.",
    ),
]

__all__ = ["LEVELS"]
