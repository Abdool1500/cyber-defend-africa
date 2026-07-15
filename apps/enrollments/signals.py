"""Keeps Enrollment.progress_percentage automatically fresh — connected
via EnrollmentsConfig.ready(). Previously recalculate_progress() was
only ever called from one place (the lesson_detail view's "mark
complete" POST handler), so progress silently went stale for any other
path that touches the underlying data: Django Admin edits, a future
API, or an instructor publishing/unpublishing a lesson (which changes
the denominator for every enrolled student, not just the one who
triggered it).
"""
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from apps.courses.models import CourseModule, Lesson

from .models import Enrollment, LessonProgress


def _recalculate_for_student_course(student, course):
    enrollment = Enrollment.objects.filter(student=student, course=course).first()
    if enrollment:
        enrollment.recalculate_progress()


def _recalculate_for_all_enrollments(course):
    for enrollment in Enrollment.objects.filter(course=course, status=Enrollment.Status.ACTIVE):
        enrollment.recalculate_progress()


@receiver(post_save, sender=LessonProgress)
@receiver(post_delete, sender=LessonProgress)
def on_lesson_progress_change(sender, instance, **kwargs):
    _recalculate_for_student_course(instance.student, instance.lesson.module.course)


@receiver(post_save, sender=Lesson)
@receiver(post_delete, sender=Lesson)
def on_lesson_change(sender, instance, **kwargs):
    _recalculate_for_all_enrollments(instance.module.course)


@receiver(post_save, sender=CourseModule)
@receiver(post_delete, sender=CourseModule)
def on_module_change(sender, instance, **kwargs):
    _recalculate_for_all_enrollments(instance.course)
