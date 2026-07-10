from rest_framework import viewsets
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated

from apps.enrollments.models import Enrollment

from .models import Assignment, AssignmentSubmission
from .serializers import AssignmentSerializer, AssignmentSubmissionSerializer


class AssignmentViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = AssignmentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Assignment.objects.none()
        course_ids = Enrollment.objects.filter(
            student=self.request.user, status=Enrollment.Status.ACTIVE
        ).values_list("course_id", flat=True)
        return Assignment.objects.filter(course_id__in=course_ids, status=Assignment.Status.PUBLISHED)


class AssignmentSubmissionViewSet(viewsets.ModelViewSet):
    """List/create/update are all scoped to the requesting student's own
    submissions. Score and instructor_feedback are read-only on the
    serializer, so a student can never write their own grade through
    this endpoint."""

    serializer_class = AssignmentSubmissionSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ["get", "post", "head", "options"]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return AssignmentSubmission.objects.none()
        return AssignmentSubmission.objects.filter(student=self.request.user)

    def perform_create(self, serializer):
        assignment = serializer.validated_data["assignment"]
        is_enrolled = Enrollment.objects.filter(
            student=self.request.user, course=assignment.course, status=Enrollment.Status.ACTIVE
        ).exists()
        if not is_enrolled or assignment.status != Assignment.Status.PUBLISHED:
            raise PermissionDenied("You are not enrolled in this assignment's course.")
        serializer.save(student=self.request.user)
