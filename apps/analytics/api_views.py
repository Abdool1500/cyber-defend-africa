from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.permissions import IsAdminRole

from .serializers import ImpactDashboardSerializer, PlatformAnalyticsSerializer
from .services.impact_stats import get_impact_dashboard_data
from .services.platform_stats import get_platform_analytics


class PlatformAnalyticsAPIView(APIView):
    """Admin-only — same data as the Management Analytics Dashboard
    (16.J), just as JSON. Read-only by construction: no POST/PUT/DELETE
    exists because there's no underlying model to write to."""

    permission_classes = [IsAdminRole]
    serializer_class = PlatformAnalyticsSerializer

    def get(self, request):
        serializer = PlatformAnalyticsSerializer(get_platform_analytics())
        return Response(serializer.data)


class ImpactDashboardAPIView(APIView):
    """Admin-only — same data as the Impact Dashboard (16.K), split into
    `computed`/`self_reported` in the response body exactly like the
    template, so API consumers can't conflate measured and self-reported
    figures either."""

    permission_classes = [IsAdminRole]
    serializer_class = ImpactDashboardSerializer

    def get(self, request):
        serializer = ImpactDashboardSerializer(get_impact_dashboard_data())
        return Response(serializer.data)
