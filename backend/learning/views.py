from rest_framework.response import Response
from rest_framework.views import APIView

from learning.selectors import (
    published_foundations,
    published_towers,
    tower_completion_count_map,
    tower_completion_denominator_map,
)
from learning.serializers import FoundationTopicSerializer, TowerListSerializer


class FoundationTopicListAPIView(APIView):
    def get(self, request):
        return Response(FoundationTopicSerializer(published_foundations(), many=True).data)


class TowerListAPIView(APIView):
    def get(self, request):
        towers = list(published_towers())
        tower_ids = [tower.id for tower in towers]
        serializer = TowerListSerializer(
            towers,
            many=True,
            context={
                "tower_completion_count_map": tower_completion_count_map(
                    user=request.user,
                    tower_ids=tower_ids,
                ),
                "tower_completion_denominator_map": tower_completion_denominator_map(
                    tower_ids=tower_ids,
                ),
            },
        )
        return Response(serializer.data)


ModuleListAPIView = TowerListAPIView
