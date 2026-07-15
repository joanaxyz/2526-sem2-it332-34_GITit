from django.db import OperationalError, transaction
from drf_spectacular.utils import extend_schema
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.views import APIView

from challenges.models import ChallengeRun
from challenges.payloads import (
    challenge_run_payload,
    command_run_payload,
    prefetch_run_payload_context,
)
from challenges.selectors import get_challenge_trial
from challenges.serializers import (
    ChallengeRunStartSerializer,
    CommandSubmitSerializer,
    WorkspaceFileCreateSerializer,
    WorkspaceFilePathSerializer,
    WorkspaceFileRenameSerializer,
)
from challenges.services import (
    ChallengeCommandProcessingService,
    ChallengeRunService,
    ChallengeWorkspaceFileService,
)
from common.constants import SESSION_STATUS_STARTED
from common.exceptions import Conflict, Locked
from common.openapi import ChallengeCommandResponseSerializer, ChallengeRunResponseSerializer
from players.services import get_or_create_player


class ChallengeRunStartAPIView(APIView):
    @extend_schema(request=ChallengeRunStartSerializer, responses={201: ChallengeRunResponseSerializer})
    def post(self, request, trial_id: int):
        serializer = ChallengeRunStartSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        trial = get_challenge_trial(trial_id)
        player = get_or_create_player(request.user)
        from shop.access import require_companion

        require_companion(player)
        chapter = trial.chapter
        if chapter.story_id:
            from curriculum.selectors import chapter_locked, story_locked

            locked, reason = story_locked(player=player, story=chapter.story)
            if locked:
                raise Locked(reason or "This story is locked.")
            locked, reason = chapter_locked(player=player, chapter=chapter)
            if locked:
                raise Locked(reason or "This chapter is locked.")
        if trial.challenge_level.source_content_definition_id:
            from shop.access import can_launch

            if not can_launch(request.user, trial.challenge_level.source_content_definition):
                raise PermissionDenied("You do not have access to this challenge.")
        prior_run = None
        prior_run_id = serializer.validated_data.get("prior_run_id")
        if prior_run_id:
            prior_run = ChallengeRun.objects.get(id=prior_run_id, player=player)
        is_replay = bool(serializer.validated_data.get("replay"))
        run = ChallengeRunService().start_run(
            player=player,
            trial=trial,
            source_entry_point=serializer.validated_data["source_entry_point"],
            prior_run=prior_run,
            is_replay=is_replay,
        )
        prefetch_run_payload_context(run)
        return Response(challenge_run_payload(run), status=201)


class ChallengeRunDetailAPIView(APIView):
    @extend_schema(responses={200: ChallengeRunResponseSerializer})
    def get(self, request, run_id: int):
        run = ChallengeRunService.hydrate_run(run_id, player=get_or_create_player(request.user))
        prefetch_run_payload_context(run)
        return Response(challenge_run_payload(run))

    @extend_schema(request=None, responses={204: None})
    def delete(self, request, run_id: int):
        player = get_or_create_player(request.user)
        run = ChallengeRun.objects.filter(id=run_id, player=player).first()
        if run is not None:
            ChallengeRunService().discard(run=run)
        return Response(status=204)


class ChallengeCommandSubmitAPIView(APIView):
    throttle_scope = "command_submit"

    # Atomic so the run-row lock taken below is held across the whole submit,
    # serializing concurrent commands for the same run.
    @extend_schema(request=CommandSubmitSerializer, responses={200: ChallengeCommandResponseSerializer})
    @transaction.atomic
    def post(self, request, run_id: int):
        serializer = CommandSubmitSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        player = get_or_create_player(request.user)
        try:
            run = (
                ChallengeRun.objects.select_for_update(nowait=True, of=("self",))
                .select_related(
                    "challenge_trial__challenge_level",
                    "challenge_trial__challenge_level__chapter",
                    "challenge_trial__challenge_level__chapter__story",
                    "challenge_trial__challenge_level__source_content_definition",
                    "selected_variant",
                )
                .get(id=run_id, player=player)
            )
        except OperationalError as exc:
            # NOWAIT lock refused: another command for this run is still
            # processing. Reject the duplicate rather than run it twice or wait.
            raise Conflict(
                "This command is still being processed - try again in a moment."
            ) from exc
        result = ChallengeCommandProcessingService().submit_command(
            run=run,
            command=serializer.validated_data["command"],
            execution=serializer.validated_data["execution"],
        )
        if result["run"].status != SESSION_STATUS_STARTED:
            prefetch_run_payload_context(result["run"])
        payload = command_run_payload(
            result["run"],
            repository_state=result["repository_state"],
            visualization=result["visualization"],
        )
        return Response(
            {
                "run": payload,
                "command_outcome": result["command_outcome"],
                "stdout": result["stdout"],
                "stderr": result["stderr"],
                "exit_code": result["exit_code"],
                "command_family": result["command_family"],
                "diagnostic_metadata": result["diagnostic_metadata"],
                "step": {
                    "id": result["step"].id,
                    "command_text": result["step"].command_text,
                    "terminal_output": result["terminal_output"],
                    "result_category": result["step"].result_category,
                    "evaluation_result": result["evaluation_result"],
                    "command_classification": result["command_classification"],
                    "contextual_feedback": result["contextual_feedback"],
                    "visualization_snapshot": result["visualization"],
                    "created_at": result["step"].created_at,
                },
            }
        )


class ChallengeWorkspaceFileAPIView(APIView):
    throttle_scope = "command_submit"

    @extend_schema(request=WorkspaceFileCreateSerializer, responses={200: ChallengeRunResponseSerializer})
    def post(self, request, run_id: int):
        serializer = WorkspaceFileCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        run = _get_workspace_run(run_id, get_or_create_player(request.user))
        run = ChallengeWorkspaceFileService().create_file(
            run=run,
            path=serializer.validated_data["path"],
            content=serializer.validated_data.get("content", ""),
        )
        run = ChallengeRunService.hydrate_run(run)
        prefetch_run_payload_context(run)
        return Response(challenge_run_payload(run))

    @extend_schema(request=WorkspaceFileCreateSerializer, responses={200: ChallengeRunResponseSerializer})
    def patch(self, request, run_id: int):
        serializer = WorkspaceFileCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        run = _get_workspace_run(run_id, get_or_create_player(request.user))
        run = ChallengeWorkspaceFileService().write_file(
            run=run,
            path=serializer.validated_data["path"],
            content=serializer.validated_data.get("content", ""),
        )
        run = ChallengeRunService.hydrate_run(run)
        prefetch_run_payload_context(run)
        return Response(challenge_run_payload(run))

    @extend_schema(request=WorkspaceFileRenameSerializer, responses={200: ChallengeRunResponseSerializer})
    def put(self, request, run_id: int):
        serializer = WorkspaceFileRenameSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        run = _get_workspace_run(run_id, get_or_create_player(request.user))
        run = ChallengeWorkspaceFileService().rename_file(
            run=run,
            path=serializer.validated_data["path"],
            new_path=serializer.validated_data["new_path"],
        )
        run = ChallengeRunService.hydrate_run(run)
        prefetch_run_payload_context(run)
        return Response(challenge_run_payload(run))

    @extend_schema(request=WorkspaceFilePathSerializer, responses={200: ChallengeRunResponseSerializer})
    def delete(self, request, run_id: int):
        serializer = WorkspaceFilePathSerializer(data=request.data or request.query_params)
        serializer.is_valid(raise_exception=True)
        run = _get_workspace_run(run_id, get_or_create_player(request.user))
        run = ChallengeWorkspaceFileService().delete_file(
            run=run,
            path=serializer.validated_data["path"],
        )
        run = ChallengeRunService.hydrate_run(run)
        prefetch_run_payload_context(run)
        return Response(challenge_run_payload(run))


class ChallengeRetryAPIView(APIView):
    @extend_schema(request=None, responses={201: ChallengeRunResponseSerializer})
    def post(self, request, run_id: int):
        player = get_or_create_player(request.user)
        prior = (
            ChallengeRun.objects.select_related(
                "challenge_trial__challenge_level",
                "challenge_trial__challenge_level__chapter",
                "challenge_trial__challenge_level__chapter__story",
                "selected_variant",
            )
            .get(id=run_id, player=player)
        )
        if prior.is_replay:
            raise Locked("Replay runs cannot be retried.")
        run = ChallengeRunService().start_run(
            player=player,
            trial=prior.challenge_trial,
            source_entry_point="retry",
            prior_run=prior,
        )
        prefetch_run_payload_context(run)
        return Response(challenge_run_payload(run), status=201)


def _get_workspace_run(run_id: int, player):
    return ChallengeRun.objects.select_related(
        "challenge_trial__challenge_level",
        "challenge_trial__challenge_level__chapter",
        "challenge_trial__challenge_level__chapter__story",
        "challenge_trial__challenge_level__source_content_definition",
        "selected_variant",
    ).get(id=run_id, player=player)
