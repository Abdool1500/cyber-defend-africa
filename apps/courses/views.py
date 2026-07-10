from django.shortcuts import get_object_or_404, render

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
