from rest_framework import serializers

from .models import Question, QuestionOption


class QuestionOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionOption
        fields = ["id", "option_text", "is_correct", "display_order"]


class QuestionSerializer(serializers.ModelSerializer):
    """Instructor/admin-only serializer — includes is_correct and other
    fields that must never reach a student-facing endpoint. Nothing in
    apps/question_bank is wired into any AllowAny/IsAuthenticated-only
    (student-accessible) route; see api_permissions.IsInstructor."""

    options = QuestionOptionSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = [
            "id", "course", "module", "topic", "question_type", "question_text",
            "explanation", "model_answer", "grading_guidance", "difficulty",
            "default_points", "status", "is_locked", "options", "created_at", "updated_at",
        ]
        read_only_fields = ["id", "is_locked", "created_at", "updated_at"]
