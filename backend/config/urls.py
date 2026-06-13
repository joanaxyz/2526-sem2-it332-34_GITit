from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

from adventures.views import (
    AdventureRunDetailAPIView,
    AdventureRunFinishAPIView,
    AdventureRunSubmitCommandAPIView,
    AdventureRunUseHintAPIView,
    AdventureWorkspaceFileAPIView,
    CommandAdventureRunStartAPIView,
)
from challenges.views import (
    ChallengeCommandSubmitAPIView,
    ChallengeRetryAPIView,
    ChallengeRunDetailAPIView,
    ChallengeRunFinishAPIView,
    ChallengeRunStartAPIView,
    ChallengeWorkspaceFileAPIView,
)
from common.views import HealthAPIView
from curriculum.views import (
    CommandFormPreviewAPIView,
    LearnedSkillsAPIView,
    StoreyBookAPIView,
    StoreyContentAPIView,
    StoreyContentOverviewAPIView,
    StoreyListAPIView,
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/health/", HealthAPIView.as_view(), name="health"),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/auth/", include("accounts.urls")),
    path("api/progress/", include("progress.urls")),
    path("api/storeys/", StoreyListAPIView.as_view(), name="storeys"),
    path("api/storeys/<int:storey_id>/content/", StoreyContentAPIView.as_view(), name="storey-content"),
    path("api/storeys/<int:storey_id>/overview/", StoreyContentOverviewAPIView.as_view(), name="storey-overview"),
    path("api/storeys/<int:storey_id>/book/", StoreyBookAPIView.as_view(), name="storey-book"),
    path("api/skills/learned/", LearnedSkillsAPIView.as_view(), name="skills-learned"),
    path("api/command-forms/<int:form_id>/preview/", CommandFormPreviewAPIView.as_view(), name="command-form-preview"),
    path("api/command-adventures/<slug:adventure_slug>/runs/", CommandAdventureRunStartAPIView.as_view(), name="adventure-run-start"),
    path("api/adventure-runs/<int:run_id>/", AdventureRunDetailAPIView.as_view(), name="adventure-run-detail"),
    path("api/adventure-runs/<int:run_id>/submit-command/", AdventureRunSubmitCommandAPIView.as_view(), name="adventure-run-submit-command"),
    path("api/adventure-runs/<int:run_id>/use-hint/", AdventureRunUseHintAPIView.as_view(), name="adventure-run-use-hint"),
    path("api/adventure-runs/<int:run_id>/files/", AdventureWorkspaceFileAPIView.as_view(), name="adventure-run-files"),
    path("api/adventure-runs/<int:run_id>/finish/", AdventureRunFinishAPIView.as_view(), name="adventure-run-finish"),
    path("api/challenge-levels/<int:level_id>/runs/", ChallengeRunStartAPIView.as_view(), name="challenge-run-start"),
    path("api/challenge-runs/<int:run_id>/", ChallengeRunDetailAPIView.as_view(), name="challenge-run-detail"),
    path("api/challenge-runs/<int:run_id>/submit-command/", ChallengeCommandSubmitAPIView.as_view(), name="challenge-run-submit-command"),
    path("api/challenge-runs/<int:run_id>/files/", ChallengeWorkspaceFileAPIView.as_view(), name="challenge-run-files"),
    path("api/challenge-runs/<int:run_id>/finish/", ChallengeRunFinishAPIView.as_view(), name="challenge-run-finish"),
    path("api/challenge-runs/<int:run_id>/retry/", ChallengeRetryAPIView.as_view(), name="challenge-run-retry"),
]

# Dev media serving. In production object storage (Supabase/S3) serves these.
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
