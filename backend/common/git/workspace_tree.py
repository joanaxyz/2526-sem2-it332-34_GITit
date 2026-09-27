"""Filesystem view of a run's working copy.

Mirrors the browser simulator's workspace tree. Files come from the visible
project tree minus deleted entries; folders are implied by file
paths plus the optional ``directories`` list, which keeps folders that hold no
files. Git never tracks those folders. ``directories`` is omitted when empty so
states without empty folders keep their existing shape and hashes.
"""

from __future__ import annotations

from collections.abc import Iterable

from simulator.state import RepositoryStateNormalizer

_NORMALIZER = RepositoryStateNormalizer()


def live_file_paths(state: dict) -> set[str]:
    visible = _NORMALIZER.visible_project_tree(state, assume_normalized=True)
    return {
        path
        for path, entry in visible.items()
        if not _NORMALIZER.is_delete_marker(_NORMALIZER.entry_status(entry))
    }


def explicit_directories(state: dict) -> list[str]:
    value = state.get("directories")
    if not isinstance(value, list):
        return []
    return [path for path in value if isinstance(path, str) and path]


def directory_paths(state: dict, files: set[str] | None = None) -> set[str]:
    files = live_file_paths(state) if files is None else files
    directories: set[str] = set()
    for path in [*files, *(f"{directory}/" for directory in explicit_directories(state))]:
        parts = path.split("/")[:-1]
        for index in range(1, len(parts) + 1):
            directories.add("/".join(parts[:index]))
    return directories


def path_kind(state: dict, path: str) -> str | None:
    """``"file"``, ``"directory"``, or ``None``; ``""`` is the project root."""

    if path == "":
        return "directory"
    files = live_file_paths(state)
    if path in files:
        return "file"
    return "directory" if path in directory_paths(state, files) else None


def directory_entries(state: dict, directory: str) -> list[dict]:
    files = live_file_paths(state)
    directories = directory_paths(state, files)
    prefix = f"{directory}/" if directory else ""
    entries: dict[str, dict] = {}
    for kind, paths in (("file", files), ("directory", directories)):
        for path in paths:
            if not path.startswith(prefix):
                continue
            rest = path[len(prefix) :]
            if not rest or "/" in rest:
                continue
            entries[rest] = {"name": rest, "path": path, "kind": kind}
    return [entries[name] for name in sorted(entries)]


def descendant_paths(state: dict, directory: str) -> tuple[list[str], list[str]]:
    """Live files and folders strictly inside ``directory``."""

    files = live_file_paths(state)
    prefix = f"{directory}/"
    return (
        sorted(path for path in files if path.startswith(prefix)),
        sorted(path for path in directory_paths(state, files) if path.startswith(prefix)),
    )


def set_explicit_directories(state: dict, candidates: Iterable[str]) -> None:
    """Store only folders that contain no files and no other listed folder."""

    files = live_file_paths(state)
    unique = list(dict.fromkeys(candidate for candidate in candidates if candidate))
    kept = [
        directory
        for directory in unique
        if directory not in files
        and not any(path.startswith(f"{directory}/") for path in files)
        and not any(other.startswith(f"{directory}/") for other in unique)
    ]
    if kept:
        state["directories"] = sorted(kept)
    else:
        state.pop("directories", None)


def parent_path(path: str) -> str:
    return "/".join(path.split("/")[:-1])
