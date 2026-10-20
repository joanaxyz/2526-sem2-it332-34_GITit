from django.urls import path

from adventures.views import (
    AdventureLevelTierCommandSubmitAPIView,
    AdventureLevelTierRetryAPIView,
    AdventureLevelTierRunDetailAPIView,
    AdventureLevelTierRunStartAPIView,
    AdventureLevelTierWorkspaceFileAPIView,
)

urlpatterns = [
    path(
        "adventure-level-tiers/<int:tier_id>/runs/",
        AdventureLevelTierRunStartAPIView.as_view(),
        name="adventure-level-tier-run-start",
    ),
    path(
        "adventure-tier-runs/<int:run_id>/",
        AdventureLevelTierRunDetailAPIView.as_view(),
        name="adventure-tier-run-detail",
    ),
    path(
        "adventure-tier-runs/<int:run_id>/submit-command/",
        AdventureLevelTierCommandSubmitAPIView.as_view(),
        name="adventure-tier-run-submit-command",
    ),
    path(
        "adventure-tier-runs/<int:run_id>/files/",
        AdventureLevelTierWorkspaceFileAPIView.as_view(),
        name="adventure-tier-run-files",
    ),
    path(
        "adventure-tier-runs/<int:run_id>/retry/",
        AdventureLevelTierRetryAPIView.as_view(),
        name="adventure-tier-run-retry",
    ),
]
