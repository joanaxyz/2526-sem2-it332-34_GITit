from django.urls import path

from learning.views import (
    LessonDetailAPIView,
    OrientationCompleteAPIView,
    OrientationLessonSessionCommandAPIView,
    OrientationLessonSessionDetailAPIView,
    OrientationLessonSessionResetAPIView,
    OrientationLessonSessionStartAPIView,
    OrientationStatusAPIView,
    UnitListAPIView,
)

urlpatterns = [
    path("modules/", UnitListAPIView.as_view(), name="module-list"),
    path("lessons/<int:lesson_id>/", LessonDetailAPIView.as_view(), name="lesson-detail"),
    path("orientation/status/", OrientationStatusAPIView.as_view(), name="orientation-status"),
    path(
        "orientation/<int:lesson_id>/complete/",
        OrientationCompleteAPIView.as_view(),
        name="orientation-complete",
    ),
    path(
        "orientation/<int:lesson_id>/sessions/",
        OrientationLessonSessionStartAPIView.as_view(),
        name="orientation-session-start",
    ),
    path(
        "orientation/sessions/<int:session_id>/",
        OrientationLessonSessionDetailAPIView.as_view(),
        name="orientation-session-detail",
    ),
    path(
        "orientation/sessions/<int:session_id>/commands/",
        OrientationLessonSessionCommandAPIView.as_view(),
        name="orientation-session-command",
    ),
    path(
        "orientation/sessions/<int:session_id>/reset/",
        OrientationLessonSessionResetAPIView.as_view(),
        name="orientation-session-reset",
    ),
]
