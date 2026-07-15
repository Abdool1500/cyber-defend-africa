import uuid

from django.conf import settings
from django.db import models


class PracticalLab(models.Model):
    """A hands-on cybersecurity lab exercise, scoped to a course — same
    shape as Assignment (course-scoped, instructor-authored, student
    submits, instructor grades), since that's the closest existing
    pattern in this codebase for "student does work, instructor scores
    it"."""

    class Category(models.TextChoices):
        LINUX = "linux", "Linux"
        NETWORKING = "networking", "Networking"
        NMAP = "nmap", "Nmap"
        WIRESHARK = "wireshark", "Wireshark"
        BURP_SUITE = "burp_suite", "Burp Suite"
        OWASP = "owasp", "OWASP"
        WEB_SECURITY = "web_security", "Web Security"
        SOC = "soc", "SOC Labs"
        THREAT_HUNTING = "threat_hunting", "Threat Hunting"
        DIGITAL_FORENSICS = "digital_forensics", "Digital Forensics"
        CLOUD_SECURITY = "cloud_security", "Cloud Security"
        PYTHON_SECURITY_AUTOMATION = "python_security_automation", "Python Security Automation"
        AI_SECURITY_ENGINEERING = "ai_security_engineering", "AI Security Engineering"

    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        PUBLISHED = "published", "Published"
        ARCHIVED = "archived", "Archived"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    course = models.ForeignKey("courses.Course", on_delete=models.CASCADE, related_name="practical_labs")
    module = models.ForeignKey(
        "courses.CourseModule", on_delete=models.SET_NULL, null=True, blank=True, related_name="practical_labs"
    )
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    instructions = models.TextField(blank=True)
    category = models.CharField(max_length=40, choices=Category.choices)
    max_score = models.PositiveIntegerField(default=100)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    allow_resubmission = models.BooleanField(
        default=True,
        help_text="If enabled, a student may restart this lab before it is graded.",
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="practical_labs_created"
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


class LabProgress(models.Model):
    """One row per (lab, student) — "Not Started" is simply the absence
    of a row, matching how LessonProgress represents lesson state."""

    class Status(models.TextChoices):
        IN_PROGRESS = "in_progress", "In Progress"
        COMPLETED = "completed", "Completed"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    lab = models.ForeignKey(PracticalLab, on_delete=models.CASCADE, related_name="progress_records")
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="lab_progress")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.IN_PROGRESS)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    attempts = models.PositiveIntegerField(default=1)
    score = models.FloatField(null=True, blank=True)
    instructor_feedback = models.TextField(blank=True)
    graded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="lab_progress_graded",
    )
    graded_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-started_at"]
        constraints = [
            models.UniqueConstraint(fields=["lab", "student"], name="unique_progress_per_student_lab"),
        ]
        indexes = [
            models.Index(fields=["student", "status"]),
        ]

    def __str__(self):
        return f"{self.student} — {self.lab.title} ({self.status})"

    @property
    def completion_duration(self):
        if not self.completed_at:
            return None
        return self.completed_at - self.started_at

    @property
    def is_graded(self):
        return self.score is not None
