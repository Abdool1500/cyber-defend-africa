from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.permissions import IsAdminRole
from apps.analytics.serializers import EmploymentSummarySerializer
from apps.analytics.services.employment_stats import get_employment_summary


class EmploymentSummaryAPIView(APIView):
    """Admin-only, aggregate-only — same data as the management-facing
    Employment Outcomes summary page. Deliberately never exposes
    individual salary or evidence via this endpoint (or anywhere else);
    those stay behind Django Admin only, per the Phase 16 planning
    decision enforced everywhere this data appears."""

    permission_classes = [IsAdminRole]
    serializer_class = EmploymentSummarySerializer

    def get(self, request):
        serializer = EmploymentSummarySerializer(get_employment_summary())
        return Response(serializer.data)
