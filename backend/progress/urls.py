from django.urls import path

from progress.views import DashboardSummaryAPIView, StatsSummaryAPIView, WalletSummaryAPIView

urlpatterns = [
    path("dashboard/", DashboardSummaryAPIView.as_view(), name="dashboard-summary"),
    path("stats/", StatsSummaryAPIView.as_view(), name="stats-summary"),
    path("wallet/", WalletSummaryAPIView.as_view(), name="wallet-summary"),
]
