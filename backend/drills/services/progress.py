"""Record one reported Squire's Drill session.

The drill pays no currency and unlocks nothing, so the client is allowed to
grade itself and report the result - forging it buys a cosmetic mark and a
worse practice readout, nothing more. What the backend does own is the
shape: counts are clamped against the session actually offered, and the
reported weak spots are intersected with the level's real command-form keys
so stored vocabulary stays authored.
"""

from __future__ import annotations

from django.db import transaction
from django.utils import timezone

from adventures.models import AdventureLevel
from drills.models import DrillProgress
from drills.selectors.content import drill_card_keys


def _accuracy(correct: int, total: int) -> int:
    if total <= 0:
        return 0
    return max(0, min(100, round(correct * 100 / total)))


@transaction.atomic
def record_drill_session(
    *,
    player,
    level: AdventureLevel,
    answers_total: int,
    answers_correct: int,
    completed: bool,
    shaky_form_keys: list[str],
) -> DrillProgress:
    known_keys = drill_card_keys(level_id=level.id)
    shaky = [key for key in dict.fromkeys(shaky_form_keys) if key in known_keys]
    answers_correct = min(answers_correct, answers_total)
    accuracy = _accuracy(answers_correct, answers_total)
    now = timezone.now()

    progress, _ = DrillProgress.objects.select_for_update().get_or_create(
        player=player,
        adventure_level=level,
        defaults={"shaky_form_keys": []},
    )
    progress.sessions += 1
    progress.last_accuracy = accuracy
    progress.best_accuracy = max(progress.best_accuracy, accuracy)
    progress.shaky_form_keys = shaky
    progress.last_played_at = now
    if completed:
        progress.clears += 1
        if progress.first_cleared_at is None:
            progress.first_cleared_at = now
    progress.save(
        update_fields=[
            "sessions",
            "clears",
            "best_accuracy",
            "last_accuracy",
            "shaky_form_keys",
            "first_cleared_at",
            "last_played_at",
        ]
    )
    return progress
