"""Second (and third) challenge levels for the advanced-story chapters.

Every advanced chapter already carries one strategy-quartet challenge built
from its incident levels. This module adds:

- a second "-forms" challenge level per advanced chapter: a precision incident
  whose diagnostics come from the chapter's drilled command forms and whose
  trials reference the chapter's drill/workflow waves, so together the
  chapter's challenge levels test every form its adventures introduced; and
- a third "-mastery" challenge level for the most form-dense chapters, mixing
  the chapter's own diagnostics with its incident diagnostics.

Trials keep the established contract: easy/medium/hard, four strategy-distinct
variants per trial (distinct case ids drive retry rotation), evaluation by
spec only, and every variant ends in a DAG-visible corrective change.
"""

from __future__ import annotations

from collections import defaultdict

from curriculum.seed_data.chapters import CHAPTERS
from curriculum.seed_data.source.adventure_level_specs.v3_advanced_workflows import INCIDENTS
from curriculum.seed_data.source.adventure_level_specs.v3_frost_form_drills import (
    LEVELS as _FROST_DRILL_LEVELS,
)
from curriculum.seed_data.source.adventure_level_specs.v3_skyline_form_drills import (
    LEVELS as _SKYLINE_DRILL_LEVELS,
)
from curriculum.seed_data.source.challenge_specs.helpers import challenge, level
from curriculum.seed_data.source.challenge_specs.v3_story_challenges import (
    _DIFFICULTY,
    _advanced_variant,
    _scenario_copy,
)

# Diagnostics for the "-forms" challenges: reads drawn from each chapter's
# drilled forms (never the same pairing the incident challenge leads with).
_FORMS_DIAGNOSTICS: dict[str, tuple[str, str]] = {
    "frost-temper-the-commit": ("git diff --check", "git diff --stat"),
    "frost-choose-the-integration": ("git diff main...feature/work", "git rev-list --count {p}0..main"),
    "frost-survive-the-conflict": ("git merge-tree main feature/work", "git merge-base main feature/work"),
    "frost-move-the-patch": ("git show {p}3", "git range-diff {p}0..old/series {p}0..feature/work"),
    "frost-reforge-the-branch": ("git log --oneline --graph --all", "git range-diff {p}0..old/series {p}0..feature/work"),
    "frost-govern-the-remote": ("git remote -v", "git branch -vv"),
    "frost-deliver-the-release": ("git describe --tags", "git shortlog -sn"),
    "frost-hunt-the-regression": ("git bisect log", "git bisect run heat-relay-test"),
    "frost-publish-the-core": ("git show-ref", "git verify-tag v1.0"),
    "skyline-revision-language": ("git rev-parse --show-toplevel", "git rev-parse HEAD~1"),
    "skyline-hidden-history": ("git grep stable", "git blame src/app.ts"),
    "skyline-first-broken-commit": ("git bisect log", "git bisect run integration-test"),
    "skyline-repeated-conflict": ("git rerere diff", "git rerere status"),
    "skyline-many-realities": ("git sparse-checkout list", "git submodule status"),
    "skyline-enchant-behavior": ("git config --list", "git config --get user.name"),
    "skyline-guard-the-archive": ("git verify-tag v1.0", "git verify-commit {p}1"),
    "skyline-restore-maintain": ("git count-objects -vH", "git fsck --full"),
    "skyline-serve-the-city": ("git show-ref", "git for-each-ref"),
    "skyline-migrate-the-grid": ("git ls-tree {p}1", "git cat-file -t {p}1"),
    "skyline-git-machinery": ("git cat-file -p {p}1", "git symbolic-ref HEAD"),
    "skyline-command-laboratory": ("git rev-parse HEAD", "git for-each-ref"),
}

# Chapters dense enough in forms to warrant a third, cross-cutting level.
_MASTERY_CHAPTERS = (
    "frost-temper-the-commit",
    "frost-survive-the-conflict",
    "frost-govern-the-remote",
    "frost-deliver-the-release",
    "skyline-many-realities",
)

_CHAPTER_TITLES = {chapter["slug"]: chapter["title"] for chapter in CHAPTERS}


def _drill_wave_slugs_by_chapter() -> dict[str, list[str]]:
    slugs: dict[str, list[str]] = defaultdict(list)
    for spec in [*_FROST_DRILL_LEVELS, *_SKYLINE_DRILL_LEVELS]:
        adventure = str(spec.get("adventure", ""))
        for suffix in ("-drills", "-workflows"):
            if adventure.endswith(suffix):
                slugs[adventure[: -len(suffix)]].append(spec["slug"])
                break
    return slugs


_DRILL_SLUGS = _drill_wave_slugs_by_chapter()


def _series_challenge(incident, *, series: str, title: str, summary: str, narrative: str, diagnostics: tuple[str, str]) -> dict:
    chapter_slug = incident.chapter
    chapter_title = _CHAPTER_TITLES[chapter_slug]
    uses = _DRILL_SLUGS.get(chapter_slug) or [f"{chapter_slug}-incident-1", f"{chapter_slug}-incident-2"]
    trials = []
    for difficulty in ("easy", "medium", "hard"):
        diagnostic_commands = (
            (diagnostics[0],)
            if difficulty == "easy"
            else (diagnostics[1],)
            if difficulty == "medium"
            else diagnostics
        )
        variants = [
            _advanced_variant(
                chapter_slug=chapter_slug,
                story_title=incident.story_title,
                chapter_title=chapter_title,
                difficulty=difficulty,
                strategy=strategy,
                diagnostic_commands=diagnostic_commands,
                prefix=prefix,
                index=index,
                series=series,
            )
            for index, (strategy, prefix) in enumerate(
                (("author", "q"), ("transplant", "r"), ("integrate", "s"), ("revert", "t")),
                start=1,
            )
        ]
        story, task, after = _scenario_copy(incident.story_title, chapter_title, difficulty)
        trials.append(
            level(
                difficulty,
                story=story,
                task=task,
                before=_DIFFICULTY[difficulty]["before"],
                after=after,
                current=(
                    "The repository provides graph, workspace, ref, and chapter-specific diagnostic evidence."
                ),
                risk=_DIFFICULTY[difficulty]["risk"],
                min_counted_commands=_DIFFICULTY[difficulty]["min"],
                max_counted_commands=_DIFFICULTY[difficulty]["max"],
                uses_adventure_levels=uses,
                variants=variants,
            )
        )
    return challenge(
        chapter_slug,
        f"{chapter_slug}-challenge{series}",
        title.format(chapter_title=chapter_title),
        summary.format(chapter_title=chapter_title),
        narrative.format(chapter_title=chapter_title),
        trials,
    )


def _forms_challenge(incident) -> dict:
    return _series_challenge(
        incident,
        series="-forms",
        title="Challenge: {chapter_title} Precision",
        summary=(
            "A tighter second scenario for {chapter_title}: the evidence commands this chapter "
            "drilled are the only reliable way in, and the fix must land as a visible history change."
        ),
        narrative=(
            "A second incident hits the same systems. The broad playbook will not fit this one; "
            "read the chapter's own diagnostics and choose the precise repair."
        ),
        diagnostics=_FORMS_DIAGNOSTICS[incident.chapter],
    )


def _mastery_challenge(incident) -> dict:
    forms_diag = _FORMS_DIAGNOSTICS[incident.chapter]
    mixed = (incident.diagnostic_commands[0], forms_diag[0])
    return _series_challenge(
        incident,
        series="-mastery",
        title="Challenge: {chapter_title} Mastery",
        summary=(
            "The capstone scenario for {chapter_title}: chapter commands and earlier skills mixed "
            "in one incident, judged only by the resulting repository state."
        ),
        narrative=(
            "The final scenario mixes everything this chapter taught with the skills that came "
            "before it. No prompts, no ordering hints; the repository state is the whole brief."
        ),
        diagnostics=mixed,
    )


V3_FORM_CHALLENGES = [
    *[_forms_challenge(incident) for incident in INCIDENTS],
    *[_mastery_challenge(incident) for incident in INCIDENTS if incident.chapter in _MASTERY_CHAPTERS],
]

__all__ = ["V3_FORM_CHALLENGES"]
