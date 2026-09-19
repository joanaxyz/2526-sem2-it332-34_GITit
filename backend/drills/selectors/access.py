"""Per-player drill state, read in batches.

The level map asks "has this level been drilled?" for every node it draws,
so this module exists to answer that in one query for a whole chapter. It
deliberately holds no content composition (see ``drills.services.composer``)
and imports nothing from ``curriculum`` or ``adventures`` selectors, so
other apps can read drill state without an import cycle.
"""

from __future__ import annotations

from collections.abc import Iterable

from drills.models import DrillProgress


def get_drill_progress(*, player, level_id: int) -> DrillProgress | None:
    if player is None:
        return None
    return DrillProgress.objects.filter(player=player, adventure_level_id=level_id).first()


def drill_progress_by_level_id(
    *, player, level_ids: Iterable[int]
) -> dict[int, DrillProgress]:
    level_ids = list(level_ids)
    if player is None or not level_ids:
        return {}
    return {
        progress.adventure_level_id: progress
        for progress in DrillProgress.objects.filter(
            player=player, adventure_level_id__in=level_ids
        )
    }


def drill_access_payload(*, available: bool, progress: DrillProgress | None) -> dict:
    """The level map's slice of drill state: is there one, and is it done.

    Intentionally thinner than the full drill payload - the map never needs
    the cards, and composing them per node would cost queries per level.
    """
    return {
        "available": available,
        "cleared": bool(progress and progress.is_cleared),
        "best_accuracy": progress.best_accuracy if progress else 0,
    }
