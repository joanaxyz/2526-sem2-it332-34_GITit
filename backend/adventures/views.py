from rest_framework import serializers
from rest_framework.response import Response
from rest_framework.views import APIView

from adventures.models import AdventureQuestAttempt, AdventureRun, CommandAdventure
from adventures.serializers import adventure_command_payload, adventure_run_payload
from adventures.services import (
    AdventureCommandService,
    AdventureRunService,
    AdventureWorkspaceFileService,
)
from common.constants import SESSION_STATUS_STARTED
from common.exceptions import Locked


class _CommandSerializer(serializers.Serializer):
    command = serializers.CharField(max_length=500)


class _WorkspaceFileSerializer(serializers.Serializer):
    path = serializers.CharField(max_length=240)
    content = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=20000,
        default="",
        trim_whitespace=False,
    )


def _get_run(run_id: int, user) -> AdventureRun:
    return AdventureRun.objects.select_related("command_adventure").get(
        id=run_id, user=user
    )


def _run_with_active_attempt(run_id: int, user) -> tuple[AdventureRun, AdventureQuestAttempt]:
    """One query for the live attempt plus everything the submit path touches
    (run, adventure, problem, variant). The returned run is the same instance the
    services mutate, so callers never need a refresh round trip."""
    attempt = (
        AdventureQuestAttempt.objects.select_related(
            "run__command_adventure", "adventure_quest", "selected_variant"
        )
        .filter(run_id=run_id, run__user=user, status=SESSION_STATUS_STARTED)
        .order_by("order")
        .first()
    )
    if attempt is None:
        _get_run(run_id, user)  # missing/foreign run raises DoesNotExist as before
        raise Locked("This run has no active attempt.")
    run = attempt.run
    # The requester is the run's owner (filtered above); priming the relation
    # spares every downstream `run.user` access a lazy query.
    run.user = user
    return run, attempt


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
        run, attempt = _run_with_active_attempt(run_id, request.user)
        result = AdventureCommandService().submit(
            attempt=attempt, command=serializer.validated_data["command"]
        )
        # `run` is the instance the service just mutated and saved (scores,
        # status, next attempt), so its in-memory state is already current.
        # A transition (solved / budget spent) advances mastery and opens the next
        # problem, so the client needs the full run. A plain mid-attempt command
        # only moves the live attempt state, so a slim patch is enough.
        submitted_attempt = result["attempt"]
        transitioned = (
            run.status != SESSION_STATUS_STARTED
            or submitted_attempt.status != SESSION_STATUS_STARTED
        )
        run_payload = (
            adventure_run_payload(run)
            if transitioned
            else adventure_command_payload(run, attempt=submitted_attempt)
        )
        step = result["step"]
        return Response(
            {
                "run": run_payload,
                "solved": result["solved"],
                "stdout": result["stdout"],
                "stderr": result["stderr"],
                "exit_code": result["exit_code"],
                "terminal_output": result["terminal_output"],
                "command_classification": result["command_classification"],
                # Symmetric to the challenge submit response: lets the client
                # replace its optimistic pending step with the persisted one.
                "step": {
                    "id": step.id,
                    "command_text": step.command_text,
                    "terminal_output": step.terminal_output,
                    "result_category": step.result_category,
                },
            }
        )


class AdventureRunUseHintAPIView(APIView):
    def post(self, request, run_id: int):
        run, attempt = _run_with_active_attempt(run_id, request.user)
        result = AdventureRunService().use_hint(attempt=attempt)
        return Response(
            {
                "run": adventure_run_payload(run),
                "hint": result["hint"],
                "hint_number": result["hint_number"],
            }
        )


class AdventureWorkspaceFileAPIView(APIView):
    def post(self, request, run_id: int):
        return self._mutate_file(request, run_id, AdventureWorkspaceFileService().create_file)

    def patch(self, request, run_id: int):
        return self._mutate_file(request, run_id, AdventureWorkspaceFileService().write_file)

    def _mutate_file(self, request, run_id: int, mutate):
        serializer = _WorkspaceFileSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        run, attempt = _run_with_active_attempt(run_id, request.user)
        mutate(
            attempt=attempt,
            path=serializer.validated_data["path"],
            content=serializer.validated_data.get("content", ""),
        )
        return Response(adventure_run_payload(run))


class AdventureRunFinishAPIView(APIView):
    def post(self, request, run_id: int):
        run = _get_run(run_id, request.user)
        run = AdventureRunService().abandon(run=run)
        return Response(adventure_run_payload(run))
