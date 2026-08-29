"""Shared command-submission response helpers.

These helpers are intentionally kept outside feature services so challenges,
adventures, and future command-based modes can return the same neutral outcome
payload without importing each other.
"""

from common.schemas.schema_validation import validate_command_outcome_payload


def command_outcome_payload(
    *,
    processed: bool,
    counted: bool,
    solved: bool,
    failed: bool,
    command_family: str,
    previous_rules_passing: int,
    rules_passing: int,
    total_rules: int,
    max_counted_commands: int,
    counted_command_count: int,
) -> dict:
    previous_rules_passing = max(0, int(previous_rules_passing or 0))
    rules_passing = max(0, int(rules_passing or 0))
    total_rules = max(1, int(total_rules or 1))
    max_counted_commands = max(0, int(max_counted_commands or 0))
    counted_command_count = max(0, int(counted_command_count or 0))
    remaining = max(0, max_counted_commands - counted_command_count)

    payload = {
        "processed": bool(processed),
        "counted": bool(counted),
        "solved": bool(solved),
        "failed": bool(failed),
        "command_family": command_family or "default",
        "previous_rules_passing": previous_rules_passing,
        "rules_passing": rules_passing,
        "rules_delta": rules_passing - previous_rules_passing,
        "total_rules": total_rules,
        "max_counted_commands": max_counted_commands,
        "counted_command_count": counted_command_count,
        "remaining_counted_commands": remaining,
    }
    validate_command_outcome_payload(payload)
    return payload
