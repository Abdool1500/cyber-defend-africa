from rest_framework import viewsets

from apps.accounts.permissions import IsAdminRole

from .models import Cohort
from .serializers import CohortSerializer


class CohortViewSet(viewsets.ReadOnlyModelViewSet):
    """Admin-only — read-only listing of cohorts with their computed
    impact stats nested in, reusing the exact same
    apps.analytics.services.cohort_stats.get_cohort_stats() the
    management-facing cohort pages already use."""

    queryset = Cohort.objects.all().order_by("name")
    serializer_class = CohortSerializer
    permission_classes = [IsAdminRole]
