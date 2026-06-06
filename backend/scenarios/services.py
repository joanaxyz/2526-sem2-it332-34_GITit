from collections import OrderedDict

from django.db import transaction
from django.db.models import Prefetch
from django.utils import timezone
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
    SESSION_MODE_REVIEW,
    SESSION_STATUS_ABANDONED,
    SESSION_STATUS_COMPLETED,
    SESSION_STATUS_FAILED,
    SESSION_STATUS_STARTED,
)
from common.exceptions import Locked
from common.performance import timing
from evaluation.completion import CompletionEvaluationContext, PracticeCompletionEvaluator
from progress.services import StreakService
from scaffolding.services import FeedbackGenerationService
from scenarios.models import (
    CommandDrill,
    CommandLog,
    CompletionRecord,
    PracticeKind,
    PracticeSession,
    ProblemVariant,
    StepLog,
    WorkflowScenarioLevel,
)
from scenarios.selectors import (
    required_successful_attempts_for_problem,
    session_meets_progress_threshold,
)
from scenarios.visualization import RepositoryVisualizationService
from simulator.command_engine import SimulatedGitCommandEngine
from simulator.services import (
    RepositorySnapshotService,
    RepositoryStateSimulator,
    is_diagnostic_command,
    normalize_command,
)
from simulator.workspace_files import WorkspaceFileError, WorkspaceFileStateService

SESSION_HYDRATE_SELECT_RELATED = (
    "module",
    "command_drill__usage__topic",
    "workflow_scenario",
    "workflow_level__scenario",
    "variant",
    "prior_session",
    "user",
)


class CommandCountClassifier:
    def classify(
        self,
        *,
        command: str,
        processed: bool,
        diagnostic: bool | None = None,
    ) -> tuple[str, int]:
        if not processed:
            normalized = normalize_command(command).lower()
            if normalized == "git" or normalized.startswith("git "):
                return COMMAND_COUNTED, 1
            return COMMAND_UNPROCESSABLE, 0
        is_diagnostic = diagnostic if diagnostic is not None else is_diagnostic_command(command)
        if is_diagnostic:
            return COMMAND_DIAGNOSTIC, 0
        return COMMAND_COUNTED, 1


class CommandHistoryCache:
    _cache: OrderedDict[tuple[int, int], list[str]] = OrderedDict()
    _max_entries = 512

    def history_for(self, *, session: PracticeSession) -> list[str]:
        key = (session.id, session.total_attempts)
        cached = self._cache.get(key)
        if cached is not None:
            self._cache.move_to_end(key)
            return list(cached)

        history = list(
            CommandLog.objects.filter(step_log__session=session)
            .order_by("step_log_id")
            .values_list("normalized_command", flat=True)
        )
        self._remember(key, history)
        return history

    def remember_after_append(
        self,
        *,
        session: PracticeSession,
        previous_history: list[str],
        normalized_command: str,
    ) -> None:
        self._remember(
            (session.id, session.total_attempts),
            [*previous_history, normalized_command],
        )

    def _remember(self, key: tuple[int, int], history: list[str]) -> None:
        self._cache[key] = list(history)
        self._cache.move_to_end(key)
        while len(self._cache) > self._max_entries:
            self._cache.popitem(last=False)


class VariantTargetStateHashCache:
    _cache: OrderedDict[tuple[int, str], str] = OrderedDict()
    _max_entries = 512

    def hash_for(self, *, variant: ProblemVariant, state_tools: RepositoryStateSimulator) -> str:
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


class VariantSelectionService:
    def select_variant(
        self,
        *,
        user,
        problem,
        prior_session: PracticeSession | None = None,
        published_variants: list[ProblemVariant] | None = None,
        tried_variant_keys: set[str] | None = None,
    ) -> ProblemVariant:
        variants = published_variants or list(problem.variants.filter(is_published=True).order_by("semantic_key", "id"))
        if not variants:
            raise Locked("This practice item has no published variants.")
        if prior_session is None:
            return variants[0]

        prior_key = self.variant_identity(prior_session.variant)
        tried_keys = tried_variant_keys if tried_variant_keys is not None else self._tried_variant_keys(user=user, problem=problem)
        for variant in variants:
            identity = self.variant_identity(variant)
            if identity != prior_key and identity not in tried_keys:
                return variant
        for variant in variants:
            if self.variant_identity(variant) != prior_key:
                return variant
        return variants[0]

    def changed_between(self, *, prior: ProblemVariant, current: ProblemVariant) -> bool:
        return self.variant_identity(prior) != self.variant_identity(current)

    def is_loopback_from_keys(
        self,
        *,
        variants: list[ProblemVariant],
        selected_variant: ProblemVariant,
        tried_keys: set[str],
    ) -> bool:
        if len(variants) <= 1:
            return False
        available = {self.variant_identity(variant) for variant in variants}
        return (
            len(tried_keys.intersection(available)) >= len(available)
            and self.variant_identity(selected_variant) in tried_keys
        )

    def variant_identity(self, variant: ProblemVariant) -> str:
        if variant.semantic_key:
            return variant.semantic_key
        if variant.case_id:
            return f"case:{variant.case_id}"
        case_id = (variant.parameter_context or {}).get("case_id")
        if case_id:
            return f"case:{case_id}"
        if variant.structure_signature:
            return f"structure:{variant.structure_signature}"
        return f"id:{variant.id}"

    def _tried_variant_keys(self, *, user, problem) -> set[str]:
        filters = {"user": user}
        if isinstance(problem, CommandDrill):
            filters["command_drill"] = problem
        else:
            filters["workflow_level"] = problem
        variant_ids = (
            PracticeSession.objects.filter(**filters)
            .exclude(variant_id__isnull=True)
            .values_list("variant_id", flat=True)
            .distinct()
        )
        return {
            self.variant_identity(variant)
            for variant in ProblemVariant.objects.filter(id__in=variant_ids)
        }


class PracticeSessionService:
    @staticmethod
    def hydrate_session(session: PracticeSession | int, *, user=None) -> PracticeSession:
        queryset = PracticeSession.objects.select_related(*SESSION_HYDRATE_SELECT_RELATED).prefetch_related(
            Prefetch("step_logs", queryset=StepLog.objects.order_by("id")),
        )
        if isinstance(session, int):
            queryset = queryset.filter(pk=session)
        else:
            queryset = queryset.filter(pk=session.pk)
        if user is not None:
            queryset = queryset.filter(user=user)
        return queryset.get()

    @transaction.atomic
    def start_session(
        self,
        *,
        user,
        problem,
        source_entry_point: str,
        prior_session: PracticeSession | None = None,
        mode: str = SESSION_MODE_PRIMARY,
    ) -> PracticeSession:
        practice_kind = (
            PracticeKind.COMMAND_DRILL if isinstance(problem, CommandDrill) else PracticeKind.WORKFLOW_SCENARIO
        )
        if prior_session and prior_session.problem != problem:
            raise Locked("Retry sessions must use the same practice item.")
        if prior_session and prior_session.status == SESSION_STATUS_STARTED:
            raise Locked("Exit the current practice session before retrying.")
        if mode == SESSION_MODE_PRIMARY and practice_kind == PracticeKind.WORKFLOW_SCENARIO:
            self._ensure_workflow_unlocked(user=user, level=problem)
        if mode == SESSION_MODE_PRIMARY:
            active = self._active_session(user=user, problem=problem)
            if active and (not prior_session or active.id != prior_session.id):
                raise Locked("Exit the current practice session before starting again.")

        selector = VariantSelectionService()
        published_variants = list(problem.variants.filter(is_published=True).order_by("semantic_key", "id"))
        tried_keys = selector._tried_variant_keys(user=user, problem=problem) if prior_session else set()
        variant = (
            self._review_variant(user=user, problem=problem)
            if mode == SESSION_MODE_REVIEW
            else selector.select_variant(
                user=user,
                problem=problem,
                prior_session=prior_session,
                published_variants=published_variants,
                tried_variant_keys=tried_keys,
            )
        )
        changed_variant = bool(prior_session and selector.changed_between(prior=prior_session.variant, current=variant))
        looped_variant = bool(
            prior_session
            and selector.is_loopback_from_keys(
                variants=published_variants,
                selected_variant=variant,
                tried_keys=tried_keys,
            )
        )
        retry_index = prior_session.retry_index + 1 if prior_session else 0
        rta_eligible = bool(
            mode == SESSION_MODE_PRIMARY
            and prior_session
            and prior_session.status in (SESSION_STATUS_FAILED, SESSION_STATUS_ABANDONED)
            and changed_variant
        )
        session = PracticeSession.objects.create(
            user=user,
            module=problem.module,
            practice_kind=practice_kind,
            command_drill=problem if practice_kind == PracticeKind.COMMAND_DRILL else None,
            workflow_scenario=problem.scenario if practice_kind == PracticeKind.WORKFLOW_SCENARIO else None,
            workflow_level=problem if practice_kind == PracticeKind.WORKFLOW_SCENARIO else None,
            variant=variant,
            prior_session=prior_session,
            source_entry_point=source_entry_point,
            mode=mode,
            difficulty=problem.difficulty if practice_kind == PracticeKind.WORKFLOW_SCENARIO else "",
            rta_eligible=rta_eligible,
            changed_variant=changed_variant,
            looped_variant=looped_variant,
            retry_index=retry_index,
            command_budget_snapshot={
                "min_counted_commands": problem.min_counted_commands,
                "max_counted_commands": problem.max_counted_commands,
            },
            repository_state=variant.initial_state,
        )
        return self.hydrate_session(session)

    def _active_session(self, *, user, problem):
        filters = {
            "user": user,
            "status": SESSION_STATUS_STARTED,
            "mode": SESSION_MODE_PRIMARY,
        }
        if isinstance(problem, CommandDrill):
            filters["command_drill"] = problem
        else:
            filters["workflow_level"] = problem
        return PracticeSession.objects.filter(**filters).first()

    def _ensure_workflow_unlocked(self, *, user, level: WorkflowScenarioLevel) -> None:
        if level.difficulty == DIFFICULTY_EASY:
            return
        previous = DIFFICULTY_EASY if level.difficulty == "medium" else "medium"
        previous_level = WorkflowScenarioLevel.objects.filter(
            scenario=level.scenario,
            difficulty=previous,
            is_published=True,
        ).first()
        if not previous_level or not CompletionRecord.objects.filter(user=user, workflow_level=previous_level).exists():
            raise Locked("This workflow level is locked until the previous level is completed.")

    def _review_variant(self, *, user, problem):
        filters = {"user": user}
        if isinstance(problem, CommandDrill):
            filters["command_drill"] = problem
        else:
            filters["workflow_level"] = problem
        completion = CompletionRecord.objects.select_related("session__variant").filter(**filters).first()
        if not completion:
            raise Locked("Review Mode is available only after completing this practice item.")
        return completion.session.variant

    @transaction.atomic
    def abandon(self, *, session: PracticeSession) -> PracticeSession:
        if session.status != SESSION_STATUS_STARTED:
            return session
        session.status = SESSION_STATUS_ABANDONED
        session.ended_at = timezone.now()
        session.failure_reason = "Student left the session before completion."
        session.save(update_fields=["status", "ended_at", "failure_reason"])
        return session


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
        self.command_engine = SimulatedGitCommandEngine()

    @transaction.atomic
    def submit_command(self, *, session: PracticeSession, command: str) -> dict:
        if session.status != SESSION_STATUS_STARTED:
            raise Locked("This session has already ended.")

        state_tools = self.state_tools
        with timing("practice.command.repository_state_clone", session_id=session.id):
            previous_state = state_tools.clone_state(session.repository_state)
            working_state = state_tools.normalize_state(previous_state)
        with timing("practice.command.parse_execute", session_id=session.id):
            command_result = self.command_engine.process(working_state, command, mutate_in_place=True)
        with timing("practice.command.repository_state_normalize", session_id=session.id):
            next_state = state_tools.normalize_state(command_result.state)

        classification, increment = CommandCountClassifier().classify(
            command=command,
            processed=command_result.processed,
            diagnostic=command_result.diagnostic,
        )
        result_category = RESULT_UNPROCESSABLE
        feedback = ""
        executed_commands: list[str] = []
        state_hash = ""
        expected_state_hash = ""
        if command_result.processed:
            state_hash = state_tools.state_hash_for_normalized(next_state)
            expected_state_hash = VariantTargetStateHashCache().hash_for(
                variant=session.variant,
                state_tools=state_tools,
            )
            previous_history = CommandHistoryCache().history_for(session=session)
            executed_commands = [*previous_history, command_result.normalized_command]
            evaluation = PracticeCompletionEvaluator().evaluate(
                CompletionEvaluationContext(
                    session=session,
                    previous_state=previous_state,
                    next_state=next_state,
                    executed_commands=executed_commands,
                    next_state_hash=state_hash,
                    expected_state_hash=expected_state_hash,
                )
            )
            result_category = evaluation.result_category
            if _uses_contextual_feedback(session) and classification == COMMAND_COUNTED:
                feedback = FeedbackGenerationService().describe(previous_state, next_state)
        else:
            result_category = RESULT_INVALID if command.strip().lower().startswith("git") else RESULT_UNPROCESSABLE
            state_hash = state_tools.state_hash_for_normalized(next_state)
            expected_state_hash = VariantTargetStateHashCache().hash_for(
                variant=session.variant,
                state_tools=state_tools,
            )

        if classification == COMMAND_COUNTED:
            session.counted_action_total += increment
        elif classification == COMMAND_DIAGNOSTIC:
            session.non_counted_diagnostic_total += 1
        session.total_attempts += 1
        if result_category != RESULT_TARGET_MATCHED:
            session.first_attempt_star_eligible = False
        session.repository_state = next_state

        visualization_snapshot = self.visualizer.snapshot(
            next_state,
            previous_state=previous_state,
            target_state=_visible_target_state(session),
        )
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
            expected_state_hash=expected_state_hash,
            contextual_feedback=feedback,
            visualization_snapshot=visualization_snapshot,
        )
        CommandLog.objects.create(
            step_log=step,
            raw_command=command,
            normalized_command=command_result.normalized_command,
            was_processable=command_result.processed,
        )
        if command_result.processed:
            CommandHistoryCache().remember_after_append(
                session=session,
                previous_history=executed_commands[:-1],
                normalized_command=command_result.normalized_command,
            )

        max_count = session.command_budget_snapshot["max_counted_commands"]
        update_fields = {"repository_state", "total_attempts", "first_attempt_star_eligible"}
        if classification == COMMAND_COUNTED:
            update_fields.add("counted_action_total")
        elif classification == COMMAND_DIAGNOSTIC:
            update_fields.add("non_counted_diagnostic_total")
        if result_category == RESULT_TARGET_MATCHED:
            update_fields.update(self._complete_session(session))
        elif classification == COMMAND_COUNTED and session.counted_action_total >= max_count:
            target_matched = False
            if command_result.processed:
                recheck = PracticeCompletionEvaluator().evaluate(
                    CompletionEvaluationContext(
                        session=session,
                        previous_state=previous_state,
                        next_state=next_state,
                        executed_commands=executed_commands,
                        next_state_hash=state_hash,
                        expected_state_hash=expected_state_hash,
                    )
                )
                target_matched = recheck.target_matched
            if target_matched:
                result_category = RESULT_TARGET_MATCHED
                update_fields.update(self._complete_session(session))
            else:
                session.status = SESSION_STATUS_FAILED
                session.ended_at = timezone.now()
                session.failure_reason = "Action limit reached before the target repository state was reached."
                update_fields.update({"status", "ended_at", "failure_reason"})

        session.save(update_fields=sorted(update_fields))
        if _command_response_includes_project_tree(
            command_result=command_result,
            previous_state=previous_state,
            next_state=next_state,
        ):
            repository_snapshot = self.snapshotter.snapshot(next_state, already_normalized=True)
        else:
            repository_snapshot = self.snapshotter.snapshot_for_command(next_state, already_normalized=True)
        return {
            "session": session,
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

    def _complete_session(self, session: PracticeSession) -> set[str]:
        session.status = SESSION_STATUS_COMPLETED
        session.completed_at = timezone.now()
        session.ended_at = session.completed_at
        session.rta_success = bool(session.rta_eligible and session.first_attempt_star_eligible)
        if session.mode == SESSION_MODE_PRIMARY:
            required = required_successful_attempts_for_problem(session.problem)
            previous_progress = 0
            filters = {
                "user": session.user,
                "mode": SESSION_MODE_PRIMARY,
                "status": SESSION_STATUS_COMPLETED,
            }
            if session.practice_kind == PracticeKind.COMMAND_DRILL:
                filters["command_drill"] = session.command_drill
            else:
                filters["workflow_level"] = session.workflow_level
            for prior_session in PracticeSession.objects.filter(**filters).exclude(pk=session.pk):
                if session_meets_progress_threshold(session=prior_session):
                    previous_progress += 1
            current_meets_progress = session_meets_progress_threshold(session=session)
            if previous_progress + (1 if current_meets_progress else 0) >= required:
                completion_filter = {
                    "user": session.user,
                    "practice_kind": session.practice_kind,
                    "command_drill": session.command_drill,
                    "workflow_level": session.workflow_level,
                }
                completion, created = CompletionRecord.objects.get_or_create(
                    **completion_filter,
                    defaults={
                        "session": session,
                        "first_attempt_star": session.first_attempt_star_eligible,
                        "counted_action_total": session.counted_action_total,
                    },
                )
                if not created:
                    completion.session = session
                    completion.first_attempt_star = session.first_attempt_star_eligible
                    completion.counted_action_total = session.counted_action_total
                    completion.completed_at = session.completed_at
                    completion.save(update_fields=["session", "first_attempt_star", "counted_action_total", "completed_at"])
                StreakService().record_completion(user=session.user, completed_at=session.completed_at)
        return {"status", "completed_at", "ended_at", "rta_success"}


def _uses_contextual_feedback(session: PracticeSession) -> bool:
    return (
        session.practice_kind == PracticeKind.COMMAND_DRILL
        or session.difficulty == DIFFICULTY_EASY
    )


def _visible_target_state(session: PracticeSession) -> dict | None:
    if session.practice_kind == PracticeKind.COMMAND_DRILL:
        return session.variant.target_state
    if session.difficulty in (DIFFICULTY_EASY, DIFFICULTY_MEDIUM):
        return session.variant.target_state
    return None


class WorkspaceFileCreationService:
    @transaction.atomic
    def create_file(self, *, session: PracticeSession, path: str, content: str = "") -> PracticeSession:
        if session.status != SESSION_STATUS_STARTED:
            raise Locked("This session has already ended.")
        try:
            next_state = WorkspaceFileStateService().create_file(
                session.repository_state,
                path=path,
                content=content,
            )
        except WorkspaceFileError as exc:
            raise ValidationError({"path": [str(exc)]}) from exc
        session.repository_state = next_state
        session.save(update_fields=["repository_state"])
        return session

    @transaction.atomic
    def write_file(self, *, session: PracticeSession, path: str, content: str = "") -> PracticeSession:
        if session.status != SESSION_STATUS_STARTED:
            raise Locked("This session has already ended.")
        try:
            next_state = WorkspaceFileStateService().write_file(
                session.repository_state,
                path=path,
                content=content,
            )
        except WorkspaceFileError as exc:
            raise ValidationError({"path": [str(exc)]}) from exc
        session.repository_state = next_state
        session.save(update_fields=["repository_state"])
        return session
