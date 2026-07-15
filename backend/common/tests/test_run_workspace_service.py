from types import SimpleNamespace
from unittest.mock import Mock, patch

import pytest

from common.exceptions import Locked
from common.services.run_workspace import mutate_run_workspace_file


class _Manager:
    def __init__(self, run):
        self.run = run

    def select_for_update(self, **_kwargs):
        return self

    def get(self, **_kwargs):
        return self.run


@pytest.mark.django_db(transaction=True)
def test_mutate_run_workspace_file_uses_persisted_locked_state():
    locked = SimpleNamespace(pk=1, status="started", repository_state={"working_tree": {}}, save=Mock())
    model = type("Run", (), {"objects": _Manager(locked)})
    incoming = model()
    incoming.pk = 1

    with patch("common.services.run_workspace.create_workspace_file", return_value={"changed": True}) as mutate:
        result = mutate_run_workspace_file(
            run=incoming,
            operation="create",
            path="README.md",
            content="hello",
            ended_message="ended",
        )

    mutate.assert_called_once_with({"working_tree": {}}, path="README.md", content="hello")
    locked.save.assert_called_once_with(update_fields=["repository_state"])
    assert result is locked


@pytest.mark.django_db(transaction=True)
def test_mutate_run_workspace_file_routes_rename_operation():
    locked = SimpleNamespace(pk=1, status="started", repository_state={"working_tree": {}}, save=Mock())
    model = type("Run", (), {"objects": _Manager(locked)})
    incoming = model()
    incoming.pk = 1

    with patch("common.services.run_workspace.rename_workspace_file", return_value={"renamed": True}) as mutate:
        result = mutate_run_workspace_file(
            run=incoming,
            operation="rename",
            path="old.md",
            new_path="new.md",
            ended_message="ended",
        )

    mutate.assert_called_once_with({"working_tree": {}}, path="old.md", new_path="new.md")
    locked.save.assert_called_once_with(update_fields=["repository_state"])
    assert result is locked


@pytest.mark.django_db(transaction=True)
def test_mutate_run_workspace_file_rejects_ended_run():
    locked = SimpleNamespace(pk=1, status="completed", repository_state={}, save=Mock())
    model = type("Run", (), {"objects": _Manager(locked)})
    incoming = model()
    incoming.pk = 1

    with pytest.raises(Locked, match="ended"):
        mutate_run_workspace_file(
            run=incoming,
            operation="write",
            path="README.md",
            content="hello",
            ended_message="ended",
        )
