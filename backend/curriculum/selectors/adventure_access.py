from __future__ import annotations

from dataclasses import dataclass, field

from adventures.models import AdventureLevel, AdventureRun
from common.constants import SESSION_STATUS_STARTED

from .access_helpers import (
    _completion_payload,
    _learned_form_ids_for,
    _level_command_form_ids,
    _level_commands,
)


@dataclass(frozen=True)
class AdventureAccessContext:
    """User-specific state for an ordered group of Adventures.

    Adventures are a linear progression within a chapter. Keeping the prior
    completion map alongside the run summaries makes the track payload and the
    launch endpoint agree without issuing a query for every adventure card.
    """

    latest_runs: dict[int, AdventureRun] = field(default_factory=dict)
    passed_adventure_ids: set[int] = field(default_factory=set)
    completed_adventure_ids: set[int] = field(default_factory=set)
    locked_adventure_ids: set[int] = field(default_factory=set)
    lock_reasons: dict[int, str] = field(default_factory=dict)


def _build_adventure_access(*, player, adventures: list[AdventureLevel]) -> AdventureAccessContext:
    if not adventures:
        return AdventureAccessContext()

    latest_runs: dict[int, AdventureRun] = {}
    passed_adventure_ids: set[int] = set()
    completed_adventure_ids: set[int] = set()
    if player is not None:
        from progress.models import AdventureLevelCompletion

        adventure_ids = [adventure.id for adventure in adventures]
        for run in (
            AdventureRun.objects.filter(player=player, level_id__in=adventure_ids)
            .order_by("id")
            .only("id", "level_id", "status", "passed_at")
        ):
            # Started runs are intentionally not exposed back to the map:
            # leaving a session must not create a resumable backend path.
            if run.status != SESSION_STATUS_STARTED:
                latest_runs[run.level_id] = run
            if run.passed_at is not None:
                passed_adventure_ids.add(run.level_id)
        completed_adventure_ids = set(
            AdventureLevelCompletion.objects.filter(
                player=player,
                adventure_level_id__in=adventure_ids,
            ).values_list("adventure_level_id", flat=True)
        )
        passed_adventure_ids |= completed_adventure_ids

    locked_adventure_ids: set[int] = set()
    lock_reasons: dict[int, str] = {}
    previous: AdventureLevel | None = None
    for adventure in adventures:
        if previous is not None and previous.id not in passed_adventure_ids:
            locked_adventure_ids.add(adventure.id)
            lock_reasons[adventure.id] = f"Complete {previous.title} to unlock this adventure."
        previous = adventure

    return AdventureAccessContext(
        latest_runs=latest_runs,
        passed_adventure_ids=passed_adventure_ids,
        completed_adventure_ids=completed_adventure_ids,
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

    latest = access.latest_runs.get(adventure.id)
    completion = None
    if player is not None:
        from progress.models import AdventureLevelCompletion

        completion = AdventureLevelCompletion.objects.filter(
            player=player,
            adventure_level_id=adventure.id,
        ).first()

    form_ids = _level_command_form_ids(adventure)
    is_passed = adventure.id in access.passed_adventure_ids
    learned_form_ids = (
        form_ids if is_passed else _learned_form_ids_for(player=player, form_ids=form_ids)
    )
    learned_form_count = len(learned_form_ids)
    denominator = len(form_ids)
    progress_value = round((learned_form_count / denominator) * 100, 1) if denominator else 0.0

    return {
        "item_type": "adventure",
        "id": adventure.id,
        "slug": adventure.slug,
        "title": adventure.title,
        "description": adventure.description,
        "command": ", ".join(_level_commands(adventure)),
        "learned": bool(form_ids) and form_ids <= learned_form_ids,
        "completed": completion is not None,
        "status": latest.status if latest else "not_started",
        "is_passed": is_passed,
        "locked": adventure.id in access.locked_adventure_ids,
        "lock_reason": access.lock_reasons.get(adventure.id, ""),
        "wave_count": max(1, adventure.waves.count()),
        "completion": _completion_payload(completion),
        "latest_run_id": latest.id if latest else None,
        "progress": {
            "value": progress_value,
            "numerator": learned_form_count,
            "denominator": denominator,
        },
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

