from django.contrib import admin

from .models import ImpactSnapshot, LearningSession, LearningTimeEntry


@admin.register(LearningSession)
class LearningSessionAdmin(admin.ModelAdmin):
    list_display = ["user", "started_at", "ended_at"]
    list_filter = ["started_at"]
    search_fields = ["user__email"]
    autocomplete_fields = ["user"]


@admin.register(LearningTimeEntry)
class LearningTimeEntryAdmin(admin.ModelAdmin):
    list_display = ["student", "lesson", "date", "seconds"]
    list_filter = ["date"]
    search_fields = ["student__email", "lesson__title"]
    autocomplete_fields = ["student", "lesson"]


@admin.register(ImpactSnapshot)
class ImpactSnapshotAdmin(admin.ModelAdmin):
    list_display = [
        "created_at", "smes_protected", "healthcare_workers_trained", "businesses_started", "recorded_by",
    ]
    readonly_fields = ["created_at", "recorded_by"]

    def save_model(self, request, obj, form, change):
        if not change:
            obj.recorded_by = request.user
        super().save_model(request, obj, form, change)
