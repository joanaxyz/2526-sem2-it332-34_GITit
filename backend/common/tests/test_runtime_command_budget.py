from types import SimpleNamespace

from common.constants import COMMAND_COUNTED, COMMAND_DIAGNOSTIC, COMMAND_UNPROCESSABLE
from common.runtime import (
    apply_command_accounting,
    command_budget_exhausted,
    update_fields_for_execution,
)


def test_apply_command_accounting_for_counted_command():
    run = SimpleNamespace(total_attempts=2, counted_action_total=1)

    result = apply_command_accounting(
        run,
        classification=COMMAND_COUNTED,
        increment=1,
        total_field="total_attempts",
        counted_field="counted_action_total",
    )

    assert run.total_attempts == 3
    assert run.counted_action_total == 2
    assert result.changed_fields == frozenset({"total_attempts", "counted_action_total"})


def test_apply_command_accounting_for_diagnostic_command():
    run = SimpleNamespace(total_attempts=2, counted_action_total=1, non_counted_diagnostic_total=0)

    result = apply_command_accounting(
        run,
        classification=COMMAND_DIAGNOSTIC,
        increment=0,
        total_field="total_attempts",
        counted_field="counted_action_total",
        diagnostic_field="non_counted_diagnostic_total",
    )

    assert run.total_attempts == 3
    assert run.counted_action_total == 1
    assert run.non_counted_diagnostic_total == 1
    assert result.changed_fields == frozenset({"total_attempts", "non_counted_diagnostic_total"})


def test_apply_command_accounting_for_non_counted_command_only_advances_revision():
    run = SimpleNamespace(command_count=4, counted_command_count=2)

    result = apply_command_accounting(
        run,
        classification=COMMAND_UNPROCESSABLE,
        increment=0,
        total_field="command_count",
        counted_field="counted_command_count",
    )

    assert run.command_count == 5
    assert run.counted_command_count == 2
    assert result.changed_fields == frozenset({"command_count"})


def test_budget_exhaustion_requires_unsolved_counted_command():
    assert command_budget_exhausted(
        solved=False,
        classification=COMMAND_COUNTED,
        counted_total=4,
        max_counted_commands=4,
    )
    assert not command_budget_exhausted(
        solved=True,
        classification=COMMAND_COUNTED,
        counted_total=4,
        max_counted_commands=4,
    )
    assert not command_budget_exhausted(
        solved=False,
        classification=COMMAND_UNPROCESSABLE,
        counted_total=4,
        max_counted_commands=4,
    )

def test_update_fields_for_execution_only_adds_repository_state_when_mutated():
    assert update_fields_for_execution({"command_count"}, state_mutated=False) == ["command_count"]
    assert update_fields_for_execution({"command_count"}, state_mutated=True) == ["command_count", "repository_state"]
