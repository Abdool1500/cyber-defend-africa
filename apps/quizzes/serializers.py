from rest_framework import serializers

from .models import Quiz, QuizAttempt


class QuizSerializer(serializers.ModelSerializer):
    course_title = serializers.CharField(source="course.title", read_only=True)

    class Meta:
        model = Quiz
        fields = [
            "id", "course", "course_title", "title", "description", "status",
            "time_limit_minutes", "attempt_limit", "passing_score",
            "available_from", "available_until",
        ]
        read_only_fields = fields


class QuizAttemptSerializer(serializers.ModelSerializer):
    """Deliberately excludes any per-question/answer detail — attempt
    results are for status/score summary only. Correct answers are never
    served through this (or any) API endpoint to students."""

    quiz_title = serializers.CharField(source="quiz.title", read_only=True)

    class Meta:
        model = QuizAttempt
        fields = [
            "id", "quiz", "quiz_title", "attempt_number", "started_at", "submitted_at",
            "status", "score", "max_score", "percentage",
        ]
        read_only_fields = fields
