"""Introduce a command form, or a technique, the moment the problem needs it.

The next useful move comes from the variant's generated solution trajectory,
not from per-command rules, so any seeded or authored problem is covered.
Back-to-back steps that one command can do together are offered as that one
command (`git add a` + `git add b` -> `git add a b`). An unknown command form
is introduced first; once the form is known, an unknown technique in the same
command (several paths, `HEAD~2`, `a..b`...) gets the guide instead.

A lesson is known once its guide was completed, or the learner used it
successfully anywhere; forms also count as known after a mastery solve.
"""

from __future__ import annotations

from dataclasses import dataclass

from django.db.models import Q

from adventures.models import SkillMastery
from common.constants import RESULT_INVALID, RESULT_UNPROCESSABLE, SESSION_STATUS_STARTED
from practice.models import CommandStep
from simulator.trajectory import next_solution_step
from tutoring.models import PlayerCommandIntroduction
from tutoring.services.concepts import concepts_for
from tutoring.services.forms import (
    FormGuide,
    command_family,
    command_matches_form,
    is_variadic,
    resolve_form,
    same_shape,
    widened_usage,
)
from tutoring.services.techniques import batch_command, techniques_in

# Bounds the "used it before" scan; a learner with this many distinct commands
# of one family has certainly met its forms.
_USAGE_SCAN_LIMIT = 300


@dataclass(frozen=True)
class Candidate:
    form: FormGuide
    # The concrete command for this step, revealed only after a missed attempt.
    example: str
    # What the repository needs from this command, derived from the replay.
    step_effect: tuple[dict[str, str], ...]
    step_index: int
    # The last solution step the command covers (later than step_index when
    # back-to-back steps were combined into one command).
    last_step_index: int
    # Plain-language ideas the learner has not met yet (see concepts.py).
    concepts: tuple[dict[str, str], ...] = ()

    @property
    def teaching_key(self) -> str:
        return self.form.teaching_key


def plan_introduction(run) -> Candidate | None:
    if run.status != SESSION_STATUS_STARTED or not run.current_wave_id:
        return None
    from adventures.services.tier_history import TierCommandHistoryCache

    trajectory = run.selected_variant.solution_trajectory
    history = TierCommandHistoryCache().history_for(run=run)
    step = next_solution_step(trajectory, run.repository_state, history)
    if step is None:
        return None
    steps = trajectory["steps"]
    command, last = batch_command(steps, step["index"])
    lesson = _next_lesson(run, command)
    if lesson is None:
        return None
    effects = tuple(
        change
        for covered in steps[step["index"] : last + 1]
        if not covered.get("diagnostic")
        for change in covered.get("effect") or ()
    )
    seen = set(PlayerCommandIntroduction.objects.filter(player_id=run.player_id).values_list("teaching_key", flat=True))
    first_guide = not any(not key.startswith("concept:") for key in seen)
    return Candidate(
        form=lesson,
        example=command,
        step_effect=effects,
        step_index=step["index"],
        last_step_index=last,
        concepts=tuple(concepts_for(effects, seen, first_guide=first_guide)),
    )


def _next_lesson(run, command: str) -> FormGuide | None:
    wave_forms = run.current_wave.command_forms.filter(is_published=True).select_related("command_skill")
    form = resolve_form(command, preferred=wave_forms)
    if form is None:
        return None
    if not lesson_is_known(run.player_id, form):
        return form
    family = command_family(command)
    for technique in techniques_in(command, run.repository_state):
        guide = technique.guide(family)
        if not lesson_is_known(run.player_id, guide):
            return guide
    return None


def lesson_is_known(player_id: int, lesson: FormGuide) -> bool:
    introduced = PlayerCommandIntroduction.objects.filter(player_id=player_id)
    if introduced.filter(teaching_key=lesson.teaching_key).exists():
        return True
    if lesson.technique is None and not is_variadic(lesson.usage_form) and any(
        # A completed "several files" guide covers the one-file form too.
        is_variadic(key.removeprefix("form:")) and same_shape(key.removeprefix("form:"), lesson.usage_form)
        for key in introduced.filter(teaching_key__startswith=f"form:git {lesson.family} ").values_list(
            "teaching_key", flat=True
        )
    ):
        return True
    if lesson.technique is None and not is_variadic(lesson.usage_form) and SkillMastery.objects.filter(
        player_id=player_id, command_form__usage_form=lesson.usage_form, solves__gt=0
    ).exists():
        return True
    prefix = "git " if lesson.technique is not None else f"git {lesson.family}"
    used = (
        CommandStep.objects.filter(
            Q(adventure_tier_run__player_id=player_id)
            | Q(attempt__player_id=player_id)
            | Q(challenge_run__player_id=player_id),
            was_processable=True,
            normalized_command__startswith=prefix,
        )
        .exclude(result_category__in=[RESULT_INVALID, RESULT_UNPROCESSABLE])
        .values_list("normalized_command", flat=True)
        .distinct()[:_USAGE_SCAN_LIMIT]
    )
    # Naming several files already shows you can name one.
    wider = None if lesson.technique is not None else widened_usage(lesson.usage_form)
    return any(
        lesson.used_by(command) or (wider is not None and command_matches_form(command, wider))
        for command in used
    )
