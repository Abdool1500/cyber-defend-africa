from django.contrib import admin
from django.utils.html import format_html

from apps.core.services.storage import StorageError, get_storage_service

from .models import EmploymentOutcome


@admin.register(EmploymentOutcome)
class EmploymentOutcomeAdmin(admin.ModelAdmin):
    list_display = ["student", "status", "employer", "country", "salary_range", "created_at"]
    list_filter = ["status", "salary_range"]
    search_fields = ["student__email", "employer", "job_title"]
    autocomplete_fields = ["student"]
    readonly_fields = ["evidence_link"]

    @admin.display(description="Evidence")
    def evidence_link(self, obj):
        if not obj.evidence_storage_path:
            return "—"
        try:
            url = get_storage_service().signed_url("employment-evidence", obj.evidence_storage_path)
        except StorageError:
            return "Evidence uploaded, but a signed link could not be generated (Supabase Storage may not be configured yet)."
        return format_html('<a href="{}" target="_blank" rel="noopener noreferrer">View uploaded evidence</a>', url)
