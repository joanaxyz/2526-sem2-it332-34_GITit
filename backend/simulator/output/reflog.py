from __future__ import annotations


def format_reflog(runtime, state: dict, outcome) -> str:
    entries = state.get("reflog", [])
    if not entries:
        target = runtime._head_commit(state) or "0000000"
        return f"{target} HEAD@{{0}}: current"
    lines = []
    for entry in reversed(entries):
        lines.append(f"{entry.get('target')} {entry.get('ref')}: {entry.get('message')}")
    return "\n".join(lines)
