from drf_spectacular.utils import extend_schema
from rest_framework.exceptions import NotFound, PermissionDenied
from rest_framework.response import Response
from rest_framework.views import APIView

from adventures.models import AdventureLevel
from common.exceptions import Locked
from curriculum.selectors import adventure_locked, chapter_locked, level_locked
from drills.openapi import (
    DrillReportResponseSerializer,
    DrillRunStateResponseSerializer,
    LevelDrillPlanResponseSerializer,
)
from drills.payloads import drill_progress_payload, drill_run_payload, level_drill_payload
from drills.selectors import get_drill_progress
from drills.serializers import DrillReportSerializer, DrillRunStateSerializer
from drills.services import (
    active_run,
    close_active_run,
    record_drill_session,
    sanitize_queue_state,
    save_run_state,
)
from players.services import get_or_create_player


def _get_level(level_id: int) -> AdventureLevel:
    try:
        return (
            AdventureLevel.objects.select_related("chapter", "chapter__story")
            .prefetch_related("command_forms__command_skill")
            .get(id=level_id, is_published=True)
        )
    except AdventureLevel.DoesNotExist as error:
        raise NotFound("That level does not exist.") from error


def _assert_drillable(player, level: AdventureLevel) -> None:
    """The drill's gate: the same content locks as the level, minus the
    companion requirement.

    A drill is recall practice on text, not a battle, so owning a companion
    is irrelevant to it - but drilling a level the player cannot reach yet
    would leak content the story has not handed them, so the chapter,
    adventure, and previous-level gates all still apply.
    """
    from shop.access import can_launch

    locked, reason = chapter_locked(player=player, chapter=level.chapter)
    if locked:
        raise Locked(reason or "Clear the previous chapter to unlock this drill.")
    if level.source_content_definition_id and not can_launch(
        player.user, level.source_content_definition
    ):
        raise PermissionDenied("You do not have access to this level.")
    locked, reason = adventure_locked(player=player, adventure=level)
    if locked:
        raise Locked(reason or "Complete the previous adventure to unlock this drill.")
    locked, reason = level_locked(player=player, level=level)
    if locked:
        raise Locked(reason or "Complete the previous level to unlock this drill.")


class LevelDrillAPIView(APIView):
    """The composed drill for one level, plus this player's drill history."""

    @extend_schema(responses={200: LevelDrillPlanResponseSerializer})
    def get(self, request, level_id: int):
        player = get_or_create_player(request.user)
        level = _get_level(level_id)
        _assert_drillable(player, level)
        progress = get_drill_progress(player=player, level_id=level.id)
        return Response(
            level_drill_payload(
                level=level,
                progress=progress,
                run=active_run(player=player, level_id=level.id),
            )
        )


class LevelDrillResultAPIView(APIView):
    """Record one reported session. Rewards nothing and unlocks nothing - see
    ``drills.services.progress`` for why self-reporting is safe here."""

    @extend_schema(
        request=DrillReportSerializer,
        responses={200: DrillReportResponseSerializer},
    )
    def post(self, request, level_id: int):
        player = get_or_create_player(request.user)
        level = _get_level(level_id)
        _assert_drillable(player, level)
        serializer = DrillReportSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        progress = record_drill_session(
            player=player,
            level=level,
            answers_total=serializer.validated_data["answers_total"],
            answers_correct=serializer.validated_data["answers_correct"],
            completed=serializer.validated_data["completed"],
            shaky_form_keys=serializer.validated_data["shaky_form_keys"],
        )
        # The queue is finished, so the resumable run retires with it -
        # otherwise the next visit would offer to resume a drill that has
        # already been reported.
        close_active_run(player=player, level=level, completed=True)
        return Response({"progress": drill_progress_payload(progress)})


class LevelDrillRunAPIView(APIView):
    """Checkpoint or discard the in-progress queue.

    PUT after each answer; DELETE when the learner deliberately starts
    over. Nothing here is reward-affecting - it only decides which
    question a return lands on.
    """

    @extend_schema(
        request=DrillRunStateSerializer,
        responses={200: DrillRunStateResponseSerializer},
    )
    def put(self, request, level_id: int):
        player = get_or_create_player(request.user)
        level = _get_level(level_id)
        _assert_drillable(player, level)
        serializer = DrillRunStateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        state = sanitize_queue_state(
            level_id=level.id,
            queue_state={
                "cards": data["cards"],
                "queue": data["queue"],
                "sequencePending": data["sequence_pending"],
                "answered": data["answered"],
                "correct": data["correct"],
            },
        )
        run = save_run_state(
            player=player,
            level=level,
            queue_state=state,
            answered=data["answered"],
            correct=data["correct"],
        )
        return Response({"resume": drill_run_payload(run)})

    @extend_schema(request=None, responses={200: DrillRunStateResponseSerializer})
    def delete(self, request, level_id: int):
        player = get_or_create_player(request.user)
        level = _get_level(level_id)
        _assert_drillable(player, level)
        close_active_run(player=player, level=level, completed=False)
        return Response({"resume": None})
