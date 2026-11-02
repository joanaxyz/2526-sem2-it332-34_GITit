from django.db import OperationalError, transaction
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework.response import Response
from rest_framework.views import APIView

from adventures.models import (
    AdventureLevel,
    AdventureLevelTier,
    AdventureLevelTierRun,
)
from adventures.openapi import (
    AdventureLevelTierCommandResponseSerializer,
    AdventureLevelTierRunResponseSerializer,
)
from adventures.services import (
    AdventureLevelTierCommandProcessingService,
    AdventureLevelTierRunService,
    playable_level_publication_filter,
)
from adventures.tier_payloads import (
    command_run_payload,
    prefetch_run_payload_context,
    tier_run_payload,
)
from adventures.tier_serializers import AdventureLevelTierRunStartSerializer
from common.constants import SESSION_STATUS_STARTED
from common.exceptions import Conflict, Locked
from common.schemas.openapi import RequiredPatchBodyAutoSchema
from common.serializers import (
    CommandSubmitSerializer,
    WorkspaceFilePathSerializer,
    WorkspaceFileRenameSerializer,
    WorkspaceFileSerializer,
)
from common.services.run_workspace import RunWorkspaceFileService
from curriculum.selectors import chapter_locked
from players.services import get_or_create_player

ADVENTURE_TIER_WORKSPACE_FILES = RunWorkspaceFileService(
    ended_message="This adventure tier run has already ended."
)


def _assert_adventure_accessible(player, level: AdventureLevel) -> None:
    """The gate every adventure tier run start owes: a companion and an
    unlocked chapter. (Challenge trials deliberately have no companion
    requirement; see challenges/tests/test_challenge_start_access.py.)"""
    from shop.access import require_companion

    require_companion(player)
    # chapter_locked resolves the owning story's prerequisite gate too and
    # reports unlocked for a chapter with no story, so it covers both.
    locked, reason = chapter_locked(player=player, chapter=level.chapter)
    if locked:
        raise Locked(reason or "Clear the previous chapter to unlock this adventure.")


# ---------------------------------------------------------------------------
# AdventureLevelTierRun lifecycle - mirrors challenges/views.py.
# ---------------------------------------------------------------------------


class AdventureLevelTierRunStartAPIView(APIView):
    throttle_scope = "run_start"

    @extend_schema(
        request=AdventureLevelTierRunStartSerializer,
        responses={201: AdventureLevelTierRunResponseSerializer},
    )
    def post(self, request, tier_id: int):
        serializer = AdventureLevelTierRunStartSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        tier = AdventureLevelTier.objects.select_related(
            "adventure_level",
            "adventure_level__chapter",
            "adventure_level__chapter__story",
        ).get(
            playable_level_publication_filter("adventure_level__"),
            id=tier_id,
            is_published=True,
            adventure_level__is_published=True,
        )
        player = get_or_create_player(request.user)
        _assert_adventure_accessible(player, tier.adventure_level)
        prior_run = None
        prior_run_id = serializer.validated_data.get("prior_run_id")
        if prior_run_id:
            prior_run = AdventureLevelTierRun.objects.get(id=prior_run_id, player=player)
        is_replay = bool(serializer.validated_data.get("replay"))
        run = AdventureLevelTierRunService().start_run(
            player=player,
            tier=tier,
            source_entry_point=serializer.validated_data["source_entry_point"],
            prior_run=prior_run,
            is_replay=is_replay,
            transfer=serializer.validated_data.get("transfer", False),
        )
        prefetch_run_payload_context(run)
        return Response(tier_run_payload(run), status=201)


class AdventureLevelTierRunDetailAPIView(APIView):
    @extend_schema(responses={200: AdventureLevelTierRunResponseSerializer})
    def get(self, request, run_id: int):
        run = AdventureLevelTierRunService.hydrate_run(
            run_id, player=get_or_create_player(request.user)
        )
        prefetch_run_payload_context(run)
        return Response(tier_run_payload(run))

    @extend_schema(request=None, responses={204: None})
    def delete(self, request, run_id: int):
        player = get_or_create_player(request.user)
        run = AdventureLevelTierRun.objects.filter(id=run_id, player=player).first()
        if run is not None:
            AdventureLevelTierRunService().discard(run=run)
        return Response(status=204)


class AdventureLevelTierCommandSubmitAPIView(APIView):
    throttle_scope = "command_submit"

    @extend_schema(
        request=CommandSubmitSerializer,
        responses={200: AdventureLevelTierCommandResponseSerializer},
    )
    @transaction.atomic
    def post(self, request, run_id: int):
        serializer = CommandSubmitSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        player = get_or_create_player(request.user)
        try:
            run = (
                AdventureLevelTierRun.objects.select_for_update(nowait=True, of=("self",))
                .select_related(
                    "tier__adventure_level__chapter__story",
                    "tier__adventure_level__chapter",
                    "current_scenario",
                    "selected_variant",
                    "player",
                    "pendingcommandintroduction",
                )
                .get(id=run_id, player=player)
            )
        except OperationalError as exc:
            raise Conflict(
                "This command is still being processed - try again in a moment."
            ) from exc
        result = AdventureLevelTierCommandProcessingService().submit_command(
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
            rewards=result["rewards"],
            tutor_context=result["tutor_context"],
        )
        return Response(
            {
                "run": payload,
                "command_outcome": result["command_outcome"],
                "stdout": result["stdout"],
                "stderr": result["stderr"],
                "exit_code": result["exit_code"],
                "command_family": result["command_family"],
                "learned_skills": result["learned_skills"],
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


class AdventureLevelTierWorkspaceFileAPIView(APIView):
    throttle_scope = "command_submit"
    schema = RequiredPatchBodyAutoSchema()

    @extend_schema(
        request=WorkspaceFileSerializer, responses={200: AdventureLevelTierRunResponseSerializer}
    )
    def post(self, request, run_id: int):
        serializer = WorkspaceFileSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        run = _get_tier_workspace_run(run_id, get_or_create_player(request.user))
        run = ADVENTURE_TIER_WORKSPACE_FILES.create_file(
            run=run,
            path=serializer.validated_data["path"],
            content=serializer.validated_data.get("content", ""),
        )
        run = AdventureLevelTierRunService.hydrate_run(run)
        prefetch_run_payload_context(run)
        return Response(tier_run_payload(run))

    @extend_schema(
        request={"application/json": {"$ref": "#/components/schemas/WorkspaceFile"}},
        responses={200: AdventureLevelTierRunResponseSerializer},
    )
    def patch(self, request, run_id: int):
        serializer = WorkspaceFileSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        run = _get_tier_workspace_run(run_id, get_or_create_player(request.user))
        run = ADVENTURE_TIER_WORKSPACE_FILES.write_file(
            run=run,
            path=serializer.validated_data["path"],
            content=serializer.validated_data.get("content", ""),
        )
        run = AdventureLevelTierRunService.hydrate_run(run)
        prefetch_run_payload_context(run)
        return Response(tier_run_payload(run))

    @extend_schema(
        request=WorkspaceFileRenameSerializer,
        responses={200: AdventureLevelTierRunResponseSerializer},
    )
    def put(self, request, run_id: int):
        serializer = WorkspaceFileRenameSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        run = _get_tier_workspace_run(run_id, get_or_create_player(request.user))
        run = ADVENTURE_TIER_WORKSPACE_FILES.rename_file(
            run=run,
            path=serializer.validated_data["path"],
            new_path=serializer.validated_data["new_path"],
        )
        run = AdventureLevelTierRunService.hydrate_run(run)
        prefetch_run_payload_context(run)
        return Response(tier_run_payload(run))

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="path",
                type={"type": "string", "maxLength": 240},
                location=OpenApiParameter.QUERY,
                required=True,
            )
        ],
        responses={200: AdventureLevelTierRunResponseSerializer},
    )
    def delete(self, request, run_id: int):
        serializer = WorkspaceFilePathSerializer(data=request.data or request.query_params)
        serializer.is_valid(raise_exception=True)
        run = _get_tier_workspace_run(run_id, get_or_create_player(request.user))
        run = ADVENTURE_TIER_WORKSPACE_FILES.delete_file(
            run=run,
            path=serializer.validated_data["path"],
        )
        run = AdventureLevelTierRunService.hydrate_run(run)
        prefetch_run_payload_context(run)
        return Response(tier_run_payload(run))


class AdventureLevelTierRetryAPIView(APIView):
    throttle_scope = "run_start"

    @extend_schema(request=None, responses={201: AdventureLevelTierRunResponseSerializer})
    def post(self, request, run_id: int):
        player = get_or_create_player(request.user)
        prior = AdventureLevelTierRun.objects.select_related(
            "tier__adventure_level__chapter__story",
            "tier__adventure_level__chapter",
            "selected_variant",
        ).get(id=run_id, player=player)
        if prior.is_replay:
            raise Locked("Replay runs cannot be retried.")
        run = AdventureLevelTierRunService().start_run(
            player=player,
            tier=prior.tier,
            source_entry_point="retry",
            prior_run=prior,
        )
        prefetch_run_payload_context(run)
        return Response(tier_run_payload(run), status=201)


def _get_tier_workspace_run(run_id: int, player) -> AdventureLevelTierRun:
    return AdventureLevelTierRun.objects.select_related(
        "tier__adventure_level__chapter__story",
        "tier__adventure_level__chapter",
        "current_scenario",
        "selected_variant",
    ).get(id=run_id, player=player)
