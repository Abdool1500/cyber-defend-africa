from django.shortcuts import render

from apps.accounts.permissions import admin_required, instructor_required, student_required
from apps.assignments.models import AssignmentSubmission
from apps.certificates.models import Certificate
from apps.courses.models import Course
from apps.enrollments.models import Enrollment
from apps.instructors.models import InstructorAssignment
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
    recent_certificates = Certificate.objects.filter(student=request.user, status=Certificate.Status.ISSUED)
    return render(request, "student/dashboard/overview.html", {
        "enrollments": enrollments,
        "upcoming_quizzes": upcoming_quizzes,
        "certificate_count": recent_certificates.count(),
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
    student_count = Enrollment.objects.filter(course_id__in=course_ids, status=Enrollment.Status.ACTIVE).values(
        "student"
    ).distinct().count()
    return render(request, "instructor/dashboard/overview.html", {
        "assignments": assignments,
        "pending_grading": pending_grading,
        "pending_submissions": pending_submissions,
        "student_count": student_count,
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
