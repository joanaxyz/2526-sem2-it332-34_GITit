from django.urls import path

from challenges.views import (
    ChallengeCommandSubmitAPIView,
    ChallengeRetryAPIView,
    ChallengeRunDetailAPIView,
    ChallengeRunStartAPIView,
    ChallengeWorkspaceFileAPIView,
)

urlpatterns = [
    path("challenge-trials/<int:trial_id>/runs/", ChallengeRunStartAPIView.as_view(), name="challenge-run-start"),
    path("challenge-runs/<int:run_id>/", ChallengeRunDetailAPIView.as_view(), name="challenge-run-detail"),
    path("challenge-runs/<int:run_id>/submit-command/", ChallengeCommandSubmitAPIView.as_view(), name="challenge-run-submit-command"),
    path("challenge-runs/<int:run_id>/files/", ChallengeWorkspaceFileAPIView.as_view(), name="challenge-run-files"),
    path("challenge-runs/<int:run_id>/retry/", ChallengeRetryAPIView.as_view(), name="challenge-run-retry"),
]
