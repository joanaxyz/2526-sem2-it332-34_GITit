from types import SimpleNamespace

import common.runtime.command_submission as command_submission
from common.runtime import repository_response_snapshot, update_fields_for_execution


class FakeSnapshotter:
    def snapshot(self, state, *, already_normalized=False):
        return {"kind": "full", "state": state, "already_normalized": already_normalized}

    def snapshot_for_command(self, state, *, already_normalized=False):
        return {"kind": "command", "state": state, "already_normalized": already_normalized}


def test_repository_response_snapshot_uses_full_tree_when_command_changes_project_tree(monkeypatch):
    monkeypatch.setattr(command_submission, "command_response_includes_project_tree", lambda **_: True)

    result = repository_response_snapshot(
        FakeSnapshotter(),
        command_result=SimpleNamespace(),
        previous_state={"before": True},
        next_state={"after": True},
    )

    assert result == {"kind": "full", "state": {"after": True}, "already_normalized": True}


def test_repository_response_snapshot_uses_command_snapshot_for_regular_commands(monkeypatch):
    monkeypatch.setattr(command_submission, "command_response_includes_project_tree", lambda **_: False)

    result = repository_response_snapshot(
        FakeSnapshotter(),
        command_result=SimpleNamespace(),
        previous_state={"before": True},
        next_state={"after": True},
    )

    assert result == {"kind": "command", "state": {"after": True}, "already_normalized": True}


def test_update_fields_for_execution_keeps_save_fields_stable_and_sorted():
    assert update_fields_for_execution({"z_field", "command_count"}, state_mutated=True) == [
        "command_count",
        "repository_state",
        "z_field",
    ]
