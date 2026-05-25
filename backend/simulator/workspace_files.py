from __future__ import annotations

import re

from simulator.ignore import refresh_ignored_paths
from simulator.services import RepositoryStateSimulator


class WorkspaceFileError(ValueError):
    pass


class WorkspaceFileStateService:
    """Apply IDE-style file creation to the teaching repository state."""

    def __init__(self) -> None:
        self.runtime = RepositoryStateSimulator()

    def create_file(self, state: dict, *, path: str, content: str = "") -> dict:
        next_state = self.runtime.clone_state(state)
        next_state = self.runtime.normalize_state(next_state)
        normalized_path = self.normalize_path(path)
        self._validate_new_path(next_state, normalized_path)
        next_state.setdefault("working_tree", {})[normalized_path] = {
            "status": "untracked",
            "content": content,
        }
        refresh_ignored_paths(self.runtime, next_state)
        self.runtime._set_operation_metadata(
            next_state,
            last_workspace_file_created=normalized_path,
        )
        return self.runtime.normalize_state(next_state)

    def write_file(self, state: dict, *, path: str, content: str = "") -> dict:
        next_state = self.runtime.clone_state(state)
        next_state = self.runtime.normalize_state(next_state)
        normalized_path = self.normalize_path(path)
        self._validate_known_path(next_state, normalized_path)
        head_tree = self.runtime._head_tree(next_state)
        status = "modified" if normalized_path in head_tree else "untracked"
        next_state.setdefault("working_tree", {})[normalized_path] = {
            "status": status,
            "content": content,
        }
        refresh_ignored_paths(self.runtime, next_state)
        self.runtime._set_operation_metadata(
            next_state,
            last_workspace_file_written=normalized_path,
        )
        return self.runtime.normalize_state(next_state)

    def normalize_path(self, path: str) -> str:
        normalized = str(path or "").replace("\\", "/").strip()
        if not normalized:
            raise WorkspaceFileError("File path is required.")
        if normalized.endswith("/"):
            raise WorkspaceFileError("File path must include a file name.")
        if re.match(r"^[A-Za-z]:", normalized) or normalized.startswith("/"):
            raise WorkspaceFileError("Use a project-relative path.")
        parts = [part for part in normalized.split("/") if part not in {"", "."}]
        if not parts or any(part == ".." for part in parts):
            raise WorkspaceFileError("Parent-directory paths are not supported.")
        if parts[0] == ".git":
            raise WorkspaceFileError("Files inside .git cannot be edited here.")
        if any(any(char in part for char in "<>|") for part in parts):
            raise WorkspaceFileError("The file path contains unsupported characters.")
        return "/".join(parts)

    def _validate_new_path(self, state: dict, path: str) -> None:
        visible_tree = self.runtime.normalizer.visible_project_tree(state)
        known_paths = (
            set(visible_tree)
            | set(state.get("staging", {}))
            | set(state.get("working_tree", {}))
        )
        if path in known_paths:
            raise WorkspaceFileError(f"{path} already exists.")

        parent_parts = path.split("/")[:-1]
        for index in range(1, len(parent_parts) + 1):
            parent_path = "/".join(parent_parts[:index])
            if parent_path in known_paths:
                raise WorkspaceFileError(f"{parent_path} is a file, not a folder.")

        path_prefix = f"{path}/"
        if any(existing.startswith(path_prefix) for existing in known_paths):
            raise WorkspaceFileError(f"{path} is already a folder.")

    def _validate_known_path(self, state: dict, path: str) -> None:
        visible_tree = self.runtime.normalizer.visible_project_tree(state)
        known_paths = (
            set(visible_tree)
            | set(state.get("staging", {}))
            | set(state.get("working_tree", {}))
        )
        if path not in known_paths:
            raise WorkspaceFileError(f"{path} does not exist.")
        path_prefix = f"{path}/"
        if any(existing.startswith(path_prefix) for existing in known_paths):
            raise WorkspaceFileError(f"{path} is a folder, not a file.")
