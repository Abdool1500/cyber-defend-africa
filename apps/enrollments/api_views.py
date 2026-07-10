from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from .models import Enrollment
from .serializers import EnrollmentSerializer


class EnrollmentViewSet(viewsets.ReadOnlyModelViewSet):
    """A user only ever sees their own enrollments — there is no
    cross-student listing here, by design (object scoping via queryset,
    not just serializer field hiding)."""

    serializer_class = EnrollmentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Enrollment.objects.none()
        return Enrollment.objects.filter(student=self.request.user).select_related("course")
