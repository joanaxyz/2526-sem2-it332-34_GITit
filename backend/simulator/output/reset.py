from __future__ import annotations


def format_reset(runtime, state: dict, outcome) -> str:
    details = outcome.details
    if "unstaged" in details:
        return ""
    if details.get("mode") == "hard":
        return f"HEAD is now at {details.get('to')}"
    return ""
