from django.test import TestCase
from django.urls import reverse

from apps.accounts.models import User
from apps.courses.models import Course

from .models import Certificate


class CertificateVerificationTests(TestCase):
    def setUp(self):
        self.course = Course.objects.create(
            title="Course", slug="course", short_description="C", description="C",
            status=Course.Status.PUBLISHED,
        )
        self.student = User.objects.create_user(
            email="student@example.com", password="pass1234", full_name="Graduate Student",
            role=User.Role.STUDENT, status=User.Status.ACTIVE,
        )
        self.certificate = Certificate.objects.create(student=self.student, course=self.course)

    def test_valid_certificate_verifies_successfully(self):
        response = self.client.get(reverse("certificates:verify", args=[self.certificate.verification_code]))
        self.assertContains(response, "Valid Certificate")
        self.assertContains(response, "Graduate Student")

    def test_revoked_certificate_shows_revoked_status(self):
        self.certificate.status = Certificate.Status.REVOKED
        self.certificate.save()
        response = self.client.get(reverse("certificates:verify", args=[self.certificate.verification_code]))
        self.assertContains(response, "revoked")

    def test_unknown_code_shows_not_found(self):
        response = self.client.get(reverse("certificates:verify", args=["doesnotexist"]))
        self.assertContains(response, "No certificate was found")

    def test_certificate_number_is_generated_automatically(self):
        self.assertTrue(self.certificate.certificate_number.startswith("CDA-"))

    def test_duplicate_certificate_per_student_course_blocked(self):
        from django.db import IntegrityError, transaction

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Certificate.objects.create(student=self.student, course=self.course)
