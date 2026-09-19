"""Read seeded drill content.

Runtime never composes. ``manage.py seed_drills`` derives the content and
writes rows; this module hands those rows to the payload layer. A level
with no seeded drill simply has none - the level map reads availability
from the same rows, so the map and the drill page can never disagree
about whether a drill exists.
"""

from __future__ import annotations

from collections.abc import Iterable

from drills.models import LevelDrill, LevelDrillCard


def get_level_drill(*, level_id: int) -> LevelDrill | None:
    return (
        LevelDrill.objects.filter(adventure_level_id=level_id, is_published=True)
        .prefetch_related("cards")
        .first()
    )


def drill_card_payloads(drill: LevelDrill | None) -> list[dict]:
    if drill is None:
        return []
    return [
        {
            "key": card.form_key,
            "command": card.command,
            "intent": card.intent,
            "base_command": card.base_command,
            "summary": card.summary,
            "tokens": list(card.tokens or []),
            "command_choices": list(card.command_choices or []),
            "intent_choices": list(card.intent_choices or []),
            # Stored as {} when the command has no token worth hiding; the
            # contract exposes that absence as null.
            "blank": card.blank or None,
            "bank": list(card.bank or []),
        }
        for card in sorted(drill.cards.all(), key=lambda item: (item.sort_order, item.id))
    ]


def drill_sequence_payload(drill: LevelDrill | None) -> dict | None:
    if drill is None or not drill.sequence_steps:
        return None
    return {
        "label": drill.sequence_label,
        "task": drill.sequence_task,
        "steps": list(drill.sequence_steps),
    }


def drill_card_keys(*, level_id: int) -> set[str]:
    """The authored vocabulary a client may report weak spots in."""
    return set(
        LevelDrillCard.objects.filter(
            drill__adventure_level_id=level_id, drill__is_published=True
        ).values_list("form_key", flat=True)
    )


def drillable_level_ids(*, level_ids: Iterable[int]) -> set[int]:
    """Which of these levels actually have seeded drill content.

    Exact rather than a proxy: the level map paints its drill row from the
    same rows the drill page reads, so a level can never advertise a drill
    that turns out to be empty.
    """
    ids = list(level_ids)
    if not ids:
        return set()
    return set(
        LevelDrill.objects.filter(adventure_level_id__in=ids, is_published=True)
        .exclude(cards__isnull=True)
        .values_list("adventure_level_id", flat=True)
        .distinct()
    )
