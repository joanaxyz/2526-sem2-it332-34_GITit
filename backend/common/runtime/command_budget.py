"""Shared runtime command-accounting helpers.

Challenge and Adventure runs use different model fields, but they both apply the
same runtime rule: every submitted command advances the client revision, counted
commands consume budget, and budget exhaustion only fails an unsolved run.
"""

from dataclasses import dataclass

from common.constants import COMMAND_COUNTED, COMMAND_DIAGNOSTIC


@dataclass(frozen=True)
class CommandAccountingResult:
    total: int
    counted_total: int
    changed_fields: frozenset[str]


def apply_command_accounting(
    owner: object,
    *,
    classification: str,
    increment: int,
    total_field: str,
    counted_field: str,
    diagnostic_field: str | None = None,
) -> CommandAccountingResult:
    """Apply command-count changes to a run-like object.

    The caller owns persistence. This helper only mutates fields and returns the
    field names that need to be included in `save(update_fields=...)`.
    """

    total = int(getattr(owner, total_field, 0)) + 1
    setattr(owner, total_field, total)
    changed_fields = {total_field}

    counted_total = int(getattr(owner, counted_field, 0))
    if classification == COMMAND_COUNTED:
        counted_total += increment
        setattr(owner, counted_field, counted_total)
        changed_fields.add(counted_field)
    elif classification == COMMAND_DIAGNOSTIC and diagnostic_field:
        setattr(owner, diagnostic_field, int(getattr(owner, diagnostic_field, 0)) + 1)
        changed_fields.add(diagnostic_field)

    return CommandAccountingResult(
        total=total,
        counted_total=counted_total,
        changed_fields=frozenset(changed_fields),
    )


def command_budget_exhausted(
    *,
    solved: bool,
    classification: str,
    counted_total: int,
    max_counted_commands: int,
) -> bool:
    return (
        not solved
        and classification == COMMAND_COUNTED
        and counted_total >= max_counted_commands
    )
