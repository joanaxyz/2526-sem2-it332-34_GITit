"""Introduce a command form the moment the problem first needs it.

The next useful move comes from the variant's generated solution trajectory,
not from per-command rules, so any seeded or authored problem is covered. A
form is introduced only when the learner has never met it: not introduced
before, not practised to a solve, and never run successfully anywhere.
"""

from __future__ import annotations

from dataclasses import dataclass

from django.db.models import Q

from adventures.models import SkillMastery
from common.constants import RESULT_INVALID, RESULT_UNPROCESSABLE, SESSION_STATUS_STARTED
from practice.models import CommandStep
from simulator.trajectory import next_solution_step
from tutoring.models import PlayerCommandIntroduction
from tutoring.services.forms import FormGuide, command_matches_form, resolve_form

# Bounds the "used it before" scan; a learner with this many distinct spellings
# of one command family has certainly met it.
_USAGE_SCAN_LIMIT = 300


@dataclass(frozen=True)
class Candidate:
    form: FormGuide
    # The concrete solution command, revealed only after a missed attempt.
    example: str
    # What the repository needs from this move, derived from the replay.
    step_effect: tuple[dict[str, str], ...]
    step_index: int

    @property
    def teaching_key(self) -> str:
        return self.form.teaching_key


def plan_introduction(run) -> Candidate | None:
    if run.status != SESSION_STATUS_STARTED or not run.current_wave_id:
        return None
    from adventures.services.tier_history import TierCommandHistoryCache

    history = TierCommandHistoryCache().history_for(run=run)
    step = next_solution_step(run.selected_variant.solution_trajectory, run.repository_state, history)
    if step is None:
        return None
    wave_forms = run.current_wave.command_forms.filter(is_published=True).select_related("command_skill")
    form = resolve_form(step["command"], preferred=wave_forms)
    if form is None or form_is_known(run.player_id, form):
        return None
    return Candidate(
        form=form,
        example=step["command"],
        step_effect=tuple(step.get("effect") or ()),
        step_index=step["index"],
    )


def form_is_known(player_id: int, form: FormGuide) -> bool:
    if PlayerCommandIntroduction.objects.filter(player_id=player_id, teaching_key=form.teaching_key).exists():
        return True
    if SkillMastery.objects.filter(
        player_id=player_id, command_form__usage_form=form.usage_form, solves__gt=0
    ).exists():
        return True
    used = (
        CommandStep.objects.filter(
            Q(adventure_tier_run__player_id=player_id)
            | Q(attempt__player_id=player_id)
            | Q(challenge_run__player_id=player_id),
            was_processable=True,
            normalized_command__startswith=f"git {form.family}",
        )
        .exclude(result_category__in=[RESULT_INVALID, RESULT_UNPROCESSABLE])
        .values_list("normalized_command", flat=True)
        .distinct()[:_USAGE_SCAN_LIMIT]
    )
    return any(command_matches_form(command, form.usage_form) for command in used)
