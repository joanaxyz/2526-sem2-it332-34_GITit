from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView

from authoring.models import ContentDefinition
from authoring.selectors import content_payload, visible_content_definitions
from authoring.services import ContentDefinitionService
from marketplace.access import can_remix
from rest_framework.exceptions import PermissionDenied


class ContentDefinitionListCreateAPIView(APIView):
    def get(self, request):
        kind = request.query_params.get("kind")
        queryset = visible_content_definitions(user=request.user).order_by("-updated_at", "-id")
        if kind:
            queryset = queryset.filter(kind=kind)
        return Response({"results": [content_payload(row, include_definition=False) for row in queryset]})

    def post(self, request):
        content = ContentDefinitionService().create(user=request.user, data=request.data)
        return Response(content_payload(content), status=201)


class ContentDefinitionDetailAPIView(APIView):
    def get(self, request, definition_id: int):
        content = get_object_or_404(visible_content_definitions(user=request.user), id=definition_id)
        return Response(content_payload(content))

    def patch(self, request, definition_id: int):
        content = ContentDefinition.objects.get(id=definition_id)
        content = ContentDefinitionService().update(user=request.user, content=content, data=request.data)
        return Response(content_payload(content))


class ContentDefinitionValidateAPIView(APIView):
    def post(self, request, definition_id: int):
        content = ContentDefinition.objects.get(id=definition_id)
        return Response(ContentDefinitionService().validate(user=request.user, content=content))


class ContentDefinitionPublishAPIView(APIView):
    def post(self, request, definition_id: int):
        content = ContentDefinition.objects.get(id=definition_id)
        content = ContentDefinitionService().publish(user=request.user, content=content)
        return Response(content_payload(content))


class ContentDefinitionTestRunAPIView(APIView):
    def post(self, request, definition_id: int):
        content = ContentDefinition.objects.get(id=definition_id)
        return Response(ContentDefinitionService().test_run(user=request.user, content=content))


class ContentDefinitionRemixAPIView(APIView):
    def post(self, request, definition_id: int):
        content = visible_content_definitions(user=request.user).get(id=definition_id)
        if not can_remix(request.user, content):
            raise PermissionDenied("You cannot remix this content definition.")
        clone = ContentDefinitionService().remix(user=request.user, content=content)
        return Response(content_payload(clone), status=201)
