from django.db import transaction
from django.utils import timezone

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
    SESSION_STATUS_ABANDONED,
    SESSION_STATUS_COMPLETED,
    SESSION_STATUS_FAILED,
    SESSION_STATUS_STARTED,
)
from common.exceptions import Locked
from evaluation.completion import CompletionEvaluationContext, ScenarioCompletionEvaluator
from learning.services import OrientationService
from progress.services import StreakService
from retries.services import VariantSelectionService
from scaffolding.services import FeedbackGenerationService, ScaffoldingService
from scenarios.models import (
    CommandLog,
    CompletionRecord,
    DifficultyInstance,
    ScenarioSession,
    StepLog,
)
from simulator.command_engine import Pygit2GitCommandEngine
from simulator.services import (
    RepositorySnapshotService,
    RepositoryStateSimulator,
    is_diagnostic_command,
    normalize_command,
)


class DifficultyAccessService:
    def status_for(self, *, user, difficulty_instance: DifficultyInstance) -> str:
        if CompletionRecord.objects.filter(
            user=user, difficulty_instance=difficulty_instance
        ).exists():
            return "completed"
        if ScenarioSession.objects.filter(
            user=user,
            difficulty_instance=difficulty_instance,
            status=SESSION_STATUS_STARTED,
            mode=SESSION_MODE_PRIMARY,
        ).exists():
            return "in_progress"
        latest_retryable = self.latest_retryable_session(
            user=user,
            difficulty_instance=difficulty_instance,
        )
        if latest_retryable and self.is_unlocked(user=user, difficulty_instance=difficulty_instance):
            return latest_retryable.status
        if self.is_unlocked(user=user, difficulty_instance=difficulty_instance):
            return "not_started"
        return "locked"

    def latest_retryable_session(self, *, user, difficulty_instance: DifficultyInstance):
        return (
            ScenarioSession.objects.filter(
                user=user,
                difficulty_instance=difficulty_instance,
                status__in=[SESSION_STATUS_FAILED, SESSION_STATUS_ABANDONED],
                mode=SESSION_MODE_PRIMARY,
            )
            .order_by("-ended_at", "-id")
            .first()
        )

    def is_unlocked(self, *, user, difficulty_instance: DifficultyInstance) -> bool:
        difficulty = difficulty_instance.difficulty
        if difficulty == DIFFICULTY_EASY:
            return True
        previous = DIFFICULTY_EASY if difficulty == DIFFICULTY_MEDIUM else DIFFICULTY_MEDIUM
        previous_instance = DifficultyInstance.objects.get(
            scenario=difficulty_instance.scenario,
            difficulty=previous,
        )
        return CompletionRecord.objects.filter(
            user=user, difficulty_instance=previous_instance
        ).exists()


class CommandCountClassifier:
    def classify(self, *, command: str, policy_snapshot: dict, processed: bool) -> tuple[str, int]:
        if not processed:
            normalized = normalize_command(command).lower()
            if normalized == "git" or normalized.startswith("git "):
                return COMMAND_COUNTED, 1
            return COMMAND_UNPROCESSABLE, 0
        if is_diagnostic_command(command):
            return COMMAND_DIAGNOSTIC, 0
        return COMMAND_COUNTED, 1


class ScenarioSessionService:
    @transaction.atomic
    def start_session(
        self,
        *,
        user,
        difficulty_instance: DifficultyInstance,
        source_entry_point: str,
        prior_session: ScenarioSession | None = None,
        mode: str = SESSION_MODE_PRIMARY,
    ) -> ScenarioSession:
        if prior_session and prior_session.difficulty_instance_id != difficulty_instance.id:
            raise Locked("Retry sessions must use the same scenario difficulty.")
        if prior_session and prior_session.status == SESSION_STATUS_STARTED:
            raise Locked("Exit the current scenario before retrying.")

        if mode == SESSION_MODE_PRIMARY and not DifficultyAccessService().is_unlocked(
            user=user, difficulty_instance=difficulty_instance
        ):
            raise Locked("This difficulty is locked until the previous level is completed.")

        student_progress = user.studentprogress
        orientation_complete = OrientationService().is_orientation_complete(user)

        if mode == SESSION_MODE_PRIMARY and prior_session is None:
            active_session = (
                ScenarioSession.objects.select_related(
                    "scenario",
                    "learning_unit",
                    "difficulty_instance",
                    "variant",
                )
                .filter(
                    user=user,
                    difficulty_instance=difficulty_instance,
                    status=SESSION_STATUS_STARTED,
                    mode=SESSION_MODE_PRIMARY,
                )
                .first()
            )
            if active_session:
                raise Locked("Exit the current scenario before starting again.")

        variant = VariantSelectionService().select_variant(
            user=user,
            difficulty_instance=difficulty_instance,
            prior_session=prior_session,
        )
        changed_variant = bool(prior_session and prior_session.variant_id != variant.id)
        retry_index = prior_session.retry_index + 1 if prior_session else 0

        rta_eligible = bool(
            mode == SESSION_MODE_PRIMARY
            and prior_session
            and prior_session.status in (SESSION_STATUS_FAILED, SESSION_STATUS_ABANDONED)
            and changed_variant
        )
        policy = difficulty_instance.command_policy.snapshot()
        session = ScenarioSession.objects.create(
            user=user,
            learning_unit=difficulty_instance.scenario.learning_unit,
            scenario=difficulty_instance.scenario,
            difficulty_instance=difficulty_instance,
            variant=variant,
            prior_session=prior_session,
            source_entry_point=source_entry_point,
            mode=mode,
            orientation_complete_at_start=orientation_complete,
            rta_eligible=rta_eligible,
            changed_variant=changed_variant,
            retry_index=retry_index,
            command_policy_snapshot=policy,
            repository_state=variant.initial_state,
        )
        if mode == SESSION_MODE_PRIMARY and student_progress.first_scenario_started_at is None:
            student_progress.first_scenario_started_at = session.started_at
            student_progress.orientation_complete_at_first_start = orientation_complete
            student_progress.save(
                update_fields=[
                    "first_scenario_started_at",
                    "orientation_complete_at_first_start",
                ]
            )
        return session

    @transaction.atomic
    def abandon(self, *, session: ScenarioSession) -> ScenarioSession:
        if session.status != SESSION_STATUS_STARTED:
            return session
        session.status = SESSION_STATUS_ABANDONED
        session.ended_at = timezone.now()
        session.failure_reason = "Student left the session before completion."
        session.save(update_fields=["status", "ended_at", "failure_reason"])
        return session


class CommandProcessingService:
    @transaction.atomic
    def submit_command(self, *, session: ScenarioSession, command: str) -> dict:
        if session.status != SESSION_STATUS_STARTED:
            raise Locked("This session has already ended.")

        state_tools = RepositoryStateSimulator()
        snapshotter = RepositorySnapshotService()
        command_engine = Pygit2GitCommandEngine()
        previous_state = state_tools.clone_state(session.repository_state)
        command_result = command_engine.process(previous_state, command)
        classification, increment = CommandCountClassifier().classify(
            command=command,
            policy_snapshot=session.command_policy_snapshot,
            processed=command_result.processed,
        )

        result_category = RESULT_UNPROCESSABLE
        feedback = ""
        if command_result.processed:
            executed_commands = [
                *session.step_logs.order_by("id").values_list("command_log__normalized_command", flat=True),
                command_result.normalized_command,
            ]
            evaluation = ScenarioCompletionEvaluator().evaluate(
                CompletionEvaluationContext(
                    session=session,
                    previous_state=previous_state,
                    next_state=command_result.state,
                    executed_commands=executed_commands,
                )
            )
            result_category = evaluation.result_category
            if session.difficulty_instance.difficulty == DIFFICULTY_EASY:
                feedback = FeedbackGenerationService().describe(previous_state, command_result.state)
        else:
            result_category = (
                RESULT_INVALID
                if command.strip().lower().startswith("git")
                else RESULT_UNPROCESSABLE
            )

        if classification == COMMAND_COUNTED:
            session.counted_action_total += increment
        elif classification == COMMAND_DIAGNOSTIC:
            session.non_counted_diagnostic_total += 1
        session.total_attempts += 1
        if result_category != RESULT_TARGET_MATCHED:
            session.first_attempt_star_eligible = False
        session.repository_state = command_result.state

        state_hash = state_tools.state_hash(command_result.state)
        step = StepLog.objects.create(
            session=session,
            command_text=command,
            terminal_output=command_result.output,
            result_category=result_category,
            command_classification=classification,
            counted_increment=increment,
            attempt_number=session.total_attempts,
            counted_total_after=session.counted_action_total,
            state_hash=state_hash,
            expected_state_hash=state_tools.state_hash(session.variant.target_state),
            repository_state=command_result.state,
            contextual_feedback=feedback,
        )
        CommandLog.objects.create(
            step_log=step,
            raw_command=command,
            normalized_command=command_result.normalized_command,
            was_processable=command_result.processed,
        )

        max_count = session.command_policy_snapshot["max_counted_commands"]
        if result_category == RESULT_TARGET_MATCHED:
            self._complete_session(session)
        elif classification == COMMAND_COUNTED and session.counted_action_total >= max_count:
            session.status = SESSION_STATUS_FAILED
            session.ended_at = timezone.now()
            session.failure_reason = "Action limit reached."

        session.save()
        return {
            "session": session,
            "step": step,
            "terminal_output": command_result.output,
            "repository_state": snapshotter.snapshot(session.repository_state),
            "evaluation_result": result_category,
            "command_classification": classification,
            "remaining_counted_commands": max(0, max_count - session.counted_action_total),
            "contextual_feedback": feedback,
            "scaffolding": ScaffoldingService().supports_for(
                session.difficulty_instance.difficulty
            ),
        }

    def _complete_session(self, session: ScenarioSession) -> None:
        session.status = SESSION_STATUS_COMPLETED
        session.completed_at = timezone.now()
        session.ended_at = session.completed_at
        session.rta_success = bool(session.rta_eligible and session.first_attempt_star_eligible)
        if session.mode == SESSION_MODE_PRIMARY:
            completion, created = CompletionRecord.objects.get_or_create(
                user=session.user,
                scenario=session.scenario,
                difficulty_instance=session.difficulty_instance,
                defaults={
                    "session": session,
                    "first_attempt_star": session.first_attempt_star_eligible,
                    "counted_action_total": session.counted_action_total,
                },
            )
            if not created and session.counted_action_total < completion.counted_action_total:
                completion.session = session
                completion.counted_action_total = session.counted_action_total
                completion.save(update_fields=["session", "counted_action_total"])
            StreakService().record_completion(user=session.user, completed_at=session.completed_at)
