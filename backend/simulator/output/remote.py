from __future__ import annotations


def format_remote(runtime, state: dict, outcome) -> str:
    details = outcome.details
    if any(key in details for key in ("added", "removed", "renamed")):
        return ""
    remotes = state.get("remotes") or {}
    if details.get("verbose"):
        lines = []
        for name, url in sorted(remotes.items()):
            lines.append(f"{name}\t{url} (fetch)")
            lines.append(f"{name}\t{url} (push)")
        return "\n".join(lines)
    return "\n".join(sorted(remotes))
