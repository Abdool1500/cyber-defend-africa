"""Row-shaping for the Course and Student exports (16.L). Unlike
apps.analytics.services, these functions exist purely to feed export
files — nothing else in the platform consumes a full per-course or
per-student row list, so they live in apps.reports rather than
polluting apps.analytics with report-only shapes.

Computed with simple per-row queries rather than one large joined
annotation, matching the same "admin-reporting page, not a hot path"
reasoning already used in apps.analytics.services.cohort_stats.
"""
from django.db.models import Avg, Sum

from apps.certificates.models import Certificate
from apps.courses.models import Course
from apps.enrollments.models import Enrollment
from apps.feedback.models import StudentFeedback
from apps.quizzes.models import QuizAttempt


def get_course_report_rows():
    rows = []
    for course in Course.objects.all().order_by("title"):
        enrollments = Enrollment.objects.filter(course=course)
        total = enrollments.count()
        completed = enrollments.filter(status=Enrollment.Status.COMPLETED).count()
        completion_rate = round((completed / total) * 100, 1) if total else 0

        avg_score = QuizAttempt.objects.filter(
            quiz__course=course, status=QuizAttempt.Status.GRADED
        ).aggregate(avg=Avg("percentage"))["avg"]

        avg_rating = StudentFeedback.objects.filter(course=course).aggregate(avg=Avg("overall_rating"))["avg"]

        certificates_issued = Certificate.objects.filter(course=course, status=Certificate.Status.ISSUED).count()

        rows.append({
            "course_title": course.title,
            "total_enrollments": total,
            "completed_enrollments": completed,
            "completion_rate": completion_rate,
            "average_score": round(avg_score, 1) if avg_score is not None else None,
            "average_rating": round(avg_rating, 1) if avg_rating is not None else None,
            "certificates_issued": certificates_issued,
        })
    return rows


def get_student_report_rows():
    from apps.accounts.models import User
    from apps.analytics.models import LearningTimeEntry

    rows = []
    for student in User.objects.filter(role=User.Role.STUDENT).order_by("full_name"):
        enrollments = Enrollment.objects.filter(student=student)
        total = enrollments.count()
        completed = enrollments.filter(status=Enrollment.Status.COMPLETED).count()

        avg_score = QuizAttempt.objects.filter(
            student=student, status=QuizAttempt.Status.GRADED
        ).aggregate(avg=Avg("percentage"))["avg"]

        certificates_earned = Certificate.objects.filter(student=student, status=Certificate.Status.ISSUED).count()

        total_seconds = LearningTimeEntry.objects.filter(student=student).aggregate(total=Sum("seconds"))["total"] or 0

        rows.append({
            "student_name": student.full_name,
            "student_email": student.email,
            "total_enrollments": total,
            "completed_enrollments": completed,
            "average_score": round(avg_score, 1) if avg_score is not None else None,
            "certificates_earned": certificates_earned,
            "learning_hours": round(total_seconds / 3600, 1),
        })
    return rows
