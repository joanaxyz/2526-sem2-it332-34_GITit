from __future__ import annotations


def format_rm(runtime, state: dict, outcome) -> str:
    return "\n".join(f"rm '{path}'" for path in outcome.details.get("paths", []))
