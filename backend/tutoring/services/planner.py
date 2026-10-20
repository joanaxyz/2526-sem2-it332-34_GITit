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
from functools import cached_property

from adventures.models import SkillMastery
from common.constants import RESULT_INVALID, RESULT_UNPROCESSABLE, SESSION_STATUS_STARTED
from curriculum.models import CommandForm
from practice.models import CommandStep
from simulator.trajectory import next_solution_step
from tutoring.models import PlayerCommandIntroduction
from tutoring.services.concepts import concepts_for
from tutoring.services.forms import (
    FormGuide,
    catalog_forms,
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
_UNUSABLE_RESULTS = (RESULT_INVALID, RESULT_UNPROCESSABLE)


class PlannerReads:
    """The player history and form catalog a plan reads, each read at most once.

    A command submission plans twice: before the command runs and again for
    its response. Share one instance between them; only the step the command
    just recorded changes in between, and ``record_step`` and
    ``remember_history`` add it. Without a shared instance each plan reads
    afresh.
    """

    def __init__(self, player_id: int) -> None:
        self.player_id = player_id
        self._history: dict[tuple[int, int], list[str]] = {}
        self._used: dict[str, list[str]] = {}
        self._catalog: dict[str, list[CommandForm]] = {}
        self._wave_forms: dict[int, list[CommandForm]] = {}

    def history(self, run) -> list[str]:
        """The run's processable commands so far."""
        key = (run.pk, run.total_attempts)
        if key not in self._history:
            from adventures.services.tier_history import TierCommandHistoryCache

            self._history[key] = TierCommandHistoryCache().history_for(run=run)
        return self._history[key]

    def remember_history(self, run, history: list[str]) -> None:
        # The shared history cache publishes only on commit, so it cannot
        # answer again inside the submission that is still recording.
        self._history[(run.pk, run.total_attempts)] = list(history)

    @cached_property
    def introduced(self) -> frozenset[str]:
        """Teaching keys of every completed guide."""
        return frozenset(
            PlayerCommandIntroduction.objects.filter(player_id=self.player_id).values_list(
                "teaching_key", flat=True
            )
        )

    @cached_property
    def practised_usage_forms(self) -> frozenset[str]:
        """Usage forms the player has solved with at least once."""
        return frozenset(
            SkillMastery.objects.filter(player_id=self.player_id, solves__gt=0).values_list(
                "command_form__usage_form", flat=True
            )
        )

    def used_commands(self, prefix: str) -> list[str]:
        """Distinct commands starting with ``prefix`` that ran successfully."""
        if prefix not in self._used:
            self._used[prefix] = list(
                # The step's own owner column is indexed; going through its
                # three possible run parents is not.
                CommandStep.objects.filter(
                    player_id=self.player_id,
                    was_processable=True,
                    normalized_command__startswith=prefix,
                )
                .exclude(result_category__in=_UNUSABLE_RESULTS)
                .values_list("normalized_command", flat=True)
                .distinct()[:_USAGE_SCAN_LIMIT]
            )
        return self._used[prefix]

    def record_step(self, *, normalized_command: str, processable: bool, result_category: str):
        """Count a command step stored after the history was read."""
        if not processable or result_category in _UNUSABLE_RESULTS:
            return
        for prefix, commands in self._used.items():
            if normalized_command.startswith(prefix) and normalized_command not in commands:
                commands.append(normalized_command)

    def catalog(self, family: str) -> list[CommandForm]:
        if family not in self._catalog:
            self._catalog[family] = catalog_forms(family)
        return self._catalog[family]

    def wave_forms(self, wave) -> list[CommandForm]:
        if wave.id not in self._wave_forms:
            self._wave_forms[wave.id] = list(
                wave.command_forms.filter(is_published=True).select_related("command_skill")
            )
        return self._wave_forms[wave.id]


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


def plan_introduction(run, reads: PlannerReads | None = None) -> Candidate | None:
    if run.status != SESSION_STATUS_STARTED or not run.current_wave_id:
        return None
    reads = reads or PlannerReads(run.player_id)
    trajectory = run.selected_variant.solution_trajectory
    step = next_solution_step(trajectory, run.repository_state, reads.history(run))
    if step is None:
        return None
    steps = trajectory["steps"]
    command, last = batch_command(steps, step["index"])
    lesson = _next_lesson(run, command, reads)
    if lesson is None:
        return None
    effects = tuple(
        change
        for covered in steps[step["index"] : last + 1]
        if not covered.get("diagnostic")
        for change in covered.get("effect") or ()
    )
    seen = reads.introduced
    first_guide = not any(not key.startswith("concept:") for key in seen)
    return Candidate(
        form=lesson,
        example=command,
        step_effect=effects,
        step_index=step["index"],
        last_step_index=last,
        concepts=tuple(concepts_for(effects, seen, first_guide=first_guide)),
    )


def _next_lesson(run, command: str, reads: PlannerReads) -> FormGuide | None:
    form = resolve_form(
        command, preferred=reads.wave_forms(run.current_wave), catalog=reads.catalog
    )
    if form is None:
        return None
    if not lesson_is_known(reads, form):
        return form
    family = command_family(command)
    for technique in techniques_in(command, run.repository_state):
        guide = technique.guide(family)
        if not lesson_is_known(reads, guide):
            return guide
    return None


def lesson_is_known(reads: PlannerReads, lesson: FormGuide) -> bool:
    introduced = reads.introduced
    if lesson.teaching_key in introduced:
        return True
    if lesson.technique is None and not is_variadic(lesson.usage_form):
        family_keys = f"form:git {lesson.family} "
        if any(
            # A completed "several files" guide covers the one-file form too.
            key.startswith(family_keys)
            and is_variadic(key.removeprefix("form:"))
            and same_shape(key.removeprefix("form:"), lesson.usage_form)
            for key in introduced
        ):
            return True
        if lesson.usage_form in reads.practised_usage_forms:
            return True
    prefix = "git " if lesson.technique is not None else f"git {lesson.family}"
    # Naming several files already shows you can name one.
    wider = None if lesson.technique is not None else widened_usage(lesson.usage_form)
    return any(
        lesson.used_by(command) or (wider is not None and command_matches_form(command, wider))
        for command in reads.used_commands(prefix)
    )
