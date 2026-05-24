from __future__ import annotations


def format_diff(runtime, state: dict, outcome) -> str:
    staged = bool(outcome.details.get("staged"))
    head = bool(outcome.details.get("head"))
    name_only = bool(outcome.details.get("name_only"))
    paths = tuple(outcome.details.get("paths") or ())
    if head:
        changes = _head_changes(runtime, state)
    elif staged:
        changes = _staged_changes(runtime, state)
    else:
        changes = _working_changes(runtime, state)
    if paths:
        requested = set(paths)
        changes = {path: change for path, change in changes.items() if path in requested}
    if name_only:
        return "\n".join(sorted(changes))
    return "\n".join(
        _format_file(runtime, path, change) for path, change in sorted(changes.items())
    )


def _staged_changes(runtime, state: dict) -> dict:
    return runtime._changes_from_entries(runtime._head_tree(state), state.get("staging", {}))


def _working_changes(runtime, state: dict) -> dict:
    index_tree = runtime._apply_changes(runtime._head_tree(state), _staged_changes(runtime, state))
    entries = {
        path: value
        for path, value in (state.get("working_tree", {}) or {}).items()
        if runtime.normalizer.entry_status(value) != "ignored"
        and runtime.normalizer.entry_status(value) != "untracked"
        and path in index_tree
    }
    return runtime._changes_from_entries(index_tree, entries)


def _head_changes(runtime, state: dict) -> dict:
    head_tree = runtime._head_tree(state)
    combined_tree = runtime._apply_changes(head_tree, _staged_changes(runtime, state))
    working_entries = {
        path: value
        for path, value in (state.get("working_tree", {}) or {}).items()
        if runtime.normalizer.entry_status(value) != "ignored"
        and runtime.normalizer.entry_status(value) != "untracked"
        and path in combined_tree
    }
    combined_tree = runtime._apply_changes(
        combined_tree,
        runtime._changes_from_entries(combined_tree, working_entries),
    )
    return runtime._diff_trees(head_tree, combined_tree)


def _format_file(runtime, path: str, change: dict) -> str:
    before = change.get("before")
    after = change.get("after")
    deleted = runtime.normalizer.is_delete_marker(change.get("change_type")) or after is None
    added = before is None and not deleted
    old_label = "/dev/null" if added else f"a/{path}"
    new_label = "/dev/null" if deleted else f"b/{path}"
    before_line = "" if before is None else str(before)
    after_line = "" if after is None else str(after)
    lines = [
        f"diff --git a/{path} b/{path}",
        "index 0000000..1111111 100644",
        f"--- {old_label}",
        f"+++ {new_label}",
        "@@ -1 +1 @@",
    ]
    if not added:
        lines.append(f"-{before_line}")
    if not deleted:
        lines.append(f"+{after_line}")
    return "\n".join(lines)
