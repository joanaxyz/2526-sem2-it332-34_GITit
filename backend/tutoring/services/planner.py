"""Plan what to teach around the learner's next move.

The next useful move comes from the variant's generated solution trajectory,
not from per-command rules, so any seeded or authored problem is covered.
Back-to-back steps that one command can do together are offered as that one
command (`git add a` + `git add b` -> `git add a b`).

A move teaches two ways:

- Its command form gets a **command guide**, anchored to the form's home
  scenario (``homes.py``). The guide opens there until the learner completes
  it; anywhere else the plan only points at the home, so playing out of order
  never uses a guide up.
- The techniques it writes (several paths, ``HEAD~2``, ``a..b``...) and the
  ideas it touches (staging area, branch...) become **tips** (``tips.py``),
  shown with the move every time it comes up.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import cached_property

from common.constants import SESSION_STATUS_STARTED
from curriculum.models import CommandForm
from simulator.trajectory import next_solution_step
from tutoring.models import CommandGuideHome, PlayerCommandIntroduction
from tutoring.services.concepts import concepts_for
from tutoring.services.forms import FormGuide, catalog_forms, command_family, resolve_form
from tutoring.services.techniques import batch_command, techniques_in
from tutoring.services.tips import Tip, concept_tip, technique_tip


class PlannerReads:
    """The player history and form catalog a plan reads, each read at most once.

    A command submission plans twice: before the command runs and again for
    its response. Share one instance between them; only the step the command
    just recorded changes in between, and ``remember_history`` adds it.
    Without a shared instance each plan reads afresh.
    """

    def __init__(self, player_id: int) -> None:
        self.player_id = player_id
        self._history: dict[tuple[int, int], list[str]] = {}
        self._catalog: dict[str, list[CommandForm]] = {}
        self._scenario_forms: dict[int, list[CommandForm]] = {}
        self._homes: dict[str, CommandGuideHome | None] = {}

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

    def catalog(self, family: str) -> list[CommandForm]:
        if family not in self._catalog:
            self._catalog[family] = catalog_forms(family)
        return self._catalog[family]

    def scenario_forms(self, scenario) -> list[CommandForm]:
        if scenario.id not in self._scenario_forms:
            self._scenario_forms[scenario.id] = list(
                scenario.command_forms.filter(is_published=True).select_related("command_skill")
            )
        return self._scenario_forms[scenario.id]

    def home(self, teaching_key: str) -> CommandGuideHome | None:
        if teaching_key not in self._homes:
            self._homes[teaching_key] = (
                CommandGuideHome.objects.filter(teaching_key=teaching_key)
                .select_related("scenario__tier__adventure_level__chapter")
                .first()
            )
        return self._homes[teaching_key]

    def homes_in(self, scenario_id: int) -> list[str]:
        """Teaching keys of the forms whose guides open in this scenario."""
        return list(
            CommandGuideHome.objects.filter(scenario_id=scenario_id)
            .order_by("id")
            .values_list("teaching_key", flat=True)
        )


@dataclass(frozen=True)
class Candidate:
    """A command guide for the next move."""

    form: FormGuide
    # The concrete command for this step, revealed only after a missed attempt.
    example: str
    # What the repository needs from this command, derived from the replay.
    step_effect: tuple[dict[str, str], ...]
    step_index: int
    # The last solution step the command covers (later than step_index when
    # back-to-back steps were combined into one command).
    last_step_index: int

    @property
    def teaching_key(self) -> str:
        return self.form.teaching_key


@dataclass(frozen=True)
class TaughtElsewhere:
    """The next move's form, whose unfinished guide lives in another scenario."""

    form: FormGuide
    home: CommandGuideHome


@dataclass(frozen=True)
class MovePlan:
    guide: Candidate | None = None
    elsewhere: TaughtElsewhere | None = None
    tips: tuple[Tip, ...] = ()


def plan_move(run, reads: PlannerReads | None = None) -> MovePlan | None:
    """What to teach for the run's next solution move, or ``None`` off route."""

    if run.status != SESSION_STATUS_STARTED or not run.current_scenario_id:
        return None
    reads = reads or PlannerReads(run.player_id)
    trajectory = run.selected_variant.solution_trajectory
    step = next_solution_step(trajectory, run.repository_state, reads.history(run))
    if step is None:
        return None
    steps = trajectory["steps"]
    command, last = batch_command(steps, step["index"])
    effects = tuple(
        change
        for covered in steps[step["index"] : last + 1]
        if not covered.get("diagnostic")
        for change in covered.get("effect") or ()
    )
    form = resolve_form(
        command, preferred=reads.scenario_forms(run.current_scenario), catalog=reads.catalog
    )
    guide = elsewhere = None
    if form is not None and form.teaching_key not in reads.introduced:
        home = reads.home(form.teaching_key)
        if home is not None and home.scenario_id == run.current_scenario_id:
            guide = Candidate(form, command, effects, step["index"], last)
        elif home is not None:
            elsewhere = TaughtElsewhere(form, home)
    return MovePlan(guide, elsewhere, _tips(run, command, effects))


def plan_introduction(run, reads: PlannerReads | None = None) -> Candidate | None:
    """The command guide for the run's next move, if one opens here."""

    plan = plan_move(run, reads)
    return plan.guide if plan else None


def _tips(run, command: str, effects: tuple[dict, ...]) -> tuple[Tip, ...]:
    family = command_family(command) or ""
    return (
        *(concept_tip(key) for key in concepts_for(effects)),
        *(
            technique_tip(technique, family)
            for technique in techniques_in(command, run.repository_state)
        ),
    )
