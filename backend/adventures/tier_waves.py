"""Ordered waves inside an adventure difficulty tier.

A tier holds one or more published waves, played in ``sort_order``. A run
plays the learner's next uncleared wave; one solve clears a wave, and the
tier completes when every published wave is cleared.
"""

from __future__ import annotations

from adventures.models import AdventureLevelTierRun, AdventureLevelTierWave


def published_waves(tier) -> list[AdventureLevelTierWave]:
    return list(tier.waves.filter(is_published=True).order_by("sort_order", "id"))


def cleared_slugs(progress) -> list[str]:
    return list(progress.cleared_wave_slugs or []) if progress is not None else []


def next_wave(waves: list[AdventureLevelTierWave], progress) -> AdventureLevelTierWave | None:
    """The first published wave the learner has not cleared, or None."""
    cleared = set(cleared_slugs(progress))
    return next((wave for wave in waves if wave.slug not in cleared), None)


def wave_progress(
    waves: list[AdventureLevelTierWave], progress, *, tier_completed: bool = False
) -> dict:
    """Cleared waves toward the tier, and the next one to play.

    A completed tier is fully cleared even when its completion predates
    per-wave tracking or a reseed replaced its waves.
    """
    total = len(waves)
    if tier_completed:
        return {"completed": total, "total": total, "cleared": True, "next_wave": None}
    cleared = set(cleared_slugs(progress))
    completed = sum(1 for wave in waves if wave.slug in cleared)
    upcoming = next(
        (
            {"index": index, "slug": wave.slug, "title": wave.title}
            for index, wave in enumerate(waves, start=1)
            if wave.slug not in cleared
        ),
        None,
    )
    return {
        "completed": completed,
        "total": total,
        "cleared": bool(waves) and upcoming is None,
        "next_wave": upcoming,
    }


def replay_wave(*, player, tier, waves: list[AdventureLevelTierWave]) -> AdventureLevelTierWave:
    """Free play cycles the tier's waves, starting after the last replayed one."""
    latest = (
        AdventureLevelTierRun.objects.filter(player=player, tier=tier, is_replay=True)
        .order_by("-started_at", "-id")
        .values_list("current_wave_id", flat=True)
        .first()
    )
    ids = [wave.id for wave in waves]
    if latest not in ids:
        return waves[0]
    return waves[(ids.index(latest) + 1) % len(waves)]
