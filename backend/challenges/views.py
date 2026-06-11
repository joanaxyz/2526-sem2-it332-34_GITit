from django.db import OperationalError, transaction
from rest_framework.response import Response
from rest_framework.views import APIView

from common.constants import SESSION_MODE_PRIMARY, SESSION_MODE_REVIEW, SESSION_STATUS_STARTED
from common.exceptions import Locked
from challenges.models import ChallengeRun
from challenges.selectors import get_challenge_quest
from challenges.serializers import (
    ChallengeRunStartSerializer,
    CommandSubmitSerializer,
    WorkspaceFileCreateSerializer,
    challenge_run_payload,
    command_run_payload,
    prefetch_run_payload_context,
)
from challenges.services import ChallengeRunService
from practice.services import CommandProcessingService, WorkspaceFileCreationService


class ChallengeRunStartAPIView(APIView):
    def post(self, request, quest_id: int):
        serializer = ChallengeRunStartSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        quest = get_challenge_quest(quest_id)
        prior_run = None
        prior_run_id = serializer.validated_data.get("prior_run_id")
        if prior_run_id:
            prior_run = ChallengeRun.objects.get(id=prior_run_id, user=request.user)
        mode = SESSION_MODE_REVIEW if serializer.validated_data.get("review") else SESSION_MODE_PRIMARY
        run = ChallengeRunService().start_run(
            user=request.user,
            quest=quest,
            source_entry_point=serializer.validated_data["source_entry_point"],
            prior_run=prior_run,
            mode=mode,
        )
        prefetch_run_payload_context(run)
        return Response(challenge_run_payload(run), status=201)


class ChallengeRunDetailAPIView(APIView):
    def get(self, request, run_id: int):
        run = ChallengeRunService.hydrate_run(run_id, user=request.user)
        prefetch_run_payload_context(run)
        return Response(challenge_run_payload(run))


class ChallengeCommandSubmitAPIView(APIView):
    throttle_scope = "command_submit"

    def post(self, request, run_id: int):
        serializer = CommandSubmitSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        run = ChallengeRun.objects.select_related(
            "storey",
            "challenge",
            "challenge_quest__challenge",
            "challenge_variant",
        ).get(id=run_id, user=request.user)
        result = CommandProcessingService().submit_command(
            run=run,
            command=serializer.validated_data["command"],
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

    def post(self, request, run_id: int):
        serializer = WorkspaceFileCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        run = _get_workspace_run(run_id, request.user)
        run = WorkspaceFileCreationService().create_file(
            run=run,
            path=serializer.validated_data["path"],
            content=serializer.validated_data.get("content", ""),
        )
        run = ChallengeRunService.hydrate_run(run)
        prefetch_run_payload_context(run)
        return Response(challenge_run_payload(run))

    def patch(self, request, run_id: int):
        serializer = WorkspaceFileCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        run = _get_workspace_run(run_id, request.user)
        run = WorkspaceFileCreationService().write_file(
            run=run,
            path=serializer.validated_data["path"],
            content=serializer.validated_data.get("content", ""),
        )
        run = ChallengeRunService.hydrate_run(run)
        prefetch_run_payload_context(run)
        return Response(challenge_run_payload(run))


class ChallengeRunFinishAPIView(APIView):
    def post(self, request, run_id: int):
        run = ChallengeRun.objects.get(id=run_id, user=request.user)
        run = ChallengeRunService().abandon(run=run)
        run = ChallengeRunService.hydrate_run(run)
        prefetch_run_payload_context(run)
        return Response(challenge_run_payload(run))


class ChallengeRetryAPIView(APIView):
    @transaction.atomic
    def post(self, request, run_id: int):
        try:
            prior = (
                ChallengeRun.objects.select_for_update(nowait=True, of=("self",))
                .select_related("challenge_quest__challenge", "challenge_variant")
                .get(id=run_id, user=request.user)
            )
        except OperationalError:
            return Response({"detail": "Run busy, retry later."}, status=409)
        if prior.mode != SESSION_MODE_PRIMARY:
            raise Locked("Review runs cannot be retried.")
        if prior.status == SESSION_STATUS_STARTED:
            prior = ChallengeRunService().abandon(run=prior)
        run = ChallengeRunService().start_run(
            user=request.user,
            quest=prior.challenge_quest,
            source_entry_point="retry",
            prior_run=prior,
        )
        prefetch_run_payload_context(run)
        return Response(challenge_run_payload(run), status=201)


def _get_workspace_run(run_id: int, user):
    return ChallengeRun.objects.select_related(
        "storey",
        "challenge",
        "challenge_quest__challenge",
        "challenge_variant",
    ).get(id=run_id, user=user)
