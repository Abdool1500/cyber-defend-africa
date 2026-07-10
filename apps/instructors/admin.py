from django.contrib import admin

from .models import InstructorAssignment


@admin.register(InstructorAssignment)
class InstructorAssignmentAdmin(admin.ModelAdmin):
    list_display = ["instructor", "course", "status", "assigned_by", "assigned_at"]
    list_filter = ["status"]
    search_fields = ["instructor__email", "course__title"]
    autocomplete_fields = ["instructor", "course", "assigned_by"]
