from __future__ import annotations

from simulator.ignore import gitignore_content, matching_gitignore_rule


def format_check_ignore(runtime, state: dict, outcome) -> str:
    path = outcome.details.get("path")
    if not path:
        return ""

    value = (state.get("working_tree") or {}).get(path)
    rule = matching_gitignore_rule(gitignore_content(runtime, state), path)
    if runtime.normalizer.entry_status(value) != "ignored" and not rule:
        outcome.exit_code = 1
        return ""
    return f".gitignore:1:{rule or path}\t{path}"
