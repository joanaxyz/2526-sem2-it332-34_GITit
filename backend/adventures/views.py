from django.db import OperationalError, transaction
from drf_spectacular.utils import extend_schema
from rest_framework.exceptions import NotFound, PermissionDenied, ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from adventures.models import AdventureLevel, AdventureRun
from adventures.payloads import (
    adventure_command_payload,
    adventure_level_library_payload,
    adventure_run_payload,
)
from adventures.serializers import (
    CommandSubmitSerializer,
    WorkspaceFilePathSerializer,
    WorkspaceFileRenameSerializer,
    WorkspaceFileSerializer,
)
from adventures.services import (
    AdventureCommandService,
    AdventureRunService,
    AdventureWorkspaceFileService,
)
from common.constants import SESSION_STATUS_STARTED
from common.exceptions import Conflict, Locked
from common.openapi import (
    AdventureCommandResponseSerializer,
    AdventureLevelLibraryResponseSerializer,
    AdventureRunResponseSerializer,
)
from curriculum.selectors import adventure_locked, chapter_locked, level_locked
from players.services import get_or_create_player


def _get_run(run_id: int, player) -> AdventureRun:
    return (
        AdventureRun.objects.select_related(
            "level",
            "level__chapter",
            "level__chapter__story",
            "level__source_content_definition",
            "current_wave",
            "selected_variant",
        )
        .prefetch_related("level__command_forms", "level__waves", "current_wave__command_forms")
        .get(id=run_id, player=player)
    )


def _run_with_active_attempt(
    run_id: int,
    player,
    *,
    lock: bool = False,
) -> tuple[AdventureRun, AdventureRun]:
    queryset = (
        AdventureRun.objects.select_related(
            "level",
            "level__chapter",
            "level__chapter__story",
            "level__source_content_definition",
            "current_wave",
            "selected_variant",
        )
        .prefetch_related("level__command_forms", "level__waves", "current_wave__command_forms")
        .filter(id=run_id, player=player, status=SESSION_STATUS_STARTED)
    )
    if lock:
        queryset = queryset.select_for_update(nowait=True, of=("self",))
    attempt = queryset.first()
    if attempt is None:
        _get_run(run_id, player)
        raise Locked("This run has no active attempt.")
    return attempt, attempt


def _assert_level_unlocked(player, level: AdventureLevel) -> None:
    from shop.access import require_companion

    require_companion(player)
    chapter = level.chapter
    if chapter.story_id:
        from curriculum.selectors import story_locked

        locked, reason = story_locked(player=player, story=chapter.story)
        if locked:
            raise Locked(reason or "This story is locked.")
    locked, reason = chapter_locked(player=player, chapter=chapter)
    if locked:
        raise Locked(reason or "Clear the previous chapter to unlock this adventure.")
    locked, reason = adventure_locked(player=player, adventure=level)
    if locked:
        raise Locked(reason or "Complete the previous adventure to unlock this adventure.")
    locked, reason = level_locked(player=player, level=level)
    if locked:
        raise Locked(reason or "Complete the previous level to unlock this one.")
    if level.source_content_definition_id:
        from shop.access import can_launch

        if not can_launch(player.user, level.source_content_definition):
            raise PermissionDenied("You do not have access to this adventure.")


class AdventureLevelRunStartAPIView(APIView):
    @extend_schema(request=None, responses={201: AdventureRunResponseSerializer})
    def post(self, request, level_id: int):
        level = (
            AdventureLevel.objects.select_related(
                "chapter",
                "chapter__story",
                "source_content_definition",
            )
            .prefetch_related("command_forms", "waves", "waves__variants")
            .get(id=level_id, is_published=True)
        )
        player = get_or_create_player(request.user)
        _assert_level_unlocked(player, level)
        run = AdventureRunService().start_run(
            player=player,
            level=level,
        )
        return Response(adventure_run_payload(run), status=201)


class AdventureRunStartAPIView(APIView):
    @extend_schema(request=None, responses={201: AdventureRunResponseSerializer})
    def post(self, request, adventure_slug: str):
        raise ValidationError(
            {
                "detail": (
                    "Adventure runs must start from a level: "
                    "/api/adventure-levels/{level_id}/runs/."
                )
            }
        )



class AdventureRunDetailAPIView(APIView):
    @extend_schema(responses={200: AdventureRunResponseSerializer})
    def get(self, request, run_id: int):
        run = _get_run(run_id, get_or_create_player(request.user))
        return Response(adventure_run_payload(run))

    @extend_schema(request=None, responses={204: None})
    def delete(self, request, run_id: int):
        player = get_or_create_player(request.user)
        run = AdventureRun.objects.filter(id=run_id, player=player).first()
        if run is not None:
            AdventureRunService().discard(run=run)
        return Response(status=204)


class AdventureRunSubmitCommandAPIView(APIView):
    throttle_scope = "command_submit"

    @extend_schema(request=CommandSubmitSerializer, responses={200: AdventureCommandResponseSerializer})
    @transaction.atomic
    def post(self, request, run_id: int):
        serializer = CommandSubmitSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        player = get_or_create_player(request.user)
        try:
            run, attempt = _run_with_active_attempt(run_id, player, lock=True)
        except OperationalError as exc:
            raise Conflict(
                "This command is still being processed - try again in a moment."
            ) from exc
        result = AdventureCommandService().submit(
            attempt=attempt,
            command=serializer.validated_data["command"],
            execution=serializer.validated_data["execution"],
        )
        submitted_attempt = result["attempt"]
        # A wave clear that advances to the next wave keeps the run STARTED but
        # still swaps in a fresh problem, so reload the full run payload too.
        transitioned = (
            run.status != SESSION_STATUS_STARTED
            or submitted_attempt.status != SESSION_STATUS_STARTED
            or result.get("run_transitioned", False)
        )
        run_payload = (
            adventure_run_payload(run, include_current_steps=False)
            if transitioned
            else adventure_command_payload(
                run,
                attempt=submitted_attempt,
                repository_state=result["repository_state"],
                executed_commands=result["executed_commands"],
            )
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
                "command_outcome": result["command_outcome"],
                "step": {
                    "id": step.id,
                    "command_text": step.command_text,
                    "terminal_output": step.terminal_output,
                    "result_category": step.result_category,
                },
            }
        )


class AdventureRunLevelLibraryAPIView(APIView):
    @extend_schema(request=None, responses={200: AdventureLevelLibraryResponseSerializer})
    @transaction.atomic
    def post(self, request, run_id: int):
        try:
            run, _attempt = _run_with_active_attempt(run_id, get_or_create_player(request.user), lock=True)
        except OperationalError as exc:
            raise Conflict(
                "This command is still being processed - try again in a moment."
            ) from exc
        book = adventure_level_library_payload(run)
        if book is None:
            raise NotFound("This adventure level has no command library.")
        AdventureRunService().record_library_opened(run=run)
        return Response({"book": book, "run": adventure_run_payload(run)})



class AdventureWorkspaceFileAPIView(APIView):
    throttle_scope = "command_submit"

    @extend_schema(request=WorkspaceFileSerializer, responses={200: AdventureRunResponseSerializer})
    def post(self, request, run_id: int):
        return self._mutate_file(request, run_id, AdventureWorkspaceFileService().create_file)

    @extend_schema(request=WorkspaceFileSerializer, responses={200: AdventureRunResponseSerializer})
    def patch(self, request, run_id: int):
        return self._mutate_file(request, run_id, AdventureWorkspaceFileService().write_file)

    @extend_schema(request=WorkspaceFileRenameSerializer, responses={200: AdventureRunResponseSerializer})
    def put(self, request, run_id: int):
        serializer = WorkspaceFileRenameSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        run, attempt = _run_with_active_attempt(run_id, get_or_create_player(request.user))
        AdventureWorkspaceFileService().rename_file(
            attempt=attempt,
            path=serializer.validated_data["path"],
            new_path=serializer.validated_data["new_path"],
        )
        return Response(adventure_run_payload(run))

    @extend_schema(request=WorkspaceFilePathSerializer, responses={200: AdventureRunResponseSerializer})
    def delete(self, request, run_id: int):
        serializer = WorkspaceFilePathSerializer(data=request.data or request.query_params)
        serializer.is_valid(raise_exception=True)
        run, attempt = _run_with_active_attempt(run_id, get_or_create_player(request.user))
        AdventureWorkspaceFileService().delete_file(
            attempt=attempt,
            path=serializer.validated_data["path"],
        )
        return Response(adventure_run_payload(run))

    def _mutate_file(self, request, run_id: int, mutate):
        serializer = WorkspaceFileSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        run, attempt = _run_with_active_attempt(run_id, get_or_create_player(request.user))
        mutate(
            attempt=attempt,
            path=serializer.validated_data["path"],
            content=serializer.validated_data.get("content", ""),
        )
        return Response(adventure_run_payload(run))
