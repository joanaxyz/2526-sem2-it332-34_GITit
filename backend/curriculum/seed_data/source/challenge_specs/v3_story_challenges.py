"""Chapter challenges for Arcane 8, Frostbound Citadel, and Neon Backstreets.

Every chapter challenge has Easy, Medium, and Hard trials.  Each trial has four
strategy-distinct variants and ends in a commit/ref change that is visible in
the live DAG. Read-only diagnostics are evidence-gathering steps, never the
whole solution.
"""

from __future__ import annotations

from curriculum.seed_data.chapters import CHAPTERS
from curriculum.seed_data.source.adventure_level_specs.v3_advanced_workflows import (
    INCIDENTS,
    _render,
    _requirements,
    _state,
)
from curriculum.seed_data.source.challenge_specs.helpers import (
    _contract,
    challenge,
    level,
    variant,
)

_DIFFICULTY = {
    "easy": {
        "extra": (),
        "min": 4,
        "max": 12,
        "before": "one known incident branch, one repair source, and a clear handoff target",
        "risk": "acting without the chapter diagnostic can put the correction on the wrong history",
    },
    "medium": {
        "extra": ("git status",),
        "min": 5,
        "max": 14,
        "before": "divergent history, several plausible repair sources, and no command-by-command guidance",
        "risk": "choosing the right final tree with the wrong history shape can still break review and rollback",
    },
    "hard": {
        "extra": ("git show-ref",),
        "min": 6,
        "max": 18,
        "before": "multiple refs, a known bad deployment, a donor patch, and a release marker under time pressure",
        "risk": "an unverified ref movement can make an incorrect history look authoritative to every downstream user",
    },
}


def _family(command: str) -> str:
    return " ".join(command.split()[:2])


def _difficulty_extra(chapter_slug: str, difficulty: str) -> list[str]:
    """Difficulty garnish commands, restricted to what the chapter has taught.

    ``git show-ref`` is introduced at frost-publish-the-core in play order, so
    earlier frost chapters use the core graph read instead of demanding an
    untaught command from the learner.
    """
    extra = list(_DIFFICULTY[difficulty]["extra"])
    show_ref_ready = chapter_slug == "frost-publish-the-core" or chapter_slug.startswith("skyline-")
    if "git show-ref" in extra and not show_ref_ready:
        extra = ["git log --oneline --graph --all" if item == "git show-ref" else item for item in extra]
    return extra


def _scenario_copy(story_title: str, chapter_title: str, difficulty: str) -> tuple[str, str, str]:
    story = (
        f"The {story_title} team opens its {chapter_title.lower()} review after a repository incident blocks "
        "the next operational handoff. The diagram contains enough evidence to choose more than one plausible "
        "command, but only a safe history strategy will preserve the useful work."
    )
    task = (
        "Inspect the chapter evidence, create a dedicated incident branch, produce the requested corrective "
        "history, and verify the resulting DAG and refs."
    )
    after = (
        f"a clean {difficulty} repair branch with a new corrective commit and a visible review tag"
    )
    return story, task, after


def _advanced_variant(
    *,
    chapter_slug: str,
    story_title: str,
    chapter_title: str,
    difficulty: str,
    strategy: str,
    diagnostic_commands: tuple[str, ...],
    prefix: str,
    index: int,
    series: str = "",
) -> dict:
    suffix = f"{chapter_slug}{series}-{difficulty}-{index}"
    branch = f"challenge/{suffix}"
    diagnostics = [_render(command, prefix) for command in diagnostic_commands]
    extra = _difficulty_extra(chapter_slug, difficulty)

    if strategy == "author":
        state = _state(prefix, mode="author")
        solution = [
            *diagnostics,
            *extra,
            "git status",
            f"git switch -c {branch}",
            "git add src/repair.ts",
            "git diff --staged",
            f"git commit -m 'Resolve {chapter_slug} challenge'",
            f"git tag {suffix}",
            "git log --oneline --graph --all",
        ]
        requirements = _requirements(branch, "Resolve", "src/repair.ts")
        strategy_copy = "author the correction from the pending workspace evidence"
        required = [*map(_family, diagnostics), "git switch -c", "git add", "git commit", "git log"]
        value_note = (
            f"Do the work on a new branch named {branch}, commit the pending src/repair.ts with the "
            f"message 'Resolve {chapter_slug} challenge', and tag the result {suffix}."
        )
        literals = [branch, "src/repair.ts", f"Resolve {chapter_slug} challenge", suffix]
    elif strategy == "transplant":
        state = _state(prefix, mode="transplant")
        solution = [
            *diagnostics,
            *extra,
            "git log --oneline --graph --all",
            f"git switch -c {branch} main",
            f"git cherry-pick --no-commit {prefix}3",
            "git status",
            f"git commit -m 'Transplant {chapter_slug} challenge repair'",
            f"git tag {suffix}",
            "git log --oneline --graph --all",
        ]
        requirements = _requirements(branch, "Transplant", "src/relay.ts")
        strategy_copy = "transplant the isolated donor patch without taking its branch history"
        required = [*map(_family, diagnostics), "git switch -c", "git cherry-pick --no-commit", "git commit", "git log"]
        value_note = (
            f"Do the work on a new branch named {branch}, take the donor patch from commit {prefix}3, "
            f"commit it with the message 'Transplant {chapter_slug} challenge repair', and tag the result {suffix}."
        )
        literals = [branch, f"{prefix}3", f"Transplant {chapter_slug} challenge repair", suffix]
    elif strategy == "integrate":
        state = _state(prefix, mode="integrate")
        solution = [
            *diagnostics,
            *extra,
            "git merge-base main feature/work",
            f"git switch -c {branch} main",
            "git merge --squash feature/work",
            "git status",
            f"git commit -m 'Integrate {chapter_slug} challenge repair'",
            f"git tag {suffix}",
            "git log --oneline --graph --all",
        ]
        requirements = _requirements(branch, "Integrate", "src/relay.ts")
        strategy_copy = "squash-integrate the divergent repair as one reviewed snapshot"
        required = [*map(_family, diagnostics), "git merge-base", "git switch -c", "git merge --squash", "git commit", "git log"]
        value_note = (
            f"Do the work on a new branch named {branch}, squash the feature/work branch into one staged "
            f"change, commit it with the message 'Integrate {chapter_slug} challenge repair', and tag the result {suffix}."
        )
        literals = [branch, "feature/work", f"Integrate {chapter_slug} challenge repair", suffix]
    else:
        state = _state(prefix, mode="revert")
        solution = [
            *diagnostics,
            *extra,
            "git log --oneline --graph --all",
            f"git switch -c {branch} main",
            f"git revert --no-edit {prefix}2",
            f"git tag {suffix}",
            "git show",
            "git log --oneline --graph --all",
        ]
        requirements = _requirements(branch, "Revert")
        strategy_copy = "reverse the known shared failure with an additive commit"
        required = [*map(_family, diagnostics), "git switch -c", "git revert", "git show", "git log"]
        value_note = (
            f"Do the work on a new branch named {branch}, revert the bad commit {prefix}2 with an "
            f"additive commit, and tag the result {suffix}."
        )
        literals = [branch, f"{prefix}2", suffix]

    story, task, after = _scenario_copy(story_title, chapter_title, difficulty)
    return variant(
        f"{chapter_slug}{series}-{difficulty}-{strategy}",
        strategy_copy.title(),
        story=story,
        task=f"Use the repository evidence to {strategy_copy}, then mark and verify the handoff. {value_note}",
        before=_DIFFICULTY[difficulty]["before"],
        after=after,
        current=(
            "The stable mainline, divergent feature, donor patch, earlier patch series, known bad commit, "
            "remote-tracking ref, and v1.0 marker are all visible in the repository evidence."
        ),
        risk=_DIFFICULTY[difficulty]["risk"],
        initial=state,
        solution=solution,
        evaluation=_contract(
            requirements,
            required=list(dict.fromkeys(required)),
            graph={
                "from": "an unresolved incident graph with several plausible repair sources",
                "to": after,
            },
            concepts=[*map(_family, diagnostics), strategy_copy, "DAG verification"],
        ),
        details=literals,
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
            _advanced_variant(
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
        story, task, after = _scenario_copy(incident.story_title, chapter["title"], difficulty)
        trials.append(
            level(
                difficulty,
                story=story,
                task=task,
                before=_DIFFICULTY[difficulty]["before"],
                after=after,
                current="The repository provides graph, workspace, ref, and chapter-specific diagnostic evidence.",
                risk=_DIFFICULTY[difficulty]["risk"],
                min_counted_commands=_DIFFICULTY[difficulty]["min"],
                max_counted_commands=_DIFFICULTY[difficulty]["max"],
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
    story, task, after = _scenario_copy("Arcane Spire", "Complete the Guild Handoff", difficulty)
    commit_message = message if message != "Merge" else "Repair Guild handoff"
    return variant(
        f"guild-handoff-{difficulty}-{strategy}",
        strategy.replace("-", " ").title(),
        story=story,
        task=(
            f"{task} Work on a new branch named {branch}, commit the untracked src/handoff.py with the "
            f"message '{commit_message}', then bring the work into main and finish the handoff."
        ),
        before=_DIFFICULTY[difficulty]["before"],
        after=after,
        current="A late handoff repair is untracked while main and the Guild ref await review.",
        risk=_DIFFICULTY[difficulty]["risk"],
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
        story, task, after = _scenario_copy("Arcane Spire", "Complete the Guild Handoff", difficulty)
        trials.append(
            level(
                difficulty,
                story=story,
                task=task,
                before=_DIFFICULTY[difficulty]["before"],
                after=after,
                current="The Guild is waiting for a clean main branch and an explainable handoff graph.",
                risk=_DIFFICULTY[difficulty]["risk"],
                min_counted_commands=_DIFFICULTY[difficulty]["min"],
                max_counted_commands=_DIFFICULTY[difficulty]["max"],
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
