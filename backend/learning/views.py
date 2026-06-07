from rest_framework.response import Response
from rest_framework.views import APIView

from learning.selectors import (
    published_foundations,
    published_storeys,
    storey_completion_count_map,
    storey_completion_denominator_map,
)
from learning.serializers import FoundationTopicSerializer, StoreyListSerializer


class FoundationTopicListAPIView(APIView):
    def get(self, request):
        return Response(FoundationTopicSerializer(published_foundations(), many=True).data)


class StoreyListAPIView(APIView):
    def get(self, request):
        storeys = list(published_storeys())
        storey_ids = [storey.id for storey in storeys]
        serializer = StoreyListSerializer(
            storeys,
            many=True,
            context={
                "storey_completion_count_map": storey_completion_count_map(
                    user=request.user,
                    storey_ids=storey_ids,
                ),
                "storey_completion_denominator_map": storey_completion_denominator_map(
                    storey_ids=storey_ids,
                ),
            },
        )
        return Response(serializer.data)


ModuleListAPIView = StoreyListAPIView
