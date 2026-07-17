from __future__ import annotations

from .rule_builders import command_matches

SUPPORTED_RULE_TYPES = frozenset({
    'forbidden_command',
    'repository_initialized',
    'required_command',
    'required_command_sequence',
})


def _required_sequence_was_executed(
    executed_commands: list[str],
    required_commands: list[str],
) -> bool:
    """Match one authored command per step, in order, while allowing extras.

    A single broad command such as ``git status --porcelain`` must not satisfy
    both an early status check and a later plain ``git status`` confirmation.
    Advancing the cursor at most once per executed command preserves that
    multiplicity while still allowing learners to run additional diagnostics.
    """

    required_index = 0
    for executed in executed_commands:
        if required_index >= len(required_commands):
            break
        if command_matches(executed, required_commands[required_index]):
            required_index += 1
    return required_index == len(required_commands)


def check_command_state_rule(
    self,
    state: dict,
    rule: dict,
    *,
    initial_state: dict | None,
    executed_commands: list[str],
) -> tuple[bool, str] | None:
    rule_type = rule.get("type")
    if rule_type == "required_command":
        required = rule.get("command", "")
        passed = any(command_matches(executed, required) for executed in executed_commands)
        return (
            passed,
            "Required command was executed."
            if passed
            else f"Required command {required!r} was not executed.",
        )
    if rule_type == "required_command_sequence":
        required = [str(command) for command in (rule.get("commands") or [])]
        passed = bool(required) and _required_sequence_was_executed(
            executed_commands,
            required,
        )
        return (
            passed,
            "Required command sequence was executed in order."
            if passed
            else "Required command sequence has not been completed in order.",
        )
    if rule_type == "forbidden_command":
        forbidden = rule.get("command", "")
        passed = not any(command_matches(executed, forbidden) for executed in executed_commands)
        return (
            passed,
            "Forbidden command was not used."
            if passed
            else f"Forbidden command {forbidden!r} was used.",
        )
    if rule_type == "repository_initialized":
        expected = bool(rule.get("value", True))
        passed = bool(state.get("repository_initialized", True)) == expected
        return (
            passed,
            f"repository_initialized is {state.get('repository_initialized', True)!r}.",
        )
    return None
