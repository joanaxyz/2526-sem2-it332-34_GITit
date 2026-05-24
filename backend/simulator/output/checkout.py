from __future__ import annotations


def format_checkout(runtime, state: dict, outcome) -> str:
    details = outcome.details
    if details.get("new"):
        return f"Switched to a new branch '{details.get('switched')}'"
    if details.get("detached"):
        return f"HEAD is now at {details.get('detached')}"
    return f"Switched to branch '{details.get('switched')}'"
