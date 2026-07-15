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


class CertificateHashTests(TestCase):
    def setUp(self):
        self.course = Course.objects.create(
            title="Hash Course", slug="hash-course", short_description="C", description="C",
            status=Course.Status.PUBLISHED,
        )
        self.student = User.objects.create_user(
            email="hashstudent@example.com", password="pass1234", full_name="Hash Student",
            role=User.Role.STUDENT, status=User.Status.ACTIVE,
        )

    def test_hash_is_generated_on_creation(self):
        certificate = Certificate.objects.create(student=self.student, course=self.course)
        self.assertTrue(certificate.certificate_hash)
        self.assertEqual(len(certificate.certificate_hash), 64)  # sha256 hex digest

    def test_hash_is_valid_for_untampered_certificate(self):
        certificate = Certificate.objects.create(student=self.student, course=self.course)
        self.assertTrue(certificate.hash_is_valid())

    def test_hash_invalid_after_direct_field_tampering(self):
        """Simulates a certificate_number altered directly (e.g. via a
        DB console or a bug), bypassing save()'s hash recomputation —
        this is exactly the scenario certificate_hash exists to catch."""
        certificate = Certificate.objects.create(student=self.student, course=self.course)
        Certificate.objects.filter(pk=certificate.pk).update(certificate_number="CDA-TAMPERED-0000")
        certificate.refresh_from_db()
        self.assertFalse(certificate.hash_is_valid())

    def test_different_certificates_get_different_hashes(self):
        other_student = User.objects.create_user(
            email="hashstudent2@example.com", password="pass1234", full_name="Hash Student 2",
            role=User.Role.STUDENT, status=User.Status.ACTIVE,
        )
        cert1 = Certificate.objects.create(student=self.student, course=self.course)
        cert2 = Certificate.objects.create(student=other_student, course=self.course)
        self.assertNotEqual(cert1.certificate_hash, cert2.certificate_hash)

    def test_hash_cannot_be_forged_without_secret_key(self):
        """A plain hash (e.g. sha256 with no key) could be recomputed by
        anyone with DB access to match tampered data. Confirms this one
        actually depends on SECRET_KEY, not just the visible fields."""
        import hashlib

        certificate = Certificate.objects.create(student=self.student, course=self.course)
        naive_hash = hashlib.sha256(
            f"{certificate.certificate_number}|{certificate.student_id}|{certificate.course_id}".encode()
        ).hexdigest()
        self.assertNotEqual(certificate.certificate_hash, naive_hash)


class CertificateQRCodeTests(TestCase):
    def setUp(self):
        self.course = Course.objects.create(
            title="QR Course", slug="qr-course", short_description="C", description="C",
            status=Course.Status.PUBLISHED,
        )
        self.student = User.objects.create_user(
            email="qrstudent@example.com", password="pass1234", full_name="QR Student",
            role=User.Role.STUDENT, status=User.Status.ACTIVE,
        )
        self.certificate = Certificate.objects.create(student=self.student, course=self.course)

    def test_qr_code_returns_png_for_valid_certificate(self):
        response = self.client.get(reverse("certificates:qr_code", args=[self.certificate.verification_code]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "image/png")
        self.assertTrue(response.content.startswith(b"\x89PNG"))

    def test_qr_code_404_for_unknown_code(self):
        response = self.client.get(reverse("certificates:qr_code", args=["doesnotexist"]))
        self.assertEqual(response.status_code, 404)

    def test_verification_page_embeds_qr_image(self):
        response = self.client.get(reverse("certificates:verify", args=[self.certificate.verification_code]))
        self.assertContains(response, reverse("certificates:qr_code", args=[self.certificate.verification_code]))


class CertificateVerificationPageContentTests(TestCase):
    def setUp(self):
        self.course = Course.objects.create(
            title="Content Course", slug="content-course", short_description="C", description="C",
            status=Course.Status.PUBLISHED,
        )
        self.student = User.objects.create_user(
            email="contentstudent@example.com", password="pass1234", full_name="Content Student",
            role=User.Role.STUDENT, status=User.Status.ACTIVE,
        )
        self.certificate = Certificate.objects.create(student=self.student, course=self.course)

    def test_shows_certificate_hash(self):
        response = self.client.get(reverse("certificates:verify", args=[self.certificate.verification_code]))
        self.assertContains(response, self.certificate.certificate_hash)

    def test_shows_verification_url(self):
        response = self.client.get(reverse("certificates:verify", args=[self.certificate.verification_code]))
        expected_path = reverse("certificates:verify", args=[self.certificate.verification_code])
        self.assertContains(response, expected_path)

    def test_shows_instructor_name_when_assigned(self):
        from apps.instructors.models import InstructorAssignment

        instructor = User.objects.create_user(
            email="certinstructor@example.com", password="pass1234", full_name="Cert Instructor",
            role=User.Role.INSTRUCTOR, status=User.Status.ACTIVE,
        )
        InstructorAssignment.objects.create(
            instructor=instructor, course=self.course, status=InstructorAssignment.Status.ACTIVE,
        )
        response = self.client.get(reverse("certificates:verify", args=[self.certificate.verification_code]))
        self.assertContains(response, "Cert Instructor")

    def test_shows_dash_when_no_instructor_assigned(self):
        response = self.client.get(reverse("certificates:verify", args=[self.certificate.verification_code]))
        self.assertContains(response, "—")


class CertificateAPITests(TestCase):
    def setUp(self):
        self.course = Course.objects.create(
            title="API Course", slug="api-course", short_description="C", description="C",
            status=Course.Status.PUBLISHED,
        )
        self.student = User.objects.create_user(
            email="certapistudent@example.com", password="pass1234", full_name="Cert API Student",
            role=User.Role.STUDENT, status=User.Status.ACTIVE,
        )
        self.other_student = User.objects.create_user(
            email="othercertapistudent@example.com", password="pass1234", full_name="Other Student",
            role=User.Role.STUDENT, status=User.Status.ACTIVE,
        )
        self.certificate = Certificate.objects.create(student=self.student, course=self.course)

    def test_student_sees_only_their_own_certificates(self):
        Certificate.objects.create(
            student=self.other_student,
            course=Course.objects.create(
                title="Other Course", slug="other-course", short_description="C", description="C",
                status=Course.Status.PUBLISHED,
            ),
        )
        self.client.login(username="certapistudent@example.com", password="pass1234")
        response = self.client.get(reverse("api-v1:api-certificate-list"))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data["results"]), 1)
        self.assertEqual(data["results"][0]["course_title"], "API Course")

    def test_api_never_exposes_storage_path(self):
        self.certificate.certificate_storage_path = "certificates/some/internal/path.pdf"
        self.certificate.save()
        self.client.login(username="certapistudent@example.com", password="pass1234")
        response = self.client.get(reverse("api-v1:api-certificate-list"))
        self.assertNotIn("certificate_storage_path", response.content.decode())
        self.assertNotIn("internal/path.pdf", response.content.decode())

    def test_anonymous_cannot_access_certificate_api(self):
        response = self.client.get(reverse("api-v1:api-certificate-list"))
        self.assertEqual(response.status_code, 403)


class CertificateAdminTests(TestCase):
    """16.Q data-quality fixes: (1) the add form was unusable because
    student/course were unconditionally readonly, and (2) certificate
    issuance/revocation via Admin was never audit-logged despite
    apps.audit.services.log_action's own docstring naming it."""

    def setUp(self):
        from apps.audit.models import AuditLog

        self.AuditLog = AuditLog
        self.admin = User.objects.create_superuser(
            email="certadminuser@example.com", password="pass1234", full_name="Cert Admin",
        )
        self.student = User.objects.create_user(
            email="certadminstudent@example.com", password="pass1234", full_name="Cert Admin Student",
            role=User.Role.STUDENT, status=User.Status.ACTIVE,
        )
        self.course = Course.objects.create(
            title="Cert Admin Course", slug="cert-admin-course", short_description="x", description="x",
            status=Course.Status.PUBLISHED,
        )
        self.client.force_login(self.admin)

    def test_add_form_renders_student_and_course_fields(self):
        response = self.client.get(reverse("admin:certificates_certificate_add"))
        content = response.content.decode()
        self.assertIn('name="student"', content)
        self.assertIn('name="course"', content)

    def test_creating_certificate_via_admin_logs_issuance(self):
        response = self.client.post(reverse("admin:certificates_certificate_add"), {
            "student": self.student.id, "course": self.course.id, "status": Certificate.Status.ISSUED,
        })
        self.assertEqual(Certificate.objects.filter(student=self.student, course=self.course).count(), 1)
        log = self.AuditLog.objects.filter(action="certificate.issue").first()
        self.assertIsNotNone(log)
        self.assertEqual(log.actor, self.admin)

    def test_revoking_certificate_via_admin_logs_status_change(self):
        certificate = Certificate.objects.create(
            student=self.student, course=self.course, status=Certificate.Status.ISSUED,
        )
        response = self.client.post(
            reverse("admin:certificates_certificate_change", args=[certificate.id]),
            {"status": Certificate.Status.REVOKED},
        )
        certificate.refresh_from_db()
        self.assertEqual(certificate.status, Certificate.Status.REVOKED)
        log = self.AuditLog.objects.filter(action="certificate.status_change").first()
        self.assertIsNotNone(log)
        self.assertEqual(log.metadata["from"], "issued")
        self.assertEqual(log.metadata["to"], "revoked")

    def test_saving_without_status_change_does_not_log_a_status_change(self):
        certificate = Certificate.objects.create(
            student=self.student, course=self.course, status=Certificate.Status.ISSUED,
        )
        self.client.post(
            reverse("admin:certificates_certificate_change", args=[certificate.id]),
            {"status": Certificate.Status.ISSUED},
        )
        self.assertEqual(self.AuditLog.objects.filter(action="certificate.status_change").count(), 0)
