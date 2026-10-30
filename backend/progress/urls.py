from django.urls import path

from progress.views import (
    DashboardSummaryAPIView,
    PerformanceSummaryAPIView,
    StatsActivityAPIView,
    StatsSummaryAPIView,
    WalletSummaryAPIView,
)

urlpatterns = [
    path("dashboard/", DashboardSummaryAPIView.as_view(), name="dashboard-summary"),
    path("stats/", StatsSummaryAPIView.as_view(), name="stats-summary"),
    path("stats/activity/", StatsActivityAPIView.as_view(), name="stats-activity"),
    path("performance/", PerformanceSummaryAPIView.as_view(), name="performance-summary"),
    path("wallet/", WalletSummaryAPIView.as_view(), name="wallet-summary"),
]
