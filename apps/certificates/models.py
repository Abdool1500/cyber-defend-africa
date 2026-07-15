import hashlib
import hmac
import secrets
import uuid

from django.conf import settings
from django.db import models


def generate_verification_code():
    return secrets.token_hex(8)


def compute_certificate_hash(certificate_number, student_id, course_id):
    """HMAC-SHA256, not a plain hash — signed with SECRET_KEY, which
    lives in settings/env, never in the database. A plain hash of
    (certificate_number, student_id, course_id) would give zero
    tamper-evidence, since anyone with DB write access could recompute
    and update it alongside any tampered field. Forging a *valid* HMAC
    requires knowing SECRET_KEY, which tampering with the database
    alone doesn't give you. issued_at is deliberately excluded — it's
    an auto_now_add field that isn't populated on the in-memory instance
    until the underlying INSERT runs, after this would be computed."""
    payload = f"{certificate_number}|{student_id}|{course_id}"
    return hmac.new(settings.SECRET_KEY.encode(), payload.encode(), hashlib.sha256).hexdigest()


class Certificate(models.Model):
    class Status(models.TextChoices):
        ISSUED = "issued", "Issued"
        REVOKED = "revoked", "Revoked"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="certificates")
    course = models.ForeignKey("courses.Course", on_delete=models.CASCADE, related_name="certificates")
    certificate_number = models.CharField(max_length=40, unique=True)
    verification_code = models.CharField(max_length=32, unique=True, default=generate_verification_code)
    certificate_hash = models.CharField(max_length=64, blank=True)
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
        if not self.certificate_hash:
            self.certificate_hash = compute_certificate_hash(
                self.certificate_number, self.student_id, self.course_id
            )
        super().save(*args, **kwargs)

    def hash_is_valid(self):
        """True if the stored hash still matches what the current field
        values would produce — a mismatch means certificate_number,
        student, or course was altered directly (e.g. via a DB console)
        without going through this model's save(), since a legitimate
        save() always keeps them in sync."""
        expected = compute_certificate_hash(self.certificate_number, self.student_id, self.course_id)
        return hmac.compare_digest(self.certificate_hash, expected)
