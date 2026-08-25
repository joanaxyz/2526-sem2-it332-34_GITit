"""Shared helpers for persisting run-like runtime state."""

from collections.abc import Iterable
from typing import cast

from django.db import transaction
from django.db.models import Model

from common.constants import SESSION_STATUS_STARTED


@transaction.atomic
def discard_started_run[RunModel: Model](run: RunModel) -> bool:
    """Lock and delete a run only while it is still active."""

    manager = cast(object, type(run).objects)
    locked = manager.select_for_update().filter(pk=run.pk).first()
    if locked is None or locked.status != SESSION_STATUS_STARTED:
        return False
    locked.delete()
    return True


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
