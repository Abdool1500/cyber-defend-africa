from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from apps.enrollments.models import Enrollment

from .models import Quiz, QuizAttempt
from .serializers import QuizAttemptSerializer, QuizSerializer


class QuizViewSet(viewsets.ReadOnlyModelViewSet):
    """Published quizzes for courses the requesting student is actively
    enrolled in — never exposes questions/options/correct answers, only
    quiz-level metadata (title, timing, attempt limit)."""

    serializer_class = QuizSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Quiz.objects.none()
        course_ids = Enrollment.objects.filter(
            student=self.request.user, status=Enrollment.Status.ACTIVE
        ).values_list("course_id", flat=True)
        return Quiz.objects.filter(course_id__in=course_ids, status=Quiz.Status.PUBLISHED)


class QuizAttemptViewSet(viewsets.ReadOnlyModelViewSet):
    """A student can only ever see their own attempts — enforced via
    queryset scoping, not just object-level permission, so there is no
    way to enumerate another student's attempt by id."""

    serializer_class = QuizAttemptSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return QuizAttempt.objects.none()
        return QuizAttempt.objects.filter(student=self.request.user).select_related("quiz")
