from django.contrib import admin

from .models import Assignment, AssignmentSubmission


@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ["title", "course", "status", "due_at", "max_points"]
    list_filter = ["status", "course"]
    search_fields = ["title"]


@admin.register(AssignmentSubmission)
class AssignmentSubmissionAdmin(admin.ModelAdmin):
    list_display = ["assignment", "student", "status", "score", "submitted_at"]
    list_filter = ["status"]
    search_fields = ["assignment__title", "student__email"]
    readonly_fields = ["id", "submitted_at", "updated_at"]
