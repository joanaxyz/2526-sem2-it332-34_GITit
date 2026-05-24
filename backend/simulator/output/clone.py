from __future__ import annotations


def format_clone(runtime, state: dict, outcome) -> str:
    return f"Cloning into '{outcome.details.get('destination')}'...\ndone."
