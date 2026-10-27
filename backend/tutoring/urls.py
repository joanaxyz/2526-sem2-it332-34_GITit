from django.urls import path

from tutoring.views import IntroductionCompleteAPIView, TipDismissAPIView, TutorChatAPIView

urlpatterns = [
    path("tutoring/chat/", TutorChatAPIView.as_view()),
    path("tutoring/tips/dismiss/", TipDismissAPIView.as_view()),
    path(
        "adventure-tier-runs/<int:run_id>/introduction/complete/",
        IntroductionCompleteAPIView.as_view(),
    ),
]
