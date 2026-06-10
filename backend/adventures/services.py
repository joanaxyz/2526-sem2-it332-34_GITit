"""CommandAdventure run orchestration.

Kept separate from the challenge/session flow so adventure progression
(ordered problems, mastery weighting) never shares logic with challenge
completion/unlock behavior.
"""

from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from adventures.models import (
    AdventureMastery,
    AdventureProblem,
    AdventureProblemAttempt,
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
    SESSION_STATUS_COMPLETED,
    SESSION_STATUS_FAILED,
    SESSION_STATUS_STARTED,
)
from common.exceptions import Locked
from evaluation.compiler import compile_evaluation_spec
from evaluation.engine import EvaluationEngine
from practice.models import CommandLog, CommandStep
from practice.services import CommandExecutor, log_command_step
from simulator.services import RepositoryStateSimulator
from simulator.workspace_files import WorkspaceFileError, WorkspaceFileStateService


def ordered_problems_for(adventure: CommandAdventure) -> list[AdventureProblem]:
    return list(
        AdventureProblem.objects.filter(
            usage__topic__module=adventure.module,
            is_published=True,
            usage__is_published=True,
            usage__topic__is_published=True,
        ).order_by("usage__topic__sort_order", "usage__sort_order", "sort_order", "id")
    )


class AdventureRunService:
    def __init__(self) -> None:
        self.scorer = AdventureScoringService()
        self.scheduler = AdventureScheduler()

    @transaction.atomic
    def start_run(self, *, user, adventure: CommandAdventure) -> AdventureRun:
        problems = ordered_problems_for(adventure)
        if not problems:
            raise Locked("This adventure has no published problems.")
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
        run = AdventureRun.objects.create(user=user, command_adventure=adventure)
        self._open_next(run=run)
        return run

    def current_attempt(self, *, run: AdventureRun) -> AdventureProblemAttempt | None:
        return run.attempts.filter(status=SESSION_STATUS_STARTED).order_by("order").first()

    @transaction.atomic
    def record_attempt_result(
        self,
        *,
        attempt: AdventureProblemAttempt,
        solved: bool,
        counted_command_count: int,
        command_count: int,
        hint_count: int = 0,
        repository_state: dict | None = None,
    ) -> AdventureProblemAttempt:
        if attempt.status != SESSION_STATUS_STARTED:
            raise Locked("This attempt has already been scored.")
        score = self.scorer.score_attempt(
            solved=solved,
            counted_commands=counted_command_count,
            ideal_commands=attempt.adventure_problem.min_counted_commands,
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
        if repository_state is not None:
            attempt.repository_state = repository_state
        attempt.save()

        run = attempt.run
        box_advanced = self.scheduler.apply_result(
            user=run.user,
            problem=attempt.adventure_problem,
            passed=score.passed,
            solved=solved,
        )
        run.session_score += mastery_points(
            box_advanced=box_advanced, final_score=score.final_score, box_value=BOX_VALUE
        )
        if run.passed_at is None and is_passed(
            user=run.user, adventure=run.command_adventure, session_score=run.session_score
        ):
            run.passed_at = timezone.now()
        run.save(update_fields=["session_score", "passed_at"])

        self._open_next(run=run)
        return attempt

    def _open_next(self, *, run: AdventureRun) -> AdventureProblemAttempt | None:
        """Ask the scheduler for the next command-problem; open it, or finish the
        session when every command is mastered."""
        problem = self.scheduler.next_problem(user=run.user, adventure=run.command_adventure)
        if problem is None:
            self._finish(run=run)
            return None
        return self._open_attempt(run=run, problem=problem)

    def _finish(self, *, run: AdventureRun) -> None:
        # Reached only when the scheduler has nothing left to serve, i.e. every
        # command is mastered. The pass milestone (passed_at) is set earlier and
        # independently, the instant the session score crosses the pass bar.
        run.status = SESSION_STATUS_COMPLETED
        run.completed_at = timezone.now()
        run.mastery_progress_gained = self._mastery_fraction(run)
        run.save(update_fields=["status", "completed_at", "mastery_progress_gained"])

    def _mastery_fraction(self, run: AdventureRun) -> float:
        """Share of total Leitner boxes filled across the adventure, in [0, 1]."""
        problems = ordered_problems_for(run.command_adventure)
        ceiling = sum(p.required_successful_attempts for p in problems)
        if not ceiling:
            return 0.0
        strengths = dict(
            AdventureMastery.objects.filter(
                user=run.user, adventure_problem__in=[p.id for p in problems]
            ).values_list("adventure_problem_id", "strength")
        )
        filled = sum(
            min(strengths.get(p.id, 0), p.required_successful_attempts) for p in problems
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
        self, *, run: AdventureRun, problem: AdventureProblem
    ) -> AdventureProblemAttempt:
        variant = self.scheduler.select_variant(user=run.user, problem=problem)
        if variant is None:
            raise Locked("This adventure problem has no published variants.")
        attempt = AdventureProblemAttempt.objects.create(
            run=run,
            adventure_problem=problem,
            selected_variant=variant,
            order=run.attempts.count(),
            repository_state=variant.initial_state,
        )
        idx = encounter_index(user=run.user, adventure=run.command_adventure)
        self.scheduler.mark_served(user=run.user, problem=problem, idx=idx)
        # current_problem_index now tracks distinct commands introduced (progress
        # hint for the UI); the linear walk it once meant no longer applies.
        run.current_problem_index = (
            AdventureMastery.objects.filter(
                user=run.user,
                adventure_problem__usage__topic__module=run.command_adventure.module,
                introduced=True,
            ).count()
        )
        run.save(update_fields=["current_problem_index"])
        return attempt

    # Non-answer-revealing nudges used when a variant authors no hint_set, or
    # once the authored hints are exhausted.
    GENERIC_HINTS = [
        "Re-read the task and check the current repository state with a read-only command.",
        "Think about which single Git command changes the state the task describes.",
        "Inspect what changed after your last command before trying another.",
    ]

    @transaction.atomic
    def use_hint(self, *, attempt: AdventureProblemAttempt) -> dict:
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
        self, *, attempt: AdventureProblemAttempt, path: str, content: str = ""
    ) -> AdventureProblemAttempt:
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
        self, *, attempt: AdventureProblemAttempt, path: str, content: str = ""
    ) -> AdventureProblemAttempt:
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
    """Processes a submitted command for one AdventureProblemAttempt.

    Reuses the shared simulator + evaluator engines but never the challenge
    completion flow. On reaching the target (or exhausting the command budget)
    it hands off to AdventureRunService for mastery scoring.
    """

    def __init__(self) -> None:
        self.sim = RepositoryStateSimulator()
        self.executor = CommandExecutor()
        self.runs = AdventureRunService()

    @transaction.atomic
    def submit(self, *, attempt: AdventureProblemAttempt, command: str) -> dict:
        if attempt.status != SESSION_STATUS_STARTED:
            raise Locked("This attempt has already ended.")
        variant = attempt.selected_variant
        execution = self.executor.execute(
            repository_state=attempt.repository_state, command=command
        )
        result = execution.result
        next_state = execution.next_state
        classification, increment = execution.classification, execution.increment
        attempt.command_count += 1
        if classification == COMMAND_COUNTED:
            attempt.counted_command_count += increment
        attempt.repository_state = next_state

        solved = False
        if result.processed:
            history = list(
                CommandLog.objects.filter(step_log__attempt=attempt)
                .order_by("step_log_id")
                .values_list("normalized_command", flat=True)
            )
            executed = [*history, result.normalized_command]
            outcome = EvaluationEngine().evaluate(
                spec=compile_evaluation_spec(variant.evaluation_spec),
                next_state=next_state,
                initial_state=variant.initial_state,
                executed_commands=executed,
                next_state_hash=self.sim.state_hash_for_normalized(next_state),
                expected_state_hash=self.sim.state_hash(variant.target_state),
            )
            solved = outcome.target_matched

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
            repository_state=next_state,
        )
        log_command_step(step, command=command, result=result)
        attempt.save(
            update_fields=["command_count", "counted_command_count", "repository_state"]
        )

        max_counted = attempt.adventure_problem.max_counted_commands
        budget_exhausted = attempt.counted_command_count >= max_counted
        if solved or budget_exhausted:
            self.runs.record_attempt_result(
                attempt=attempt,
                solved=solved,
                counted_command_count=attempt.counted_command_count,
                command_count=attempt.command_count,
                hint_count=attempt.hint_count,
                repository_state=next_state,
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
