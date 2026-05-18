from rest_framework.response import Response
from rest_framework.views import APIView

from review.services import ReviewModeService
from scenarios.selectors import get_difficulty_instance
from scenarios.serializers import CommandSubmitSerializer, ScenarioStartSerializer, session_payload
from scenarios.views import CommandSubmitAPIView


class ReviewSessionStartAPIView(APIView):
    def post(self, request):
        serializer = ScenarioStartSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        difficulty = get_difficulty_instance(serializer.validated_data["difficulty_instance_id"])
        session = ReviewModeService().start_review_session(
            user=request.user,
            difficulty_instance=difficulty,
        )
        return Response(session_payload(session), status=201)


class ReviewCommandSubmitAPIView(CommandSubmitAPIView):
    serializer_class = CommandSubmitSerializer
