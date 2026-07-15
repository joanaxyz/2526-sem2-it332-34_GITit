"""Workspace-file mutations for active challenge runs."""

from challenges.models import ChallengeRun
from common.services.run_workspace import mutate_run_workspace_file


class ChallengeWorkspaceFileService:
    def create_file(
        self,
        *,
        run: ChallengeRun,
        path: str,
        content: str = "",
    ) -> ChallengeRun:
        return mutate_run_workspace_file(
            run=run,
            operation="create",
            path=path,
            content=content,
            ended_message="This challenge run has already ended.",
        )

    def write_file(
        self,
        *,
        run: ChallengeRun,
        path: str,
        content: str = "",
    ) -> ChallengeRun:
        return mutate_run_workspace_file(
            run=run,
            operation="write",
            path=path,
            content=content,
            ended_message="This challenge run has already ended.",
        )

    def delete_file(
        self,
        *,
        run: ChallengeRun,
        path: str,
    ) -> ChallengeRun:
        return mutate_run_workspace_file(
            run=run,
            operation="delete",
            path=path,
            ended_message="This challenge run has already ended.",
        )

    def rename_file(
        self,
        *,
        run: ChallengeRun,
        path: str,
        new_path: str,
    ) -> ChallengeRun:
        return mutate_run_workspace_file(
            run=run,
            operation="rename",
            path=path,
            new_path=new_path,
            ended_message="This challenge run has already ended.",
        )
