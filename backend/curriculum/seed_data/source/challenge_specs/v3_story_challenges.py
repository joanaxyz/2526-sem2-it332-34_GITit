"""Chapter challenges for Arcane 8, Frostbound Citadel, and Neon Backstreets.

Every chapter challenge has Easy, Medium, and Hard trials.  Each trial has four
strategy-distinct variants and ends in a commit/ref change that is visible in
the live DAG. Read-only diagnostics are evidence-gathering steps, never the
whole solution.
"""

from __future__ import annotations

from curriculum.seed_data.chapters import CHAPTERS
from curriculum.seed_data.source.adventure_level_specs.v3_advanced_workflows import INCIDENTS
from curriculum.seed_data.source.challenge_specs.advanced_challenge_support import (
    ADVANCED_CHALLENGE_DIFFICULTY,
    advanced_challenge_scenario_copy,
    build_advanced_challenge_variant,
)
from curriculum.seed_data.source.challenge_specs.helpers import (
    _contract,
    challenge,
    level,
    variant,
)


def _advanced_challenge(incident) -> dict:
    chapter = next(item for item in CHAPTERS if item["slug"] == incident.chapter)
    trials = []
    for difficulty in ("easy", "medium", "hard"):
        diagnostic_commands = (
            (incident.diagnostic_commands[0],)
            if difficulty == "easy"
            else (incident.diagnostic_commands[1],)
            if difficulty == "medium"
            else incident.diagnostic_commands
        )
        variants = [
            build_advanced_challenge_variant(
                chapter_slug=incident.chapter,
                story_title=incident.story_title,
                chapter_title=chapter["title"],
                difficulty=difficulty,
                strategy=strategy,
                diagnostic_commands=diagnostic_commands,
                prefix=prefix,
                index=index,
            )
            for index, (strategy, prefix) in enumerate(
                (("author", "q"), ("transplant", "r"), ("integrate", "s"), ("revert", "t")),
                start=1,
            )
        ]
        story, task, after = advanced_challenge_scenario_copy(incident.story_title, chapter["title"], difficulty)
        trials.append(
            level(
                difficulty,
                story=story,
                task=task,
                before=ADVANCED_CHALLENGE_DIFFICULTY[difficulty]["before"],
                after=after,
                current="The repository provides graph, workspace, ref, and chapter-specific diagnostic evidence.",
                risk=ADVANCED_CHALLENGE_DIFFICULTY[difficulty]["risk"],
                min_counted_commands=ADVANCED_CHALLENGE_DIFFICULTY[difficulty]["min"],
                max_counted_commands=ADVANCED_CHALLENGE_DIFFICULTY[difficulty]["max"],
                uses_adventure_levels=[
                    f"{incident.chapter}-incident-1",
                    f"{incident.chapter}-incident-2",
                ],
                variants=variants,
            )
        )
    return challenge(
        incident.chapter,
        f"{incident.chapter}-challenge",
        f"Challenge: {chapter['title']}",
        (
            f"Use the commands introduced through {chapter['title']} together with earlier Git skills to "
            "produce and verify a visible repository correction."
        ),
        (
            f"The operational handoff for {chapter['title']} has failed. No character tells you which Git "
            "strategy to use; inspect the graph and complete the repair from repository state alone."
        ),
        trials,
    )


def _arcane_state(prefix: str, *, divergent: bool) -> dict:
    from curriculum.seed_data.spec_helpers import commit, repo

    commits = [
        commit(f"{prefix}0", "Awaken the Chronicle", [], {"README.md": "Chronicle\n"}),
        commit(f"{prefix}1", "Restore the signal", [f"{prefix}0"], {"README.md": "Chronicle\n", "src/signal.py": "ready = True\n"}),
    ]
    if divergent:
        commits.append(
            commit(f"{prefix}2", "Prepare Guild notes", [f"{prefix}1"], {"README.md": "Guild review\n", "src/signal.py": "ready = True\n"})
        )
    tip = f"{prefix}2" if divergent else f"{prefix}1"
    return repo(
        commits=commits,
        branches={"main": tip},
        head="main",
        working_tree={"src/handoff.py": {"status": "untracked", "content": "handoff = 'verified'\n"}},
        remotes={"origin": "https://example.test/guild/arcane-spire.git"},
        remote_branches={"origin/main": tip},
        upstream_tracking={"main": "origin/main"},
    )


def _arcane_variant(difficulty: str, strategy: str, prefix: str) -> dict:
    branch = f"handoff/{difficulty}-{strategy}"
    state = _arcane_state(prefix, divergent=strategy in {"merge", "squash"})
    if strategy == "fast-forward":
        solution = [
            "git status",
            "git log --oneline --graph --all",
            f"git switch -c {branch}",
            "git add src/handoff.py",
            "git commit -m 'Complete Guild handoff'",
            "git switch main",
            f"git merge {branch}",
            "git log --oneline --graph --all",
        ]
        message = "Complete Guild handoff"
    elif strategy == "merge":
        solution = [
            "git status",
            f"git switch -c {branch} {prefix}1",
            "git add src/handoff.py",
            "git commit -m 'Repair Guild handoff'",
            "git switch main",
            f"git merge --no-ff {branch}",
            "git show",
            "git log --oneline --graph --all",
        ]
        message = "Merge"
    elif strategy == "squash":
        solution = [
            "git status",
            f"git switch -c {branch} {prefix}1",
            "git add src/handoff.py",
            "git commit -m 'Draft Guild handoff'",
            "git switch main",
            f"git merge --squash {branch}",
            "git commit -m 'Complete reviewed handoff'",
            "git log --oneline --graph --all",
        ]
        message = "Complete reviewed handoff"
    else:
        solution = [
            "git remote -v",
            "git fetch origin",
            "git status",
            f"git switch -c {branch}",
            "git add src/handoff.py",
            "git commit -m 'Prepare relay handoff'",
            "git switch main",
            f"git merge {branch}",
            "git push",
            "git log --oneline --graph --all",
        ]
        message = "Prepare relay handoff"
    story, task, after = advanced_challenge_scenario_copy("Arcane Spire", "Complete the Guild Handoff", difficulty)
    commit_message = message if message != "Merge" else "Repair Guild handoff"
    return variant(
        f"guild-handoff-{difficulty}-{strategy}",
        strategy.replace("-", " ").title(),
        story=story,
        task=(
            f"{task} Work on a new branch named {branch}, commit the untracked src/handoff.py with the "
            f"message '{commit_message}', then bring the work into main and finish the handoff."
        ),
        before=ADVANCED_CHALLENGE_DIFFICULTY[difficulty]["before"],
        after=after,
        current="A late handoff repair is untracked while main and the Guild ref await review.",
        risk=ADVANCED_CHALLENGE_DIFFICULTY[difficulty]["risk"],
        initial=state,
        solution=solution,
        details=[branch, "src/handoff.py", message if message != "Merge" else "Repair Guild handoff"],
        evaluation=_contract(
            {
                "head_branch": "main",
                "latest_commit": {
                    "branch": "main",
                    "contains_paths": ["src/handoff.py"],
                    "message_contains": [message],
                },
                "working_tree_clean": True,
                "staging_empty": True,
                "branch_exists": [branch],
                "min_commits_on_branch": {"main": 3},
            },
            required=["git status", "git switch -c", "git add", "git commit", "git merge", "git log"],
            graph={"from": "main without the final handoff repair", "to": after},
            concepts=["branching", "committing", "integration", "verification"],
        ),
    )


def _arcane_challenge() -> dict:
    trials = []
    for difficulty in ("easy", "medium", "hard"):
        story, task, after = advanced_challenge_scenario_copy("Arcane Spire", "Complete the Guild Handoff", difficulty)
        trials.append(
            level(
                difficulty,
                story=story,
                task=task,
                before=ADVANCED_CHALLENGE_DIFFICULTY[difficulty]["before"],
                after=after,
                current="The Guild is waiting for a clean main branch and an explainable handoff graph.",
                risk=ADVANCED_CHALLENGE_DIFFICULTY[difficulty]["risk"],
                min_counted_commands=ADVANCED_CHALLENGE_DIFFICULTY[difficulty]["min"],
                max_counted_commands=ADVANCED_CHALLENGE_DIFFICULTY[difficulty]["max"],
                uses_adventure_levels=["guild-handoff-workflow-1", "guild-handoff-workflow-2"],
                variants=[
                    _arcane_variant(difficulty, strategy, prefix)
                    for strategy, prefix in (
                        ("fast-forward", "u"),
                        ("merge", "v"),
                        ("squash", "w"),
                        ("publish", "x"),
                    )
                ],
            )
        )
    return challenge(
        "guild-archive-handoff",
        "guild-archive-handoff-challenge",
        "Challenge: Complete the Guild Handoff",
        "Use the full beginner command set to leave main clean, integrated, and ready for the Guild.",
        "The Guild review begins without step-by-step instructions. Read the repository and choose the complete workflow.",
        trials,
    )


V3_CHALLENGES = [_arcane_challenge(), *[_advanced_challenge(incident) for incident in INCIDENTS]]

__all__ = ["V3_CHALLENGES"]
