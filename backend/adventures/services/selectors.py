"""Read helpers shared by the adventure tier runtime.

An adventure level is played through its difficulty tiers; each tier is an
ordered set of waves (see ``adventures/tier_waves.py``).
"""

from django.db.models import Count, Q

from adventures.models import AdventureLevelTierWave


def playable_level_publication_filter(prefix: str = "") -> Q:
    """Publication rule every adventure run-start path must apply.

    A level is startable only while its own chapter is published. Player-authored
    levels are exempt from the chapter half on purpose: the compiler parks them in
    a deliberately unpublished runtime chapter (see
    ``ContentRuntimeCompiler._runtime_chapter``), so ``shop.access.can_launch`` is
    their publication gate instead. Mirrors the rule ``get_challenge_trial``
    already applies on the challenge side.

    ``prefix`` walks the relation from a related model, e.g. ``"adventure_level__"``
    when filtering ``AdventureLevelTier``.
    """
    return Q(**{f"{prefix}chapter__is_published": True}) | Q(
        **{f"{prefix}source_content_definition__isnull": False}
    )


MASTERY_TARGET_CAP = 8


def form_solve_targets(form_ids) -> dict[int, int]:
    """Mastery target = count of distinct published tier waves per command.

    Every wave that attaches a form (inside a required, published level) counts
    toward its target, so a command is only "mastered" after it has been used
    across many distinct scenarios. A wave attaches only the forms every one of
    its variants uses, so each counted wave is one a learner is sure to practise
    the form in. The cap keeps the bar achievable for core commands that repeat
    across the whole curriculum.
    """
    form_ids = set(form_ids)
    targets = {form_id: 0 for form_id in form_ids}
    if not form_ids:
        return targets
    rows = (
        AdventureLevelTierWave.objects.filter(
            is_published=True,
            tier__is_published=True,
            tier__adventure_level__is_published=True,
            tier__adventure_level__is_required=True,
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
