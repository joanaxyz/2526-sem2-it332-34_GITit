from django.urls import path

from tutoring.views import IntroductionCompleteAPIView

urlpatterns = [
    path("adventure-tier-runs/<int:run_id>/introduction/complete/", IntroductionCompleteAPIView.as_view()),
]
