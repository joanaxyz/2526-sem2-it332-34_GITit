from evaluation.services.state_requirements import _HANDLER_GROUPS, STATE_RULE_HANDLER_REGISTRY


def test_state_rule_registry_has_one_handler_per_declared_rule_type():
    declared = [rule_type for rule_types, _handler in _HANDLER_GROUPS for rule_type in rule_types]
    assert len(declared) == len(set(declared))
    assert set(declared) == set(STATE_RULE_HANDLER_REGISTRY)


def test_unknown_state_rule_type_is_not_registered():
    assert "not-a-real-rule" not in STATE_RULE_HANDLER_REGISTRY
