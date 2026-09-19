"""Save and close a resumable drill run.

The drill is a queue several minutes long that deliberately re-asks cards
the learner missed. Losing it to a refresh means climbing the whole ladder
again, which is the exact frustration this feature exists to remove - so
the client's queue is checkpointed after every answer and handed back on
return.

The stored state is client-owned and opaque here beyond validation: the
backend bounds it, proves its card keys are authored vocabulary, and
refuses anything larger than a real session could produce. Nothing in it
affects rewards, so there is nothing to forge.
"""

from __future__ import annotations

from django.db import transaction
from django.utils import timezone

from adventures.models import AdventureLevel
from common.constants import SESSION_STATUS_ABANDONED, SESSION_STATUS_COMPLETED, SESSION_STATUS_STARTED
from drills.models import DrillRun
from drills.selectors.content import drill_card_keys


def active_run(*, player, level_id: int) -> DrillRun | None:
    if player is None:
        return None
    return DrillRun.objects.filter(
        player=player, adventure_level_id=level_id, status=SESSION_STATUS_STARTED
    ).first()


@transaction.atomic
def save_run_state(
    *,
    player,
    level: AdventureLevel,
    queue_state: dict,
    answered: int,
    correct: int,
) -> DrillRun:
    """Checkpoint the in-progress queue. Upserts the single active run."""
    run, _ = DrillRun.objects.select_for_update().get_or_create(
        player=player,
        adventure_level=level,
        status=SESSION_STATUS_STARTED,
        defaults={"queue_state": {}},
    )
    run.queue_state = queue_state
    run.answered = answered
    run.correct = min(correct, answered)
    run.save(update_fields=["queue_state", "answered", "correct", "updated_at"])
    return run


@transaction.atomic
def close_active_run(*, player, level: AdventureLevel, completed: bool) -> None:
    """Retire the active run once the session ends or is abandoned.

    Closed rather than deleted: the row is the only record that a learner
    started a drill and walked away, which is worth keeping for the
    practice readout even though nothing gates on it.
    """
    run = active_run(player=player, level_id=level.id)
    if run is None:
        return
    run.status = SESSION_STATUS_COMPLETED if completed else SESSION_STATUS_ABANDONED
    run.completed_at = timezone.now()
    run.save(update_fields=["status", "completed_at", "updated_at"])


def sanitize_queue_state(*, level_id: int, queue_state: dict) -> dict:
    """Keep stored state inside the authored vocabulary.

    A resumed queue drives which questions appear, so a card key that is
    not part of this level's seeded drill is dropped rather than trusted:
    otherwise a stale client (or a hand-edited payload) could resume into
    a question the level does not teach.
    """
    known = drill_card_keys(level_id=level_id)
    cards = queue_state.get("cards")
    if not isinstance(cards, dict):
        return {}
    kept = {key: value for key, value in cards.items() if key in known}
    queue = [key for key in queue_state.get("queue", []) if key in kept]
    return {
        "cards": kept,
        "queue": queue,
        "sequencePending": bool(queue_state.get("sequencePending")),
        "answered": int(queue_state.get("answered") or 0),
        "correct": int(queue_state.get("correct") or 0),
    }
