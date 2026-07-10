import uuid

from django.conf import settings
from django.db import models


class Notification(models.Model):
    class Type(models.TextChoices):
        QUIZ_PUBLISHED = "quiz_published", "Quiz Published"
        ASSIGNMENT_DUE = "assignment_due", "Assignment Due"
        GRADE_AVAILABLE = "grade_available", "Grade Available"
        ANNOUNCEMENT = "announcement", "Announcement"
        SYSTEM = "system", "System Message"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notifications")
    title = models.CharField(max_length=200)
    message = models.TextField(blank=True)
    type = models.CharField(max_length=30, choices=Type.choices, default=Type.SYSTEM)
    read_at = models.DateTimeField(null=True, blank=True)
    action_url = models.CharField(max_length=500, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "read_at"]),
        ]

    def __str__(self):
        return f"{self.user} — {self.title}"


class Announcement(models.Model):
    class Audience(models.TextChoices):
        PLATFORM_WIDE = "platform_wide", "Platform-wide"
        COURSE = "course", "Course"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200)
    body = models.TextField()
    audience = models.CharField(max_length=20, choices=Audience.choices, default=Audience.COURSE)
    course = models.ForeignKey(
        "courses.Course", on_delete=models.CASCADE, null=True, blank=True, related_name="announcements"
    )
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="announcements_created")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title
