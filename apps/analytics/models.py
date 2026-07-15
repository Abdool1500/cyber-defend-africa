# Aggregation services, Impact Dashboard, FID report, and analytics API
# — see tasks/todo.md Phase 16.J/16.K/16.M/16.P.
import uuid

from django.conf import settings
from django.db import models


class LearningSession(models.Model):
    """One row per login, closed on logout (or capped if abandoned
    without an explicit logout — see signals.py). This tracks time *on
    the platform*, which is a different thing from actual content
    engagement — see LearningTimeEntry for that. Kept for every
    authenticated user (not just students) since it also feeds
    platform-wide DAU/MAU reporting later (Phase 16.J)."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="learning_sessions")
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-started_at"]
        indexes = [
            models.Index(fields=["user", "started_at"]),
        ]

    def __str__(self):
        return f"{self.user} session started {self.started_at}"


class LearningTimeEntry(models.Model):
    """Per-day, per-lesson accumulated time-on-task, fed by a periodic
    heartbeat from the lesson-viewing page (see
    apps.enrollments.student_views.lesson_heartbeat). One row per
    (student, lesson, date) — never a single cumulative counter — so
    today/weekly/monthly/lifetime aggregates are all simple date-range
    sums over the same source of truth, and per-lesson/per-course/
    per-content-type breakdowns are simple joins through `lesson`."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="learning_time_entries"
    )
    lesson = models.ForeignKey("courses.Lesson", on_delete=models.CASCADE, related_name="time_entries")
    date = models.DateField()
    seconds = models.PositiveIntegerField(default=0)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["student", "lesson", "date"], name="unique_time_entry_per_student_lesson_day"
            ),
        ]
        indexes = [
            models.Index(fields=["student", "date"]),
        ]

    def __str__(self):
        return f"{self.student} — {self.lesson} on {self.date}: {self.seconds}s"


class ImpactSnapshot(models.Model):
    """Admin-entered figures for impact KPIs that can't be derived from
    any tracked LMS event (no "SME protected" or "business started"
    event exists anywhere in this system) — self-reported, and always
    rendered separately from the genuinely-computed stats on the Impact
    Dashboard so it's never unclear which numbers are measured vs.
    self-reported. Append-only, like EmploymentOutcome: each save is a
    new dated record rather than an overwrite, so the "current" figures
    are simply the most recent row, and past snapshots remain as a
    history of how these self-reported figures changed over time.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    smes_protected = models.PositiveIntegerField(default=0, help_text="SMEs protected from cyber threats")
    healthcare_workers_trained = models.PositiveIntegerField(default=0)
    businesses_started = models.PositiveIntegerField(
        default=0, help_text="Businesses started by graduates as a direct result of training"
    )
    notes = models.TextField(blank=True, help_text="Source/context for these figures (e.g. survey, partner report)")
    recorded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="impact_snapshots"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Impact Snapshot {self.created_at:%Y-%m-%d}"
