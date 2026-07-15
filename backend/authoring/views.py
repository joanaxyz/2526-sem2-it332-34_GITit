from django.shortcuts import get_object_or_404
from drf_spectacular.utils import OpenApiTypes, extend_schema
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.views import APIView

from authoring.models import AuthoringChapter, ContentDefinition
from authoring.selectors import (
    chapter_payload,
    command_form_catalog,
    content_payload,
    visible_content_definitions,
)
from authoring.services import AuthoringChapterService, ContentDefinitionService
from shop.access import can_remix


class CommandFormCatalogAPIView(APIView):
    """Published command forms an author can attach to a level (introduce/reuse)."""

    @extend_schema(responses={200: OpenApiTypes.OBJECT})
    def get(self, request):
        return Response({"results": command_form_catalog()})


class AuthoringChapterListCreateAPIView(APIView):
    @extend_schema(responses={200: OpenApiTypes.OBJECT})
    def get(self, request):
        chapters = AuthoringChapter.objects.filter(owner=request.user)
        return Response({"results": [chapter_payload(row) for row in chapters]})

    @extend_schema(request=OpenApiTypes.OBJECT, responses={200: OpenApiTypes.OBJECT})
    def post(self, request):
        chapter = AuthoringChapterService().create(user=request.user, data=request.data)
        return Response(chapter_payload(chapter), status=201)


class AuthoringChapterDetailAPIView(APIView):
    @extend_schema(request=OpenApiTypes.OBJECT, responses={200: OpenApiTypes.OBJECT})
    def patch(self, request, chapter_id: int):
        chapter = get_object_or_404(AuthoringChapter, id=chapter_id)
        chapter = AuthoringChapterService().update(user=request.user, chapter=chapter, data=request.data)
        return Response(chapter_payload(chapter))

    @extend_schema(request=None, responses={204: None})
    def delete(self, request, chapter_id: int):
        chapter = get_object_or_404(AuthoringChapter, id=chapter_id)
        AuthoringChapterService().delete(user=request.user, chapter=chapter)
        return Response(status=204)


class ContentDefinitionListCreateAPIView(APIView):
    @extend_schema(responses={200: OpenApiTypes.OBJECT})
    def get(self, request):
        kind = request.query_params.get("kind")
        queryset = visible_content_definitions(user=request.user).order_by("-updated_at", "-id")
        if kind:
            queryset = queryset.filter(kind=kind)
        return Response({"results": [content_payload(row, include_definition=False) for row in queryset]})

    @extend_schema(request=OpenApiTypes.OBJECT, responses={200: OpenApiTypes.OBJECT})
    def post(self, request):
        content = ContentDefinitionService().create(user=request.user, data=request.data)
        return Response(content_payload(content), status=201)


class ContentDefinitionDetailAPIView(APIView):
    @extend_schema(responses={200: OpenApiTypes.OBJECT})
    def get(self, request, definition_id: int):
        content = get_object_or_404(visible_content_definitions(user=request.user), id=definition_id)
        return Response(content_payload(content))

    @extend_schema(request=OpenApiTypes.OBJECT, responses={200: OpenApiTypes.OBJECT})
    def patch(self, request, definition_id: int):
        content = ContentDefinition.objects.get(id=definition_id)
        content = ContentDefinitionService().update(user=request.user, content=content, data=request.data)
        return Response(content_payload(content))


class ContentDefinitionValidateAPIView(APIView):
    @extend_schema(request=OpenApiTypes.OBJECT, responses={200: OpenApiTypes.OBJECT})
    def post(self, request, definition_id: int):
        content = ContentDefinition.objects.get(id=definition_id)
        return Response(ContentDefinitionService().validate(user=request.user, content=content))


class ContentDefinitionPublishAPIView(APIView):
    @extend_schema(request=OpenApiTypes.OBJECT, responses={200: OpenApiTypes.OBJECT})
    def post(self, request, definition_id: int):
        content = ContentDefinition.objects.get(id=definition_id)
        content = ContentDefinitionService().publish(user=request.user, content=content)
        return Response(content_payload(content))


class ContentDefinitionTestRunAPIView(APIView):
    @extend_schema(request=OpenApiTypes.OBJECT, responses={200: OpenApiTypes.OBJECT})
    def post(self, request, definition_id: int):
        content = ContentDefinition.objects.get(id=definition_id)
        return Response(ContentDefinitionService().test_run(user=request.user, content=content))


class ContentDefinitionRemixAPIView(APIView):
    @extend_schema(request=OpenApiTypes.OBJECT, responses={200: OpenApiTypes.OBJECT})
    def post(self, request, definition_id: int):
        content = visible_content_definitions(user=request.user).get(id=definition_id)
        if not can_remix(request.user, content):
            raise PermissionDenied("You cannot remix this content definition.")
        clone = ContentDefinitionService().remix(user=request.user, content=content)
        return Response(content_payload(clone), status=201)
