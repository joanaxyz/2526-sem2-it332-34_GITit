from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from adventures.models import AdventureLevel, AdventureRun

from .access_helpers import (
    _completion_payload,
    _level_commands,
)

if TYPE_CHECKING:
    from progress.models import AdventureLevelCompletion


@dataclass(frozen=True)
class AdventureAccessContext:
    """User-specific state for an ordered group of Adventures.

    Adventures are a linear progression within a chapter. Completion rows are
    batch-loaded once so building the overview never issues a query per level.
    """

    completion_by_adventure_id: dict[int, AdventureLevelCompletion] = field(default_factory=dict)
    passed_adventure_ids: set[int] = field(default_factory=set)
    locked_adventure_ids: set[int] = field(default_factory=set)
    lock_reasons: dict[int, str] = field(default_factory=dict)


def _build_adventure_access(*, player, adventures: list[AdventureLevel]) -> AdventureAccessContext:
    if not adventures:
        return AdventureAccessContext()

    completion_by_adventure_id: dict[int, AdventureLevelCompletion] = {}
    passed_adventure_ids: set[int] = set()
    if player is not None:
        from progress.models import AdventureLevelCompletion

        adventure_ids = [adventure.id for adventure in adventures]
        passed_adventure_ids = set(
            AdventureRun.objects.filter(
                player=player,
                level_id__in=adventure_ids,
                passed_at__isnull=False,
            ).values_list("level_id", flat=True)
        )
        completion_by_adventure_id = {
            completion.adventure_level_id: completion
            for completion in AdventureLevelCompletion.objects.filter(
                player=player,
                adventure_level_id__in=adventure_ids,
            ).only("adventure_level_id", "stars", "counted_action_total", "completed_at")
        }
        passed_adventure_ids |= completion_by_adventure_id.keys()

    locked_adventure_ids: set[int] = set()
    lock_reasons: dict[int, str] = {}
    previous: AdventureLevel | None = None
    for adventure in adventures:
        if previous is not None and previous.id not in passed_adventure_ids:
            locked_adventure_ids.add(adventure.id)
            lock_reasons[adventure.id] = f"Complete {previous.title} to unlock this adventure."
        previous = adventure

    return AdventureAccessContext(
        completion_by_adventure_id=completion_by_adventure_id,
        passed_adventure_ids=passed_adventure_ids,
        locked_adventure_ids=locked_adventure_ids,
        lock_reasons=lock_reasons,
    )


def adventure_locked(*, player, adventure: AdventureLevel) -> tuple[bool, str]:
    """Return whether the immediately preceding adventure still blocks launch."""
    adventures = list(
        AdventureLevel.objects.filter(
            chapter_id=adventure.chapter_id, is_published=True
        ).order_by("sort_order", "id")
    )
    access = _build_adventure_access(player=player, adventures=adventures)
    return (
        adventure.id in access.locked_adventure_ids,
        access.lock_reasons.get(adventure.id, ""),
    )


def level_locked(*, player, level: AdventureLevel) -> tuple[bool, str]:
    """Return whether this adventure level is blocked by the previous level in the chapter."""
    return adventure_locked(player=player, adventure=level)


def adventure_summary_payload(
    *,
    player,
    adventure: AdventureLevel,
    access: AdventureAccessContext | None = None,
) -> dict:
    if access is None:
        chapter_adventures = list(
            AdventureLevel.objects.filter(
                chapter_id=adventure.chapter_id, is_published=True
            ).order_by("sort_order", "id")
        )
        access = _build_adventure_access(player=player, adventures=chapter_adventures)

    completion = access.completion_by_adventure_id.get(adventure.id)
    is_passed = adventure.id in access.passed_adventure_ids

    return {
        "item_type": "adventure",
        "id": adventure.id,
        "slug": adventure.slug,
        "title": adventure.title,
        "command": ", ".join(_level_commands(adventure)),
        "is_passed": is_passed,
        "locked": adventure.id in access.locked_adventure_ids,
        "lock_reason": access.lock_reasons.get(adventure.id, ""),
        "completion": _completion_payload(completion),
    }


def _adventure_passed(*, player, chapter_id: int) -> bool:
    required_level_ids = set(
        AdventureLevel.objects.filter(
            chapter_id=chapter_id,
            is_published=True,
            is_required=True,
        ).values_list("id", flat=True)
    )
    if not required_level_ids:
        return True
    from progress.models import AdventureLevelCompletion

    completed_level_ids = set(
        AdventureLevelCompletion.objects.filter(
            player=player,
            adventure_level_id__in=required_level_ids,
        ).values_list("adventure_level_id", flat=True)
    )
    if required_level_ids <= completed_level_ids:
        return True
    passed_ids = set(
        AdventureRun.objects.filter(
            player=player, level_id__in=required_level_ids, passed_at__isnull=False
        ).values_list("level_id", flat=True)
    )
    return required_level_ids <= passed_ids
