from django.urls import path

from learning.views import FoundationTopicListAPIView, ModuleListAPIView

urlpatterns = [
    path("foundations/", FoundationTopicListAPIView.as_view(), name="foundation-list"),
    path("modules/", ModuleListAPIView.as_view(), name="module-list"),
]
