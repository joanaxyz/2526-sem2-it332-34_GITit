"""Shared construction helpers for advanced authored challenge ledgers."""

from __future__ import annotations

from curriculum.seed_data.source.advanced_story_support import (
    build_advanced_story_requirements,
    build_advanced_story_state,
    render_advanced_story_command,
)
from curriculum.seed_data.source.challenge_specs.helpers import _contract, variant

ADVANCED_CHALLENGE_DIFFICULTY = {
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


def _command_family(command: str) -> str:
    return " ".join(command.split()[:2])


def _difficulty_extra(chapter_slug: str, difficulty: str) -> list[str]:
    """Return difficulty garnish restricted to commands the chapter has taught."""

    extra = list(ADVANCED_CHALLENGE_DIFFICULTY[difficulty]["extra"])
    show_ref_ready = chapter_slug == "frost-publish-the-core" or chapter_slug.startswith("skyline-")
    if "git show-ref" in extra and not show_ref_ready:
        extra = [
            "git log --oneline --graph --all" if item == "git show-ref" else item for item in extra
        ]
    return extra


def advanced_challenge_scenario_copy(
    story_title: str,
    chapter_title: str,
    difficulty: str,
) -> tuple[str, str, str]:
    """Build shared story, task, and target-state copy for advanced challenges."""

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


def build_advanced_challenge_variant(
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
    """Build one advanced challenge variant from a strategy and diagnostics."""

    suffix = f"{chapter_slug}{series}-{difficulty}-{index}"
    branch = f"challenge/{suffix}"
    diagnostics = [
        render_advanced_story_command(command, prefix) for command in diagnostic_commands
    ]
    extra = _difficulty_extra(chapter_slug, difficulty)

    if strategy == "author":
        state = build_advanced_story_state(prefix, mode="author")
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
        requirements = build_advanced_story_requirements(
            branch,
            "Resolve",
            "src/repair.ts",
        )
        strategy_copy = "author the correction from the pending workspace evidence"
        required = [
            *map(_command_family, diagnostics),
            "git switch -c",
            "git add",
            "git commit",
            "git log",
        ]
        value_note = (
            f"Do the work on a new branch named {branch}, commit the pending src/repair.ts with the "
            f"message 'Resolve {chapter_slug} challenge', and tag the result {suffix}."
        )
        literals = [branch, "src/repair.ts", f"Resolve {chapter_slug} challenge", suffix]
    elif strategy == "transplant":
        state = build_advanced_story_state(prefix, mode="transplant")
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
        requirements = build_advanced_story_requirements(
            branch,
            "Transplant",
            "src/relay.ts",
        )
        strategy_copy = "transplant the isolated donor patch without taking its branch history"
        required = [
            *map(_command_family, diagnostics),
            "git switch -c",
            "git cherry-pick --no-commit",
            "git commit",
            "git log",
        ]
        value_note = (
            f"Do the work on a new branch named {branch}, take the donor patch from commit {prefix}3, "
            f"commit it with the message 'Transplant {chapter_slug} challenge repair', and tag the result {suffix}."
        )
        literals = [branch, f"{prefix}3", f"Transplant {chapter_slug} challenge repair", suffix]
    elif strategy == "integrate":
        state = build_advanced_story_state(prefix, mode="integrate")
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
        requirements = build_advanced_story_requirements(
            branch,
            "Integrate",
            "src/relay.ts",
        )
        strategy_copy = "squash-integrate the divergent repair as one reviewed snapshot"
        required = [
            *map(_command_family, diagnostics),
            "git merge-base",
            "git switch -c",
            "git merge --squash",
            "git commit",
            "git log",
        ]
        value_note = (
            f"Do the work on a new branch named {branch}, squash the feature/work branch into one staged "
            f"change, commit it with the message 'Integrate {chapter_slug} challenge repair', and tag the result {suffix}."
        )
        literals = [branch, "feature/work", f"Integrate {chapter_slug} challenge repair", suffix]
    else:
        state = build_advanced_story_state(prefix, mode="revert")
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
        requirements = build_advanced_story_requirements(branch, "Revert")
        strategy_copy = "reverse the known shared failure with an additive commit"
        required = [
            *map(_command_family, diagnostics),
            "git switch -c",
            "git revert",
            "git show",
            "git log",
        ]
        value_note = (
            f"Do the work on a new branch named {branch}, revert the bad commit {prefix}2 with an "
            f"additive commit, and tag the result {suffix}."
        )
        literals = [branch, f"{prefix}2", suffix]

    story, task, after = advanced_challenge_scenario_copy(
        story_title,
        chapter_title,
        difficulty,
    )
    return variant(
        f"{chapter_slug}{series}-{difficulty}-{strategy}",
        strategy_copy.title(),
        story=story,
        task=f"Use the repository evidence to {strategy_copy}, then mark and verify the handoff. {value_note}",
        before=ADVANCED_CHALLENGE_DIFFICULTY[difficulty]["before"],
        after=after,
        current=(
            "The stable mainline, divergent feature, donor patch, earlier patch series, known bad commit, "
            "remote-tracking ref, and v1.0 marker are all visible in the repository evidence."
        ),
        risk=ADVANCED_CHALLENGE_DIFFICULTY[difficulty]["risk"],
        initial=state,
        solution=solution,
        evaluation=_contract(
            requirements,
            required=list(dict.fromkeys(required)),
            graph={
                "from": "an unresolved incident graph with several plausible repair sources",
                "to": after,
            },
            concepts=[*map(_command_family, diagnostics), strategy_copy, "DAG verification"],
        ),
        details=literals,
    )


__all__ = [
    "ADVANCED_CHALLENGE_DIFFICULTY",
    "advanced_challenge_scenario_copy",
    "build_advanced_challenge_variant",
]
