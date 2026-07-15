"""Platform-wide KPIs for the Management Analytics Dashboard (16.J) —
read-only, computed fresh on every call, same philosophy as every other
service in this package. Reuses the cohort-level building blocks
(dropout statuses, NPS, employment) rather than redefining them, so a
platform-wide number and a cohort-level number can never silently
disagree on what "dropout" or "employed" means.
"""
from datetime import timedelta

from django.db.models import Avg, Count, Sum
from django.utils import timezone

from apps.certificates.models import Certificate
from apps.enrollments.models import Enrollment
from apps.feedback.models import StudentFeedback
from apps.quizzes.models import Quiz, QuizAttempt

from .cohort_stats import DROPOUT_STATUSES
from .employment_stats import get_employment_summary
from .nps import calculate_nps
from ..models import LearningSession, LearningTimeEntry

TOP_N = 5


def _active_user_count(since):
    return LearningSession.objects.filter(started_at__gte=since).values("user_id").distinct().count()


def get_platform_analytics():
    now = timezone.now()
    today_start = timezone.localtime(now).replace(hour=0, minute=0, second=0, microsecond=0)
    thirty_days_ago = now - timedelta(days=30)

    enrollments = Enrollment.objects.all()
    total_enrollments = enrollments.count()
    completed_enrollments = enrollments.filter(status=Enrollment.Status.COMPLETED).count()
    dropout_enrollments = enrollments.filter(status__in=DROPOUT_STATUSES).count()
    completion_rate = round((completed_enrollments / total_enrollments) * 100, 1) if total_enrollments else 0
    dropout_rate = round((dropout_enrollments / total_enrollments) * 100, 1) if total_enrollments else 0
    retention_rate = round(100 - dropout_rate, 1) if total_enrollments else 0

    average_score = QuizAttempt.objects.filter(status=QuizAttempt.Status.GRADED).aggregate(
        avg=Avg("percentage")
    )["avg"]
    average_score = round(average_score, 1) if average_score is not None else None

    avg_pre_test = QuizAttempt.objects.filter(
        status=QuizAttempt.Status.GRADED, quiz__quiz_type=Quiz.QuizType.PRE_TEST
    ).aggregate(avg=Avg("percentage"))["avg"]
    avg_post_test = QuizAttempt.objects.filter(
        status=QuizAttempt.Status.GRADED, quiz__quiz_type=Quiz.QuizType.POST_TEST
    ).aggregate(avg=Avg("percentage"))["avg"]
    avg_skill_improvement = (
        round(avg_post_test - avg_pre_test, 1) if avg_pre_test is not None and avg_post_test is not None else None
    )

    certificates_issued = Certificate.objects.filter(status=Certificate.Status.ISSUED).count()
    certificates_this_month = Certificate.objects.filter(
        status=Certificate.Status.ISSUED, issued_at__gte=today_start.replace(day=1)
    ).count()

    total_learning_seconds = LearningTimeEntry.objects.aggregate(total=Sum("seconds"))["total"] or 0

    # Grouped by id (not just title/name) — course titles and instructor
    # full names are not unique, so grouping on the display field alone
    # would silently merge two different courses/instructors that
    # happen to share a name.
    top_courses = list(
        enrollments.values("course_id", "course__title")
        .annotate(enrollment_count=Count("id"))
        .order_by("-enrollment_count")[:TOP_N]
    )

    top_instructors = list(
        StudentFeedback.objects.exclude(instructor__isnull=True)
        .values("instructor_id", "instructor__full_name")
        .annotate(avg_rating=Avg("overall_rating"), response_count=Count("id"))
        .order_by("-avg_rating")[:TOP_N]
    )

    return {
        "dau": _active_user_count(today_start),
        "mau": _active_user_count(thirty_days_ago),
        "total_enrollments": total_enrollments,
        "completion_rate": completion_rate,
        "dropout_rate": dropout_rate,
        "retention_rate": retention_rate,
        "average_score": average_score,
        "avg_pre_test": round(avg_pre_test, 1) if avg_pre_test is not None else None,
        "avg_post_test": round(avg_post_test, 1) if avg_post_test is not None else None,
        "avg_skill_improvement": avg_skill_improvement,
        "certificates_issued": certificates_issued,
        "certificates_this_month": certificates_this_month,
        "total_learning_hours": round(total_learning_seconds / 3600, 1),
        "top_courses": top_courses,
        "top_instructors": top_instructors,
        "employment": get_employment_summary(),
        "nps": calculate_nps(StudentFeedback.objects.all()),
    }
