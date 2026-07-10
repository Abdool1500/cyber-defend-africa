from rest_framework import serializers

from .models import Enrollment


class EnrollmentSerializer(serializers.ModelSerializer):
    course_title = serializers.CharField(source="course.title", read_only=True)

    class Meta:
        model = Enrollment
        fields = ["id", "course", "course_title", "status", "enrolled_at", "completed_at", "progress_percentage"]
        read_only_fields = fields
