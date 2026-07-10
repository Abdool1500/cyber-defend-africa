from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

from apps.accounts.permissions import student_required
from apps.enrollments.models import Enrollment

from .models import Course


def course_list(request):
    courses = Course.objects.filter(status=Course.Status.PUBLISHED).prefetch_related("modules")
    return render(request, "public/course_list.html", {"courses": courses})


def course_detail(request, slug):
    course = get_object_or_404(
        Course.objects.prefetch_related("modules__lessons"),
        slug=slug,
        status=Course.Status.PUBLISHED,
    )
    is_enrolled = False
    if request.user.is_authenticated and getattr(request.user, "is_student", False):
        is_enrolled = course.enrollments.filter(student=request.user, status="active").exists()
    return render(
        request,
        "public/course_detail.html",
        {"course": course, "is_enrolled": is_enrolled},
    )


@student_required
def enroll(request, slug):
    course = get_object_or_404(Course, slug=slug, status=Course.Status.PUBLISHED)
    Enrollment.objects.get_or_create(
        student=request.user, course=course, defaults={"status": Enrollment.Status.ACTIVE}
    )
    messages.success(request, f"You're enrolled in {course.title}.")
    return redirect("student_learning:course_overview", course_id=course.id)
