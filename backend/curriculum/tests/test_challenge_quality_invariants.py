"""Permanent quality laws for authored challenge content.

Challenges assess transfer after the adventure drills. They must therefore use
only command shapes the player has already practiced, cite adventure content
that is not later than the challenge, and finish with a change the live DAG can
actually render.
"""

from __future__ import annotations

from collections import defaultdict
import re
import shlex

from curriculum.seed_data.adventure_levels import ADVENTURE_LEVELS
from curriculum.seed_data.adventures import ADVENTURE_SOURCES
from curriculum.seed_data.challenges import CHALLENGES
from curriculum.seed_data.chapters import CHAPTERS
from curriculum.seed_data.command_catalog import COMMAND_CATALOG
from curriculum.seed_data.stories import STORIES


_STORY_ORDER = {story["slug"]: story["sort_order"] for story in STORIES}
_CHAPTER_ORDER = {
    chapter["slug"]: (_STORY_ORDER[chapter["story"]], chapter["number"])
    for chapter in CHAPTERS
}
_ARCANE_CHAPTER_BY_NUMBER = {
    chapter["number"]: chapter["slug"]
    for chapter in CHAPTERS
    if chapter["story"] == "arcane-spire"
}
_ADVENTURE_SOURCE_OWNER = {
    source["slug"]: chapter_slug
    for chapter_slug, sources in ADVENTURE_SOURCES.items()
    for source in sources
}


def _command_tokens(command: str) -> list[str]:
    normalized = " ".join(str(command).strip().lower().split())
    try:
        return shlex.split(normalized)
    except ValueError:
        return normalized.split()


def _catalog_literal_operands() -> set[str]:
    """Return authored Git syntax words while excluding flags/placeholders."""

    literals = set()
    for skill in COMMAND_CATALOG:
        for form in skill.get("usages", []):
            for token in _command_tokens(form["usage_form"])[2:]:
                if "<" not in token and not token.startswith("-"):
                    literals.add(token)
    return literals


_LITERAL_OPERANDS = _catalog_literal_operands()


def _command_shape(command: str) -> tuple[str, ...]:
    """Mask scenario values while retaining the Git syntax being assessed.

    Branch names, paths, messages, and commit ids vary between scenarios. Git
    flags and catalog-owned operands such as ``stash pop`` or ``bisect run`` are
    the teachable command shape and must have appeared in an earlier drill.
    """

    tokens = _command_tokens(command)
    shape = tokens[:2]
    for token in tokens[2:]:
        if token.startswith("-") or token == "." or token in _LITERAL_OPERANDS:
            shape.append(token)
        else:
            shape.append("<arg>")
    return tuple(shape)


def _introduced_command_shapes() -> dict[str, set[tuple[str, ...]]]:
    by_chapter: dict[str, set[tuple[str, ...]]] = defaultdict(set)
    for spec in ADVENTURE_LEVELS:
        chapter_slug = _ADVENTURE_SOURCE_OWNER[spec["adventure"]]
        for variant in spec.get("variants", []):
            by_chapter[chapter_slug].update(
                _command_shape(command)
                for command in variant.get("solution_commands_template", [])
            )

    cumulative: dict[str, set[tuple[str, ...]]] = {}
    introduced: set[tuple[str, ...]] = set()
    for chapter_slug in sorted(_CHAPTER_ORDER, key=_CHAPTER_ORDER.get):
        introduced.update(by_chapter[chapter_slug])
        cumulative[chapter_slug] = set(introduced)
    return cumulative


def _live_dag_signature(state: dict) -> tuple:
    """Project repository state onto exactly what the live DAG renders."""

    branches = state.get("branches") or {}
    head = state.get("head") or {}
    head_target = head.get("target")
    if head.get("type") == "branch" and head_target is None:
        head_target = branches.get(head.get("name"))

    commits = tuple(
        sorted(
            (
                commit.get("id"),
                commit.get("message"),
                tuple(commit.get("parents") or []),
            )
            for commit in state.get("commits") or []
        )
    )
    return (
        bool(state.get("repository_initialized")),
        commits,
        tuple(sorted(branches.items())),
        (head.get("type"), head.get("name"), head_target),
        tuple(sorted((state.get("remote_branches") or {}).items())),
    )


def _citation_owners() -> dict[str, str]:
    return {
        spec["slug"]: _ADVENTURE_SOURCE_OWNER[spec["adventure"]]
        for spec in ADVENTURE_LEVELS
    }


def _citation_owner(citation: str, owners: dict[str, str]) -> str | None:
    if citation in owners:
        return owners[citation]
    foundational = re.fullmatch(r"ch([1-7])-adv-.+", citation)
    if foundational:
        return _ARCANE_CHAPTER_BY_NUMBER[int(foundational.group(1))]
    return None


def test_challenge_commands_are_introduced_before_the_challenge():
    introduced_by_chapter = _introduced_command_shapes()
    violations = []

    for challenge in CHALLENGES:
        introduced = introduced_by_chapter[challenge["module"]]
        for trial in challenge.get("levels", []):
            for variant in trial.get("variants", []):
                for command in variant.get("solution_commands_template", []):
                    shape = _command_shape(command)
                    if shape not in introduced:
                        violations.append(
                            f"{challenge['slug']}/{trial['difficulty']}/{variant['case_id']}: "
                            f"{command} ({' '.join(shape)})"
                        )

    assert not violations, (
        "Challenge solutions may only use command shapes introduced in adventure "
        "drills from the same or an earlier chapter:\n" + "\n".join(violations)
    )


def test_challenge_citations_do_not_point_to_future_adventures():
    owners = _citation_owners()
    violations = []

    for challenge in CHALLENGES:
        challenge_order = _CHAPTER_ORDER[challenge["module"]]
        for trial in challenge.get("levels", []):
            for citation in trial.get("uses_adventure_levels", []):
                owner = _citation_owner(citation, owners)
                if owner is None:
                    violations.append(
                        f"{challenge['slug']}/{trial['difficulty']}: unknown citation {citation}"
                    )
                elif _CHAPTER_ORDER[owner] > challenge_order:
                    violations.append(
                        f"{challenge['slug']}/{trial['difficulty']} -> {citation} ({owner})"
                    )

    assert not violations, (
        "Challenge trials may cite only same-chapter or earlier adventure drills:\n"
        + "\n".join(violations)
    )


def test_every_challenge_variant_changes_the_live_dag():
    violations = []

    for challenge in CHALLENGES:
        for trial in challenge.get("levels", []):
            for variant in trial.get("variants", []):
                initial = variant.get("initial_state_template") or {}
                target = variant.get("target_state_template") or {}
                contract = (variant.get("evaluation_spec_template") or {}).get(
                    "curriculum_contract", {}
                )
                transition = contract.get("dag_transition") or {}
                reasons = []
                if not target:
                    reasons.append("missing generated target")
                elif _live_dag_signature(initial) == _live_dag_signature(target):
                    reasons.append("target has no visible commit/ref/HEAD change")
                if contract.get("challenge_type") != "scenario_graph_transition":
                    reasons.append("missing scenario_graph_transition contract")
                if not transition.get("from") or not transition.get("to"):
                    reasons.append("missing authored DAG before/after description")
                if reasons:
                    violations.append(
                        f"{challenge['slug']}/{trial['difficulty']}/{variant['case_id']}: "
                        + ", ".join(reasons)
                    )

    assert not violations, (
        "Every challenge variant must end in a change the live DAG renders:\n"
        + "\n".join(violations)
    )
