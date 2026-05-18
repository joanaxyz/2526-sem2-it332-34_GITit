from rest_framework.response import Response
from rest_framework.views import APIView

from scenarios.models import ScenarioSession
from scenarios.selectors import get_difficulty_instance, scenario_queryset, scenario_status_payload
from scenarios.serializers import CommandSubmitSerializer, ScenarioStartSerializer, session_payload
from scenarios.services import CommandProcessingService, ScenarioSessionService


class LessonScenarioListAPIView(APIView):
    def get(self, request, lesson_id: int):
        scenarios = scenario_queryset().filter(lesson_id=lesson_id)
        return Response([scenario_status_payload(user=request.user, scenario=s) for s in scenarios])


class UnitScenarioListAPIView(APIView):
    def get(self, request, unit_id: int):
        scenarios = scenario_queryset().filter(learning_unit_id=unit_id)
        return Response([scenario_status_payload(user=request.user, scenario=s) for s in scenarios])


class ScenarioSessionStartAPIView(APIView):
    def post(self, request):
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
        return Response(session_payload(session), status=201)


class ScenarioSessionDetailAPIView(APIView):
    def get(self, request, session_id: int):
        session = ScenarioSession.objects.select_related(
            "scenario",
            "learning_unit",
            "difficulty_instance",
            "variant",
        ).get(id=session_id, user=request.user)
        return Response(session_payload(session))


class CommandSubmitAPIView(APIView):
    def post(self, request, session_id: int):
        serializer = CommandSubmitSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        session = ScenarioSession.objects.select_related(
            "scenario",
            "learning_unit",
            "difficulty_instance",
            "difficulty_instance__target_rule",
            "variant",
        ).get(id=session_id, user=request.user)
        result = CommandProcessingService().submit_command(
            session=session,
            command=serializer.validated_data["command"],
        )
        return Response(
            {
                "session": session_payload(result["session"]),
                "step": {
                    "id": result["step"].id,
                    "terminal_output": result["terminal_output"],
                    "evaluation_result": result["evaluation_result"],
                    "command_classification": result["command_classification"],
                    "contextual_feedback": result["contextual_feedback"],
                },
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
        ).get(id=session_id, user=request.user)
        session = ScenarioSessionService().start_session(
            user=request.user,
            difficulty_instance=prior.difficulty_instance,
            source_entry_point="retry",
            prior_session=prior,
        )
        return Response(session_payload(session), status=201)
