"""Tiered pedagogy laws for the advanced-story content (Frostbound/Skyline).

The arcane blueprint keeps its stricter laws in
``test_blueprint_pedagogy_invariants``. Advanced stories hold a tiered law:

1. Every playable advanced command form is INTRODUCED by a dedicated solo wave
   (single-command solution, no extra form tags) before any other wave uses it.
2. Every playable advanced form recurs across at least three distinct waves,
   so its mastery bar reflects real practice.
3. Mastery stays reachable story by story: a form taught in one story must
   reach its capped mastery target using that story's waves plus earlier
   stories' waves alone (otherwise completing the story would be impossible
   under mastery-based story completion).

Waves are counted over the advanced level specs (one spec == one wave).
"""

from __future__ import annotations

from collections import Counter, defaultdict

from curriculum.seed_data.adventure_levels import ADVENTURE_LEVELS
from curriculum.seed_data.adventures import ADVENTURE_SOURCES
from curriculum.seed_data.chapters import CHAPTERS
from curriculum.seed_data.command_catalog import COMMAND_CATALOG
from curriculum.seed_data.stories import STORIES

MIN_APPEARANCES = 3
MASTERY_TARGET_CAP = 8

ENFORCED_STORIES = {"frostbound-citadel", "neon-backstreets"}

_STORY_ORDER = {story["slug"]: index for index, story in enumerate(STORIES)}
_CHAPTER_STORY = {chapter["slug"]: chapter["story"] for chapter in CHAPTERS}
_CHAPTER_NUMBER = {chapter["slug"]: chapter["number"] for chapter in CHAPTERS}

_ADVANCED_PLAYABLE_FORMS = {
    f"{skill['slug']}/{form['slug']}"
    for skill in COMMAND_CATALOG
    for form in skill.get("usages", [])
    if form.get("module", skill["module"]).startswith(("frost-", "skyline-"))
    and not form.get("reference_only")
}


def _ordered_advanced_waves() -> list[dict]:
    """Advanced specs in exact play order.

    Order: story sort order, chapter number, the chapter's adventure sources
    in declared order, then authoring order inside each adventure.
    """
    by_adventure: dict[str, list[dict]] = defaultdict(list)
    for spec in ADVENTURE_LEVELS:
        by_adventure[str(spec.get("adventure", ""))].append(spec)

    ordered: list[dict] = []
    chapters = sorted(
        (slug for slug in ADVENTURE_SOURCES if _CHAPTER_STORY.get(slug, "").startswith(("frostbound", "skyline"))),
        key=lambda slug: (_STORY_ORDER[_CHAPTER_STORY[slug]], _CHAPTER_NUMBER[slug]),
    )
    for chapter_slug in chapters:
        if _CHAPTER_STORY[chapter_slug] not in ENFORCED_STORIES:
            continue
        for source in ADVENTURE_SOURCES[chapter_slug]:
            ordered.extend(by_adventure.get(source["slug"], []))
    return ordered


ORDERED_WAVES = _ordered_advanced_waves()


def _forms_used(spec: dict) -> list[str]:
    used = [spec["usage"], *spec.get("command_forms", [])]
    return [form for form in used if form in _ADVANCED_PLAYABLE_FORMS]


def _is_solo_intro(spec: dict) -> bool:
    if spec.get("command_forms"):
        return False
    return all(
        len(variant.get("solution_commands_template", [])) == 1
        for variant in spec.get("variants", [])
    )


def test_enforced_stories_have_advanced_waves():
    assert ORDERED_WAVES, "No advanced waves found for the enforced stories."


def test_every_used_form_has_a_solo_intro_before_first_use():
    first_intro: dict[str, int] = {}
    for index, spec in enumerate(ORDERED_WAVES):
        if _is_solo_intro(spec) and spec["usage"] in _ADVANCED_PLAYABLE_FORMS:
            first_intro.setdefault(spec["usage"], index)

    violations = []
    for index, spec in enumerate(ORDERED_WAVES):
        for form in _forms_used(spec):
            intro_index = first_intro.get(form)
            if intro_index is None:
                violations.append(f"{form} is used in {spec['slug']} but has no solo intro wave")
            elif index < intro_index:
                violations.append(
                    f"{form} is used in wave #{index} ({spec['slug']}) before its intro "
                    f"#{intro_index} ({ORDERED_WAVES[intro_index]['slug']})"
                )
    assert not violations, "Intro-first law violated:\n" + "\n".join(sorted(set(violations)))


def test_every_used_form_recurs_across_enough_waves():
    appearances = Counter(
        form for spec in ORDERED_WAVES for form in set(_forms_used(spec))
    )
    shortfalls = [
        f"{form}: {count}/{MIN_APPEARANCES}"
        for form, count in sorted(appearances.items())
        if count < MIN_APPEARANCES
    ]
    assert not shortfalls, (
        "Every advanced form must recur across enough distinct waves for its "
        "mastery bar to be honest. Shortfalls:\n" + "\n".join(shortfalls)
    )


def test_mastery_stays_reachable_within_story_order():
    """Cumulative waves through a form's earliest teaching story must cover
    its capped mastery target, or that story can never be completed under
    mastery-based story completion."""
    story_of_wave = {
        spec["slug"]: _STORY_ORDER[_CHAPTER_STORY[_chapter_of(spec)]] for spec in ORDERED_WAVES
    }
    per_story: dict[str, Counter] = defaultdict(Counter)
    for spec in ORDERED_WAVES:
        story_index = story_of_wave[spec["slug"]]
        for form in set(_forms_used(spec)):
            per_story[form][story_index] += 1

    violations = []
    for form, story_counts in sorted(per_story.items()):
        total = sum(story_counts.values())
        target = min(MASTERY_TARGET_CAP, total)
        earliest = min(story_counts)
        cumulative = sum(count for story, count in story_counts.items() if story <= earliest)
        if cumulative < target:
            violations.append(
                f"{form}: earliest story offers {cumulative} waves but the capped target is {target}"
            )
    assert not violations, (
        "Forms must be masterable within their first teaching story:\n" + "\n".join(violations)
    )


def _chapter_of(spec: dict) -> str:
    adventure = str(spec.get("adventure", ""))
    for suffix in ("-drills", "-workflows", "-incidents"):
        if adventure.endswith(suffix):
            return adventure[: -len(suffix)]
    return adventure


def test_wave_slugs_are_unique():
    slugs = [spec["slug"] for spec in ORDERED_WAVES]
    dupes = sorted(slug for slug, count in Counter(slugs).items() if count > 1)
    assert not dupes, f"Duplicate advanced wave slugs: {dupes}"
