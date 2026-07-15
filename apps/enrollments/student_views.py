import json

from django.contrib import messages
from django.db.models import F
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from apps.accounts.permissions import student_required
from apps.analytics.models import LearningTimeEntry
from apps.analytics.services.course_progress import get_course_module_breakdown
from apps.courses.models import Course, Lesson

from .models import Enrollment, LessonProgress

# Heartbeat fires every 60s from the lesson page — cap well above that
# so a client can never report an inflated time-spent value, whether
# from a bug or deliberate tampering.
MAX_HEARTBEAT_SECONDS = 90


def _get_enrollment(student, course_id):
    return get_object_or_404(
        Enrollment.objects.select_related("course"), student=student, course_id=course_id, status=Enrollment.Status.ACTIVE
    )


@student_required
def course_overview(request, course_id):
    enrollment = _get_enrollment(request.user, course_id)
    course = enrollment.course
    modules = list(course.modules.filter(status="published").prefetch_related("lessons"))
    completed_lesson_ids = set(
        LessonProgress.objects.filter(student=request.user, completed=True, lesson__module__course=course).values_list(
            "lesson_id", flat=True
        )
    )
    progress_by_module_id = {
        row["module"].id: row["percentage"] for row in get_course_module_breakdown(request.user, course)
    }
    for module in modules:
        module.progress_percentage = progress_by_module_id.get(module.id, 0)

    return render(request, "student/learning/overview.html", {
        "course": course, "modules": modules, "completed_lesson_ids": completed_lesson_ids,
        "enrollment": enrollment,
    })


@student_required
def lesson_detail(request, course_id, lesson_id):
    enrollment = _get_enrollment(request.user, course_id)
    course = enrollment.course
    lesson = get_object_or_404(Lesson, id=lesson_id, module__course=course, status="published")

    progress, created = LessonProgress.objects.get_or_create(student=request.user, lesson=lesson)
    if not created:
        progress.save(update_fields=["last_accessed_at"])

    if request.method == "POST":
        progress.completed = True
        progress.completed_at = timezone.now()
        progress.save()
        # No manual enrollment.recalculate_progress() call needed here —
        # apps.enrollments.signals recalculates automatically on every
        # LessonProgress save, so it stays correct for every code path
        # (Admin, API, etc.), not just this view.
        messages.success(request, "Lesson marked complete.")
        return redirect("student_learning:lesson_detail", course_id=course.id, lesson_id=lesson.id)

    all_lessons = list(
        Lesson.objects.filter(module__course=course, module__status="published", status="published").order_by(
            "module__display_order", "display_order"
        )
    )
    idx = next((i for i, l in enumerate(all_lessons) if l.id == lesson.id), 0)
    prev_lesson = all_lessons[idx - 1] if idx > 0 else None
    next_lesson = all_lessons[idx + 1] if idx < len(all_lessons) - 1 else None

    return render(request, "student/learning/lesson.html", {
        "course": course, "lesson": lesson, "progress": progress,
        "prev_lesson": prev_lesson, "next_lesson": next_lesson,
    })


@student_required
@require_POST
def lesson_heartbeat(request, course_id, lesson_id):
    """Called periodically by the lesson page while it's visible, to
    accumulate time-on-task. Never trusts the client's reported duration
    beyond a small capped increment — see MAX_HEARTBEAT_SECONDS."""
    enrollment = _get_enrollment(request.user, course_id)
    lesson = get_object_or_404(Lesson, id=lesson_id, module__course=enrollment.course, status="published")

    try:
        payload = json.loads(request.body)
        seconds = int(payload.get("seconds", 0))
    except (ValueError, TypeError, json.JSONDecodeError):
        seconds = 0
    seconds = max(0, min(seconds, MAX_HEARTBEAT_SECONDS))

    if seconds > 0:
        entry, _created = LearningTimeEntry.objects.get_or_create(
            student=request.user, lesson=lesson, date=timezone.localdate(),
        )
        LearningTimeEntry.objects.filter(pk=entry.pk).update(seconds=F("seconds") + seconds)

    return JsonResponse({"ok": True})
