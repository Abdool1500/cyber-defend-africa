from rest_framework import serializers

from .models import StudentFeedback


class StudentFeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentFeedback
        fields = [
            "id", "course", "overall_rating", "content_quality", "instructor_effectiveness",
            "practical_lab_quality", "platform_experience", "most_helpful",
            "improvement_suggestions", "additional_comments", "is_anonymous", "created_at",
        ]
        read_only_fields = ["id", "created_at"]
