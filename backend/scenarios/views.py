from django.db import OperationalError, transaction
from rest_framework.response import Response
from rest_framework.views import APIView

from common.constants import SESSION_MODE_PRIMARY, SESSION_STATUS_STARTED
from common.exceptions import Locked
from common.performance import timing
from scenarios.models import PracticeKind, PracticeSession
from scenarios.selectors import (
    get_command_drill,
    get_command_usage,
    get_workflow_level,
    storey_content_page,
)
from scenarios.serializers import (
    CommandSubmitSerializer,
    PracticeStartSerializer,
    WorkspaceFileCreateSerializer,
    command_session_payload,
    prefetch_session_payload_context,
    session_payload,
)
from scenarios.services import (
    CommandProcessingService,
    PracticeSessionService,
    WorkspaceFileCreationService,
)


class StoreyContentAPIView(APIView):
    def get(self, request, storey_id: int):
        section = request.query_params.get("section") or "command_topics"
        cursor = _int_param(request.query_params.get("cursor"))
        limit = _int_param(request.query_params.get("limit")) or 8
        with timing("practice.storey_content", storey_id=storey_id, section=section):
            return Response(
                storey_content_page(
                    user=request.user,
                    storey_id=storey_id,
                    section=section,
                    cursor=cursor,
                    limit=limit,
                )
            )


class ModuleContentAPIView(StoreyContentAPIView):
    def get(self, request, module_id: int):
        return super().get(request, storey_id=module_id)


class CommandUsagePreviewAPIView(APIView):
    def get(self, request, usage_id: int):
        usage = get_command_usage(usage_id)
        return Response(
            {
                "id": usage.id,
                "slug": usage.slug,
                "usage_form": usage.usage_form,
                "label": usage.label,
                "summary": usage.summary,
                "topic": {
                    "id": usage.topic_id,
                    "slug": usage.topic.slug,
                    "base_command": usage.topic.base_command,
                    "title": usage.topic.title,
                },
                "command_preview": usage.command_preview or usage.topic.command_preview or {},
            }
        )


class PracticeSessionStartAPIView(APIView):
    def post(self, request):
        serializer = PracticeStartSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        problem = _problem_from_validated(serializer.validated_data)
        prior_session = None
        prior_session_id = serializer.validated_data.get("prior_session_id")
        if prior_session_id:
            prior_session = PracticeSession.objects.get(id=prior_session_id, user=request.user)
        session = PracticeSessionService().start_session(
            user=request.user,
            problem=problem,
            source_entry_point=serializer.validated_data["source_entry_point"],
            prior_session=prior_session,
        )
        prefetch_session_payload_context(session)
        return Response(session_payload(session), status=201)


class PracticeSessionDetailAPIView(APIView):
    def get(self, request, session_id: int):
        session = PracticeSessionService.hydrate_session(session_id, user=request.user)
        prefetch_session_payload_context(session)
        return Response(session_payload(session))


class CommandSubmitAPIView(APIView):
    def post(self, request, session_id: int):
        serializer = CommandSubmitSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        session = PracticeSession.objects.select_related(
            "module",
            "command_drill__usage__topic",
            "workflow_scenario",
            "workflow_level__scenario",
            "variant",
        ).get(id=session_id, user=request.user)
        result = CommandProcessingService().submit_command(
            session=session,
            command=serializer.validated_data["command"],
        )
        if result["session"].status != SESSION_STATUS_STARTED:
            prefetch_session_payload_context(result["session"])
        payload = command_session_payload(
            result["session"],
            repository_state=result["repository_state"],
            visualization=result["visualization"],
        )
        return Response(
            {
                "session": payload,
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


class WorkspaceFileCreateAPIView(APIView):
    def post(self, request, session_id: int):
        serializer = WorkspaceFileCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        session = PracticeSession.objects.select_related(
            "module",
            "command_drill__usage__topic",
            "workflow_scenario",
            "workflow_level__scenario",
            "variant",
        ).get(id=session_id, user=request.user)
        session = WorkspaceFileCreationService().create_file(
            session=session,
            path=serializer.validated_data["path"],
            content=serializer.validated_data.get("content", ""),
        )
        session = PracticeSessionService.hydrate_session(session)
        prefetch_session_payload_context(session)
        return Response(session_payload(session))

    def patch(self, request, session_id: int):
        serializer = WorkspaceFileCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        session = PracticeSession.objects.select_related(
            "module",
            "command_drill__usage__topic",
            "workflow_scenario",
            "workflow_level__scenario",
            "variant",
        ).get(id=session_id, user=request.user)
        session = WorkspaceFileCreationService().write_file(
            session=session,
            path=serializer.validated_data["path"],
            content=serializer.validated_data.get("content", ""),
        )
        session = PracticeSessionService.hydrate_session(session)
        prefetch_session_payload_context(session)
        return Response(session_payload(session))


class PracticeSessionAbandonAPIView(APIView):
    def post(self, request, session_id: int):
        session = PracticeSession.objects.get(id=session_id, user=request.user)
        session = PracticeSessionService().abandon(session=session)
        session = PracticeSessionService.hydrate_session(session)
        prefetch_session_payload_context(session)
        return Response(session_payload(session))


class PracticeRetryAPIView(APIView):
    @transaction.atomic
    def post(self, request, session_id: int):
        try:
            prior = (
                PracticeSession.objects.select_for_update(nowait=True, of=("self",))
                .select_related(
                    "command_drill__usage__topic",
                    "workflow_level__scenario",
                    "variant",
                )
                .get(id=session_id, user=request.user)
            )
        except OperationalError:
            return Response({"detail": "Session busy, retry later."}, status=409)
        if prior.mode != SESSION_MODE_PRIMARY:
            raise Locked("Review sessions cannot be retried.")
        if prior.status == SESSION_STATUS_STARTED:
            prior = PracticeSessionService().abandon(session=prior)
        session = PracticeSessionService().start_session(
            user=request.user,
            problem=prior.problem,
            source_entry_point="retry",
            prior_session=prior,
        )
        prefetch_session_payload_context(session)
        return Response(session_payload(session), status=201)


def _problem_from_validated(data: dict):
    if data["problem_type"] == PracticeKind.COMMAND_DRILL:
        return get_command_drill(data["command_drill_id"])
    return get_workflow_level(data["workflow_level_id"])


def _int_param(value: str | None) -> int | None:
    try:
        return int(value) if value is not None else None
    except (TypeError, ValueError):
        return None
