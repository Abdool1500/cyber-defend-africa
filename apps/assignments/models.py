import uuid

from django.conf import settings
from django.db import models


class Assignment(models.Model):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        PUBLISHED = "published", "Published"
        ARCHIVED = "archived", "Archived"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    course = models.ForeignKey("courses.Course", on_delete=models.CASCADE, related_name="assignments")
    module = models.ForeignKey(
        "courses.CourseModule", on_delete=models.SET_NULL, null=True, blank=True, related_name="assignments"
    )
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    instructions = models.TextField(blank=True)
    due_at = models.DateTimeField(null=True, blank=True)
    max_points = models.PositiveIntegerField(default=100)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    allow_late_submissions = models.BooleanField(
        default=True,
        help_text="If disabled, submissions are rejected once due_at has passed.",
    )
    allow_resubmission = models.BooleanField(
        default=True,
        help_text="If enabled, a student may replace their submission before it is graded.",
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="assignments_created"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["course", "status"]),
        ]

    def __str__(self):
        return self.title


class AssignmentSubmission(models.Model):
    class Status(models.TextChoices):
        SUBMITTED = "submitted", "Submitted"
        LATE = "late", "Late"
        GRADED = "graded", "Graded"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name="submissions")
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="assignment_submissions"
    )
    text_submission = models.TextField(blank=True)
    storage_path = models.CharField(max_length=500, null=True, blank=True)
    original_filename = models.CharField(max_length=255, null=True, blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.SUBMITTED)
    score = models.FloatField(null=True, blank=True)
    instructor_feedback = models.TextField(blank=True)
    graded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="submissions_graded"
    )
    graded_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-submitted_at"]
        constraints = [
            models.UniqueConstraint(fields=["assignment", "student"], name="unique_submission_per_student_assignment")
        ]
        indexes = [
            models.Index(fields=["student"]),
            models.Index(fields=["assignment", "status"]),
        ]

    def __str__(self):
        return f"{self.student} — {self.assignment.title}"

    def is_late(self):
        if not self.assignment.due_at:
            return False
        return self.submitted_at > self.assignment.due_at
