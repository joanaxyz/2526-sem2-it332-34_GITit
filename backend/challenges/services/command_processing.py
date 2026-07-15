from django.db import transaction
from django.utils import timezone

from challenges.models import ChallengeRun
from common.constants import (
    COMMAND_COUNTED,
    DIFFICULTY_EASY,
    DIFFICULTY_MEDIUM,
    RESULT_INVALID,
    RESULT_TARGET_MATCHED,
    RESULT_UNPROCESSABLE,
    SESSION_STATUS_COMPLETED,
    SESSION_STATUS_FAILED,
    SESSION_STATUS_STARTED,
)
from common.exceptions import Locked
from common.git.client_command_execution import ClientCommandExecutionService
from common.git.command_outcomes import command_outcome_payload
from common.git.repository_state import VariantTargetStateHashCache
from common.runtime import (
    apply_command_accounting,
    command_budget_exhausted,
    repository_response_snapshot,
    rule_counts,
    update_fields_for_execution,
)
from common.services.performance import timing
from evaluation.completion import CompletionEvaluationContext, PracticeCompletionEvaluator
from practice.models import CommandStep
from practice.services.scaffolding import FeedbackGenerationService
from practice.services.visualization import RepositoryVisualizationService
from progress.chests import ChapterChestService
from progress.models import ChallengeLevelCompletion, ChallengeTrialCompletion
from progress.services import StreakService
from progress.wallet import WalletService
from simulator.services import (
    RepositorySnapshotService,
    RepositoryStateSimulator,
)

from .history import CommandHistoryCache


class ChallengeCommandProcessingService:
    def __init__(self) -> None:
        self.state_tools = RepositoryStateSimulator()
        self.snapshotter = RepositorySnapshotService()
        self.visualizer = RepositoryVisualizationService()
        self.executor = ClientCommandExecutionService()

    # savepoint=False: the submit view already opened the transaction (to hold
    # the run-row lock), so join it directly instead of paying a nested
    # SAVEPOINT/RELEASE round trip. Standalone callers still get their own.
    @transaction.atomic(savepoint=False)
    def submit_command(self, *, run: ChallengeRun, command: str, execution: dict) -> dict:
        if run.status != SESSION_STATUS_STARTED:
            raise Locked("This challenge run has already ended.")

        state_tools = self.state_tools

        def span(stage: str):
            return timing(f"challenge.command.{stage}", run_id=run.id)

        execution = self.executor.from_payload(
            repository_state=run.repository_state,
            command=command,
            execution=execution,
            timing_label="challenge.command",
            run_id=run.id,
            expected_client_revision=run.total_attempts,
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
        previous_rules_passing = 0
        rules_passing = 0
        total_rules = max(1, run.max_counted_commands)
        if command_result.processed:
            with span("evaluate"):
                state_hash = state_tools.state_hash_for_normalized(next_state)
                expected_state_hash = VariantTargetStateHashCache().hash_for(
                    variant=run.variant,
                    state_tools=state_tools,
                )
                previous_history = CommandHistoryCache().history_for(run=run)
                previous_evaluation = PracticeCompletionEvaluator().evaluate(
                    CompletionEvaluationContext(
                        run=run,
                        previous_state=previous_state,
                        next_state=previous_state,
                        executed_commands=previous_history,
                        next_state_hash=state_tools.state_hash_for_normalized(previous_state),
                        expected_state_hash=expected_state_hash,
                        next_state_already_normalized=True,
                    )
                )
                previous_rules_passing, total_rules = rule_counts(previous_evaluation)
                executed_commands = [*previous_history, command_result.normalized_command]
                evaluation = PracticeCompletionEvaluator().evaluate(
                    CompletionEvaluationContext(
                        run=run,
                        previous_state=previous_state,
                        next_state=next_state,
                        executed_commands=executed_commands,
                        next_state_hash=state_hash,
                        expected_state_hash=expected_state_hash,
                        next_state_already_normalized=True,
                    )
                )
                result_category = evaluation.result_category
                rules_passing, total_rules = rule_counts(evaluation)
                if _uses_contextual_feedback(run) and classification == COMMAND_COUNTED:
                    feedback = FeedbackGenerationService().describe(previous_state, next_state)
        else:
            result_category = RESULT_INVALID if command.strip().lower().startswith("git") else RESULT_UNPROCESSABLE
            state_hash = state_tools.state_hash_for_normalized(next_state)
            expected_state_hash = VariantTargetStateHashCache().hash_for(
                variant=run.variant,
                state_tools=state_tools,
            )

        accounting = apply_command_accounting(
            run,
            classification=classification,
            increment=increment,
            total_field="total_attempts",
            counted_field="counted_action_total",
            diagnostic_field="non_counted_diagnostic_total",
        )

        solved = result_category == RESULT_TARGET_MATCHED
        failed = command_budget_exhausted(
            solved=solved,
            classification=classification,
            counted_total=run.counted_action_total,
            max_counted_commands=run.max_counted_commands,
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
                # Command logging folded into the step INSERT (was a second
                # CommandLog write); command_text already carries the raw command.
                normalized_command=command_result.normalized_command,
                was_processable=command_result.processed,
            )
        if command_result.processed:
            CommandHistoryCache().remember_after_append(
                run=run,
                previous_history=executed_commands[:-1],
                normalized_command=command_result.normalized_command,
            )

        # Only persist the (large) repository_state JSON when the command actually
        # changed it. Read-only/invalid commands leave it identical, so re-writing
        # the blob is wasted I/O on the hot path.
        if execution.state_mutated:
            run.repository_state = next_state
        update_fields = set(update_fields_for_execution(
            accounting.changed_fields,
            state_mutated=execution.state_mutated,
        ))
        chest_pending = False
        if solved:
            completion_fields, chest_pending = self._complete_run(run)
            update_fields.update(completion_fields)
        elif failed:
            run.status = SESSION_STATUS_FAILED
            run.ended_at = timezone.now()
            run.failure_reason = "You ran out of counted commands before reaching the target repository state."
            update_fields.update({"status", "ended_at", "failure_reason"})

        with span("run_save"):
            run.save(update_fields=sorted(update_fields))
        if chest_pending:
            ChapterChestService().award_chests(player=run.player, chapter=run.chapter)
        with span("response_snapshot"):
            repository_snapshot = repository_response_snapshot(
                self.snapshotter,
                command_result=command_result,
                previous_state=previous_state,
                next_state=next_state,
            )
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
            "command_outcome": command_outcome_payload(
                processed=command_result.processed,
                counted=classification == COMMAND_COUNTED,
                solved=solved,
                failed=failed,
                command_family=command_result.command_family or "default",
                previous_rules_passing=previous_rules_passing,
                rules_passing=rules_passing,
                total_rules=total_rules,
                max_counted_commands=run.max_counted_commands,
                counted_command_count=run.counted_action_total,
            ),
        }

    def _complete_run(self, run: ChallengeRun) -> tuple[set[str], bool]:
        """Mark the run completed and record trial progress. Returns the saved
        field names plus whether a chapter-chest check should run after the
        caller persists this run (the check reads completed runs from the DB)."""
        from adventures.scoring import stars as compute_stars

        run.status = SESSION_STATUS_COMPLETED
        run.completed_at = timezone.now()
        run.ended_at = run.completed_at
        first_try = run.retry_index == 0
        run.stars = compute_stars(
            solved=True,
            counted_commands=run.counted_action_total,
            budget=run.min_counted_commands,
            first_try=first_try,
        )
        chest_pending = False
        if not run.is_replay:
            completion, created = ChallengeTrialCompletion.objects.get_or_create(
                player=run.player,
                challenge_trial=run.challenge_trial,
                defaults={
                    "challenge_run": run,
                    "stars": run.stars,
                    "counted_action_total": run.counted_action_total,
                },
            )
            if not created and (
                run.stars > completion.stars
                or (
                    run.stars == completion.stars
                    and run.counted_action_total < completion.counted_action_total
                )
            ):
                completion.challenge_run = run
                completion.stars = run.stars
                completion.counted_action_total = run.counted_action_total
                completion.completed_at = run.completed_at
                completion.save(
                    update_fields=[
                        "challenge_run",
                        "stars",
                        "counted_action_total",
                        "completed_at",
                    ]
                )
            self._complete_challenge_level_if_ready(run=run)
            StreakService().record_completion(player=run.player, completed_at=run.completed_at)
            # Authored trial reward; the ledger award_key keeps it once-per-trial.
            if run.challenge_trial.reward_coins:
                WalletService().award(
                    player=run.player,
                    amount=run.challenge_trial.reward_coins,
                    reason="challenge_trial_reward",
                    award_key=f"trial-reward:{run.challenge_trial_id}",
                )
            chest_pending = True
        return {"status", "completed_at", "ended_at", "stars"}, chest_pending

    def _complete_challenge_level_if_ready(self, *, run: ChallengeRun) -> None:
        trial_ids = set(
            run.challenge_trial.challenge_level.trials.filter(is_published=True).values_list(
                "id",
                flat=True,
            )
        )
        if not trial_ids:
            return
        completed_ids = set(
            ChallengeTrialCompletion.objects.filter(
                player=run.player,
                challenge_trial_id__in=trial_ids,
            ).values_list("challenge_trial_id", flat=True)
        )
        if trial_ids <= completed_ids:
            ChallengeLevelCompletion.objects.get_or_create(
                player=run.player,
                challenge_level=run.challenge_trial.challenge_level,
            )

def _uses_contextual_feedback(run: ChallengeRun) -> bool:
    return run.difficulty == DIFFICULTY_EASY

def _visible_target_state(run: ChallengeRun) -> dict | None:
    if run.difficulty in (DIFFICULTY_EASY, DIFFICULTY_MEDIUM):
        return run.variant.target_state
    return None
