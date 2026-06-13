from django.urls import path

from authoring.views import (
    ContentDefinitionDetailAPIView,
    ContentDefinitionListCreateAPIView,
    ContentDefinitionPublishAPIView,
    ContentDefinitionRemixAPIView,
    ContentDefinitionTestRunAPIView,
    ContentDefinitionValidateAPIView,
)

urlpatterns = [
    path("content-definitions/", ContentDefinitionListCreateAPIView.as_view(), name="content-definition-list"),
    path("content-definitions/<int:definition_id>/", ContentDefinitionDetailAPIView.as_view(), name="content-definition-detail"),
    path("content-definitions/<int:definition_id>/validate/", ContentDefinitionValidateAPIView.as_view(), name="content-definition-validate"),
    path("content-definitions/<int:definition_id>/publish/", ContentDefinitionPublishAPIView.as_view(), name="content-definition-publish"),
    path("content-definitions/<int:definition_id>/test-run/", ContentDefinitionTestRunAPIView.as_view(), name="content-definition-test-run"),
    path("content-definitions/<int:definition_id>/remix/", ContentDefinitionRemixAPIView.as_view(), name="content-definition-remix"),
]
