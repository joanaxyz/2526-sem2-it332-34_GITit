from __future__ import annotations


def format_init(runtime, state: dict, outcome) -> str:
    if outcome.details.get("quiet"):
        return ""
    directory = outcome.details.get("directory")
    suffix = f" in {directory}/.git/" if directory else " in .git/"
    action = "Reinitialized existing Git repository" if outcome.details.get("reinitialized") else "Initialized empty Git repository"
    return f"{action}{suffix}"
