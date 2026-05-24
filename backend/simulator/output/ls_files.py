from __future__ import annotations


def format_ls_files(runtime, state: dict, outcome) -> str:
    tracked = set(runtime._head_tree(state))
    for path, value in (state.get("staging") or {}).items():
        if runtime.normalizer.is_delete_marker(value) or runtime.normalizer.is_delete_marker(
            runtime.normalizer.entry_status(value)
        ):
            tracked.discard(path)
        else:
            tracked.add(path)
    return "\n".join(sorted(tracked))
