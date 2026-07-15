# Cohort grouping + per-cohort analytics — see tasks/todo.md Phase 16.F.
import uuid

from django.conf import settings
from django.db import models


class Cohort(models.Model):
    """A named group of students for impact reporting — e.g. "January
    2026", "Women in Cybersecurity", "Government Training". Not
    course-specific: a cohort can span any number of courses, and a
    student can belong to more than one cohort (a time-based intake
    cohort and a demographic/program cohort at once), hence the
    separate CohortMembership through-model rather than a FK on User."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=150, unique=True)
    description = models.TextField(blank=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="cohorts_created"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.name


class CohortMembership(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    cohort = models.ForeignKey(Cohort, on_delete=models.CASCADE, related_name="memberships")
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="cohort_memberships",
        limit_choices_to={"role": "student"},
    )
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-joined_at"]
        constraints = [
            models.UniqueConstraint(fields=["cohort", "student"], name="unique_membership_per_cohort_student"),
        ]
        indexes = [
            models.Index(fields=["cohort"]),
        ]

    def __str__(self):
        return f"{self.student} in {self.cohort}"
