"""Module-level and cross-course ("overall academy") progress views,
built on top of the same LessonProgress data that
Enrollment.recalculate_progress() already uses for the stored
course-level percentage (kept auto-fresh via apps.enrollments.signals).
Read-only, derived fresh every call — same philosophy as the rest of
apps.analytics.
"""
from apps.courses.models import Lesson
from apps.enrollments.models import Enrollment, LessonProgress


def get_module_progress(student, module):
    total = Lesson.objects.filter(module=module, status="published").count()
    if total == 0:
        return 0
    completed = LessonProgress.objects.filter(
        student=student, lesson__module=module, completed=True
    ).count()
    return round((completed / total) * 100)


def get_course_module_breakdown(student, course):
    modules = course.modules.filter(status="published")
    return [
        {"module": module, "percentage": get_module_progress(student, module)}
        for module in modules
    ]


def get_overall_academy_progress(student):
    """Lesson-count-weighted average across all active enrollments — a
    plain average of per-course percentages would let a 2-lesson course
    finished count the same as a 50-lesson course barely started."""
    enrollments = Enrollment.objects.filter(
        student=student, status=Enrollment.Status.ACTIVE
    ).select_related("course")

    total_lessons = 0
    total_completed = 0
    for enrollment in enrollments:
        total_lessons += Lesson.objects.filter(
            module__course=enrollment.course, module__status="published", status="published",
        ).count()
        total_completed += LessonProgress.objects.filter(
            student=student, lesson__module__course=enrollment.course, completed=True,
        ).count()

    if total_lessons == 0:
        return 0
    return round((total_completed / total_lessons) * 100)
