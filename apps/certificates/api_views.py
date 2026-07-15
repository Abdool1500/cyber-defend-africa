from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from .models import Certificate
from .serializers import CertificateSerializer


class CertificateViewSet(viewsets.ReadOnlyModelViewSet):
    """A user only ever sees their own issued certificates — same
    object-scoping-via-queryset pattern as EnrollmentViewSet. Excludes
    `certificate_storage_path` from the serializer (internal Supabase
    reference, never shown in any template either)."""

    serializer_class = CertificateSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Certificate.objects.none()
        return Certificate.objects.filter(
            student=self.request.user, status=Certificate.Status.ISSUED
        ).select_related("course")
