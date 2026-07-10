import uuid

from django.conf import settings
from django.db import models


class Question(models.Model):
    class QuestionType(models.TextChoices):
        MULTIPLE_CHOICE = "multiple_choice", "Multiple Choice"
        MULTIPLE_SELECT = "multiple_select", "Multiple Select"
        TRUE_FALSE = "true_false", "True/False"
        SHORT_ANSWER = "short_answer", "Short Answer"

    class Difficulty(models.TextChoices):
        EASY = "easy", "Easy"
        MEDIUM = "medium", "Medium"
        HARD = "hard", "Hard"

    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        PUBLISHED = "published", "Published"
        ARCHIVED = "archived", "Archived"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    course = models.ForeignKey("courses.Course", on_delete=models.CASCADE, related_name="questions")
    module = models.ForeignKey(
        "courses.CourseModule", on_delete=models.SET_NULL, null=True, blank=True, related_name="questions"
    )
    topic = models.CharField(max_length=150, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="questions_created"
    )
    question_type = models.CharField(max_length=20, choices=QuestionType.choices)
    question_text = models.TextField()
    explanation = models.TextField(blank=True)
    model_answer = models.TextField(blank=True)
    grading_guidance = models.TextField(blank=True)
    difficulty = models.CharField(max_length=10, choices=Difficulty.choices, default=Difficulty.MEDIUM)
    default_points = models.PositiveIntegerField(default=1)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    is_archived = models.BooleanField(default=False)

    # Set once a question has been used in a submitted attempt — after that
    # point, edits must go through duplication rather than in-place changes
    # so historical attempt data keeps its original meaning (spec 46).
    is_locked = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]
        indexes = [
            models.Index(fields=["course", "status"]),
            models.Index(fields=["difficulty"]),
            models.Index(fields=["question_type"]),
        ]

    def __str__(self):
        return self.question_text[:60]

    def mark_locked_if_used(self):
        if self.attempt_questions.exists() and not self.is_locked:
            self.is_locked = True
            self.save(update_fields=["is_locked"])


class QuestionOption(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="options")
    option_text = models.CharField(max_length=500)
    is_correct = models.BooleanField(default=False)
    display_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["question", "display_order"]

    def __str__(self):
        return self.option_text[:60]
