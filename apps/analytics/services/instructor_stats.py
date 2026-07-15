"""Instructor Dashboard aggregation (16.O) — every metric scoped to the
courses an instructor is actively assigned to, computed fresh on every
call like every other service in this package. Unlike the student-facing
leaderboard (16.N), instructor-facing student data is never anonymized
here — an instructor already sees their own students' names elsewhere
(the existing Students page), so a name + course + progress on an
at-risk list is not a new exposure.
"""
from datetime import timedelta

from django.db.models import Avg
from django.utils import timezone

from apps.analytics.services.nps import calculate_nps
from apps.assignments.models import AssignmentSubmission
from apps.enrollments.models import Enrollment
from apps.feedback.models import StudentFeedback
from apps.instructors.models import InstructorAssignment
from apps.labs.models import LabProgress, PracticalLab
from apps.quizzes.models import QuizAttempt

from ..models import LearningTimeEntry

AT_RISK_PROGRESS_THRESHOLD = 30
AT_RISK_SCORE_THRESHOLD = 50
ENGAGEMENT_WINDOW_DAYS = 7
AT_RISK_MAX_ROWS = 10


def _assigned_course_ids(instructor):
    return list(
        InstructorAssignment.objects.filter(
            instructor=instructor, status=InstructorAssignment.Status.ACTIVE
        ).values_list("course_id", flat=True)
    )


def get_instructor_dashboard_stats(instructor):
    course_ids = _assigned_course_ids(instructor)
    enrollments = Enrollment.objects.filter(course_id__in=course_ids).select_related("student", "course")
    active_enrollments = enrollments.filter(status=Enrollment.Status.ACTIVE)
    total_students = enrollments.values("student_id").distinct().count()

    since = timezone.now() - timedelta(days=ENGAGEMENT_WINDOW_DAYS)
    active_this_week = LearningTimeEntry.objects.filter(
        student_id__in=active_enrollments.values_list("student_id", flat=True),
        lesson__module__course_id__in=course_ids,
        date__gte=since.date(),
    ).values("student_id").distinct().count()

    average_quiz_score = QuizAttempt.objects.filter(
        quiz__course_id__in=course_ids, status=QuizAttempt.Status.GRADED
    ).aggregate(avg=Avg("percentage"))["avg"]

    avg_assignment = AssignmentSubmission.objects.filter(
        assignment__course_id__in=course_ids, status=AssignmentSubmission.Status.GRADED
    ).aggregate(avg=Avg("score"))["avg"]
    average_assignment_score = round(avg_assignment, 1) if avg_assignment is not None else None

    total_labs = PracticalLab.objects.filter(course_id__in=course_ids, status=PracticalLab.Status.PUBLISHED).count()
    completed_lab_progress = LabProgress.objects.filter(
        lab__course_id__in=course_ids, lab__status=PracticalLab.Status.PUBLISHED, status=LabProgress.Status.COMPLETED,
    ).count()
    lab_completion_rate = (
        round((completed_lab_progress / (total_labs * total_students)) * 100, 1)
        if total_labs and total_students else 0
    )

    students_attempted_quiz = QuizAttempt.objects.filter(quiz__course_id__in=course_ids).values(
        "student_id"
    ).distinct().count()
    quiz_completion_rate = round((students_attempted_quiz / total_students) * 100, 1) if total_students else 0

    students_submitted_assignment = AssignmentSubmission.objects.filter(
        assignment__course_id__in=course_ids
    ).values("student_id").distinct().count()
    assignment_submission_rate = (
        round((students_submitted_assignment / total_students) * 100, 1) if total_students else 0
    )

    at_risk_students = _get_at_risk_students(active_enrollments, course_ids)

    feedback_qs = StudentFeedback.objects.filter(course_id__in=course_ids)
    average_feedback_rating = feedback_qs.aggregate(avg=Avg("overall_rating"))["avg"]

    return {
        "total_students": total_students,
        "active_this_week": active_this_week,
        "average_quiz_score": round(average_quiz_score, 1) if average_quiz_score is not None else None,
        "average_assignment_score": average_assignment_score,
        "lab_completion_rate": lab_completion_rate,
        "quiz_completion_rate": quiz_completion_rate,
        "assignment_submission_rate": assignment_submission_rate,
        "at_risk_students": at_risk_students,
        "feedback": {
            "average_rating": round(average_feedback_rating, 1) if average_feedback_rating is not None else None,
            "response_count": feedback_qs.count(),
            **calculate_nps(feedback_qs),
        },
    }


def _get_at_risk_students(active_enrollments, course_ids):
    """A student is "at risk" if their progress in an active enrollment
    is low, or their average graded quiz score in that course is low.
    Bounded to one instructor's own roster (not platform-wide), so a
    per-enrollment loop is acceptable here for the same reason it's
    acceptable in apps.analytics.services.cohort_stats — this is an
    instructor-facing reporting view, not a hot path, and the roster
    size is naturally small."""
    at_risk = []
    for enrollment in active_enrollments:
        low_progress = enrollment.progress_percentage < AT_RISK_PROGRESS_THRESHOLD
        avg_score = QuizAttempt.objects.filter(
            quiz__course=enrollment.course, student=enrollment.student, status=QuizAttempt.Status.GRADED,
        ).aggregate(avg=Avg("percentage"))["avg"]
        low_score = avg_score is not None and avg_score < AT_RISK_SCORE_THRESHOLD

        if low_progress or low_score:
            at_risk.append({
                "student_name": enrollment.student.full_name,
                "course_title": enrollment.course.title,
                "progress_percentage": enrollment.progress_percentage,
                "average_score": round(avg_score, 1) if avg_score is not None else None,
            })
        if len(at_risk) >= AT_RISK_MAX_ROWS:
            break
    return at_risk
