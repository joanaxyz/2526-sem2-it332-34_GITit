from django.urls import path

from progress.views import DashboardSummaryAPIView

urlpatterns = [
    path("dashboard/", DashboardSummaryAPIView.as_view(), name="dashboard-summary"),
]
