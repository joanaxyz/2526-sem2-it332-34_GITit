"""Pedagogy laws for the blueprint content ledger.

Pure-Python invariants over ``blueprint_overlay.py`` (no database): every
command form gets a dedicated solo intro wave before any other wave uses it,
and every form repeats across enough distinct waves for its mastery bar to
mean something. These laws are what make "mastered" an honest word in the UI;
new content must keep them true.
"""

from collections import Counter

from curriculum.seed_data.adventure_levels import ADVENTURE_LEVELS
from curriculum.seed_data.adventures import ADVENTURE_SOURCES
from curriculum.seed_data.blueprint_overlay import BLUEPRINT_ADVENTURE_LEVELS
from curriculum.seed_data.challenges import CHALLENGES
from curriculum.seed_data.chapters import CHAPTERS
from curriculum.seed_data.command_catalog import COMMAND_CATALOG

# Every form must be exercised by at least this many distinct adventure waves
# (challenge trials do not count toward mastery). The core suite - the everyday
# loop a working developer runs constantly - holds a higher bar.
MIN_APPEARANCES = 6
CORE_MIN_APPEARANCES = 10
CORE_FORMS = {
    "git-status/plain",
    "git-add/file",
    "git-add/dot",
    "git-commit/message",
    "git-log/oneline",
    "git-log/graph-all",
    "git-branch/list",
    "git-branch/create",
    "git-switch/existing",
    "git-switch/create",
    "git-merge/branch",
    "git-push/upstream",
    "git-push/current",
    "git-pull/default",
}

CATALOG_SKILL_TRACKING = {
    skill["slug"]: skill.get("mastery_trackable", True)
    for skill in COMMAND_CATALOG
}
CATALOG_FORMS = {
    form
    for level in ADVENTURE_LEVELS
    if not str(level.get("adventure", "")).startswith(("frost-", "skyline-"))
    for form in [level["usage"], *level.get("command_forms", [])]
    if CATALOG_SKILL_TRACKING.get(form.split("/", 1)[0], True)
}


def _ordered_waves():
    """Every blueprint wave in the exact order the seeder publishes them.

    Mirrors ``seed_curriculum``: chapter sort order, then each chapter's
    sources in ADVENTURE_SOURCES order, then level list order, then wave
    list order.
    """
    chapter_order = {spec["slug"]: spec["number"] for spec in CHAPTERS}
    ordered = []
    for chapter_slug in sorted(ADVENTURE_SOURCES, key=lambda slug: chapter_order[slug]):
        for source in ADVENTURE_SOURCES[chapter_slug]:
            for level in BLUEPRINT_ADVENTURE_LEVELS.get(source["slug"], []):
                for wave in level["waves"]:
                    ordered.append(wave)
    return ordered


ORDERED_WAVES = _ordered_waves()


def _forms_used(wave):
    return [wave["usage"], *wave.get("forms", [])]


def _is_intro(wave):
    return len(wave["solution"]) == 1 and not wave.get("forms")


def test_wave_slugs_are_globally_unique():
    slugs = [wave["slug"] for wave in ORDERED_WAVES]
    dupes = sorted(slug for slug, count in Counter(slugs).items() if count > 1)
    assert not dupes, f"Duplicate wave slugs: {dupes}"


def test_every_usage_and_form_reference_exists_in_catalog():
    unknown = sorted(
        {
            form
            for wave in ORDERED_WAVES
            for form in _forms_used(wave)
            if form not in CATALOG_FORMS
        }
    )
    assert not unknown, f"Waves reference forms missing from COMMAND_CATALOG: {unknown}"


def test_every_catalog_form_has_a_solo_intro_wave():
    introduced = {wave["usage"] for wave in ORDERED_WAVES if _is_intro(wave)}
    missing = sorted(CATALOG_FORMS - introduced)
    assert not missing, (
        "Every command form needs a dedicated single-command intro wave. "
        f"Missing intros: {missing}"
    )


def test_no_form_is_used_before_its_intro():
    first_intro = {}
    for index, wave in enumerate(ORDERED_WAVES):
        if _is_intro(wave) and wave["usage"] not in first_intro:
            first_intro[wave["usage"]] = index

    violations = []
    for index, wave in enumerate(ORDERED_WAVES):
        for form in _forms_used(wave):
            intro_index = first_intro.get(form)
            if intro_index is not None and index < intro_index:
                violations.append(
                    f"{form} used in wave #{index} ({wave['slug']}) before its intro "
                    f"#{intro_index} ({ORDERED_WAVES[intro_index]['slug']})"
                )
    assert not violations, "Forms used before their intro wave:\n" + "\n".join(violations)


def test_repetition_law():
    appearances = Counter(
        form for wave in ORDERED_WAVES for form in set(_forms_used(wave))
    )
    shortfalls = []
    for form in sorted(CATALOG_FORMS):
        need = CORE_MIN_APPEARANCES if form in CORE_FORMS else MIN_APPEARANCES
        have = appearances.get(form, 0)
        if have < need:
            shortfalls.append(f"{form}: {have}/{need}")
    assert not shortfalls, (
        "Every form must recur across enough distinct waves for mastery to be "
        "honest. Shortfalls:\n" + "\n".join(shortfalls)
    )


def test_challenge_uses_reference_live_blueprint_waves():
    # Challenges may cite either a blueprint wave slug (arcane content) or a
    # top-level adventure level slug (advanced/handoff content).
    known_slugs = {wave["slug"] for wave in ORDERED_WAVES}
    known_slugs.update(spec["slug"] for spec in ADVENTURE_LEVELS)
    broken = []
    for challenge in CHALLENGES:
        for trial in challenge.get("levels", []):
            for used in trial.get("uses_adventure_levels", []) or []:
                if used not in known_slugs:
                    broken.append(
                        f"{challenge['slug']}/{trial.get('difficulty', '?')} -> {used}"
                    )
    assert not broken, "Challenge trials reference unknown wave slugs:\n" + "\n".join(broken)


def test_authored_stories_do_not_spoil_solution_commands():
    leaks = []
    for wave in ORDERED_WAVES:
        story = (wave.get("story") or "").lower()
        if not story:
            continue
        for command in wave["solution"]:
            if command.lower() in story:
                leaks.append(f"{wave['slug']}: story contains {command!r}")
    assert not leaks, "Stories must not spell out solution commands:\n" + "\n".join(leaks)
