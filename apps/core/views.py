from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import redirect, render


def home(request):
    from apps.courses.models import Course

    featured_courses = Course.objects.filter(status=Course.Status.PUBLISHED)[:3]
    return render(request, "public/home.html", {"featured_courses": featured_courses})


def health_check(request):
    return JsonResponse({"status": "ok"})


@login_required
def post_login_redirect(request):
    role = getattr(request.user, "role", None)
    if role == "student":
        return redirect("student:overview")
    if role == "instructor":
        return redirect("instructor:overview")
    if role in ("admin", "super_admin"):
        return redirect("management:overview")
    return redirect("core:home")
