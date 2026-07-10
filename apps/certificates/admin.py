from django.contrib import admin

from .models import Certificate


@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = ["certificate_number", "student", "course", "status", "issued_at"]
    list_filter = ["status"]
    search_fields = ["certificate_number", "verification_code", "student__email"]
    readonly_fields = ["id", "certificate_number", "verification_code", "issued_at"]
