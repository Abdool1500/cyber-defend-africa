from django.contrib import admin

from .models import LabProgress, PracticalLab


@admin.register(PracticalLab)
class PracticalLabAdmin(admin.ModelAdmin):
    list_display = ["title", "course", "category", "status", "max_score"]
    list_filter = ["category", "status"]
    search_fields = ["title", "course__title"]
    autocomplete_fields = ["course", "module", "created_by"]


@admin.register(LabProgress)
class LabProgressAdmin(admin.ModelAdmin):
    list_display = ["student", "lab", "status", "attempts", "score", "started_at", "completed_at"]
    list_filter = ["status"]
    search_fields = ["student__email", "lab__title"]
    autocomplete_fields = ["lab", "student", "graded_by"]
