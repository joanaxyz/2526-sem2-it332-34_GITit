from __future__ import annotations


def format_ls_files(runtime, state: dict, outcome) -> str:
    if outcome.details.get("unmerged"):
        return _format_unmerged(runtime, state)

    tracked = set(runtime._head_tree(state))
    for path, value in (state.get("staging") or {}).items():
        if runtime.normalizer.is_delete_marker(value) or runtime.normalizer.is_delete_marker(
            runtime.normalizer.entry_status(value)
        ):
            tracked.discard(path)
        else:
            tracked.add(path)
    return "\n".join(sorted(tracked))


def _format_unmerged(runtime, state: dict) -> str:
    current = runtime._head_commit(state) or "HEAD"
    incoming = state.get("merge_parent") or state.get("operation_metadata", {}).get("last_merge_target") or "MERGE_HEAD"
    base = "BASE"
    lines = []
    for path in sorted(state.get("conflicts", [])):
        lines.extend(
            [
                f"100644 {base} 1\t{path}",
                f"100644 {current} 2\t{path}",
                f"100644 {incoming} 3\t{path}",
            ]
        )
    return "\n".join(lines)
