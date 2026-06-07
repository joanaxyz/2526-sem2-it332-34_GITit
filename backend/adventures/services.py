"""CommandAdventure run orchestration.

Kept separate from the challenge/session flow so adventure progression
(ordered problems, mastery weighting) never shares logic with challenge
completion/unlock behavior.
"""

from django.db import transaction
from django.utils import timezone

from common.constants import (
    COMMAND_COUNTED,
    SESSION_STATUS_COMPLETED,
    SESSION_STATUS_FAILED,
    SESSION_STATUS_STARTED,
)
from common.exceptions import Locked
from evaluation.compiler import compile_evaluation_spec
from evaluation.engine import EvaluationEngine
from adventures.models import AdventureProblem, AdventureProblemAttempt, AdventureRun, CommandAdventure
from adventures.scoring import AdventureScoringService
from practice.models import CommandLog, CommandStep
from practice.services import CommandCountClassifier
from simulator.command_engine import SimulatedGitCommandEngine
from simulator.services import RepositoryStateSimulator


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

    @transaction.atomic
    def start_run(self, *, user, adventure: CommandAdventure) -> AdventureRun:
        problems = ordered_problems_for(adventure)
        if not problems:
            raise Locked("This adventure has no published problems.")
        active = AdventureRun.objects.filter(
            user=user, command_adventure=adventure, status=SESSION_STATUS_STARTED
        ).first()
        if active:
            raise Locked("Finish or abandon the active run before starting again.")
        run = AdventureRun.objects.create(user=user, command_adventure=adventure)
        self._open_attempt(run=run, problem=problems[0], order=0)
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
        variant = attempt.selected_variant
        score = self.scorer.score_attempt(
            solved=solved,
            counted_commands=counted_command_count,
            ideal_commands=variant.ideal_counted_commands or variant.min_counted_commands,
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
        self._advance(run=attempt.run)
        return attempt

    def _advance(self, *, run: AdventureRun) -> None:
        problems = ordered_problems_for(run.command_adventure)
        next_index = run.attempts.count()
        if next_index < len(problems):
            run.current_problem_index = next_index
            run.save(update_fields=["current_problem_index"])
            self._open_attempt(run=run, problem=problems[next_index], order=next_index)
        else:
            self._finish(run=run, problems=problems)

    def _finish(self, *, run: AdventureRun, problems: list[AdventureProblem]) -> None:
        attempts = list(run.attempts.all())
        if attempts:
            run.total_score = round(sum(a.final_score for a in attempts) / len(attempts))
            run.mastery_progress_gained = round(
                sum(a.mastery_gain for a in attempts) / len(problems), 4
            )
        solved_problem_ids = {
            a.adventure_problem_id for a in attempts if a.status == SESSION_STATUS_COMPLETED
        }
        required_unsolved = any(
            p.is_required and p.id not in solved_problem_ids for p in problems
        )
        run.status = SESSION_STATUS_FAILED if required_unsolved else SESSION_STATUS_COMPLETED
        run.completed_at = timezone.now()
        run.save(
            update_fields=[
                "total_score",
                "mastery_progress_gained",
                "status",
                "completed_at",
            ]
        )

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
        self, *, run: AdventureRun, problem: AdventureProblem, order: int
    ) -> AdventureProblemAttempt:
        variant = problem.variants.filter(is_published=True).order_by("semantic_key", "id").first()
        if variant is None:
            raise Locked("This adventure problem has no published variants.")
        return AdventureProblemAttempt.objects.create(
            run=run,
            adventure_problem=problem,
            selected_variant=variant,
            order=order,
            repository_state=variant.initial_state,
        )

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


class AdventureCommandService:
    """Processes a submitted command for one AdventureProblemAttempt.

    Reuses the shared simulator + evaluator engines but never the challenge
    completion flow. On reaching the target (or exhausting the command budget)
    it hands off to AdventureRunService for mastery scoring.
    """

    def __init__(self) -> None:
        self.sim = RepositoryStateSimulator()
        self.engine = SimulatedGitCommandEngine()
        self.runs = AdventureRunService()

    @transaction.atomic
    def submit(self, *, attempt: AdventureProblemAttempt, command: str) -> dict:
        if attempt.status != SESSION_STATUS_STARTED:
            raise Locked("This attempt has already ended.")
        variant = attempt.selected_variant
        previous_state = self.sim.clone_state(attempt.repository_state)
        working_state = self.sim.normalize_state(previous_state)
        result = self.engine.process(working_state, command, mutate_in_place=True)
        next_state = self.sim.normalize_state(result.state)

        classification, increment = CommandCountClassifier().classify(
            command=command, processed=result.processed, diagnostic=result.diagnostic
        )
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
        CommandLog.objects.create(
            step_log=step,
            raw_command=command,
            normalized_command=result.normalized_command,
            was_processable=result.processed,
        )
        attempt.save(
            update_fields=["command_count", "counted_command_count", "repository_state"]
        )

        max_counted = attempt.selected_variant.max_counted_commands
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
            "solved": solved,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "exit_code": result.exit_code,
            "terminal_output": result.output,
            "command_classification": classification,
            "repository_state": next_state,
        }
