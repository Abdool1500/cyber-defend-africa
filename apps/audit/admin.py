from django.contrib import admin

from .models import AuditLog


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ["action", "entity_type", "entity_id", "actor", "created_at"]
    list_filter = ["action", "entity_type"]
    search_fields = ["actor__email", "entity_id"]
    readonly_fields = ["id", "actor", "action", "entity_type", "entity_id", "metadata", "created_at"]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
