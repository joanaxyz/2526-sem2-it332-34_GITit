"""Shared transactional mutations for playable run workspaces.

Adventure and challenge runs persist the same normalized repository-state shape.
This module owns the common lock/status/mutate/save sequence while each domain
keeps a small service that supplies its own terminology and model instance.
"""

from __future__ import annotations

from typing import Literal, cast

from django.db import transaction
from django.db.models import Model

from common.constants import SESSION_STATUS_STARTED
from common.exceptions import Locked
from common.git.workspace_files import (
    create_workspace_file,
    delete_workspace_file,
    rename_workspace_file,
    write_workspace_file,
)

WorkspaceOperation = Literal["create", "write", "delete", "rename"]

@transaction.atomic
def mutate_run_workspace_file[RunModel: Model](
    *,
    run: RunModel,
    operation: WorkspaceOperation,
    path: str,
    content: str = "",
    new_path: str = "",
    ended_message: str,
) -> RunModel:
    """Lock ``run`` and apply one trusted workspace-file mutation."""

    manager = cast(object, type(run).objects)
    locked_run = manager.select_for_update(of=("self",)).get(pk=run.pk)
    if locked_run.status != SESSION_STATUS_STARTED:
        raise Locked(ended_message)

    mutators = {
        "create": create_workspace_file,
        "write": write_workspace_file,
        "delete": delete_workspace_file,
        "rename": rename_workspace_file,
    }
    mutator = mutators[operation]
    kwargs = {"path": path, "content": content}
    if operation == "delete":
        kwargs = {"path": path}
    elif operation == "rename":
        kwargs = {"path": path, "new_path": new_path}
    locked_run.repository_state = mutator(
        locked_run.repository_state,
        **kwargs,
    )
    locked_run.save(update_fields=["repository_state"])
    return cast(RunModel, locked_run)
