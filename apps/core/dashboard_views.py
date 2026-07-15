from django.shortcuts import render

from apps.accounts.permissions import admin_required, instructor_required, student_required
from apps.analytics.services.course_progress import get_overall_academy_progress
from apps.analytics.services.lab_progress import get_lab_summary
from apps.analytics.services.instructor_stats import get_instructor_dashboard_stats
from apps.analytics.services.leaderboard import get_leaderboard_position
from apps.analytics.services.learning_time import get_learning_streak, get_learning_time_summary
from apps.analytics.services.skill_improvement import get_skill_improvement
from apps.assignments.models import Assignment, AssignmentSubmission
from apps.certificates.models import Certificate
from apps.courses.models import Course
from apps.enrollments.models import Enrollment
from apps.instructors.models import InstructorAssignment
from apps.labs.models import LabProgress
from apps.leads.models import ConsultationRequest, ContactSubmission, DemoRequest, PilotRequest
from apps.quizzes.models import Quiz, QuizAttempt


# --- Student ---------------------------------------------------------

@student_required
def student_overview(request):
    enrollments = Enrollment.objects.filter(student=request.user).select_related("course")
    course_ids = [e.course_id for e in enrollments]
    upcoming_quizzes = Quiz.objects.filter(
        course_id__in=course_ids, status=Quiz.Status.PUBLISHED
    ).exclude(attempts__student=request.user)[:5]
    upcoming_assignments = Assignment.objects.filter(
        course_id__in=course_ids, status=Assignment.Status.PUBLISHED
    ).exclude(submissions__student=request.user).order_by("due_at")[:5]
    recent_quiz_attempts = QuizAttempt.objects.filter(
        student=request.user, status=QuizAttempt.Status.GRADED
    ).select_related("quiz").order_by("-graded_at")[:5]
    recent_certificates = Certificate.objects.filter(student=request.user, status=Certificate.Status.ISSUED)

    skill_improvements = [
        {"course": e.course, **get_skill_improvement(request.user, e.course)}
        for e in enrollments
    ]
    skill_improvements = [row for row in skill_improvements if row["complete"]]
    skill_improvement_chart_data = {
        "labels": [row["course"].title for row in skill_improvements],
        "pre": [row["pre_test_percentage"] for row in skill_improvements],
        "post": [row["post_test_percentage"] for row in skill_improvements],
    }

    return render(request, "student/dashboard/overview.html", {
        "enrollments": enrollments,
        "upcoming_quizzes": upcoming_quizzes,
        "upcoming_assignments": upcoming_assignments,
        "recent_quiz_attempts": recent_quiz_attempts,
        "certificate_count": recent_certificates.count(),
        "skill_improvements": skill_improvements,
        "skill_improvement_chart_data": skill_improvement_chart_data,
        "learning_time": get_learning_time_summary(request.user),
        "learning_streak": get_learning_streak(request.user),
        "lab_summary": get_lab_summary(request.user),
        "overall_academy_progress": get_overall_academy_progress(request.user),
        "leaderboard": get_leaderboard_position(request.user),
    })


@student_required
def student_courses(request):
    enrollments = Enrollment.objects.filter(student=request.user, status=Enrollment.Status.ACTIVE).select_related("course")
    return render(request, "student/dashboard/courses.html", {"enrollments": enrollments})


# --- Instructor --------------------------------------------------------

@instructor_required
def instructor_overview(request):
    assignments = InstructorAssignment.objects.filter(
        instructor=request.user, status=InstructorAssignment.Status.ACTIVE
    ).select_related("course")
    course_ids = [a.course_id for a in assignments]
    pending_grading = QuizAttempt.objects.filter(
        quiz__course_id__in=course_ids, status=QuizAttempt.Status.PENDING_MANUAL_GRADING
    ).count()
    pending_submissions = AssignmentSubmission.objects.filter(
        assignment__course_id__in=course_ids, status=AssignmentSubmission.Status.SUBMITTED
    ).count()
    pending_lab_grading = LabProgress.objects.filter(
        lab__course_id__in=course_ids, status=LabProgress.Status.COMPLETED, score__isnull=True,
    ).count()
    student_count = Enrollment.objects.filter(course_id__in=course_ids, status=Enrollment.Status.ACTIVE).values(
        "student"
    ).distinct().count()
    return render(request, "instructor/dashboard/overview.html", {
        "assignments": assignments,
        "pending_grading": pending_grading,
        "pending_submissions": pending_submissions,
        "pending_lab_grading": pending_lab_grading,
        "student_count": student_count,
        "stats": get_instructor_dashboard_stats(request.user),
    })


@instructor_required
def instructor_courses(request):
    assignments = InstructorAssignment.objects.filter(
        instructor=request.user, status=InstructorAssignment.Status.ACTIVE
    ).select_related("course")
    return render(request, "instructor/dashboard/courses.html", {"assignments": assignments})


@instructor_required
def instructor_students(request):
    assignments = InstructorAssignment.objects.filter(
        instructor=request.user, status=InstructorAssignment.Status.ACTIVE
    )
    course_ids = [a.course_id for a in assignments]
    enrollments = Enrollment.objects.filter(course_id__in=course_ids).select_related("student", "course")
    return render(request, "instructor/dashboard/students.html", {"enrollments": enrollments})


# --- Management --------------------------------------------------------

@admin_required
def management_overview(request):
    from apps.accounts.models import User

    stats = {
        "total_students": User.objects.filter(role=User.Role.STUDENT).count(),
        "total_instructors": User.objects.filter(role=User.Role.INSTRUCTOR).count(),
        "total_courses": Course.objects.count(),
        "total_enrollments": Enrollment.objects.count(),
        "new_contact_submissions": ContactSubmission.objects.count(),
        "new_demo_requests": DemoRequest.objects.filter(status=DemoRequest.Status.NEW).count(),
        "new_pilot_requests": PilotRequest.objects.filter(status=PilotRequest.Status.NEW).count(),
        "new_consultation_requests": ConsultationRequest.objects.filter(status=ConsultationRequest.Status.NEW).count(),
    }
    return render(request, "management/overview.html", {"stats": stats})
