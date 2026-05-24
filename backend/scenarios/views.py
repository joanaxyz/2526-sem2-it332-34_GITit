from rest_framework.response import Response
from rest_framework.views import APIView

from common.constants import (
    SESSION_MODE_PRIMARY,
    SESSION_STATUS_COMPLETED,
    SESSION_STATUS_STARTED,
)
from common.exceptions import Locked
from common.performance import timing
from scenarios.models import ScenarioSession
from scenarios.selectors import (
    get_difficulty_instance,
    required_successful_attempts_for_difficulty,
    scenario_list_queryset,
    scenario_queryset,
    scenario_status_payloads,
)
from scenarios.serializers import (
    CommandSubmitSerializer,
    InspectionAnswerSubmitSerializer,
    ScenarioStartSerializer,
    SkillFocusDemoCommandSerializer,
    session_payload,
)
from scenarios.services import (
    CommandProcessingService,
    InspectionAnswerSubmissionService,
    ScenarioSessionService,
)
from simulator.command_engine import GitCommandEngine
from simulator.services import RepositorySnapshotService


class LessonScenarioListAPIView(APIView):
    def get(self, request, lesson_id: int):
        with timing("scenario.lesson_list", lesson_id=lesson_id):
            scenarios = scenario_list_queryset().filter(lesson_id=lesson_id)
            return Response(
                scenario_status_payloads(
                    user=request.user,
                    scenarios=scenarios,
                    include_preview=False,
                )
            )


class UnitScenarioListAPIView(APIView):
    def get(self, request, unit_id: int):
        with timing("scenario.module_list", unit_id=unit_id):
            scenarios = scenario_list_queryset().filter(learning_unit_id=unit_id)
            return Response(
                scenario_status_payloads(
                    user=request.user,
                    scenarios=scenarios,
                    include_preview=False,
                )
            )


class UnitScenarioSummaryAPIView(APIView):
    def get(self, request):
        with timing("scenario.module_summary"):
            raw_unit_ids = request.query_params.get("module_ids") or request.query_params.get("unit_ids", "")
            unit_ids = [
                int(item)
                for item in raw_unit_ids.split(",")
                if item.strip().isdigit()
            ]
            scenarios = scenario_list_queryset()
            if unit_ids:
                scenarios = scenarios.filter(learning_unit_id__in=unit_ids)

            grouped = {str(unit_id): [] for unit_id in unit_ids}
            for payload in scenario_status_payloads(
                user=request.user,
                scenarios=scenarios,
                include_preview=False,
            ):
                grouped.setdefault(str(payload["learning_unit_id"]), []).append(payload)
            return Response(grouped)


class SkillFocusDetailAPIView(APIView):
    def get(self, request, slug: str):
        with timing("scenario.skill_focus_detail", slug=slug):
            scenario = scenario_queryset(include_variants=False).get(slug=slug)
            return Response(
                scenario_status_payloads(
                    user=request.user,
                    scenarios=[scenario],
                    include_preview=True,
                )[0]
            )


class SkillFocusDemoCommandAPIView(APIView):
    def post(self, request, slug: str):
        with timing("scenario.demo_command", slug=slug):
            serializer = SkillFocusDemoCommandSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            scenario = scenario_queryset(include_variants=False).get(slug=slug)

            def normalize(command: str) -> str:
                return " ".join(command.strip().split()).lower()

            command = serializer.validated_data["command"]
            normalized_command = normalize(command)
            preview_config = scenario.command_preview_config or {}
            safe_commands = (
                preview_config.get("supported_demo_commands")
                or [
                    item if isinstance(item, str) else item.get("command")
                    for item in preview_config.get("command_refs", [])
                    if isinstance(item, str) or (isinstance(item, dict) and item.get("command"))
                ]
                or scenario.safe_demo_commands
                or []
            )
            normalized_safe = {normalize(item) for item in safe_commands}
            if normalized_command not in normalized_safe:
                return Response(
                    {
                        "detail": "This command preview only accepts the listed demo commands.",
                    },
                    status=400,
                )

            state = serializer.validated_data.get("repository_state") or scenario.demo_repository_state
            result = GitCommandEngine().process(state, command)
            snapshot = RepositorySnapshotService().snapshot(result.state)
            return Response(
                {
                    "repository_state": snapshot,
                    "terminal_output": result.output,
                    "was_processable": result.processed,
                    "exit_code": result.exit_code,
                    "command_classification": "diagnostic" if result.diagnostic else "counted",
                }
            )


class ScenarioSessionStartAPIView(APIView):
    def post(self, request):
        with timing("scenario.session_start"):
            serializer = ScenarioStartSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            difficulty = get_difficulty_instance(serializer.validated_data["difficulty_instance_id"])
            prior_session = None
            prior_session_id = serializer.validated_data.get("prior_session_id")
            if prior_session_id:
                prior_session = ScenarioSession.objects.get(id=prior_session_id, user=request.user)
            session = ScenarioSessionService().start_session(
                user=request.user,
                difficulty_instance=difficulty,
                source_entry_point=serializer.validated_data["source_entry_point"],
                prior_session=prior_session,
            )
            with timing("scenario.session_start.serialization", session_id=session.id):
                payload = session_payload(session)
            return Response(payload, status=201)


class ScenarioSessionDetailAPIView(APIView):
    def get(self, request, session_id: int):
        session = (
            ScenarioSession.objects.select_related(
                "scenario",
                "learning_unit",
                "difficulty_instance",
                "variant",
            )
            .prefetch_related("step_logs")
            .get(id=session_id, user=request.user)
        )
        return Response(session_payload(session))


class CommandSubmitAPIView(APIView):
    def post(self, request, session_id: int):
        with timing("scenario.command_submit", session_id=session_id):
            serializer = CommandSubmitSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            session = ScenarioSession.objects.select_related(
                "scenario",
                "learning_unit",
                "difficulty_instance",
                "difficulty_instance__target_rule",
                "difficulty_instance__command_policy",
                "variant",
            ).get(id=session_id, user=request.user)
            result = CommandProcessingService().submit_command(
                session=session,
                command=serializer.validated_data["command"],
            )
            with timing("scenario.command_submit.serialization", session_id=session_id):
                payload = session_payload(result["session"], include_steps=False)
            return Response(
                {
                    "session": payload,
                    "step": {
                        "id": result["step"].id,
                        "command_text": result["step"].command_text,
                        "terminal_output": result["terminal_output"],
                        "result_category": result["step"].result_category,
                        "evaluation_result": result["evaluation_result"],
                        "command_classification": result["command_classification"],
                        "contextual_feedback": result["contextual_feedback"],
                        "created_at": result["step"].created_at,
                    },
                }
            )


class InspectionAnswerSubmitAPIView(APIView):
    def post(self, request, session_id: int):
        serializer = InspectionAnswerSubmitSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        session = ScenarioSession.objects.select_related(
            "scenario",
            "learning_unit",
            "difficulty_instance",
            "difficulty_instance__target_rule",
            "variant",
        ).get(id=session_id, user=request.user)
        result = InspectionAnswerSubmissionService().submit_answer(
            session=session,
            answer=serializer.validated_data["answer"],
        )
        return Response(
            {
                "session": session_payload(result["session"], include_steps=False),
                "evaluation_result": result["evaluation"].result_category,
                "summary": result["evaluation"].summary,
                "failed_rules": result["evaluation"].failed_rules,
            }
        )


class ScenarioSessionAbandonAPIView(APIView):
    def post(self, request, session_id: int):
        session = ScenarioSession.objects.get(id=session_id, user=request.user)
        session = ScenarioSessionService().abandon(session=session)
        return Response(session_payload(session))


class ScenarioRetryAPIView(APIView):
    def post(self, request, session_id: int):
        prior = ScenarioSession.objects.select_related(
            "scenario",
            "difficulty_instance",
            "difficulty_instance__command_policy",
            "difficulty_instance__target_rule",
            "variant",
        ).get(id=session_id, user=request.user)
        if prior.mode != SESSION_MODE_PRIMARY:
            raise Locked("Review sessions cannot be retried.")
        # If the prior session is a completed, accurate primary session and the
        # user already has the required number of successful accurate completions
        # for this difficulty, prevent retrying and direct them to Review mode.
        if (
            prior.mode == SESSION_MODE_PRIMARY
            and prior.status == SESSION_STATUS_COMPLETED
            and prior.counted_action_total <= prior.command_policy_snapshot["min_counted_commands"]
        ):
            required = required_successful_attempts_for_difficulty(prior.difficulty_instance)
            accurate_count = ScenarioSession.objects.filter(
                user=request.user,
                mode=SESSION_MODE_PRIMARY,
                status=SESSION_STATUS_COMPLETED,
                difficulty_instance=prior.difficulty_instance,
                counted_action_total__lte=prior.command_policy_snapshot["min_counted_commands"],
            ).count()
            if accurate_count >= required:
                raise Locked("This scenario is already mastered. Use Review mode instead.")
        if prior.status == SESSION_STATUS_STARTED:
            prior = ScenarioSessionService().abandon(session=prior)
        session = ScenarioSessionService().start_session(
            user=request.user,
            difficulty_instance=prior.difficulty_instance,
            source_entry_point="retry",
            prior_session=prior,
        )
        return Response(session_payload(session), status=201)
