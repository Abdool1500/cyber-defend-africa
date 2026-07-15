# Graduate employment outcome self-reporting — see tasks/todo.md
# Phase 16.H.
import uuid

from django.conf import settings
from django.db import models


class EmploymentOutcome(models.Model):
    """Append-only history log — one row per self-reported update, not
    one row per student. A student's "current" status is their most
    recent row. This preserves the actual career timeline (seeking ->
    internship -> employed -> promoted) instead of silently overwriting
    it, which is what genuine impact reporting needs — "students
    should update these after graduation" (spec) implies a sequence of
    updates, not a single mutable snapshot."""

    class Status(models.TextChoices):
        SEEKING = "seeking", "Seeking Employment"
        INTERNSHIP = "internship", "Internship"
        FREELANCING = "freelancing", "Freelancing"
        BUSINESS_OWNER = "business_owner", "Business Owner"
        EMPLOYED_FULL_TIME = "employed_full_time", "Employed Full-Time"
        EMPLOYED_PART_TIME = "employed_part_time", "Employed Part-Time"
        PROMOTED = "promoted", "Promoted"
        UNEMPLOYED = "unemployed", "Unemployed"

    class SalaryRange(models.TextChoices):
        """Bucketed ranges only — never an exact figure. Optional."""
        UNDER_50K = "under_50k", "Under $50,000/year (or local equivalent)"
        R50K_100K = "50k_100k", "$50,000 - $100,000/year"
        R100K_150K = "100k_150k", "$100,000 - $150,000/year"
        OVER_150K = "over_150k", "Over $150,000/year"
        PREFER_NOT_TO_SAY = "prefer_not_to_say", "Prefer not to say"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="employment_outcomes",
    )
    status = models.CharField(max_length=30, choices=Status.choices)
    employer = models.CharField(max_length=200, blank=True)
    job_title = models.CharField(max_length=150, blank=True)
    country = models.CharField(max_length=100, blank=True)
    date_employed = models.DateField(null=True, blank=True)
    salary_range = models.CharField(max_length=30, choices=SalaryRange.choices, null=True, blank=True)
    how_academy_helped = models.TextField(blank=True)
    evidence_storage_path = models.CharField(max_length=500, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["student", "-created_at"]),
        ]

    def __str__(self):
        return f"{self.student} — {self.get_status_display()} ({self.created_at:%Y-%m-%d})"
