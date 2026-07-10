from rest_framework import serializers

from .models import Course, CourseModule, Lesson


class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = [
            "id", "title", "slug", "lesson_type", "display_order",
            "estimated_minutes", "is_preview", "video_url",
        ]


class CourseModuleSerializer(serializers.ModelSerializer):
    lessons = LessonSerializer(many=True, read_only=True)

    class Meta:
        model = CourseModule
        fields = ["id", "title", "description", "display_order", "lessons"]


class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = [
            "id", "title", "slug", "short_description", "description",
            "category", "level", "estimated_duration", "status", "published_at",
        ]


class CourseDetailSerializer(CourseSerializer):
    modules = CourseModuleSerializer(many=True, read_only=True)

    class Meta(CourseSerializer.Meta):
        fields = CourseSerializer.Meta.fields + ["modules"]
