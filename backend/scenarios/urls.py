from django.urls import path

from scenarios.views import (
    CommandSubmitAPIView,
    WorkspaceFileCreateAPIView,
    ScenarioRetryAPIView,
    ScenarioSessionAbandonAPIView,
    ScenarioSessionDetailAPIView,
    ScenarioSessionStartAPIView,
    SkillFocusDemoCommandAPIView,
    SkillFocusDetailAPIView,
    ModuleScenarioListAPIView,
    ModuleScenarioSummaryAPIView,
)

urlpatterns = [
    path(
        "skill-focus/<slug:slug>/demo/commands/",
        SkillFocusDemoCommandAPIView.as_view(),
        name="skill-focus-demo-command",
    ),
    path("skill-focus/<slug:slug>/", SkillFocusDetailAPIView.as_view(), name="skill-focus-detail"),
    path("modules/summary/", ModuleScenarioSummaryAPIView.as_view(), name="module-scenario-summary"),
    path("modules/<int:module_id>/", ModuleScenarioListAPIView.as_view(), name="module-scenarios"),
    path("sessions/", ScenarioSessionStartAPIView.as_view(), name="scenario-session-start"),
    path("sessions/<int:session_id>/", ScenarioSessionDetailAPIView.as_view(), name="scenario-session"),
    path(
        "sessions/<int:session_id>/commands/",
        CommandSubmitAPIView.as_view(),
        name="scenario-command",
    ),
    path(
        "sessions/<int:session_id>/files/",
        WorkspaceFileCreateAPIView.as_view(),
        name="scenario-workspace-file",
    ),
    path(
        "sessions/<int:session_id>/abandon/",
        ScenarioSessionAbandonAPIView.as_view(),
        name="scenario-abandon",
    ),
    path("sessions/<int:session_id>/retry/", ScenarioRetryAPIView.as_view(), name="scenario-retry"),
]
