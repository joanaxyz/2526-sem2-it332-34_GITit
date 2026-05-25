from django.shortcuts import get_object_or_404
from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from rest_framework.views import APIView

from learning.models import Lesson
from learning.selectors import (
    orientation_progress_map,
    practice_completion_count_map,
    practice_completion_denominator_map,
    published_lesson,
    published_units,
)
from learning.serializers import (
    LessonDetailSerializer,
    OrientationCompleteSerializer,
    OrientationProgressSerializer,
    UnitListSerializer,
)
from learning.services import OrientationService


class UnitListAPIView(APIView):
    def get(self, request):
        units = list(published_units(user=request.user))
        unit_ids = [unit.id for unit in units]
        serializer = UnitListSerializer(
            units,
            many=True,
            context={
                "practice_completion_count_map": practice_completion_count_map(
                    user=request.user,
                    unit_ids=unit_ids,
                ),
                "practice_completion_denominator_map": practice_completion_denominator_map(
                    unit_ids=unit_ids,
                ),
            },
        )
        return Response(serializer.data)


class LessonDetailAPIView(APIView):
    def get(self, request, lesson_id: int):
        lesson = published_lesson(lesson_id)
        if not lesson.unit.is_orientation:
            raise NotFound()
        serializer = LessonDetailSerializer(
            lesson,
            context={"orientation_progress_map": orientation_progress_map(request.user)},
        )
        return Response(serializer.data)


class OrientationStatusAPIView(APIView):
    def get(self, request):
        service = OrientationService()
        progress = orientation_progress_map(request.user)
        payload = []
        for lesson in service.orientation_lessons():
            item = progress.get(lesson.id)
            if item:
                payload.append(OrientationProgressSerializer(item).data)
            else:
                payload.append(
                    {
                        "lesson_id": lesson.id,
                        "highest_step_seen": 0,
                        "completed_at": None,
                        "is_complete": False,
                    }
                )
        return Response({"orientation_complete": service.is_orientation_complete(request.user), "lessons": payload})


class OrientationCompleteAPIView(APIView):
    def post(self, request, lesson_id: int):
        serializer = OrientationCompleteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        lesson = get_object_or_404(
            Lesson.objects.select_related("unit"),
            id=lesson_id,
            is_published=True,
            unit__is_published=True,
        )
        if not lesson.unit.is_orientation:
            raise NotFound()
        progress = OrientationService().mark_complete(
            user=request.user,
            lesson=lesson,
            highest_step_seen=serializer.validated_data["highest_step_seen"],
        )
        return Response(OrientationProgressSerializer(progress).data)
