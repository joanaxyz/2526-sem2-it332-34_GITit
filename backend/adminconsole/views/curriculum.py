"""Story and chapter HTTP adapters for the admin console."""

from drf_spectacular.utils import extend_schema
from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from rest_framework.views import APIView

from adminconsole.selectors import (
    admin_chapter_list_payload,
    admin_story_detail_payload,
    admin_story_list_payload,
    chapter_payload,
    find_admin_chapter,
    find_admin_story,
    story_payload,
)
from adminconsole.serializers import (
    AdminChapterCreateRequestSerializer,
    AdminChapterListQuerySerializer,
    AdminChapterListResponseSerializer,
    AdminChapterSerializer,
    AdminChapterUpdateRequestSerializer,
    AdminStoryCreateRequestSerializer,
    AdminStoryListResponseSerializer,
    AdminStorySerializer,
    AdminStoryUpdateRequestSerializer,
)
from adminconsole.services import AdminCurriculumService
from common.permissions import IsStaff


class AdminStoryListCreateAPIView(APIView):
    permission_classes = [IsStaff]

    @extend_schema(responses={200: AdminStoryListResponseSerializer})
    def get(self, request):
        return Response(admin_story_list_payload())

    @extend_schema(
        request=AdminStoryCreateRequestSerializer,
        responses={201: AdminStorySerializer},
    )
    def post(self, request):
        serializer = AdminStoryCreateRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        story = AdminCurriculumService().create_story(
            actor=request.user,
            data=serializer.validated_data,
        )
        return Response(story_payload(story, 0), status=201)


class AdminStoryDetailAPIView(APIView):
    permission_classes = [IsStaff]

    @extend_schema(
        request=AdminStoryUpdateRequestSerializer,
        responses={200: AdminStorySerializer},
    )
    def patch(self, request, story_id: int):
        story = find_admin_story(story_id)
        if story is None:
            raise NotFound("Story not found.")
        serializer = AdminStoryUpdateRequestSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        story = AdminCurriculumService().update_story(
            actor=request.user,
            story=story,
            data=serializer.validated_data,
        )
        return Response(admin_story_detail_payload(story))


class AdminChapterListAPIView(APIView):
    permission_classes = [IsStaff]

    @extend_schema(
        parameters=[AdminChapterListQuerySerializer],
        responses={200: AdminChapterListResponseSerializer},
    )
    def get(self, request):
        query_serializer = AdminChapterListQuerySerializer(data=request.query_params)
        query_serializer.is_valid(raise_exception=True)
        return Response(
            admin_chapter_list_payload(
                story_id=query_serializer.validated_data.get("story"),
            )
        )

    @extend_schema(
        request=AdminChapterCreateRequestSerializer,
        responses={201: AdminChapterSerializer},
    )
    def post(self, request):
        serializer = AdminChapterCreateRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        chapter = AdminCurriculumService().create_chapter(
            actor=request.user,
            data=serializer.validated_data,
        )
        return Response(chapter_payload(chapter), status=201)


class AdminChapterDetailAPIView(APIView):
    permission_classes = [IsStaff]

    @extend_schema(
        request=AdminChapterUpdateRequestSerializer,
        responses={200: AdminChapterSerializer},
    )
    def patch(self, request, chapter_id: int):
        chapter = find_admin_chapter(chapter_id)
        if chapter is None:
            raise NotFound("Chapter not found.")
        serializer = AdminChapterUpdateRequestSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        chapter = AdminCurriculumService().update_chapter(
            actor=request.user,
            chapter=chapter,
            data=serializer.validated_data,
        )
        return Response(chapter_payload(chapter))
