"""CommandAdventure run orchestration.

Kept separate from the challenge/session flow so adventure progression
(ordered quests, mastery weighting) never shares logic with challenge
completion/unlock behavior.
"""

from collections import OrderedDict

from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from adventures.models import (
    AdventureMastery,
    AdventureQuest,
    AdventureQuestAttempt,
    AdventureRun,
    CommandAdventure,
)
from adventures.scheduler import (
    BOX_VALUE,
    AdventureScheduler,
    encounter_index,
    is_passed,
)
from adventures.scoring import AdventureScoringService, mastery_points
from common.constants import (
    COMMAND_COUNTED,
    SESSION_MODE_PRIMARY,
    SESSION_MODE_REPLAY,
    SESSION_STATUS_COMPLETED,
    SESSION_STATUS_FAILED,
    SESSION_STATUS_STARTED,
)
from common.exceptions import Locked
from common.performance import timing
from evaluation.compiler import CompiledEvaluationSpecCache
from evaluation.engine import EvaluationEngine
from practice.models import CommandLog, CommandStep
from practice.services import CommandExecutor, VariantTargetStateHashCache, log_command_step
from progress.chests import StoreyChestService
from simulator.services import RepositoryStateSimulator
from simulator.workspace_files import WorkspaceFileError, WorkspaceFileStateService


def ordered_quests_for(
    adventure: CommandAdventure, *, with_prerequisites: bool = False
) -> list[AdventureQuest]:
    queryset = AdventureQuest.objects.filter(
        command_form__command_skill__storey_id=adventure.storey_id,
        is_published=True,
        command_form__is_published=True,
        command_form__command_skill__is_published=True,
    ).order_by("command_form__command_skill__sort_order", "command_form__sort_order", "sort_order", "id")
    if with_prerequisites:
        # The scheduler walks quest.prerequisites for every candidate; the
        # prefetch turns that per-quest N+1 into a single extra query.
        queryset = queryset.prefetch_related("prerequisites")
    return list(queryset)


class AdventureCommandHistoryCache:
    """Process-local LRU of an attempt's normalized command history, mirroring
    challenges.services.CommandHistoryCache. The key includes the attempt's log
    count, so a stale entry is never served: any miss (other worker, rollback,
    restart) falls back to the DB query."""

    _cache: OrderedDict[tuple[int, int], list[str]] = OrderedDict()
    _max_entries = 512

    def history_for(self, *, attempt: AdventureQuestAttempt, log_count: int) -> list[str]:
        key = (attempt.id, log_count)
        cached = self._cache.get(key)
        if cached is not None:
            self._cache.move_to_end(key)
            return list(cached)

        history = list(
            CommandLog.objects.filter(step__attempt=attempt)
            .order_by("step_id")
            .values_list("normalized_command", flat=True)
        )
        self._remember(key, history)
        return history

    def remember(
        self, *, attempt: AdventureQuestAttempt, log_count: int, history: list[str]
    ) -> None:
        self._remember((attempt.id, log_count), history)

    def _remember(self, key: tuple[int, int], history: list[str]) -> None:
        self._cache[key] = list(history)
        self._cache.move_to_end(key)
        while len(self._cache) > self._max_entries:
            self._cache.popitem(last=False)


class AdventureRunService:
    def __init__(self) -> None:
        self.scorer = AdventureScoringService()
        self.scheduler = AdventureScheduler()

    @transaction.atomic
    def start_run(self, *, user, adventure: CommandAdventure) -> AdventureRun:
        quests = ordered_quests_for(adventure)
        if not quests:
            raise Locked("This adventure has no published quests.")
        # Re-entering an adventure (replay, refresh, or navigating back in)
        # resumes the run already in progress rather than locking the user out.
        # This keeps the "one active run per adventure" invariant while letting
        # a finished adventure always be replayed: completed/failed/abandoned
        # runs are terminal, so they never match here and a fresh run is created.
        active = (
            AdventureRun.objects.filter(
                user=user, command_adventure=adventure, status=SESSION_STATUS_STARTED
            )
            .order_by("-id")
            .first()
        )
        if active:
            return active
        # Once the adventure has been passed, every further playthrough is an
        # uncounted free-play replay: it stays fully playable (the scheduler's
        # mastery view would otherwise have nothing left to serve and finish the
        # run instantly) but never touches mastery, the pass milestone, or KPIs.
        mode = (
            SESSION_MODE_REPLAY
            if AdventureRun.objects.filter(
                user=user, command_adventure=adventure, passed_at__isnull=False
            ).exists()
            else SESSION_MODE_PRIMARY
        )
        run = AdventureRun.objects.create(user=user, command_adventure=adventure, mode=mode)
        self._open_next(run=run)
        return run

    def current_attempt(self, *, run: AdventureRun) -> AdventureQuestAttempt | None:
        return run.attempts.filter(status=SESSION_STATUS_STARTED).order_by("order").first()

    # savepoint=False: when nested inside the submit transaction this joins it
    # instead of paying SAVEPOINT/RELEASE round trips; standalone callers still
    # get their own transaction.
    @transaction.atomic(savepoint=False)
    def record_attempt_result(
        self,
        *,
        attempt: AdventureQuestAttempt,
        solved: bool,
        counted_command_count: int,
        command_count: int,
        hint_count: int = 0,
        repository_state: dict | None = None,
    ) -> AdventureQuestAttempt:
        if attempt.status != SESSION_STATUS_STARTED:
            raise Locked("This attempt has already been scored.")
        score = self.scorer.score_attempt(
            solved=solved,
            counted_commands=counted_command_count,
            ideal_commands=attempt.adventure_quest.min_counted_commands,
            hint_count=hint_count,
        )
        attempt.correctness_score = score.correctness_score
        attempt.efficiency_score = score.efficiency_score
        attempt.independence_score = score.independence_score
        attempt.final_score = score.final_score
        attempt.mastery_gain = score.mastery_gain
        attempt.hint_count = hint_count
        attempt.command_count = command_count
        attempt.counted_command_count = counted_command_count
        attempt.status = SESSION_STATUS_COMPLETED if score.passed else SESSION_STATUS_FAILED
        attempt.completed_at = timezone.now()
        update_fields = [
            "correctness_score",
            "efficiency_score",
            "independence_score",
            "final_score",
            "mastery_gain",
            "hint_count",
            "command_count",
            "counted_command_count",
            "status",
            "completed_at",
        ]
        if repository_state is not None:
            attempt.repository_state = repository_state
            update_fields.append("repository_state")
        # update_fields keeps the big repository_state JSON off the wire unless it
        # actually changed (the submit path has already persisted it).
        attempt.save(update_fields=update_fields)

        run = attempt.run
        # The ordered-quests join feeds the pass check, the scheduler, and the
        # mastery fraction below; resolve it once per transition.
        quests = ordered_quests_for(run.command_adventure, with_prerequisites=True)
        # Replays are uncounted free-play: the attempt is still scored (so the
        # learner sees how the run went), but mastery, session score, and the
        # pass milestone are left untouched. Primary runs alone drive progress.
        if run.mode != SESSION_MODE_REPLAY:
            box_advanced = self.scheduler.apply_result(
                user=run.user,
                quest=attempt.adventure_quest,
                passed=score.passed,
                solved=solved,
            )
            run.session_score += mastery_points(
                box_advanced=box_advanced, final_score=score.final_score, box_value=BOX_VALUE
            )
            newly_passed = run.passed_at is None and is_passed(
                user=run.user,
                adventure=run.command_adventure,
                session_score=run.session_score,
                quests=quests,
            )
            if newly_passed:
                run.passed_at = timezone.now()
            run.save(update_fields=["session_score", "passed_at"])
            if newly_passed:
                # Passing the adventure moves the storey progress bar; GitCoins
                # come from the progress chests, so check them now that
                # passed_at is persisted.
                StoreyChestService().award_chests(
                    user=run.user, storey=run.command_adventure.storey
                )

        self._open_next(run=run, quests=quests)
        return attempt

    def _open_next(
        self, *, run: AdventureRun, quests: list[AdventureQuest] | None = None
    ) -> AdventureQuestAttempt | None:
        """Open the next command-quest, or finish the session when there is
        nothing left to serve. Primary runs ask the mastery scheduler; replays
        walk the adventure once, ignoring mastery, so a passed adventure stays
        fully playable instead of finishing the instant it starts."""
        if quests is None:
            quests = ordered_quests_for(run.command_adventure, with_prerequisites=True)
        if run.mode == SESSION_MODE_REPLAY:
            quest = self._next_replay_quest(run=run, quests=quests)
        else:
            quest = self.scheduler.next_quest(
                user=run.user, adventure=run.command_adventure, quests=quests
            )
        if quest is None:
            self._finish(run=run, quests=quests)
            return None
        return self._open_attempt(run=run, quest=quest)

    def _next_replay_quest(
        self, *, run: AdventureRun, quests: list[AdventureQuest]
    ) -> AdventureQuest | None:
        """Next unplayed command in this replay: a single linear walk through the
        adventure's ordered quests, decoupled from the global mastery view."""
        served_ids = set(run.attempts.values_list("adventure_quest_id", flat=True))
        for quest in quests:
            if quest.id not in served_ids:
                return quest
        return None

    def _finish(self, *, run: AdventureRun, quests: list[AdventureQuest]) -> None:
        # Primary: reached only when the scheduler has nothing left to serve, i.e.
        # every command is mastered. The pass milestone (passed_at) is set earlier
        # and independently, the instant the session score crosses the pass bar.
        # Replay: reached once the linear walk is exhausted; it earns no mastery
        # progress because it is uncounted.
        run.status = SESSION_STATUS_COMPLETED
        run.completed_at = timezone.now()
        run.mastery_progress_gained = (
            0.0 if run.mode == SESSION_MODE_REPLAY else self._mastery_fraction(run, quests)
        )
        run.save(update_fields=["status", "completed_at", "mastery_progress_gained"])

    def _mastery_fraction(self, run: AdventureRun, quests: list[AdventureQuest]) -> float:
        """Share of total Leitner boxes filled across the adventure, in [0, 1]."""
        ceiling = sum(q.required_successful_attempts for q in quests)
        if not ceiling:
            return 0.0
        strengths = dict(
            AdventureMastery.objects.filter(
                user_id=run.user_id, adventure_quest__in=[q.id for q in quests]
            ).values_list("adventure_quest_id", "strength")
        )
        filled = sum(
            min(strengths.get(q.id, 0), q.required_successful_attempts) for q in quests
        )
        return round(filled / ceiling, 4)

    @transaction.atomic
    def abandon(self, *, run: AdventureRun) -> AdventureRun:
        if run.status != SESSION_STATUS_STARTED:
            return run
        run.attempts.filter(status=SESSION_STATUS_STARTED).update(
            status=SESSION_STATUS_FAILED, completed_at=timezone.now()
        )
        run.status = "abandoned"
        run.completed_at = timezone.now()
        run.save(update_fields=["status", "completed_at"])
        return run

    def _open_attempt(
        self, *, run: AdventureRun, quest: AdventureQuest
    ) -> AdventureQuestAttempt:
        variant = self.scheduler.select_variant(user=run.user, quest=quest)
        if variant is None:
            raise Locked("This adventure quest has no published variants.")
        attempt = AdventureQuestAttempt.objects.create(
            run=run,
            adventure_quest=quest,
            selected_variant=variant,
            order=run.attempts.count(),
            repository_state=variant.initial_state,
        )
        if run.mode == SESSION_MODE_REPLAY:
            # Free-play never mutates mastery; progress is just the linear walk's
            # position through this replay's quests.
            run.current_quest_index = run.attempts.count()
        else:
            idx = encounter_index(user=run.user, adventure=run.command_adventure)
            self.scheduler.mark_served(user=run.user, quest=quest, idx=idx)
            # current_quest_index now tracks distinct commands introduced
            # (progress hint for the UI); the linear walk it once meant no longer
            # applies.
            run.current_quest_index = (
                AdventureMastery.objects.filter(
                    user=run.user,
                    adventure_quest__command_form__command_skill__storey=run.command_adventure.storey,
                    introduced=True,
                ).count()
            )
        run.save(update_fields=["current_quest_index"])
        return attempt

    # Non-answer-revealing nudges used when a variant authors no hint_set, or
    # once the authored hints are exhausted.
    GENERIC_HINTS = [
        "Re-read the task and check the current repository state with a read-only command.",
        "Think about which single Git command changes the state the task describes.",
        "Inspect what changed after your last command before trying another.",
    ]

    @transaction.atomic
    def use_hint(self, *, attempt: AdventureQuestAttempt) -> dict:
        if attempt.status != SESSION_STATUS_STARTED:
            raise Locked("This attempt has already been scored.")
        index = attempt.hint_count
        attempt.hint_count += 1
        attempt.save(update_fields=["hint_count"])
        authored = attempt.selected_variant.hint_set or []
        if index < len(authored):
            hint = authored[index]
        else:
            hint = self.GENERIC_HINTS[index % len(self.GENERIC_HINTS)]
        return {"attempt": attempt, "hint": hint, "hint_number": attempt.hint_count}


class AdventureWorkspaceFileService:
    """Workspace file create/edit for the live attempt.

    The adventure counterpart of practice.services.WorkspaceFileCreationService:
    challenges keep repository_state on the run, adventures on the attempt.
    """

    @transaction.atomic
    def create_file(
        self, *, attempt: AdventureQuestAttempt, path: str, content: str = ""
    ) -> AdventureQuestAttempt:
        if attempt.status != SESSION_STATUS_STARTED:
            raise Locked("This attempt has already ended.")
        try:
            next_state = WorkspaceFileStateService().create_file(
                attempt.repository_state, path=path, content=content
            )
        except WorkspaceFileError as exc:
            raise ValidationError({"path": [str(exc)]}) from exc
        attempt.repository_state = next_state
        attempt.save(update_fields=["repository_state"])
        return attempt

    @transaction.atomic
    def write_file(
        self, *, attempt: AdventureQuestAttempt, path: str, content: str = ""
    ) -> AdventureQuestAttempt:
        if attempt.status != SESSION_STATUS_STARTED:
            raise Locked("This attempt has already ended.")
        try:
            next_state = WorkspaceFileStateService().write_file(
                attempt.repository_state, path=path, content=content
            )
        except WorkspaceFileError as exc:
            raise ValidationError({"path": [str(exc)]}) from exc
        attempt.repository_state = next_state
        attempt.save(update_fields=["repository_state"])
        return attempt


class AdventureCommandService:
    """Processes a submitted command for one AdventureQuestAttempt.

    Reuses the shared simulator + evaluator engines but never the challenge
    completion flow. On reaching the target (or exhausting the command budget)
    it hands off to AdventureRunService for mastery scoring.
    """

    def __init__(self) -> None:
        self.sim = RepositoryStateSimulator()
        self.executor = CommandExecutor()
        self.runs = AdventureRunService()

    @transaction.atomic
    def submit(self, *, attempt: AdventureQuestAttempt, command: str) -> dict:
        if attempt.status != SESSION_STATUS_STARTED:
            raise Locked("This attempt has already ended.")
        run_id = attempt.run_id

        def span(stage: str):
            return timing(f"adventure.command.{stage}", run_id=run_id)

        variant = attempt.selected_variant
        execution = self.executor.execute(
            repository_state=attempt.repository_state,
            command=command,
            timing_label="adventure.command",
            run_id=run_id,
        )
        result = execution.result
        next_state = execution.next_state
        classification, increment = execution.classification, execution.increment
        attempt.command_count += 1
        if classification == COMMAND_COUNTED:
            attempt.counted_command_count += increment
        attempt.repository_state = next_state

        solved = False
        executed: list[str] = []
        if result.processed:
            with span("evaluate"):
                # Every submit logs exactly one CommandLog, so the pre-increment
                # command count equals the number of logs already persisted — the
                # cache key the previous submit remembered its history under.
                history = AdventureCommandHistoryCache().history_for(
                    attempt=attempt, log_count=attempt.command_count - 1
                )
                executed = [*history, result.normalized_command]
                outcome = EvaluationEngine().evaluate(
                    spec=CompiledEvaluationSpecCache().spec_for(
                        key=("variant", variant.id, variant.semantic_key or ""),
                        raw_spec=variant.evaluation_spec,
                    ),
                    next_state=next_state,
                    initial_state=variant.initial_state,
                    executed_commands=executed,
                    next_state_hash=self.sim.state_hash_for_normalized(next_state),
                    expected_state_hash=VariantTargetStateHashCache().hash_for(
                        variant=variant, state_tools=self.sim
                    ),
                )
                solved = outcome.target_matched

        with span("step_create"):
            step = CommandStep.objects.create(
                attempt=attempt,
                command_text=command,
                terminal_output=result.output,
                result_category=CommandStep.ResultCategory.TARGET_MATCHED
                if solved
                else CommandStep.ResultCategory.TARGET_NOT_YET_MATCHED
                if result.processed
                else CommandStep.ResultCategory.UNPROCESSABLE,
                command_classification=classification,
                counted_increment=increment,
                attempt_number=attempt.command_count,
                counted_total_after=attempt.counted_command_count,
                # repository_state intentionally omitted: the live attempt already
                # holds current state, and this column is write-only (no replay path
                # reads it), so persisting the full JSON here was a duplicate write.
            )
        with span("log_create"):
            log_command_step(step, command=command, result=result)
        if result.processed:
            AdventureCommandHistoryCache().remember(
                attempt=attempt, log_count=attempt.command_count, history=executed
            )
        # The big repository_state JSON is persisted only when the command actually
        # changed it; read-only/invalid commands leave it identical.
        update_fields = ["command_count", "counted_command_count"]
        if execution.state_mutated:
            update_fields.append("repository_state")
        with span("attempt_save"):
            attempt.save(update_fields=update_fields)

        max_counted = attempt.adventure_quest.max_counted_commands
        budget_exhausted = attempt.counted_command_count >= max_counted
        if solved or budget_exhausted:
            # repository_state is omitted: this submit already persisted
            # next_state on the attempt, so re-sending the JSON blob is waste.
            self.runs.record_attempt_result(
                attempt=attempt,
                solved=solved,
                counted_command_count=attempt.counted_command_count,
                command_count=attempt.command_count,
                hint_count=attempt.hint_count,
            )
            attempt.refresh_from_db()

        return {
            "attempt": attempt,
            "step": step,
            "solved": solved,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "exit_code": result.exit_code,
            "terminal_output": result.output,
            "command_classification": classification,
            "repository_state": next_state,
        }
