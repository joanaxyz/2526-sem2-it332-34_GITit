from rest_framework.response import Response
from rest_framework.views import APIView

from progress.services import MetricsService
from progress.wallet import WalletService


class DashboardSummaryAPIView(APIView):
    def get(self, request):
        return Response(MetricsService().dashboard_summary(user=request.user))


class StatsSummaryAPIView(APIView):
    def get(self, request):
        return Response(MetricsService().stats_summary(user=request.user))


class WalletSummaryAPIView(APIView):
    def get(self, request):
        return Response(WalletService().summary(user=request.user))
