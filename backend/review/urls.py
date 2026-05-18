from django.urls import path

from review.views import ReviewCommandSubmitAPIView, ReviewSessionStartAPIView

urlpatterns = [
    path("sessions/", ReviewSessionStartAPIView.as_view(), name="review-session-start"),
    path(
        "sessions/<int:session_id>/commands/",
        ReviewCommandSubmitAPIView.as_view(),
        name="review-command",
    ),
]
