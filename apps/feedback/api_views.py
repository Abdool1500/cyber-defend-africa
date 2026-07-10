from rest_framework import viewsets
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.permissions import IsAuthenticated

from apps.enrollments.models import Enrollment

from .models import StudentFeedback
from .serializers import StudentFeedbackSerializer


class StudentFeedbackViewSet(viewsets.ModelViewSet):
    """A student may only ever see and create their own feedback through
    this endpoint — instructor/management feedback views are separate,
    template-rendered pages with their own anonymity-safe queries."""

    serializer_class = StudentFeedbackSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ["get", "post", "head", "options"]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return StudentFeedback.objects.none()
        return StudentFeedback.objects.filter(student=self.request.user)

    def perform_create(self, serializer):
        course = serializer.validated_data["course"]
        is_enrolled = Enrollment.objects.filter(
            student=self.request.user, course=course, status=Enrollment.Status.ACTIVE
        ).exists()
        if not is_enrolled:
            raise PermissionDenied("You must be enrolled in this course to leave feedback.")
        if StudentFeedback.objects.filter(student=self.request.user, course=course).exists():
            raise ValidationError("You have already submitted feedback for this course.")
        serializer.save(student=self.request.user)
