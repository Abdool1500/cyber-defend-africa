import io
from unittest.mock import patch

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse

from apps.accounts.models import User

from .models import EmploymentOutcome


def _make_student(email="graduate@example.com"):
    return User.objects.create_user(
        email=email, password="pass1234", full_name="Graduate Student",
        role=User.Role.STUDENT, status=User.Status.ACTIVE,
    )


def _pdf_upload(name="offer_letter.pdf"):
    return SimpleUploadedFile(name, b"%PDF-1.4 fake but valid-enough content", content_type="application/pdf")


class EmploymentOutcomeModelTests(TestCase):
    def test_str_representation(self):
        student = _make_student()
        outcome = EmploymentOutcome.objects.create(student=student, status=EmploymentOutcome.Status.SEEKING)
        self.assertIn(student.email, str(outcome))  # User.__str__ returns email, not full_name
        self.assertIn("Seeking Employment", str(outcome))

    def test_multiple_updates_ordered_newest_first(self):
        student = _make_student()
        first = EmploymentOutcome.objects.create(student=student, status=EmploymentOutcome.Status.SEEKING)
        second = EmploymentOutcome.objects.create(student=student, status=EmploymentOutcome.Status.EMPLOYED_FULL_TIME)
        outcomes = list(EmploymentOutcome.objects.filter(student=student))
        self.assertEqual(outcomes[0], second)
        self.assertEqual(outcomes[1], first)


class StudentEmploymentFlowTests(TestCase):
    def setUp(self):
        self.student = _make_student()
        self.client.login(username="graduate@example.com", password="pass1234")

    def test_employment_list_shows_no_updates_message_when_empty(self):
        response = self.client.get(reverse("student_employment:list"))
        self.assertContains(response, "No updates yet")

    def test_create_employment_update_without_evidence(self):
        response = self.client.post(reverse("student_employment:create"), {
            "status": EmploymentOutcome.Status.EMPLOYED_FULL_TIME,
            "employer": "Cyber Defend Africa",
            "job_title": "SOC Analyst",
            "country": "Nigeria",
            "date_employed": "2026-06-01",
            "salary_range": "",
            "how_academy_helped": "Learned practical SOC skills.",
        })
        self.assertEqual(response.status_code, 302)
        outcome = EmploymentOutcome.objects.get(student=self.student)
        self.assertEqual(outcome.status, EmploymentOutcome.Status.EMPLOYED_FULL_TIME)
        self.assertEqual(outcome.employer, "Cyber Defend Africa")
        self.assertFalse(outcome.evidence_storage_path)

    def test_future_date_employed_rejected(self):
        response = self.client.post(reverse("student_employment:create"), {
            "status": EmploymentOutcome.Status.EMPLOYED_FULL_TIME,
            "date_employed": "2099-01-01",
        })
        self.assertContains(response, "cannot be in the future")
        self.assertFalse(EmploymentOutcome.objects.filter(student=self.student).exists())

    def test_oversized_evidence_rejected_without_reaching_storage(self):
        big_file = SimpleUploadedFile("big.pdf", b"0" * (21 * 1024 * 1024), content_type="application/pdf")
        with patch("apps.core.services.storage.requests.post") as mock_post:
            response = self.client.post(reverse("student_employment:create"), {
                "status": EmploymentOutcome.Status.SEEKING, "evidence": big_file,
            })
            mock_post.assert_not_called()
        self.assertContains(response, "too large")

    def test_disallowed_evidence_type_rejected(self):
        bad_file = SimpleUploadedFile("virus.exe", b"MZ", content_type="application/x-msdownload")
        response = self.client.post(reverse("student_employment:create"), {
            "status": EmploymentOutcome.Status.SEEKING, "evidence": bad_file,
        })
        self.assertContains(response, "not permitted")

    @override_settings(SUPABASE_URL="https://example.supabase.co", SUPABASE_SERVICE_ROLE_KEY="fake-key")
    @patch("apps.core.services.storage.requests.post")
    def test_create_with_valid_evidence_uploads_and_stores_path(self, mock_post):
        mock_post.return_value.status_code = 200
        mock_post.return_value.text = ""
        response = self.client.post(reverse("student_employment:create"), {
            "status": EmploymentOutcome.Status.INTERNSHIP, "evidence": _pdf_upload(),
        })
        self.assertEqual(response.status_code, 302)
        mock_post.assert_called_once()
        outcome = EmploymentOutcome.objects.get(student=self.student)
        self.assertTrue(outcome.evidence_storage_path)
        self.assertTrue(outcome.evidence_storage_path.startswith(f"employment-evidence/{self.student.id}/"))

    @patch("apps.core.services.storage.requests.post")
    def test_storage_error_during_evidence_upload_shows_message_not_500(self, mock_post):
        mock_post.return_value.status_code = 500
        mock_post.return_value.text = "internal error"
        response = self.client.post(reverse("student_employment:create"), {
            "status": EmploymentOutcome.Status.INTERNSHIP, "evidence": _pdf_upload(),
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Evidence upload failed")
        self.assertFalse(EmploymentOutcome.objects.filter(student=self.student).exists())

    def test_anonymous_redirected_to_login(self):
        self.client.logout()
        response = self.client.get(reverse("student_employment:list"))
        self.assertEqual(response.status_code, 302)

    def test_only_own_updates_are_listed(self):
        other = _make_student(email="other@example.com")
        EmploymentOutcome.objects.create(student=other, status=EmploymentOutcome.Status.EMPLOYED_FULL_TIME)
        EmploymentOutcome.objects.create(student=self.student, status=EmploymentOutcome.Status.SEEKING)
        response = self.client.get(reverse("student_employment:list"))
        self.assertContains(response, "Seeking Employment")
        self.assertNotContains(response, "Employed Full-Time")


class ManagementEmploymentSummaryTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            email="employmentadmin@example.com", password="pass1234", full_name="Employment Admin",
            role=User.Role.ADMIN, status=User.Status.ACTIVE, is_staff=True,
        )
        self.client.login(username="employmentadmin@example.com", password="pass1234")

    def test_summary_shows_zero_state(self):
        response = self.client.get(reverse("management_employment:summary"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "0%")

    def test_summary_counts_latest_status_per_student_only(self):
        student = _make_student()
        EmploymentOutcome.objects.create(student=student, status=EmploymentOutcome.Status.SEEKING)
        EmploymentOutcome.objects.create(student=student, status=EmploymentOutcome.Status.EMPLOYED_FULL_TIME)

        response = self.client.get(reverse("management_employment:summary"))
        self.assertContains(response, "100.0%")  # 1 of 1 reporting graduate is employed

    def test_summary_employment_rate_across_multiple_students(self):
        s1 = _make_student("s1@example.com")
        s2 = _make_student("s2@example.com")
        EmploymentOutcome.objects.create(student=s1, status=EmploymentOutcome.Status.EMPLOYED_FULL_TIME)
        EmploymentOutcome.objects.create(student=s2, status=EmploymentOutcome.Status.SEEKING)

        response = self.client.get(reverse("management_employment:summary"))
        self.assertContains(response, "50.0%")

    def test_student_cannot_access_management_summary(self):
        self.client.logout()
        _make_student()
        self.client.login(username="graduate@example.com", password="pass1234")
        response = self.client.get(reverse("management_employment:summary"))
        self.assertEqual(response.status_code, 403)

    def test_summary_never_shows_salary_or_evidence(self):
        student = _make_student()
        EmploymentOutcome.objects.create(
            student=student, status=EmploymentOutcome.Status.EMPLOYED_FULL_TIME,
            salary_range=EmploymentOutcome.SalaryRange.OVER_150K,
            evidence_storage_path="employment-evidence/some/path.pdf",
        )
        response = self.client.get(reverse("management_employment:summary"))
        self.assertNotContains(response, "150,000")
        self.assertNotContains(response, "employment-evidence/some/path.pdf")


class EmploymentSummaryAPITests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            email="employmentapiadmin@example.com", password="pass1234", full_name="Employment API Admin",
            role=User.Role.ADMIN, status=User.Status.ACTIVE, is_staff=True,
        )

    def test_admin_gets_aggregate_summary(self):
        student = _make_student("employmentapigrad@example.com")
        EmploymentOutcome.objects.create(student=student, status=EmploymentOutcome.Status.EMPLOYED_FULL_TIME)
        self.client.login(username="employmentapiadmin@example.com", password="pass1234")
        response = self.client.get(reverse("api-v1:api-employment"))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["employment_rate"], 100.0)

    def test_api_never_exposes_salary_or_evidence_fields(self):
        student = _make_student("employmentapigrad2@example.com")
        EmploymentOutcome.objects.create(
            student=student, status=EmploymentOutcome.Status.EMPLOYED_FULL_TIME,
            salary_range=EmploymentOutcome.SalaryRange.OVER_150K,
            evidence_storage_path="employment-evidence/some/path.pdf",
        )
        self.client.login(username="employmentapiadmin@example.com", password="pass1234")
        response = self.client.get(reverse("api-v1:api-employment"))
        content = response.content.decode()
        self.assertNotIn("150,000", content)
        self.assertNotIn("employment-evidence", content)

    def test_student_cannot_access_employment_api(self):
        student = _make_student("employmentapistudent@example.com")
        self.client.login(username="employmentapistudent@example.com", password="pass1234")
        response = self.client.get(reverse("api-v1:api-employment"))
        self.assertEqual(response.status_code, 403)
