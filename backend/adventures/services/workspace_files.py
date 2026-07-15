"""Workspace-file mutations for active adventure attempts."""

from adventures.models import AdventureRun
from common.services.run_workspace import mutate_run_workspace_file


class AdventureWorkspaceFileService:
    def create_file(
        self,
        *,
        attempt: AdventureRun,
        path: str,
        content: str = "",
    ) -> AdventureRun:
        return mutate_run_workspace_file(
            run=attempt,
            operation="create",
            path=path,
            content=content,
            ended_message="This attempt has already ended.",
        )

    def write_file(
        self,
        *,
        attempt: AdventureRun,
        path: str,
        content: str = "",
    ) -> AdventureRun:
        return mutate_run_workspace_file(
            run=attempt,
            operation="write",
            path=path,
            content=content,
            ended_message="This attempt has already ended.",
        )

    def delete_file(
        self,
        *,
        attempt: AdventureRun,
        path: str,
    ) -> AdventureRun:
        return mutate_run_workspace_file(
            run=attempt,
            operation="delete",
            path=path,
            ended_message="This attempt has already ended.",
        )

    def rename_file(
        self,
        *,
        attempt: AdventureRun,
        path: str,
        new_path: str,
    ) -> AdventureRun:
        return mutate_run_workspace_file(
            run=attempt,
            operation="rename",
            path=path,
            new_path=new_path,
            ended_message="This attempt has already ended.",
        )
