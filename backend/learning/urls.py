from django.urls import path

from learning.views import FoundationTopicListAPIView, ModuleListAPIView, TowerListAPIView

urlpatterns = [
    path("foundations/", FoundationTopicListAPIView.as_view(), name="foundation-list"),
    path("towers/", TowerListAPIView.as_view(), name="tower-list"),
    path("modules/", ModuleListAPIView.as_view(), name="module-list"),
]
