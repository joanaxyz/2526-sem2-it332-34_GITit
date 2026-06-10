from rest_framework.response import Response
from rest_framework.views import APIView

from common.performance import timing
from curriculum.selectors import (
    get_command_form,
    published_foundations,
    published_storeys,
    storey_book,
    storey_completion_count_map,
    storey_completion_denominator_map,
    storey_content_page,
)
from curriculum.serializers import FoundationTopicSerializer, StoreyListSerializer


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


class StoreyContentAPIView(APIView):
    def get(self, request, storey_id: int):
        section = request.query_params.get("section") or "command_skills"
        cursor = _int_param(request.query_params.get("cursor"))
        limit = _int_param(request.query_params.get("limit")) or 8
        with timing("curriculum.storey_content", storey_id=storey_id, section=section):
            return Response(
                storey_content_page(
                    user=request.user,
                    storey_id=storey_id,
                    section=section,
                    cursor=cursor,
                    limit=limit,
                )
            )


class StoreyBookAPIView(APIView):
    def get(self, request, storey_id: int):
        with timing("curriculum.storey_book", storey_id=storey_id):
            book = storey_book(storey_id=storey_id)
        if book is None:
            return Response({"detail": "Storey not found."}, status=404)
        return Response(book)


class CommandFormPreviewAPIView(APIView):
    def get(self, request, form_id: int):
        form = get_command_form(form_id)
        return Response(
            {
                "id": form.id,
                "slug": form.slug,
                "usage_form": form.usage_form,
                "label": form.label,
                "summary": form.summary,
                "skill": {
                    "id": form.topic_id,
                    "slug": form.topic.slug,
                    "base_command": form.topic.base_command,
                    "title": form.topic.title,
                },
                "command_preview": form.command_preview or form.topic.command_preview or {},
            }
        )


def _int_param(value: str | None) -> int | None:
    try:
        return int(value) if value is not None else None
    except (TypeError, ValueError):
        return None
