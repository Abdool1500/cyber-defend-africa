import uuid

from django.conf import settings
from django.db import models


class Quiz(models.Model):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        PUBLISHED = "published", "Published"
        ARCHIVED = "archived", "Archived"

    class QuizType(models.TextChoices):
        STANDARD = "standard", "Standard"
        PRE_TEST = "pre_test", "Pre-Test (Diagnostic)"
        POST_TEST = "post_test", "Post-Test (Final)"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    course = models.ForeignKey("courses.Course", on_delete=models.CASCADE, related_name="quizzes")
    module = models.ForeignKey(
        "courses.CourseModule", on_delete=models.SET_NULL, null=True, blank=True, related_name="quizzes"
    )
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    instructions = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    quiz_type = models.CharField(max_length=20, choices=QuizType.choices, default=QuizType.STANDARD)
    time_limit_minutes = models.PositiveIntegerField(null=True, blank=True)
    attempt_limit = models.PositiveIntegerField(default=1)
    passing_score = models.PositiveIntegerField(default=70, help_text="Passing score as a percentage.")
    shuffle_questions = models.BooleanField(default=True)
    shuffle_options = models.BooleanField(default=True)
    show_score_after_submission = models.BooleanField(default=True)
    show_correct_answers = models.BooleanField(default=False)
    show_explanations = models.BooleanField(default=False)
    available_from = models.DateTimeField(null=True, blank=True)
    available_until = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="quizzes_created"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]
        indexes = [
            models.Index(fields=["course", "status"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["course", "quiz_type"],
                condition=models.Q(quiz_type__in=["pre_test", "post_test"]),
                name="unique_pre_post_test_per_course",
            ),
        ]

    def __str__(self):
        return self.title


class QuizQuestion(models.Model):
    """Manually-selected questions attached to a quiz. Random pools are
    configured separately via QuizRandomRule and resolved at attempt-start
    time — they are not represented here."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name="quiz_questions")
    question = models.ForeignKey("question_bank.Question", on_delete=models.CASCADE, related_name="quiz_links")
    points_override = models.PositiveIntegerField(null=True, blank=True)
    display_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["quiz", "display_order"]
        constraints = [
            models.UniqueConstraint(fields=["quiz", "question"], name="unique_question_per_quiz")
        ]

    def __str__(self):
        return f"{self.quiz.title} — {self.question.question_text[:40]}"

    def points(self):
        return self.points_override or self.question.default_points


class QuizRandomRule(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name="random_rules")
    difficulty = models.CharField(max_length=10, choices=[
        ("easy", "Easy"), ("medium", "Medium"), ("hard", "Hard"),
    ], blank=True)
    topic = models.CharField(max_length=150, blank=True)
    question_type = models.CharField(max_length=20, blank=True)
    number_of_questions = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.quiz.title}: {self.number_of_questions} question(s) ({self.difficulty or 'any difficulty'})"

    def matching_questions(self):
        from apps.question_bank.models import Question

        qs = Question.objects.filter(
            course=self.quiz.course, status=Question.Status.PUBLISHED, is_archived=False
        )
        if self.difficulty:
            qs = qs.filter(difficulty=self.difficulty)
        if self.topic:
            qs = qs.filter(topic=self.topic)
        if self.question_type:
            qs = qs.filter(question_type=self.question_type)
        return qs


class QuizAttempt(models.Model):
    class Status(models.TextChoices):
        IN_PROGRESS = "in_progress", "In Progress"
        SUBMITTED = "submitted", "Submitted"
        PENDING_MANUAL_GRADING = "pending_manual_grading", "Pending Manual Grading"
        GRADED = "graded", "Graded"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name="attempts")
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="quiz_attempts")
    attempt_number = models.PositiveIntegerField()
    started_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    submitted_at = models.DateTimeField(null=True, blank=True)
    score = models.FloatField(null=True, blank=True)
    max_score = models.FloatField(null=True, blank=True)
    percentage = models.FloatField(null=True, blank=True)
    status = models.CharField(max_length=30, choices=Status.choices, default=Status.IN_PROGRESS)
    requires_manual_grading = models.BooleanField(default=False)
    graded_at = models.DateTimeField(null=True, blank=True)
    graded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="attempts_graded"
    )

    class Meta:
        ordering = ["-started_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["quiz", "student", "attempt_number"], name="unique_attempt_number_per_student_quiz"
            )
        ]
        indexes = [
            models.Index(fields=["student", "status"]),
            models.Index(fields=["quiz", "student"]),
        ]

    def __str__(self):
        return f"{self.student} — {self.quiz.title} (attempt {self.attempt_number})"

    @property
    def passed(self):
        if self.percentage is None:
            return None
        return self.percentage >= self.quiz.passing_score


class AttemptQuestion(models.Model):
    """The exact, frozen set of questions (and their order) presented to a
    student for a given attempt. Created once at attempt-start time inside
    a transaction and never regenerated on refresh."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    attempt = models.ForeignKey(QuizAttempt, on_delete=models.CASCADE, related_name="attempt_questions")
    question = models.ForeignKey("question_bank.Question", on_delete=models.PROTECT, related_name="attempt_questions")
    display_order = models.PositiveIntegerField()
    points = models.PositiveIntegerField()
    # Frozen option display order, e.g. [option_id, option_id, ...] — so
    # shuffle_options doesn't reshuffle on every page load/refresh.
    option_order_snapshot = models.JSONField(default=list, blank=True)

    class Meta:
        ordering = ["attempt", "display_order"]
        constraints = [
            models.UniqueConstraint(fields=["attempt", "question"], name="unique_question_per_attempt"),
            models.UniqueConstraint(fields=["attempt", "display_order"], name="unique_order_per_attempt"),
        ]

    def __str__(self):
        return f"{self.attempt} — Q{self.display_order}"


class QuizAnswer(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    attempt = models.ForeignKey(QuizAttempt, on_delete=models.CASCADE, related_name="answers")
    attempt_question = models.OneToOneField(AttemptQuestion, on_delete=models.CASCADE, related_name="answer")
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="quiz_answers")
    selected_options = models.ManyToManyField(
        "question_bank.QuestionOption", blank=True, related_name="selected_in_answers"
    )
    text_answer = models.TextField(blank=True)
    is_correct = models.BooleanField(null=True, blank=True)
    awarded_points = models.FloatField(null=True, blank=True)
    instructor_feedback = models.TextField(blank=True)
    graded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="answers_graded"
    )
    graded_at = models.DateTimeField(null=True, blank=True)
    flagged_for_review = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["student"]),
        ]

    def __str__(self):
        return f"Answer for {self.attempt_question}"
