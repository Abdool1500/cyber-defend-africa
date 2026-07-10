from rest_framework import viewsets

from apps.core.api_permissions import IsInstructor
from apps.instructors.models import InstructorAssignment

from .models import Question
from .serializers import QuestionSerializer


class QuestionViewSet(viewsets.ReadOnlyModelViewSet):
    """Instructor-only, scoped to the requesting instructor's assigned
    courses. Never exposed to student-authenticated requests — IsInstructor
    denies access outright regardless of object scoping."""

    serializer_class = QuestionSerializer
    permission_classes = [IsInstructor]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Question.objects.none()
        course_ids = InstructorAssignment.objects.filter(
            instructor=self.request.user, status=InstructorAssignment.Status.ACTIVE
        ).values_list("course_id", flat=True)
        return Question.objects.filter(course_id__in=course_ids).select_related("course")
