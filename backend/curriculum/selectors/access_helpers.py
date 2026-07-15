from __future__ import annotations

from adventures.models import AdventureLevel, SkillMastery
from challenges.models import ChallengeTrial
from common.constants import DIFFICULTY_EASY, DIFFICULTY_HARD, DIFFICULTY_MEDIUM


def _level_command_form_ids(level: AdventureLevel) -> set[int]:
    return {form.id for form in level.command_forms.all()}


def _level_commands(level: AdventureLevel) -> list[str]:
    """Distinct base commands a level exercises (for the read-only overview)."""
    commands: list[str] = []
    for form in level.command_forms.all():
        command = form.command_skill.base_command
        if command not in commands:
            commands.append(command)
    return commands


def _learned_form_ids_for(*, player, form_ids: set[int]) -> set[int]:
    if player is None or not form_ids:
        return set()
    return set(
        SkillMastery.objects.filter(
            player=player,
            learned_at__isnull=False,
            command_form_id__in=form_ids,
        ).values_list("command_form_id", flat=True)
    )


def _latest_attempt_payload(run) -> dict | None:
    if not run:
        return None
    return {
        "id": run.id,
        "status": run.status,
        "stars": run.stars,
        "counted_action_total": run.counted_action_total,
        "total_attempts": run.total_attempts,
        "completed_at": run.completed_at,
        "ended_at": run.ended_at,
    }


def _completion_payload(completion) -> dict | None:
    if not completion:
        return None
    return {
        "stars": completion.stars,
        "counted_action_total": completion.counted_action_total,
        "completed_at": completion.completed_at,
    }


def _ordered_trials(trials) -> list[ChallengeTrial]:
    order = {DIFFICULTY_EASY: 0, DIFFICULTY_MEDIUM: 1, DIFFICULTY_HARD: 2}
    return sorted(trials, key=lambda trial: order.get(trial.difficulty, 99))
