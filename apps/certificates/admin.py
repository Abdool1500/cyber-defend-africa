from django.contrib import admin

from apps.audit.services import log_action

from .models import Certificate


@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = ["certificate_number", "student", "course", "status", "issued_at", "hash_is_valid"]
    list_filter = ["status"]
    search_fields = ["certificate_number", "verification_code", "student__email"]
    # student/course/certificate_hash are locked after issuance — a
    # certificate's identity shouldn't change post-issuance, and
    # certificate_hash exists specifically to make it detectable if it
    # ever does (see Certificate.hash_is_valid()). Only applied on
    # change, not add (see get_readonly_fields) — student/course have
    # no default and are required, so making them unconditionally
    # readonly made the add form incapable of ever creating a
    # certificate (16.Q finding: confirmed empirically, not theoretical
    # — the add form rendered with no student/course inputs at all).
    readonly_fields = [
        "id", "student", "course", "certificate_number", "verification_code",
        "certificate_hash", "issued_at",
    ]

    def get_readonly_fields(self, request, obj=None):
        if obj is None:
            # certificate_number/verification_code/certificate_hash stay
            # readonly even on add — they auto-generate in Certificate.save()
            # when blank, so leaving them out of the form entirely (rather
            # than requiring blank input, which the ModelForm would reject)
            # is correct, not just "locked". Only student/course genuinely
            # need to be enterable to create a certificate at all.
            return ["id", "certificate_number", "verification_code", "certificate_hash", "issued_at"]
        return self.readonly_fields

    @admin.display(boolean=True, description="Hash valid")
    def hash_is_valid(self, obj):
        return obj.hash_is_valid()

    def save_model(self, request, obj, form, change):
        # apps.audit.services.log_action's own docstring names
        # "certificate issuance/revocation" as one of the actions that
        # must be logged — this was never wired up (16.Q finding), since
        # Certificate has no application code path other than Admin.
        previous_status = None
        if change:
            previous_status = Certificate.objects.filter(pk=obj.pk).values_list("status", flat=True).first()

        super().save_model(request, obj, form, change)

        if not change:
            log_action(request.user, "certificate.issue", obj, {"status": obj.status})
        elif previous_status != obj.status:
            log_action(
                request.user, "certificate.status_change", obj,
                {"from": previous_status, "to": obj.status},
            )
