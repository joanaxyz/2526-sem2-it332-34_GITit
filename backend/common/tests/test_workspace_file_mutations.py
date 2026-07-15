import pytest

from common.exceptions import BadRequest
from common.git.workspace_files import (
    create_workspace_file,
    delete_workspace_file,
    rename_workspace_file,
    write_workspace_file,
)


def base_state():
    return {
        "commits": [
            {
                "id": "c0",
                "message": "initial",
                "parents": [],
                "tree": {"README.md": "hello", "src/app.py": "print('hi')"},
            }
        ],
        "branches": {"main": "c0"},
        "head": {"type": "branch", "name": "main"},
        "working_tree": {},
        "staging": {},
    }


def test_create_workspace_file_mutates_only_requested_file_from_persisted_state():
    forged_client_state = {**base_state(), "branches": {"main": "forged"}}

    next_state = create_workspace_file(base_state(), path="notes/todo.md", content="draft")

    assert next_state["branches"] == {"main": "c0"}
    assert next_state["working_tree"]["notes/todo.md"] == {
        "status": "untracked",
        "content": "draft",
    }
    assert "forged" not in str(next_state)
    assert forged_client_state["branches"] == {"main": "forged"}


def test_write_workspace_file_uses_tracked_status_for_committed_files():
    next_state = write_workspace_file(base_state(), path="README.md", content="changed")

    assert next_state["working_tree"]["README.md"] == {
        "status": "modified",
        "content": "changed",
    }


def test_delete_workspace_file_marks_tracked_files_deleted_and_removes_untracked_files():
    state = create_workspace_file(base_state(), path="notes/todo.md", content="draft")

    next_state = delete_workspace_file(state, path="notes/todo.md")
    next_state = delete_workspace_file(next_state, path="README.md")

    assert "notes/todo.md" not in next_state["working_tree"]
    assert next_state["working_tree"]["README.md"] == "deleted"


def test_rename_workspace_file_moves_folder_contents_without_opening_editor_state():
    state = write_workspace_file(base_state(), path="src/app.py", content="print('bye')")

    next_state = rename_workspace_file(state, path="src", new_path="lib")

    assert next_state["working_tree"]["src/app.py"] == "deleted"
    assert next_state["working_tree"]["lib/app.py"] == {
        "status": "untracked",
        "content": "print('bye')",
    }
    assert next_state["operation_metadata"]["last_workspace_file_renamed_from"] == "src"
    assert next_state["operation_metadata"]["last_workspace_file_renamed_to"] == "lib"


def test_workspace_file_rejects_unsafe_paths():
    with pytest.raises(BadRequest, match="project-relative"):
        create_workspace_file(base_state(), path="/etc/passwd", content="")
    with pytest.raises(BadRequest, match=".git"):
        create_workspace_file(base_state(), path=".git/config", content="")
    with pytest.raises(BadRequest, match="Parent-directory"):
        create_workspace_file(base_state(), path="../secret.txt", content="")
