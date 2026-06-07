from django.urls import path

from learning.views import FoundationTopicListAPIView, ModuleListAPIView, StoreyListAPIView

urlpatterns = [
    path("foundations/", FoundationTopicListAPIView.as_view(), name="foundation-list"),
    path("storeys/", StoreyListAPIView.as_view(), name="storey-list"),
    path("modules/", ModuleListAPIView.as_view(), name="module-list"),
]
