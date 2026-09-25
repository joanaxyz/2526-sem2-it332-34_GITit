from types import SimpleNamespace

from evaluation.completion import CompletionEvaluationContext, PracticeCompletionEvaluator
from evaluation.services.state_requirements import STATE_RULE_HANDLER_REGISTRY

STATE = {
    "repository_initialized": True,
    "commits": [{"id": "c0", "message": "Base", "parents": [], "tree": {"a.txt": "a"}}],
    "branches": {"main": "c0"},
    "head": {"type": "branch", "name": "main"},
    "staging": {},
    "working_tree": {},
    "conflicts": [],
}


def _passes(state):
    variant = SimpleNamespace(
        id=None,
        semantic_key="",
        initial_state=STATE,
        target_state={},
        evaluation_spec={
            "state_requirements": {"rules": [{"type": "rebase_not_in_progress"}]},
            "process_requirements": {"required_commands": [], "forbidden_commands": []},
            "completion_policy": {"mode": "rules"},
        },
    )
    outcome = PracticeCompletionEvaluator().evaluate(
        CompletionEvaluationContext(variant=variant, next_state=state, executed_commands=[])
    )
    return outcome.target_matched


def test_rule_is_registered():
    assert "rebase_not_in_progress" in STATE_RULE_HANDLER_REGISTRY


def test_passes_without_a_rebase_and_fails_while_one_is_stopped():
    stopped = {**STATE, "rebase_state": {"remaining": ["c2"], "abort_state": {"head": "c0"}}}

    assert _passes(STATE) is True
    assert _passes({**STATE, "rebase_state": {}}) is True
    assert _passes(stopped) is False
