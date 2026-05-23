from __future__ import annotations


def format_commit(runtime, state: dict, outcome) -> str:
    details = outcome.details
    branch = details.get("branch") or runtime._head_branch(state) or "HEAD"
    commit_id = details.get("commit_id")
    message = details.get("message", "")
    changes = details.get("changes") or {}
    prefix = f"[{branch} {commit_id}] {message}"
    stats = _stats(runtime, changes)
    return "\n".join([prefix, *stats])


def _stats(runtime, changes: dict) -> list[str]:
    if not changes:
        return []
    files = len(changes)
    insertions = 0
    deletions = 0
    for change in changes.values():
        change_type = (
            change.get("change_type")
            if isinstance(change, dict)
            else runtime.normalizer.entry_status(change)
        )
        if change_type in {"deleted", "removed"}:
            deletions += 1
        elif change_type in {"added", "new"}:
            insertions += 1
        else:
            insertions += 1
            deletions += 1
    parts = [f"{files} file{'s' if files != 1 else ''} changed"]
    if insertions:
        parts.append(f"{insertions} insertion{'s' if insertions != 1 else ''}(+)")
    if deletions:
        parts.append(f"{deletions} deletion{'s' if deletions != 1 else ''}(-)")
    return [f" {', '.join(parts)}"]
