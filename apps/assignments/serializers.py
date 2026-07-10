from rest_framework import serializers

from .models import Assignment, AssignmentSubmission


class AssignmentSerializer(serializers.ModelSerializer):
    course_title = serializers.CharField(source="course.title", read_only=True)

    class Meta:
        model = Assignment
        fields = ["id", "course", "course_title", "title", "description", "due_at", "max_points", "status"]
        read_only_fields = fields


class AssignmentSubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssignmentSubmission
        fields = [
            "id", "assignment", "text_submission", "submitted_at", "status", "score", "instructor_feedback",
        ]
        read_only_fields = ["id", "submitted_at", "status", "score", "instructor_feedback"]
