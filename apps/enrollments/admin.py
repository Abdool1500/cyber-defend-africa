from django.contrib import admin

from .models import Enrollment, LessonProgress


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ["student", "course", "status", "progress_percentage", "enrolled_at"]
    list_filter = ["status"]
    search_fields = ["student__email", "course__title"]
    autocomplete_fields = ["student", "course"]


@admin.register(LessonProgress)
class LessonProgressAdmin(admin.ModelAdmin):
    list_display = ["student", "lesson", "completed", "last_accessed_at"]
    list_filter = ["completed"]
    search_fields = ["student__email", "lesson__title"]
    autocomplete_fields = ["student", "lesson"]
