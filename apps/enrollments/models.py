import uuid

from django.conf import settings
from django.db import models
from django.utils import timezone


class Enrollment(models.Model):
    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        COMPLETED = "completed", "Completed"
        SUSPENDED = "suspended", "Suspended"
        WITHDRAWN = "withdrawn", "Withdrawn"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="enrollments",
        limit_choices_to={"role": "student"},
    )
    course = models.ForeignKey("courses.Course", on_delete=models.CASCADE, related_name="enrollments")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)
    enrolled_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    progress_percentage = models.PositiveIntegerField(default=0)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["student", "course"], name="unique_enrollment_per_student_course")
        ]
        indexes = [
            models.Index(fields=["student", "status"]),
            models.Index(fields=["course", "status"]),
        ]

    def __str__(self):
        return f"{self.student} in {self.course} ({self.status})"

    def recalculate_progress(self):
        """Server-side progress calculation — never trust a client-submitted
        percentage. Percentage of published lessons in the course marked
        complete by this student.

        Also the single place `status` auto-promotes ACTIVE -> COMPLETED
        (and stamps `completed_at`) once progress reaches 100% — before
        16.Q, nothing in the codebase ever set `status` to COMPLETED
        outside Django Admin, so every completion-rate/dropout-rate
        figure across the Phase 16 analytics services was silently
        undercounting completions. Deliberately one-directional: later
        dropping below 100% (e.g. an instructor publishes a new lesson,
        changing the denominator) never demotes a student back to
        ACTIVE — a student who already completed a course, and may
        already hold a certificate for it, shouldn't lose that status
        because the course grew after the fact."""
        from apps.courses.models import Lesson

        total_lessons = Lesson.objects.filter(
            module__course=self.course,
            module__status="published",
            status="published",
        ).count()
        if total_lessons == 0:
            self.progress_percentage = 0
        else:
            completed = LessonProgress.objects.filter(
                student=self.student,
                lesson__module__course=self.course,
                completed=True,
            ).count()
            self.progress_percentage = round((completed / total_lessons) * 100)

        update_fields = ["progress_percentage"]
        if self.progress_percentage == 100 and self.status == self.Status.ACTIVE:
            self.status = self.Status.COMPLETED
            self.completed_at = timezone.now()
            update_fields += ["status", "completed_at"]

        self.save(update_fields=update_fields)
        return self.progress_percentage


class LessonProgress(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="lesson_progress"
    )
    lesson = models.ForeignKey("courses.Lesson", on_delete=models.CASCADE, related_name="progress_records")
    completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    last_accessed_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["student", "lesson"], name="unique_progress_per_student_lesson")
        ]
        indexes = [
            models.Index(fields=["student", "completed"]),
        ]

    def __str__(self):
        return f"{self.student} — {self.lesson} ({'done' if self.completed else 'in progress'})"
