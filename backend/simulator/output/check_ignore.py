from __future__ import annotations

import fnmatch


def format_check_ignore(runtime, state: dict, outcome) -> str:
    path = outcome.details.get("path")
    if not path:
        return ""

    value = (state.get("working_tree") or {}).get(path)
    rule = _matching_rule(runtime, state, path)
    if runtime.normalizer.entry_status(value) != "ignored" and not rule:
        outcome.exit_code = 1
        return ""
    return f".gitignore:1:{rule or path}\t{path}"


def _matching_rule(runtime, state: dict, path: str) -> str:
    content = _gitignore_content(runtime, state)
    if not content:
        return path
    lines = [
        line.strip()
        for line in str(content).splitlines()
        if line.strip() and not line.strip().startswith("#")
    ]
    if not lines:
        return str(content)
    for line in lines:
        pattern = line.rstrip("/")
        if line.endswith("/") and (path == pattern or path.startswith(f"{pattern}/")):
            return line
        if fnmatch.fnmatch(path, line) or fnmatch.fnmatch(path.rsplit("/", 1)[-1], line):
            return line
    return lines[0]


def _gitignore_content(runtime, state: dict) -> object:
    for source in (state.get("working_tree") or {}, state.get("staging") or {}, runtime._head_tree(state)):
        if ".gitignore" in source:
            value = source[".gitignore"]
            if isinstance(value, dict):
                return value.get("content") or value.get("after") or value.get("value") or value
            return value
    return ""
