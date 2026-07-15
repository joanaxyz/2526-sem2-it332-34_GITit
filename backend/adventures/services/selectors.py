"""Adventure run orchestration.

An adventure run is one playable `AdventureLevel`, walked as an ordered sequence
of `AdventureWave` problems. Each wave selects its own variant; the run completes
only when the last wave is cleared. Chapters order adventure levels for
unlocks and mastery targets, but the runtime never walks a whole chapter as
one continuous session.
"""


from django.db.models import Count

from adventures.models import (
    AdventureLevel,
    AdventureWave,
)


def ordered_levels_for(adventure: AdventureLevel) -> list[AdventureLevel]:
    """Return published adventure levels in the same chapter as ``adventure``."""
    return list(
        AdventureLevel.objects.filter(chapter_id=adventure.chapter_id, is_published=True)
        .select_related("chapter", "chapter__story", "source_content_definition")
        .prefetch_related("command_forms", "waves", "waves__variants")
        .order_by("sort_order", "id")
    )

def ordered_levels_for_story(story) -> list[AdventureLevel]:
    return list(
        AdventureLevel.objects.filter(
            chapter__story=story,
            is_published=True,
        )
        .select_related("chapter", "chapter__story", "source_content_definition")
        .prefetch_related("command_forms", "waves", "waves__variants")
        .order_by("chapter__sort_order", "sort_order", "id")
    )

def adventure_command_form_ids(adventure: AdventureLevel) -> set[int]:
    # Only the forms taught in *this* level. Scoping to the whole chapter would
    # unlock commands from later, not-yet-reached levels the moment any one level
    # in the chapter is passed.
    return set(
        adventure.command_forms.filter(is_published=True).values_list("id", flat=True)
    )

def story_command_form_ids(story) -> set[int]:
    return {
        form_id
        for form_id in AdventureLevel.objects.filter(
            chapter__story=story,
            is_published=True,
            is_required=True,
        ).values_list("command_forms", flat=True)
        if form_id is not None
    }

MASTERY_TARGET_CAP = 8

def form_solve_targets(form_ids) -> dict[int, int]:
    """Mastery target = count of distinct published waves per command.

    Every wave that exercises a form (inside a required, published level) counts
    toward its target, so a command is only "mastered" after it has been used
    across many distinct scenarios. The cap keeps the bar achievable for core
    commands that repeat across the whole curriculum.
    """
    form_ids = set(form_ids)
    targets = {form_id: 0 for form_id in form_ids}
    if not form_ids:
        return targets
    rows = (
        AdventureWave.objects.filter(
            is_published=True,
            level__is_published=True,
            level__is_required=True,
            command_forms__in=form_ids,
        )
        .values("command_forms")
        .annotate(n=Count("id", distinct=True))
    )
    for row in rows:
        form_id = row["command_forms"]
        if form_id in targets:
            targets[form_id] = row["n"]
    return {form_id: max(1, min(MASTERY_TARGET_CAP, n)) for form_id, n in targets.items()}

def ordered_waves_for(level: AdventureLevel) -> list[AdventureWave]:
    return list(
        level.waves.filter(is_published=True)
        .prefetch_related("variants")
        .order_by("sort_order", "id")
    )
