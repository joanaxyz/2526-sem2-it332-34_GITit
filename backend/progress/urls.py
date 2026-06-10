from django.urls import path

from progress.views import DashboardSummaryAPIView, WalletSummaryAPIView

urlpatterns = [
    path("dashboard/", DashboardSummaryAPIView.as_view(), name="dashboard-summary"),
    path("wallet/", WalletSummaryAPIView.as_view(), name="wallet-summary"),
]
