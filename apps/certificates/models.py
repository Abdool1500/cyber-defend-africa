import secrets
import uuid

from django.conf import settings
from django.db import models


def generate_verification_code():
    return secrets.token_hex(8)


class Certificate(models.Model):
    class Status(models.TextChoices):
        ISSUED = "issued", "Issued"
        REVOKED = "revoked", "Revoked"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="certificates")
    course = models.ForeignKey("courses.Course", on_delete=models.CASCADE, related_name="certificates")
    certificate_number = models.CharField(max_length=40, unique=True)
    verification_code = models.CharField(max_length=32, unique=True, default=generate_verification_code)
    issued_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ISSUED)
    certificate_storage_path = models.CharField(max_length=500, null=True, blank=True)

    class Meta:
        ordering = ["-issued_at"]
        constraints = [
            models.UniqueConstraint(fields=["student", "course"], name="unique_certificate_per_student_course")
        ]

    def __str__(self):
        return f"{self.certificate_number} — {self.student} — {self.course}"

    def save(self, *args, **kwargs):
        if not self.certificate_number:
            self.certificate_number = f"CDA-{self.course_id.hex[:6].upper()}-{secrets.token_hex(4).upper()}"
        super().save(*args, **kwargs)
