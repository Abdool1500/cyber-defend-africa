from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework.routers import DefaultRouter

from apps.assignments.api_views import AssignmentSubmissionViewSet, AssignmentViewSet
from apps.courses.api_views import CourseViewSet
from apps.enrollments.api_views import EnrollmentViewSet
from apps.feedback.api_views import StudentFeedbackViewSet
from apps.notifications.api_views import NotificationViewSet
from apps.question_bank.api_views import QuestionViewSet
from apps.quizzes.api_views import QuizAttemptViewSet, QuizViewSet
from apps.resources.api_views import ResourcePostViewSet

router = DefaultRouter()
router.register("courses", CourseViewSet, basename="api-course")
router.register("enrollments", EnrollmentViewSet, basename="api-enrollment")
router.register("quizzes", QuizViewSet, basename="api-quiz")
router.register("attempts", QuizAttemptViewSet, basename="api-attempt")
router.register("assignments", AssignmentViewSet, basename="api-assignment")
router.register("assignment-submissions", AssignmentSubmissionViewSet, basename="api-assignment-submission")
router.register("feedback", StudentFeedbackViewSet, basename="api-feedback")
router.register("notifications", NotificationViewSet, basename="api-notification")
router.register("resources", ResourcePostViewSet, basename="api-resource")
router.register("question-bank", QuestionViewSet, basename="api-question-bank")

app_name = "api-v1"

urlpatterns = [
    path("", include(router.urls)),
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
    path("docs/", SpectacularSwaggerView.as_view(url_name="api-v1:schema"), name="docs"),
]
