"""Ordered waves inside an adventure difficulty tier.

A tier holds one or more published waves, played in ``sort_order``. A run
plays the learner's next uncleared wave; a wave is cleared once the learner
has solved it ``required_successful_attempts`` times (one for designed waves;
several only for the transitional single-wave tiers that repeat one pool);
the tier completes when every published wave is cleared.
"""

from __future__ import annotations

from adventures.models import AdventureLevelTierRun, AdventureLevelTierWave
from common.constants import SESSION_STATUS_COMPLETED


def published_waves(tier) -> list[AdventureLevelTierWave]:
    return list(tier.waves.filter(is_published=True).order_by("sort_order", "id"))


def cleared_slugs(progress) -> list[str]:
    return list(progress.cleared_wave_slugs or []) if progress is not None else []


def next_wave(waves: list[AdventureLevelTierWave], progress) -> AdventureLevelTierWave | None:
    """The first published wave the learner has not cleared, or None."""
    cleared = set(cleared_slugs(progress))
    return next((wave for wave in waves if wave.slug not in cleared), None)


def solved_wave_runs(*, player, wave) -> int:
    """Completed, graded (non-replay, non-transfer) runs of this wave."""
    return AdventureLevelTierRun.objects.filter(
        player=player,
        current_wave=wave,
        status=SESSION_STATUS_COMPLETED,
        is_replay=False,
        is_transfer=False,
    ).count()


def wave_progress(
    waves: list[AdventureLevelTierWave], progress, *, tier_completed: bool = False
) -> dict:
    """Clears toward the tier: each wave counts its required clears.

    Only the next uncleared wave can be partly done, and only on a
    transitional single-wave tier that needs several clears; its partial
    count is the clears not yet spent on earlier waves. A completed tier is
    fully cleared even when its completion predates per-wave tracking.
    """
    if tier_completed:
        total = sum(max(1, wave.required_successful_attempts) for wave in waves)
        return {"completed": total, "total": total, "cleared": True, "next_wave": None}
    cleared = set(cleared_slugs(progress))
    spare = progress.successful_clears if progress is not None else 0
    completed = total = 0
    upcoming = None
    for index, wave in enumerate(waves, start=1):
        needed = max(1, wave.required_successful_attempts)
        total += needed
        if wave.slug in cleared:
            completed += needed
            spare -= needed
            continue
        if upcoming is None:
            completed += max(0, min(spare, needed - 1))
            upcoming = {"index": index, "slug": wave.slug, "title": wave.title}
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
