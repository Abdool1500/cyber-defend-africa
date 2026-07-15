import uuid

from django.conf import settings
from django.db import models


class StudentFeedback(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="feedback_submitted")
    course = models.ForeignKey("courses.Course", on_delete=models.CASCADE, related_name="feedback")
    instructor = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="feedback_received"
    )
    overall_rating = models.PositiveSmallIntegerField()
    content_quality = models.PositiveSmallIntegerField()
    instructor_effectiveness = models.PositiveSmallIntegerField(null=True, blank=True)
    practical_lab_quality = models.PositiveSmallIntegerField()
    platform_experience = models.PositiveSmallIntegerField()
    difficulty = models.PositiveSmallIntegerField(help_text="1 = Very Easy, 5 = Very Difficult")
    confidence_before = models.PositiveSmallIntegerField(help_text="1 = Not at all confident, 5 = Very confident")
    confidence_after = models.PositiveSmallIntegerField(help_text="1 = Not at all confident, 5 = Very confident")
    nps_score = models.PositiveSmallIntegerField(
        help_text="0-10: How likely are you to recommend this course to a friend or colleague?"
    )
    most_helpful = models.TextField(blank=True)
    improvement_suggestions = models.TextField(blank=True)
    additional_comments = models.TextField(blank=True)
    is_anonymous = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(fields=["student", "course"], name="one_feedback_per_student_per_course"),
            models.CheckConstraint(
                check=models.Q(overall_rating__gte=1, overall_rating__lte=5), name="overall_rating_1_to_5"
            ),
            models.CheckConstraint(
                check=models.Q(content_quality__gte=1, content_quality__lte=5), name="content_quality_1_to_5"
            ),
            models.CheckConstraint(
                check=models.Q(practical_lab_quality__gte=1, practical_lab_quality__lte=5),
                name="lab_quality_1_to_5",
            ),
            models.CheckConstraint(
                check=models.Q(platform_experience__gte=1, platform_experience__lte=5),
                name="platform_experience_1_to_5",
            ),
            models.CheckConstraint(
                check=models.Q(instructor_effectiveness__isnull=True)
                | models.Q(instructor_effectiveness__gte=1, instructor_effectiveness__lte=5),
                name="instructor_effectiveness_1_to_5_or_null",
            ),
            models.CheckConstraint(
                check=models.Q(difficulty__gte=1, difficulty__lte=5), name="difficulty_1_to_5"
            ),
            models.CheckConstraint(
                check=models.Q(confidence_before__gte=1, confidence_before__lte=5),
                name="confidence_before_1_to_5",
            ),
            models.CheckConstraint(
                check=models.Q(confidence_after__gte=1, confidence_after__lte=5),
                name="confidence_after_1_to_5",
            ),
            models.CheckConstraint(
                check=models.Q(nps_score__gte=0, nps_score__lte=10), name="nps_score_0_to_10"
            ),
        ]
        indexes = [
            models.Index(fields=["course"]),
            models.Index(fields=["instructor"]),
        ]

    def __str__(self):
        return f"Feedback on {self.course} ({'anonymous' if self.is_anonymous else self.student})"

    def display_name(self):
        """The only place feedback identity should be resolved for
        instructor-facing display — anonymous feedback never reveals the
        student, even to the course's own instructor."""
        return "Anonymous Student" if self.is_anonymous else self.student.full_name
