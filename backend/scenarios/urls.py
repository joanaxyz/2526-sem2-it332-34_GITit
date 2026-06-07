from django.urls import path

from scenarios.views import (
    CommandSubmitAPIView,
    CommandUsagePreviewAPIView,
    ModuleContentAPIView,
    PracticeRetryAPIView,
    PracticeSessionAbandonAPIView,
    PracticeSessionDetailAPIView,
    PracticeSessionStartAPIView,
    StoreyContentAPIView,
    WorkspaceFileCreateAPIView,
)

urlpatterns = [
    path("storeys/<int:storey_id>/content/", StoreyContentAPIView.as_view(), name="storey-content"),
    path("modules/<int:module_id>/content/", ModuleContentAPIView.as_view(), name="module-content"),
    path("command-usages/<int:usage_id>/preview/", CommandUsagePreviewAPIView.as_view(), name="command-usage-preview"),
    path("sessions/", PracticeSessionStartAPIView.as_view(), name="practice-session-start"),
    path("sessions/<int:session_id>/", PracticeSessionDetailAPIView.as_view(), name="practice-session"),
    path("sessions/<int:session_id>/commands/", CommandSubmitAPIView.as_view(), name="practice-command"),
    path("sessions/<int:session_id>/files/", WorkspaceFileCreateAPIView.as_view(), name="practice-workspace-file"),
    path("sessions/<int:session_id>/abandon/", PracticeSessionAbandonAPIView.as_view(), name="practice-abandon"),
    path("sessions/<int:session_id>/retry/", PracticeRetryAPIView.as_view(), name="practice-retry"),
]
