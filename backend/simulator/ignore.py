from __future__ import annotations

import copy
import fnmatch


def gitignore_content(runtime, state: dict) -> object:
    for source in (
        state.get("working_tree") or {},
        state.get("staging") or {},
        runtime._head_tree(state),
    ):
        if ".gitignore" in source:
            return runtime.normalizer.entry_content(source[".gitignore"])
    return ""


def gitignore_patterns(content: object) -> list[str]:
    return [
        line.strip()
        for line in str(content or "").splitlines()
        if line.strip() and not line.strip().startswith("#")
    ]


def matching_gitignore_rule(content: object, path: str) -> str:
    for line in gitignore_patterns(content):
        pattern = line.rstrip("/")
        basename = path.rsplit("/", 1)[-1]
        if line.endswith("/") and (path == pattern or path.startswith(f"{pattern}/")):
            return line
        if "/" in line and fnmatch.fnmatch(path, line):
            return line
        if fnmatch.fnmatch(path, line) or fnmatch.fnmatch(basename, line):
            return line
    return ""


def path_matches_gitignore(content: object, path: str) -> bool:
    return bool(matching_gitignore_rule(content, path))


def refresh_ignored_paths(runtime, state: dict) -> None:
    content = gitignore_content(runtime, state)
    working_tree = state.setdefault("working_tree", {})
    if not working_tree:
        return

    head_tree = runtime._head_tree(state)
    staging = state.setdefault("staging", {})
    for path, value in list(working_tree.items()):
        if path == ".gitignore":
            continue
        status = runtime.normalizer.entry_status(value)
        if status in {"deleted", "removed"}:
            continue

        tracked = path in head_tree and not _staged_for_deletion(runtime, staging.get(path))
        content_value = runtime.normalizer.entry_content(value)
        matches = path_matches_gitignore(content, path)
        if matches and not tracked:
            if status != "ignored" or not isinstance(value, dict):
                working_tree[path] = {
                    "status": "ignored",
                    "content": copy.deepcopy(content_value),
                }
            continue
        if status == "ignored" and not matches:
            working_tree[path] = {
                "status": "untracked",
                "content": copy.deepcopy(content_value),
            }


def _staged_for_deletion(runtime, value: object | None) -> bool:
    return runtime.normalizer.entry_status(value) in {"deleted", "removed"}
