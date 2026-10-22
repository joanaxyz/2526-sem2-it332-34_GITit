from django.urls import path

from tutoring.views import IntroductionCompleteAPIView, TutorChatAPIView

urlpatterns = [
    path("tutoring/chat/", TutorChatAPIView.as_view()),
    path(
        "adventure-tier-runs/<int:run_id>/introduction/complete/",
        IntroductionCompleteAPIView.as_view(),
    ),
]
