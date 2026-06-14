import json
from collections import OrderedDict
from contextlib import nullcontext
from dataclasses import dataclass
from typing import Any

from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from battle.state import initial_challenge_battle_state
from battle.turn import apply_battle_turn
from challenges.models import ChallengeRun
from challenges.selectors import (
    required_successful_attempts_for_level,
    run_meets_progress_threshold,
)
from challenges.services import CommandHistoryCache
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
from common.exceptions import Locked, PayloadTooLarge
from common.performance import timing
from evaluation.completion import CompletionEvaluationContext, PracticeCompletionEvaluator
from practice.models import CommandLog, CommandStep
from practice.scaffolding import FeedbackGenerationService
from practice.visualization import RepositoryVisualizationService
from progress.chests import StoreyChestService
from progress.models import LevelCompletion
from progress.services import StreakService
from simulator.command_engine import SimulatedGitCommandEngine
from simulator.services import (
    RepositorySnapshotService,
    RepositoryStateSimulator,
    is_diagnostic_command,
    normalize_command,
)
from simulator.workspace_files import WorkspaceFileError, WorkspaceFileStateService

# Cap for the serialized repository_state JSON. Stored states are typically a
# few KB; anything near this size means a runaway command sequence, and letting
# it grow bloats the DB row and every subsequent response payload.
MAX_REPOSITORY_STATE_BYTES = 256 * 1024


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
    # True only when the command actually changed repository state. Read-only
    # (diagnostic), unprocessable, and invalid commands leave the state untouched,
    # so callers can skip persisting the full repository_state JSON for them.
    state_mutated: bool


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
            # normalize_state() deep-copies internally, so working_state (which the
            # engine mutates in place) is already independent of the caller's stored
            # state. previous_state is only read afterwards (contextual feedback +
            # visible-tree diff), so the extra defensive clone this used to take was
            # pure overhead - one deep copy per command saved.
            previous_state = repository_state
            working_state = tools.normalize_state(repository_state)
        with span("parse_execute"):
            result = self.command_engine.process(working_state, command, mutate_in_place=True)
        with span("repository_state_normalize"):
            next_state = tools.normalize_state(result.state)

        # Repository state is stored as an unbounded JSON column and shipped in
        # every payload; a pathological command sequence (mass file/commit
        # creation) must not grow it past what a row and response can carry.
        if result.processed and not result.diagnostic:
            state_size = len(json.dumps(next_state, separators=(",", ":"), default=str))
            if state_size > MAX_REPOSITORY_STATE_BYTES:
                raise PayloadTooLarge(
                    "This scenario's repository grew too large to continue. "
                    "Retry the run to start from a clean state."
                )

        classification, increment = CommandCountClassifier().classify(
            command=command, processed=result.processed, diagnostic=result.diagnostic
        )
        return ExecutedCommand(
            previous_state=previous_state,
            next_state=next_state,
            result=result,
            classification=classification,
            increment=increment,
            # Only processed, non-diagnostic commands write to the repository.
            state_mutated=result.processed and not result.diagnostic,
        )


def log_command_step(step: CommandStep, *, command: str, result: Any) -> None:
    """Persist the raw/normalized command for a step. Identical across flows."""
    CommandLog.objects.create(
        step=step,
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

        def span(stage: str):
            return timing(f"challenge.command.{stage}", run_id=run.id)

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
        rules_passing: int | None = None
        if command_result.processed:
            with span("evaluate"):
                state_hash = state_tools.state_hash_for_normalized(next_state)
                expected_state_hash = VariantTargetStateHashCache().hash_for(
                    variant=run.variant,
                    state_tools=state_tools,
                )
                previous_history = CommandHistoryCache().history_for(run=run)
                executed_commands = [*previous_history, command_result.normalized_command]
                evaluation = PracticeCompletionEvaluator().evaluate(
                    CompletionEvaluationContext(
                        run=run,
                        previous_state=previous_state,
                        next_state=next_state,
                        executed_commands=executed_commands,
                        next_state_hash=state_hash,
                        expected_state_hash=expected_state_hash,
                    )
                )
                result_category = evaluation.result_category
                rules_passing = len(evaluation.passed_rules)
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

        # Battle turn: a pure function over the signals computed above. The
        # state rides the run save below - no new query.
        solved = result_category == RESULT_TARGET_MATCHED
        max_count = run.command_budget_snapshot["max_counted_commands"]
        battle_defeated = (
            not solved
            and classification == COMMAND_COUNTED
            and run.counted_action_total >= max_count
        )
        battle_events, battle_changed = apply_battle_turn(
            run,
            lambda: initial_challenge_battle_state(run.challenge_level, run.challenge_variant),
            counted=classification == COMMAND_COUNTED,
            processed=command_result.processed,
            solved=solved,
            rules_passing=rules_passing,
            skill=command_result.command_family or "default",
            defeated=battle_defeated,
        )

        with span("visualization"):
            # next_state is already normalized by the executor; skip re-normalizing.
            visualization_snapshot = self.visualizer.snapshot(
                next_state,
                previous_state=previous_state,
                target_state=_visible_target_state(run),
                already_normalized=True,
            )
        with span("step_create"):
            step = CommandStep.objects.create(
                challenge_run=run,
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
        with span("log_create"):
            log_command_step(step, command=command, result=command_result)
        if command_result.processed:
            CommandHistoryCache().remember_after_append(
                run=run,
                previous_history=executed_commands[:-1],
                normalized_command=command_result.normalized_command,
            )

        update_fields = {"total_attempts", "first_attempt_star_eligible"}
        if battle_changed:
            update_fields.add("battle_state")
        # Only persist the (large) repository_state JSON when the command actually
        # changed it. Read-only/invalid commands leave it identical, so re-writing
        # the blob is wasted I/O on the hot path.
        if execution.state_mutated:
            run.repository_state = next_state
            update_fields.add("repository_state")
        if classification == COMMAND_COUNTED:
            update_fields.add("counted_action_total")
        elif classification == COMMAND_DIAGNOSTIC:
            update_fields.add("non_counted_diagnostic_total")
        chest_pending = False
        if result_category == RESULT_TARGET_MATCHED:
            completion_fields, chest_pending = self._complete_run(run)
            update_fields.update(completion_fields)
        elif classification == COMMAND_COUNTED and run.counted_action_total >= max_count:
            run.status = SESSION_STATUS_FAILED
            run.ended_at = timezone.now()
            run.failure_reason = "Action limit reached before the target repository state was reached."
            update_fields.update({"status", "ended_at", "failure_reason"})

        with span("run_save"):
            run.save(update_fields=sorted(update_fields))
        if chest_pending:
            StoreyChestService().award_chests(user=run.user, storey=run.storey)
        with span("response_snapshot"):
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
            "battle_events": battle_events,
        }

    def _complete_run(self, run: ChallengeRun) -> tuple[set[str], bool]:
        """Mark the run completed and record level progress. Returns the saved
        field names plus whether a storey-chest check should run after the
        caller persists this run (the check reads completed runs from the DB)."""
        run.status = SESSION_STATUS_COMPLETED
        run.completed_at = timezone.now()
        run.ended_at = run.completed_at
        run.rta_success = bool(run.rta_eligible and run.first_attempt_star_eligible)
        chest_pending = False
        if run.mode == SESSION_MODE_PRIMARY:
            required = required_successful_attempts_for_level(run.challenge_level)
            previous_progress = 0
            # only(): the threshold check reads three small fields; without it every
            # prior run ships its full repository_state JSON over the wire.
            for prior_run in ChallengeRun.objects.filter(
                user=run.user,
                mode=SESSION_MODE_PRIMARY,
                status=SESSION_STATUS_COMPLETED,
                challenge_level=run.challenge_level,
            ).exclude(pk=run.pk).only("status", "counted_action_total", "command_budget_snapshot"):
                if run_meets_progress_threshold(run=prior_run):
                    previous_progress += 1
            current_meets_progress = run_meets_progress_threshold(run=run)
            if previous_progress + (1 if current_meets_progress else 0) >= required:
                completion, created = LevelCompletion.objects.get_or_create(
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
            # GitCoins come from the storey progress chests. The chest check
            # reads completed runs from the DB, so it must wait until the
            # caller persists this run - report it back for after run.save().
            chest_pending = current_meets_progress
        return {"status", "completed_at", "ended_at", "rta_success"}, chest_pending


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
