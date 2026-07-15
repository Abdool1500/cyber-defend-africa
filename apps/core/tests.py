import io
from unittest.mock import patch

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from apps.core.services import storage

User = get_user_model()


class MessageToastRenderingTests(TestCase):
    """Regression coverage for the flat-alert -> Bootstrap toast switch:
    the message must actually render inside a .toast element, and error
    messages (tag "error") must map to a real Bootstrap color class since
    Bootstrap 5 has no .text-bg-error."""

    def test_success_message_renders_in_toast_container(self):
        response = self.client.post(reverse("accounts:register"), {
            "first_name": "Toast", "last_name": "Tester", "email": "toasttest@example.com",
            "phone": "+2348011112222", "country": "Nigeria",
            "password1": "SuperSecret123!", "password2": "SuperSecret123!", "agree_terms": "on",
        }, follow=True)
        self.assertContains(response, "toast-container")
        self.assertContains(response, "text-bg-success")

    def test_error_tag_maps_to_bootstrap_danger_class(self):
        """Bootstrap 5 has no .text-bg-error class, so Django's default
        "error" tag (from messages.error()) must be remapped — otherwise
        error toasts would render with no background color at all."""
        from django.conf import settings
        self.assertEqual(settings.MESSAGE_TAGS.get(messages.ERROR), "danger")


class StorageValidationTests(TestCase):
    def test_validate_mime_type_rejects_disallowed_type(self):
        with self.assertRaises(storage.InvalidFileError):
            storage.validate_mime_type("application/x-msdownload")

    def test_validate_mime_type_allows_pdf(self):
        storage.validate_mime_type("application/pdf")  # should not raise

    def test_validate_file_size_rejects_oversized_file(self):
        with self.assertRaises(storage.InvalidFileError):
            storage.validate_file_size(storage.MAX_FILE_SIZE_BYTES + 1)

    def test_generate_safe_path_ignores_original_filename_except_extension(self):
        path = storage.generate_safe_path(
            "assignments", "course-id", "assignment-id", "student-id",
            original_filename="../../etc/passwd.pdf",
        )
        self.assertTrue(path.endswith(".pdf"))
        self.assertNotIn("passwd", path)
        self.assertNotIn("..", path)
        self.assertTrue(path.startswith("assignments/course-id/assignment-id/student-id/"))

    def test_generate_safe_path_strips_unknown_extension_characters(self):
        path = storage.generate_safe_path("bucket", original_filename="evil.php;.jpg")
        # Extension characters are alnum-only, so no shell/path metacharacters survive.
        ext = path.rsplit(".", 1)[-1]
        self.assertTrue(ext.isalnum())

    @override_settings(SUPABASE_URL="", SUPABASE_SERVICE_ROLE_KEY="")
    def test_upload_fails_gracefully_when_not_configured(self):
        """Without live Supabase credentials, the service must raise a
        clear, typed error rather than silently no-opping or crashing with
        an unrelated exception."""
        service = storage.StorageService()
        with self.assertRaises(storage.StorageNotConfiguredError):
            service.upload("assignment-submissions", "some/path.pdf", io.BytesIO(b"data"), "application/pdf")

    @override_settings(SUPABASE_URL="https://example.supabase.co", SUPABASE_SERVICE_ROLE_KEY="fake-key")
    @patch("apps.core.services.storage.requests.post")
    def test_upload_succeeds_with_mocked_supabase_response(self, mock_post):
        mock_post.return_value.status_code = 200
        mock_post.return_value.text = ""
        service = storage.StorageService()
        path = service.upload("assignment-submissions", "some/path.pdf", io.BytesIO(b"data"), "application/pdf")
        self.assertEqual(path, "some/path.pdf")
        mock_post.assert_called_once()

    @override_settings(SUPABASE_URL="https://example.supabase.co", SUPABASE_SERVICE_ROLE_KEY="fake-key")
    @patch("apps.core.services.storage.requests.post")
    def test_signed_url_generation_with_mocked_supabase_response(self, mock_post):
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {"signedURL": "/object/sign/bucket/path?token=abc"}
        service = storage.StorageService()
        url = service.signed_url("assignment-submissions", "some/path.pdf")
        self.assertTrue(url.startswith("https://example.supabase.co/storage/v1/object/sign/"))

    def test_public_url_rejected_for_private_bucket(self):
        service = storage.StorageService()
        with self.assertRaises(storage.InvalidBucketError):
            service.public_url("assignment-submissions", "some/path.pdf")

    def test_unknown_bucket_rejected(self):
        service = storage.StorageService()
        with self.assertRaises(storage.InvalidBucketError):
            service.public_url("not-a-real-bucket", "path")


class StudentDashboardLearningTimeWidgetTests(TestCase):
    def test_learning_time_widget_shows_real_totals(self):
        from apps.analytics.models import LearningTimeEntry
        from apps.courses.models import Course, CourseModule, Lesson

        user = User.objects.create_user(
            email="widgetcheck@example.com", password="pass1234", full_name="Widget Check",
            role=User.Role.STUDENT, status=User.Status.ACTIVE,
        )
        course = Course.objects.create(
            title="Widget Course", slug="widget-course", short_description="x", description="x",
            status=Course.Status.PUBLISHED,
        )
        module = CourseModule.objects.create(course=course, title="Module 1", status="published")
        lesson = Lesson.objects.create(module=module, title="L", slug="l", status="published")
        LearningTimeEntry.objects.create(student=user, lesson=lesson, date=timezone.now().date(), seconds=5400)

        self.client.force_login(user)
        response = self.client.get(reverse("student_dashboard:overview"))
        self.assertContains(response, "My Learning Time")
        self.assertContains(response, "1h 30m")

    def test_learning_time_widget_shows_zero_state(self):
        user = User.objects.create_user(
            email="zerotime@example.com", password="pass1234", full_name="Zero Time",
            role=User.Role.STUDENT, status=User.Status.ACTIVE,
        )
        self.client.force_login(user)
        response = self.client.get(reverse("student_dashboard:overview"))
        self.assertContains(response, "My Learning Time")
        self.assertContains(response, "0m")


class StudentDashboardNewWidgetTests(TestCase):
    """16.N — Learning Streak, Recent Quiz Scores, Upcoming Assignments,
    and the anonymized Leaderboard Position widget."""

    def setUp(self):
        from apps.courses.models import Course

        self.student = User.objects.create_user(
            email="widgets16n@example.com", password="pass1234", full_name="Widgets Student",
            role=User.Role.STUDENT, status=User.Status.ACTIVE,
        )
        self.course = Course.objects.create(
            title="16N Course", slug="16n-course", short_description="x", description="x",
            status=Course.Status.PUBLISHED,
        )
        self.client.force_login(self.student)

    def test_zero_state_shows_no_streak_and_not_ranked(self):
        response = self.client.get(reverse("student_dashboard:overview"))
        self.assertContains(response, "Learning Streak")
        self.assertContains(response, "0 days")
        self.assertContains(response, "Complete a graded quiz to rank")

    def test_learning_streak_counts_consecutive_days_including_today(self):
        from apps.analytics.models import LearningTimeEntry
        from apps.courses.models import CourseModule, Lesson

        module = CourseModule.objects.create(course=self.course, title="Module 1", status="published")
        lesson = Lesson.objects.create(module=module, title="L", slug="l", status="published")
        today = timezone.now().date()
        for offset in range(3):
            LearningTimeEntry.objects.create(
                student=self.student, lesson=lesson, date=today - timezone.timedelta(days=offset), seconds=600
            )
        response = self.client.get(reverse("student_dashboard:overview"))
        self.assertContains(response, "3 days")

    def test_recent_quiz_scores_and_leaderboard_after_grading(self):
        from apps.quizzes.models import Quiz, QuizAttempt

        quiz = Quiz.objects.create(course=self.course, title="16N Quiz", status=Quiz.Status.PUBLISHED)
        QuizAttempt.objects.create(
            quiz=quiz, student=self.student, attempt_number=1, status=QuizAttempt.Status.GRADED,
            percentage=75.0, score=75, max_score=100, graded_at=timezone.now(),
        )
        response = self.client.get(reverse("student_dashboard:overview"))
        self.assertContains(response, "16N Quiz")
        self.assertContains(response, "75%")
        self.assertContains(response, "Top 100%")  # sole ranked student

    def test_upcoming_assignments_widget_shows_unsubmitted_assignment(self):
        from apps.assignments.models import Assignment
        from apps.enrollments.models import Enrollment

        Enrollment.objects.create(student=self.student, course=self.course, status=Enrollment.Status.ACTIVE)
        Assignment.objects.create(course=self.course, title="16N Assignment", status=Assignment.Status.PUBLISHED)
        response = self.client.get(reverse("student_dashboard:overview"))
        self.assertContains(response, "16N Assignment")

    def test_upcoming_assignments_excludes_already_submitted(self):
        from apps.assignments.models import Assignment, AssignmentSubmission
        from apps.enrollments.models import Enrollment

        Enrollment.objects.create(student=self.student, course=self.course, status=Enrollment.Status.ACTIVE)
        assignment = Assignment.objects.create(
            course=self.course, title="16N Submitted Assignment", status=Assignment.Status.PUBLISHED
        )
        AssignmentSubmission.objects.create(assignment=assignment, student=self.student)
        response = self.client.get(reverse("student_dashboard:overview"))
        self.assertNotContains(response, "16N Submitted Assignment")


class InstructorDashboardWidgetTests(TestCase):
    """16.O — Engagement/Performance stat cards and Students At Risk table."""

    def setUp(self):
        from apps.courses.models import Course
        from apps.instructors.models import InstructorAssignment

        self.instructor = User.objects.create_user(
            email="instrwidgets16o@example.com", password="pass1234", full_name="Instr Widgets",
            role=User.Role.INSTRUCTOR, status=User.Status.ACTIVE,
        )
        self.course = Course.objects.create(
            title="16O Course", slug="16o-course", short_description="x", description="x",
            status=Course.Status.PUBLISHED,
        )
        InstructorAssignment.objects.create(
            instructor=self.instructor, course=self.course, status=InstructorAssignment.Status.ACTIVE,
        )
        self.client.force_login(self.instructor)

    def test_zero_state_shows_new_sections(self):
        response = self.client.get(reverse("instructor_dashboard:overview"))
        self.assertContains(response, "Engagement &amp; Performance")
        self.assertContains(response, "Students At Risk")
        self.assertContains(response, "No students currently flagged as at risk.")

    def test_at_risk_student_appears_in_table(self):
        from apps.enrollments.models import Enrollment

        student = User.objects.create_user(
            email="atriskview16o@example.com", password="pass1234", full_name="At Risk View",
            role=User.Role.STUDENT, status=User.Status.ACTIVE,
        )
        Enrollment.objects.create(
            student=student, course=self.course, status=Enrollment.Status.ACTIVE, progress_percentage=5,
        )
        response = self.client.get(reverse("instructor_dashboard:overview"))
        self.assertContains(response, "At Risk View")
        self.assertContains(response, "16O Course")

    def test_student_cannot_access_instructor_dashboard(self):
        self.client.logout()
        student = User.objects.create_user(
            email="notinstr16o@example.com", password="pass1234", full_name="Not Instructor",
            role=User.Role.STUDENT, status=User.Status.ACTIVE,
        )
        self.client.force_login(student)
        response = self.client.get(reverse("instructor_dashboard:overview"))
        self.assertEqual(response.status_code, 403)
