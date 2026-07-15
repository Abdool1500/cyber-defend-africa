from django.contrib import admin

from .models import StudentFeedback


@admin.register(StudentFeedback)
class StudentFeedbackAdmin(admin.ModelAdmin):
    list_display = ["course", "anonymized_student", "overall_rating", "nps_score", "is_anonymous", "created_at"]
    list_filter = ["is_anonymous", "course"]
    readonly_fields = ["id", "created_at", "updated_at"]

    def anonymized_student(self, obj):
        return obj.display_name()
    anonymized_student.short_description = "Respondent"
