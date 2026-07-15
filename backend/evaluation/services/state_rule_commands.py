from __future__ import annotations

from .rule_builders import command_matches

SUPPORTED_RULE_TYPES = frozenset({
    'forbidden_command',
    'repository_initialized',
    'required_command',
})

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
