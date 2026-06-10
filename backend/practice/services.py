from collections import OrderedDict
from contextlib import nullcontext
from dataclasses import dataclass
from typing import Any

from django.db import transaction
from rest_framework.exceptions import ValidationError

from common.constants import (
    COMMAND_COUNTED,
    COMMAND_DIAGNOSTIC,
    COMMAND_UNPROCESSABLE,
    DIFFICULTY_EASY,
    DIFFICULTY_MEDIUM,
    RESULT_INVALID,
    RESULT_TARGET_MATCHED,
    RESULT_UNPROCESSABLE,
    SESSION_MODE_PRIMARY,
    SESSION_STATUS_COMPLETED,
    SESSION_STATUS_FAILED,
    SESSION_STATUS_STARTED,
)
from common.exceptions import Locked
from common.performance import timing
from evaluation.completion import CompletionEvaluationContext, PracticeCompletionEvaluator
from progress.models import ProblemCompletion
from progress.services import StreakService
from challenges.models import ChallengeRun
from challenges.selectors import (
    required_successful_attempts_for_problem,
    session_meets_progress_threshold,
)
from challenges.services import CommandHistoryCache
from practice.models import CommandLog, CommandStep
from practice.scaffolding import FeedbackGenerationService
from practice.visualization import RepositoryVisualizationService
from simulator.command_engine import SimulatedGitCommandEngine
from simulator.services import (
    RepositorySnapshotService,
    RepositoryStateSimulator,
    is_diagnostic_command,
    normalize_command,
)
from simulator.workspace_files import WorkspaceFileError, WorkspaceFileStateService


class CommandCountClassifier:
    def classify(self, *, command: str, processed: bool, diagnostic: bool | None = None) -> tuple[str, int]:
        if not processed:
            normalized = normalize_command(command).lower()
            if normalized == "git" or normalized.startswith("git "):
                return COMMAND_COUNTED, 1
            return COMMAND_UNPROCESSABLE, 0
        is_diagnostic = diagnostic if diagnostic is not None else is_diagnostic_command(command)
        if is_diagnostic:
            return COMMAND_DIAGNOSTIC, 0
        return COMMAND_COUNTED, 1


@dataclass(frozen=True)
class ExecutedCommand:
    """Outcome of running a single command through the simulated git engine,
    before any feature-specific evaluation or persistence."""

    previous_state: dict
    next_state: dict
    result: Any
    classification: str
    increment: int


class CommandExecutor:
    """Shared command-execution primitive for both the challenge and adventure
    flows: clone the repository state, run the simulated git engine, normalize the
    result, and classify the command. Each flow layers its own evaluation,
    persistence, and scoring on top; only this raw execution is identical.

    Challenge passes `timing_label`/`run_id` to keep its per-stage timing spans;
    adventure omits them, so it stays uninstrumented exactly as before."""

    def __init__(self) -> None:
        self.state_tools = RepositoryStateSimulator()
        self.command_engine = SimulatedGitCommandEngine()

    def execute(
        self,
        *,
        repository_state: dict,
        command: str,
        timing_label: str | None = None,
        run_id: int | None = None,
    ) -> ExecutedCommand:
        tools = self.state_tools

        def span(stage: str):
            return timing(f"{timing_label}.{stage}", run_id=run_id) if timing_label else nullcontext()

        with span("repository_state_clone"):
            previous_state = tools.clone_state(repository_state)
            working_state = tools.normalize_state(previous_state)
        with span("parse_execute"):
            result = self.command_engine.process(working_state, command, mutate_in_place=True)
        with span("repository_state_normalize"):
            next_state = tools.normalize_state(result.state)

        classification, increment = CommandCountClassifier().classify(
            command=command, processed=result.processed, diagnostic=result.diagnostic
        )
        return ExecutedCommand(
            previous_state=previous_state,
            next_state=next_state,
            result=result,
            classification=classification,
            increment=increment,
        )


def log_command_step(step: CommandStep, *, command: str, result: Any) -> None:
    """Persist the raw/normalized command for a step. Identical across flows."""
    CommandLog.objects.create(
        step_log=step,
        raw_command=command,
        normalized_command=result.normalized_command,
        was_processable=result.processed,
    )


class VariantTargetStateHashCache:
    _cache: OrderedDict[tuple[int, str], str] = OrderedDict()
    _max_entries = 512

    def hash_for(self, *, variant, state_tools: RepositoryStateSimulator) -> str:
        key = (variant.id, variant.semantic_key or "")
        cached = self._cache.get(key)
        if cached is not None:
            self._cache.move_to_end(key)
            return cached

        state_hash = state_tools.state_hash(variant.target_state)
        self._cache[key] = state_hash
        self._cache.move_to_end(key)
        while len(self._cache) > self._max_entries:
            self._cache.popitem(last=False)
        return state_hash


def _state_affects_visible_tree(previous_state: dict, next_state: dict) -> bool:
    for key in ("commits", "staging", "working_tree", "conflicts", "branches", "head"):
        if previous_state.get(key) != next_state.get(key):
            return True
    return False


def _command_response_includes_project_tree(*, command_result, previous_state: dict, next_state: dict) -> bool:
    if not command_result.processed or command_result.diagnostic:
        return False
    return _state_affects_visible_tree(previous_state, next_state)


class CommandProcessingService:
    def __init__(self) -> None:
        self.state_tools = RepositoryStateSimulator()
        self.snapshotter = RepositorySnapshotService()
        self.visualizer = RepositoryVisualizationService()
        self.executor = CommandExecutor()

    @transaction.atomic
    def submit_command(self, *, run: ChallengeRun, command: str) -> dict:
        if run.status != SESSION_STATUS_STARTED:
            raise Locked("This challenge run has already ended.")

        state_tools = self.state_tools
        execution = self.executor.execute(
            repository_state=run.repository_state,
            command=command,
            timing_label="challenge.command",
            run_id=run.id,
        )
        previous_state = execution.previous_state
        next_state = execution.next_state
        command_result = execution.result
        classification, increment = execution.classification, execution.increment
        result_category = RESULT_UNPROCESSABLE
        feedback = ""
        executed_commands: list[str] = []
        state_hash = ""
        expected_state_hash = ""
        if command_result.processed:
            state_hash = state_tools.state_hash_for_normalized(next_state)
            expected_state_hash = VariantTargetStateHashCache().hash_for(
                variant=run.variant,
                state_tools=state_tools,
            )
            previous_history = CommandHistoryCache().history_for(run=run)
            executed_commands = [*previous_history, command_result.normalized_command]
            evaluation = PracticeCompletionEvaluator().evaluate(
                CompletionEvaluationContext(
                    session=run,
                    previous_state=previous_state,
                    next_state=next_state,
                    executed_commands=executed_commands,
                    next_state_hash=state_hash,
                    expected_state_hash=expected_state_hash,
                )
            )
            result_category = evaluation.result_category
            if _uses_contextual_feedback(run) and classification == COMMAND_COUNTED:
                feedback = FeedbackGenerationService().describe(previous_state, next_state)
        else:
            result_category = RESULT_INVALID if command.strip().lower().startswith("git") else RESULT_UNPROCESSABLE
            state_hash = state_tools.state_hash_for_normalized(next_state)
            expected_state_hash = VariantTargetStateHashCache().hash_for(
                variant=run.variant,
                state_tools=state_tools,
            )

        if classification == COMMAND_COUNTED:
            run.counted_action_total += increment
        elif classification == COMMAND_DIAGNOSTIC:
            run.non_counted_diagnostic_total += 1
        run.total_attempts += 1
        if result_category != RESULT_TARGET_MATCHED:
            run.first_attempt_star_eligible = False
        run.repository_state = next_state

        visualization_snapshot = self.visualizer.snapshot(
            next_state,
            previous_state=previous_state,
            target_state=_visible_target_state(run),
        )
        step = CommandStep.objects.create(
            session=run,
            command_text=command,
            terminal_output=command_result.output,
            result_category=result_category,
            command_classification=classification,
            counted_increment=increment,
            attempt_number=run.total_attempts,
            counted_total_after=run.counted_action_total,
            state_hash=state_hash,
            expected_state_hash=expected_state_hash,
            contextual_feedback=feedback,
            visualization_snapshot=visualization_snapshot,
        )
        log_command_step(step, command=command, result=command_result)
        if command_result.processed:
            CommandHistoryCache().remember_after_append(
                run=run,
                previous_history=executed_commands[:-1],
                normalized_command=command_result.normalized_command,
            )

        max_count = run.command_budget_snapshot["max_counted_commands"]
        update_fields = {"repository_state", "total_attempts", "first_attempt_star_eligible"}
        if classification == COMMAND_COUNTED:
            update_fields.add("counted_action_total")
        elif classification == COMMAND_DIAGNOSTIC:
            update_fields.add("non_counted_diagnostic_total")
        if result_category == RESULT_TARGET_MATCHED:
            update_fields.update(self._complete_run(run))
        elif classification == COMMAND_COUNTED and run.counted_action_total >= max_count:
            run.status = SESSION_STATUS_FAILED
            from django.utils import timezone

            run.ended_at = timezone.now()
            run.failure_reason = "Action limit reached before the target repository state was reached."
            update_fields.update({"status", "ended_at", "failure_reason"})

        run.save(update_fields=sorted(update_fields))
        if _command_response_includes_project_tree(
            command_result=command_result,
            previous_state=previous_state,
            next_state=next_state,
        ):
            repository_snapshot = self.snapshotter.snapshot(next_state, already_normalized=True)
        else:
            repository_snapshot = self.snapshotter.snapshot_for_command(next_state, already_normalized=True)
        return {
            "run": run,
            "step": step,
            "terminal_output": command_result.output,
            "stdout": command_result.stdout,
            "stderr": command_result.stderr,
            "exit_code": command_result.exit_code,
            "command_family": command_result.command_family,
            "diagnostic_metadata": command_result.diagnostic_metadata,
            "repository_state": repository_snapshot,
            "visualization": visualization_snapshot,
            "evaluation_result": result_category,
            "command_classification": classification,
            "contextual_feedback": feedback,
        }

    def _complete_run(self, run: ChallengeRun) -> set[str]:
        from django.utils import timezone

        run.status = SESSION_STATUS_COMPLETED
        run.completed_at = timezone.now()
        run.ended_at = run.completed_at
        run.rta_success = bool(run.rta_eligible and run.first_attempt_star_eligible)
        if run.mode == SESSION_MODE_PRIMARY:
            required = required_successful_attempts_for_problem(run.challenge_level)
            previous_progress = 0
            for prior_run in ChallengeRun.objects.filter(
                user=run.user,
                mode=SESSION_MODE_PRIMARY,
                status=SESSION_STATUS_COMPLETED,
                challenge_level=run.challenge_level,
            ).exclude(pk=run.pk):
                if session_meets_progress_threshold(session=prior_run):
                    previous_progress += 1
            current_meets_progress = session_meets_progress_threshold(session=run)
            if previous_progress + (1 if current_meets_progress else 0) >= required:
                completion, created = ProblemCompletion.objects.get_or_create(
                    user=run.user,
                    challenge_level=run.challenge_level,
                    defaults={
                        "challenge_run": run,
                        "first_attempt_star": run.first_attempt_star_eligible,
                        "counted_action_total": run.counted_action_total,
                    },
                )
                if not created:
                    completion.challenge_run = run
                    completion.first_attempt_star = run.first_attempt_star_eligible
                    completion.counted_action_total = run.counted_action_total
                    completion.completed_at = run.completed_at
                    completion.save(update_fields=["challenge_run", "first_attempt_star", "counted_action_total", "completed_at"])
                StreakService().record_completion(user=run.user, completed_at=run.completed_at)
        return {"status", "completed_at", "ended_at", "rta_success"}


def _uses_contextual_feedback(run: ChallengeRun) -> bool:
    return run.difficulty == DIFFICULTY_EASY


def _visible_target_state(run: ChallengeRun) -> dict | None:
    if run.difficulty in (DIFFICULTY_EASY, DIFFICULTY_MEDIUM):
        return run.variant.target_state
    return None


class WorkspaceFileCreationService:
    @transaction.atomic
    def create_file(self, *, run: ChallengeRun, path: str, content: str = "") -> ChallengeRun:
        if run.status != SESSION_STATUS_STARTED:
            raise Locked("This challenge run has already ended.")
        try:
            next_state = WorkspaceFileStateService().create_file(run.repository_state, path=path, content=content)
        except WorkspaceFileError as exc:
            raise ValidationError({"path": [str(exc)]}) from exc
        run.repository_state = next_state
        run.save(update_fields=["repository_state"])
        return run

    @transaction.atomic
    def write_file(self, *, run: ChallengeRun, path: str, content: str = "") -> ChallengeRun:
        if run.status != SESSION_STATUS_STARTED:
            raise Locked("This challenge run has already ended.")
        try:
            next_state = WorkspaceFileStateService().write_file(run.repository_state, path=path, content=content)
        except WorkspaceFileError as exc:
            raise ValidationError({"path": [str(exc)]}) from exc
        run.repository_state = next_state
        run.save(update_fields=["repository_state"])
        return run
