"""Shared helpers for persisting run-like runtime state."""

from collections.abc import Iterable


def update_fields_for_execution(
    changed_fields: Iterable[str],
    *,
    state_mutated: bool,
    repository_state_field: str = "repository_state",
) -> list[str]:
    """Return stable `save(update_fields=...)` fields for a command submission.

    Challenge and Adventure runs use different counters, but both only persist the
    large repository-state JSON when the client execution actually mutated it.
    """

    fields = set(changed_fields)
    if state_mutated:
        fields.add(repository_state_field)
    return sorted(fields)
