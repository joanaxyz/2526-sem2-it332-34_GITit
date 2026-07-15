"""Trusted backend workspace-file mutations.

The browser may preview file edits optimistically, but reward-affecting run state
must be derived from the persisted run plus the requested path/content only. This
keeps a forged client ``repository_state`` from skipping puzzle objectives.
"""

from __future__ import annotations

import copy
import re

from common.exceptions import BadRequest
from simulator.ignore import refresh_ignored_paths
from simulator.services import RepositoryStateSimulator

_UNSUPPORTED_PATH_CHARS = re.compile(r"[<>|]")
_WINDOWS_DRIVE = re.compile(r"^[A-Za-z]:")


def create_workspace_file(repository_state: dict, *, path: str, content: str = "") -> dict:
    runtime = RepositoryStateSimulator()
    state = runtime.normalize_state(repository_state)
    normalized_path = normalize_workspace_path(path)
    _validate_new_path(runtime, state, normalized_path)
    state.setdefault("working_tree", {})[normalized_path] = {
        "status": "untracked",
        "content": content,
    }
    refresh_ignored_paths(runtime, state)
    _set_operation_metadata(state, last_workspace_file_created=normalized_path)
    return runtime.normalize_state(state)


def write_workspace_file(repository_state: dict, *, path: str, content: str = "") -> dict:
    runtime = RepositoryStateSimulator()
    state = runtime.normalize_state(repository_state)
    normalized_path = normalize_workspace_path(path)
    _validate_known_path(runtime, state, normalized_path)
    base_tree = runtime.normalizer.head_tree(state)
    state.setdefault("working_tree", {})[normalized_path] = {
        "status": "modified" if normalized_path in base_tree else "untracked",
        "content": content,
    }
    refresh_ignored_paths(runtime, state)
    _set_operation_metadata(state, last_workspace_file_written=normalized_path)
    return runtime.normalize_state(state)


def delete_workspace_file(repository_state: dict, *, path: str) -> dict:
    runtime = RepositoryStateSimulator()
    state = runtime.normalize_state(repository_state)
    normalized_path = normalize_workspace_path(path)
    target_paths = _target_file_paths(runtime, state, normalized_path)
    base_tree = runtime.normalizer.head_tree(state)

    working_tree = state.setdefault("working_tree", {})
    staging = state.setdefault("staging", {})
    conflicts = set(state.get("conflicts") or [])
    conflict_details = state.get("conflict_details") or {}

    for target_path in target_paths:
        staging.pop(target_path, None)
        if target_path in base_tree:
            working_tree[target_path] = "deleted"
        else:
            working_tree.pop(target_path, None)
        conflicts.discard(target_path)
        conflict_details.pop(target_path, None)

    state["conflicts"] = sorted(conflicts)
    state["conflict_details"] = conflict_details
    refresh_ignored_paths(runtime, state)
    _set_operation_metadata(
        state,
        last_workspace_file_deleted=normalized_path,
        last_workspace_file_deleted_paths=target_paths,
    )
    return runtime.normalize_state(state)


def rename_workspace_file(repository_state: dict, *, path: str, new_path: str) -> dict:
    runtime = RepositoryStateSimulator()
    state = runtime.normalize_state(repository_state)
    normalized_path = normalize_workspace_path(path)
    normalized_new_path = normalize_workspace_path(new_path)
    if normalized_path == normalized_new_path:
        raise BadRequest("Choose a different name.")
    if normalized_new_path.startswith(f"{normalized_path}/"):
        raise BadRequest("A folder cannot be moved inside itself.")

    source_paths = _target_file_paths(runtime, state, normalized_path)
    destinations = _rename_destinations(normalized_path, normalized_new_path, source_paths)
    _validate_destination_paths(runtime, state, destinations, source_paths)

    base_tree = runtime.normalizer.head_tree(state)
    visible_tree = runtime.normalizer.visible_project_tree(state, assume_normalized=True)
    working_tree = state.setdefault("working_tree", {})
    staging = state.setdefault("staging", {})
    conflicts = set(state.get("conflicts") or [])
    conflict_details = state.get("conflict_details") or {}

    moved_entries: list[tuple[str, str, object]] = []
    for source_path, destination in zip(source_paths, destinations, strict=True):
        visible_entry = visible_tree.get(source_path)
        if not visible_entry or visible_entry.get("status") == "deleted":
            raise BadRequest(f"{source_path} cannot be renamed because it is deleted.")
        moved_entries.append((source_path, destination, copy.deepcopy(visible_entry.get("content"))))

    for source_path, destination, content in moved_entries:
        staging.pop(source_path, None)
        working_tree.pop(source_path, None)
        if source_path in base_tree:
            working_tree[source_path] = "deleted"
        working_tree[destination] = {
            "status": "modified" if destination in base_tree else "untracked",
            "content": content,
        }
        conflicts.discard(source_path)
        conflict_details.pop(source_path, None)

    state["conflicts"] = sorted(conflicts)
    state["conflict_details"] = conflict_details
    refresh_ignored_paths(runtime, state)
    _set_operation_metadata(
        state,
        last_workspace_file_renamed_from=normalized_path,
        last_workspace_file_renamed_to=normalized_new_path,
    )
    return runtime.normalize_state(state)


def normalize_workspace_path(path: str) -> str:
    normalized = str(path or "").replace("\\", "/").strip()
    if not normalized:
        raise BadRequest("File path is required.")
    if normalized.endswith("/"):
        raise BadRequest("File path must include a file name.")
    if _WINDOWS_DRIVE.match(normalized) or normalized.startswith("/"):
        raise BadRequest("Use a project-relative path.")

    parts = [part for part in normalized.split("/") if part and part != "."]
    if not parts or any(part == ".." for part in parts):
        raise BadRequest("Parent-directory paths are not supported.")
    if parts[0] == ".git":
        raise BadRequest("Files inside .git cannot be edited here.")
    if any(_UNSUPPORTED_PATH_CHARS.search(part) for part in parts):
        raise BadRequest("The file path contains unsupported characters.")
    return "/".join(parts)


def _validate_new_path(runtime: RepositoryStateSimulator, state: dict, path: str) -> None:
    known_paths = _known_file_paths(runtime, state)
    if path in known_paths:
        raise BadRequest(f"{path} already exists.")

    parent_parts = path.split("/")[:-1]
    for index in range(1, len(parent_parts) + 1):
        parent_path = "/".join(parent_parts[:index])
        if parent_path in known_paths:
            raise BadRequest(f"{parent_path} is a file, not a folder.")

    prefix = f"{path}/"
    if any(known.startswith(prefix) for known in known_paths):
        raise BadRequest(f"{path} is already a folder.")


def _validate_known_path(runtime: RepositoryStateSimulator, state: dict, path: str) -> None:
    known_paths = _known_file_paths(runtime, state)
    if path not in known_paths:
        raise BadRequest(f"{path} does not exist.")
    prefix = f"{path}/"
    if any(known.startswith(prefix) for known in known_paths):
        raise BadRequest(f"{path} is a folder, not a file.")


def _target_file_paths(runtime: RepositoryStateSimulator, state: dict, path: str) -> list[str]:
    known_paths = _known_file_paths(runtime, state)
    if path in known_paths:
        return [path]

    prefix = f"{path}/"
    matches = sorted(known for known in known_paths if known.startswith(prefix))
    if matches:
        return matches
    raise BadRequest(f"{path} does not exist.")


def _rename_destinations(source: str, destination: str, source_paths: list[str]) -> list[str]:
    if len(source_paths) == 1 and source_paths[0] == source:
        return [destination]
    prefix = f"{source}/"
    return [f"{destination}/{source_path.removeprefix(prefix)}" for source_path in source_paths]


def _validate_destination_paths(
    runtime: RepositoryStateSimulator,
    state: dict,
    destinations: list[str],
    source_paths: list[str],
) -> None:
    occupied_paths = _known_file_paths(runtime, state) - set(source_paths)
    for destination in destinations:
        if destination in occupied_paths:
            raise BadRequest(f"{destination} already exists.")

        parent_parts = destination.split("/")[:-1]
        for index in range(1, len(parent_parts) + 1):
            parent_path = "/".join(parent_parts[:index])
            if parent_path in occupied_paths:
                raise BadRequest(f"{parent_path} is a file, not a folder.")

        prefix = f"{destination}/"
        if any(known.startswith(prefix) for known in occupied_paths):
            raise BadRequest(f"{destination} is already a folder.")


def _known_file_paths(runtime: RepositoryStateSimulator, state: dict) -> set[str]:
    visible = runtime.normalizer.visible_project_tree(state, assume_normalized=True)
    return {
        *visible.keys(),
        *(state.get("staging") or {}).keys(),
        *(state.get("working_tree") or {}).keys(),
    }


def _set_operation_metadata(state: dict, **metadata: object) -> None:
    state.setdefault("operation_metadata", {}).update(metadata)
    for key, value in metadata.items():
        state[key] = value
