from rest_framework import serializers
from rest_framework.response import Response
from rest_framework.views import APIView

from adventures.services import (
    AdventureCommandService,
    AdventureRunService,
)
from adventures.serializers import adventure_run_payload
from adventures.models import AdventureProblemAttempt, AdventureRun, CommandAdventure


class _CommandSerializer(serializers.Serializer):
    command = serializers.CharField(max_length=500)


def _get_run(run_id: int, user) -> AdventureRun:
    return AdventureRun.objects.select_related("command_adventure").get(
        id=run_id, user=user
    )


def _active_attempt(run: AdventureRun) -> AdventureProblemAttempt:
    attempt = AdventureRunService().current_attempt(run=run)
    if attempt is None:
        from common.exceptions import Locked

        raise Locked("This run has no active attempt.")
    return attempt


class CommandAdventureRunStartAPIView(APIView):
    def post(self, request, adventure_slug: str):
        adventure = CommandAdventure.objects.get(slug=adventure_slug, is_published=True)
        run = AdventureRunService().start_run(user=request.user, adventure=adventure)
        return Response(adventure_run_payload(run), status=201)


class AdventureRunDetailAPIView(APIView):
    def get(self, request, run_id: int):
        run = _get_run(run_id, request.user)
        return Response(adventure_run_payload(run))


class AdventureRunSubmitCommandAPIView(APIView):
    def post(self, request, run_id: int):
        serializer = _CommandSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        run = _get_run(run_id, request.user)
        attempt = _active_attempt(run)
        result = AdventureCommandService().submit(
            attempt=attempt, command=serializer.validated_data["command"]
        )
        run.refresh_from_db()
        return Response(
            {
                "run": adventure_run_payload(run),
                "solved": result["solved"],
                "stdout": result["stdout"],
                "stderr": result["stderr"],
                "exit_code": result["exit_code"],
                "terminal_output": result["terminal_output"],
                "command_classification": result["command_classification"],
            }
        )


class AdventureRunUseHintAPIView(APIView):
    def post(self, request, run_id: int):
        run = _get_run(run_id, request.user)
        attempt = _active_attempt(run)
        result = AdventureRunService().use_hint(attempt=attempt)
        run.refresh_from_db()
        return Response(
            {
                "run": adventure_run_payload(run),
                "hint": result["hint"],
                "hint_number": result["hint_number"],
            }
        )


class AdventureRunFinishAPIView(APIView):
    def post(self, request, run_id: int):
        run = _get_run(run_id, request.user)
        run = AdventureRunService().abandon(run=run)
        return Response(adventure_run_payload(run))
