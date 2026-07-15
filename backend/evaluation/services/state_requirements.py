from __future__ import annotations

from collections.abc import Callable, Mapping
from types import MappingProxyType

from .state_rule_commands import SUPPORTED_RULE_TYPES as COMMAND_RULE_TYPES
from .state_rule_commands import check_command_state_rule
from .state_rule_commit_tree import SUPPORTED_RULE_TYPES as COMMIT_TREE_RULE_TYPES
from .state_rule_commit_tree import check_commit_tree_state_rule
from .state_rule_commits import SUPPORTED_RULE_TYPES as COMMIT_RULE_TYPES
from .state_rule_commits import check_commit_state_rule
from .state_rule_refs import SUPPORTED_RULE_TYPES as REF_RULE_TYPES
from .state_rule_refs import check_ref_state_rule
from .state_rule_remotes_history import SUPPORTED_RULE_TYPES as REMOTE_HISTORY_RULE_TYPES
from .state_rule_remotes_history import check_remote_history_state_rule
from .state_rule_workspace import SUPPORTED_RULE_TYPES as WORKSPACE_RULE_TYPES
from .state_rule_workspace import check_workspace_state_rule

StateRuleHandler = Callable[..., tuple[bool, str] | None]

_HANDLER_GROUPS: tuple[tuple[frozenset[str], StateRuleHandler], ...] = (
    (COMMAND_RULE_TYPES, check_command_state_rule),
    (REF_RULE_TYPES, check_ref_state_rule),
    (COMMIT_RULE_TYPES, check_commit_state_rule),
    (WORKSPACE_RULE_TYPES, check_workspace_state_rule),
    (REMOTE_HISTORY_RULE_TYPES, check_remote_history_state_rule),
    (COMMIT_TREE_RULE_TYPES, check_commit_tree_state_rule),
)


def _build_rule_handler_registry() -> dict[str, StateRuleHandler]:
    registry: dict[str, StateRuleHandler] = {}
    for rule_types, handler in _HANDLER_GROUPS:
        duplicates = rule_types.intersection(registry)
        if duplicates:
            raise RuntimeError(f"Duplicate evaluation rule handlers: {sorted(duplicates)}")
        registry.update(dict.fromkeys(rule_types, handler))
    return registry


STATE_RULE_HANDLER_REGISTRY: Mapping[str, StateRuleHandler] = MappingProxyType(
    _build_rule_handler_registry()
)


class StateRequirementRuleMixin:
    """Dispatch authored evaluation rules through an explicit handler registry."""

    def _check_rule(
        self,
        state: dict,
        rule: dict,
        *,
        initial_state: dict | None,
        executed_commands: list[str],
    ) -> tuple[bool, str]:
        rule_type = str(rule.get("type") or "")
        handler = STATE_RULE_HANDLER_REGISTRY.get(rule_type)
        if handler is None:
            return False, f"Unsupported rule type: {rule.get('type')!r}."
        result = handler(
            self,
            state,
            rule,
            initial_state=initial_state,
            executed_commands=executed_commands,
        )
        if result is None:
            raise RuntimeError(
                f"Registered evaluation handler {handler.__name__} did not handle {rule_type!r}."
            )
        return result
