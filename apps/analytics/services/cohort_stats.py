"""Per-cohort impact metrics — read-only, computed fresh on every call
(same philosophy as the rest of apps.analytics). Cohort management
itself (creating cohorts, adding/removing members) is handled via
Django Admin — this module only answers "how is this group doing".
"""
from django.db.models import Avg

from apps.certificates.models import Certificate
from apps.cohorts.models import CohortMembership
from apps.enrollments.models import Enrollment
from apps.quizzes.models import QuizAttempt

from .skill_improvement import get_skill_improvement

DROPOUT_STATUSES = [Enrollment.Status.WITHDRAWN, Enrollment.Status.SUSPENDED]


def get_cohort_stats(cohort):
    student_ids = list(CohortMembership.objects.filter(cohort=cohort).values_list("student_id", flat=True))
    member_count = len(student_ids)

    enrollments = Enrollment.objects.filter(student_id__in=student_ids).select_related("student", "course")
    total_enrollments = enrollments.count()
    completed_enrollments = enrollments.filter(status=Enrollment.Status.COMPLETED).count()
    dropout_enrollments = enrollments.filter(status__in=DROPOUT_STATUSES).count()

    completion_rate = round((completed_enrollments / total_enrollments) * 100, 1) if total_enrollments else 0
    dropout_rate = round((dropout_enrollments / total_enrollments) * 100, 1) if total_enrollments else 0

    average_score = QuizAttempt.objects.filter(
        student_id__in=student_ids, status=QuizAttempt.Status.GRADED,
    ).aggregate(avg=Avg("percentage"))["avg"]
    average_score = round(average_score, 1) if average_score is not None else None

    improvements = [
        result["improvement"]
        for result in (get_skill_improvement(e.student, e.course) for e in enrollments)
        if result["complete"]
    ]
    average_improvement = round(sum(improvements) / len(improvements), 1) if improvements else None

    certificates_earned = Certificate.objects.filter(
        student_id__in=student_ids, status=Certificate.Status.ISSUED,
    ).count()

    return {
        "member_count": member_count,
        "total_enrollments": total_enrollments,
        "completion_rate": completion_rate,
        "average_score": average_score,
        "average_improvement": average_improvement,
        "dropout_rate": dropout_rate,
        "certificates_earned": certificates_earned,
    }
