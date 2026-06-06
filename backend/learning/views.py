from rest_framework.response import Response
from rest_framework.views import APIView

from learning.selectors import (
    practice_completion_count_map,
    practice_completion_denominator_map,
    published_foundations,
    published_modules,
)
from learning.serializers import FoundationTopicSerializer, ModuleListSerializer


class FoundationTopicListAPIView(APIView):
    def get(self, request):
        return Response(FoundationTopicSerializer(published_foundations(), many=True).data)


class ModuleListAPIView(APIView):
    def get(self, request):
        modules = list(published_modules())
        module_ids = [module.id for module in modules]
        serializer = ModuleListSerializer(
            modules,
            many=True,
            context={
                "practice_completion_count_map": practice_completion_count_map(
                    user=request.user,
                    module_ids=module_ids,
                ),
                "practice_completion_denominator_map": practice_completion_denominator_map(
                    module_ids=module_ids,
                ),
            },
        )
        return Response(serializer.data)
