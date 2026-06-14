from django.shortcuts import get_object_or_404
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.views import APIView

from authoring.models import AuthoringStorey, ContentDefinition
from authoring.selectors import content_payload, storey_payload, visible_content_definitions
from authoring.services import AuthoringStoreyService, ContentDefinitionService
from marketplace.access import can_remix


class AuthoringStoreyListCreateAPIView(APIView):
    def get(self, request):
        storeys = AuthoringStorey.objects.filter(owner=request.user)
        return Response({"results": [storey_payload(row) for row in storeys]})

    def post(self, request):
        storey = AuthoringStoreyService().create(user=request.user, data=request.data)
        return Response(storey_payload(storey), status=201)


class AuthoringStoreyDetailAPIView(APIView):
    def patch(self, request, storey_id: int):
        storey = get_object_or_404(AuthoringStorey, id=storey_id)
        storey = AuthoringStoreyService().update(user=request.user, storey=storey, data=request.data)
        return Response(storey_payload(storey))

    def delete(self, request, storey_id: int):
        storey = get_object_or_404(AuthoringStorey, id=storey_id)
        AuthoringStoreyService().delete(user=request.user, storey=storey)
        return Response(status=204)


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
