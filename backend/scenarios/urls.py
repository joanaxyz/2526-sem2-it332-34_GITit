from django.urls import path

from scenarios.views import (
    CommandSubmitAPIView,
    ScenarioRetryAPIView,
    ScenarioSessionAbandonAPIView,
    ScenarioSessionDetailAPIView,
    ScenarioSessionStartAPIView,
    SkillFocusDemoCommandAPIView,
    SkillFocusDetailAPIView,
    UnitScenarioListAPIView,
    UnitScenarioSummaryAPIView,
)

urlpatterns = [
    path(
        "skill-focus/<slug:slug>/demo/commands/",
        SkillFocusDemoCommandAPIView.as_view(),
        name="skill-focus-demo-command",
    ),
    path("skill-focus/<slug:slug>/", SkillFocusDetailAPIView.as_view(), name="skill-focus-detail"),
    path("modules/summary/", UnitScenarioSummaryAPIView.as_view(), name="module-scenario-summary"),
    path("modules/<int:unit_id>/", UnitScenarioListAPIView.as_view(), name="module-scenarios"),
    path("units/summary/", UnitScenarioSummaryAPIView.as_view(), name="unit-scenario-summary"),
    path("units/<int:unit_id>/", UnitScenarioListAPIView.as_view(), name="unit-scenarios"),
    path("sessions/", ScenarioSessionStartAPIView.as_view(), name="scenario-session-start"),
    path("sessions/<int:session_id>/", ScenarioSessionDetailAPIView.as_view(), name="scenario-session"),
    path(
        "sessions/<int:session_id>/commands/",
        CommandSubmitAPIView.as_view(),
        name="scenario-command",
    ),
    path(
        "sessions/<int:session_id>/abandon/",
        ScenarioSessionAbandonAPIView.as_view(),
        name="scenario-abandon",
    ),
    path("sessions/<int:session_id>/retry/", ScenarioRetryAPIView.as_view(), name="scenario-retry"),
]
