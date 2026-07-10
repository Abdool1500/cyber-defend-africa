from django.test import TestCase
from django.urls import reverse

from .models import User


class PublicRegistrationTests(TestCase):
    def test_registration_creates_student_role(self):
        response = self.client.post(reverse("accounts:register"), {
            "full_name": "New Student",
            "email": "newstudent@example.com",
            "password1": "SuperSecret123!",
            "password2": "SuperSecret123!",
        })
        self.assertEqual(response.status_code, 302)
        user = User.objects.get(email="newstudent@example.com")
        self.assertEqual(user.role, User.Role.STUDENT)
        self.assertEqual(user.status, User.Status.ACTIVE)

    def test_registration_form_has_no_role_field(self):
        """Role must never be selectable at public registration — this is
        the field-level guarantee that backs up the view-level guarantee."""
        response = self.client.get(reverse("accounts:register"))
        self.assertNotContains(response, 'name="role"')

    def test_registration_cannot_set_role_via_post_injection(self):
        """Even if a crafted request includes a `role` field, the
        ModelForm doesn't declare it, so it's silently ignored."""
        self.client.post(reverse("accounts:register"), {
            "full_name": "Sneaky User",
            "email": "sneaky@example.com",
            "password1": "SuperSecret123!",
            "password2": "SuperSecret123!",
            "role": "super_admin",
        })
        user = User.objects.get(email="sneaky@example.com")
        self.assertEqual(user.role, User.Role.STUDENT)


class RoleBoundaryTests(TestCase):
    def setUp(self):
        self.student = User.objects.create_user(
            email="student@example.com", password="pass1234", full_name="Student",
            role=User.Role.STUDENT, status=User.Status.ACTIVE,
        )
        self.instructor = User.objects.create_user(
            email="instructor@example.com", password="pass1234", full_name="Instructor",
            role=User.Role.INSTRUCTOR, status=User.Status.ACTIVE,
        )
        self.admin = User.objects.create_user(
            email="admin@example.com", password="pass1234", full_name="Admin",
            role=User.Role.ADMIN, status=User.Status.ACTIVE, is_staff=True,
        )

    def test_student_cannot_access_instructor_dashboard(self):
        self.client.login(username="student@example.com", password="pass1234")
        response = self.client.get(reverse("instructor_dashboard:overview"))
        self.assertEqual(response.status_code, 403)

    def test_student_cannot_access_question_bank(self):
        self.client.login(username="student@example.com", password="pass1234")
        response = self.client.get(reverse("instructor_question_bank:list"))
        self.assertEqual(response.status_code, 403)

    def test_student_cannot_access_management(self):
        self.client.login(username="student@example.com", password="pass1234")
        response = self.client.get(reverse("management:overview"))
        self.assertEqual(response.status_code, 403)

    def test_instructor_cannot_access_management(self):
        self.client.login(username="instructor@example.com", password="pass1234")
        response = self.client.get(reverse("management:overview"))
        self.assertEqual(response.status_code, 403)

    def test_instructor_cannot_access_student_dashboard(self):
        self.client.login(username="instructor@example.com", password="pass1234")
        response = self.client.get(reverse("student_dashboard:overview"))
        self.assertEqual(response.status_code, 403)

    def test_anonymous_redirected_to_login(self):
        response = self.client.get(reverse("student_dashboard:overview"))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("accounts:login"), response.url)

    def test_suspended_student_denied_access(self):
        self.student.status = User.Status.SUSPENDED
        self.student.save()
        self.client.login(username="student@example.com", password="pass1234")
        response = self.client.get(reverse("student_dashboard:overview"))
        self.assertEqual(response.status_code, 403)
