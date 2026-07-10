import uuid

from django.conf import settings
from django.db import models


class InstructorAssignment(models.Model):
    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        REVOKED = "revoked", "Revoked"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    instructor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="instructor_assignments",
        limit_choices_to={"role": "instructor"},
    )
    course = models.ForeignKey("courses.Course", on_delete=models.CASCADE, related_name="instructor_assignments")
    assigned_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="assignments_made",
    )
    assigned_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["instructor", "course"], name="unique_instructor_per_course"
            )
        ]
        indexes = [
            models.Index(fields=["instructor", "status"]),
            models.Index(fields=["course", "status"]),
        ]

    def __str__(self):
        return f"{self.instructor} → {self.course} ({self.status})"
