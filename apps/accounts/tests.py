import io
from unittest.mock import patch

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse

from .models import User


def _png_bytes(color=(10, 20, 30)):
    """A genuinely decodable PNG — ImageField runs Pillow's own decode
    check before any custom validation, so fake byte fixtures won't
    exercise the code paths we actually care about testing here."""
    from PIL import Image
    buf = io.BytesIO()
    Image.new("RGB", (16, 16), color=color).save(buf, format="PNG")
    return buf.getvalue()


def _avatar_upload(name="avatar.png"):
    return SimpleUploadedFile(name, _png_bytes(), content_type="image/png")


class PublicRegistrationTests(TestCase):
    valid_payload = {
        "first_name": "New",
        "last_name": "Student",
        "email": "newstudent@example.com",
        "phone": "+2348000000000",
        "country": "Nigeria",
        "password1": "SuperSecret123!",
        "password2": "SuperSecret123!",
        "agree_terms": "on",
    }

    def test_registration_creates_student_role(self):
        response = self.client.post(reverse("accounts:register"), self.valid_payload)
        self.assertEqual(response.status_code, 302)
        user = User.objects.get(email="newstudent@example.com")
        self.assertEqual(user.role, User.Role.STUDENT)
        self.assertEqual(user.status, User.Status.ACTIVE)
        self.assertEqual(user.full_name, "New Student")
        self.assertEqual(user.phone, "+2348000000000")
        self.assertEqual(user.country, "Nigeria")

    def test_registration_requires_agree_terms(self):
        payload = {**self.valid_payload, "email": "noterms@example.com"}
        del payload["agree_terms"]
        response = self.client.post(reverse("accounts:register"), payload)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(email="noterms@example.com").exists())

    def test_registration_form_has_no_role_field(self):
        """Role must never be selectable at public registration — this is
        the field-level guarantee that backs up the view-level guarantee."""
        response = self.client.get(reverse("accounts:register"))
        self.assertNotContains(response, 'name="role"')

    def test_registration_cannot_set_role_via_post_injection(self):
        """Even if a crafted request includes a `role` field, the
        ModelForm doesn't declare it, so it's silently ignored."""
        payload = {**self.valid_payload, "email": "sneaky@example.com", "role": "super_admin"}
        self.client.post(reverse("accounts:register"), payload)
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

    def test_post_login_redirect_sends_each_role_to_its_own_dashboard(self):
        cases = [
            ("student@example.com", reverse("student_dashboard:overview")),
            ("instructor@example.com", reverse("instructor_dashboard:overview")),
            ("admin@example.com", reverse("management:overview")),
        ]
        for email, expected_url in cases:
            self.client.login(username=email, password="pass1234")
            response = self.client.get(reverse("core:post_login_redirect"))
            self.assertRedirects(response, expected_url)
            self.client.logout()


@override_settings(SUPABASE_URL="https://example.supabase.co", SUPABASE_SERVICE_ROLE_KEY="fake-key")
class ProfileAvatarUploadTests(TestCase):
    """Mocks the Supabase HTTP calls rather than depending on live
    credentials — same convention as apps/core/tests.py's storage tests,
    so this suite runs the same in CI as it does locally."""

    def setUp(self):
        self.user = User.objects.create_user(
            email="avatar@example.com", password="pass1234", full_name="Avatar User",
            role=User.Role.STUDENT, status=User.Status.ACTIVE,
        )
        self.client.login(username="avatar@example.com", password="pass1234")

    def _post_profile(self, avatar=None):
        data = {"full_name": "Avatar User", "phone": "", "country": "", "bio": ""}
        if avatar is not None:
            data["avatar"] = avatar
        return self.client.post(reverse("accounts:profile"), data)

    @patch("apps.core.services.storage.requests.post")
    def test_successful_upload_sets_avatar_path(self, mock_post):
        mock_post.return_value.status_code = 200
        mock_post.return_value.text = ""
        response = self._post_profile(avatar=_avatar_upload())
        self.assertEqual(response.status_code, 302)
        mock_post.assert_called_once()
        self.user.refresh_from_db()
        self.assertTrue(self.user.avatar_path)
        self.assertTrue(self.user.avatar_path.startswith(f"avatars/{self.user.id}/"))

    @patch("apps.core.services.storage.requests.delete")
    @patch("apps.core.services.storage.requests.post")
    def test_reuploading_deletes_previous_avatar(self, mock_post, mock_delete):
        mock_post.return_value.status_code = 200
        mock_post.return_value.text = ""
        self._post_profile(avatar=_avatar_upload("first.png"))
        self.user.refresh_from_db()
        first_path = self.user.avatar_path

        mock_delete.return_value.status_code = 200
        self._post_profile(avatar=_avatar_upload("second.png"))
        mock_delete.assert_called_once()
        self.assertIn(first_path, mock_delete.call_args[0][0])
        self.user.refresh_from_db()
        self.assertNotEqual(self.user.avatar_path, first_path)

    def test_oversized_avatar_rejected_without_reaching_storage(self):
        from PIL import Image
        buf = io.BytesIO()
        Image.new("RGB", (4000, 4000)).save(buf, format="PNG", compress_level=0)
        big_file = SimpleUploadedFile("big.png", buf.getvalue(), content_type="image/png")
        with patch("apps.core.services.storage.requests.post") as mock_post:
            response = self._post_profile(avatar=big_file)
            mock_post.assert_not_called()
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "too large")
        self.user.refresh_from_db()
        self.assertFalse(self.user.avatar_path)

    def test_disallowed_image_format_rejected(self):
        from PIL import Image
        buf = io.BytesIO()
        Image.new("RGB", (16, 16)).save(buf, format="GIF")
        gif_file = SimpleUploadedFile("avatar.gif", buf.getvalue(), content_type="image/gif")
        with patch("apps.core.services.storage.requests.post") as mock_post:
            response = self._post_profile(avatar=gif_file)
            mock_post.assert_not_called()
        self.assertContains(response, "not permitted")

    @patch("apps.core.services.storage.requests.post")
    def test_storage_error_during_upload_shows_message_not_500(self, mock_post):
        mock_post.return_value.status_code = 500
        mock_post.return_value.text = "internal error"
        response = self._post_profile(avatar=_avatar_upload())
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Profile picture upload failed")
        self.user.refresh_from_db()
        self.assertFalse(self.user.avatar_path)

    def test_profile_page_shows_initials_badge_when_no_avatar(self):
        response = self.client.get(reverse("accounts:profile"))
        self.assertContains(response, "cda-avatar\">AU")
        self.assertNotContains(response, "cda-avatar-img")

    @patch("apps.core.services.storage.requests.post")
    def test_profile_page_shows_real_image_after_upload(self, mock_post):
        mock_post.return_value.status_code = 200
        mock_post.return_value.text = ""
        mock_post.return_value.json.return_value = {"signedURL": "/object/sign/avatars/x?token=abc"}
        self._post_profile(avatar=_avatar_upload())
        response = self.client.get(reverse("accounts:profile"))
        self.assertContains(response, "cda-avatar-img")
        self.assertContains(response, "/storage/v1/object/sign/avatars/x")


class ProfileDemographicsTests(TestCase):
    """Gender/date_of_birth are optional, profile-only fields (never on
    the public registration form) that feed the Impact Dashboard's
    "Women trained"/"Youth trained" KPIs — see tasks/todo.md Phase 16.A."""

    def setUp(self):
        self.user = User.objects.create_user(
            email="demographics@example.com", password="pass1234", full_name="Demo User",
            role=User.Role.STUDENT, status=User.Status.ACTIVE,
        )
        self.client.login(username="demographics@example.com", password="pass1234")

    def _post_profile(self, **overrides):
        data = {"full_name": "Demo User", "phone": "", "country": "", "bio": "", "gender": "", "date_of_birth": ""}
        data.update(overrides)
        return self.client.post(reverse("accounts:profile"), data)

    def test_registration_form_has_no_demographic_fields(self):
        """These must only ever be collected via the profile page. Uses
        a fresh anonymous client — register() redirects logged-in users
        before ever rendering the form."""
        from django.test import Client
        response = Client().get(reverse("accounts:register"))
        self.assertNotContains(response, 'name="gender"')
        self.assertNotContains(response, 'name="date_of_birth"')

    def test_demographics_are_optional(self):
        response = self._post_profile()
        self.assertEqual(response.status_code, 302)
        self.user.refresh_from_db()
        self.assertIsNone(self.user.gender)
        self.assertIsNone(self.user.date_of_birth)

    def test_can_set_gender_and_date_of_birth(self):
        response = self._post_profile(gender="female", date_of_birth="2000-05-15")
        self.assertEqual(response.status_code, 302)
        self.user.refresh_from_db()
        self.assertEqual(self.user.gender, "female")
        self.assertEqual(str(self.user.date_of_birth), "2000-05-15")

    def test_future_date_of_birth_rejected(self):
        response = self._post_profile(date_of_birth="2099-01-01")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "cannot be in the future")
        self.user.refresh_from_db()
        self.assertIsNone(self.user.date_of_birth)
