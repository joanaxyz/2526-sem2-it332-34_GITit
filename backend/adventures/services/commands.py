"""Adventure run orchestration.

An adventure run is one playable `AdventureLevel`, walked as an ordered sequence
of `AdventureWave` problems. Each wave selects its own variant; the run completes
only when the last wave is cleared. Chapters order adventure levels for
unlocks and mastery targets, but the runtime never walks a whole chapter as
one continuous session.
"""


from django.db import transaction

from adventures.models import (
    AdventureRun,
)
from common.constants import (
    COMMAND_COUNTED,
    SESSION_STATUS_COMPLETED,
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
    update_fields_for_execution,
)
from common.services.performance import timing
from evaluation.compiler import CompiledEvaluationSpecCache
from evaluation.engine import EvaluationEngine
from practice.models import CommandStep
from simulator.services import RepositorySnapshotService, RepositoryStateSimulator

from .history import AdventureCommandHistoryCache
from .runs import AdventureRunService


class AdventureCommandService:
    def __init__(self) -> None:
        self.sim = RepositoryStateSimulator()
        self.snapshotter = RepositorySnapshotService()
        self.executor = ClientCommandExecutionService()
        self.runs = AdventureRunService()

    @transaction.atomic(savepoint=False)
    def submit(self, *, attempt: AdventureRun, command: str, execution: dict) -> dict:
        if attempt.status != SESSION_STATUS_STARTED:
            raise Locked("This attempt has already ended.")
        run_id = attempt.id

        def span(stage: str):
            return timing(f"adventure.command.{stage}", run_id=run_id)

        variant = attempt.selected_variant
        wave = attempt.current_wave
        execution = self.executor.from_payload(
            repository_state=attempt.repository_state,
            command=command,
            execution=execution,
            timing_label="adventure.command",
            run_id=run_id,
            expected_client_revision=attempt.command_count,
        )
        previous_state = execution.previous_state
        result = execution.result
        next_state = execution.next_state
        classification, increment = execution.classification, execution.increment
        accounting = apply_command_accounting(
            attempt,
            classification=classification,
            increment=increment,
            total_field="command_count",
            counted_field="counted_command_count",
        )
        attempt.repository_state = next_state

        solved = False
        previous_rules_passing = 0
        rules_passing = 0
        total_rules = max(1, wave.max_counted_commands if wave is not None else 1)
        executed: list[str] = []
        if result.processed:
            with span("evaluate"):
                history = AdventureCommandHistoryCache().history_for(
                    attempt=attempt,
                    log_count=attempt.command_count - 1,
                )
                previous_outcome = EvaluationEngine().evaluate(
                    spec=CompiledEvaluationSpecCache().spec_for(
                        key=("adventure-wave-variant", variant.id, variant.semantic_key or ""),
                        raw_spec=variant.evaluation_spec,
                    ),
                    next_state=previous_state,
                    initial_state=variant.initial_state,
                    executed_commands=history,
                    next_state_hash=self.sim.state_hash_for_normalized(previous_state),
                    expected_state_hash=VariantTargetStateHashCache().hash_for(
                        variant=variant,
                        state_tools=self.sim,
                    ),
                    next_state_already_normalized=True,
                )
                previous_rules_passing = len(previous_outcome.passed_rules)
                total_rules = max(1, previous_rules_passing + len(previous_outcome.failed_rules))
                executed = [*history, result.normalized_command]
                outcome = EvaluationEngine().evaluate(
                    spec=CompiledEvaluationSpecCache().spec_for(
                        key=("adventure-wave-variant", variant.id, variant.semantic_key or ""),
                        raw_spec=variant.evaluation_spec,
                    ),
                    next_state=next_state,
                    initial_state=variant.initial_state,
                    executed_commands=executed,
                    next_state_hash=self.sim.state_hash_for_normalized(next_state),
                    expected_state_hash=VariantTargetStateHashCache().hash_for(
                        variant=variant,
                        state_tools=self.sim,
                    ),
                    next_state_already_normalized=True,
                )
                solved = outcome.target_matched
                rules_passing = len(outcome.passed_rules)
                total_rules = max(1, rules_passing + len(outcome.failed_rules))

        failed = command_budget_exhausted(
            solved=solved,
            classification=classification,
            counted_total=attempt.counted_command_count,
            max_counted_commands=wave.max_counted_commands if wave is not None else 0,
        )

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
                normalized_command=result.normalized_command,
                was_processable=result.processed,
            )
        if result.processed:
            AdventureCommandHistoryCache().remember(
                attempt=attempt,
                log_count=attempt.command_count,
                history=executed,
            )

        update_fields = update_fields_for_execution(
            accounting.changed_fields,
            state_mutated=execution.state_mutated,
        )
        with span("attempt_save"):
            attempt.save(update_fields=update_fields)

        run_transitioned = False
        if solved or failed:
            outcome = self.runs.record_wave_outcome(
                attempt=attempt,
                solved=solved,
                defeated=failed,
                counted_command_count=attempt.counted_command_count,
                command_count=attempt.command_count,
            )
            run_transitioned = bool(outcome["advanced"] or outcome["completed"])
            repository_snapshot = None
        else:
            with span("response_snapshot"):
                repository_snapshot = repository_response_snapshot(
                    self.snapshotter,
                    command_result=result,
                    previous_state=previous_state,
                    next_state=next_state,
                )

        # The level is only "solved" once the run itself completes; an
        # intermediate wave clear keeps the run running with a fresh problem.
        level_solved = solved and not failed and attempt.status == SESSION_STATUS_COMPLETED

        return {
            "attempt": attempt,
            "step": step,
            "solved": level_solved,
            "wave_advanced": run_transitioned and attempt.status == SESSION_STATUS_STARTED,
            "run_transitioned": run_transitioned,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "exit_code": result.exit_code,
            "terminal_output": result.output,
            "command_classification": classification,
            "repository_state": repository_snapshot,
            "executed_commands": executed if result.processed else None,
            "command_outcome": command_outcome_payload(
                processed=result.processed,
                counted=classification == COMMAND_COUNTED,
                solved=solved,
                failed=failed,
                command_family=result.command_family or "default",
                previous_rules_passing=previous_rules_passing,
                rules_passing=rules_passing,
                total_rules=total_rules,
                max_counted_commands=wave.max_counted_commands if wave is not None else 0,
                counted_command_count=attempt.counted_command_count,
            ),
        }
