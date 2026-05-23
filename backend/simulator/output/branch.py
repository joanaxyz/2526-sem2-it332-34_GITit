from __future__ import annotations


def format_branch(runtime, state: dict, outcome) -> str:
    details = outcome.details
    if "created" in details:
        return ""
    if "deleted" in details:
        target = details.get("target") or ""
        return f"Deleted branch {details['deleted']} (was {target})."

    verbose = bool(details.get("verbose"))
    current = runtime._head_branch(state)
    lines = []
    for name, target in sorted((state.get("branches") or {}).items()):
        marker = "*" if name == current else " "
        if verbose:
            message = ""
            commit = runtime._commit_by_id(state, target)
            if commit:
                message = f" {commit.get('message', '')}"
            lines.append(f"{marker} {name:<16} {target or '(no commits)'}{message}".rstrip())
        else:
            lines.append(f"{marker} {name}")
    return "\n".join(lines)
