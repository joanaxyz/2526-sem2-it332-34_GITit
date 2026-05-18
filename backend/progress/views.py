from rest_framework.response import Response
from rest_framework.views import APIView

from progress.services import MetricsService


class DashboardSummaryAPIView(APIView):
    def get(self, request):
        return Response(MetricsService().dashboard_summary(user=request.user))
