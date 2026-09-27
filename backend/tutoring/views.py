from django.db import transaction
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema
from rest_framework.response import Response
from rest_framework.views import APIView

from adventures.models import AdventureLevelTierRun
from players.services import get_or_create_player
from tutoring.openapi import IntroductionCompleteResponseSerializer
from tutoring.payloads import tutor_payload
from tutoring.serializers import IntroductionCompleteSerializer
from tutoring.services.introductions import complete_introduction


def locked_run(request, run_id):
    return get_object_or_404(
        AdventureLevelTierRun.objects.select_for_update(of=("self",)).select_related(
            "current_wave", "selected_variant",
        ), pk=run_id, player=get_or_create_player(request.user),
    )


class IntroductionCompleteAPIView(APIView):
    throttle_scope = "command_submit"

    @extend_schema(
        operation_id="command_introduction_complete",
        request=IntroductionCompleteSerializer, responses={200: IntroductionCompleteResponseSerializer},
    )
    @transaction.atomic
    def post(self, request, run_id):
        serializer = IntroductionCompleteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        run = locked_run(request, run_id)
        complete_introduction(run, serializer.validated_data["token"])
        return Response({"tutor": tutor_payload(run)})
