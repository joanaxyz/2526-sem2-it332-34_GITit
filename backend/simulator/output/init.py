from __future__ import annotations


def format_init(runtime, state: dict, outcome) -> str:
    if outcome.details.get("quiet"):
        return ""
    directory = outcome.details.get("directory")
    suffix = f" in {directory}/.git/" if directory else " in .git/"
    return f"Initialized empty Git repository{suffix}"
