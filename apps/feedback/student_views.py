from django.contrib import messages
from django.db import IntegrityError
from django.shortcuts import get_object_or_404, redirect, render

from apps.accounts.permissions import student_required
from apps.courses.models import Course
from apps.enrollments.models import Enrollment

from .forms import StudentFeedbackForm
from .models import StudentFeedback


def _enrolled_courses(student):
    course_ids = Enrollment.objects.filter(
        student=student, status=Enrollment.Status.ACTIVE
    ).values_list("course_id", flat=True)
    return Course.objects.filter(id__in=course_ids)


@student_required
def feedback_list(request):
    enrolled_courses = _enrolled_courses(request.user)
    submitted_course_ids = set(
        StudentFeedback.objects.filter(student=request.user, course__in=enrolled_courses).values_list(
            "course_id", flat=True
        )
    )
    eligible_courses = [c for c in enrolled_courses if c.id not in submitted_course_ids]
    my_feedback = StudentFeedback.objects.filter(student=request.user).select_related("course")
    return render(request, "student/feedback/list.html", {
        "eligible_courses": eligible_courses, "my_feedback": my_feedback,
    })


@student_required
def feedback_create(request, course_id):
    # Only courses the student is actively enrolled in are eligible — this
    # is the server-side guard, not just a hidden dropdown option.
    course = get_object_or_404(_enrolled_courses(request.user), id=course_id)

    if StudentFeedback.objects.filter(student=request.user, course=course).exists():
        messages.info(request, "You've already submitted feedback for this course. Only one submission per course is allowed.")
        return redirect("student_feedback:list")

    if request.method == "POST":
        form = StudentFeedbackForm(request.POST)
        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.student = request.user
            feedback.course = course
            try:
                feedback.save()
            except IntegrityError:
                messages.info(request, "You've already submitted feedback for this course.")
                return redirect("student_feedback:list")
            messages.success(request, "Thank you — your feedback has been submitted.")
            return redirect("student_feedback:list")
    else:
        form = StudentFeedbackForm()

    return render(request, "student/feedback/form.html", {"form": form, "course": course})
