from django.urls import path

from learning.views import (
    LessonDetailAPIView,
    OrientationCompleteAPIView,
    OrientationStatusAPIView,
    UnitListAPIView,
)

urlpatterns = [
    path("modules/", UnitListAPIView.as_view(), name="module-list"),
    path("units/", UnitListAPIView.as_view(), name="unit-list"),
    path("lessons/<int:lesson_id>/", LessonDetailAPIView.as_view(), name="lesson-detail"),
    path("orientation/status/", OrientationStatusAPIView.as_view(), name="orientation-status"),
    path(
        "orientation/<int:lesson_id>/complete/",
        OrientationCompleteAPIView.as_view(),
        name="orientation-complete",
    ),
]
