"""Challenge coverage law for the advanced-story chapters.

A chapter's challenge levels must collectively test every playable advanced
command form its adventure waves teach. Coverage is encoded declaratively:
each challenge trial cites the adventure waves it draws on via
``uses_adventure_levels``, and the union of forms taught by the cited waves
must cover the forms the chapter's own waves exercise.
"""

from __future__ import annotations

from collections import defaultdict

from curriculum.seed_data.adventure_levels import ADVENTURE_LEVELS
from curriculum.seed_data.challenges import CHALLENGES
from curriculum.seed_data.chapters import CHAPTERS
from curriculum.seed_data.command_catalog import COMMAND_CATALOG

_ADVANCED_PLAYABLE_FORMS = {
    f"{skill['slug']}/{form['slug']}"
    for skill in COMMAND_CATALOG
    for form in skill.get("usages", [])
    if form.get("module", skill["module"]).startswith(("frost-", "skyline-"))
    and not form.get("reference_only")
}

_ADVANCED_CHAPTERS = [
    chapter["slug"]
    for chapter in CHAPTERS
    if chapter["slug"].startswith(("frost-", "skyline-"))
]

_SPEC_BY_SLUG = {spec["slug"]: spec for spec in ADVENTURE_LEVELS}


def _chapter_of(spec: dict) -> str:
    adventure = str(spec.get("adventure", ""))
    for suffix in ("-drills", "-workflows", "-incidents"):
        if adventure.endswith(suffix):
            return adventure[: -len(suffix)]
    return adventure


def _forms_of(spec: dict) -> set[str]:
    used = {spec["usage"], *spec.get("command_forms", [])}
    return used & _ADVANCED_PLAYABLE_FORMS


def _taught_forms_by_chapter() -> dict[str, set[str]]:
    taught: dict[str, set[str]] = defaultdict(set)
    for spec in ADVENTURE_LEVELS:
        chapter = _chapter_of(spec)
        if chapter in _ADVANCED_CHAPTERS:
            taught[chapter] |= _forms_of(spec)
    return taught


def _covered_forms_by_chapter() -> dict[str, set[str]]:
    covered: dict[str, set[str]] = defaultdict(set)
    for challenge in CHALLENGES:
        chapter = challenge.get("module")
        if chapter not in _ADVANCED_CHAPTERS:
            continue
        for trial in challenge.get("levels", []):
            for slug in trial.get("uses_adventure_levels", []) or []:
                spec = _SPEC_BY_SLUG.get(slug)
                if spec is not None:
                    covered[chapter] |= _forms_of(spec)
    return covered


def test_every_advanced_chapter_has_multiple_challenge_levels():
    counts = defaultdict(int)
    for challenge in CHALLENGES:
        if challenge.get("module") in _ADVANCED_CHAPTERS:
            counts[challenge["module"]] += 1
    shortfalls = sorted(
        f"{chapter}: {counts.get(chapter, 0)}"
        for chapter in _ADVANCED_CHAPTERS
        if counts.get(chapter, 0) < 2
    )
    assert not shortfalls, (
        "Every advanced chapter needs at least two challenge levels:\n" + "\n".join(shortfalls)
    )


def test_chapter_challenges_cover_every_taught_form():
    taught = _taught_forms_by_chapter()
    covered = _covered_forms_by_chapter()
    gaps = []
    for chapter in _ADVANCED_CHAPTERS:
        missing = sorted(taught.get(chapter, set()) - covered.get(chapter, set()))
        if missing:
            gaps.append(f"{chapter}: {', '.join(missing)}")
    assert not gaps, (
        "Chapter challenges must collectively reference waves teaching every "
        "form the chapter's adventures exercise. Missing coverage:\n" + "\n".join(gaps)
    )


def test_challenge_citations_resolve_to_real_waves():
    unknown = []
    for challenge in CHALLENGES:
        if challenge.get("module") not in _ADVANCED_CHAPTERS:
            continue
        for trial in challenge.get("levels", []):
            for slug in trial.get("uses_adventure_levels", []) or []:
                if slug not in _SPEC_BY_SLUG:
                    unknown.append(f"{challenge['slug']}/{trial.get('difficulty')} -> {slug}")
    assert not unknown, "Challenge citations reference unknown waves:\n" + "\n".join(unknown)
