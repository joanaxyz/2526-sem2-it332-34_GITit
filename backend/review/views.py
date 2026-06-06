from rest_framework.response import Response
from rest_framework.views import APIView

from review.services import ReviewModeService
from scenarios.models import PracticeKind
from scenarios.selectors import get_command_drill, get_workflow_level
from scenarios.serializers import CommandSubmitSerializer, PracticeStartSerializer, session_payload
from scenarios.views import CommandSubmitAPIView


class ReviewSessionStartAPIView(APIView):
    def post(self, request):
        serializer = PracticeStartSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        problem = (
            get_command_drill(data["command_drill_id"])
            if data["problem_type"] == PracticeKind.COMMAND_DRILL
            else get_workflow_level(data["workflow_level_id"])
        )
        session = ReviewModeService().start_review_session(user=request.user, problem=problem)
        return Response(session_payload(session), status=201)


class ReviewCommandSubmitAPIView(CommandSubmitAPIView):
    serializer_class = CommandSubmitSerializer
